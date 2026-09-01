"""add registration otp policy fields

Revision ID: d8e9f0a1b2c3
Revises: c7d8e9f0a1b2
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "d8e9f0a1b2c3"
down_revision: str | None = "c7d8e9f0a1b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "registration_sessions",
        sa.Column("otp_request_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "registration_sessions",
        sa.Column("otp_last_requested_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.alter_column("registration_sessions", "otp_request_count", server_default=None)


def downgrade() -> None:
    op.drop_column("registration_sessions", "otp_last_requested_at")
    op.drop_column("registration_sessions", "otp_request_count")
