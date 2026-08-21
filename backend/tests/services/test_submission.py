from datetime import timezone

import pytest

from backend.app.core.execution import MAX_SOURCE_CODE_BYTES
from backend.app.models.problem import Difficulty, Problem
from backend.app.models.topic import Topic
from backend.app.models.submission import SubmissionStatus
from backend.app.services.submission import create_submission
from backend.app.services.test_case import list_submit_test_cases_for_problem


def create_problem(db):
    topic = Topic(
        name="Submission Service Topic",
        slug="submission-service-topic",
        display_order=1,
    )
    db.add(topic)
    db.flush()

    problem = Problem(
        topic_id=topic.id,
        title="Submission Service Problem",
        slug="submission-service-problem",
        statement="Submission service test problem.",
        constraints="1 <= n <= 1000",
        difficulty=Difficulty.EASY,
        tags=[],
        starter_code={"python": "", "cpp": ""},
        time_limit_ms=1000,
        memory_limit_mb=128,
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


def create_test_case(db, problem, *, submit_enabled, run_enabled, display_order):
    from backend.app.models.test_case import TestCase

    test_case = TestCase(
        problem_id=problem.id,
        input=f"input-{display_order}",
        expected_output=f"output-{display_order}",
        run_enabled=run_enabled,
        submit_enabled=submit_enabled,
        is_sample=False,
        display_order=display_order,
    )
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return test_case


def test_create_submission_creates_queued_submission(db, normal_user):
    problem = create_problem(db)

    submission = create_submission(
        db,
        user_id=normal_user.id,
        problem_id=problem.id,
        language="python",
        source_code="print(1 + 2)",
    )

    assert submission.id is not None
    assert submission.user_id == normal_user.id
    assert submission.problem_id == problem.id
    assert submission.language == "python"
    assert submission.source_code == "print(1 + 2)"
    assert submission.status is SubmissionStatus.QUEUED
    assert submission.verdict is None
    assert submission.completed_at is None
    assert submission.created_at.tzinfo is not None
    assert submission.updated_at.tzinfo is not None
    assert submission.created_at.astimezone(timezone.utc)


def test_create_submission_rejects_missing_problem(db, normal_user):
    with pytest.raises(ValueError, match="Problem not found"):
        create_submission(
            db,
            user_id=normal_user.id,
            problem_id=999999,
            language="python",
            source_code="print(1)",
        )


def test_create_submission_rejects_unsupported_language(db, normal_user):
    problem = create_problem(db)

    with pytest.raises(ValueError, match="Unsupported language"):
        create_submission(
            db,
            user_id=normal_user.id,
            problem_id=problem.id,
            language="java",
            source_code="class Main {}",
        )


def test_create_submission_rejects_empty_source(db, normal_user):
    problem = create_problem(db)

    with pytest.raises(ValueError, match="Source code must not be empty"):
        create_submission(
            db,
            user_id=normal_user.id,
            problem_id=problem.id,
            language="python",
            source_code="",
        )


def test_create_submission_enforces_source_code_byte_limit(db, normal_user):
    problem = create_problem(db)
    source_code = "x" * (MAX_SOURCE_CODE_BYTES + 1)

    with pytest.raises(ValueError, match="source_code exceeds"):
        create_submission(
            db,
            user_id=normal_user.id,
            problem_id=problem.id,
            language="python",
            source_code=source_code,
        )


def test_submit_test_case_selector_only_returns_submit_enabled_cases(db):
    problem = create_problem(db)
    run_only = create_test_case(
        db,
        problem,
        submit_enabled=False,
        run_enabled=True,
        display_order=1,
    )
    submit_only = create_test_case(
        db,
        problem,
        submit_enabled=True,
        run_enabled=False,
        display_order=2,
    )
    both = create_test_case(
        db,
        problem,
        submit_enabled=True,
        run_enabled=True,
        display_order=3,
    )

    cases = list_submit_test_cases_for_problem(db, problem.id)

    assert [case.id for case in cases] == [submit_only.id, both.id]
    assert run_only.id not in [case.id for case in cases]


def test_submit_test_case_selector_orders_by_display_order_then_id(db):
    problem = create_problem(db)
    first = create_test_case(
        db,
        problem,
        submit_enabled=True,
        run_enabled=True,
        display_order=2,
    )
    second = create_test_case(
        db,
        problem,
        submit_enabled=True,
        run_enabled=True,
        display_order=1,
    )

    cases = list_submit_test_cases_for_problem(db, problem.id)

    assert [case.id for case in cases] == [second.id, first.id]


def test_submit_test_case_selector_rejects_missing_problem(db):
    with pytest.raises(ValueError, match="Problem not found"):
        list_submit_test_cases_for_problem(db, 999999)
