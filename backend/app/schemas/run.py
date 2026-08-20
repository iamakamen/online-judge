from enum import Enum

from pydantic import BaseModel, Field, PositiveInt


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
