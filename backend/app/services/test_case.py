from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.problem import Problem
from backend.app.models.test_case import TestCase


def _require_problem(db: Session, problem_id: int) -> Problem:
    problem = db.scalar(select(Problem).where(Problem.id == problem_id))
    if problem is None:
        raise ValueError("Problem not found")
    return problem


def _get_owned_test_case(
    db: Session,
    test_case_id: int,
    problem_id: int | None = None,
) -> TestCase:
    filters = [TestCase.id == test_case_id]
    if problem_id is not None:
        filters.append(TestCase.problem_id == problem_id)

    test_case = db.scalar(select(TestCase).where(*filters))
    if test_case is None:
        if problem_id is not None:
            raise ValueError("Test case does not belong to problem")
        raise ValueError("Test case not found")
    return test_case


def create_test_case(
    db: Session,
    problem_id: int,
    input: str,
    expected_output: str,
    run_enabled: bool,
    submit_enabled: bool,
    is_sample: bool,
    display_order: int,
) -> TestCase:
    _require_problem(db, problem_id)
    if not run_enabled and not submit_enabled:
        raise ValueError("Test case must be enabled for run or submit")

    test_case = TestCase(
        problem_id=problem_id,
        input=input,
        expected_output=expected_output,
        run_enabled=run_enabled,
        submit_enabled=submit_enabled,
        is_sample=is_sample,
        display_order=display_order,
    )
    db.add(test_case)

    try:
        db.commit()
        db.refresh(test_case)
    except Exception:
        db.rollback()
        raise

    return test_case


def get_test_case(
    db: Session,
    test_case_id: int,
    problem_id: int | None = None,
) -> TestCase:
    return _get_owned_test_case(db, test_case_id, problem_id)


def list_test_cases_for_problem(
    db: Session,
    problem_id: int,
    *,
    run_visible_only: bool = True,
) -> list[TestCase]:
    _require_problem(db, problem_id)

    filters = [TestCase.problem_id == problem_id]
    if run_visible_only:
        filters.append(TestCase.run_enabled.is_(True))

    return list(
        db.scalars(
            select(TestCase)
            .where(*filters)
            .order_by(TestCase.display_order.asc(), TestCase.id.asc())
        ).all()
    )


def list_submit_test_cases_for_problem(
    db: Session,
    problem_id: int,
) -> list[TestCase]:
    """Return the test cases that are enabled for judge submission."""
    _require_problem(db, problem_id)

    return list(
        db.scalars(
            select(TestCase)
            .where(
                TestCase.problem_id == problem_id,
                TestCase.submit_enabled.is_(True),
            )
            .order_by(TestCase.display_order.asc(), TestCase.id.asc())
        ).all()
    )


def update_test_case(
    db: Session,
    test_case_id: int,
    *,
    problem_id: int | None = None,
    input: str | None = None,
    expected_output: str | None = None,
    run_enabled: bool | None = None,
    submit_enabled: bool | None = None,
    is_sample: bool | None = None,
    display_order: int | None = None,
) -> TestCase:
    test_case = _get_owned_test_case(db, test_case_id, problem_id)

    final_run_enabled = (
        test_case.run_enabled if run_enabled is None else run_enabled
    )
    final_submit_enabled = (
        test_case.submit_enabled
        if submit_enabled is None
        else submit_enabled
    )
    if not final_run_enabled and not final_submit_enabled:
        raise ValueError("Test case must be enabled for run or submit")

    if input is not None:
        test_case.input = input
    if expected_output is not None:
        test_case.expected_output = expected_output
    if run_enabled is not None:
        test_case.run_enabled = run_enabled
    if submit_enabled is not None:
        test_case.submit_enabled = submit_enabled
    if is_sample is not None:
        test_case.is_sample = is_sample
    if display_order is not None:
        test_case.display_order = display_order

    try:
        db.commit()
        db.refresh(test_case)
    except Exception:
        db.rollback()
        raise

    return test_case


def delete_test_case(
    db: Session,
    test_case_id: int,
    problem_id: int | None = None,
) -> None:
    test_case = _get_owned_test_case(db, test_case_id, problem_id)
    db.delete(test_case)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
