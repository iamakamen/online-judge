from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.user_problem_progress import UserProblemProgress
from backend.app.schemas.dashboard import DashboardResponse


def get_dashboard(db: Session, current_user: User) -> DashboardResponse:
    """Build the current V1 dashboard summary without new persistence."""
    solved_count = db.scalar(
        select(func.count(UserProblemProgress.id)).where(
            UserProblemProgress.user_id == current_user.id,
            UserProblemProgress.solved.is_(True),
        )
    ) or 0

    return DashboardResponse(
        first_name=current_user.first_name,
        solved_count=solved_count,
        day_streak="N/A",
        global_rank="N/A",
    )
