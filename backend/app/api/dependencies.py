import os

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis import Redis
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.refresh_session import RefreshSession
from backend.app.services.authentication import IDLE_SESSION_TIMEOUT
from backend.app.services.execution.submission_transport import SubmissionTransport
from backend.app.services.submission_dispatch import SubmissionDispatcher
from backend.app.services.token import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)
DEFAULT_REDIS_URL = "redis://localhost:6379/0"


def get_redis() -> Redis:
    return Redis.from_url(os.getenv("REDIS_URL", DEFAULT_REDIS_URL))


def get_submission_dispatcher(
    redis: Redis = Depends(get_redis),
) -> SubmissionDispatcher:
    return SubmissionDispatcher(SubmissionTransport(redis))


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    session_row = db.execute(
        select(RefreshSession, func.current_timestamp()).where(
            RefreshSession.id == payload["sid"],
        )
    ).one_or_none()

    if session_row is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    refresh_session, database_now = session_row

    if (
        refresh_session.user_id != payload["sub"]
        or refresh_session.revoked_at is not None
        or refresh_session.expires_at <= database_now
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if database_now >= refresh_session.last_activity_at + IDLE_SESSION_TIMEOUT:
        refresh_session.revoked_at = database_now
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.scalar(select(User).where(User.id == payload["sub"]))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email verification required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    request.state.auth_session_id = refresh_session.id

    return user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator access required",
        )

    return current_user
