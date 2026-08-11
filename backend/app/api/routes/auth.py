from fastapi import APIRouter

from backend.app.schemas.auth import (
    RegisterCompleteRequest,
    RegisterStartRequest,
    VerifyOTPRequest,
)


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register/start")
def register_start(request: RegisterStartRequest):
    return {"status": "registration_start_received"}


@router.post("/register/verify-otp")
def register_verify_otp(request: VerifyOTPRequest):
    return {"status": "registration_otp_received"}


@router.post("/register/complete")
def register_complete(request: RegisterCompleteRequest):
    return {"status": "registration_complete_received"}
