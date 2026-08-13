from backend.app.models.user import User


def test_authenticated_admin_fixture(
    client,
    admin_user: User,
    admin_headers: dict[str, str],
):
    response = client.get(
        "/api/v1/problems",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert admin_user.role.value == "ADMIN"
