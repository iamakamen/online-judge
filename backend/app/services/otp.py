from datetime import datetime, timedelta, timezone
import secrets

from pwdlib import PasswordHash
from sqlalchemy import func, select, text, update
from sqlalchemy.orm import Session

from backend.app.models.otp_code import OTPCode


password_hash = PasswordHash.recommended()

OTP_LIFETIME_MINUTES = 5
OTP_MAX_ATTEMPTS = 5
OTP_REQUEST_LIMIT = 3
OTP_REQUEST_WINDOW_MINUTES = 10


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(otp: str) -> str:
    return password_hash.hash(otp)


def verify_otp(otp: str, hashed_otp: str) -> bool:
    return password_hash.verify(otp, hashed_otp)


def issue_otp(db: Session, email: str) -> str:
    email = email.strip().lower()
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=OTP_REQUEST_WINDOW_MINUTES)

    # Serialize OTP issuance for the same email so concurrent requests
    # cannot bypass the request limit.
    db.execute(
        text(
            "SELECT pg_advisory_xact_lock("
            "hashtextextended(:email, 0)"
            ")"
        ),
        {"email": email},
    )

    recent_requests = db.scalar(
        select(func.count())
        .select_from(OTPCode)
        .where(
            OTPCode.email == email,
            OTPCode.created_at >= window_start,
        )
    )

    if recent_requests >= OTP_REQUEST_LIMIT:
        raise ValueError("OTP request limit exceeded")

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


def verify_otp_code(db: Session, email: str, otp: str) -> bool:
    email = email.strip().lower()
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

    record = db.scalar(
        select(OTPCode)
        .where(
            OTPCode.email == email,
            OTPCode.invalidated_at.is_(None),
        )
        .order_by(OTPCode.created_at.desc())
        .with_for_update()
    )

    if record is None:
        db.rollback()
        raise ValueError("Invalid OTP")

    if record.expires_at <= now:
        record.invalidated_at = now
        db.commit()
        raise ValueError("OTP expired")

    if record.attempts >= OTP_MAX_ATTEMPTS:
        record.invalidated_at = now
        db.commit()
        raise ValueError("OTP attempt limit exceeded")

    if not verify_otp(otp, record.code_hash):
        record.attempts += 1

        if record.attempts >= OTP_MAX_ATTEMPTS:
            record.invalidated_at = now

        # Persist the failed attempt before raising.
        db.commit()

        raise ValueError("Invalid OTP")

    # OTP is single-use. Invalidate it immediately after successful use.
    record.invalidated_at = now
    db.commit()

    return True
