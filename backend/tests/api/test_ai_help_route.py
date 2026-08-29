import pytest

from backend.app.core.ai import (
    MAX_AI_DIAGNOSTIC_BYTES,
    MAX_AI_REQUEST_BYTES,
    MAX_AI_SOURCE_CODE_BYTES,
)
from backend.app.models.problem import Difficulty, Problem
from backend.app.services.ai_help import AI_CONTEXT_FIELDS, build_ai_help_context


@pytest.fixture(autouse=True)
def bedrock_unconfigured_for_route_tests(monkeypatch):
    for name in (
        "BEDROCK_AWS_REGION",
        "AWS_REGION",
        "AWS_DEFAULT_REGION",
        "BEDROCK_MODEL_ID",
        "BEDROCK_TIMEOUT_SECONDS",
    ):
        monkeypatch.delenv(name, raising=False)


def create_problem(db, topic_id, *, statement="Solve the problem", constraints="n <= 10"):
    problem = Problem(
        topic_id=topic_id,
        title="Two Sum",
        slug="two-sum-ai-test",
        statement=statement,
        constraints=constraints,
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
def problem(db):
    from backend.app.models.topic import Topic

    db.add(Topic(name="Arrays", slug="arrays", display_order=1))
    db.commit()
    topic = db.query(Topic).one()
    return create_problem(db, topic.id)


def payload(problem_id, **overrides):
    body = {
        "problem_id": problem_id,
        "language": "python",
        "operation": "run",
        "source_code": "print('x')",
        "failure_status": "runtime_error",
        "diagnostic": "NameError: name 'x' is not defined",
        "stdout": "",
        "stderr": "NameError: name 'x' is not defined",
    }
    body.update(overrides)
    return body


def test_ai_help_requires_authentication(client, problem):
    response = client.post("/api/v1/ai/help", json=payload(problem.id))
    assert response.status_code == 401


def test_ai_help_requires_verified_user(client, db, problem, user_token, normal_user):
    normal_user.email_verified = False
    db.commit()
    response = client.post(
        "/api/v1/ai/help",
        headers={"Authorization": f"Bearer {user_token}"},
        json=payload(problem.id),
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Email verification required"


@pytest.mark.parametrize("operation", ["debug", "", "RUN"])
def test_ai_help_rejects_invalid_operation(client, user_headers, problem, operation):
    response = client.post(
        "/api/v1/ai/help",
        headers=user_headers,
        json=payload(problem.id, operation=operation),
    )
    assert response.status_code == 422


@pytest.mark.parametrize("status_value", ["passed", "accepted"])
def test_ai_help_rejects_successful_result(client, user_headers, problem, status_value):
    response = client.post(
        "/api/v1/ai/help",
        headers=user_headers,
        json=payload(problem.id, failure_status=status_value),
    )
    assert response.status_code == 422


def test_ai_help_rejects_invalid_language(client, user_headers, problem):
    response = client.post(
        "/api/v1/ai/help",
        headers=user_headers,
        json=payload(problem.id, language="javascript"),
    )
    assert response.status_code == 422


def test_ai_help_rejects_unknown_problem(client, user_headers):
    response = client.post(
        "/api/v1/ai/help",
        headers=user_headers,
        json=payload(999999),
    )
    assert response.status_code == 404


def test_ai_help_rejects_missing_fields(client, user_headers, problem):
    body = payload(problem.id)
    del body["diagnostic"]
    response = client.post("/api/v1/ai/help", headers=user_headers, json=body)
    assert response.status_code == 422


def test_ai_help_rejects_source_size(client, user_headers, problem):
    response = client.post(
        "/api/v1/ai/help",
        headers=user_headers,
        json=payload(problem.id, source_code="x" * (MAX_AI_SOURCE_CODE_BYTES + 1)),
    )
    assert response.status_code == 422


def test_ai_help_rejects_diagnostic_size(client, user_headers, problem):
    response = client.post(
        "/api/v1/ai/help",
        headers=user_headers,
        json=payload(problem.id, diagnostic="x" * (MAX_AI_DIAGNOSTIC_BYTES + 1)),
    )
    assert response.status_code == 422


def test_ai_help_rejects_oversized_request(client, user_headers, problem):
    response = client.post(
        "/api/v1/ai/help",
        headers=user_headers,
        json=payload(
            problem.id,
            source_code="x" * 81_000,
            diagnostic="y" * 8_000,
            stdout="z" * 16_000,
            stderr="w" * 16_000,
        ),
    )
    assert response.status_code == 422
    assert "request context" in response.json()["detail"][0]["msg"]


def test_ai_help_rejects_arbitrary_fields(client, user_headers, problem):
    response = client.post(
        "/api/v1/ai/help",
        headers=user_headers,
        json=payload(problem.id, arbitrary_context={"secret": "value"}),
    )
    assert response.status_code == 422


def test_ai_help_resolves_problem_context_server_side(db, problem):
    request_body = payload(problem.id)
    from backend.app.schemas.ai import AiHelpRequest

    context = build_ai_help_context(db, AiHelpRequest.model_validate(request_body))
    assert set(context) == AI_CONTEXT_FIELDS
    assert context["problem_statement"] == "Solve the problem"
    assert context["problem_constraints"] == "n <= 10"
    assert context["problem_title"] == "Two Sum"


def test_ai_help_context_excludes_hidden_tests_reference_code_and_secrets(db, problem):
    from backend.app.schemas.ai import AiHelpRequest

    context = build_ai_help_context(db, AiHelpRequest.model_validate(payload(problem.id)))
    serialized = str(context)
    assert "test_case" not in serialized
    assert "reference" not in serialized
    assert "DATABASE_URL" not in serialized
    assert "REDIS_URL" not in serialized
    assert "JWT_SECRET" not in serialized
    assert "AWS_ACCESS_KEY" not in serialized
    assert "starter_code" not in context


@pytest.mark.parametrize(
    ("operation", "failure_status"),
    [("run", "runtime_error"), ("submit", "wrong_answer")],
)
def test_ai_help_accepts_run_and_submit_failure_context(
    client, user_headers, problem, operation, failure_status
):
    response = client.post(
        "/api/v1/ai/help",
        headers=user_headers,
        json=payload(
            problem.id,
            operation=operation,
            failure_status=failure_status,
        ),
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "AI Help provider is not configured"


def test_ai_help_rejects_run_wrong_answer(client, user_headers, problem):
    response = client.post(
        "/api/v1/ai/help",
        headers=user_headers,
        json=payload(problem.id, failure_status="wrong_answer"),
    )
    assert response.status_code == 422


def test_ai_help_fails_safely_before_provider_integration(client, user_headers, problem):
    response = client.post(
        "/api/v1/ai/help",
        headers=user_headers,
        json=payload(problem.id),
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "AI Help provider is not configured"


def test_configured_provider_returns_existing_ai_response(
    client, user_headers, problem, monkeypatch
):
    from backend.app.api.routes import ai as ai_route
    from backend.app.schemas.ai import AiHelpResponse

    class FakeProvider:
        def __init__(self):
            self.context = None

        def generate(self, context):
            self.context = context
            return AiHelpResponse(
                summary="Inspect the failing expression.",
                tips=["Check the variable before it is used."],
            )

    provider = FakeProvider()
    monkeypatch.setattr(ai_route, "get_bedrock_provider", lambda: provider)
    response = client.post(
        "/api/v1/ai/help",
        headers=user_headers,
        json=payload(problem.id),
    )
    assert response.status_code == 200
    assert response.json()["tips"] == ["Check the variable before it is used."]
    assert "test_cases" not in provider.context
    assert "starter_code" not in provider.context


def test_configured_provider_timeout_is_safe(
    client, user_headers, problem, monkeypatch
):
    from backend.app.api.routes import ai as ai_route
    from backend.app.services.bedrock_ai_help import BedrockProviderTimeout

    class FakeProvider:
        def generate(self, context):
            raise BedrockProviderTimeout("internal timeout details")

    monkeypatch.setattr(ai_route, "get_bedrock_provider", FakeProvider)
    response = client.post(
        "/api/v1/ai/help",
        headers=user_headers,
        json=payload(problem.id),
    )
    assert response.status_code == 504
    assert response.json()["detail"] == "AI Help provider timed out"
    assert "internal" not in response.text
