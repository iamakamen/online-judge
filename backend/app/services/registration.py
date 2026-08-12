from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.app.models.registration_session import RegistrationSession
from backend.app.models.user import User
from backend.app.services.email import EmailDeliveryError, send_otp_email
from backend.app.services.otp import issue_otp, verify_otp_code
from backend.app.services.password import hash_password


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
        select(RegistrationSession).where(
            RegistrationSession.email == email
        )
    )

    if session is None:
        session = RegistrationSession(
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        db.add(session)
    else:
        session.first_name = first_name
        session.last_name = last_name
        session.email_verified_at = None
        session.updated_at = datetime.now(timezone.utc)

    try:
        otp = issue_otp(db, email)
        send_otp_email(
            recipient_email=email,
            otp=otp,
        )
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
    username = username.strip()

    if not username:
        raise ValueError("Username is required")

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

    except Exception:
        db.rollback()
        raise
