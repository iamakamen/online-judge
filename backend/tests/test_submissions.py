from datetime import datetime, timezone

from backend.app.models.problem import Difficulty, Problem
from backend.app.models.topic import Topic
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


def create_problem(db):
    topic = Topic(
        name="Submission Test Topic",
        slug="submission-test-topic",
        display_order=1,
    )
    db.add(topic)
    db.flush()

    problem = Problem(
        topic_id=topic.id,
        title="Two Sum",
        slug="two-sum-submission-test",
        statement="Submission persistence test problem.",
        constraints="1 <= n <= 1000",
        difficulty=Difficulty.EASY,
        tags=[],
        starter_code={
            "python": "",
            "cpp": "",
        },
        time_limit_ms=1000,
        memory_limit_mb=128,
    )

    db.add(problem)
    db.commit()
    db.refresh(problem)

    return problem


def create_test_case(db, problem):
    test_case = TestCase(
        problem_id=problem.id,
        input="1 2\n",
        expected_output="3\n",
        run_enabled=True,
        submit_enabled=True,
        is_sample=False,
        display_order=1,
    )
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return test_case


def test_submission_persists_with_queued_status(db, normal_user):
    problem = create_problem(db)

    now = datetime.now(timezone.utc)

    submission = Submission(
        user_id=normal_user.id,
        problem_id=problem.id,
        language="python",
        source_code="print(1 + 2)",
        created_at=now,
        updated_at=now,
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    assert submission.id is not None
    assert submission.user_id == normal_user.id
    assert submission.problem_id == problem.id
    assert submission.language == "python"
    assert submission.source_code == "print(1 + 2)"
    assert submission.status is SubmissionStatus.QUEUED
    assert submission.verdict is None
    assert submission.completed_at is None


def test_submission_result_persists_and_round_trips_status(
    db,
    normal_user,
):
    problem = create_problem(db)
    test_case = create_test_case(db, problem)

    now = datetime.now(timezone.utc)

    submission = Submission(
        user_id=normal_user.id,
        problem_id=problem.id,
        language="python",
        source_code="print(3)",
        created_at=now,
        updated_at=now,
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    result = SubmissionResult(
        submission_id=submission.id,
        test_case_id=test_case.id,
        display_order=1,
        status=SubmissionResultStatus.PASSED,
        execution_time_ms=25,
        memory_used_mb=12,
        created_at=now,
    )

    db.add(result)
    db.commit()
    db.refresh(result)

    assert result.id is not None
    assert result.submission_id == submission.id
    assert result.test_case_id == test_case.id
    assert result.display_order == 1
    assert result.status is SubmissionResultStatus.PASSED
    assert result.execution_time_ms == 25
    assert result.memory_used_mb == 12


def test_submission_results_relationship(db, normal_user):
    problem = create_problem(db)
    test_case = create_test_case(db, problem)

    now = datetime.now(timezone.utc)

    submission = Submission(
        user_id=normal_user.id,
        problem_id=problem.id,
        language="python",
        source_code="print(3)",
        created_at=now,
        updated_at=now,
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    result = SubmissionResult(
        submission_id=submission.id,
        test_case_id=test_case.id,
        display_order=1,
        status=SubmissionResultStatus.PASSED,
        created_at=now,
    )

    submission.results.append(result)

    db.commit()
    db.refresh(submission)

    assert len(submission.results) == 1
    assert submission.results[0].id == result.id
    assert submission.results[0].status is SubmissionResultStatus.PASSED


def test_submission_delete_cascades_results(db, normal_user):
    problem = create_problem(db)
    test_case = create_test_case(db, problem)

    now = datetime.now(timezone.utc)

    submission = Submission(
        user_id=normal_user.id,
        problem_id=problem.id,
        language="python",
        source_code="print(3)",
        created_at=now,
        updated_at=now,
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    result = SubmissionResult(
        submission_id=submission.id,
        test_case_id=test_case.id,
        display_order=1,
        status=SubmissionResultStatus.PASSED,
        created_at=now,
    )

    db.add(result)
    db.commit()
    db.refresh(result)

    result_id = result.id

    db.delete(submission)
    db.commit()

    assert db.get(Submission, submission.id) is None
    assert db.get(SubmissionResult, result_id) is None


def test_submission_verdict_persists(db, normal_user):
    problem = create_problem(db)

    now = datetime.now(timezone.utc)

    submission = Submission(
        user_id=normal_user.id,
        problem_id=problem.id,
        language="python",
        source_code="print(3)",
        status=SubmissionStatus.COMPLETED,
        verdict=SubmissionVerdict.ACCEPTED,
        created_at=now,
        updated_at=now,
        completed_at=now,
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    assert submission.status is SubmissionStatus.COMPLETED
    assert submission.verdict is SubmissionVerdict.ACCEPTED
    assert submission.completed_at is not None
