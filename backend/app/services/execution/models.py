from dataclasses import dataclass
from enum import Enum


class ExecutionStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    COMPILE_ERROR = "compile_error"
    RUNTIME_ERROR = "runtime_error"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    OUTPUT_LIMIT_EXCEEDED = "output_limit_exceeded"
    SYSTEM_ERROR = "system_error"


@dataclass(frozen=True)
class ExecutionRequest:
    source_code: str
    stdin: str
    time_limit_ms: int
    memory_limit_mb: int


@dataclass(frozen=True)
class ExecutionResult:
    status: ExecutionStatus
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    execution_time_ms: int | None = None
    memory_used_mb: int | None = None


class ExecutionRunner:
    """Language-neutral execution contract.

    Implementations own language-specific preparation. Sandbox/container
    enforcement remains a separate concern and will be introduced later.
    """

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        raise NotImplementedError
