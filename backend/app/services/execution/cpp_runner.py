from backend.app.services.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionRunner,
)


class CppRunner(ExecutionRunner):
    """C++ execution adapter.

    Compilation and execution are intentionally deferred to the sandbox
    executor. No compiler or user program is launched by the API process.
    """

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        raise NotImplementedError(
            "C++ execution requires the sandbox executor"
        )
