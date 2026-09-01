from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.credentials import USERNAME_RE
from backend.app.models.registration_session import RegistrationSession
from backend.app.models.otp_code import OTPCode
from backend.app.models.user import User
from backend.app.services.email import EmailDeliveryError, send_otp_email
from backend.app.services.otp import (
    OTPRequestPolicyError,
    OTP_REQUEST_LIMIT,
    OTP_REQUEST_WINDOW_MINUTES,
    OTP_RESEND_COOLDOWN_MINUTES,
    issue_otp,
    verify_otp_code,
)
from backend.app.services.password import hash_password, validate_password
from backend.app.services.authentication import create_authenticated_session
from backend.app.services.token import (
    create_registration_verification_proof,
    decode_registration_verification_proof,
)

REGISTRATION_SESSION_LIFETIME_MINUTES = 30


class RegistrationSessionError(ValueError):
    code = "registration_session_missing"


class RegistrationProofError(ValueError):
    code = "registration_proof_invalid"


class EmailAlreadyRegisteredError(ValueError):
    code = "email_already_registered"


class RegistrationEmailDeliveryError(ValueError):
    code = "email_delivery_failed"


def username_is_valid(username: str) -> bool:
    return USERNAME_RE.fullmatch(username) is not None


def username_is_available(db: Session, username: str) -> bool:
    if not username_is_valid(username):
        return False
    normalized_username = username.lower()
    return db.scalar(select(User.id).where(User.username == normalized_username)) is None


def enforce_otp_request_policy(session: RegistrationSession, now: datetime) -> None:
    if (
        session.otp_request_window_started_at is not None
        and now - session.otp_request_window_started_at
        >= timedelta(minutes=OTP_REQUEST_WINDOW_MINUTES)
    ):
        session.otp_request_count = 0
        session.otp_request_window_started_at = None

    if session.otp_request_count >= OTP_REQUEST_LIMIT:
        raise OTPRequestPolicyError("request_limit", "OTP request limit exceeded")
    if session.otp_last_requested_at is None:
        return
    elapsed = (now - session.otp_last_requested_at).total_seconds()
    cooldown = OTP_RESEND_COOLDOWN_MINUTES * 60
    if elapsed < cooldown:
        retry_after = max(1, int(cooldown - elapsed + 0.999))
        raise OTPRequestPolicyError(
            "request_cooldown",
            f"Please wait {retry_after} seconds before requesting another code",
            retry_after=retry_after,
        )


def start_registration(
    db: Session,
    first_name: str,
    last_name: str,
    email: str,
) -> dict[str, int | str]:
    email = email.strip().lower()
    first_name = first_name.strip()
    last_name = last_name.strip()

    if not first_name:
        raise ValueError("First name is required")

    if not last_name:
        raise ValueError("Last name is required")

    db.execute(
        text(
            "SELECT pg_advisory_xact_lock("
            "hashtextextended(:email, 0)"
            ")"
        ),
        {"email": email},
    )

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user is not None:
        raise EmailAlreadyRegisteredError("Email already registered")

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
        now = datetime.now(timezone.utc)
        if session.registration_expires_at <= now:
            db.execute(delete(OTPCode).where(OTPCode.email == email))
            db.delete(session)
            db.flush()
            session = RegistrationSession(
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            db.add(session)
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
        now = datetime.now(timezone.utc)
        if session.otp_request_window_started_at is None:
            session.otp_request_window_started_at = now
        session.otp_request_count += 1
        session.otp_last_requested_at = now
        db.commit()
    except EmailDeliveryError:
        db.rollback()
        raise RegistrationEmailDeliveryError("Unable to send verification email")
    except Exception:
        db.rollback()
        raise

    return {
        "cooldown_seconds": OTP_RESEND_COOLDOWN_MINUTES * 60,
        "remaining_requests": OTP_REQUEST_LIMIT - session.otp_request_count,
    }


def verify_registration_otp(
    db: Session,
    email: str,
    otp: str,
) -> str:
    email = email.strip().lower()

    db.execute(
        text(
            "SELECT pg_advisory_xact_lock("
            "hashtextextended(:email, 0)"
            ")"
        ),
        {"email": email},
    )

    session = db.scalar(
        select(RegistrationSession).where(
            RegistrationSession.email == email
        ).with_for_update()
    )

    if session is None:
        raise RegistrationSessionError("Registration session not found")

    if session.registration_expires_at <= datetime.now(timezone.utc):
        db.execute(delete(OTPCode).where(OTPCode.email == email))
        db.delete(session)
        db.commit()
        raise RegistrationSessionError("Registration session expired")

    if session.email_verified_at is not None:
        raise ValueError("Email already verified")

    verify_otp_code(db, session, otp)
    return create_registration_verification_proof(
        email,
        session.id,
        session.registration_expires_at,
    )


def complete_registration(
    db: Session,
    email: str,
    username: str,
    password: str,
    verification_proof: str,
) -> tuple[User, str, str]:
    email = email.strip().lower()
    if not username_is_valid(username):
        raise ValueError("Username must be 8-16 characters using only letters and numbers")
    username = username.lower()

    try:
        proof = decode_registration_verification_proof(verification_proof)
        if proof["sub"] != email:
            raise ValueError
        session_id = int(proof["sid"])
    except (ValueError, TypeError, KeyError) as exc:
        raise RegistrationProofError("Invalid registration verification proof") from exc

    validate_password(password)

    db.execute(
        text(
            "SELECT pg_advisory_xact_lock(" "hashtextextended(:email, 0)" ")"
        ),
        {"email": email},
    )

    session = db.scalar(
        select(RegistrationSession)
        .where(
            RegistrationSession.id == session_id,
            RegistrationSession.email == email,
        )
        .with_for_update()
    )

    if session is None:
        raise RegistrationSessionError("Registration session not found")

    if session.registration_expires_at <= datetime.now(timezone.utc):
        db.execute(delete(OTPCode).where(OTPCode.email == email))
        db.delete(session)
        db.commit()
        raise RegistrationSessionError("Registration session expired")

    if session.email_verified_at is not None:
        raise RegistrationSessionError("Registration session is no longer valid")

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
        db.execute(delete(OTPCode).where(OTPCode.email == email))

        access_token, refresh_token = create_authenticated_session(db, user)
        db.refresh(user)
        return user, access_token, refresh_token

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
