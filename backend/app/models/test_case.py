from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class TestCase(Base):
    __tablename__ = "test_cases"
    __table_args__ = (
        CheckConstraint(
            "run_enabled OR submit_enabled",
            name="ck_test_cases_enabled_for_run_or_submit",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problems.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    input: Mapped[str] = mapped_column(Text, nullable=False)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    run_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    submit_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_sample: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
