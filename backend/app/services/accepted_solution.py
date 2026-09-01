from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from backend.app.models.accepted_solution import AcceptedSolution
from backend.app.models.problem import Problem


def upsert_accepted_solution(
    db: Session,
    *,
    user_id: int,
    problem_id: int,
    language: str,
    source_code: str,
    now: datetime,
) -> None:
    statement = pg_insert(AcceptedSolution).values(
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        source_code=source_code,
        created_at=now,
        updated_at=now,
    )
    db.execute(
        statement.on_conflict_do_update(
            constraint="uq_accepted_solutions_user_problem_language",
            set_={"source_code": source_code, "updated_at": now},
        )
    )


def get_accepted_solutions(
    db: Session,
    *,
    user_id: int,
    problem_id: int,
) -> dict[str, str | None]:
    rows = db.execute(
        select(AcceptedSolution.language, AcceptedSolution.source_code).where(
            AcceptedSolution.user_id == user_id,
            AcceptedSolution.problem_id == problem_id,
        )
    ).all()
    solutions = {"python": None, "cpp": None}
    for language, source_code in rows:
        solutions[language] = source_code
    return solutions


def require_problem(db: Session, problem_id: int) -> None:
    if db.scalar(select(Problem.id).where(Problem.id == problem_id)) is None:
        raise ValueError("Problem not found")
