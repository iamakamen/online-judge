import os
import asyncio

os.environ.setdefault(
    "DATABASE_URL",
    "sqlite+pysqlite:///:memory:",
)
os.environ["CORS_ALLOWED_ORIGINS"] = " https://online-judge-five-phi.vercel.app, https://staging.example.com "

import httpx

from backend.app.main import app


ALLOWED_ORIGIN = "https://online-judge-five-phi.vercel.app"


async def cors_test_post():
    return {"status": "ok"}


app.add_api_route("/__cors_test_post", cors_test_post, methods=["POST"])


def request(method, path, *, headers=None, json=None):
    async def send_request():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.request(method, path, headers=headers, json=json)

    return asyncio.run(send_request())


def test_allowed_origin_preflight_returns_cors_permissions():
    response = request(
        "OPTIONS",
        "/auth/login",
        headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type, authorization",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN
    assert response.headers["access-control-allow-credentials"] == "true"
    assert "POST" in response.headers["access-control-allow-methods"]
    allowed_headers = {
        header.strip().lower()
        for header in response.headers["access-control-allow-headers"].split(",")
    }
    assert {"content-type", "authorization"}.issubset(allowed_headers)


def test_disallowed_origin_is_not_granted_cors_access():
    response = request(
        "OPTIONS",
        "/auth/login",
        headers={
            "Origin": "https://malicious.example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_allowed_origin_normal_post_receives_cors_headers():
    response = request(
        "POST",
        "/__cors_test_post",
        headers={"Origin": ALLOWED_ORIGIN},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN
    assert response.headers["access-control-allow-credentials"] == "true"


def test_request_without_origin_continues_to_work():
    response = request(
        "POST",
        "/__cors_test_post",
    )

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers
