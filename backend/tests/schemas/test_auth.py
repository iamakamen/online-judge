from pydantic import ValidationError
import pytest

from backend.app.schemas.auth import (
    RegisterCompleteRequest,
    RegisterStartRequest,
    VerifyOTPRequest,
)


def test_registration_start_rejects_empty_or_control_character_names():
    with pytest.raises(ValidationError):
        RegisterStartRequest(first_name=" ", last_name="Doe", email="jane@example.com")
    with pytest.raises(ValidationError):
        RegisterStartRequest(first_name="Jane\n", last_name="Doe", email="jane@example.com")


def test_registration_schemas_reject_malformed_email_otp_and_password():
    with pytest.raises(ValidationError):
        RegisterStartRequest(first_name="Jane", last_name="Doe", email="not-an-email")
    with pytest.raises(ValidationError):
        VerifyOTPRequest(email="jane@example.com", otp="12345")
    with pytest.raises(ValidationError):
        RegisterCompleteRequest(
            email="jane@example.com",
            username="jane",
            password="short",
            confirm_password="short",
        )
    with pytest.raises(ValidationError):
        RegisterCompleteRequest(
            email="jane@example.com",
            username="jane",
            password="a" * 129,
            confirm_password="a" * 129,
        )

    request = RegisterCompleteRequest(
        email="jane@example.com",
        username="jane",
        password="a" * 12,
        confirm_password="a" * 12,
    )
    assert len(request.password) == 12


def test_registration_complete_normalizes_username_and_rejects_mismatch():
    request = RegisterCompleteRequest(
        email="jane@example.com",
        username="Jane_Doe",
        password="long-enough1",
        confirm_password="long-enough1",
    )
    assert request.username == "jane_doe"
    with pytest.raises(ValidationError, match="Passwords do not match"):
        RegisterCompleteRequest(
            email="jane@example.com",
            username="jane",
            password="long-enough1",
            confirm_password="different",
        )
