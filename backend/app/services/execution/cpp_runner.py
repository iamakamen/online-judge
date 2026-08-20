from pathlib import Path

from backend.app.core.execution import (
    COMPILE_TIMEOUT_MS,
    MAX_STDERR_BYTES,
    MAX_STDOUT_BYTES,
)
from backend.app.services.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionRunner,
    ExecutionStatus,
)
from backend.app.services.execution.sandbox import (
    SandboxExecutor,
    SandboxRequest,
    SandboxWorkspace,
)


CPP_IMAGE = "online-judge-run-cpp:17"


class CppRunner(ExecutionRunner):
    """Compile and execute C++17 source exclusively through the Docker sandbox."""

    def __init__(self, sandbox: SandboxExecutor | None = None) -> None:
        self._sandbox = sandbox or SandboxExecutor()

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        with SandboxWorkspace() as workspace:
            source_path = workspace / "solution.cpp"
            binary_path = workspace / "solution"
            source_path.write_text(request.source_code, encoding="utf-8")

            compile_result = self._sandbox.execute(
                SandboxRequest(
                    image=CPP_IMAGE,
                    command=(
                        "g++",
                        "-std=c++17",
                        "-O2",
                        "-pipe",
                        "/workspace/solution.cpp",
                        "-o",
                        "/workspace/solution",
                    ),
                    workspace=Path(workspace),
                    stdin="",
                    timeout_ms=COMPILE_TIMEOUT_MS,
                    memory_limit_mb=request.memory_limit_mb,
                    stdout_limit_bytes=MAX_STDOUT_BYTES,
                    stderr_limit_bytes=MAX_STDERR_BYTES,
                    workspace_read_only=False,
                )
            )

            if compile_result.infrastructure_error is not None:
                return ExecutionResult(
                    status=ExecutionStatus.SYSTEM_ERROR,
                    stdout=compile_result.stdout,
                    stderr=compile_result.stderr,
                    exit_code=compile_result.exit_code,
                    execution_time_ms=compile_result.execution_time_ms,
                )

            if compile_result.timed_out:
                return ExecutionResult(
                    status=ExecutionStatus.COMPILE_ERROR,
                    stdout=compile_result.stdout,
                    stderr=compile_result.stderr,
                    exit_code=None,
                    execution_time_ms=compile_result.execution_time_ms,
                )

            if compile_result.output_limited:
                return ExecutionResult(
                    status=ExecutionStatus.COMPILE_ERROR,
                    stdout=compile_result.stdout,
                    stderr=compile_result.stderr,
                    exit_code=compile_result.exit_code,
                    execution_time_ms=compile_result.execution_time_ms,
                )

            if compile_result.exit_code != 0 or not binary_path.is_file():
                return ExecutionResult(
                    status=ExecutionStatus.COMPILE_ERROR,
                    stdout=compile_result.stdout,
                    stderr=compile_result.stderr,
                    exit_code=compile_result.exit_code,
                    execution_time_ms=compile_result.execution_time_ms,
                )

            runtime_result = self._sandbox.execute(
                SandboxRequest(
                    image=CPP_IMAGE,
                    command=("/workspace/solution",),
                    workspace=Path(workspace),
                    stdin=request.stdin,
                    timeout_ms=request.time_limit_ms,
                    memory_limit_mb=request.memory_limit_mb,
                    stdout_limit_bytes=MAX_STDOUT_BYTES,
                    stderr_limit_bytes=MAX_STDERR_BYTES,
                    workspace_read_only=True,
                )
            )

        if runtime_result.infrastructure_error is not None:
            status = ExecutionStatus.SYSTEM_ERROR
        elif runtime_result.timed_out:
            status = ExecutionStatus.TIME_LIMIT_EXCEEDED
        elif runtime_result.output_limited:
            status = ExecutionStatus.OUTPUT_LIMIT_EXCEEDED
        elif runtime_result.exit_code == 0:
            status = ExecutionStatus.PASSED
        else:
            status = ExecutionStatus.RUNTIME_ERROR

        return ExecutionResult(
            status=status,
            stdout=runtime_result.stdout,
            stderr=runtime_result.stderr,
            exit_code=runtime_result.exit_code,
            execution_time_ms=runtime_result.execution_time_ms,
        )
