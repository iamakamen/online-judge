from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from backend.app.services.otp import OTPRequestPolicyError
from backend.app.services.registration import (
    complete_registration,
    enforce_otp_request_policy,
    username_is_available,
)


def test_registration_policy_allows_first_request_and_rejects_cooldown():
    now = datetime.now(timezone.utc)
    session = SimpleNamespace(
        otp_request_count=0,
        otp_request_window_started_at=None,
        otp_last_requested_at=None,
    )
    enforce_otp_request_policy(session, now)
    session.otp_request_count = 1
    session.otp_last_requested_at = now
    with pytest.raises(OTPRequestPolicyError, match="Please wait") as error:
        enforce_otp_request_policy(session, now + timedelta(seconds=1))
    assert error.value.retry_after == 119


def test_registration_policy_rejects_after_five_requests():
    now = datetime.now(timezone.utc)
    session = SimpleNamespace(
        otp_request_count=5,
        otp_request_window_started_at=now - timedelta(minutes=3),
        otp_last_requested_at=now - timedelta(minutes=3),
    )
    with pytest.raises(OTPRequestPolicyError, match="limit exceeded") as error:
        enforce_otp_request_policy(session, now)
    assert error.value.retry_after is None


def test_registration_policy_resets_expired_request_window():
    now = datetime.now(timezone.utc)
    session = SimpleNamespace(
        otp_request_count=5,
        otp_request_window_started_at=now - timedelta(minutes=21),
        otp_last_requested_at=now - timedelta(minutes=3),
    )
    enforce_otp_request_policy(session, now)
    assert session.otp_request_count == 0
    assert session.otp_request_window_started_at is None


def test_completion_maps_duplicate_username_to_user_facing_error(monkeypatch):
    session = SimpleNamespace(
        id=1,
        email_verified_at=None,
        registration_expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    existing_user = SimpleNamespace(email="other@example.com", username="takenuser")
    db = Mock()
    db.scalar.side_effect = [session, existing_user]
    monkeypatch.setattr(
        "backend.app.services.registration.decode_registration_verification_proof",
        lambda _: {"sub": "jane@example.com", "sid": "1"},
    )
    with pytest.raises(ValueError, match="Username already taken"):
        complete_registration(db, "jane@example.com", "takenuser", "longenough1A!", "proof")


def test_username_availability_normalizes_and_checks_only_valid_usernames():
    db = Mock()
    db.scalar.return_value = None
    assert username_is_available(db, "JaneDoe1") is True
    assert db.scalar.call_count == 1
    assert username_is_available(db, "not valid") is False
    assert db.scalar.call_count == 1
