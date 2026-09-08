import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from dotenv import load_dotenv


load_dotenv()

JWT_ALGORITHM = "HS256"
REGISTRATION_PROOF_EXPIRE_MINUTES = 10

password_hash = PasswordHash.recommended()


def _get_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET_KEY")

    if not secret:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    return secret


def _get_access_token_expiry_minutes() -> int:
    value = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15")

    try:
        minutes = int(value)
    except ValueError as exc:
        raise RuntimeError(
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES must be an integer"
        ) from exc

    if minutes <= 0:
        raise RuntimeError(
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES must be positive"
        )

    return minutes


def _get_refresh_token_expiry_days() -> int:
    value = os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30")

    try:
        days = int(value)
    except ValueError as exc:
        raise RuntimeError(
            "JWT_REFRESH_TOKEN_EXPIRE_DAYS must be an integer"
        ) from exc

    if days <= 0:
        raise RuntimeError(
            "JWT_REFRESH_TOKEN_EXPIRE_DAYS must be positive"
        )

    return days


def create_access_token(user_id: int, session_id: int) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        minutes=_get_access_token_expiry_minutes()
    )

    payload = {
        "sub": str(user_id),
        "sid": str(session_id),
        "type": "access",
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        _get_jwt_secret(),
        algorithm=JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            _get_jwt_secret(),
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.PyJWTError as exc:
        raise ValueError("Invalid access token") from exc

    if payload.get("type") != "access":
        raise ValueError("Invalid access token")

    subject = payload.get("sub")

    if not subject:
        raise ValueError("Invalid access token")

    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid access token") from exc

    payload["sub"] = user_id

    session_id = payload.get("sid")

    if (
        not isinstance(session_id, str)
        or not session_id.isdecimal()
        or int(session_id) <= 0
    ):
        raise ValueError("Invalid access token")

    payload["sid"] = int(session_id)

    return payload


def create_registration_verification_proof(
    email: str,
    session_id: int,
    session_expires_at: datetime,
) -> str:
    now = datetime.now(timezone.utc)
    expires_at = min(
        now + timedelta(minutes=REGISTRATION_PROOF_EXPIRE_MINUTES),
        session_expires_at,
    )
    if expires_at <= now:
        raise ValueError("Registration session expired")
    return jwt.encode(
        {
            "sub": email.strip().lower(),
            "sid": str(session_id),
            "flow": "registration",
            "type": "registration_verification",
            "aud": "registration-complete",
            "iat": now,
            "exp": expires_at,
        },
        _get_jwt_secret(),
        algorithm=JWT_ALGORITHM,
    )


def decode_registration_verification_proof(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            _get_jwt_secret(),
            algorithms=[JWT_ALGORITHM],
            audience="registration-complete",
        )
    except jwt.PyJWTError as exc:
        raise ValueError("Invalid registration verification proof") from exc

    if (
        payload.get("type") != "registration_verification"
        or payload.get("flow") != "registration"
        or payload.get("aud") != "registration-complete"
        or not payload.get("sub")
        or not payload.get("sid")
    ):
        raise ValueError("Invalid registration verification proof")
    return payload


def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    return password_hash.hash(token)


def fingerprint_refresh_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def verify_refresh_token(
    token: str,
    hashed_token: str,
) -> bool:
    return password_hash.verify(token, hashed_token)


def get_refresh_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(
        days=_get_refresh_token_expiry_days()
    )
