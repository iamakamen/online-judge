def test_dashboard_requires_authentication(client):
    response = client.get("/api/v1/dashboard")

    assert response.status_code == 401


def test_authenticated_dashboard_returns_v1_statistics(
    client,
    user_headers,
):
    response = client.get(
        "/api/v1/dashboard",
        headers=user_headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        "first_name": "Test",
        "solved_count": 0,
        "day_streak": 0,
        "global_rank": "N/A",
    }
