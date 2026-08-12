from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from backend.app.models.refresh_session import RefreshSession
from backend.app.models.user import User
from backend.app.services.password import verify_password
from backend.app.services.token import (
    create_access_token,
    create_refresh_token,
    fingerprint_refresh_token,
    get_refresh_token_expiry,
    hash_refresh_token,
    verify_refresh_token,
)


def login(
    db: Session,
    identifier: str,
    password: str,
) -> tuple[str, str]:
    identifier = identifier.strip()

    if not identifier:
        raise ValueError("Identifier is required")

    if not password:
        raise ValueError("Password is required")

    normalized_identifier = identifier.lower()

    user = db.scalar(
        select(User).where(
            or_(
                User.email == normalized_identifier,
                User.username == identifier,
            )
        )
    )

    if user is None:
        raise ValueError("Invalid credentials")

    if not verify_password(password, user.password_hash):
        raise ValueError("Invalid credentials")

    if not user.email_verified:
        raise ValueError("Email verification required")

    refresh_token = create_refresh_token()

    refresh_session = RefreshSession(
        user_id=user.id,
        token_fingerprint=fingerprint_refresh_token(refresh_token),
        token_hash=hash_refresh_token(refresh_token),
        expires_at=get_refresh_token_expiry(),
    )

    db.add(refresh_session)

    try:
        access_token = create_access_token(user.id)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return access_token, refresh_token



def refresh_access_token(
    db: Session,
    refresh_token: str,
) -> tuple[str, str]:
    refresh_token = refresh_token.strip()

    if not refresh_token:
        raise ValueError("Refresh token is required")

    fingerprint = fingerprint_refresh_token(refresh_token)
    now = datetime.now(timezone.utc)

    refresh_session = db.scalar(
        select(RefreshSession)
        .where(
            RefreshSession.token_fingerprint == fingerprint,
            RefreshSession.revoked_at.is_(None),
            RefreshSession.expires_at > now,
        )
        .with_for_update()
    )

    if refresh_session is None:
        raise ValueError("Invalid refresh token")

    if not verify_refresh_token(
        refresh_token,
        refresh_session.token_hash,
    ):
        raise ValueError("Invalid refresh token")

    user = db.scalar(
        select(User).where(User.id == refresh_session.user_id)
    )

    if user is None:
        raise ValueError("Invalid refresh token")

    if not user.email_verified:
        raise ValueError("Email verification required")

    new_refresh_token = create_refresh_token()

    refresh_session.revoked_at = now

    new_refresh_session = RefreshSession(
        user_id=user.id,
        token_fingerprint=fingerprint_refresh_token(
            new_refresh_token
        ),
        token_hash=hash_refresh_token(new_refresh_token),
        expires_at=get_refresh_token_expiry(),
    )

    db.add(new_refresh_session)

    try:
        access_token = create_access_token(user.id)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return access_token, new_refresh_token



def logout(
    db: Session,
    refresh_token: str,
) -> None:
    refresh_token = refresh_token.strip()

    if not refresh_token:
        raise ValueError("Refresh token is required")

    fingerprint = fingerprint_refresh_token(refresh_token)

    refresh_session = db.scalar(
        select(RefreshSession)
        .where(
            RefreshSession.token_fingerprint == fingerprint,
            RefreshSession.revoked_at.is_(None),
        )
        .with_for_update()
    )

    if refresh_session is None:
        raise ValueError("Invalid refresh token")

    if not verify_refresh_token(
        refresh_token,
        refresh_session.token_hash,
    ):
        raise ValueError("Invalid refresh token")

    refresh_session.revoked_at = datetime.now(timezone.utc)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
