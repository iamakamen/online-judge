"""V1 Run worker consuming execution jobs from Redis."""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Protocol

from redis import Redis
from sqlalchemy.orm import Session

from backend.app.core.execution import MAX_CONCURRENT_RUNS
from backend.app.schemas.run import RunResponse, RunStatus
from backend.app.services.execution.redis_transport import RunJob, RunTransport
from backend.app.services.execution.run_service import RunService


logger = logging.getLogger(__name__)

DEFAULT_REDIS_URL = "redis://localhost:6379/0"
DEFAULT_CONSUME_TIMEOUT_SECONDS = 5


class RunTransportProtocol(Protocol):
    def consume_job(self, timeout_seconds: int = 5) -> RunJob | None: ...

    def publish_result(self, request_id: str, result: RunResponse) -> None: ...


class RunWorker:
    """Consume Run jobs and execute them outside the FastAPI process."""

    def __init__(
        self,
        transport: RunTransportProtocol,
        *,
        run_service: RunService | None = None,
        session_factory: Callable[[], Session] | None = None,
        max_concurrent_runs: int = MAX_CONCURRENT_RUNS,
        consume_timeout_seconds: int = DEFAULT_CONSUME_TIMEOUT_SECONDS,
    ) -> None:
        if max_concurrent_runs <= 0:
            raise ValueError("max_concurrent_runs must be positive")
        if consume_timeout_seconds <= 0:
            raise ValueError("consume_timeout_seconds must be positive")

        self._transport = transport
        self._run_service = run_service or RunService()
        self._session_factory = session_factory or self._default_session_factory
        self._max_concurrent_runs = max_concurrent_runs
        self._consume_timeout_seconds = consume_timeout_seconds

    @staticmethod
    def _default_session_factory() -> Session:
        from backend.app.db.session import SessionLocal

        return SessionLocal()

    @property
    def max_concurrent_runs(self) -> int:
        return self._max_concurrent_runs

    def process_job(self, job: RunJob) -> None:
        db = self._session_factory()
        try:
            result = self._run_service.execute(db, job.request)
        except Exception:
            logger.exception("Run job failed: request_id=%s", job.request_id)
            result = RunResponse(
                status=RunStatus.SYSTEM_ERROR,
                language=job.request.language,
                mode=job.request.mode,
                results=[],
            )
        finally:
            db.close()

        self._transport.publish_result(job.request_id, result)

    def run_forever(self) -> None:
        """Consume jobs until the worker process is terminated."""
        with ThreadPoolExecutor(max_workers=self._max_concurrent_runs) as executor:
            while True:
                job = self._transport.consume_job(
                    timeout_seconds=self._consume_timeout_seconds
                )
                if job is not None:
                    executor.submit(self.process_job, job)


def build_worker() -> RunWorker:
    """Build the production worker from environment configuration."""
    redis_url = os.getenv("REDIS_URL", DEFAULT_REDIS_URL)
    redis = Redis.from_url(redis_url)
    return RunWorker(RunTransport(redis))


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    build_worker().run_forever()


if __name__ == "__main__":
    main()
