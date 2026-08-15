from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class UserProblemProgress(Base):
    __tablename__ = "user_problem_progress"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "problem_id",
            name="uq_user_problem_progress_user_problem",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
    )
    solved: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
