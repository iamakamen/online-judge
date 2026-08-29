from collections import defaultdict

import pytest
from redis.exceptions import RedisError

from backend.app.api.routes.ai import get_ai_help_redis
from backend.app.main import app
from backend.app.models.problem import Difficulty, Problem
from backend.app.models.topic import Topic
from backend.app.schemas.ai import AiHelpResponse
from backend.app.services.ai_help_throttle import (
    AI_HELP_RATE_LIMIT,
    AI_HELP_RATE_WINDOW_SECONDS,
)


class FakeRedis:
    def __init__(self, error=None):
        self.error = error
        self.counts = defaultdict(int)
        self.keys = []

    def eval(self, script, number_of_keys, key, window_seconds):
        if self.error is not None:
            raise self.error
        self.keys.append(key)
        self.counts[key] += 1
        return [self.counts[key], AI_HELP_RATE_WINDOW_SECONDS]


class FakeProvider:
    def generate(self, context):
        return AiHelpResponse(
            summary="Inspect the failing expression.",
            tips=["Check the failing line."],
        )


@pytest.fixture()
def problem(db):
    topic = Topic(name="Throttle Arrays", slug="throttle-arrays", display_order=1)
    db.add(topic)
    db.commit()
    problem = Problem(
        topic_id=topic.id,
        title="Throttle Test",
        slug="throttle-test",
        statement="Solve this problem.",
        constraints="n <= 10",
        difficulty=Difficulty.EASY,
        tags=["arrays"],
        starter_code={"python": "", "cpp": ""},
        time_limit_ms=1000,
        memory_limit_mb=128,
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


@pytest.fixture()
def throttle_dependencies(monkeypatch):
    from backend.app.api.routes import ai as ai_route

    redis = FakeRedis()
    app.dependency_overrides[get_ai_help_redis] = lambda: redis
    monkeypatch.setattr(ai_route, "get_bedrock_provider", lambda: FakeProvider())
    yield redis
    app.dependency_overrides.pop(get_ai_help_redis, None)


def payload(problem_id):
    return {
        "problem_id": problem_id,
        "language": "python",
        "operation": "run",
        "source_code": "print(x)",
        "failure_status": "runtime_error",
        "diagnostic": "NameError",
        "stdout": "",
        "stderr": "NameError",
    }


def test_ai_help_request_is_allowed(client, user_headers, problem, throttle_dependencies):
    response = client.post(
        "/api/v1/ai/help",
        headers=user_headers,
        json=payload(problem.id),
    )
    assert response.status_code == 200


def test_ai_help_request_is_rejected_after_limit(
    client, user_headers, problem, throttle_dependencies
):
    responses = [
        client.post(
            "/api/v1/ai/help",
            headers=user_headers,
            json=payload(problem.id),
        )
        for _ in range(AI_HELP_RATE_LIMIT + 1)
    ]

    assert [response.status_code for response in responses[:-1]] == [200] * AI_HELP_RATE_LIMIT
    assert responses[-1].status_code == 429
    assert responses[-1].headers["Retry-After"] == str(AI_HELP_RATE_WINDOW_SECONDS)
    assert responses[-1].json()["detail"] == "AI Help rate limit exceeded"


def test_ai_help_limits_are_separate_per_user(
    client, user_headers, admin_headers, problem, throttle_dependencies
):
    for _ in range(AI_HELP_RATE_LIMIT):
        response = client.post(
            "/api/v1/ai/help",
            headers=user_headers,
            json=payload(problem.id),
        )
        assert response.status_code == 200

    assert client.post(
        "/api/v1/ai/help",
        headers=user_headers,
        json=payload(problem.id),
    ).status_code == 429
    assert client.post(
        "/api/v1/ai/help",
        headers=admin_headers,
        json=payload(problem.id),
    ).status_code == 200


def test_ai_help_redis_failure_is_safe(client, user_headers, problem, monkeypatch):
    from backend.app.api.routes import ai as ai_route

    app.dependency_overrides[get_ai_help_redis] = lambda: FakeRedis(
        error=RedisError("redis internal details")
    )
    monkeypatch.setattr(ai_route, "get_bedrock_provider", lambda: FakeProvider())
    try:
        response = client.post(
            "/api/v1/ai/help",
            headers=user_headers,
            json=payload(problem.id),
        )
    finally:
        app.dependency_overrides.pop(get_ai_help_redis, None)

    assert response.status_code == 503
    assert response.json()["detail"] == "AI Help service unavailable"
    assert "redis internal" not in response.text
