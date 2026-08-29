import json

import pytest

from backend.app.core.bedrock import (
    BedrockConfig,
    BedrockNotConfiguredError,
)
from backend.app.schemas.ai import AiHelpResponse
from backend.app.services.bedrock_ai_help import (
    BedrockAiHelpProvider,
    BedrockMalformedResponse,
    BedrockProviderError,
    BedrockProviderTimeout,
)


class FakeBedrockClient:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def converse(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.response


def config():
    return BedrockConfig(region="us-east-1")


def context():
    return {
        "problem_title": "Two Sum",
        "problem_statement": "Find the pair.",
        "problem_constraints": "n <= 1000",
        "language": "python",
        "operation": "run",
        "failure_status": "runtime_error",
        "source_code": "print(x)",
        "diagnostic": "NameError",
        "stdout": "",
        "stderr": "NameError",
    }


def response(summary="Inspect the undefined variable.", tips=None):
    return {
        "output": {
            "message": {
                "content": [
                    {
                        "text": json.dumps(
                            {
                                "summary": summary,
                                "tips": tips or ["Check where x is initialized."],
                            }
                        )
                    }
                ]
            }
        }
    }


def fenced_response(summary="Inspect the undefined variable.", tips=None):
    payload = {
        "summary": summary,
        "tips": tips or ["Check where x is initialized."],
    }
    return {
        "output": {
            "message": {
                "content": [
                    {"text": f"```json\n{json.dumps(payload)}\n```"}
                ]
            }
        }
    }


def test_provider_returns_existing_response_schema():
    client = FakeBedrockClient(response=response())
    result = BedrockAiHelpProvider(config(), client=client).generate(context())
    assert isinstance(result, AiHelpResponse)
    assert result.tips == ["Check where x is initialized."]
    assert client.calls[0]["modelId"] == "amazon.nova-lite-v1:0"


def test_provider_accepts_nova_lite_fenced_json_response():
    client = FakeBedrockClient(response=fenced_response())
    result = BedrockAiHelpProvider(config(), client=client).generate(context())
    assert isinstance(result, AiHelpResponse)
    assert result.summary == "Inspect the undefined variable."
    assert result.tips == ["Check where x is initialized."]


def test_provider_sends_only_allowlisted_context():
    client = FakeBedrockClient(response=response())
    BedrockAiHelpProvider(config(), client=client).generate(context())
    prompt = client.calls[0]["messages"][0]["content"][0]["text"]
    assert "Two Sum" in prompt
    assert "DATABASE_URL" not in prompt
    assert "REDIS_URL" not in prompt
    assert "AWS_SECRET_ACCESS_KEY" not in prompt
    assert "hidden" in prompt.lower()
    assert "reference solution" in prompt.lower()
    assert "test_case_id" not in prompt


def test_provider_rejects_context_outside_allowlist():
    client = FakeBedrockClient(response=response())
    invalid_context = {**context(), "hidden_test_input": "secret"}
    with pytest.raises(BedrockProviderError):
        BedrockAiHelpProvider(config(), client=client).generate(invalid_context)
    assert client.calls == []


def test_provider_rejects_malformed_json_response():
    client = FakeBedrockClient(
        response={
            "output": {
                "message": {"content": [{"text": "not json"}]}
            }
        }
    )
    with pytest.raises(BedrockMalformedResponse):
        BedrockAiHelpProvider(config(), client=client).generate(context())


def test_provider_rejects_response_with_arbitrary_surrounding_prose():
    client = FakeBedrockClient(
        response={
            "output": {
                "message": {
                    "content": [
                        {"text": "Here is the advice: " + json.dumps({"summary": "x", "tips": ["y"]})}
                    ]
                }
            }
        }
    )
    with pytest.raises(BedrockMalformedResponse):
        BedrockAiHelpProvider(config(), client=client).generate(context())


def test_provider_rejects_response_missing_required_fields():
    client = FakeBedrockClient(
        response={
            "output": {
                "message": {
                    "content": [{"text": json.dumps({"summary": "x"})}]
                }
            }
        }
    )
    with pytest.raises(BedrockMalformedResponse):
        BedrockAiHelpProvider(config(), client=client).generate(context())


def test_provider_rejects_malformed_provider_shape():
    with pytest.raises(BedrockMalformedResponse):
        BedrockAiHelpProvider(
            config(), client=FakeBedrockClient(response={})
        ).generate(context())


def test_provider_maps_timeout():
    client = FakeBedrockClient(error=TimeoutError())
    with pytest.raises(BedrockProviderTimeout):
        BedrockAiHelpProvider(config(), client=client).generate(context())


def test_provider_maps_provider_exception_without_details():
    client = FakeBedrockClient(error=RuntimeError("sensitive provider details"))
    with pytest.raises(BedrockProviderError) as error:
        BedrockAiHelpProvider(config(), client=client).generate(context())
    assert str(error.value) == "AI Help provider request failed"
    assert "sensitive" not in str(error.value)


def test_provider_enforces_bounded_response_schema():
    result = BedrockAiHelpProvider(
        config(),
        client=FakeBedrockClient(
            response=response(summary="A" * 1_000, tips=["B" * 600])
        ),
    ).generate(context())
    assert len(result.summary) == 1_000
    assert len(result.tips[0]) == 600


def test_provider_rejects_more_than_five_tips():
    with pytest.raises(BedrockMalformedResponse):
        BedrockAiHelpProvider(
            config(),
            client=FakeBedrockClient(response=response(tips=["tip"] * 6)),
        ).generate(context())


def test_provider_rejects_oversized_tip():
    with pytest.raises(BedrockMalformedResponse):
        BedrockAiHelpProvider(
            config(),
            client=FakeBedrockClient(response=response(tips=["tip" * 201])),
        ).generate(context())


def test_bedrock_configuration_requires_region(monkeypatch):
    monkeypatch.delenv("BEDROCK_AWS_REGION", raising=False)
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)
    with pytest.raises(BedrockNotConfiguredError):
        BedrockConfig.from_environment()
