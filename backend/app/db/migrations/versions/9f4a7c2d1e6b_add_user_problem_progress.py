"""add user problem progress

Revision ID: 9f4a7c2d1e6b
Revises: 8c9d0e1f2a3b
Create Date: 2026-08-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9f4a7c2d1e6b"
down_revision: Union[str, Sequence[str], None] = "8c9d0e1f2a3b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_problem_progress",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column(
            "solved",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["problem_id"],
            ["problems.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "problem_id",
            name="uq_user_problem_progress_user_problem",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user_problem_progress")
