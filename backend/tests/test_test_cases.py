def _create_problem(client, admin_headers, **overrides):
    problem_slug = overrides.get("slug", "test-problem")
    topic_slug = f"test-topic-{problem_slug}"

    topic_response = client.post(
        "/api/v1/topics",
        headers=admin_headers,
        json={
            "name": f"Test Topic {problem_slug}",
            "slug": topic_slug,
            "display_order": 1,
        },
    )

    assert topic_response.status_code == 201

    topic_id = topic_response.json()["id"]

    payload = {
        "topic_id": topic_id,
        "title": "Test Problem",
        "slug": problem_slug,
        "statement": "Test problem statement.",
        "constraints": "Test problem constraints.",
        "difficulty": "EASY",
        "tags": ["test"],
        "starter_code": {
            "python": "print('test')",
            "cpp": "#include <iostream>\nint main() { return 0; }",
        },
        "time_limit_ms": 1000,
        "memory_limit_mb": 128,
    }

    payload.update(overrides)

    response = client.post(
        "/api/v1/problems",
        headers=admin_headers,
        json=payload,
    )

    assert response.status_code == 201

    return response.json()

def _create_test_case(client, admin_headers, problem_id, **overrides):
    payload = {
        "input": "3\n1 2 3",
        "expected_output": "6",
        "run_enabled": True,
        "submit_enabled": True,
        "is_sample": True,
        "display_order": 1,
    }
    payload.update(overrides)

    response = client.post(
        f"/api/v1/problems/{problem_id}/test-cases",
        headers=admin_headers,
        json=payload,
    )

    assert response.status_code == 201
    return response.json()


def test_create_test_case_requires_authentication(client):
    problem_id = 999

    response = client.post(
        f"/api/v1/problems/{problem_id}/test-cases",
        json={
            "input": "1",
            "expected_output": "1",
            "run_enabled": True,
            "submit_enabled": True,
            "is_sample": True,
            "display_order": 1,
        },
    )

    assert response.status_code == 401


def test_user_cannot_create_test_case(client, user_headers):
    response = client.post(
        "/api/v1/problems/1/test-cases",
        headers=user_headers,
        json={
            "input": "1",
            "expected_output": "1",
            "run_enabled": True,
            "submit_enabled": True,
            "is_sample": True,
            "display_order": 1,
        },
    )

    assert response.status_code == 403


def test_admin_can_create_test_case(client, admin_headers):
    problem = _create_problem(
        client,
        admin_headers,
        slug="create-test-case-problem",
    )

    response = client.post(
        f"/api/v1/problems/{problem['id']}/test-cases",
        headers=admin_headers,
        json={
            "input": "3\n1 2 3",
            "expected_output": "6",
            "run_enabled": True,
            "submit_enabled": True,
            "is_sample": True,
            "display_order": 1,
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["input"] == "3\n1 2 3"
    assert body["expected_output"] == "6"
    assert body["run_enabled"] is True
    assert body["submit_enabled"] is True
    assert body["is_sample"] is True
    assert body["display_order"] == 1


def test_create_test_case_missing_problem_returns_404(
    client,
    admin_headers,
):
    response = client.post(
        "/api/v1/problems/999999/test-cases",
        headers=admin_headers,
        json={
            "input": "1",
            "expected_output": "1",
            "run_enabled": True,
            "submit_enabled": True,
            "is_sample": False,
            "display_order": 1,
        },
    )

    assert response.status_code == 404


def test_create_test_case_must_be_enabled_for_run_or_submit(
    client,
    admin_headers,
):
    problem = _create_problem(
        client,
        admin_headers,
        slug="invalid-test-case-problem",
    )

    response = client.post(
        f"/api/v1/problems/{problem['id']}/test-cases",
        headers=admin_headers,
        json={
            "input": "1",
            "expected_output": "1",
            "run_enabled": False,
            "submit_enabled": False,
            "is_sample": False,
            "display_order": 1,
        },
    )

    assert response.status_code == 422


def test_admin_can_update_test_case(client, admin_headers):
    problem = _create_problem(
        client,
        admin_headers,
        slug="update-test-case-problem",
    )

    test_case = _create_test_case(
        client,
        admin_headers,
        problem["id"],
    )

    response = client.patch(
        f"/api/v1/problems/{problem['id']}/test-cases/{test_case['id']}",
        headers=admin_headers,
        json={
            "input": "2\n10 20",
            "expected_output": "30",
            "run_enabled": False,
            "submit_enabled": True,
            "is_sample": False,
            "display_order": 2,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["input"] == "2\n10 20"
    assert body["expected_output"] == "30"
    assert body["run_enabled"] is False
    assert body["submit_enabled"] is True
    assert body["is_sample"] is False
    assert body["display_order"] == 2


def test_partial_update_preserves_other_execution_flag(
    client,
    admin_headers,
):
    problem = _create_problem(
        client,
        admin_headers,
        slug="partial-update-test-case-problem",
    )

    test_case = _create_test_case(
        client,
        admin_headers,
        problem["id"],
        run_enabled=True,
        submit_enabled=True,
    )

    response = client.patch(
        f"/api/v1/problems/{problem['id']}/test-cases/{test_case['id']}",
        headers=admin_headers,
        json={
            "run_enabled": False,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["run_enabled"] is False
    assert body["submit_enabled"] is True


def test_update_cannot_disable_both_execution_modes(
    client,
    admin_headers,
):
    problem = _create_problem(
        client,
        admin_headers,
        slug="invalid-update-test-case-problem",
    )

    test_case = _create_test_case(
        client,
        admin_headers,
        problem["id"],
    )

    response = client.patch(
        f"/api/v1/problems/{problem['id']}/test-cases/{test_case['id']}",
        headers=admin_headers,
        json={
            "run_enabled": False,
            "submit_enabled": False,
        },
    )

    assert response.status_code == 422


def test_user_cannot_update_test_case(client, admin_headers, user_headers):
    problem = _create_problem(
        client,
        admin_headers,
        slug="user-update-test-case-problem",
    )

    test_case = _create_test_case(
        client,
        admin_headers,
        problem["id"],
    )

    response = client.patch(
        f"/api/v1/problems/{problem['id']}/test-cases/{test_case['id']}",
        headers=user_headers,
        json={
            "display_order": 99,
        },
    )

    assert response.status_code == 403


def test_update_missing_test_case_returns_404(
    client,
    admin_headers,
):
    problem = _create_problem(
        client,
        admin_headers,
        slug="missing-update-test-case-problem",
    )

    response = client.patch(
        f"/api/v1/problems/{problem['id']}/test-cases/999999",
        headers=admin_headers,
        json={
            "display_order": 2,
        },
    )

    assert response.status_code == 404


def test_update_test_case_from_wrong_problem_returns_404(
    client,
    admin_headers,
):
    problem_one = _create_problem(
        client,
        admin_headers,
        slug="wrong-owner-problem-one",
    )

    problem_two = _create_problem(
        client,
        admin_headers,
        slug="wrong-owner-problem-two",
    )

    test_case = _create_test_case(
        client,
        admin_headers,
        problem_one["id"],
    )

    response = client.patch(
        f"/api/v1/problems/{problem_two['id']}/test-cases/{test_case['id']}",
        headers=admin_headers,
        json={
            "display_order": 99,
        },
    )

    assert response.status_code == 404


def test_admin_can_delete_test_case(client, admin_headers):
    problem = _create_problem(
        client,
        admin_headers,
        slug="delete-test-case-problem",
    )

    test_case = _create_test_case(
        client,
        admin_headers,
        problem["id"],
    )

    response = client.delete(
        f"/api/v1/problems/{problem['id']}/test-cases/{test_case['id']}",
        headers=admin_headers,
    )

    assert response.status_code == 204

    update_response = client.patch(
        f"/api/v1/problems/{problem['id']}/test-cases/{test_case['id']}",
        headers=admin_headers,
        json={
            "display_order": 2,
        },
    )

    assert update_response.status_code == 404


def test_user_cannot_delete_test_case(client, admin_headers, user_headers):
    problem = _create_problem(
        client,
        admin_headers,
        slug="user-delete-test-case-problem",
    )

    test_case = _create_test_case(
        client,
        admin_headers,
        problem["id"],
    )

    response = client.delete(
        f"/api/v1/problems/{problem['id']}/test-cases/{test_case['id']}",
        headers=user_headers,
    )

    assert response.status_code == 403


def test_delete_missing_test_case_returns_404(
    client,
    admin_headers,
):
    problem = _create_problem(
        client,
        admin_headers,
        slug="missing-delete-test-case-problem",
    )

    response = client.delete(
        f"/api/v1/problems/{problem['id']}/test-cases/999999",
        headers=admin_headers,
    )

    assert response.status_code == 404


def test_delete_test_case_from_wrong_problem_returns_404(
    client,
    admin_headers,
):
    problem_one = _create_problem(
        client,
        admin_headers,
        slug="wrong-delete-problem-one",
    )

    problem_two = _create_problem(
        client,
        admin_headers,
        slug="wrong-delete-problem-two",
    )

    test_case = _create_test_case(
        client,
        admin_headers,
        problem_one["id"],
    )

    response = client.delete(
        f"/api/v1/problems/{problem_two['id']}/test-cases/{test_case['id']}",
        headers=admin_headers,
    )

    assert response.status_code == 404
