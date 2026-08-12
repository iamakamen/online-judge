from fastapi import APIRouter, Depends, HTTPException, status
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
    complete_registration,
    start_registration,
    verify_registration_otp,
)

router = APIRouter(prefix="/auth", tags=["authentication"])





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
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return {
        "status": "otp_sent",
        "message": "Verification code sent to your email.",
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
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return {
        "status": "registration_complete",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email_verified": user.email_verified,
        },
    }
