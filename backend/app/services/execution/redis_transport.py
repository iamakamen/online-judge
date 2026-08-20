"""Redis request/reply transport for V1 Run jobs.

Redis is only a transient transport here. Run results are not persisted in
PostgreSQL and expire after the configured TTL.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass
from typing import Any

from redis import Redis

from backend.app.core.execution import (
    RUN_REQUEST_TIMEOUT_MS,
    RUN_RESULT_TTL_SECONDS,
)
from backend.app.schemas.run import RunRequest, RunResponse


RUN_QUEUE_KEY = "run:jobs"
RUN_RESULT_KEY_PREFIX = "run:result:"


@dataclass(frozen=True)
class RunJob:
    request_id: str
    user_id: int
    request: RunRequest


class RunTransport:
    """Serialize Run jobs/results and provide transient Redis request/reply."""

    def __init__(
        self,
        redis: Redis,
        *,
        result_ttl_seconds: int = RUN_RESULT_TTL_SECONDS,
        wait_timeout_ms: int = RUN_REQUEST_TIMEOUT_MS,
    ) -> None:
        self._redis = redis
        self._result_ttl_seconds = result_ttl_seconds
        self._wait_timeout_seconds = wait_timeout_ms / 1000

    def enqueue(self, user_id: int, request: RunRequest) -> str:
        request_id = str(uuid.uuid4())
        job = RunJob(request_id=request_id, user_id=user_id, request=request)
        self._redis.rpush(RUN_QUEUE_KEY, self.serialize_job(job))
        return request_id

    def wait_for_result(self, request_id: str) -> RunResponse | None:
        key = self.result_key(request_id)
        deadline = time.monotonic() + self._wait_timeout_seconds

        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None

            value = self._redis.get(key)
            if value is not None:
                return self.deserialize_result(value)

            time.sleep(min(0.05, remaining))

    def publish_result(self, request_id: str, result: RunResponse) -> None:
        self._redis.setex(
            self.result_key(request_id),
            self._result_ttl_seconds,
            self.serialize_result(result),
        )

    def consume_job(self, timeout_seconds: int = 5) -> RunJob | None:
        item = self._redis.blpop(RUN_QUEUE_KEY, timeout=timeout_seconds)
        if item is None:
            return None
        _, payload = item
        return self.deserialize_job(payload)

    @staticmethod
    def result_key(request_id: str) -> str:
        return f"{RUN_RESULT_KEY_PREFIX}{request_id}"

    @staticmethod
    def serialize_job(job: RunJob) -> str:
        payload: dict[str, Any] = asdict(job.request)
        payload["language"] = job.request.language.value
        payload["mode"] = job.request.mode.value
        return json.dumps(
            {
                "request_id": job.request_id,
                "user_id": job.user_id,
                "request": payload,
            },
            separators=(",", ":"),
        )

    @staticmethod
    def deserialize_job(payload: str | bytes) -> RunJob:
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        data = json.loads(payload)
        return RunJob(
            request_id=str(data["request_id"]),
            user_id=int(data["user_id"]),
            request=RunRequest.model_validate(data["request"]),
        )

    @staticmethod
    def serialize_result(result: RunResponse) -> str:
        return result.model_dump_json()

    @staticmethod
    def deserialize_result(payload: str | bytes) -> RunResponse:
        if isinstance(payload, bytes):
            payload = payload.decode("utf-8")
        return RunResponse.model_validate_json(payload)
