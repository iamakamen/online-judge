from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user, require_admin
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.topic import TopicCreate, TopicResponse, TopicUpdate
from backend.app.services.topic import (
    create_topic,
    delete_topic,
    get_topic,
    list_topics,
    update_topic,
)


router = APIRouter(prefix="/api/v1/topics", tags=["topics"])


def _topic_error(exc: ValueError) -> HTTPException:
    detail = str(exc)
    if detail == "Topic not found":
        code = status.HTTP_404_NOT_FOUND
    elif detail == "Topic slug already exists":
        code = status.HTTP_409_CONFLICT
    else:
        code = status.HTTP_400_BAD_REQUEST
    return HTTPException(status_code=code, detail=detail)


@router.get("", response_model=list[TopicResponse])
def list_topic_route(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return list_topics(db)


@router.get("/{topic_id}", response_model=TopicResponse)
def get_topic_route(
    topic_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        return get_topic(db, topic_id)
    except ValueError as exc:
        raise _topic_error(exc) from exc


@router.post("", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
def create_topic_route(
    request: TopicCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    try:
        return create_topic(
            db=db,
            name=request.name,
            slug=request.slug,
            display_order=request.display_order,
        )
    except ValueError as exc:
        raise _topic_error(exc) from exc


@router.patch("/{topic_id}", response_model=TopicResponse)
def update_topic_route(
    topic_id: int,
    request: TopicUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    try:
        return update_topic(
            db=db,
            topic_id=topic_id,
            name=request.name,
            slug=request.slug,
            display_order=request.display_order,
        )
    except ValueError as exc:
        raise _topic_error(exc) from exc


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic_route(
    topic_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    try:
        delete_topic(db, topic_id)
    except ValueError as exc:
        raise _topic_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
