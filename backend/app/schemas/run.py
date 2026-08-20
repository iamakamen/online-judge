from enum import Enum

from pydantic import BaseModel, Field, PositiveInt, model_validator

from backend.app.core.execution import (
    MAX_CUSTOM_INPUT_BYTES,
    MAX_SOURCE_CODE_BYTES,
)


class RunLanguage(str, Enum):
    PYTHON = "python"
    CPP = "cpp"


class RunMode(str, Enum):
    TEST_CASES = "run_tests"
    CUSTOM_INPUT = "custom_input"


class RunStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    COMPILE_ERROR = "compile_error"
    RUNTIME_ERROR = "runtime_error"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    OUTPUT_LIMIT_EXCEEDED = "output_limit_exceeded"
    SYSTEM_ERROR = "system_error"


class RunRequest(BaseModel):
    problem_id: PositiveInt
    language: RunLanguage
    mode: RunMode = RunMode.TEST_CASES
    source_code: str = Field(min_length=1)
    custom_input: str | None = None

    @model_validator(mode="after")
    def validate_execution_payload(self):
        source_bytes = len(self.source_code.encode("utf-8"))
        if source_bytes > MAX_SOURCE_CODE_BYTES:
            raise ValueError(
                f"source_code exceeds {MAX_SOURCE_CODE_BYTES} bytes"
            )

        if self.custom_input is not None:
            custom_input_bytes = len(self.custom_input.encode("utf-8"))
            if custom_input_bytes > MAX_CUSTOM_INPUT_BYTES:
                raise ValueError(
                    f"custom_input exceeds {MAX_CUSTOM_INPUT_BYTES} bytes"
                )

        if self.mode is RunMode.TEST_CASES and self.custom_input is not None:
            raise ValueError(
                "custom_input must be omitted when mode is run_tests"
            )

        if self.mode is RunMode.CUSTOM_INPUT and self.custom_input is None:
            raise ValueError(
                "custom_input is required when mode is custom_input"
            )

        return self


class RunTestResult(BaseModel):
    test_case_id: PositiveInt | None = None
    display_order: PositiveInt | None = None
    status: RunStatus
    input: str
    expected_output: str | None = None
    stdout: str = ""
    stderr: str = ""
    execution_time_ms: int | None = None


class RunResponse(BaseModel):
    status: RunStatus
    language: RunLanguage
    mode: RunMode
    results: list[RunTestResult]
