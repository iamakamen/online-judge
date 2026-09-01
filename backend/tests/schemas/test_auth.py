from pydantic import ValidationError
import pytest

from backend.app.schemas.auth import (
    RegisterCompleteRequest,
    RegisterStartRequest,
    VerifyOTPRequest,
)
from backend.app.services.password import validate_password
from backend.app.services.registration import username_is_valid


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
            username="janedoe1",
            password="short",
            confirm_password="short",
        )
    with pytest.raises(ValidationError):
        RegisterCompleteRequest(
            email="jane@example.com",
            username="janedoe1",
            password="a" * 25,
            confirm_password="a" * 25,
        )

    request = RegisterCompleteRequest(
        email="jane@example.com",
        username="janedoe1",
        password="a" * 12,
        confirm_password="a" * 12,
    )
    assert len(request.password) == 12


@pytest.mark.parametrize(
    ("length", "accepted"),
    [(11, False), (12, True), (24, True), (25, False)],
)
def test_registration_password_length_boundaries(length, accepted):
    values = {
        "email": "jane@example.com",
        "username": "janedoe1",
        "password": "a" * length,
        "confirm_password": "a" * length,
    }
    if accepted:
        assert len(RegisterCompleteRequest(**values).password) == length
        validate_password(values["password"])
    else:
        with pytest.raises(ValidationError):
            RegisterCompleteRequest(**values)
        with pytest.raises(ValueError):
            validate_password(values["password"])


def test_registration_complete_normalizes_username_and_rejects_mismatch():
    request = RegisterCompleteRequest(
        email="jane@example.com",
        username="JaneDoe1",
        password="longenough1A!",
        confirm_password="longenough1A!",
    )
    assert request.username == "janedoe1"
    with pytest.raises(ValidationError, match="Passwords do not match"):
        RegisterCompleteRequest(
            email="jane@example.com",
            username="janedoe1",
            password="longenough1A!",
            confirm_password="different123",
        )


@pytest.mark.parametrize(
    ("username", "accepted"),
    [
        ("abcdefg", False), ("abcdefgh", True), ("abcdefghijklmnop", True),
        ("abcdefghijklmnopq", False), ("abc12345", True), ("abcd_123", False),
        ("abcd 123", False), ("abcd-123", False), ("abcd!123", False),
        ("abcdé123", False),
    ],
)
def test_registration_username_policy(username, accepted):
    values = {
        "email": "jane@example.com", "username": username,
        "password": "longenough1A!", "confirm_password": "longenough1A!",
    }
    assert username_is_valid(username) is accepted
    if accepted:
        assert RegisterCompleteRequest(**values).username == username.lower()
    else:
        with pytest.raises(ValidationError):
            RegisterCompleteRequest(**values)


@pytest.mark.parametrize(
    ("password", "accepted"),
    [
        ("a" * 11, False), ("a" * 12, True), ("a" * 24, True),
        ("a" * 25, False), ("abcdefghijkl", True), ("Abcdefgh1234", True),
        ("!@#$%^&*()ab", True), ("abcdefghijk ", False),
        ("abcdefghij_", False), ("abcdefghij-", False),
        ("abcdefghij.", False), ("abcdefghij=", False),
    ],
)
def test_registration_password_character_policy(password, accepted):
    values = {
        "email": "jane@example.com", "username": "janedoe1",
        "password": password, "confirm_password": password,
    }
    if accepted:
        RegisterCompleteRequest(**values)
        validate_password(password)
    else:
        with pytest.raises(ValidationError):
            RegisterCompleteRequest(**values)
        with pytest.raises(ValueError):
            validate_password(password)
