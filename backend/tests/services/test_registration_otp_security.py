from datetime import datetime, timedelta, timezone
from itertools import count
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from sqlalchemy import delete, select

from backend.app.models.otp_code import OTPCode
from backend.app.models.registration_session import RegistrationSession
from backend.app.models.refresh_session import RefreshSession
from backend.app.models.user import User
from backend.app.services import otp as otp_service
from backend.app.services import registration as registration_service
from backend.app.services.otp import OTPVerificationError
from backend.app.db.session import SessionLocal


@pytest.fixture()
def registration_email(db, monkeypatch):
    email = f"otp-policy-{uuid4().hex}@example.com"
    codes = count(100000)
    monkeypatch.setattr(
        otp_service,
        "generate_otp",
        lambda: f"{next(codes):06d}",
    )
    monkeypatch.setattr(registration_service, "send_otp_email", lambda **_: None)
    yield email
    db.rollback()
    db.execute(delete(OTPCode).where(OTPCode.email == email))
    db.execute(
        delete(RefreshSession).where(
            RefreshSession.user_id.in_(select(User.id).where(User.email == email))
        )
    )
    db.execute(delete(User).where(User.email == email))
    db.execute(delete(RegistrationSession).where(RegistrationSession.email == email))
    db.commit()


def expire_request_cooldown(db, email):
    session = db.scalar(
        select(RegistrationSession).where(RegistrationSession.email == email)
    )
    session.otp_last_requested_at = datetime.now(timezone.utc) - timedelta(minutes=3)
    db.commit()


def test_request_quota_is_persisted_and_server_authoritative(db, registration_email):
    email = registration_email
    result = registration_service.start_registration(db, "Jane", "Doe", email)
    assert result["remaining_requests"] == 4

    for expected_remaining in (3, 2, 1, 0):
        expire_request_cooldown(db, email)
        result = registration_service.start_registration(db, "Jane", "Doe", email)
        assert result["remaining_requests"] == expected_remaining

    expire_request_cooldown(db, email)
    with pytest.raises(registration_service.OTPRequestPolicyError) as error:
        registration_service.start_registration(db, "Jane", "Doe", email)
    assert error.value.code == "request_limit"

    session = db.scalar(
        select(RegistrationSession).where(RegistrationSession.email == email)
    )
    assert session.otp_request_count == 5
    assert session.otp_request_window_started_at is not None
    db.execute(delete(OTPCode).where(OTPCode.email == email))
    db.commit()
    expire_request_cooldown(db, email)
    with pytest.raises(registration_service.OTPRequestPolicyError) as error:
        registration_service.start_registration(db, "Jane", "Doe", email)
    assert error.value.code == "request_limit"


def test_request_cooldown_and_window_expiry_are_independent(db, registration_email):
    email = registration_email
    registration_service.start_registration(db, "Jane", "Doe", email)
    with pytest.raises(registration_service.OTPRequestPolicyError) as error:
        registration_service.start_registration(db, "Jane", "Doe", email)
    assert error.value.code == "request_cooldown"
    assert error.value.retry_after is not None

    session = db.scalar(
        select(RegistrationSession).where(RegistrationSession.email == email)
    )
    now = datetime.now(timezone.utc)
    session.otp_request_count = 5
    session.otp_request_window_started_at = now - timedelta(minutes=21)
    session.otp_last_requested_at = now - timedelta(minutes=3)
    db.commit()

    result = registration_service.start_registration(db, "Jane", "Doe", email)
    assert result["remaining_requests"] == 4
    session = db.scalar(
        select(RegistrationSession).where(RegistrationSession.email == email)
    )
    assert session.otp_request_count == 1
    assert session.otp_request_window_started_at > now - timedelta(seconds=5)


def test_concurrent_new_registration_requests_are_serialized(
    db, registration_email
):
    email = registration_email

    def request_otp():
        session = SessionLocal()
        try:
            return registration_service.start_registration(session, "Jane", "Doe", email)
        except Exception as error:
            return error
        finally:
            session.close()

    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(lambda _: request_otp(), range(6)))

    assert sum(isinstance(result, dict) for result in results) == 1
    assert sum(
        isinstance(result, registration_service.OTPRequestPolicyError)
        for result in results
    ) == 5


def test_resend_invalidates_previous_otp_without_resetting_verification_budget(
    db, registration_email
):
    email = registration_email
    registration_service.start_registration(db, "Jane", "Doe", email)
    old_code = "100000"
    with pytest.raises(OTPVerificationError) as error:
        registration_service.verify_registration_otp(db, email, "000000")
    assert error.value.code == "otp_invalid"

    session = db.scalar(
        select(RegistrationSession).where(RegistrationSession.email == email)
    )
    assert session.otp_verification_attempt_count == 1
    expire_request_cooldown(db, email)
    registration_service.start_registration(db, "Jane", "Doe", email)

    with pytest.raises(OTPVerificationError) as error:
        registration_service.verify_registration_otp(db, email, old_code)
    assert error.value.code == "otp_superseded"
    session = db.scalar(
        select(RegistrationSession).where(RegistrationSession.email == email)
    )
    assert session.otp_verification_attempt_count == 2


def test_verification_window_expiry_resets_only_verification_budget(
    db, registration_email
):
    email = registration_email
    registration_service.start_registration(db, "Jane", "Doe", email)
    with pytest.raises(OTPVerificationError):
        registration_service.verify_registration_otp(db, email, "000000")

    session = db.scalar(
        select(RegistrationSession).where(RegistrationSession.email == email)
    )
    session.otp_verification_attempt_count = 10
    session.otp_verification_window_started_at = datetime.now(timezone.utc) - timedelta(
        minutes=21
    )
    db.commit()

    with pytest.raises(OTPVerificationError) as error:
        registration_service.verify_registration_otp(db, email, "000000")
    assert error.value.code == "otp_invalid"
    session = db.scalar(
        select(RegistrationSession).where(RegistrationSession.email == email)
    )
    assert session.otp_verification_attempt_count == 1


def test_per_otp_limit_and_registration_limit_are_both_enforced(db, registration_email):
    email = registration_email
    registration_service.start_registration(db, "Jane", "Doe", email)

    for _ in range(4):
        with pytest.raises(OTPVerificationError) as error:
            registration_service.verify_registration_otp(db, email, "000000")
        assert error.value.code == "otp_invalid"
    with pytest.raises(OTPVerificationError) as error:
        registration_service.verify_registration_otp(db, email, "000000")
    assert error.value.code == "otp_attempt_limit"

    expire_request_cooldown(db, email)
    registration_service.start_registration(db, "Jane", "Doe", email)
    for attempt in range(5):
        with pytest.raises(OTPVerificationError) as error:
            registration_service.verify_registration_otp(db, email, "000000")
        if attempt < 4:
            assert error.value.code == "otp_invalid"
        else:
            assert error.value.code == "otp_attempt_limit"

    with pytest.raises(OTPVerificationError) as error:
        registration_service.verify_registration_otp(db, email, "000000")
    assert error.value.code == "verification_attempt_limit"


def test_concurrent_verification_attempts_cannot_bypass_limits(db, registration_email):
    email = registration_email
    registration_service.start_registration(db, "Jane", "Doe", email)

    def verify_wrong_code():
        session = SessionLocal()
        try:
            registration_service.verify_registration_otp(session, email, "000000")
            return None
        except OTPVerificationError as error:
            return error.code
        finally:
            session.close()

    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(lambda _: verify_wrong_code(), range(6)))

    assert all(result in {"otp_invalid", "otp_attempt_limit"} for result in results)
    session = db.scalar(
        select(RegistrationSession).where(RegistrationSession.email == email)
    )
    record = db.scalar(select(OTPCode).where(OTPCode.email == email))
    assert session.otp_verification_attempt_count == 6
    assert record.attempts == 5
    assert record.invalidated_at is not None


def test_successful_otp_is_single_use_and_expiry_is_classified(db, registration_email):
    email = registration_email
    registration_service.start_registration(db, "Jane", "Doe", email)
    record = db.scalar(
        select(OTPCode).where(OTPCode.email == email)
    )
    record.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db.commit()
    with pytest.raises(OTPVerificationError) as error:
        registration_service.verify_registration_otp(db, email, "100000")
    assert error.value.code == "otp_expired"

    expire_request_cooldown(db, email)
    registration_service.start_registration(db, "Jane", "Doe", email)
    proof = registration_service.verify_registration_otp(db, email, "100001")
    assert proof
    session = db.scalar(
        select(RegistrationSession).where(RegistrationSession.email == email)
    )
    assert session.email_verified_at is None
    assert db.scalar(select(User).where(User.email == email)) is None

    with pytest.raises(OTPVerificationError) as error:
        registration_service.verify_registration_otp(db, email, "100001")
    assert error.value.code == "otp_invalid"

    user, access_token, refresh_token = registration_service.complete_registration(
        db,
        email,
        f"user_{uuid4().hex[:12]}",
        "longenough1A!",
        proof,
    )
    assert user.email_verified is True
    assert access_token
    assert refresh_token
    assert db.scalar(
        select(RegistrationSession).where(RegistrationSession.email == email)
    ) is None
    assert db.scalar(select(OTPCode).where(OTPCode.email == email)) is None


def test_expired_verified_flow_cannot_complete_or_leave_temporary_state(
    db, registration_email
):
    email = registration_email
    registration_service.start_registration(db, "Jane", "Doe", email)
    proof = registration_service.verify_registration_otp(db, email, "100000")
    session = db.scalar(
        select(RegistrationSession).where(RegistrationSession.email == email)
    )
    session.registration_expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db.commit()

    with pytest.raises(registration_service.RegistrationSessionError):
        registration_service.complete_registration(
        db, email, f"user{uuid4().hex[:12]}", "longenough1A!", proof
        )

    assert db.scalar(select(User).where(User.email == email)) is None
    assert db.scalar(
        select(RegistrationSession).where(RegistrationSession.email == email)
    ) is None
    assert db.scalar(select(OTPCode).where(OTPCode.email == email)) is None
