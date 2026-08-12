from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import require_admin
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.test_case import (
    AdminTestCaseResponse,
    PublicTestCaseResponse,
    TestCaseCreate,
    TestCaseUpdate,
)
from backend.app.services.test_case import (
    create_test_case,
    delete_test_case,
    update_test_case,
)


router = APIRouter(
    prefix="/api/v1/problems/{problem_id}/test-cases",
    tags=["test-cases"],
)


def _test_case_error(exc: ValueError) -> HTTPException:
    detail = str(exc)
    if detail in {
        "Problem not found",
        "Test case not found",
        "Test case does not belong to problem",
    }:
        code = status.HTTP_404_NOT_FOUND
    else:
        code = status.HTTP_400_BAD_REQUEST
    return HTTPException(status_code=code, detail=detail)


@router.post(
    "",
    response_model=AdminTestCaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_test_case_route(
    problem_id: int,
    request: TestCaseCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    try:
        return create_test_case(
            db=db,
            problem_id=problem_id,
            input=request.input,
            expected_output=request.expected_output,
            run_enabled=request.run_enabled,
            submit_enabled=request.submit_enabled,
            is_sample=request.is_sample,
            display_order=request.display_order,
        )
    except ValueError as exc:
        raise _test_case_error(exc) from exc


@router.patch("/{test_case_id}", response_model=AdminTestCaseResponse)
def update_test_case_route(
    problem_id: int,
    test_case_id: int,
    request: TestCaseUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    try:
        return update_test_case(
            db=db,
            test_case_id=test_case_id,
            problem_id=problem_id,
            input=request.input,
            expected_output=request.expected_output,
            run_enabled=request.run_enabled,
            submit_enabled=request.submit_enabled,
            is_sample=request.is_sample,
            display_order=request.display_order,
        )
    except ValueError as exc:
        raise _test_case_error(exc) from exc


@router.delete(
    "/{test_case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_test_case_route(
    problem_id: int,
    test_case_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    try:
        delete_test_case(
            db=db,
            test_case_id=test_case_id,
            problem_id=problem_id,
        )
    except ValueError as exc:
        raise _test_case_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
