"""create topics, problems, and test cases

Revision ID: 1c2d3e4f5a6b
Revises: aee7211900ff
Create Date: 2026-08-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "1c2d3e4f5a6b"
down_revision: Union[str, Sequence[str], None] = "aee7211900ff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    difficulty_enum = postgresql.ENUM(
        "EASY", "MEDIUM", "HARD", name="difficulty_enum"
    )

    op.create_table(
        "topics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(op.f("ix_topics_slug"), "topics", ["slug"], unique=True)

    op.create_table(
        "problems",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("difficulty", difficulty_enum, nullable=False),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("starter_code", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("time_limit_ms", sa.Integer(), nullable=False),
        sa.Column("memory_limit_mb", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "time_limit_ms > 0",
            name="ck_problems_time_limit_positive",
        ),
        sa.CheckConstraint(
            "memory_limit_mb > 0",
            name="ck_problems_memory_limit_positive",
        ),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index(
        op.f("ix_problems_topic_id"), "problems", ["topic_id"], unique=False
    )
    op.create_index(op.f("ix_problems_slug"), "problems", ["slug"], unique=True)
    op.create_index(
        op.f("ix_problems_difficulty"),
        "problems",
        ["difficulty"],
        unique=False,
    )

    op.create_table(
        "test_cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("problem_id", sa.Integer(), nullable=False),
        sa.Column("input", sa.Text(), nullable=False),
        sa.Column("expected_output", sa.Text(), nullable=False),
        sa.Column("run_enabled", sa.Boolean(), nullable=False),
        sa.Column("submit_enabled", sa.Boolean(), nullable=False),
        sa.Column("is_sample", sa.Boolean(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "run_enabled OR submit_enabled",
            name="ck_test_cases_enabled_for_run_or_submit",
        ),
        sa.ForeignKeyConstraint(["problem_id"], ["problems.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_test_cases_problem_id"),
        "test_cases",
        ["problem_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_test_cases_problem_id"), table_name="test_cases")
    op.drop_table("test_cases")
    op.drop_index(op.f("ix_problems_difficulty"), table_name="problems")
    op.drop_index(op.f("ix_problems_slug"), table_name="problems")
    op.drop_index(op.f("ix_problems_topic_id"), table_name="problems")
    op.drop_table("problems")
    op.drop_index(op.f("ix_topics_slug"), table_name="topics")
    op.drop_table("topics")
    difficulty_enum = postgresql.ENUM(
        "EASY", "MEDIUM", "HARD", name="difficulty_enum"
    )
    difficulty_enum.drop(op.get_bind(), checkfirst=True)
