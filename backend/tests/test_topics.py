def test_list_topics_requires_authentication(client):
    response = client.get("/api/v1/topics")

    assert response.status_code == 401


def test_get_topic_requires_authentication(client):
    response = client.get("/api/v1/topics/1")

    assert response.status_code == 401


def test_list_topics_as_user(client, user_headers):
    response = client.get(
        "/api/v1/topics",
        headers=user_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_can_create_topic(client, admin_headers):
    response = client.post(
        "/api/v1/topics",
        headers=admin_headers,
        json={
            "name": "Test Topic",
            "slug": "test-topic",
            "display_order": 99,
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == "Test Topic"
    assert body["slug"] == "test-topic"
    assert body["display_order"] == 99


def test_create_topic_requires_authentication(client):
    response = client.post(
        "/api/v1/topics",
        json={
            "name": "Unauthorized Topic",
            "slug": "unauthorized-topic",
            "display_order": 99,
        },
    )

    assert response.status_code == 401


def test_create_topic_requires_admin(client, user_headers):
    response = client.post(
        "/api/v1/topics",
        headers=user_headers,
        json={
            "name": "User Topic",
            "slug": "user-topic",
            "display_order": 99,
        },
    )

    assert response.status_code == 403


def test_admin_can_get_topic(client, admin_headers):
    create_response = client.post(
        "/api/v1/topics",
        headers=admin_headers,
        json={
            "name": "Readable Topic",
            "slug": "readable-topic",
            "display_order": 99,
        },
    )

    assert create_response.status_code == 201

    topic_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/topics/{topic_id}",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == topic_id


def test_admin_can_update_topic(client, admin_headers):
    create_response = client.post(
        "/api/v1/topics",
        headers=admin_headers,
        json={
            "name": "Original Topic",
            "slug": "original-topic",
            "display_order": 99,
        },
    )

    assert create_response.status_code == 201

    topic_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/topics/{topic_id}",
        headers=admin_headers,
        json={
            "name": "Updated Topic",
            "slug": "updated-topic",
            "display_order": 100,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == topic_id
    assert body["name"] == "Updated Topic"
    assert body["slug"] == "updated-topic"
    assert body["display_order"] == 100


def test_update_topic_requires_admin(client, user_headers):
    response = client.patch(
        "/api/v1/topics/1",
        headers=user_headers,
        json={
            "name": "Should Not Update",
        },
    )

    assert response.status_code == 403


def test_admin_can_delete_topic(client, admin_headers):
    create_response = client.post(
        "/api/v1/topics",
        headers=admin_headers,
        json={
            "name": "Delete Topic",
            "slug": "delete-topic",
            "display_order": 99,
        },
    )

    assert create_response.status_code == 201

    topic_id = create_response.json()["id"]

    response = client.delete(
        f"/api/v1/topics/{topic_id}",
        headers=admin_headers,
    )

    assert response.status_code == 204

    get_response = client.get(
        f"/api/v1/topics/{topic_id}",
        headers=admin_headers,
    )

    assert get_response.status_code == 404


def test_delete_topic_requires_admin(client, user_headers):
    response = client.delete(
        "/api/v1/topics/1",
        headers=user_headers,
    )

    assert response.status_code == 403


def test_duplicate_topic_slug_returns_conflict(client, admin_headers):
    payload = {
        "name": "Duplicate Topic",
        "slug": "duplicate-topic",
        "display_order": 99,
    }

    first_response = client.post(
        "/api/v1/topics",
        headers=admin_headers,
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/topics",
        headers=admin_headers,
        json={
            **payload,
            "name": "Another Topic",
        },
    )

    assert second_response.status_code == 409


def test_get_missing_topic_returns_404(client, admin_headers):
    response = client.get(
        "/api/v1/topics/999999",
        headers=admin_headers,
    )

    assert response.status_code == 404


def test_update_missing_topic_returns_404(client, admin_headers):
    response = client.patch(
        "/api/v1/topics/999999",
        headers=admin_headers,
        json={
            "name": "Missing Topic",
        },
    )

    assert response.status_code == 404


def test_delete_missing_topic_returns_404(client, admin_headers):
    response = client.delete(
        "/api/v1/topics/999999",
        headers=admin_headers,
    )

    assert response.status_code == 404
