"""add problem constraints

Revision ID: b1c2d3e4f5a6
Revises: 9f4a7c2d1e6b
Create Date: 2026-08-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "9f4a7c2d1e6b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CANONICAL_CONSTRAINTS = (
    (
        "two-sum",
        """2 <= nums.length <= 10^5
-10^9 <= nums[i], target <= 10^9""",
    ),
    (
        "maximum-subarray",
        """1 <= nums.length <= 10^5
-10^4 <= nums[i] <= 10^4""",
    ),
    (
        "merge-intervals",
        """1 <= intervals.length <= 10^4
intervals[i].length == 2
-10^4 <= start <= end <= 10^4""",
    ),
    (
        "product-except-self",
        """2 <= nums.length <= 10^5
-30 <= nums[i] <= 30""",
    ),
    (
        "rotate-array",
        """1 <= nums.length <= 10^5
-10^9 <= nums[i] <= 10^9
0 <= k <= 10^9""",
    ),
    (
        "valid-anagram",
        """1 <= s.length, t.length <= 5 * 10^4
s and t contain lowercase English letters""",
    ),
    (
        "longest-substring-without-repeat",
        """0 <= s.length <= 5 * 10^4
s contains printable ASCII characters""",
    ),
    (
        "group-anagrams",
        """1 <= strs.length <= 10^4
0 <= strs[i].length <= 100
strs[i] contains lowercase English letters""",
    ),
    (
        "valid-palindrome",
        """1 <= s.length <= 2 * 10^5
s contains printable ASCII characters""",
    ),
    (
        "minimum-window-substring",
        """1 <= s.length, t.length <= 10^5
s and t contain English letters""",
    ),
    (
        "reverse-linked-list",
        """0 <= number of nodes <= 10^5
-10^4 <= node value <= 10^4""",
    ),
    (
        "merge-two-sorted-lists",
        """0 <= list1.length, list2.length <= 10^5
-10^4 <= node value <= 10^4""",
    ),
    (
        "linked-list-cycle",
        """0 <= number of nodes <= 10^5
-10^4 <= node value <= 10^4""",
    ),
    (
        "remove-nth-node",
        """1 <= number of nodes <= 10^5
1 <= n <= number of nodes""",
    ),
    (
        "copy-list-with-random-pointer",
        """0 <= number of nodes <= 10^5
-10^4 <= node value <= 10^4""",
    ),
    (
        "valid-parentheses",
        """1 <= s.length <= 10^5
s contains only ()[]{}""",
    ),
    (
        "min-stack",
        """1 <= number of operations <= 10^5
-10^9 <= value <= 10^9""",
    ),
    (
        "daily-temperatures",
        """1 <= temperatures.length <= 10^5
30 <= temperatures[i] <= 100""",
    ),
    (
        "evaluate-reverse-polish-notation",
        """1 <= tokens.length <= 10^4
tokens form a valid RPN expression""",
    ),
    (
        "sliding-window-maximum",
        """1 <= nums.length <= 10^5
-10^4 <= nums[i] <= 10^4
1 <= k <= nums.length""",
    ),
    ("climbing-stairs", """1 <= n <= 45"""),
    (
        "house-robber",
        """1 <= nums.length <= 10^5
0 <= nums[i] <= 10^4""",
    ),
    (
        "coin-change",
        """1 <= coins.length <= 100
1 <= coins[i] <= 10^4
1 <= amount <= 10^4""",
    ),
    (
        "longest-increasing-subsequence",
        """1 <= nums.length <= 2500
-10^4 <= nums[i] <= 10^4""",
    ),
    (
        "edit-distance",
        """1 <= word1.length, word2.length <= 500
word1 and word2 contain lowercase English letters""",
    ),
)


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "problems",
        sa.Column("constraints", sa.Text(), nullable=True),
    )

    connection = op.get_bind()
    update_statement = sa.text(
        "UPDATE problems "
        "SET constraints = :constraints "
        "WHERE slug = :slug"
    )
    for slug, constraints in CANONICAL_CONSTRAINTS:
        connection.execute(
            update_statement,
            {"slug": slug, "constraints": constraints},
        )

    null_count = connection.execute(
        sa.text(
            "SELECT count(*) "
            "FROM problems "
            "WHERE constraints IS NULL"
        )
    ).scalar_one()
    if null_count:
        raise RuntimeError(
            "Existing Problems could not be backfilled: "
            f"{null_count} Problem rows have NULL constraints"
        )

    op.alter_column(
        "problems",
        "constraints",
        existing_type=sa.Text(),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "problems",
        "constraints",
        existing_type=sa.Text(),
        nullable=True,
    )
    op.drop_column("problems", "constraints")
