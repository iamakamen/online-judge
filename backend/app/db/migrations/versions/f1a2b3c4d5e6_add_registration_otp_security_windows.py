"""add registration OTP security windows

Revision ID: f1a2b3c4d5e6
Revises: e0f1a2b3c4d5
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "f1a2b3c4d5e6"
down_revision: str | None = "e0f1a2b3c4d5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "registration_sessions",
        sa.Column(
            "otp_request_window_started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "registration_sessions",
        sa.Column(
            "otp_verification_attempt_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
    )
    op.add_column(
        "registration_sessions",
        sa.Column(
            "otp_verification_window_started_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("registration_sessions", "otp_verification_window_started_at")
    op.drop_column("registration_sessions", "otp_verification_attempt_count")
    op.drop_column("registration_sessions", "otp_request_window_started_at")
