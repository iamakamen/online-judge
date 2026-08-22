from datetime import datetime, timezone

from backend.app.models.problem import Difficulty, Problem
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
from backend.app.models.topic import Topic


def create_problem(db, *, starter_code=None):
    topic = Topic(
        name="Submission API Topic",
        slug="submission-api-topic",
        display_order=1,
    )
    db.add(topic)
    db.flush()

    problem = Problem(
        topic_id=topic.id,
        title="Submission API Problem",
        slug="submission-api-problem",
        statement="Test problem.",
        constraints="1 <= n <= 100",
        difficulty=Difficulty.EASY,
        tags=[],
        starter_code=starter_code or {
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


def create_test_case(db, problem, *, submit_enabled=True, display_order=1):
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


def create_submission(db, user, problem, *, status=SubmissionStatus.QUEUED,
                      verdict=None):
    now = datetime.now(timezone.utc)
    submission = Submission(
        user_id=user.id,
        problem_id=problem.id,
        language="python",
        source_code="print(1)",
        status=status,
        verdict=verdict,
        created_at=now,
        updated_at=now,
        completed_at=(now if status is not SubmissionStatus.QUEUED else None),
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def create_result(db, submission, test_case, *, status, display_order=None):
    result = SubmissionResult(
        submission_id=submission.id,
        test_case_id=test_case.id,
        display_order=(
            test_case.display_order
            if display_order is None
            else display_order
        ),
        status=status,
        execution_time_ms=12,
        memory_used_mb=3,
        created_at=datetime.now(timezone.utc),
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def test_create_submission_api(
    client,
    db,
    normal_user,
    user_token,
):
    problem = create_problem(db)
    create_test_case(db, problem)

    response = client.post(
        "/api/v1/submissions",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "problem_id": problem.id,
            "language": "python",
            "source_code": "print(1)",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["id"] is not None
    assert body["problem_id"] == problem.id
    assert body["language"] == "python"
    assert body["status"] == "queued"
    assert body["verdict"] is None
    assert body["completed_at"] is None

    submission = db.get(Submission, body["id"])

    assert submission is not None
    assert submission.user_id == normal_user.id
    assert submission.problem_id == problem.id
    assert submission.source_code == "print(1)"


def test_submission_owner_can_retrieve_submission_without_hidden_fields(
    client,
    db,
    normal_user,
    user_token,
):
    problem = create_problem(db)
    submission = create_submission(db, normal_user, problem)

    response = client.get(
        f"/api/v1/submissions/{submission.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == submission.id
    assert body["problem_id"] == problem.id
    assert body["language"] == "python"
    assert body["status"] == "queued"
    assert body["verdict"] is None
    assert body["results"] == []
    assert "source_code" not in body
    assert "input" not in body
    assert "expected_output" not in body
    assert "stdout" not in body
    assert "stderr" not in body


def test_submission_belonging_to_another_user_returns_404(
    client,
    db,
    normal_user,
    admin_user,
    admin_token,
):
    problem = create_problem(db)
    submission = create_submission(db, normal_user, problem)

    response = client.get(
        f"/api/v1/submissions/{submission.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 404


def test_missing_submission_returns_404(client, user_token):
    response = client.get(
        "/api/v1/submissions/999999",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 404


def test_running_submission_returns_ordered_partial_results(
    client,
    db,
    normal_user,
    user_token,
):
    problem = create_problem(db)
    first = create_test_case(db, problem, display_order=2)
    second = create_test_case(db, problem, display_order=1)
    submission = create_submission(
        db,
        normal_user,
        problem,
        status=SubmissionStatus.RUNNING,
    )
    create_result(
        db,
        submission,
        first,
        status=SubmissionResultStatus.PASSED,
    )
    create_result(
        db,
        submission,
        second,
        status=SubmissionResultStatus.WRONG_ANSWER,
    )

    response = client.get(
        f"/api/v1/submissions/{submission.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 200
    assert [item["display_order"] for item in response.json()["results"]] == [
        1,
        2,
    ]
    assert set(response.json()["results"][0]) == {
        "display_order",
        "status",
        "execution_time_ms",
        "memory_used_mb",
        "created_at",
    }


def test_completed_submission_returns_results_in_display_order_then_id(
    client,
    db,
    normal_user,
    user_token,
):
    problem = create_problem(db)
    first = create_test_case(db, problem, display_order=2)
    second = create_test_case(db, problem, display_order=1)
    third = create_test_case(db, problem, display_order=1)
    submission = create_submission(
        db,
        normal_user,
        problem,
        status=SubmissionStatus.COMPLETED,
        verdict=SubmissionVerdict.ACCEPTED,
    )
    create_result(
        db,
        submission,
        first,
        status=SubmissionResultStatus.RUNTIME_ERROR,
    )
    second_result = create_result(
        db,
        submission,
        second,
        status=SubmissionResultStatus.PASSED,
    )
    third_result = create_result(
        db,
        submission,
        third,
        status=SubmissionResultStatus.WRONG_ANSWER,
    )

    response = client.get(
        f"/api/v1/submissions/{submission.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    results = response.json()["results"]
    assert response.status_code == 200
    assert [item["display_order"] for item in results] == [1, 1, 2]
    assert [item["status"] for item in results] == [
        "passed",
        "wrong_answer",
        "runtime_error",
    ]
    assert set(results[0]) == {
        "display_order",
        "status",
        "execution_time_ms",
        "memory_used_mb",
        "created_at",
    }


def test_failed_submission_returns_persisted_results(
    client,
    db,
    normal_user,
    user_token,
):
    problem = create_problem(db)
    test_case = create_test_case(db, problem)
    submission = create_submission(
        db,
        normal_user,
        problem,
        status=SubmissionStatus.FAILED,
        verdict=SubmissionVerdict.SYSTEM_ERROR,
    )
    create_result(
        db,
        submission,
        test_case,
        status=SubmissionResultStatus.SYSTEM_ERROR,
    )

    response = client.get(
        f"/api/v1/submissions/{submission.id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "failed"
    assert response.json()["results"][0]["status"] == "system_error"


def test_create_submission_api_requires_authentication(
    client,
    db,
):
    problem = create_problem(db)
    create_test_case(db, problem)

    response = client.post(
        "/api/v1/submissions",
        json={
            "problem_id": problem.id,
            "language": "python",
            "source_code": "print(1)",
        },
    )

    assert response.status_code in (401, 403)


def test_create_submission_api_rejects_unknown_problem(
    client,
    user_token,
):
    response = client.post(
        "/api/v1/submissions",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "problem_id": 999999,
            "language": "python",
            "source_code": "print(1)",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Problem not found"


def test_create_submission_api_rejects_unsupported_language(
    client,
    db,
    user_token,
):
    problem = create_problem(
        db,
        starter_code={"python": ""},
    )
    create_test_case(db, problem)

    response = client.post(
        "/api/v1/submissions",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "problem_id": problem.id,
            "language": "java",
            "source_code": "System.out.println(1);",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported language"


def test_create_submission_api_requires_submit_cases(
    client,
    db,
    user_token,
):
    problem = create_problem(db)
    create_test_case(
        db,
        problem,
        submit_enabled=False,
    )

    response = client.post(
        "/api/v1/submissions",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "problem_id": problem.id,
            "language": "python",
            "source_code": "print(1)",
        },
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Problem has no submit-enabled test cases"
    )
