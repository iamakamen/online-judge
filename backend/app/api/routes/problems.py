import math

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user, require_admin
from backend.app.db.session import get_db
from backend.app.models.problem import Difficulty
from backend.app.models.user import User
from backend.app.schemas.problem import (
    ProblemCreate,
    ProblemDetailResponse,
    ProblemListPage,
    ProblemListResponse,
    ProblemUpdate,
)
from backend.app.schemas.accepted_solution import AcceptedSolutionsResponse
from backend.app.services.problem import (
    ProblemListResult,
    create_problem,
    delete_problem,
    get_problem_detail,
    get_problem_by_slug,
    list_problems,
    update_problem,
)
from backend.app.services.accepted_solution import (
    get_accepted_solutions,
    require_problem,
)


router = APIRouter(prefix="/api/v1/problems", tags=["problems"])


def _problem_error(exc: ValueError) -> HTTPException:
    detail = str(exc)
    if detail in {"Problem not found", "Topic not found"}:
        code = status.HTTP_404_NOT_FOUND
    elif detail == "Problem slug already exists":
        code = status.HTTP_409_CONFLICT
    else:
        code = status.HTTP_400_BAD_REQUEST
    return HTTPException(status_code=code, detail=detail)


def _problem_detail_response(
    problem,
    test_cases,
) -> ProblemDetailResponse:
    return ProblemDetailResponse(
        id=problem.id,
        topic_id=problem.topic_id,
        created_by_user_id=problem.created_by_user_id,
        title=problem.title,
        slug=problem.slug,
        statement=problem.statement,
        constraints=problem.constraints,
        difficulty=problem.difficulty,
        tags=problem.tags,
        starter_code=problem.starter_code,
        time_limit_ms=problem.time_limit_ms,
        memory_limit_mb=problem.memory_limit_mb,
        created_at=problem.created_at,
        updated_at=problem.updated_at,
        test_cases=test_cases,
    )


def _created_problem_response(db: Session, problem_id: int):
    problem, test_cases = get_problem_detail(db, problem_id)
    return _problem_detail_response(problem, test_cases)


@router.get("", response_model=ProblemListPage)
def list_problem_route(
    topic_id: int | None = None,
    difficulty: Difficulty | None = None,
    tag: str | None = None,
    tags: list[str] | None = Query(default=None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        result: ProblemListResult = list_problems(
            db=db,
            user_id=current_user.id,
            topic_id=topic_id,
            difficulty=difficulty,
            tag=tag,
            tags=tags,
            page=page,
            page_size=page_size,
        )
    except ValueError as exc:
        raise _problem_error(exc) from exc

    return ProblemListPage(
        items=[
            ProblemListResponse(
                id=item.problem.id,
                topic_id=item.problem.topic_id,
                created_by_user_id=item.problem.created_by_user_id,
                title=item.problem.title,
                slug=item.problem.slug,
                difficulty=item.problem.difficulty,
                tags=item.problem.tags,
                solved=item.solved,
            )
            for item in result.items
        ],
        total=result.total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(result.total / page_size),
    )


@router.get("/by-slug/{slug}", response_model=ProblemDetailResponse)
def get_problem_by_slug_route(
    slug: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        problem = get_problem_by_slug(db, slug)
        _, test_cases = get_problem_detail(db, problem.id)
    except ValueError as exc:
        raise _problem_error(exc) from exc
    return _problem_detail_response(problem, test_cases)


@router.get(
    "/{problem_id}/accepted-solutions",
    response_model=AcceptedSolutionsResponse,
)
def get_accepted_solutions_route(
    problem_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        require_problem(db, problem_id)
    except ValueError as exc:
        raise _problem_error(exc) from exc
    return AcceptedSolutionsResponse(
        solutions=get_accepted_solutions(
            db, user_id=current_user.id, problem_id=problem_id
        )
    )


@router.get("/{problem_id}", response_model=ProblemDetailResponse)
def get_problem_route(
    problem_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        problem, test_cases = get_problem_detail(db, problem_id)
    except ValueError as exc:
        raise _problem_error(exc) from exc
    return _problem_detail_response(problem, test_cases)


@router.post(
    "",
    response_model=ProblemDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_problem_route(
    request: ProblemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    try:
        problem = create_problem(
            db=db,
            topic_id=request.topic_id,
            title=request.title,
            slug=request.slug,
            statement=request.statement,
            constraints=request.constraints,
            difficulty=request.difficulty,
            tags=request.tags,
            starter_code=request.starter_code,
            time_limit_ms=request.time_limit_ms,
            memory_limit_mb=request.memory_limit_mb,
            created_by_user_id=current_user.id,
        )
        return _created_problem_response(db, problem.id)
    except ValueError as exc:
        raise _problem_error(exc) from exc


@router.patch("/{problem_id}", response_model=ProblemDetailResponse)
def update_problem_route(
    problem_id: int,
    request: ProblemUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    try:
        problem = update_problem(
            db=db,
            problem_id=problem_id,
            topic_id=request.topic_id,
            title=request.title,
            slug=request.slug,
            statement=request.statement,
            constraints=request.constraints,
            difficulty=request.difficulty,
            tags=request.tags,
            starter_code=request.starter_code,
            time_limit_ms=request.time_limit_ms,
            memory_limit_mb=request.memory_limit_mb,
        )
        return _created_problem_response(db, problem.id)
    except ValueError as exc:
        raise _problem_error(exc) from exc


@router.delete("/{problem_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_problem_route(
    problem_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    try:
        delete_problem(db, problem_id)
    except ValueError as exc:
        raise _problem_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
