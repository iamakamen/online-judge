from backend.app.models.problem import Difficulty
from backend.app.models.user import User, UserRole
from backend.app.models.user_problem_progress import UserProblemProgress
from backend.app.services.password import hash_password
from backend.app.services.authentication import create_authenticated_session


def create_topic(client, admin_headers, name="Test Topic", slug="test-topic"):
    response = client.post(
        "/api/v1/topics",
        headers=admin_headers,
        json={
            "name": name,
            "slug": slug,
            "display_order": 1,
        },
    )
    assert response.status_code == 201
    return response.json()


def create_problem(
    client,
    admin_headers,
    topic_id,
    *,
    slug,
    difficulty="EASY",
    tags=None,
):
    response = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json={
            "topic_id": topic_id,
            "title": slug.replace("-", " ").title(),
            "slug": slug,
            "statement": "Test problem statement.",
            "constraints": "Test problem constraints.",
            "difficulty": difficulty,
            "tags": tags or ["array"],
            "starter_code": {
                "python": "print('test')",
                "cpp": "#include <iostream>\nint main() { return 0; }",
            },
            "time_limit_ms": 1000,
            "memory_limit_mb": 128,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_problem_list_returns_solved_false_without_progress(
    client,
    admin_headers,
    user_headers,
):
    topic = create_topic(client, admin_headers)
    create_problem(
        client,
        admin_headers,
        topic["id"],
        slug="unsolved-problem",
    )

    response = client.get(
        "/api/v1/problems",
        headers=user_headers,
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["solved"] is False


def test_problem_list_returns_user_specific_solved_state(
    client,
    admin_headers,
    user_headers,
    normal_user,
    db,
):
    topic = create_topic(client, admin_headers)
    first = create_problem(
        client,
        admin_headers,
        topic["id"],
        slug="first-problem",
    )
    second = create_problem(
        client,
        admin_headers,
        topic["id"],
        slug="second-problem",
    )

    db.add(
        UserProblemProgress(
            user_id=normal_user.id,
            problem_id=first["id"],
            solved=True,
        )
    )
    db.commit()

    response = client.get(
        "/api/v1/problems",
        headers=user_headers,
    )

    assert response.status_code == 200
    solved_by_slug = {
        item["slug"]: item["solved"]
        for item in response.json()["items"]
    }

    assert solved_by_slug["first-problem"] is True
    assert solved_by_slug["second-problem"] is False


def test_problem_list_does_not_leak_another_users_solved_state(
    client,
    admin_headers,
    user_headers,
    normal_user,
    db,
):
    topic = create_topic(client, admin_headers)
    first = create_problem(
        client,
        admin_headers,
        topic["id"],
        slug="first-problem",
    )
    second = create_problem(
        client,
        admin_headers,
        topic["id"],
        slug="second-problem",
    )

    other_user = User(
        first_name="Other",
        last_name="User",
        username="other_user",
        email="other_user@example.com",
        password_hash=hash_password("TestPassword123!"),
        role=UserRole.USER,
        email_verified=True,
    )
    db.add(other_user)
    db.commit()
    db.refresh(other_user)

    db.add_all(
        [
            UserProblemProgress(
                user_id=normal_user.id,
                problem_id=first["id"],
                solved=True,
            ),
            UserProblemProgress(
                user_id=other_user.id,
                problem_id=second["id"],
                solved=True,
            ),
        ]
    )
    db.commit()

    other_access_token, _ = create_authenticated_session(db, other_user)
    other_headers = {
        "Authorization": f"Bearer {other_access_token}",
    }

    first_response = client.get(
        "/api/v1/problems",
        headers=user_headers,
    )
    second_response = client.get(
        "/api/v1/problems",
        headers=other_headers,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_states = {
        item["slug"]: item["solved"]
        for item in first_response.json()["items"]
    }
    second_states = {
        item["slug"]: item["solved"]
        for item in second_response.json()["items"]
    }

    assert first_states == {
        "first-problem": True,
        "second-problem": False,
    }
    assert second_states == {
        "first-problem": False,
        "second-problem": True,
    }


def test_problem_list_supports_multiple_tags_with_and_semantics(
    client,
    admin_headers,
    user_headers,
):
    topic = create_topic(client, admin_headers)
    create_problem(
        client,
        admin_headers,
        topic["id"],
        slug="array-hash",
        tags=["array", "hash-map"],
    )
    create_problem(
        client,
        admin_headers,
        topic["id"],
        slug="array-only",
        tags=["array"],
    )
    create_problem(
        client,
        admin_headers,
        topic["id"],
        slug="hash-only",
        tags=["hash-map"],
    )

    response = client.get(
        "/api/v1/problems?tags=array&tags=hash-map",
        headers=user_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["slug"] == "array-hash"


def test_problem_list_combines_difficulty_and_multiple_tags(
    client,
    admin_headers,
    user_headers,
):
    topic = create_topic(client, admin_headers)
    create_problem(
        client,
        admin_headers,
        topic["id"],
        slug="matching-medium",
        difficulty="MEDIUM",
        tags=["array", "hash-map"],
    )
    create_problem(
        client,
        admin_headers,
        topic["id"],
        slug="easy-same-tags",
        difficulty="EASY",
        tags=["array", "hash-map"],
    )
    create_problem(
        client,
        admin_headers,
        topic["id"],
        slug="medium-one-tag",
        difficulty="MEDIUM",
        tags=["array"],
    )

    response = client.get(
        "/api/v1/problems?difficulty=MEDIUM&tags=array&tags=hash-map",
        headers=user_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["slug"] == "matching-medium"


def test_problem_list_preserves_topic_filter_and_pagination(
    client,
    admin_headers,
    user_headers,
):
    first_topic = create_topic(
        client,
        admin_headers,
        name="First Topic",
        slug="first-topic",
    )
    second_topic = create_topic(
        client,
        admin_headers,
        name="Second Topic",
        slug="second-topic",
    )

    for index in range(3):
        create_problem(
            client,
            admin_headers,
            first_topic["id"],
            slug=f"first-{index}",
        )

    create_problem(
        client,
        admin_headers,
        second_topic["id"],
        slug="second-only",
    )

    response = client.get(
        f"/api/v1/problems?topic_id={first_topic['id']}&page=1&page_size=2",
        headers=user_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert body["total_pages"] == 2
    assert len(body["items"]) == 2
    assert all(item["topic_id"] == first_topic["id"] for item in body["items"])


def test_problem_list_does_not_expose_test_case_data(
    client,
    admin_headers,
    user_headers,
):
    topic = create_topic(client, admin_headers)
    create_problem(
        client,
        admin_headers,
        topic["id"],
        slug="safe-list-problem",
    )

    response = client.get(
        "/api/v1/problems",
        headers=user_headers,
    )

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert "statement" not in item
    assert "starter_code" not in item
    assert "test_cases" not in item
    assert "expected_output" not in item
