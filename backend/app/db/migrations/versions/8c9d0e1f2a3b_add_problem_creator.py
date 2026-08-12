"""add problem creator

Revision ID: 8c9d0e1f2a3b
Revises: 7b8c9d0e1f2a
Create Date: 2026-08-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8c9d0e1f2a3b"
down_revision: Union[str, Sequence[str], None] = "7b8c9d0e1f2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "problems",
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_problems_created_by_user_id_users",
        "problems",
        "users",
        ["created_by_user_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_problems_created_by_user_id",
        "problems",
        ["created_by_user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_problems_created_by_user_id",
        table_name="problems",
    )
    op.drop_constraint(
        "fk_problems_created_by_user_id_users",
        "problems",
        type_="foreignkey",
    )
    op.drop_column("problems", "created_by_user_id")
