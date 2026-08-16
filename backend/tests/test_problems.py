from backend.app.models.problem import Difficulty
from backend.app.models.test_case import TestCase


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


def problem_payload(topic_id, slug="test-problem"):
    return {
        "topic_id": topic_id,
        "title": "Test Problem",
        "slug": slug,
        "statement": "Test problem statement.",
        "constraints": "Test problem constraints.",
        "difficulty": "EASY",
        "tags": ["array", "hash-map"],
        "starter_code": {
            "python": "print('test')",
            "cpp": "#include <iostream>\nint main() { return 0; }",
        },
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    }


def test_list_problems_requires_authentication(client):
    response = client.get("/api/v1/problems")

    assert response.status_code == 401


def test_get_problem_requires_authentication(client):
    response = client.get("/api/v1/problems/1")

    assert response.status_code == 401


def test_get_problem_by_slug_requires_authentication(client):
    response = client.get("/api/v1/problems/by-slug/test-problem")

    assert response.status_code == 401


def test_create_problem_requires_authentication(client):
    response = client.post(
        "/api/v1/problems",
        json=problem_payload(1),
    )

    assert response.status_code == 401


def test_update_problem_requires_authentication(client):
    response = client.patch(
        "/api/v1/problems/1",
        json={"title": "Unauthorized"},
    )

    assert response.status_code == 401


def test_delete_problem_requires_authentication(client):
    response = client.delete("/api/v1/problems/1")

    assert response.status_code == 401


def test_list_problems_as_user(client, user_headers):
    response = client.get(
        "/api/v1/problems",
        headers=user_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert "items" in body
    assert "total" in body
    assert "page" in body
    assert "page_size" in body
    assert "total_pages" in body


def test_get_problem_as_user(client, admin_headers, user_headers):
    topic = create_topic(client, admin_headers)

    create_response = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=problem_payload(topic["id"]),
    )

    assert create_response.status_code == 201

    problem_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/problems/{problem_id}",
        headers=user_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == problem_id


def test_user_cannot_create_problem(client, user_headers):
    response = client.post(
        "/api/v1/problems",
        headers=user_headers,
        json=problem_payload(1),
    )

    assert response.status_code == 403


def test_user_cannot_update_problem(client, user_headers):
    response = client.patch(
        "/api/v1/problems/1",
        headers=user_headers,
        json={
            "title": "Should Not Update",
        },
    )

    assert response.status_code == 403


def test_user_cannot_delete_problem(client, user_headers):
    response = client.delete(
        "/api/v1/problems/1",
        headers=user_headers,
    )

    assert response.status_code == 403


def test_admin_can_create_problem(client, admin_headers):
    topic = create_topic(client, admin_headers)

    response = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=problem_payload(topic["id"]),
    )

    assert response.status_code == 201

    body = response.json()

    assert body["topic_id"] == topic["id"]
    assert body["title"] == "Test Problem"
    assert body["slug"] == "test-problem"
    assert body["constraints"] == "Test problem constraints."
    assert body["difficulty"] == "EASY"
    assert body["tags"] == ["array", "hash-map"]
    assert body["time_limit_ms"] == 1000
    assert body["memory_limit_mb"] == 128
    assert body["created_by_user_id"] is not None


def test_create_problem_with_missing_topic_returns_404(
    client,
    admin_headers,
):
    response = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=problem_payload(999999),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Topic not found"


def test_duplicate_problem_slug_returns_conflict(
    client,
    admin_headers,
):
    topic = create_topic(client, admin_headers)

    payload = problem_payload(topic["id"])

    first_response = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json={
            **payload,
            "title": "Another Problem",
        },
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Problem slug already exists"


def test_create_problem_rejects_invalid_limits(
    client,
    admin_headers,
):
    topic = create_topic(client, admin_headers)

    payload = problem_payload(topic["id"])
    payload["time_limit_ms"] = 0

    response = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=payload,
    )

    assert response.status_code == 422

    payload = problem_payload(
        topic["id"],
        slug="invalid-memory-limit",
    )
    payload["memory_limit_mb"] = 0

    response = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=payload,
    )

    assert response.status_code == 422


def test_get_missing_problem_returns_404(
    client,
    admin_headers,
):
    response = client.get(
        "/api/v1/problems/999999",
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Problem not found"


def test_get_problem_by_slug_as_user(client, admin_headers, user_headers):
    topic = create_topic(client, admin_headers)
    payload = problem_payload(topic["id"])
    payload["constraints"] = "1 <= n <= 1000"

    create_response = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=payload,
    )

    assert create_response.status_code == 201

    response = client.get(
        "/api/v1/problems/by-slug/test-problem",
        headers=user_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == "test-problem"
    assert body["title"] == "Test Problem"
    assert body["constraints"] == "1 <= n <= 1000"


def test_get_missing_problem_by_slug_returns_404(client, user_headers):
    response = client.get(
        "/api/v1/problems/by-slug/does-not-exist",
        headers=user_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Problem not found"


def test_admin_can_update_problem(
    client,
    admin_headers,
):
    topic = create_topic(client, admin_headers)

    create_response = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=problem_payload(topic["id"]),
    )

    assert create_response.status_code == 201

    problem_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/problems/{problem_id}",
        headers=admin_headers,
        json={
            "title": "Updated Problem",
            "difficulty": "MEDIUM",
            "tags": ["array", "updated"],
            "constraints": "Updated problem constraints.",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == problem_id
    assert body["title"] == "Updated Problem"
    assert body["difficulty"] == "MEDIUM"
    assert body["tags"] == ["array", "updated"]

    assert body["slug"] == "test-problem"
    assert body["statement"] == "Test problem statement."
    assert body["constraints"] == "Updated problem constraints."
    assert body["time_limit_ms"] == 1000
    assert body["memory_limit_mb"] == 128


def test_update_problem_with_missing_topic_returns_404(
    client,
    admin_headers,
):
    topic = create_topic(client, admin_headers)

    create_response = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=problem_payload(topic["id"]),
    )

    assert create_response.status_code == 201

    problem_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/problems/{problem_id}",
        headers=admin_headers,
        json={
            "topic_id": 999999,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Topic not found"


def test_update_problem_duplicate_slug_returns_conflict(
    client,
    admin_headers,
):
    topic = create_topic(client, admin_headers)

    first = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=problem_payload(
            topic["id"],
            slug="first-problem",
        ),
    )

    second = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=problem_payload(
            topic["id"],
            slug="second-problem",
        ),
    )

    assert first.status_code == 201
    assert second.status_code == 201

    second_id = second.json()["id"]

    response = client.patch(
        f"/api/v1/problems/{second_id}",
        headers=admin_headers,
        json={
            "slug": "first-problem",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Problem slug already exists"


def test_admin_can_delete_problem(
    client,
    admin_headers,
):
    topic = create_topic(client, admin_headers)

    create_response = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=problem_payload(topic["id"]),
    )

    assert create_response.status_code == 201

    problem_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/problems/{problem_id}",
        headers=admin_headers,
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/problems/{problem_id}",
        headers=admin_headers,
    )

    assert get_response.status_code == 404


def test_delete_problem_cascades_test_cases(
    client,
    admin_headers,
    db,
):
    topic = create_topic(client, admin_headers)

    create_response = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=problem_payload(topic["id"]),
    )

    assert create_response.status_code == 201

    problem_id = create_response.json()["id"]

    test_case_response = client.post(
        f"/api/v1/problems/{problem_id}/test-cases",
        headers=admin_headers,
        json={
            "input": "1 2 3",
            "expected_output": "6",
            "run_enabled": True,
            "submit_enabled": True,
            "is_sample": True,
            "display_order": 1,
        },
    )

    assert test_case_response.status_code == 201

    response = client.delete(
        f"/api/v1/problems/{problem_id}",
        headers=admin_headers,
    )

    assert response.status_code == 204

    remaining = (
        db.query(TestCase)
        .filter(TestCase.problem_id == problem_id)
        .count()
    )

    assert remaining == 0


def test_problem_pagination(
    client,
    admin_headers,
    user_headers,
):
    topic = create_topic(client, admin_headers)

    for index in range(3):
        response = client.post(
            "/api/v1/problems",
            headers=admin_headers,
            json=problem_payload(
                topic["id"],
                slug=f"pagination-problem-{index}",
            ),
        )

        assert response.status_code == 201

    response = client.get(
        "/api/v1/problems?page=1&page_size=2",
        headers=user_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 3
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert body["total_pages"] == 2
    assert len(body["items"]) == 2


def test_problem_filters(
    client,
    admin_headers,
    user_headers,
):
    arrays = create_topic(
        client,
        admin_headers,
        name="Arrays",
        slug="arrays",
    )

    strings = create_topic(
        client,
        admin_headers,
        name="Strings",
        slug="strings",
    )

    first_payload = problem_payload(
        arrays["id"],
        slug="array-easy",
    )

    first_payload["tags"] = ["array"]

    first = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=first_payload,
    )

    assert first.status_code == 201

    second_payload = problem_payload(
        strings["id"],
        slug="string-hard",
    )

    second_payload["difficulty"] = "HARD"
    second_payload["tags"] = ["string"]

    second = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=second_payload,
    )

    assert second.status_code == 201

    response = client.get(
        f"/api/v1/problems?topic_id={arrays['id']}",
        headers=user_headers,
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["slug"] == "array-easy"

    response = client.get(
        "/api/v1/problems?difficulty=HARD",
        headers=user_headers,
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["slug"] == "string-hard"

    response = client.get(
        "/api/v1/problems?tag=array",
        headers=user_headers,
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["slug"] == "array-easy"


def test_hidden_test_cases_are_not_exposed(
    client,
    admin_headers,
    user_headers,
):
    topic = create_topic(client, admin_headers)

    create_response = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=problem_payload(
            topic["id"],
            slug="hidden-test-problem",
        ),
    )

    assert create_response.status_code == 201

    problem_id = create_response.json()["id"]

    visible_response = client.post(
        f"/api/v1/problems/{problem_id}/test-cases",
        headers=admin_headers,
        json={
            "input": "visible-input",
            "expected_output": "visible-output",
            "run_enabled": True,
            "submit_enabled": True,
            "is_sample": True,
            "display_order": 1,
        },
    )

    assert visible_response.status_code == 201

    hidden_response = client.post(
        f"/api/v1/problems/{problem_id}/test-cases",
        headers=admin_headers,
        json={
            "input": "SECRET-HIDDEN-INPUT",
            "expected_output": "SECRET-HIDDEN-OUTPUT",
            "run_enabled": False,
            "submit_enabled": True,
            "is_sample": False,
            "display_order": 2,
        },
    )

    assert hidden_response.status_code == 201

    response = client.get(
        f"/api/v1/problems/{problem_id}",
        headers=user_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert len(body["test_cases"]) == 1
    assert body["test_cases"][0]["input"] == "visible-input"
    assert body["test_cases"][0]["expected_output"] == "visible-output"

    assert "SECRET-HIDDEN-INPUT" not in response.text
    assert "SECRET-HIDDEN-OUTPUT" not in response.text


def test_slug_endpoint_does_not_expose_hidden_test_cases(
    client,
    admin_headers,
    user_headers,
):
    topic = create_topic(client, admin_headers)

    create_response = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=problem_payload(topic["id"]),
    )

    assert create_response.status_code == 201
    problem_id = create_response.json()["id"]

    for payload in (
        {
            "input": "visible-input",
            "expected_output": "visible-output",
            "run_enabled": True,
            "submit_enabled": True,
            "is_sample": True,
            "display_order": 1,
        },
        {
            "input": "SECRET-HIDDEN-INPUT",
            "expected_output": "SECRET-HIDDEN-OUTPUT",
            "run_enabled": False,
            "submit_enabled": True,
            "is_sample": False,
            "display_order": 2,
        },
    ):
        test_case_response = client.post(
            f"/api/v1/problems/{problem_id}/test-cases",
            headers=admin_headers,
            json=payload,
        )
        assert test_case_response.status_code == 201

    response = client.get(
        "/api/v1/problems/by-slug/test-problem",
        headers=user_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["test_cases"]) == 1
    assert body["test_cases"][0]["input"] == "visible-input"
    assert "SECRET-HIDDEN-INPUT" not in response.text
    assert "SECRET-HIDDEN-OUTPUT" not in response.text
