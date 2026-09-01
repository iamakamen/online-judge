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
    session = SimpleNamespace(otp_request_count=0, otp_last_requested_at=None)
    enforce_otp_request_policy(session, now)
    session.otp_request_count = 1
    session.otp_last_requested_at = now
    with pytest.raises(OTPRequestPolicyError, match="Please wait") as error:
        enforce_otp_request_policy(session, now + timedelta(seconds=1))
    assert error.value.retry_after == 119


def test_registration_policy_rejects_after_three_requests():
    now = datetime.now(timezone.utc)
    session = SimpleNamespace(otp_request_count=3, otp_last_requested_at=now - timedelta(minutes=3))
    with pytest.raises(OTPRequestPolicyError, match="limit exceeded") as error:
        enforce_otp_request_policy(session, now)
    assert error.value.retry_after is None


def test_completion_maps_duplicate_username_to_user_facing_error():
    session = SimpleNamespace(email_verified_at=datetime.now(timezone.utc))
    existing_user = SimpleNamespace(email="other@example.com", username="taken")
    db = Mock()
    db.scalar.side_effect = [session, existing_user]
    with pytest.raises(ValueError, match="Username already taken"):
        complete_registration(db, "jane@example.com", "taken", "long-enough1")


def test_username_availability_normalizes_and_checks_only_valid_usernames():
    db = Mock()
    db.scalar.return_value = None
    assert username_is_available(db, " Jane_Doe ") is True
    assert db.scalar.call_count == 1
    assert username_is_available(db, "not valid") is False
    assert db.scalar.call_count == 1
