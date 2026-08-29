"""Server-side AI Help context boundary.

This module deliberately does not call an AI provider. It resolves only the
problem fields needed for a targeted explanation and never loads test cases,
submissions, environment variables, or provider credentials.
"""

import json
from typing import Any

from sqlalchemy.orm import Session

from backend.app.core.ai import MAX_AI_CONTEXT_BYTES
from backend.app.schemas.ai import AiHelpRequest
from backend.app.services.problem import get_problem


AI_CONTEXT_FIELDS = frozenset(
    {
        "problem_title",
        "problem_statement",
        "problem_constraints",
        "language",
        "operation",
        "failure_status",
        "source_code",
        "diagnostic",
        "stdout",
        "stderr",
    }
)


def build_ai_help_context(
    db: Session,
    request: AiHelpRequest,
) -> dict[str, Any]:
    """Resolve and return the explicit allowlist sent to a future provider."""
    problem = get_problem(db, request.problem_id)
    context = {
        "problem_title": problem.title,
        "problem_statement": problem.statement,
        "problem_constraints": problem.constraints,
        "language": request.language.value,
        "operation": request.operation.value,
        "failure_status": request.failure_status.value,
        "source_code": request.source_code,
        "diagnostic": request.diagnostic,
        "stdout": request.stdout,
        "stderr": request.stderr,
    }

    if set(context) != AI_CONTEXT_FIELDS:
        raise RuntimeError("AI Help context allowlist changed unexpectedly")

    context_bytes = len(
        json.dumps(context, ensure_ascii=False, separators=(",", ":")).encode(
            "utf-8"
        )
    )
    if context_bytes > MAX_AI_CONTEXT_BYTES:
        raise ValueError(
            f"AI Help context exceeds {MAX_AI_CONTEXT_BYTES} bytes"
        )

    return context
