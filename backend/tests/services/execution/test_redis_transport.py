from dataclasses import dataclass

from backend.app.schemas.run import RunLanguage, RunMode, RunRequest, RunResponse, RunStatus
from backend.app.services.execution.redis_transport import (
    RUN_QUEUE_KEY,
    RunJob,
    RunTransport,
)


def request() -> RunRequest:
    return RunRequest(
        problem_id=7,
        language=RunLanguage.PYTHON,
        mode=RunMode.CUSTOM_INPUT,
        source_code="print(input())",
        custom_input="hello\n",
    )


def response() -> RunResponse:
    return RunResponse(
        status=RunStatus.PASSED,
        language=RunLanguage.PYTHON,
        mode=RunMode.CUSTOM_INPUT,
        results=[],
    )


@dataclass
class FakeRedis:
    values: dict[str, str]
    lists: dict[str, list[str]]
    expirations: dict[str, int]

    def rpush(self, key: str, value: str) -> None:
        self.lists.setdefault(key, []).append(value)

    def blpop(self, key: str, timeout: int):
        values = self.lists.get(key, [])
        if not values:
            return None
        return key, values.pop(0)

    def setex(self, key: str, ttl: int, value: str) -> None:
        self.values[key] = value
        self.expirations[key] = ttl

    def get(self, key: str):
        return self.values.get(key)


def transport(fake: FakeRedis) -> RunTransport:
    return RunTransport(fake, result_ttl_seconds=60, wait_timeout_ms=100)


def test_enqueue_serializes_request_and_returns_request_id():
    fake = FakeRedis({}, {}, {})
    queue = transport(fake)

    request_id = queue.enqueue(42, request())

    assert request_id
    assert len(fake.lists[RUN_QUEUE_KEY]) == 1

    job = queue.consume_job(timeout_seconds=0)
    assert job == RunJob(request_id=request_id, user_id=42, request=request())


def test_publish_and_consume_result_uses_configured_ttl():
    fake = FakeRedis({}, {}, {})
    queue = transport(fake)
    request_id = "request-1"

    queue.publish_result(request_id, response())

    assert fake.expirations[queue.result_key(request_id)] == 60
    assert queue.wait_for_result(request_id) == response()


def test_wait_for_result_returns_none_when_result_does_not_arrive():
    fake = FakeRedis({}, {}, {})
    queue = RunTransport(fake, result_ttl_seconds=60, wait_timeout_ms=1)

    assert queue.wait_for_result("missing") is None
