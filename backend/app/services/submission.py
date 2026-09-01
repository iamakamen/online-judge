from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from contextlib import contextmanager
from collections.abc import Iterator

from sqlalchemy import delete, select, text, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session, selectinload

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
from backend.app.models.user import User  # noqa: F401 - registers FK metadata
from backend.app.models.user_problem_progress import UserProblemProgress
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
from backend.app.services.accepted_solution import upsert_accepted_solution
from backend.app.services.test_case import list_submit_test_cases_for_problem


@dataclass
class SubmissionCreationResult:
    submission: Submission
    test_cases: list[TestCase]


class AcceptedProgressPersistenceError(RuntimeError):
    """The Accepted terminal transaction could not persist solved progress."""


def get_submission_for_user(
    db: Session,
    *,
    submission_id: int,
    user_id: int,
) -> Submission:
    """Return one owner's submission with results in deterministic order."""
    submission = db.scalar(
        select(Submission)
        .options(selectinload(Submission.results))
        .where(
            Submission.id == submission_id,
            Submission.user_id == user_id,
        )
    )
    if submission is None:
        raise ValueError("Submission not found")

    submission.results.sort(
        key=lambda result: (result.display_order, result.id)
    )
    return submission


@contextmanager
def submission_execution_fence(
    db: Session,
    submission_id: int,
) -> Iterator[bool]:
    """Hold a PostgreSQL session advisory lock for one judging lifecycle."""
    if not hasattr(db, "connection"):
        # Lightweight worker fakes do not expose a SQLAlchemy bind.
        yield True
        return

    connection = db.connection()
    lock_key = f"submission:{submission_id}"
    acquired = bool(
        connection.execute(
            text(
                "SELECT pg_try_advisory_lock(hashtextextended(:lock_key, 0))"
            ),
            {"lock_key": lock_key},
        ).scalar()
    )
    if not acquired:
        yield False
        return

    db.info["submission_execution_connection"] = connection
    try:
        yield True
    finally:
        try:
            if not connection.invalidated:
                connection.execute(
                    text(
                        "SELECT pg_advisory_unlock(hashtextextended(:lock_key, 0))"
                    ),
                    {"lock_key": lock_key},
                )
        finally:
            db.info.pop("submission_execution_connection", None)


def _submission_fence_connection_invalidated(db: Session) -> bool:
    connection = db.info.get("submission_execution_connection")
    return bool(connection is not None and connection.invalidated)


def reset_stale_submission(
    db: Session,
    submission_id: int,
    *,
    stale_cutoff: datetime,
) -> bool:
    """Reset one stale running submission and discard partial results."""
    now = datetime.now(timezone.utc)
    result = db.execute(
        update(Submission)
        .where(
            Submission.id == submission_id,
            Submission.status == SubmissionStatus.RUNNING,
            Submission.updated_at <= stale_cutoff,
        )
        .values(
            status=SubmissionStatus.QUEUED,
            verdict=None,
            completed_at=None,
            updated_at=now,
        )
    )
    if result.rowcount != 1:
        db.rollback()
        return False

    db.execute(
        delete(SubmissionResult).where(
            SubmissionResult.submission_id == submission_id
        )
    )
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True


def fail_submission_with_system_error(
    db: Session,
    submission_id: int,
) -> bool:
    """Persist a terminal infrastructure failure for an active submission."""
    now = datetime.now(timezone.utc)
    result = db.execute(
        update(Submission)
        .where(
            Submission.id == submission_id,
            Submission.status.in_(
                [SubmissionStatus.QUEUED, SubmissionStatus.RUNNING]
            ),
        )
        .values(
            status=SubmissionStatus.FAILED,
            verdict=SubmissionVerdict.SYSTEM_ERROR,
            completed_at=now,
            updated_at=now,
        )
    )
    if result.rowcount != 1:
        db.rollback()
        return False
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True


_EXECUTION_RESULT_STATUSES = {
    ExecutionStatus.COMPILE_ERROR: SubmissionResultStatus.COMPILE_ERROR,
    ExecutionStatus.RUNTIME_ERROR: SubmissionResultStatus.RUNTIME_ERROR,
    ExecutionStatus.TIME_LIMIT_EXCEEDED: SubmissionResultStatus.TIME_LIMIT_EXCEEDED,
    ExecutionStatus.MEMORY_LIMIT_EXCEEDED: SubmissionResultStatus.MEMORY_LIMIT_EXCEEDED,
    ExecutionStatus.OUTPUT_LIMIT_EXCEEDED: SubmissionResultStatus.OUTPUT_LIMIT_EXCEEDED,
    ExecutionStatus.SYSTEM_ERROR: SubmissionResultStatus.SYSTEM_ERROR,
}


def claim_submission(db: Session, submission_id: int) -> Submission:
    """Atomically transition one queued submission to running."""
    now = datetime.now(timezone.utc)
    result = db.execute(
        update(Submission)
        .where(
            Submission.id == submission_id,
            Submission.status == SubmissionStatus.QUEUED,
        )
        .values(
            status=SubmissionStatus.RUNNING,
            updated_at=now,
        )
    )

    if result.rowcount != 1:
        db.rollback()
        submission = db.get(Submission, submission_id)
        if submission is None:
            raise ValueError("Submission not found")
        raise ValueError("Submission is not queued")

    try:
        db.commit()
        submission = db.get(Submission, submission_id)
    except Exception:
        db.rollback()
        raise

    if submission is None:
        raise ValueError("Submission not found")
    return submission


def upsert_solved_progress(
    db: Session,
    *,
    user_id: int,
    problem_id: int,
    now: datetime,
) -> None:
    """Mark a user's problem as solved without ever downgrading it."""
    db.execute(
        pg_insert(UserProblemProgress)
        .values(
            user_id=user_id,
            problem_id=problem_id,
            solved=True,
            created_at=now,
            updated_at=now,
        )
        .on_conflict_do_update(
            index_elements=[
                UserProblemProgress.user_id,
                UserProblemProgress.problem_id,
            ],
            set_={
                "solved": True,
                "updated_at": now,
            },
        )
    )


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
        submission = claim_submission(db, submission.id)

        return self._execute_claimed(
            db,
            submission,
            problem,
            test_cases,
            runner,
        )

    def execute_claimed(
        self,
        db: Session,
        submission: Submission,
    ) -> Submission:
        """Judge a submission already claimed by the current worker."""
        if submission.status is not SubmissionStatus.RUNNING:
            raise ValueError("Submission is not running")

        try:
            problem = get_problem(db, submission.problem_id)
            test_cases = list_submit_test_cases_for_problem(db, problem.id)
            if not test_cases:
                raise ValueError("Problem has no submit-enabled test cases")
            runner = self._runner_for(submission.language)
            return self._execute_claimed(
                db,
                submission,
                problem,
                test_cases,
                runner,
            )
        except AcceptedProgressPersistenceError:
            db.rollback()
            raise
        except Exception:
            if _submission_fence_connection_invalidated(db):
                raise
            self._mark_failed(db, submission.id)
            return db.get(Submission, submission.id) or submission

    def _execute_claimed(
        self,
        db: Session,
        submission: Submission,
        problem: Problem,
        test_cases: list[TestCase],
        runner: ExecutionRunner,
    ) -> Submission:
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
        except AcceptedProgressPersistenceError:
            db.rollback()
            raise
        except Exception:
            if _submission_fence_connection_invalidated(db):
                raise
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
            if verdict is SubmissionVerdict.ACCEPTED:
                upsert_solved_progress(
                    db,
                    user_id=submission.user_id,
                    problem_id=submission.problem_id,
                    now=now,
                )
                upsert_accepted_solution(
                    db,
                    user_id=submission.user_id,
                    problem_id=submission.problem_id,
                    language=submission.language,
                    source_code=submission.source_code,
                    now=now,
                )
            db.commit()
            db.refresh(submission)
        except Exception as exc:
            db.rollback()
            if verdict is SubmissionVerdict.ACCEPTED:
                raise AcceptedProgressPersistenceError(
                    "Could not persist Accepted progress"
                ) from exc
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
