from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.schemas.dashboard import DashboardResponse


def get_dashboard(db: Session, current_user: User) -> DashboardResponse:
    """Build the current V1 dashboard summary without new persistence."""
    return DashboardResponse(
        first_name=current_user.first_name,
        solved_count=0,
        day_streak=0,
        global_rank="N/A",
    )
