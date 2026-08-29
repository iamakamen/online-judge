"""Seed the frozen Module 8 canonical problem-management dataset.

The catalog is loaded from docs/module-8/dataset/canonical-problem-data-v0.json.
User-facing stdin/stdout starters are loaded from docs/module-8/starter.

Usage:
    backend/.venv/bin/python scripts/seed.py --dry-run
    backend/.venv/bin/python scripts/seed.py
"""

from __future__ import annotations

import argparse
import json
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


CANONICAL_DATA_PATH = (
    PROJECT_ROOT / "docs/module-8/dataset/canonical-problem-data-v0.json"
)
STARTER_ROOT = PROJECT_ROOT / "docs/module-8/starter"

TOPIC_DIRECTORIES = {
    "Arrays": "arrays",
    "Strings": "strings",
    "Linked List": "linked-list",
    "Stack & Queue": "stack-queue",
    "Dynamic Programming": "dynamic-programming",
}

EXPECTED_CASE_KEYS = ("P1", "P2", "H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8")
PUBLIC_CASE_KEYS = {"P1", "P2"}

# These are the known rows from the superseded hard-coded Module 8 catalog.
# They are an explicit cleanup allowlist, not a general "delete unexpected"
# policy. linked-list-cycle is intentionally absent because its slug is still
# canonical and will be reconciled in place.
LEGACY_MODULE_8_PROBLEM_SLUGS = frozenset(
    {
        "two-sum",
        "maximum-subarray",
        "merge-intervals",
        "product-except-self",
        "rotate-array",
        "valid-anagram",
        "longest-substring-without-repeat",
        "group-anagrams",
        "valid-palindrome",
        "minimum-window-substring",
        "reverse-linked-list",
        "merge-two-sorted-lists",
        "remove-nth-node",
        "copy-list-with-random-pointer",
        "valid-parentheses",
        "min-stack",
        "daily-temperatures",
        "evaluate-reverse-polish-notation",
        "sliding-window-maximum",
        "climbing-stairs",
        "house-robber",
        "coin-change",
        "longest-increasing-subsequence",
        "edit-distance",
    }
)
DIAGNOSTIC_PROBLEM_SLUG = "c54d-diagnostic"


@dataclass(frozen=True)
class SeedExample:
    input: str
    output: str
    explanation: str


@dataclass(frozen=True)
class SeedCase:
    case_key: str
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
    examples: tuple[SeedExample, ...]
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


def _starter_path(problem: dict[str, object], language: str) -> Path:
    topic = str(problem["topic"])
    slug = str(problem["slug"])
    topic_directory = TOPIC_DIRECTORIES.get(topic)
    if topic_directory is None:
        raise ValueError(f"Unknown canonical topic: {topic}")
    extension = "py" if language == "python" else "cpp"
    return STARTER_ROOT / topic_directory / language / f"{slug}.{extension}"


def _read_starter(problem: dict[str, object], language: str) -> str:
    path = _starter_path(problem, language)
    if not path.is_file():
        raise ValueError(f"Missing {language} starter: {path}")
    source = path.read_text(encoding="utf-8")
    if not source.strip():
        raise ValueError(f"Empty {language} starter: {path}")
    if "TODO" not in source:
        raise ValueError(f"{language} starter has no algorithm TODO: {path}")
    return source


def _difficulty(value: object) -> Difficulty:
    try:
        return Difficulty[str(value).upper()]
    except KeyError as exc:
        raise ValueError(f"Invalid canonical difficulty: {value}") from exc


def load_canonical_data(
    path: Path = CANONICAL_DATA_PATH,
) -> tuple[tuple[SeedTopic, ...], tuple[SeedProblem, ...]]:
    """Load and validate the structured catalog without opening a DB session."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    raw_topics = payload.get("topics")
    raw_problems = payload.get("problems")
    if not isinstance(raw_topics, list) or len(raw_topics) != 5:
        raise ValueError("Canonical dataset must contain exactly five topics")
    if not isinstance(raw_problems, list) or len(raw_problems) != 25:
        raise ValueError("Canonical dataset must contain exactly 25 problems")

    topics = tuple(
        SeedTopic(
            slug=str(item["slug"]),
            name=str(item["name"]),
            display_order=int(item["display_order"]),
        )
        for item in raw_topics
    )
    topic_by_name = {topic.name: topic for topic in topics}
    if len(topic_by_name) != 5 or len({topic.slug for topic in topics}) != 5:
        raise ValueError("Canonical topic names and slugs must be unique")
    if [topic.display_order for topic in topics] != [1, 2, 3, 4, 5]:
        raise ValueError("Canonical topics must use display orders 1 through 5")

    problems: list[SeedProblem] = []
    seen_slugs: set[str] = set()
    topic_counts = {topic.name: 0 for topic in topics}

    for raw in raw_problems:
        slug = str(raw["slug"])
        topic_name = str(raw["topic"])
        if slug in seen_slugs:
            raise ValueError(f"Duplicate canonical problem slug: {slug}")
        seen_slugs.add(slug)
        topic = topic_by_name.get(topic_name)
        if topic is None:
            raise ValueError(f"Problem {slug} has an unknown topic: {topic_name}")

        tags = tuple(str(tag) for tag in raw["tags"])
        if len(tags) != 3 or len(set(tags)) != 3:
            raise ValueError(f"Problem {slug} must have exactly three unique tags")
        if topic_name in tags:
            raise ValueError(f"Problem {slug} uses its topic as a tag")

        raw_examples = raw["examples"]
        if not isinstance(raw_examples, list) or len(raw_examples) != 2:
            raise ValueError(f"Problem {slug} must have exactly two examples")
        examples = tuple(
            SeedExample(
                input=str(example["input"]),
                output=str(example["output"]),
                explanation=str(example["explanation"]),
            )
            for example in raw_examples
        )

        raw_cases = raw["test_cases"]
        if not isinstance(raw_cases, list) or len(raw_cases) != 10:
            raise ValueError(f"Problem {slug} must have exactly ten cases")
        case_keys = [str(raw_case["case_key"]) for raw_case in raw_cases]
        if case_keys != list(EXPECTED_CASE_KEYS):
            raise ValueError(
                f"Problem {slug} must use ordered P1/P2/H1-H8 case keys"
            )
        cases: list[SeedCase] = []
        for raw_case in raw_cases:
            case_key = str(raw_case["case_key"])
            expected_order = (
                EXPECTED_CASE_KEYS.index(case_key) + 1
                if case_key in EXPECTED_CASE_KEYS
                else None
            )
            if expected_order is None:
                raise ValueError(f"Problem {slug} has invalid case key: {case_key}")
            is_public = case_key in PUBLIC_CASE_KEYS
            expected_flags = (
                is_public,
                True,
                is_public,
                expected_order,
            )
            actual_flags = (
                bool(raw_case["run_enabled"]),
                bool(raw_case["submit_enabled"]),
                bool(raw_case["is_sample"]),
                int(raw_case["display_order"]),
            )
            if actual_flags != expected_flags:
                raise ValueError(
                    f"Problem {slug} case {case_key} has invalid flags/order"
                )
            cases.append(
                SeedCase(
                    case_key=case_key,
                    input=str(raw_case["input"]),
                    expected_output=str(raw_case["expected_output"]),
                    run_enabled=actual_flags[0],
                    submit_enabled=actual_flags[1],
                    is_sample=actual_flags[2],
                    display_order=actual_flags[3],
                )
            )

        if examples[0].input != cases[0].input or examples[0].output != cases[0].expected_output:
            raise ValueError(f"Problem {slug} Example 1 must equal P1")
        if examples[1].input != cases[1].input or examples[1].output != cases[1].expected_output:
            raise ValueError(f"Problem {slug} Example 2 must equal P2")

        topic_counts[topic_name] += 1
        problems.append(
            SeedProblem(
                topic_slug=topic.slug,
                slug=slug,
                title=str(raw["title"]),
                statement=str(raw["statement"]),
                constraints=str(raw["constraints"]),
                difficulty=_difficulty(raw["difficulty"]),
                tags=tags,
                examples=examples,
                python_starter=_read_starter(raw, "python"),
                cpp_starter=_read_starter(raw, "cpp"),
                time_limit_ms=int(raw["time_limit_ms"]),
                memory_limit_mb=int(raw["memory_limit_mb"]),
                cases=tuple(cases),
            )
        )

    if any(count != 5 for count in topic_counts.values()):
        raise ValueError(f"Canonical topic distribution is invalid: {topic_counts}")
    if sum(len(problem.cases) for problem in problems) != 250:
        raise ValueError("Canonical dataset must contain 250 test cases")

    return topics, tuple(problems)


TOPICS, PROBLEMS = load_canonical_data()
CANONICAL_PROBLEM_SLUGS = frozenset(problem.slug for problem in PROBLEMS)


def _case_identity(test_case: TestCase | SeedCase) -> tuple[int]:
    """Use stable display order as the DB identity for source case keys."""
    return (test_case.display_order,)


def _set_if_changed(record: object, field: str, value: object) -> bool:
    if getattr(record, field) == value:
        return False
    setattr(record, field, value)
    return True


def _remove_obsolete_problems(
    db,
    problems: list[Problem],
    *,
    dry_run: bool,
) -> set[str]:
    targets = LEGACY_MODULE_8_PROBLEM_SLUGS | {DIAGNOSTIC_PROBLEM_SLUG}
    obsolete = [
        problem
        for problem in problems
        if problem.slug in targets and problem.slug not in CANONICAL_PROBLEM_SLUGS
    ]
    for problem in obsolete:
        label = (
            "explicit diagnostic cleanup"
            if problem.slug == DIAGNOSTIC_PROBLEM_SLUG
            else "legacy Module 8 cleanup"
        )
        print(f"{label}: {problem.slug}")
        if not dry_run:
            db.delete(problem)
    return {problem.slug for problem in obsolete}


def _remove_obsolete_topics(
    db,
    topics: list[Topic],
    *,
    dry_run: bool,
) -> set[str]:
    """Remove only the explicitly allowlisted diagnostic topic."""
    obsolete = [
        topic
        for topic in topics
        if topic.slug == DIAGNOSTIC_PROBLEM_SLUG
        and topic.slug not in {item.slug for item in TOPICS}
    ]
    for topic in obsolete:
        print(f"explicit diagnostic topic cleanup: {topic.slug}")
        if not dry_run:
            db.delete(topic)
    return {topic.slug for topic in obsolete}


def _report_unexpected_records(
    topics: list[Topic],
    problems: list[Problem],
) -> None:
    canonical_topic_slugs = {topic.slug for topic in TOPICS}
    extra_topics = [topic for topic in topics if topic.slug not in canonical_topic_slugs]
    extra_problems = [
        problem
        for problem in problems
        if problem.slug not in CANONICAL_PROBLEM_SLUGS
        and problem.slug not in LEGACY_MODULE_8_PROBLEM_SLUGS
        and problem.slug != DIAGNOSTIC_PROBLEM_SLUG
    ]
    if extra_topics:
        print("Unexpected existing topics (preserved):")
        for topic in extra_topics:
            print(f"  - {topic.slug}: {topic.name}")
    if extra_problems:
        print("Unexpected existing problems (preserved):")
        for problem in extra_problems:
            print(f"  - {problem.slug}: {problem.title}")
    if not extra_topics and not extra_problems:
        print("No unexpected existing topics or problems found.")


def seed(*, dry_run: bool = False) -> None:
    with SessionLocal() as db:
        topics = db.scalars(select(Topic).order_by(Topic.id)).all()
        problems = db.scalars(select(Problem).order_by(Problem.id)).all()
        removed_slugs = _remove_obsolete_problems(
            db,
            problems,
            dry_run=dry_run,
        )
        removed_topic_slugs = _remove_obsolete_topics(
            db,
            topics,
            dry_run=dry_run,
        )
        _report_unexpected_records(
            [topic for topic in topics if topic.slug not in removed_topic_slugs],
            [problem for problem in problems if problem.slug not in removed_slugs],
        )

        topics_by_slug = {topic.slug: topic for topic in topics}
        problems_by_slug = {
            problem.slug: problem
            for problem in problems
            if problem.slug not in removed_slugs
        }

        if dry_run:
            existing_canonical = [
                problem
                for problem in problems
                if problem.slug in CANONICAL_PROBLEM_SLUGS
            ]
            print(
                "Dry run: no database changes made. "
                f"Would create {len(TOPICS) - len(topics_by_slug.keys() & {item.slug for item in TOPICS})} topics, "
                f"{len(PROBLEMS) - len(existing_canonical)} problems, "
                "and reconcile 250 canonical test cases."
            )
            return

        topic_ids: dict[str, int] = {}
        created_topics = updated_topics = 0
        created_problems = updated_problems = 0
        created_cases = updated_cases = deleted_cases = 0

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
                    topic,
                    "display_order",
                    seed_topic.display_order,
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
            canonical_by_identity: dict[tuple[int], TestCase] = {}
            stale_case_ids: set[int] = set()
            for existing_case in existing_cases:
                identity = _case_identity(existing_case)
                if identity in canonical_by_identity:
                    stale_case_ids.add(existing_case.id)
                else:
                    canonical_by_identity[identity] = existing_case

            expected_identities = {
                _case_identity(seed_case) for seed_case in seed_problem.cases
            }
            stale_case_ids.update(
                case.id
                for identity, case in canonical_by_identity.items()
                if identity not in expected_identities
            )

            for seed_case in seed_problem.cases:
                canonical_case = canonical_by_identity.get(
                    _case_identity(seed_case)
                )
                if canonical_case is None:
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
                    continue

                changed = False
                changed |= _set_if_changed(
                    canonical_case,
                    "input",
                    seed_case.input,
                )
                changed |= _set_if_changed(
                    canonical_case,
                    "expected_output",
                    seed_case.expected_output,
                )
                changed |= _set_if_changed(
                    canonical_case,
                    "run_enabled",
                    seed_case.run_enabled,
                )
                changed |= _set_if_changed(
                    canonical_case,
                    "submit_enabled",
                    seed_case.submit_enabled,
                )
                changed |= _set_if_changed(
                    canonical_case,
                    "is_sample",
                    seed_case.is_sample,
                )
                changed |= _set_if_changed(
                    canonical_case,
                    "display_order",
                    seed_case.display_order,
                )
                updated_cases += int(changed)

            for stale_case in existing_cases:
                if stale_case.id in stale_case_ids:
                    db.delete(stale_case)
                    deleted_cases += 1

        db.commit()
        print(
            "Topics: "
            f"created={created_topics}, updated={updated_topics}, canonical={len(TOPICS)}"
        )
        print(
            "Problems: "
            f"created={created_problems}, updated={updated_problems}, "
            f"removed={len(removed_slugs)}, canonical={len(PROBLEMS)}"
        )
        print(
            "Test cases: "
            f"created={created_cases}, updated={updated_cases}, "
            f"deleted={deleted_cases}, canonical={len(PROBLEMS) * 10}"
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
