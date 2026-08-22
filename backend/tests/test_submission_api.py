from backend.app.models.problem import Difficulty, Problem
from backend.app.models.submission import Submission
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
