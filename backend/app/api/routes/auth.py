from datetime import datetime, timezone
import os

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterCompleteRequest,
    RegisterStartRequest,
    VerifyOTPRequest,
)
from backend.app.services.authentication import (
    login,
    logout,
    refresh_access_token,
)
from backend.app.services.registration import (
    EmailAlreadyRegisteredError,
    RegistrationEmailDeliveryError,
    RegistrationSessionError,
    RegistrationProofError,
    REGISTRATION_SESSION_LIFETIME_MINUTES,
    complete_registration,
    start_registration,
    verify_registration_otp,
    username_is_available,
)
from backend.app.models.registration_session import RegistrationSession
from backend.app.api.dependencies import get_redis
from backend.app.services.otp import OTPRequestPolicyError, OTPVerificationError
from backend.app.services.token import (
    REGISTRATION_PROOF_EXPIRE_MINUTES,
    decode_registration_verification_proof,
)

router = APIRouter(prefix="/auth", tags=["authentication"])

USERNAME_AVAILABILITY_LIMIT = 30
USERNAME_AVAILABILITY_WINDOW_SECONDS = 60
REGISTRATION_PROOF_COOKIE = "registration_verification"
REGISTRATION_PROOF_COOKIE_PATH = "/auth/register"
REGISTRATION_PROOF_COOKIE_MAX_AGE = min(
    REGISTRATION_PROOF_EXPIRE_MINUTES * 60,
    REGISTRATION_SESSION_LIFETIME_MINUTES * 60,
)


def registration_proof_cookie_secure() -> bool:
    configured = os.getenv("REGISTRATION_PROOF_COOKIE_SECURE")
    if configured is not None:
        return configured.strip().lower() in {"1", "true", "yes", "on"}
    environment = os.getenv("ENVIRONMENT", os.getenv("APP_ENV", "development"))
    return environment.strip().lower() in {"production", "prod"}


def registration_proof_cookie_samesite() -> str:
    environment = os.getenv("ENVIRONMENT", os.getenv("APP_ENV", "development"))
    return (
        "none"
        if environment.strip().lower() in {"production", "prod"}
        else "lax"
    )


def set_registration_proof_cookie(response: Response, proof: str) -> None:
    response.set_cookie(
        key=REGISTRATION_PROOF_COOKIE,
        value=proof,
        max_age=REGISTRATION_PROOF_COOKIE_MAX_AGE,
        httponly=True,
        secure=registration_proof_cookie_secure(),
        samesite=registration_proof_cookie_samesite(),
        path=REGISTRATION_PROOF_COOKIE_PATH,
    )


def clear_registration_proof_cookie(response: Response) -> None:
    response.delete_cookie(
        key=REGISTRATION_PROOF_COOKIE,
        path=REGISTRATION_PROOF_COOKIE_PATH,
    )


def registration_proof_cookie_clear_header() -> str:
    response = Response()
    clear_registration_proof_cookie(response)
    return response.headers["set-cookie"]


def enforce_username_availability_rate_limit(request: Request, redis: Redis) -> None:
    client_host = request.client.host if request.client else "unknown"
    key = f"auth:username-availability:{client_host}"
    try:
        count = redis.incr(key)
        if count == 1:
            redis.expire(key, USERNAME_AVAILABILITY_WINDOW_SECONDS)
    except RedisError as exc:
        raise HTTPException(status_code=503, detail="Availability check unavailable") from exc
    if count > USERNAME_AVAILABILITY_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too many username availability checks",
            headers={"Retry-After": str(redis.ttl(key))},
        )





@router.post("/logout")
def logout_user(
    request: RefreshRequest,
    db: Session = Depends(get_db),
):
    try:
        logout(
            db=db,
            refresh_token=request.refresh_token,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    return {
        "status": "logged_out",
        "message": "Logout successful.",
    }


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login_user(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        access_token, refresh_token = login(
            db=db,
            identifier=request.identifier,
            password=request.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
)
def refresh_token(
    request: RefreshRequest,
    db: Session = Depends(get_db),
):
    try:
        access_token, refresh_token = refresh_access_token(
            db=db,
            refresh_token=request.refresh_token,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    return RefreshResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/register/start", status_code=status.HTTP_202_ACCEPTED)
def register_start(
    request: RegisterStartRequest,
    db: Session = Depends(get_db),
):
    try:
        result = start_registration(
            db=db,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
        )
    except OTPRequestPolicyError as exc:
        headers = {"Retry-After": str(exc.retry_after)} if exc.retry_after else None
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "code": exc.code,
                "message": (
                    "Please wait before requesting another verification code."
                    if exc.code == "request_cooldown"
                    else "You've reached the maximum of 5 verification-code requests for this 20-minute window. Please try again later."
                ),
            },
            headers=headers,
        ) from exc
    except RegistrationEmailDeliveryError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "email_delivery_failed",
                "message": "We couldn't send the verification code. Please try again.",
            },
        ) from exc
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": exc.code, "message": "That email is already registered."},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "registration_error", "message": "The registration request could not be completed."},
        ) from exc

    return {
        "status": "otp_sent",
        "message": "Verification code sent to your email.",
        "cooldown_seconds": result["cooldown_seconds"],
        "remaining_requests": result["remaining_requests"],
    }


@router.get("/register/username-availability")
def register_username_availability(
    request: Request,
    username: str = Query(min_length=1, max_length=100),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    enforce_username_availability_rate_limit(request, redis)
    normalized_username = username.strip().lower()
    return {
        "username": normalized_username,
        "available": username_is_available(db, normalized_username),
    }


@router.post("/register/verify-otp")
def register_verify_otp(
    request: VerifyOTPRequest,
    response: Response,
    db: Session = Depends(get_db),
):
    try:
        verification_proof = verify_registration_otp(
            db=db,
            email=request.email,
            otp=request.otp,
        )
    except OTPVerificationError as exc:
        messages = {
            "otp_invalid": "The verification code is incorrect.",
            "otp_expired": "This verification code has expired. Please request a new code.",
            "otp_superseded": "This verification code is no longer valid because a newer code was requested.",
            "otp_attempt_limit": "Too many incorrect attempts. This verification code is no longer valid. Please request a new code.",
            "verification_attempt_limit": "You've reached the maximum number of verification attempts for this registration window. Please try again later.",
        }
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": exc.code, "message": messages[exc.code]},
        ) from exc
    except RegistrationSessionError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": exc.code,
                "message": "Your registration session is missing or expired.",
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "registration_error", "message": "The verification request could not be completed."},
        ) from exc

    set_registration_proof_cookie(response, verification_proof)
    return {
        "status": "email_verified",
        "message": "Email verified successfully.",
    }


@router.get("/register/status")
def register_status(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    proof_token = request.cookies.get(REGISTRATION_PROOF_COOKIE)
    if not proof_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "registration_proof_missing", "message": "Email verification is required or has expired."},
        )

    try:
        proof = decode_registration_verification_proof(proof_token)
        session = db.scalar(
            select(RegistrationSession).where(
                RegistrationSession.id == int(proof["sid"]),
                RegistrationSession.email == proof["sub"],
            )
        )
        if session is None or session.registration_expires_at <= datetime.now(timezone.utc):
            raise ValueError
    except (ValueError, TypeError, KeyError):
        clear_registration_proof_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "registration_proof_invalid", "message": "Email verification is required or has expired."},
            headers={"Set-Cookie": registration_proof_cookie_clear_header()},
        ) from None

    return {
        "status": "email_verified",
        "email": session.email,
    }


@router.post("/register/complete")
def register_complete(
    request_context: Request,
    response: Response,
    request: RegisterCompleteRequest,
    db: Session = Depends(get_db),
):
    verification_proof = request_context.cookies.get(REGISTRATION_PROOF_COOKIE)
    if not verification_proof:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "registration_proof_missing", "message": "Email verification is required or has expired."},
        )
    try:
        user, access_token, refresh_token = complete_registration(
            db=db,
            email=request.email,
            username=request.username,
            password=request.password,
            verification_proof=verification_proof,
        )
    except RegistrationProofError as exc:
        clear_registration_proof_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": exc.code, "message": "Email verification is required or has expired."},
            headers={"Set-Cookie": registration_proof_cookie_clear_header()},
        ) from exc
    except RegistrationSessionError as exc:
        clear_registration_proof_cookie(response)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": exc.code, "message": "Your registration session is missing or expired."},
            headers={"Set-Cookie": registration_proof_cookie_clear_header()},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The registration request could not be completed.",
        ) from exc

    clear_registration_proof_cookie(response)
    return {
        "status": "registration_complete",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email_verified": user.email_verified,
        },
    }
