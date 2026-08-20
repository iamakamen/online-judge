from collections.abc import Mapping

from sqlalchemy.orm import Session

from backend.app.models.problem import Problem
from backend.app.models.test_case import TestCase
from backend.app.schemas.run import (
    RunLanguage,
    RunMode,
    RunRequest,
    RunResponse,
    RunStatus,
    RunTestResult,
)
from backend.app.services.execution.cpp_runner import CppRunner
from backend.app.services.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionRunner,
    ExecutionStatus,
)
from backend.app.services.execution.python_runner import PythonRunner
from backend.app.services.problem import get_problem
from backend.app.services.test_case import list_test_cases_for_problem


_RUNNER_TYPES: Mapping[RunLanguage, type[ExecutionRunner]] = {
    RunLanguage.PYTHON: PythonRunner,
    RunLanguage.CPP: CppRunner,
}


def _outputs_match(actual: str, expected: str) -> bool:
    """Compare program output while ignoring line-ending representation."""
    return actual.rstrip("\r\n") == expected.rstrip("\r\n")


class RunService:
    """Orchestrate a user-facing Run without owning sandbox mechanics."""

    def __init__(
        self,
        runners: Mapping[RunLanguage, ExecutionRunner] | None = None,
    ) -> None:
        self._runners = dict(runners or {})

    def execute(self, db: Session, request: RunRequest) -> RunResponse:
        problem = get_problem(db, request.problem_id)
        runner = self._runner_for(request.language)

        if request.mode is RunMode.CUSTOM_INPUT:
            execution = runner.execute(
                self._execution_request(
                    request.source_code,
                    request.custom_input or "",
                    problem,
                )
            )
            result = self._custom_result(request.custom_input or "", execution)
            return RunResponse(
                status=result.status,
                language=request.language,
                mode=request.mode,
                results=[result],
            )

        test_cases = list_test_cases_for_problem(
            db,
            request.problem_id,
            run_visible_only=True,
        )

        results: list[RunTestResult] = []
        for test_case in test_cases:
            execution = runner.execute(
                self._execution_request(
                    request.source_code,
                    test_case.input,
                    problem,
                )
            )
            results.append(self._test_result(test_case, execution))

        return RunResponse(
            status=self._aggregate_status(results),
            language=request.language,
            mode=request.mode,
            results=results,
        )

    def _runner_for(self, language: RunLanguage) -> ExecutionRunner:
        if language in self._runners:
            return self._runners[language]

        runner_type = _RUNNER_TYPES.get(language)
        if runner_type is None:
            raise ValueError(f"Unsupported language: {language.value}")
        return runner_type()

    @staticmethod
    def _execution_request(
        source_code: str,
        stdin: str,
        problem: Problem,
    ) -> ExecutionRequest:
        return ExecutionRequest(
            source_code=source_code,
            stdin=stdin,
            time_limit_ms=problem.time_limit_ms,
            memory_limit_mb=problem.memory_limit_mb,
        )

    @staticmethod
    def _custom_result(stdin: str, execution: ExecutionResult) -> RunTestResult:
        return RunTestResult(
            status=execution.status.value,
            input=stdin,
            expected_output=None,
            stdout=execution.stdout,
            stderr=execution.stderr,
            execution_time_ms=execution.execution_time_ms,
        )

    @staticmethod
    def _test_result(
        test_case: TestCase,
        execution: ExecutionResult,
    ) -> RunTestResult:
        status = execution.status.value
        if execution.status is ExecutionStatus.PASSED:
            status = (
                RunStatus.PASSED.value
                if _outputs_match(execution.stdout, test_case.expected_output)
                else RunStatus.FAILED.value
            )

        return RunTestResult(
            test_case_id=test_case.id,
            display_order=test_case.display_order,
            status=status,
            input=test_case.input,
            expected_output=test_case.expected_output,
            stdout=execution.stdout,
            stderr=execution.stderr,
            execution_time_ms=execution.execution_time_ms,
        )

    @staticmethod
    def _aggregate_status(results: list[RunTestResult]) -> RunStatus:
        if not results:
            return RunStatus.PASSED

        for status in (
            RunStatus.COMPILE_ERROR,
            RunStatus.RUNTIME_ERROR,
            RunStatus.TIME_LIMIT_EXCEEDED,
            RunStatus.MEMORY_LIMIT_EXCEEDED,
            RunStatus.OUTPUT_LIMIT_EXCEEDED,
            RunStatus.SYSTEM_ERROR,
            RunStatus.FAILED,
        ):
            if any(result.status == status for result in results):
                return status
        return RunStatus.PASSED
