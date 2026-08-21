from backend.app.models.problem import Difficulty, Problem
from backend.app.models.test_case import TestCase
from backend.app.services.submission import create_submission
from backend.app.models.submission import SubmissionStatus


def create_problem(db, *, starter_code=None):
    from backend.app.models.topic import Topic

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
        statement="Test problem.",
        constraints="1 <= n <= 100",
        difficulty=Difficulty.EASY,
        tags=[],
        starter_code=starter_code
        or {
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


def create_test_case(
    db,
    problem,
    *,
    display_order,
    submit_enabled=True,
):
    test_case = TestCase(
        problem_id=problem.id,
        input=f"{display_order}\n",
        expected_output=f"{display_order}\n",
        run_enabled=True,
        submit_enabled=submit_enabled,
        is_sample=False,
        display_order=display_order,
    )

    db.add(test_case)
    db.commit()
    db.refresh(test_case)

    return test_case


def test_create_submission(db, normal_user):
    problem = create_problem(db)

    first = create_test_case(
        db,
        problem,
        display_order=2,
    )
    second = create_test_case(
        db,
        problem,
        display_order=1,
    )

    result = create_submission(
        db,
        user_id=normal_user.id,
        problem_id=problem.id,
        language="python",
        source_code="print(1)",
    )

    submission = result.submission

    assert submission.id is not None
    assert submission.user_id == normal_user.id
    assert submission.problem_id == problem.id
    assert submission.language == "python"
    assert submission.source_code == "print(1)"
    assert submission.status is SubmissionStatus.QUEUED
    assert submission.verdict is None
    assert submission.completed_at is None
    assert submission.created_at is not None
    assert submission.updated_at is not None

    assert [case.id for case in result.test_cases] == [
        second.id,
        first.id,
    ]


def test_create_submission_rejects_unknown_problem(db, normal_user):
    import pytest

    with pytest.raises(ValueError, match="Problem not found"):
        create_submission(
            db,
            user_id=normal_user.id,
            problem_id=999999,
            language="python",
            source_code="print(1)",
        )


def test_create_submission_rejects_unsupported_language(
    db,
    normal_user,
):
    import pytest

    problem = create_problem(
        db,
        starter_code={"python": ""},
    )
    create_test_case(db, problem, display_order=1)

    with pytest.raises(ValueError, match="Unsupported language"):
        create_submission(
            db,
            user_id=normal_user.id,
            problem_id=problem.id,
            language="java",
            source_code="System.out.println(1);",
        )


def test_create_submission_rejects_problem_without_submit_cases(
    db,
    normal_user,
):
    import pytest

    problem = create_problem(db)
    create_test_case(
        db,
        problem,
        display_order=1,
        submit_enabled=False,
    )

    with pytest.raises(
        ValueError,
        match="no submit-enabled test cases",
    ):
        create_submission(
            db,
            user_id=normal_user.id,
            problem_id=problem.id,
            language="python",
            source_code="print(1)",
        )


def test_create_submission_ignores_run_only_cases(
    db,
    normal_user,
):
    problem = create_problem(db)

    create_test_case(
        db,
        problem,
        display_order=1,
        submit_enabled=False,
    )
    submit_case = create_test_case(
        db,
        problem,
        display_order=2,
        submit_enabled=True,
    )

    result = create_submission(
        db,
        user_id=normal_user.id,
        problem_id=problem.id,
        language="python",
        source_code="print(1)",
    )

    assert [case.id for case in result.test_cases] == [
        submit_case.id,
    ]
