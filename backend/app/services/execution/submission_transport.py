"""Durable Redis Streams transport for asynchronous submission jobs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from collections.abc import Iterator, Sequence
from typing import Mapping
import uuid

from redis import Redis
from redis.exceptions import ResponseError


SUBMISSION_STREAM_KEY = "submission:jobs"
SUBMISSION_CONSUMER_GROUP = "submission-workers"
DEFAULT_CONSUME_TIMEOUT_SECONDS = 5
DEFAULT_RECLAIM_IDLE_TIME_MS = 60_000


@dataclass(frozen=True)
class SubmissionJob:
    job_id: str
    submission_id: int
    enqueued_at: datetime


@dataclass(frozen=True)
class SubmissionDelivery:
    stream_id: str
    job: SubmissionJob
    times_delivered: int = 1


@dataclass(frozen=True)
class SubmissionReclaimResult(Sequence[SubmissionDelivery]):
    deliveries: tuple[SubmissionDelivery, ...]
    next_cursor: str

    def __iter__(self) -> Iterator[SubmissionDelivery]:
        return iter(self.deliveries)

    def __len__(self) -> int:
        return len(self.deliveries)

    def __getitem__(self, index):
        return self.deliveries[index]


class SubmissionTransport:
    """Serialize and deliver submission jobs through a Redis Stream."""

    def __init__(
        self,
        redis: Redis,
        *,
        stream_key: str = SUBMISSION_STREAM_KEY,
        consumer_group: str = SUBMISSION_CONSUMER_GROUP,
    ) -> None:
        self._redis = redis
        self._stream_key = stream_key
        self._consumer_group = consumer_group

    def enqueue(self, submission_id: int) -> SubmissionJob:
        job = SubmissionJob(
            job_id=str(uuid.uuid4()),
            submission_id=submission_id,
            enqueued_at=datetime.now(timezone.utc),
        )
        self._redis.xadd(
            self._stream_key,
            self.serialize_job(job),
            id="*",
        )
        return job

    def consume(
        self,
        consumer_name: str,
        *,
        count: int = 1,
        timeout_seconds: int = DEFAULT_CONSUME_TIMEOUT_SECONDS,
    ) -> list[SubmissionDelivery]:
        if not consumer_name:
            raise ValueError("consumer_name must not be empty")
        if count <= 0:
            raise ValueError("count must be positive")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

        self._ensure_consumer_group()
        response = self._redis.xreadgroup(
            self._consumer_group,
            consumer_name,
            {self._stream_key: ">"},
            count=count,
            block=timeout_seconds * 1000,
        )
        return self._deliveries_from_response(response)

    def acknowledge(self, stream_id: str) -> int:
        if not stream_id:
            raise ValueError("stream_id must not be empty")
        return int(self._redis.xack(self._stream_key, self._consumer_group, stream_id))

    def reclaim(
        self,
        consumer_name: str,
        *,
        min_idle_time_ms: int = DEFAULT_RECLAIM_IDLE_TIME_MS,
        count: int = 10,
        start_id: str = "0-0",
    ) -> SubmissionReclaimResult:
        if not consumer_name:
            raise ValueError("consumer_name must not be empty")
        if min_idle_time_ms <= 0:
            raise ValueError("min_idle_time_ms must be positive")
        if count <= 0:
            raise ValueError("count must be positive")
        if not start_id:
            raise ValueError("start_id must not be empty")

        self._ensure_consumer_group()
        response = self._redis.xautoclaim(
            self._stream_key,
            self._consumer_group,
            consumer_name,
            min_idle_time_ms,
            start_id=start_id,
            count=count,
        )
        next_cursor = self._text(response[0]) if response else "0-0"
        messages = response[1] if len(response) > 1 else []
        stream_ids = [self._text(stream_id) for stream_id, _ in messages]
        delivery_counts = self._pending_delivery_counts(stream_ids)
        return SubmissionReclaimResult(
            deliveries=tuple(
                SubmissionDelivery(
                    stream_id=stream_id,
                    job=self.deserialize_job(fields),
                    times_delivered=delivery_counts.get(stream_id, 1),
                )
                for stream_id, (_, fields) in zip(stream_ids, messages)
            ),
            next_cursor=next_cursor,
        )

    def _pending_delivery_counts(self, stream_ids: list[str]) -> dict[str, int]:
        if not stream_ids:
            return {}
        xpending_range = getattr(self._redis, "xpending_range", None)
        if xpending_range is None:
            return {stream_id: 1 for stream_id in stream_ids}

        wanted = set(stream_ids)
        counts: dict[str, int] = {}
        for stream_id in stream_ids:
            pending = xpending_range(
                self._stream_key,
                self._consumer_group,
                min=stream_id,
                max=stream_id,
                count=1,
            )
            for entry in pending or []:
                entry_id = self._text(
                    entry["message_id"] if isinstance(entry, dict) else entry[0]
                )
                if entry_id in wanted:
                    count = (
                        entry["times_delivered"]
                        if isinstance(entry, dict)
                        else entry[3]
                    )
                    counts[entry_id] = int(count)
        return counts

    def _ensure_consumer_group(self) -> None:
        try:
            self._redis.xgroup_create(
                self._stream_key,
                self._consumer_group,
                id="0-0",
                mkstream=True,
            )
        except ResponseError as exc:
            if "BUSYGROUP" not in str(exc):
                raise

    @classmethod
    def _deliveries_from_response(cls, response) -> list[SubmissionDelivery]:
        deliveries: list[SubmissionDelivery] = []
        for _, messages in response or []:
            deliveries.extend(
                SubmissionDelivery(
                    stream_id=cls._text(stream_id),
                    job=cls.deserialize_job(fields),
                    times_delivered=1,
                )
                for stream_id, fields in messages
            )
        return deliveries

    @staticmethod
    def serialize_job(job: SubmissionJob) -> dict[str, str]:
        return {
            "job_id": job.job_id,
            "submission_id": str(job.submission_id),
            "enqueued_at": job.enqueued_at.astimezone(timezone.utc).isoformat(),
        }

    @classmethod
    def deserialize_job(cls, payload: Mapping[str, str | bytes]) -> SubmissionJob:
        try:
            job_id = cls._text(payload["job_id"])
            submission_id = int(cls._text(payload["submission_id"]))
            enqueued_at = datetime.fromisoformat(
                cls._text(payload["enqueued_at"])
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Invalid submission job payload") from exc

        if not job_id or submission_id <= 0:
            raise ValueError("Invalid submission job payload")
        if enqueued_at.tzinfo is None:
            raise ValueError("Submission job timestamp must include timezone")

        return SubmissionJob(
            job_id=job_id,
            submission_id=submission_id,
            enqueued_at=enqueued_at.astimezone(timezone.utc),
        )

    @staticmethod
    def _text(value: str | bytes) -> str:
        return value.decode("utf-8") if isinstance(value, bytes) else value
