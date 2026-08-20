from backend.app.api.routes.run import get_redis, get_run_transport
from backend.app.main import app
from backend.app.schemas.run import RunResponse


class FakeRedis:
    def __init__(self, count: int = 0):
        self.count = count
        self.expire_calls: list[tuple[str, int]] = []

    def incr(self, key: str) -> int:
        self.count += 1
        return self.count

    def expire(self, key: str, seconds: int) -> bool:
        self.expire_calls.append((key, seconds))
        return True


class FakeTransport:
    def __init__(self, result: RunResponse | None):
        self.result = result
        self.enqueued: list[tuple[int, object]] = []

    def enqueue(self, user_id: int, request):
        self.enqueued.append((user_id, request))
        return "request-1"

    def wait_for_result(self, request_id: str):
        return self.result


def run_payload() -> dict:
    return {
        "problem_id": 1,
        "language": "python",
        "mode": "custom_input",
        "source_code": "print(input())",
        "custom_input": "hello\n",
    }


def result() -> RunResponse:
    return RunResponse.model_validate(
        {
            "status": "passed",
            "language": "python",
            "mode": "custom_input",
            "results": [
                {
                    "status": "passed",
                    "input": "hello\n",
                    "expected_output": None,
                    "stdout": "hello\n",
                    "stderr": "",
                    "execution_time_ms": 10,
                }
            ],
        }
    )


def override_dependencies(redis: FakeRedis, transport: FakeTransport):
    app.dependency_overrides[get_redis] = lambda: redis
    app.dependency_overrides[get_run_transport] = lambda: transport


def clear_dependencies():
    app.dependency_overrides.pop(get_redis, None)
    app.dependency_overrides.pop(get_run_transport, None)


def test_run_requires_authentication(client):
    response = client.post("/api/v1/run", json=run_payload())

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required"


def test_run_enqueues_and_returns_result(client, user_headers):
    redis = FakeRedis()
    transport = FakeTransport(result())
    override_dependencies(redis, transport)

    try:
        response = client.post(
            "/api/v1/run",
            json=run_payload(),
            headers=user_headers,
        )
    finally:
        clear_dependencies()

    assert response.status_code == 200
    assert response.json()["status"] == "passed"
    assert len(transport.enqueued) == 1
    assert redis.count == 1
    assert redis.expire_calls


def test_run_returns_gateway_timeout_when_worker_result_is_missing(
    client, user_headers
):
    redis = FakeRedis()
    transport = FakeTransport(None)
    override_dependencies(redis, transport)

    try:
        response = client.post(
            "/api/v1/run",
            json=run_payload(),
            headers=user_headers,
        )
    finally:
        clear_dependencies()

    assert response.status_code == 504
    assert response.json()["detail"] == "Run execution timed out"


def test_run_enforces_rate_limit(client, user_headers):
    redis = FakeRedis(count=10)
    transport = FakeTransport(result())
    override_dependencies(redis, transport)

    try:
        response = client.post(
            "/api/v1/run",
            json=run_payload(),
            headers=user_headers,
        )
    finally:
        clear_dependencies()

    assert response.status_code == 429
    assert response.json()["detail"] == "Run rate limit exceeded"
    assert transport.enqueued == []


def test_run_rejects_invalid_payload(client, user_headers):
    response = client.post(
        "/api/v1/run",
        json={
            "problem_id": 1,
            "language": "python",
            "mode": "custom_input",
            "source_code": "print(1)",
        },
        headers=user_headers,
    )

    assert response.status_code == 422
