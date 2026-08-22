from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.models.problem import Problem
from backend.app.models.submission import (
    Submission,
    SubmissionStatus,
    SubmissionVerdict,
)
from backend.app.models.submission_result import (
    SubmissionResult,
    SubmissionResultStatus,
)
from backend.app.models.test_case import TestCase
from backend.app.schemas.run import RunLanguage
from backend.app.services.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionRunner,
    ExecutionStatus,
)
from backend.app.services.execution.run_service import (
    _RUNNER_TYPES,
    _outputs_match,
)
from backend.app.services.problem import get_problem
from backend.app.services.test_case import list_submit_test_cases_for_problem


@dataclass
class SubmissionCreationResult:
    submission: Submission
    test_cases: list[TestCase]


_EXECUTION_RESULT_STATUSES = {
    ExecutionStatus.COMPILE_ERROR: SubmissionResultStatus.COMPILE_ERROR,
    ExecutionStatus.RUNTIME_ERROR: SubmissionResultStatus.RUNTIME_ERROR,
    ExecutionStatus.TIME_LIMIT_EXCEEDED: SubmissionResultStatus.TIME_LIMIT_EXCEEDED,
    ExecutionStatus.MEMORY_LIMIT_EXCEEDED: SubmissionResultStatus.MEMORY_LIMIT_EXCEEDED,
    ExecutionStatus.OUTPUT_LIMIT_EXCEEDED: SubmissionResultStatus.OUTPUT_LIMIT_EXCEEDED,
    ExecutionStatus.SYSTEM_ERROR: SubmissionResultStatus.SYSTEM_ERROR,
}


class SubmissionJudgeService:
    """Judge a persisted submission using the existing execution runners."""

    def __init__(
        self,
        runners: dict[str, ExecutionRunner] | None = None,
    ) -> None:
        self._runners = dict(runners or {})

    def execute(self, db: Session, submission_id: int) -> Submission:
        submission = db.get(Submission, submission_id)
        if submission is None:
            raise ValueError("Submission not found")
        if submission.status is not SubmissionStatus.QUEUED:
            raise ValueError("Submission is not queued")

        problem: Problem = get_problem(db, submission.problem_id)
        test_cases = list_submit_test_cases_for_problem(db, problem.id)
        if not test_cases:
            raise ValueError("Problem has no submit-enabled test cases")

        runner = self._runner_for(submission.language)
        self._transition_to_running(db, submission)

        try:
            for test_case in test_cases:
                execution = runner.execute(
                    ExecutionRequest(
                        source_code=submission.source_code,
                        stdin=test_case.input,
                        time_limit_ms=problem.time_limit_ms,
                        memory_limit_mb=problem.memory_limit_mb,
                    )
                )
                result_status = self._result_status(
                    execution,
                    test_case.expected_output,
                )
                self._persist_result(
                    db,
                    submission,
                    test_case,
                    result_status,
                    execution,
                )

                if result_status is not SubmissionResultStatus.PASSED:
                    return self._complete(
                        db,
                        submission,
                        SubmissionVerdict(result_status.value),
                    )

            return self._complete(db, submission, SubmissionVerdict.ACCEPTED)
        except Exception:
            self._mark_failed(db, submission.id)
            return db.get(Submission, submission.id) or submission

    def _runner_for(self, language: str) -> ExecutionRunner:
        if language in self._runners:
            return self._runners[language]

        try:
            run_language = RunLanguage(language)
        except ValueError as exc:
            raise ValueError(f"Unsupported language: {language}") from exc

        runner_type = _RUNNER_TYPES.get(run_language)
        if runner_type is None:
            raise ValueError(f"Unsupported language: {language}")
        return runner_type()

    @staticmethod
    def _result_status(
        execution: ExecutionResult,
        expected_output: str,
    ) -> SubmissionResultStatus:
        if execution.status is ExecutionStatus.PASSED:
            if _outputs_match(execution.stdout, expected_output):
                return SubmissionResultStatus.PASSED
            return SubmissionResultStatus.WRONG_ANSWER

        return _EXECUTION_RESULT_STATUSES.get(
            execution.status,
            SubmissionResultStatus.SYSTEM_ERROR,
        )

    @staticmethod
    def _transition_to_running(
        db: Session,
        submission: Submission,
    ) -> None:
        submission.status = SubmissionStatus.RUNNING
        submission.updated_at = datetime.now(timezone.utc)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def _persist_result(
        db: Session,
        submission: Submission,
        test_case: TestCase,
        result_status: SubmissionResultStatus,
        execution: ExecutionResult,
    ) -> None:
        db.add(
            SubmissionResult(
                submission_id=submission.id,
                test_case_id=test_case.id,
                display_order=test_case.display_order,
                status=result_status,
                execution_time_ms=execution.execution_time_ms,
                memory_used_mb=execution.memory_used_mb,
                created_at=datetime.now(timezone.utc),
            )
        )
        submission.updated_at = datetime.now(timezone.utc)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

    @staticmethod
    def _complete(
        db: Session,
        submission: Submission,
        verdict: SubmissionVerdict,
    ) -> Submission:
        now = datetime.now(timezone.utc)
        submission.status = SubmissionStatus.COMPLETED
        submission.verdict = verdict
        submission.completed_at = now
        submission.updated_at = now
        try:
            db.commit()
            db.refresh(submission)
        except Exception:
            db.rollback()
            raise
        return submission

    @staticmethod
    def _mark_failed(db: Session, submission_id: int) -> None:
        try:
            db.rollback()
            submission = db.get(Submission, submission_id)
            if submission is None or submission.status is not SubmissionStatus.RUNNING:
                return

            now = datetime.now(timezone.utc)
            submission.status = SubmissionStatus.FAILED
            submission.verdict = SubmissionVerdict.SYSTEM_ERROR
            submission.completed_at = now
            submission.updated_at = now
            db.commit()
        except Exception:
            db.rollback()


def create_submission(
    db: Session,
    *,
    user_id: int,
    problem_id: int,
    language: str,
    source_code: str,
) -> SubmissionCreationResult:
    problem: Problem = get_problem(db, problem_id)

    if language not in problem.starter_code:
        raise ValueError("Unsupported language")

    test_cases = list_submit_test_cases_for_problem(
        db,
        problem_id,
    )

    if not test_cases:
        raise ValueError("Problem has no submit-enabled test cases")

    now = datetime.now(timezone.utc)

    submission = Submission(
        user_id=user_id,
        problem_id=problem.id,
        language=language,
        source_code=source_code,
        status=SubmissionStatus.QUEUED,
        verdict=None,
        created_at=now,
        updated_at=now,
        completed_at=None,
    )

    db.add(submission)

    try:
        db.commit()
        db.refresh(submission)
    except Exception:
        db.rollback()
        raise

    return SubmissionCreationResult(
        submission=submission,
        test_cases=test_cases,
    )
