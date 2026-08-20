from dataclasses import dataclass

import pytest

from backend.app.schemas.run import RunLanguage, RunMode, RunRequest, RunResponse, RunStatus
from backend.app.services.execution.redis_transport import RunJob
from backend.app.services.execution.run_worker import RunWorker


REQUEST = RunRequest(
    problem_id=1,
    language=RunLanguage.PYTHON,
    mode=RunMode.CUSTOM_INPUT,
    source_code="print('hello')",
    custom_input="input",
)


class FakeDb:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class FakeTransport:
    def __init__(self):
        self.published = []

    def publish_result(self, request_id, result):
        self.published.append((request_id, result))

    def consume_job(self, timeout_seconds=5):
        return None


@dataclass
class FakeService:
    result: RunResponse | None = None
    error: Exception | None = None

    def execute(self, db, request):
        if self.error is not None:
            raise self.error
        assert db.closed is False
        return self.result


def make_job(request_id="request-1"):
    return RunJob(request_id=request_id, user_id=7, request=REQUEST)


def test_process_job_executes_service_publishes_result_and_closes_db():
    transport = FakeTransport()
    db = FakeDb()
    expected = RunResponse(
        status=RunStatus.PASSED,
        language=RunLanguage.PYTHON,
        mode=RunMode.CUSTOM_INPUT,
        results=[],
    )
    service = FakeService(result=expected)

    worker = RunWorker(
        transport,
        run_service=service,
        session_factory=lambda: db,
    )

    worker.process_job(make_job())

    assert db.closed is True
    assert transport.published == [("request-1", expected)]


def test_process_job_publishes_system_error_when_service_fails():
    transport = FakeTransport()
    db = FakeDb()
    service = FakeService(error=RuntimeError("boom"))

    worker = RunWorker(
        transport,
        run_service=service,
        session_factory=lambda: db,
    )

    worker.process_job(make_job())

    assert db.closed is True
    request_id, result = transport.published[0]
    assert request_id == "request-1"
    assert result.status is RunStatus.SYSTEM_ERROR
    assert result.language is RunLanguage.PYTHON
    assert result.mode is RunMode.CUSTOM_INPUT
    assert result.results == []


def test_worker_uses_configured_concurrency():
    worker = RunWorker(FakeTransport(), max_concurrent_runs=2)

    assert worker.max_concurrent_runs == 2


@pytest.mark.parametrize("value", [0, -1])
def test_worker_rejects_invalid_concurrency(value):
    with pytest.raises(ValueError, match="max_concurrent_runs"):
        RunWorker(FakeTransport(), max_concurrent_runs=value)
