from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.dashboard import DashboardResponse
from backend.app.services.dashboard import get_dashboard


router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard_route(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DashboardResponse:
    return get_dashboard(db=db, current_user=current_user)
