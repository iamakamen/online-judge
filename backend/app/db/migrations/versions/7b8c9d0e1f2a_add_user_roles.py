"""add user roles

Revision ID: 7b8c9d0e1f2a
Revises: 1c2d3e4f5a6b
Create Date: 2026-08-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "7b8c9d0e1f2a"
down_revision: Union[str, Sequence[str], None] = "1c2d3e4f5a6b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    user_role_enum = postgresql.ENUM(
        "USER", "ADMIN", name="user_role_enum"
    )
    user_role_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "role",
            user_role_enum,
            nullable=True,
            server_default=sa.text("'USER'"),
        ),
    )

    op.execute("UPDATE users SET role = 'USER' WHERE role IS NULL")
    op.alter_column("users", "role", nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "role")

    user_role_enum = postgresql.ENUM(
        "USER", "ADMIN", name="user_role_enum"
    )
    user_role_enum.drop(op.get_bind(), checkfirst=True)
