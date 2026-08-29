from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, model_validator

from backend.app.core.ai import (
    MAX_AI_DIAGNOSTIC_BYTES,
    MAX_AI_REQUEST_BYTES,
    MAX_AI_SOURCE_CODE_BYTES,
    MAX_AI_STDERR_BYTES,
    MAX_AI_STDOUT_BYTES,
    MAX_AI_SUMMARY_LENGTH,
    MAX_AI_TIP_LENGTH,
    MAX_AI_RESPONSE_TIPS,
)


class AiHelpOperation(str, Enum):
    RUN = "run"
    SUBMIT = "submit"


class AiHelpLanguage(str, Enum):
    PYTHON = "python"
    CPP = "cpp"


class AiHelpFailureStatus(str, Enum):
    PASSED = "passed"
    ACCEPTED = "accepted"
    FAILED = "failed"
    WRONG_ANSWER = "wrong_answer"
    COMPILE_ERROR = "compile_error"
    RUNTIME_ERROR = "runtime_error"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    OUTPUT_LIMIT_EXCEEDED = "output_limit_exceeded"
    SYSTEM_ERROR = "system_error"


SUCCESSFUL_STATUSES = {
    AiHelpFailureStatus.PASSED,
    AiHelpFailureStatus.ACCEPTED,
}


class AiHelpRequest(BaseModel):
    """Strict, user-controlled failure details for a single AI Help request."""

    model_config = ConfigDict(extra="forbid")

    problem_id: PositiveInt
    language: AiHelpLanguage
    operation: AiHelpOperation
    source_code: str = Field(min_length=1)
    failure_status: AiHelpFailureStatus
    diagnostic: str = Field(min_length=1)
    stdout: str = ""
    stderr: str = ""

    @model_validator(mode="after")
    def validate_failure_context(self):
        if self.failure_status in SUCCESSFUL_STATUSES:
            raise ValueError("AI Help requires a failed Run or Submit result")

        if (
            self.operation is AiHelpOperation.RUN
            and self.failure_status is AiHelpFailureStatus.WRONG_ANSWER
        ):
            raise ValueError("wrong_answer is only valid for Submit")

        if (
            self.operation is AiHelpOperation.SUBMIT
            and self.failure_status is AiHelpFailureStatus.FAILED
        ):
            raise ValueError("failed is only valid for Run")

        bounded_fields = {
            "source_code": (self.source_code, MAX_AI_SOURCE_CODE_BYTES),
            "diagnostic": (self.diagnostic, MAX_AI_DIAGNOSTIC_BYTES),
            "stdout": (self.stdout, MAX_AI_STDOUT_BYTES),
            "stderr": (self.stderr, MAX_AI_STDERR_BYTES),
        }
        for field_name, (value, limit) in bounded_fields.items():
            if len(value.encode("utf-8")) > limit:
                raise ValueError(f"{field_name} exceeds {limit} bytes")

        request_bytes = sum(
            len(value.encode("utf-8"))
            for value in (
                self.source_code,
                self.diagnostic,
                self.stdout,
                self.stderr,
            )
        )
        if request_bytes > MAX_AI_REQUEST_BYTES:
            raise ValueError(
                f"AI Help request context exceeds {MAX_AI_REQUEST_BYTES} bytes"
            )

        return self


class AiHelpResponse(BaseModel):
    """Bounded response contract for short, diagnostic-only tips."""

    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1, max_length=MAX_AI_SUMMARY_LENGTH)
    tips: list[str] = Field(min_length=1, max_length=MAX_AI_RESPONSE_TIPS)

    @model_validator(mode="after")
    def validate_tip_lengths(self):
        if any(len(tip) > MAX_AI_TIP_LENGTH for tip in self.tips):
            raise ValueError(f"Each AI Help tip must be at most {MAX_AI_TIP_LENGTH} characters")
        return self
