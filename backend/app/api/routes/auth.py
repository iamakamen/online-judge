from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from redis import Redis
from redis.exceptions import RedisError
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
    create_authenticated_session,
    login,
    logout,
    refresh_access_token,
)
from backend.app.services.registration import (
    complete_registration,
    start_registration,
    verify_registration_otp,
    username_is_available,
)
from backend.app.api.dependencies import get_redis
from backend.app.services.otp import OTPRequestPolicyError

router = APIRouter(prefix="/auth", tags=["authentication"])

USERNAME_AVAILABILITY_LIMIT = 30
USERNAME_AVAILABILITY_WINDOW_SECONDS = 60


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
        otp = start_registration(
            db=db,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
        )
    except OTPRequestPolicyError as exc:
        headers = {"Retry-After": str(exc.retry_after)} if exc.retry_after else None
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
            headers=headers,
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return {
        "status": "otp_sent",
        "message": "Verification code sent to your email.",
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
    db: Session = Depends(get_db),
):
    try:
        verify_registration_otp(
            db=db,
            email=request.email,
            otp=request.otp,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return {
        "status": "email_verified",
        "message": "Email verified successfully.",
    }


@router.post("/register/complete")
def register_complete(
    request: RegisterCompleteRequest,
    db: Session = Depends(get_db),
):
    try:
        user = complete_registration(
            db=db,
            email=request.email,
            username=request.username,
            password=request.password,
        )
        access_token, refresh_token = create_authenticated_session(db, user)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

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
