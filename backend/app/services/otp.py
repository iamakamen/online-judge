from datetime import datetime, timedelta, timezone
import secrets

from pwdlib import PasswordHash
from sqlalchemy import select, text, update
from sqlalchemy.orm import Session

from backend.app.models.otp_code import OTPCode


password_hash = PasswordHash.recommended()

OTP_LIFETIME_MINUTES = 5
OTP_MAX_ATTEMPTS = 5
OTP_REQUEST_LIMIT = 5
OTP_REQUEST_WINDOW_MINUTES = 20
OTP_RESEND_COOLDOWN_MINUTES = 2
OTP_VERIFICATION_ATTEMPT_LIMIT = 10
OTP_VERIFICATION_WINDOW_MINUTES = 20


class OTPRequestPolicyError(ValueError):
    def __init__(self, code: str, message: str, retry_after: int | None = None):
        super().__init__(message)
        self.code = code
        self.retry_after = retry_after


class OTPVerificationError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(otp: str) -> str:
    return password_hash.hash(otp)


def verify_otp(otp: str, hashed_otp: str) -> bool:
    return password_hash.verify(otp, hashed_otp)


def issue_otp(db: Session, email: str) -> str:
    email = email.strip().lower()
    now = datetime.now(timezone.utc)
    # Serialize OTP issuance for the same email so concurrent requests
    # cannot race OTP replacement. RegistrationSession owns request quota.
    db.execute(
        text(
            "SELECT pg_advisory_xact_lock("
            "hashtextextended(:email, 0)"
            ")"
        ),
        {"email": email},
    )

    db.execute(
        update(OTPCode)
        .where(
            OTPCode.email == email,
            OTPCode.invalidated_at.is_(None),
        )
        .values(invalidated_at=now)
    )

    otp = generate_otp()

    db.add(
        OTPCode(
            email=email,
            code_hash=hash_otp(otp),
            expires_at=now + timedelta(minutes=OTP_LIFETIME_MINUTES),
            attempts=0,
            created_at=now,
        )
    )

    db.flush()

    return otp


def verify_otp_code(db: Session, session, otp: str) -> bool:
    email = session.email.strip().lower()
    now = datetime.now(timezone.utc)

    # Serialize verification for the same email so concurrent attempts
    # cannot race the attempt counter or OTP invalidation state.
    db.execute(
        text(
            "SELECT pg_advisory_xact_lock("
            "hashtextextended(:email, 0)"
            ")"
        ),
        {"email": email},
    )

    if (
        session.otp_verification_window_started_at is not None
        and now - session.otp_verification_window_started_at
        >= timedelta(minutes=OTP_VERIFICATION_WINDOW_MINUTES)
    ):
        session.otp_verification_attempt_count = 0
        session.otp_verification_window_started_at = None

    if session.otp_verification_attempt_count >= OTP_VERIFICATION_ATTEMPT_LIMIT:
        db.rollback()
        raise OTPVerificationError(
            "verification_attempt_limit",
            "Registration verification attempt limit exceeded",
        )

    records = db.scalars(
        select(OTPCode)
        .where(OTPCode.email == email)
        .order_by(OTPCode.created_at.desc())
        .with_for_update()
    ).all()
    record = next((item for item in records if item.invalidated_at is None), None)

    def failed_verification() -> None:
        if session.otp_verification_window_started_at is None:
            session.otp_verification_window_started_at = now
        session.otp_verification_attempt_count += 1

    matching_record = next(
        (item for item in records if verify_otp(otp, item.code_hash)),
        None,
    )
    matching_index = records.index(matching_record) if matching_record is not None else None

    if record is None:
        failed_verification()
        db.commit()
        if matching_record is not None:
            if matching_record.expires_at <= now:
                raise OTPVerificationError("otp_expired", "OTP expired")
            if matching_record.attempts >= OTP_MAX_ATTEMPTS:
                raise OTPVerificationError(
                    "otp_attempt_limit",
                    "OTP attempt limit exceeded",
                )
            if matching_index and matching_index > 0:
                raise OTPVerificationError(
                    "otp_superseded",
                    "OTP superseded by newer OTP",
                )
            raise OTPVerificationError("otp_invalid", "Invalid OTP")
        raise OTPVerificationError("otp_invalid", "Invalid OTP")

    if record.expires_at <= now:
        record.invalidated_at = now
        failed_verification()
        db.commit()
        raise OTPVerificationError("otp_expired", "OTP expired")

    if matching_record is not None and matching_record is not record:
        failed_verification()
        db.commit()
        if matching_record.expires_at <= now:
            raise OTPVerificationError("otp_expired", "OTP expired")
        if matching_record.attempts >= OTP_MAX_ATTEMPTS:
            raise OTPVerificationError(
                "otp_attempt_limit",
                "OTP attempt limit exceeded",
            )
        raise OTPVerificationError(
            "otp_superseded",
            "OTP superseded by newer OTP",
        )

    if record.attempts >= OTP_MAX_ATTEMPTS:
        record.invalidated_at = now
        db.commit()
        raise OTPVerificationError("otp_attempt_limit", "OTP attempt limit exceeded")

    if matching_record is not record:
        record.attempts += 1
        failed_verification()
        reached_limit = record.attempts >= OTP_MAX_ATTEMPTS
        if reached_limit:
            record.invalidated_at = now
        db.commit()
        if reached_limit:
            raise OTPVerificationError(
                "otp_attempt_limit",
                "OTP attempt limit exceeded",
            )
        raise OTPVerificationError("otp_invalid", "Invalid OTP")

    record.invalidated_at = now
    db.commit()
    return True
