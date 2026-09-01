"""restore registration OTP request count server default

Revision ID: e0f1a2b3c4d5
Revises: d8e9f0a1b2c3
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "e0f1a2b3c4d5"
down_revision: str | None = "d8e9f0a1b2c3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE registration_sessions "
            "SET otp_request_count = 0 "
            "WHERE otp_request_count IS NULL"
        )
    )
    op.alter_column(
        "registration_sessions",
        "otp_request_count",
        existing_type=sa.Integer(),
        nullable=False,
        server_default=sa.text("0"),
    )


def downgrade() -> None:
    op.alter_column(
        "registration_sessions",
        "otp_request_count",
        existing_type=sa.Integer(),
        server_default=None,
    )
