import pytest
from pydantic import ValidationError

from backend.app.schemas.run import RunLanguage, RunMode, RunRequest, RunStatus


def valid_request(**overrides) -> RunRequest:
    values = {
        "problem_id": 1,
        "language": RunLanguage.PYTHON,
        "mode": RunMode.TEST_CASES,
        "source_code": "print('hello')",
        "custom_input": None,
    }
    values.update(overrides)
    return RunRequest(**values)


def test_run_tests_request_accepts_no_custom_input():
    request = valid_request()

    assert request.mode is RunMode.TEST_CASES
    assert request.custom_input is None


def test_custom_input_request_requires_input():
    with pytest.raises(ValidationError, match="custom_input is required"):
        valid_request(mode=RunMode.CUSTOM_INPUT)


def test_run_tests_request_rejects_custom_input():
    with pytest.raises(ValidationError, match="custom_input must be omitted"):
        valid_request(custom_input="hello")


def test_source_code_is_limited_by_utf8_bytes():
    source = "é" * 50_001

    with pytest.raises(ValidationError, match="source_code exceeds"):
        valid_request(source_code=source)


def test_custom_input_is_limited_by_utf8_bytes():
    custom_input = "é" * 50_001

    with pytest.raises(ValidationError, match="custom_input exceeds"):
        valid_request(mode=RunMode.CUSTOM_INPUT, custom_input=custom_input)


def test_multibyte_source_uses_bytes_not_characters():
    source = "é" * 50_000

    request = valid_request(source_code=source)

    assert len(request.source_code.encode("utf-8")) == 100_000


def test_custom_input_allows_empty_string():
    request = valid_request(mode=RunMode.CUSTOM_INPUT, custom_input="")

    assert request.custom_input == ""


def test_supported_languages_are_python_and_cpp():
    assert {language.value for language in RunLanguage} == {"python", "cpp"}


def test_run_statuses_match_execution_contract():
    assert {status.value for status in RunStatus} == {
        "passed",
        "failed",
        "compile_error",
        "runtime_error",
        "time_limit_exceeded",
        "memory_limit_exceeded",
        "output_limit_exceeded",
        "system_error",
    }
