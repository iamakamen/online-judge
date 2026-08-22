"""Application-level dispatch policy for persisted submissions."""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Protocol

from redis.exceptions import (
    BusyLoadingError,
    ConnectionError as RedisConnectionError,
    RedisError,
    TimeoutError as RedisTimeoutError,
    TryAgainError,
)


logger = logging.getLogger(__name__)

DEFAULT_DISPATCH_ATTEMPTS = 3
DEFAULT_DISPATCH_BACKOFF_SECONDS = (0.05, 0.1)

_TRANSIENT_REDIS_ERRORS = (
    RedisConnectionError,
    RedisTimeoutError,
    BusyLoadingError,
    TryAgainError,
)


class SubmissionTransportProtocol(Protocol):
    def enqueue(self, submission_id: int): ...


class SubmissionDispatcher:
    """Dispatch persisted submissions with bounded transient-error retries."""

    def __init__(
        self,
        transport: SubmissionTransportProtocol,
        *,
        attempts: int = DEFAULT_DISPATCH_ATTEMPTS,
        backoff_seconds: tuple[float, ...] = DEFAULT_DISPATCH_BACKOFF_SECONDS,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        if attempts <= 0:
            raise ValueError("attempts must be positive")
        if len(backoff_seconds) < attempts - 1:
            raise ValueError("backoff_seconds must cover retry delays")
        if any(delay < 0 for delay in backoff_seconds):
            raise ValueError("backoff_seconds must not be negative")

        self._transport = transport
        self._attempts = attempts
        self._backoff_seconds = backoff_seconds
        self._sleeper = sleeper

    def dispatch(self, submission_id: int) -> bool:
        """Attempt to enqueue a committed submission.

        Returns False after a non-transient failure or retry exhaustion. The
        submission remains QUEUED; PostgreSQL state is not touched here.
        """
        for attempt in range(1, self._attempts + 1):
            try:
                self._transport.enqueue(submission_id)
                return True
            except RedisError as exc:
                transient = isinstance(exc, _TRANSIENT_REDIS_ERRORS)
                if transient and attempt < self._attempts:
                    self._sleeper(self._backoff_seconds[attempt - 1])
                    continue

                logger.exception(
                    "Submission enqueue failed: submission_id=%s "
                    "attempts=%s transient=%s",
                    submission_id,
                    attempt,
                    transient,
                )
                return False

        return False
