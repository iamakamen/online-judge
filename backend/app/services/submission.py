from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.models.problem import Problem
from backend.app.models.submission import Submission, SubmissionStatus
from backend.app.models.test_case import TestCase
from backend.app.services.problem import get_problem
from backend.app.services.test_case import list_submit_test_cases_for_problem


@dataclass
class SubmissionCreationResult:
    submission: Submission
    test_cases: list[TestCase]


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
