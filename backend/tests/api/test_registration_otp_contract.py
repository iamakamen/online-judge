from types import SimpleNamespace

import pytest
from fastapi import Response, status
from starlette.requests import Request

from backend.app.api.routes import auth
from backend.app.schemas.auth import RegisterCompleteRequest, VerifyOTPRequest
from backend.app.services.registration import RegistrationProofError
from backend.app.services.otp import OTPRequestPolicyError, OTPVerificationError


def test_otp_request_success_returns_server_metadata(client, monkeypatch):
    monkeypatch.setattr(
        auth,
        "start_registration",
        lambda **_: {
            "cooldown_seconds": 120,
            "remaining_requests": 4,
        },
    )
    response = client.post(
        "/auth/register/start",
        json={"first_name": "Jane", "last_name": "Doe", "email": "jane@example.com"},
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json()["remaining_requests"] == 4
    assert response.json()["cooldown_seconds"] == 120


def test_otp_request_policy_errors_have_stable_codes_and_retry_after(client, monkeypatch):
    monkeypatch.setattr(
        auth,
        "start_registration",
        lambda **_: (_ for _ in ()).throw(
            OTPRequestPolicyError("request_cooldown", "internal", retry_after=119)
        ),
    )
    response = client.post(
        "/auth/register/start",
        json={"first_name": "Jane", "last_name": "Doe", "email": "jane@example.com"},
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert response.json()["detail"]["code"] == "request_cooldown"
    assert response.headers["retry-after"] == "119"


def test_otp_verification_errors_have_stable_classifications(client, monkeypatch):
    monkeypatch.setattr(
        auth,
        "verify_registration_otp",
        lambda **_: (_ for _ in ()).throw(
            OTPVerificationError("otp_superseded", "internal")
        ),
    )
    response = client.post(
        "/auth/register/verify-otp",
        json={"email": "jane@example.com", "otp": "123456"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"]["code"] == "otp_superseded"


def test_successful_otp_verification_sets_secure_http_only_cookie(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.delenv("REGISTRATION_PROOF_COOKIE_SECURE", raising=False)
    monkeypatch.setattr(auth, "verify_registration_otp", lambda **_: "signed-proof")
    response = Response()

    result = auth.register_verify_otp(
        VerifyOTPRequest(email="jane@example.com", otp="123456"),
        response,
        None,
    )

    cookie = response.headers["set-cookie"]
    assert result["status"] == "email_verified"
    assert "registration_verification=signed-proof" in cookie
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "SameSite=lax" in cookie
    assert "Path=/auth/register" in cookie
    assert "Max-Age=600" in cookie


def registration_request(cookie=""):
    headers = [(b"cookie", cookie.encode())] if cookie else []
    return Request({
        "type": "http",
        "method": "POST",
        "path": "/auth/register/complete",
        "headers": headers,
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
        "scheme": "http",
    })


def valid_complete_request():
    return RegisterCompleteRequest(
        email="jane@example.com",
        username="janedoe1",
        password="longenough1A!",
        confirm_password="longenough1A!",
    )


def test_complete_uses_cookie_proof_and_clears_cookie(monkeypatch):
    user = SimpleNamespace(
        id=1,
        username="janedoe1",
        email="jane@example.com",
        first_name="Jane",
        last_name="Doe",
        email_verified=True,
    )
    captured = {}

    def fake_complete_registration(**kwargs):
        captured.update(kwargs)
        return user, "access", "refresh"

    monkeypatch.setattr(auth, "complete_registration", fake_complete_registration)
    response = Response()
    result = auth.register_complete(
        registration_request("registration_verification=signed-proof"),
        response,
        valid_complete_request(),
        None,
    )

    assert captured["verification_proof"] == "signed-proof"
    assert result["status"] == "registration_complete"
    assert "registration_verification=\"\";" in response.headers["set-cookie"]
    assert "Max-Age=0" in response.headers["set-cookie"]
    assert "verification_proof" not in valid_complete_request().model_dump()


def test_invalid_cookie_is_rejected_and_cleared(monkeypatch):
    monkeypatch.setattr(
        auth,
        "complete_registration",
        lambda **_: (_ for _ in ()).throw(RegistrationProofError("Invalid registration verification proof")),
    )
    response = Response()

    try:
        auth.register_complete(
            registration_request("registration_verification=invalid"),
            response,
            valid_complete_request(),
            None,
        )
    except Exception as error:
        assert getattr(error, "status_code", None) == status.HTTP_400_BAD_REQUEST
    else:
        raise AssertionError("invalid proof should be rejected")

    assert "Max-Age=0" in response.headers["set-cookie"]


def test_registration_status_rejects_missing_cookie():
    with pytest.raises(Exception) as error:
        auth.register_status(
            registration_request(),
            Response(),
            None,
        )

    assert getattr(error.value, "status_code", None) == status.HTTP_401_UNAUTHORIZED
