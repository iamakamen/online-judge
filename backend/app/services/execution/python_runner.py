from pathlib import Path

from backend.app.core.execution import MAX_STDERR_BYTES, MAX_STDOUT_BYTES
from backend.app.services.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionRunner,
    ExecutionStatus,
)
from backend.app.services.execution.sandbox import SandboxExecutor, SandboxWorkspace, SandboxRequest


PYTHON_IMAGE = "online-judge-run-python:3.12"


class PythonRunner(ExecutionRunner):
    """Execute Python 3.12 source exclusively through the Docker sandbox."""

    def __init__(self, sandbox: SandboxExecutor | None = None) -> None:
        self._sandbox = sandbox or SandboxExecutor()

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        with SandboxWorkspace() as workspace:
            source_path = workspace / "solution.py"
            source_path.write_text(request.source_code, encoding="utf-8")

            result = self._sandbox.execute(
                SandboxRequest(
                    image=PYTHON_IMAGE,
                    command=("python3", "/workspace/solution.py"),
                    workspace=Path(workspace),
                    stdin=request.stdin,
                    timeout_ms=request.time_limit_ms,
                    memory_limit_mb=request.memory_limit_mb,
                    stdout_limit_bytes=MAX_STDOUT_BYTES,
                    stderr_limit_bytes=MAX_STDERR_BYTES,
                )
            )

        if result.infrastructure_error is not None:
            status = ExecutionStatus.SYSTEM_ERROR
        elif result.timed_out:
            status = ExecutionStatus.TIME_LIMIT_EXCEEDED
        elif result.output_limited:
            status = ExecutionStatus.OUTPUT_LIMIT_EXCEEDED
        elif result.exit_code == 0:
            status = ExecutionStatus.PASSED
        else:
            status = ExecutionStatus.RUNTIME_ERROR

        return ExecutionResult(
            status=status,
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.exit_code,
            execution_time_ms=result.execution_time_ms,
        )
