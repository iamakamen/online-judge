"""Reconcile committed queued submissions into the submission stream."""

from __future__ import annotations

import logging
from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.submission import Submission, SubmissionStatus
from backend.app.services.submission_dispatch import SubmissionDispatcher


logger = logging.getLogger(__name__)

SUBMISSION_RECONCILIATION_BATCH_SIZE = 50
DEFAULT_RECONCILIATION_BATCH_SIZE = SUBMISSION_RECONCILIATION_BATCH_SIZE


class SubmissionReconciler:
    """Dispatch a bounded batch of persisted queued submissions."""

    def __init__(
        self,
        dispatcher: SubmissionDispatcher,
        *,
        session_factory: Callable[[], Session],
        batch_size: int = DEFAULT_RECONCILIATION_BATCH_SIZE,
    ) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")

        self._dispatcher = dispatcher
        self._session_factory = session_factory
        self._batch_size = batch_size

    def reconcile_once(self) -> int:
        """Dispatch one ordered batch and return its successful count."""
        submission_ids = self._queued_submission_ids()
        dispatched = 0

        for submission_id in submission_ids:
            try:
                succeeded = self._dispatcher.dispatch(submission_id)
            except Exception:
                logger.exception(
                    "Submission reconciliation dispatch failed: "
                    "submission_id=%s",
                    submission_id,
                )
                break

            if not succeeded:
                logger.error(
                    "Submission reconciliation stopped after dispatch "
                    "failure: submission_id=%s dispatched=%s batch_size=%s",
                    submission_id,
                    dispatched,
                    self._batch_size,
                )
                break

            dispatched += 1

        return dispatched

    def _queued_submission_ids(self) -> list[int]:
        db = None
        try:
            db = self._session_factory()
            statement = (
                select(Submission.id)
                .where(Submission.status == SubmissionStatus.QUEUED)
                .order_by(Submission.created_at.asc(), Submission.id.asc())
                .limit(self._batch_size)
            )
            return list(db.scalars(statement))
        except Exception:
            if db is not None:
                db.rollback()
            logger.exception(
                "Submission reconciliation query failed: batch_size=%s",
                self._batch_size,
            )
            return []
        finally:
            # No database transaction may remain open while Redis is called.
            if db is not None:
                db.rollback()
                db.close()
