"""add expiry to temporary registration sessions

Revision ID: g2b3c4d5e6f7
Revises: f1a2b3c4d5e6
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "g2b3c4d5e6f7"
down_revision: str | None = "f1a2b3c4d5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "registration_sessions",
        sa.Column(
            "registration_expires_at",
            sa.DateTime(timezone=True),
            nullable=True,
            server_default=sa.text("CURRENT_TIMESTAMP + INTERVAL '30 minutes'"),
        ),
    )
    op.execute(
        sa.text(
            "UPDATE registration_sessions "
            "SET registration_expires_at = created_at + INTERVAL '30 minutes' "
            "WHERE registration_expires_at IS NULL"
        )
    )
    op.alter_column(
        "registration_sessions",
        "registration_expires_at",
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("registration_sessions", "registration_expires_at")
