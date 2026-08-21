from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.app.core.execution import MAX_SOURCE_CODE_BYTES
from backend.app.models.submission import Submission, SubmissionStatus
from backend.app.services.problem import get_problem


SUPPORTED_SUBMISSION_LANGUAGES = frozenset({"python", "cpp"})


def _validate_language(language: str) -> None:
    if language not in SUPPORTED_SUBMISSION_LANGUAGES:
        supported = ", ".join(sorted(SUPPORTED_SUBMISSION_LANGUAGES))
        raise ValueError(f"Unsupported language: {language}. Supported languages: {supported}")


def _validate_source_code(source_code: str) -> None:
    if not source_code:
        raise ValueError("Source code must not be empty")

    source_bytes = len(source_code.encode("utf-8"))
    if source_bytes > MAX_SOURCE_CODE_BYTES:
        raise ValueError(
            f"source_code exceeds {MAX_SOURCE_CODE_BYTES} bytes"
        )


def create_submission(
    db: Session,
    *,
    user_id: int,
    problem_id: int,
    language: str,
    source_code: str,
) -> Submission:
    """Create a queued submission without executing or enqueueing it."""
    get_problem(db, problem_id)
    _validate_language(language)
    _validate_source_code(source_code)

    now = datetime.now(timezone.utc)
    submission = Submission(
        user_id=user_id,
        problem_id=problem_id,
        language=language,
        source_code=source_code,
        status=SubmissionStatus.QUEUED,
        verdict=None,
        created_at=now,
        updated_at=now,
        completed_at=None,
    )
    db.add(submission)

    try:
        db.commit()
        db.refresh(submission)
    except Exception:
        db.rollback()
        raise

    return submission
