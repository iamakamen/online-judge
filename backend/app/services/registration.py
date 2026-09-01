from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.registration_session import RegistrationSession
from backend.app.models.user import User
from backend.app.services.email import EmailDeliveryError, send_otp_email
from backend.app.services.otp import (
    OTPRequestPolicyError,
    OTP_REQUEST_LIMIT,
    OTP_RESEND_COOLDOWN_MINUTES,
    issue_otp,
    verify_otp_code,
)
from backend.app.services.password import hash_password, validate_password


def username_is_valid(username: str) -> bool:
    return bool(username) and len(username) <= 100 and all(
        character.isascii() and (character.isalnum() or character == "_")
        for character in username
    )


def username_is_available(db: Session, username: str) -> bool:
    normalized_username = username.strip().lower()
    if not username_is_valid(normalized_username):
        return False
    return db.scalar(select(User.id).where(User.username == normalized_username)) is None


def enforce_otp_request_policy(session: RegistrationSession, now: datetime) -> None:
    if session.otp_request_count >= OTP_REQUEST_LIMIT:
        raise OTPRequestPolicyError("OTP request limit exceeded")
    if session.otp_last_requested_at is None:
        return
    elapsed = (now - session.otp_last_requested_at).total_seconds()
    cooldown = OTP_RESEND_COOLDOWN_MINUTES * 60
    if elapsed < cooldown:
        retry_after = max(1, int(cooldown - elapsed + 0.999))
        raise OTPRequestPolicyError(
            f"Please wait {retry_after} seconds before requesting another code",
            retry_after=retry_after,
        )


def start_registration(
    db: Session,
    first_name: str,
    last_name: str,
    email: str,
) -> str:
    email = email.strip().lower()
    first_name = first_name.strip()
    last_name = last_name.strip()

    if not first_name:
        raise ValueError("First name is required")

    if not last_name:
        raise ValueError("Last name is required")

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user is not None:
        raise ValueError("Email already registered")

    session = db.scalar(
        select(RegistrationSession)
        .where(RegistrationSession.email == email)
        .with_for_update()
    )

    if session is None:
        session = RegistrationSession(
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        db.add(session)
    else:
        if session.email_verified_at is not None:
            raise ValueError("Email already verified")
        now = datetime.now(timezone.utc)
        enforce_otp_request_policy(session, now)
        session.first_name = first_name
        session.last_name = last_name
        session.updated_at = now

    try:
        otp = issue_otp(db, email)
        send_otp_email(
            recipient_email=email,
            otp=otp,
        )
        session.otp_request_count += 1
        session.otp_last_requested_at = datetime.now(timezone.utc)
        db.commit()
    except EmailDeliveryError:
        db.rollback()
        raise ValueError("Unable to send verification email")
    except Exception:
        db.rollback()
        raise

    return otp


def verify_registration_otp(
    db: Session,
    email: str,
    otp: str,
) -> None:
    email = email.strip().lower()

    session = db.scalar(
        select(RegistrationSession).where(
            RegistrationSession.email == email
        )
    )

    if session is None:
        raise ValueError("Registration session not found")

    if session.email_verified_at is not None:
        raise ValueError("Email already verified")

    verify_otp_code(db, email, otp)

    now = datetime.now(timezone.utc)
    session.email_verified_at = now
    session.updated_at = now

    db.commit()


def complete_registration(
    db: Session,
    email: str,
    username: str,
    password: str,
) -> User:
    email = email.strip().lower()
    username = username.strip().lower()

    if not username_is_valid(username):
        raise ValueError("Username may contain only letters, numbers, and underscores")
    validate_password(password)

    session = db.scalar(
        select(RegistrationSession)
        .where(RegistrationSession.email == email)
        .with_for_update()
    )

    if session is None:
        raise ValueError("Registration session not found")

    if session.email_verified_at is None:
        raise ValueError("Email verification required")

    existing_user = db.scalar(
        select(User).where(
            (User.email == email) | (User.username == username)
        )
    )

    if existing_user is not None:
        if existing_user.email == email:
            raise ValueError("Email already registered")
        raise ValueError("Username already taken")

    try:
        user = User(
            first_name=session.first_name,
            last_name=session.last_name,
            username=username,
            email=email,
            password_hash=hash_password(password),
            email_verified=True,
        )

        db.add(user)
        db.flush()

        db.execute(
            delete(RegistrationSession).where(
                RegistrationSession.id == session.id
            )
        )

        db.commit()
        db.refresh(user)

        return user

    except IntegrityError as exc:
        db.rollback()
        constraint = str(getattr(getattr(exc.orig, "diag", None), "constraint_name", ""))
        detail = str(exc).lower()
        if "username" in constraint.lower() or "username" in detail:
            raise ValueError("Username already taken") from exc
        if "email" in constraint.lower() or "email" in detail:
            raise ValueError("Email already registered") from exc
        raise
    except Exception:
        db.rollback()
        raise
