"""Worker for asynchronously judging persisted submissions."""

from __future__ import annotations

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from typing import Protocol

from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from backend.app.core.execution import MAX_CONCURRENT_RUNS
from backend.app.models.submission import Submission, SubmissionStatus
from backend.app.services.execution.submission_transport import (
    DEFAULT_RECLAIM_IDLE_TIME_MS,
    SubmissionDelivery,
    SubmissionTransport,
)
from backend.app.services.submission import (
    SubmissionJudgeService,
    claim_submission,
    fail_submission_with_system_error,
    reset_stale_submission,
    submission_execution_fence,
)


logger = logging.getLogger(__name__)

DEFAULT_CONSUME_TIMEOUT_SECONDS = 5
DEFAULT_MAX_DELIVERY_ATTEMPTS = 5


class SubmissionTransportProtocol(Protocol):
    def consume(
        self,
        consumer_name: str,
        *,
        count: int = 1,
        timeout_seconds: int = 5,
    ) -> list[SubmissionDelivery]: ...

    def acknowledge(self, stream_id: str) -> int: ...

    def reclaim(
        self,
        consumer_name: str,
        *,
        min_idle_time_ms: int = DEFAULT_RECLAIM_IDLE_TIME_MS,
        count: int = 10,
        start_id: str = "0-0",
    ): ...


class SubmissionWorker:
    """Consume submission deliveries and run the persisted judge service."""

    def __init__(
        self,
        transport: SubmissionTransportProtocol,
        *,
        consumer_name: str,
        judge_service: SubmissionJudgeService | None = None,
        session_factory: Callable[[], Session] | None = None,
        connection_factory: Callable[[], Connection] | None = None,
        max_concurrent_submissions: int = MAX_CONCURRENT_RUNS,
        consume_timeout_seconds: int = DEFAULT_CONSUME_TIMEOUT_SECONDS,
        reclaim_idle_time_ms: int = DEFAULT_RECLAIM_IDLE_TIME_MS,
        max_delivery_attempts: int = DEFAULT_MAX_DELIVERY_ATTEMPTS,
    ) -> None:
        if not consumer_name:
            raise ValueError("consumer_name must not be empty")
        if max_concurrent_submissions <= 0:
            raise ValueError("max_concurrent_submissions must be positive")
        if consume_timeout_seconds <= 0:
            raise ValueError("consume_timeout_seconds must be positive")
        if reclaim_idle_time_ms <= 0:
            raise ValueError("reclaim_idle_time_ms must be positive")
        if max_delivery_attempts <= 0:
            raise ValueError("max_delivery_attempts must be positive")

        self._transport = transport
        self._consumer_name = consumer_name
        self._judge_service = judge_service or SubmissionJudgeService()
        self._session_factory = session_factory
        self._connection_factory = connection_factory
        self._max_concurrent_submissions = max_concurrent_submissions
        self._consume_timeout_seconds = consume_timeout_seconds
        self._reclaim_idle_time_ms = reclaim_idle_time_ms
        self._max_delivery_attempts = max_delivery_attempts

    def _open_session(self) -> tuple[Session, Connection | None]:
        if self._session_factory is not None:
            return self._session_factory(), None

        from backend.app.db.session import engine

        connection = (
            self._connection_factory()
            if self._connection_factory is not None
            else engine.connect()
        )
        return Session(bind=connection, autoflush=False), connection

    @property
    def max_concurrent_submissions(self) -> int:
        return self._max_concurrent_submissions

    def process_delivery(self, delivery: SubmissionDelivery) -> None:
        db, connection = self._open_session()
        try:
            with submission_execution_fence(
                db,
                delivery.job.submission_id,
            ) as acquired:
                if not acquired:
                    return

                try:
                    submission = claim_submission(
                        db,
                        delivery.job.submission_id,
                    )
                except ValueError:
                    self._transport.acknowledge(delivery.stream_id)
                    return

                self._judge_and_ack(db, submission, delivery)
        except Exception:
            logger.exception(
                "Submission job failed: job_id=%s submission_id=%s",
                delivery.job.job_id,
                delivery.job.submission_id,
            )
        finally:
            db.close()
            if connection is not None:
                connection.close()

    def process_reclaimed_delivery(
        self,
        delivery: SubmissionDelivery,
    ) -> None:
        """Recover one idle pending delivery without duplicate execution."""
        db, connection = self._open_session()
        try:
            with submission_execution_fence(
                db,
                delivery.job.submission_id,
            ) as acquired:
                if not acquired:
                    return

                submission = db.get(Submission, delivery.job.submission_id)
                if submission is None or submission.status in (
                    SubmissionStatus.COMPLETED,
                    SubmissionStatus.FAILED,
                ):
                    self._transport.acknowledge(delivery.stream_id)
                    return

                stale_cutoff = datetime.now(timezone.utc) - timedelta(
                    milliseconds=self._reclaim_idle_time_ms
                )
                if submission.status is SubmissionStatus.RUNNING:
                    if submission.updated_at > stale_cutoff:
                        return
                    if delivery.times_delivered > self._max_delivery_attempts:
                        fail_submission_with_system_error(
                            db,
                            submission.id,
                        )
                        self._transport.acknowledge(delivery.stream_id)
                        return
                    if not reset_stale_submission(
                        db,
                        submission.id,
                        stale_cutoff=stale_cutoff,
                    ):
                        return
                    submission = db.get(Submission, submission.id)
                    if submission is None:
                        self._transport.acknowledge(delivery.stream_id)
                        return

                if delivery.times_delivered > self._max_delivery_attempts:
                    if fail_submission_with_system_error(db, submission.id):
                        self._transport.acknowledge(delivery.stream_id)
                    return

                if submission.status is SubmissionStatus.QUEUED:
                    try:
                        submission = claim_submission(db, submission.id)
                    except ValueError:
                        return
                    self._judge_and_ack(db, submission, delivery)
        except Exception:
            logger.exception(
                "Reclaimed submission job failed: job_id=%s submission_id=%s",
                delivery.job.job_id,
                delivery.job.submission_id,
            )
        finally:
            db.close()
            if connection is not None:
                connection.close()

    def recover_pending(self) -> None:
        """Reclaim idle deliveries in Redis cursor order."""
        cursor = "0-0"
        while True:
            result = self._transport.reclaim(
                self._consumer_name,
                min_idle_time_ms=self._reclaim_idle_time_ms,
                count=self._max_concurrent_submissions,
                start_id=cursor,
            )
            for delivery in result:
                self.process_reclaimed_delivery(delivery)
            if result.next_cursor == "0-0":
                return
            cursor = result.next_cursor

    def _judge_and_ack(self, db, submission, delivery) -> None:
        judged_submission = self._judge_service.execute_claimed(
            db,
            submission,
        )
        if judged_submission.status not in (
            SubmissionStatus.COMPLETED,
            SubmissionStatus.FAILED,
        ):
            raise RuntimeError("submission judge did not reach a terminal status")
        self._transport.acknowledge(delivery.stream_id)

    def run_forever(self) -> None:
        """Consume submission deliveries until the worker is terminated."""
        with ThreadPoolExecutor(
            max_workers=self._max_concurrent_submissions
        ) as executor:
            while True:
                self.recover_pending()
                deliveries = self._transport.consume(
                    self._consumer_name,
                    count=self._max_concurrent_submissions,
                    timeout_seconds=self._consume_timeout_seconds,
                )
                for delivery in deliveries:
                    executor.submit(self.process_delivery, delivery)
