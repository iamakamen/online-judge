"""Seed the canonical Online Judge V1 Problem Management data.

Usage:
    backend/.venv/bin/python scripts/seed.py --dry-run
    backend/.venv/bin/python scripts/seed.py

The seed is deterministic and idempotent. Canonical topics and problems are
identified by stable slugs. Existing records with other slugs are reported
and never deleted. Test cases are matched by their complete deterministic
content, so unexpected existing cases are preserved as well.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import select

from backend.app.db.session import SessionLocal
from backend.app.models.problem import Difficulty, Problem
from backend.app.models.test_case import TestCase
from backend.app.models.topic import Topic
from backend.app.models.user import User  # noqa: F401 - registers FK metadata


@dataclass(frozen=True)
class SeedCase:
    input: str
    expected_output: str
    run_enabled: bool
    submit_enabled: bool
    is_sample: bool
    display_order: int


@dataclass(frozen=True)
class SeedProblem:
    topic_slug: str
    slug: str
    title: str
    statement: str
    constraints: str
    difficulty: Difficulty
    tags: tuple[str, ...]
    python_starter: str
    cpp_starter: str
    time_limit_ms: int
    memory_limit_mb: int
    cases: tuple[SeedCase, ...]


@dataclass(frozen=True)
class SeedTopic:
    slug: str
    name: str
    display_order: int


TOPICS = (
    SeedTopic("arrays", "Arrays", 1),
    SeedTopic("strings", "Strings", 2),
    SeedTopic("linked-list", "Linked List", 3),
    SeedTopic("stack-queue", "Stack & Queue", 4),
    SeedTopic("dynamic-programming", "Dynamic Programming", 5),
)


def starter(function: str, python_args: str, cpp_args: str) -> tuple[str, str]:
    return (
        f"def {function}({python_args}):\n    pass\n",
        f"class Solution {{\npublic:\n    auto {function}({cpp_args}) {{\n        // TODO\n    }}\n}};\n",
    )


def cases(
    sample_input: str,
    sample_output: str,
    run_input: str,
    run_output: str,
    hidden_input: str,
    hidden_output: str,
) -> tuple[SeedCase, ...]:
    return (
        SeedCase(sample_input, sample_output, True, True, True, 1),
        SeedCase(run_input, run_output, True, False, False, 2),
        SeedCase(hidden_input, hidden_output, False, True, False, 3),
    )


def problem(
    topic_slug: str,
    slug: str,
    title: str,
    statement: str,
    constraints: str,
    difficulty: Difficulty,
    tags: tuple[str, ...],
    function: str,
    python_args: str,
    cpp_args: str,
    test_cases: tuple[SeedCase, ...],
    time_limit_ms: int,
    memory_limit_mb: int,
) -> SeedProblem:
    python_starter, cpp_starter = starter(function, python_args, cpp_args)
    return SeedProblem(
        topic_slug=topic_slug,
        slug=slug,
        title=title,
        statement=statement,
        constraints=constraints,
        difficulty=difficulty,
        tags=tags,
        python_starter=python_starter,
        cpp_starter=cpp_starter,
        time_limit_ms=time_limit_ms,
        memory_limit_mb=memory_limit_mb,
        cases=test_cases,
    )


PROBLEMS = (
    problem(
        "arrays", "two-sum", "Two Sum",
        "Given an array of integers and a target, return the indices of two distinct values that add to the target.",
        """2 <= nums.length <= 10^5
-10^9 <= nums[i], target <= 10^9""",
        Difficulty.EASY, ("hash-map", "complement", "lookup"), "two_sum",
        "nums: list[int], target: int", "nums, target", cases(
            "4\n2 7 11 15\n9", "0 1", "4\n3 2 4 7\n6", "1 2", "5\n1 5 3 7 9\n10", "1 2"),
        time_limit_ms=1000, memory_limit_mb=128),
    problem(
        "arrays", "maximum-subarray", "Maximum Subarray",
        "Find the contiguous subarray with the largest sum and return that sum.",
        """1 <= nums.length <= 10^5
-10^4 <= nums[i] <= 10^4""",
        Difficulty.MEDIUM, ("kadane", "greedy", "subarray"), "max_sub_array",
        "nums: list[int]", "nums", cases(
            "-2 1 -3 4 -1 2 1 -5 4", "6", "1", "1", "-8 -3 -6 -2 -5 -4", "-2"),
        time_limit_ms=1000, memory_limit_mb=128),
    problem(
        "arrays", "merge-intervals", "Merge Intervals",
        "Merge every pair of overlapping intervals and return the resulting sorted intervals.",
        """1 <= intervals.length <= 10^4
intervals[i].length == 2
-10^4 <= start <= end <= 10^4""",
        Difficulty.MEDIUM, ("sorting", "intervals", "sweep"), "merge",
        "intervals: list[list[int]]", "intervals", cases(
            "1 3;2 6;8 10;15 18", "1 6;8 10;15 18", "1 4;4 5", "1 5", "1 10;2 3;4 8", "1 10"),
        time_limit_ms=1500, memory_limit_mb=128),
    problem(
        "arrays", "product-except-self", "Product of Array Except Self",
        "Return an array where each position contains the product of every input value except the value at that position.",
        """2 <= nums.length <= 10^5
-30 <= nums[i] <= 30""",
        Difficulty.MEDIUM, ("prefix-product", "suffix-product", "no-division"), "product_except_self",
        "nums: list[int]", "nums", cases(
            "1 2 3 4", "24 12 8 6", "-1 1 0 -3 3", "0 0 9 0 0", "2 3 4 5", "60 40 30 24"),
        time_limit_ms=1000, memory_limit_mb=128),
    problem(
        "arrays", "rotate-array", "Rotate Array",
        "Rotate an array to the right by k positions in place and return the resulting array.",
        """1 <= nums.length <= 10^5
-10^9 <= nums[i] <= 10^9
0 <= k <= 10^9""",
        Difficulty.MEDIUM, ("in-place", "reversal", "cyclic"), "rotate",
        "nums: list[int], k: int", "nums, k", cases(
            "1 2 3 4 5 6 7\n3", "5 6 7 1 2 3 4", "-1 -100 3\n2", "-100 3 -1", "0 1 2 3 4 5\n8", "4 5 0 1 2 3"),
        time_limit_ms=1000, memory_limit_mb=128),
    problem(
        "strings", "valid-anagram", "Valid Anagram",
        "Return whether two strings contain the same letters with the same frequencies.",
        """1 <= s.length, t.length <= 5 * 10^4
s and t contain lowercase English letters""",
        Difficulty.EASY, ("frequency-count", "hash-map", "sorting"), "is_anagram",
        "s: str, t: str", "s, t", cases(
            "anagram\nnagaram", "true", "rat\ncar", "false", "conversation\nvoicesranton", "true"),
        time_limit_ms=1000, memory_limit_mb=128),
    problem(
        "strings", "longest-substring-without-repeat", "Longest Substring Without Repeating Characters",
        "Return the length of the longest substring containing no repeated characters.",
        """0 <= s.length <= 5 * 10^4
s contains printable ASCII characters""",
        Difficulty.MEDIUM, ("sliding-window", "hash-set", "two-pointers"), "length_of_longest_substring",
        "s: str", "s", cases(
            "abcabcbb", "3", "bbbbb", "1", "pwwkew", "3"),
        time_limit_ms=1000, memory_limit_mb=128),
    problem(
        "strings", "group-anagrams", "Group Anagrams",
        "Group words that are anagrams of one another. The order of groups is unrestricted.",
        """1 <= strs.length <= 10^4
0 <= strs[i].length <= 100
strs[i] contains lowercase English letters""",
        Difficulty.MEDIUM, ("hash-map", "canonical-form", "sorting"), "group_anagrams",
        "strs: list[str]", "strs", cases(
            "eat tea tan ate nat bat", "aet ate eat;ant nat tan;abt bat", "", "", "abc bca cab xyz", "abc bca cab;xyz"),
        time_limit_ms=2000, memory_limit_mb=256),
    problem(
        "strings", "valid-palindrome", "Valid Palindrome",
        "Return whether the input is a palindrome after removing non-alphanumeric characters and ignoring case.",
        """1 <= s.length <= 2 * 10^5
s contains printable ASCII characters""",
        Difficulty.EASY, ("two-pointers", "string-normalization"), "is_palindrome",
        "s: str", "s", cases(
            "A man, a plan, a canal: Panama", "true", "race a car", "false", "0P", "false"),
        time_limit_ms=1000, memory_limit_mb=128),
    problem(
        "strings", "minimum-window-substring", "Minimum Window Substring",
        "Return the smallest substring of s containing every character of t with the required multiplicity.",
        """1 <= s.length, t.length <= 10^5
s and t contain English letters""",
        Difficulty.HARD, ("sliding-window", "frequency-count", "two-pointers"), "min_window",
        "s: str, t: str", "s, t", cases(
            "ADOBECODEBANC\nABC", "BANC", "a\naa", "aa", "a\na", ""),
        time_limit_ms=2000, memory_limit_mb=128),
    problem(
        "linked-list", "reverse-linked-list", "Reverse Linked List",
        "Reverse a singly linked list and return its new head.",
        """0 <= number of nodes <= 10^5
-10^4 <= node value <= 10^4""",
        Difficulty.EASY, ("iteration", "pointers"), "reverse_list",
        "head", "head", cases(
            "1 2 3 4 5", "5 4 3 2 1", "1 2", "2 1", "", ""),
        time_limit_ms=1000, memory_limit_mb=128),
    problem(
        "linked-list", "merge-two-sorted-lists", "Merge Two Sorted Lists",
        "Merge two sorted singly linked lists into one sorted list.",
        """0 <= list1.length, list2.length <= 10^5
-10^4 <= node value <= 10^4""",
        Difficulty.EASY, ("two-pointers", "sentinel"), "merge_two_lists",
        "list1, list2", "list1, list2", cases(
            "1 2 4\n1 3 4", "1 1 2 3 4 4", "\n0", "0", "-5 -2\n-6 -3 -1", "-6 -5 -3 -2 -1"),
        time_limit_ms=1000, memory_limit_mb=128),
    problem(
        "linked-list", "linked-list-cycle", "Linked List Cycle",
        "Return whether a singly linked list contains a cycle.",
        """0 <= number of nodes <= 10^5
-10^4 <= node value <= 10^4""",
        Difficulty.EASY, ("fast-slow-pointers", "cycle-detection"), "has_cycle",
        "head", "head", cases(
            "3 2 0 -4\nindex=1", "true", "1\nindex=-1", "false", "1 2\nindex=0", "true"),
        time_limit_ms=1000, memory_limit_mb=128),
    problem(
        "linked-list", "remove-nth-node", "Remove Nth Node From End of List",
        "Remove the nth node from the end of a linked list and return the resulting list.",
        """1 <= number of nodes <= 10^5
1 <= n <= number of nodes""",
        Difficulty.MEDIUM, ("two-pointers", "sentinel"), "remove_nth_from_end",
        "head, n", "head, n", cases(
            "1 2 3 4 5\n2", "1 2 3 5", "1\n1", "", "1 2\n2", "2"),
        time_limit_ms=1000, memory_limit_mb=128),
    problem(
        "linked-list", "copy-list-with-random-pointer", "Copy List with Random Pointer",
        "Deep-copy a linked list whose nodes have both next and arbitrary random pointers.",
        """0 <= number of nodes <= 10^5
-10^4 <= node value <= 10^4""",
        Difficulty.HARD, ("hash-map", "deep-copy"), "copy_random_list",
        "head", "head", cases(
            "7,null;13,0;11,4;10,2;1,0", "7,null;13,0;11,4;10,2;1,0", "1,null", "1,null", "", ""),
        time_limit_ms=2000, memory_limit_mb=256),
    problem(
        "stack-queue", "valid-parentheses", "Valid Parentheses",
        "Return whether every opening bracket is closed by the correct bracket in the correct order.",
        """1 <= s.length <= 10^5
s contains only ()[]{}""",
        Difficulty.EASY, ("stack", "parsing", "matching"), "is_valid",
        "s: str", "s", cases(
            "()[]{}", "true", "(]", "false", "([)]", "false"),
        time_limit_ms=1000, memory_limit_mb=128),
    problem(
        "stack-queue", "min-stack", "Min Stack",
        "Design a stack supporting push, pop, top, and retrieving the minimum value in constant time.",
        """1 <= number of operations <= 10^5
-10^9 <= value <= 10^9""",
        Difficulty.MEDIUM, ("stack", "design", "constant-time"), "min_stack_operations",
        "operations: list[str]", "operations", cases(
            "push -2;push 0;push -3;getMin;pop;top;getMin", "-3 -2 -2", "push 2;push 1;getMin", "1", "push 5;push 4;pop;getMin", "5"),
        time_limit_ms=1500, memory_limit_mb=128),
    problem(
        "stack-queue", "daily-temperatures", "Daily Temperatures",
        "For each day, return how many days must pass before a warmer temperature occurs.",
        """1 <= temperatures.length <= 10^5
30 <= temperatures[i] <= 100""",
        Difficulty.MEDIUM, ("monotonic-stack", "stack", "next-greater"), "daily_temperatures",
        "temperatures: list[int]", "temperatures", cases(
            "73 74 75 71 69 72 76 73", "1 1 4 2 1 1 0 0", "30 40 50 60", "1 1 1 0", "90 80 70", "0 0 0"),
        time_limit_ms=1500, memory_limit_mb=128),
    problem(
        "stack-queue", "evaluate-reverse-polish-notation", "Evaluate Reverse Polish Notation",
        "Evaluate an arithmetic expression written in postfix notation using integer division toward zero.",
        """1 <= tokens.length <= 10^4
tokens form a valid RPN expression""",
        Difficulty.MEDIUM, ("stack", "expression-evaluation", "division"), "eval_rpn",
        "tokens: list[str]", "tokens", cases(
            "2 1 + 3 *", "9", "4 13 5 / +", "6", "10 6 9 3 + -11 * / * 17 + 5 +", "22"),
        time_limit_ms=1000, memory_limit_mb=128),
    problem(
        "stack-queue", "sliding-window-maximum", "Sliding Window Maximum",
        "Return the maximum value in every contiguous window of size k.",
        """1 <= nums.length <= 10^5
-10^4 <= nums[i] <= 10^4
1 <= k <= nums.length""",
        Difficulty.HARD, ("deque", "monotonic-queue", "sliding-window"), "max_sliding_window",
        "nums: list[int], k: int", "nums, k", cases(
            "1 3 -1 -3 5 3 6 7\n3", "3 3 5 5 6 7", "1\n1", "1", "9 8 7 6 5\n2", "9 8 7 6"),
        time_limit_ms=2000, memory_limit_mb=128),
    problem(
        "dynamic-programming", "climbing-stairs", "Climbing Stairs",
        "Count the distinct ways to reach the nth step when each move advances one or two steps.",
        """1 <= n <= 45""",
        Difficulty.EASY, ("fibonacci", "counting"), "climb_stairs",
        "n: int", "n", cases(
            "2", "2", "3", "3", "10", "89"),
        time_limit_ms=1000, memory_limit_mb=128),
    problem(
        "dynamic-programming", "house-robber", "House Robber",
        "Maximize the amount robbed from non-adjacent houses without triggering the alarm.",
        """1 <= nums.length <= 10^5
0 <= nums[i] <= 10^4""",
        Difficulty.MEDIUM, ("one-dimensional-dp", "optimization"), "rob",
        "nums: list[int]", "nums", cases(
            "1 2 3 1", "4", "2 7 9 3 1", "12", "2 1 1 2", "4"),
        time_limit_ms=1000, memory_limit_mb=128),
    problem(
        "dynamic-programming", "coin-change", "Coin Change",
        "Return the fewest coins needed to make the target amount, or -1 if it is impossible.",
        """1 <= coins.length <= 100
1 <= coins[i] <= 10^4
1 <= amount <= 10^4""",
        Difficulty.MEDIUM, ("unbounded-knapsack", "bottom-up"), "coin_change",
        "coins: list[int], amount: int", "coins, amount", cases(
            "1 2 5\n11", "3", "2\n3", "-1", "1 3 4\n6", "2"),
        time_limit_ms=2500, memory_limit_mb=128),
    problem(
        "dynamic-programming", "longest-increasing-subsequence", "Longest Increasing Subsequence",
        "Return the length of the longest strictly increasing subsequence.",
        """1 <= nums.length <= 2500
-10^4 <= nums[i] <= 10^4""",
        Difficulty.MEDIUM, ("binary-search", "subsequence"), "length_of_lis",
        "nums: list[int]", "nums", cases(
            "10 9 2 5 3 7 101 18", "4", "0 1 0 3 2 3", "4", "7 7 7 7", "1"),
        time_limit_ms=2000, memory_limit_mb=128),
    problem(
        "dynamic-programming", "edit-distance", "Edit Distance",
        "Return the minimum number of insertions, deletions, and substitutions needed to transform one word into another.",
        """1 <= word1.length, word2.length <= 500
word1 and word2 contain lowercase English letters""",
        Difficulty.HARD, ("two-dimensional-dp", "levenshtein"), "min_distance",
        "word1: str, word2: str", "word1, word2", cases(
            "horse\nros", "3", "intention\nexecution", "5", "abc\nabc", "0"),
        time_limit_ms=3000, memory_limit_mb=256),
)


def _case_identity(test_case: TestCase | SeedCase) -> tuple[object, ...]:
    return (
        test_case.input,
        test_case.expected_output,
        test_case.display_order,
    )


def _set_if_changed(record: object, field: str, value: object) -> bool:
    if getattr(record, field) == value:
        return False
    setattr(record, field, value)
    return True


def _report_existing_records(
    topics: list[Topic], problems: list[Problem]
) -> None:
    topic_slugs = {topic.slug for topic in TOPICS}
    problem_slugs = {item.slug for item in PROBLEMS}
    extra_topics = [topic for topic in topics if topic.slug not in topic_slugs]
    extra_problems = [
        item for item in problems if item.slug not in problem_slugs
    ]

    if extra_topics:
        print("Unexpected existing topics (preserved):")
        for topic in extra_topics:
            print(f"  - {topic.slug}: {topic.name}")
    if extra_problems:
        print("Unexpected existing problems (preserved):")
        for item in extra_problems:
            print(f"  - {item.slug}: {item.title}")
            if item.title.casefold() == "two sum":
                print("    conflict: Two Sum title uses a non-canonical slug")
    if not extra_topics and not extra_problems:
        print("No unexpected existing topics or problems found.")


def seed(*, dry_run: bool = False) -> None:
    with SessionLocal() as db:
        topics = db.scalars(select(Topic).order_by(Topic.id)).all()
        problems = db.scalars(select(Problem).order_by(Problem.id)).all()
        _report_existing_records(topics, problems)

        topics_by_slug = {topic.slug: topic for topic in topics}
        problems_by_slug = {item.slug: item for item in problems}

        if dry_run:
            canonical_problem_slugs = {item.slug for item in PROBLEMS}
            existing_canonical_problems = [
                item
                for item in problems
                if item.slug in canonical_problem_slugs
            ]
            print(
                "Dry run: no database changes made. "
                f"Would create {len(TOPICS) - len(topics_by_slug.keys() & {item.slug for item in TOPICS})} topics and "
                f"{len(PROBLEMS) - len(existing_canonical_problems)} problems."
            )
            print(
                "Canonical test cases would be reconciled for "
                f"{len(existing_canonical_problems)} existing and "
                f"{len(PROBLEMS) - len(existing_canonical_problems)} new problems."
            )
            return

        topic_ids: dict[str, int] = {}
        created_topics = 0
        updated_topics = 0
        created_problems = 0
        updated_problems = 0
        created_cases = 0
        unexpected_cases = 0

        for seed_topic in TOPICS:
            topic = topics_by_slug.get(seed_topic.slug)
            if topic is None:
                topic = Topic(
                    name=seed_topic.name,
                    slug=seed_topic.slug,
                    display_order=seed_topic.display_order,
                )
                db.add(topic)
                db.flush()
                topics_by_slug[seed_topic.slug] = topic
                created_topics += 1
            else:
                changed = False
                changed |= _set_if_changed(topic, "name", seed_topic.name)
                changed |= _set_if_changed(
                    topic, "display_order", seed_topic.display_order
                )
                updated_topics += int(changed)
            topic_ids[seed_topic.slug] = topic.id

        for seed_problem in PROBLEMS:
            problem_record = problems_by_slug.get(seed_problem.slug)
            values = {
                "topic_id": topic_ids[seed_problem.topic_slug],
                "title": seed_problem.title,
                "statement": seed_problem.statement,
                "constraints": seed_problem.constraints,
                "difficulty": seed_problem.difficulty,
                "tags": list(seed_problem.tags),
                "starter_code": {
                    "python": seed_problem.python_starter,
                    "cpp": seed_problem.cpp_starter,
                },
                "time_limit_ms": seed_problem.time_limit_ms,
                "memory_limit_mb": seed_problem.memory_limit_mb,
            }
            if problem_record is None:
                problem_record = Problem(slug=seed_problem.slug, **values)
                db.add(problem_record)
                db.flush()
                problems_by_slug[seed_problem.slug] = problem_record
                created_problems += 1
            else:
                changed = False
                for field, value in values.items():
                    changed |= _set_if_changed(problem_record, field, value)
                updated_problems += int(changed)

            existing_cases = list(
                db.scalars(
                    select(TestCase)
                    .where(TestCase.problem_id == problem_record.id)
                    .order_by(TestCase.id)
                ).all()
            )

            used_case_ids: set[int] = set()

            for seed_case in seed_problem.cases:
                matches = [
                    case
                    for case in existing_cases
                    if case.id not in used_case_ids
                    and _case_identity(case) == _case_identity(seed_case)
                ]

                if matches:
                    canonical_case = matches[0]
                    used_case_ids.add(canonical_case.id)

                    if not dry_run:
                        _set_if_changed(
                            canonical_case,
                            "run_enabled",
                            seed_case.run_enabled,
                        )
                        _set_if_changed(
                            canonical_case,
                            "submit_enabled",
                            seed_case.submit_enabled,
                        )
                        _set_if_changed(
                            canonical_case,
                            "is_sample",
                            seed_case.is_sample,
                        )

                    unexpected_cases += len(matches) - 1
                    continue

                if not dry_run:
                    db.add(
                        TestCase(
                            problem_id=problem_record.id,
                            input=seed_case.input,
                            expected_output=seed_case.expected_output,
                            run_enabled=seed_case.run_enabled,
                            submit_enabled=seed_case.submit_enabled,
                            is_sample=seed_case.is_sample,
                            display_order=seed_case.display_order,
                        )
                    )

                created_cases += 1
            unexpected_cases += sum(
                1
                for case in existing_cases
                if case.id not in used_case_ids
            )

        db.commit()

        print(
            "Topics: "
            f"created={created_topics}, updated={updated_topics}, "
            f"canonical={len(TOPICS)}"
        )
        print(
            "Problems: "
            f"created={created_problems}, updated={updated_problems}, "
            f"canonical={len(PROBLEMS)}"
        )
        print(
            "Test cases: "
            f"canonical_per_problem={len(PROBLEMS[0].cases)}, "
            f"created={created_cases}"
        )
        if unexpected_cases:
            print(
                "Unexpected or duplicate test cases under canonical problems "
                f"(preserved): {unexpected_cases}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="inspect and plan seed changes without committing them",
    )
    args = parser.parse_args()
    seed(dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
