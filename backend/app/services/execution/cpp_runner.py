from pathlib import Path

from backend.app.core.execution import (
    COMPILE_TIMEOUT_MS,
    MAX_MEMORY_LIMIT_MB,
    MAX_STDERR_BYTES,
    MAX_STDOUT_BYTES,
)
from backend.app.services.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionRunner,
    ExecutionStatus,
)
from backend.app.services.execution.sandbox import SandboxExecutor, SandboxWorkspace, SandboxRequest


CPP_IMAGE = "online-judge-run-cpp:17"
COMPILE_MEMORY_LIMIT_MB = MAX_MEMORY_LIMIT_MB


class CppRunner(ExecutionRunner):
    """Compile and execute C++17 source exclusively through Docker sandboxes."""

    def __init__(self, sandbox: SandboxExecutor | None = None) -> None:
        self._sandbox = sandbox or SandboxExecutor()

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        with SandboxWorkspace() as workspace:
            source_path = workspace / "main.cpp"
            binary_path = workspace / "main"
            source_path.write_text(request.source_code, encoding="utf-8")

            compile_result = self._sandbox.execute(
                SandboxRequest(
                    image=CPP_IMAGE,
                    command=(
                        "/usr/bin/g++",
                        "-std=c++17",
                        "-O2",
                        "-pipe",
                        "/workspace/main.cpp",
                        "-o",
                        "/workspace/main",
                    ),
                    workspace=Path(workspace),
                    timeout_ms=COMPILE_TIMEOUT_MS,
                    memory_limit_mb=COMPILE_MEMORY_LIMIT_MB,
                    stdout_limit_bytes=MAX_STDOUT_BYTES,
                    stderr_limit_bytes=MAX_STDERR_BYTES,
                    workspace_read_only=False,
                )
            )

            compile_status = self._compile_status(compile_result)
            if compile_status is not None:
                return ExecutionResult(
                    status=compile_status,
                    stdout=compile_result.stdout,
                    stderr=compile_result.stderr,
                    exit_code=compile_result.exit_code,
                    execution_time_ms=compile_result.execution_time_ms,
                )

            if not binary_path.is_file():
                return ExecutionResult(
                    status=ExecutionStatus.SYSTEM_ERROR,
                    stdout=compile_result.stdout,
                    stderr="compiler reported success but produced no executable",
                    exit_code=compile_result.exit_code,
                    execution_time_ms=compile_result.execution_time_ms,
                )

            runtime_result = self._sandbox.execute(
                SandboxRequest(
                    image=CPP_IMAGE,
                    command=("/workspace/main",),
                    workspace=Path(workspace),
                    stdin=request.stdin,
                    timeout_ms=request.time_limit_ms,
                    memory_limit_mb=request.memory_limit_mb,
                    stdout_limit_bytes=MAX_STDOUT_BYTES,
                    stderr_limit_bytes=MAX_STDERR_BYTES,
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

    @staticmethod
    def _compile_status(result) -> ExecutionStatus | None:
        if result.infrastructure_error is not None:
            return ExecutionStatus.SYSTEM_ERROR
        if result.timed_out:
            return ExecutionStatus.TIME_LIMIT_EXCEEDED
        if result.output_limited:
            return ExecutionStatus.OUTPUT_LIMIT_EXCEEDED
        if result.exit_code != 0:
            return ExecutionStatus.COMPILE_ERROR
        return None
