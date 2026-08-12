from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.problem import Difficulty, Problem
from backend.app.models.test_case import TestCase
from backend.app.models.topic import Topic


@dataclass
class ProblemListResult:
    items: list[Problem]
    total: int


def _is_problem_slug_conflict(exc: IntegrityError) -> bool:
    constraint_name = getattr(
        getattr(exc.orig, "diag", None),
        "constraint_name",
        None,
    )
    return constraint_name in {"problems_slug_key", "ix_problems_slug"}


def _require_topic(db: Session, topic_id: int) -> Topic:
    topic = db.scalar(select(Topic).where(Topic.id == topic_id))
    if topic is None:
        raise ValueError("Topic not found")
    return topic


def _validate_limits(time_limit_ms: int, memory_limit_mb: int) -> None:
    if time_limit_ms <= 0:
        raise ValueError("Time limit must be positive")
    if memory_limit_mb <= 0:
        raise ValueError("Memory limit must be positive")


def create_problem(
    db: Session,
    topic_id: int,
    title: str,
    slug: str,
    statement: str,
    difficulty: Difficulty,
    tags: list[str],
    starter_code: dict[str, str],
    time_limit_ms: int,
    memory_limit_mb: int,
) -> Problem:
    _require_topic(db, topic_id)
    _validate_limits(time_limit_ms, memory_limit_mb)

    if db.scalar(select(Problem).where(Problem.slug == slug)) is not None:
        raise ValueError("Problem slug already exists")

    problem = Problem(
        topic_id=topic_id,
        title=title,
        slug=slug,
        statement=statement,
        difficulty=difficulty,
        tags=tags,
        starter_code=starter_code,
        time_limit_ms=time_limit_ms,
        memory_limit_mb=memory_limit_mb,
    )
    db.add(problem)

    try:
        db.commit()
        db.refresh(problem)
    except IntegrityError as exc:
        db.rollback()
        if _is_problem_slug_conflict(exc):
            raise ValueError("Problem slug already exists") from exc
        raise
    except Exception:
        db.rollback()
        raise

    return problem


def get_problem(db: Session, problem_id: int) -> Problem:
    problem = db.scalar(select(Problem).where(Problem.id == problem_id))
    if problem is None:
        raise ValueError("Problem not found")
    return problem


def get_problem_detail(
    db: Session,
    problem_id: int,
) -> tuple[Problem, list[TestCase]]:
    problem = get_problem(db, problem_id)
    test_cases = list(
        db.scalars(
            select(TestCase)
            .where(
                TestCase.problem_id == problem_id,
                TestCase.run_enabled.is_(True),
            )
            .order_by(TestCase.display_order.asc(), TestCase.id.asc())
        ).all()
    )
    return problem, test_cases


def list_problems(
    db: Session,
    *,
    topic_id: int | None = None,
    difficulty: Difficulty | None = None,
    tag: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> ProblemListResult:
    if page <= 0:
        raise ValueError("Page must be positive")
    if page_size <= 0:
        raise ValueError("Page size must be positive")

    filters = []
    if topic_id is not None:
        filters.append(Problem.topic_id == topic_id)
    if difficulty is not None:
        filters.append(Problem.difficulty == difficulty)
    if tag is not None:
        filters.append(Problem.tags.contains([tag]))
    if search is not None:
        filters.append(Problem.title.ilike(f"%{search}%"))

    filtered_query = select(Problem).where(*filters)
    total = db.scalar(
        select(func.count()).select_from(filtered_query.subquery())
    )
    items = list(
        db.scalars(
            filtered_query
            .order_by(Problem.id.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
    )
    return ProblemListResult(items=items, total=total or 0)


def update_problem(
    db: Session,
    problem_id: int,
    *,
    topic_id: int | None = None,
    title: str | None = None,
    slug: str | None = None,
    statement: str | None = None,
    difficulty: Difficulty | None = None,
    tags: list[str] | None = None,
    starter_code: dict[str, str] | None = None,
    time_limit_ms: int | None = None,
    memory_limit_mb: int | None = None,
) -> Problem:
    problem = get_problem(db, problem_id)

    final_time_limit = (
        problem.time_limit_ms if time_limit_ms is None else time_limit_ms
    )
    final_memory_limit = (
        problem.memory_limit_mb
        if memory_limit_mb is None
        else memory_limit_mb
    )
    _validate_limits(final_time_limit, final_memory_limit)

    if topic_id is not None:
        _require_topic(db, topic_id)
        problem.topic_id = topic_id

    if slug is not None:
        duplicate = db.scalar(
            select(Problem).where(
                Problem.slug == slug,
                Problem.id != problem_id,
            )
        )
        if duplicate is not None:
            raise ValueError("Problem slug already exists")
        problem.slug = slug

    if title is not None:
        problem.title = title
    if statement is not None:
        problem.statement = statement
    if difficulty is not None:
        problem.difficulty = difficulty
    if tags is not None:
        problem.tags = tags
    if starter_code is not None:
        problem.starter_code = starter_code
    if time_limit_ms is not None:
        problem.time_limit_ms = time_limit_ms
    if memory_limit_mb is not None:
        problem.memory_limit_mb = memory_limit_mb
    problem.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(problem)
    except IntegrityError as exc:
        db.rollback()
        if _is_problem_slug_conflict(exc):
            raise ValueError("Problem slug already exists") from exc
        raise
    except Exception:
        db.rollback()
        raise

    return problem


def delete_problem(db: Session, problem_id: int) -> None:
    problem = get_problem(db, problem_id)
    db.delete(problem)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
