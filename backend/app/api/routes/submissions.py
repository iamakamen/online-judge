from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import (
    get_current_user,
    get_submission_dispatcher,
)
from backend.app.db.session import get_db
from backend.app.models.submission import Submission
from backend.app.models.user import User
from backend.app.schemas.submission import (
    SubmissionCreate,
    SubmissionDetailResponse,
    SubmissionResponse,
)
from backend.app.services.submission import (
    create_submission,
    get_submission_for_user,
)
from backend.app.services.submission_dispatch import SubmissionDispatcher


router = APIRouter(
    prefix="/api/v1/submissions",
    tags=["submissions"],
)


@router.post(
    "",
    response_model=SubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_submission_route(
    request: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    dispatcher: SubmissionDispatcher = Depends(get_submission_dispatcher),
) -> Submission:
    try:
        result = create_submission(
            db,
            user_id=current_user.id,
            problem_id=request.problem_id,
            language=request.language,
            source_code=request.source_code,
        )
    except ValueError as exc:
        detail = str(exc)

        if detail == "Problem not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=detail,
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        ) from exc

    dispatcher.dispatch(result.submission.id)
    return result.submission


@router.get(
    "/{submission_id}",
    response_model=SubmissionDetailResponse,
)
def get_submission_route(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Submission:
    try:
        return get_submission_for_user(
            db,
            submission_id=submission_id,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
