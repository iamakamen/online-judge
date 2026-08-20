from types import SimpleNamespace

from backend.app.schemas.run import RunLanguage, RunMode, RunRequest, RunStatus
from backend.app.services.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionRunner,
    ExecutionStatus,
)
from backend.app.services.execution.run_service import RunService


class FakeRunner(ExecutionRunner):
    def __init__(self, results):
        self.results = iter(results)
        self.requests: list[ExecutionRequest] = []

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        self.requests.append(request)
        return next(self.results)


def problem():
    return SimpleNamespace(time_limit_ms=1000, memory_limit_mb=128)


def test_run_tests_selects_run_enabled_cases_and_compares_output(monkeypatch):
    runner = FakeRunner(
        [
            ExecutionResult(
                status=ExecutionStatus.PASSED,
                stdout="6\n",
                execution_time_ms=10,
            ),
            ExecutionResult(
                status=ExecutionStatus.PASSED,
                stdout="wrong\n",
                execution_time_ms=11,
            ),
        ]
    )
    cases = [
        SimpleNamespace(
            id=1,
            display_order=1,
            input="3\n1 2 3",
            expected_output="6\n",
        ),
        SimpleNamespace(
            id=2,
            display_order=2,
            input="2\n5 7",
            expected_output="12\n",
        ),
    ]

    monkeypatch.setattr(
        "backend.app.services.execution.run_service.get_problem", lambda db, problem_id: problem()
    )
    monkeypatch.setattr(
        "backend.app.services.execution.run_service.list_test_cases_for_problem",
        lambda db, problem_id, run_visible_only: cases,
    )

    request = RunRequest(
        problem_id=1,
        language=RunLanguage.PYTHON,
        mode=RunMode.TEST_CASES,
        source_code="print(6)",
    )
    response = RunService({RunLanguage.PYTHON: runner}).execute(None, request)

    assert response.status is RunStatus.FAILED
    assert [result.status for result in response.results] == [
        RunStatus.PASSED,
        RunStatus.FAILED,
    ]
    assert [request.stdin for request in runner.requests] == [
        "3\n1 2 3",
        "2\n5 7",
    ]
    assert all(request.time_limit_ms == 1000 for request in runner.requests)
    assert all(request.memory_limit_mb == 128 for request in runner.requests)


def test_custom_input_does_not_load_test_cases(monkeypatch):
    runner = FakeRunner(
        [
            ExecutionResult(
                status=ExecutionStatus.PASSED,
                stdout="hello\n",
                execution_time_ms=8,
            )
        ]
    )
    monkeypatch.setattr(
        "backend.app.services.execution.run_service.get_problem", lambda db, problem_id: problem()
    )

    def unexpected_test_case_query(*args, **kwargs):
        raise AssertionError("custom input must not query stored test cases")

    monkeypatch.setattr(
        "backend.app.services.execution.run_service.list_test_cases_for_problem",
        unexpected_test_case_query,
    )

    request = RunRequest(
        problem_id=1,
        language=RunLanguage.PYTHON,
        mode=RunMode.CUSTOM_INPUT,
        source_code="print(input())",
        custom_input="hello\n",
    )
    response = RunService({RunLanguage.PYTHON: runner}).execute(None, request)

    assert response.status is RunStatus.PASSED
    assert len(response.results) == 1
    assert response.results[0].test_case_id is None
    assert response.results[0].expected_output is None
    assert response.results[0].input == "hello\n"
    assert response.results[0].stdout == "hello\n"


def test_execution_failure_is_preserved_per_test(monkeypatch):
    runner = FakeRunner(
        [
            ExecutionResult(
                status=ExecutionStatus.RUNTIME_ERROR,
                stderr="boom",
                exit_code=1,
                execution_time_ms=4,
            )
        ]
    )
    cases = [
        SimpleNamespace(
            id=7,
            display_order=1,
            input="1",
            expected_output="1",
        )
    ]
    monkeypatch.setattr(
        "backend.app.services.execution.run_service.get_problem", lambda db, problem_id: problem()
    )
    monkeypatch.setattr(
        "backend.app.services.execution.run_service.list_test_cases_for_problem",
        lambda db, problem_id, run_visible_only: cases,
    )

    request = RunRequest(
        problem_id=1,
        language=RunLanguage.CPP,
        source_code="int main() { return 1; }",
    )
    response = RunService({RunLanguage.CPP: runner}).execute(None, request)

    assert response.status is RunStatus.RUNTIME_ERROR
    assert response.results[0].status is RunStatus.RUNTIME_ERROR
    assert response.results[0].stderr == "boom"
