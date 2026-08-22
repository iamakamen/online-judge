"""add wrong answer submission result status

Revision ID: a2b3c4d5e6f7
Revises: 9414428162bf
Create Date: 2026-08-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a2b3c4d5e6f7"
down_revision: Union[str, Sequence[str], None] = "9414428162bf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_ENUM_NAME = "submission_result_status_enum"
_OLD_VALUES = (
    "passed",
    "compile_error",
    "runtime_error",
    "time_limit_exceeded",
    "memory_limit_exceeded",
    "output_limit_exceeded",
    "system_error",
)


def upgrade() -> None:
    """Add WRONG_ANSWER to the PostgreSQL submission-result enum."""
    op.execute(
        sa.text(
            "ALTER TYPE submission_result_status_enum "
            "ADD VALUE IF NOT EXISTS 'wrong_answer'"
        )
    )


def downgrade() -> None:
    """Remove WRONG_ANSWER when no rows still use it.

    PostgreSQL cannot directly drop an enum value. Recreate the type after
    verifying that removing the value would not make existing data invalid.
    """
    bind = op.get_bind()
    in_use = bind.scalar(
        sa.text(
            "SELECT COUNT(*) FROM submission_results "
            "WHERE status = 'wrong_answer'"
        )
    )
    if in_use:
        raise RuntimeError(
            "cannot downgrade while submission_results uses wrong_answer"
        )

    old_type = f"{_ENUM_NAME}_old"
    values_sql = ", ".join(f"'{value}'" for value in _OLD_VALUES)

    op.execute(
        sa.text(
            f"ALTER TYPE {_ENUM_NAME} RENAME TO {old_type}"
        )
    )
    op.execute(
        sa.text(
            f"CREATE TYPE {_ENUM_NAME} AS ENUM ({values_sql})"
        )
    )
    op.execute(
        sa.text(
            "ALTER TABLE submission_results "
            "ALTER COLUMN status TYPE submission_result_status_enum "
            "USING status::text::submission_result_status_enum"
        )
    )
    op.execute(sa.text(f"DROP TYPE {old_type}"))
