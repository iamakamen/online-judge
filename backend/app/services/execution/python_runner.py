from backend.app.services.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionRunner,
)


class PythonRunner(ExecutionRunner):
    """Python execution adapter.

    The actual process/container launch is intentionally deferred to the
    sandbox implementation. This adapter defines the language boundary
    without executing user code on the FastAPI host.
    """

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        raise NotImplementedError(
            "Python execution requires the sandbox executor"
        )
