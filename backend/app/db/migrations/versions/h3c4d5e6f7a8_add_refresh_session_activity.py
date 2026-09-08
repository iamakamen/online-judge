"""add idle activity timestamp to refresh sessions

Revision ID: h3c4d5e6f7a8
Revises: g2b3c4d5e6f7
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "h3c4d5e6f7a8"
down_revision: str | None = "g2b3c4d5e6f7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "refresh_sessions",
        sa.Column(
            "last_activity_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.execute(
        sa.text(
            "UPDATE refresh_sessions "
            "SET last_activity_at = created_at "
            "WHERE last_activity_at IS NULL"
        )
    )
    op.alter_column(
        "refresh_sessions",
        "last_activity_at",
        nullable=False,
        server_default=sa.text("CURRENT_TIMESTAMP"),
    )


def downgrade() -> None:
    op.drop_column("refresh_sessions", "last_activity_at")
