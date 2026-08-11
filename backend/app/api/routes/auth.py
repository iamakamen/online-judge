from fastapi import APIRouter

from backend.app.schemas.auth import RegisterRequest


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register")
def register(request: RegisterRequest):
    return {"status": "registration_request_valid"}
