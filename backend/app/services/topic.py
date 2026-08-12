from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.topic import Topic


def _is_topic_slug_conflict(exc: IntegrityError) -> bool:
    constraint_name = getattr(
        getattr(exc.orig, "diag", None),
        "constraint_name",
        None,
    )
    return constraint_name in {"topics_slug_key", "ix_topics_slug"}


def create_topic(
    db: Session,
    name: str,
    slug: str,
    display_order: int,
) -> Topic:
    if db.scalar(select(Topic).where(Topic.slug == slug)) is not None:
        raise ValueError("Topic slug already exists")

    topic = Topic(
        name=name,
        slug=slug,
        display_order=display_order,
    )
    db.add(topic)

    try:
        db.commit()
        db.refresh(topic)
    except IntegrityError as exc:
        db.rollback()
        if _is_topic_slug_conflict(exc):
            raise ValueError("Topic slug already exists") from exc
        raise
    except Exception:
        db.rollback()
        raise

    return topic


def get_topic(db: Session, topic_id: int) -> Topic:
    topic = db.scalar(select(Topic).where(Topic.id == topic_id))
    if topic is None:
        raise ValueError("Topic not found")
    return topic


def list_topics(db: Session) -> list[Topic]:
    return list(
        db.scalars(
            select(Topic).order_by(
                Topic.display_order.asc(),
                Topic.id.asc(),
            )
        ).all()
    )


def update_topic(
    db: Session,
    topic_id: int,
    *,
    name: str | None = None,
    slug: str | None = None,
    display_order: int | None = None,
) -> Topic:
    topic = get_topic(db, topic_id)

    if slug is not None:
        duplicate = db.scalar(
            select(Topic).where(
                Topic.slug == slug,
                Topic.id != topic_id,
            )
        )
        if duplicate is not None:
            raise ValueError("Topic slug already exists")
        topic.slug = slug

    if name is not None:
        topic.name = name
    if display_order is not None:
        topic.display_order = display_order
    topic.updated_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(topic)
    except IntegrityError as exc:
        db.rollback()
        if _is_topic_slug_conflict(exc):
            raise ValueError("Topic slug already exists") from exc
        raise
    except Exception:
        db.rollback()
        raise

    return topic


def delete_topic(db: Session, topic_id: int) -> None:
    topic = get_topic(db, topic_id)
    db.delete(topic)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
