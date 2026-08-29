from fastapi import APIRouter, Depends, HTTPException, status
from redis import Redis
from sqlalchemy.orm import Session

from backend.app.api.dependencies import get_current_user, get_redis
from backend.app.core.bedrock import (
    BedrockConfig,
    BedrockNotConfiguredError,
)
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.ai import AiHelpRequest, AiHelpResponse
from backend.app.services.bedrock_ai_help import (
    BedrockAiHelpProvider,
    BedrockMalformedResponse,
    BedrockProviderError,
    BedrockProviderTimeout,
)
from backend.app.services.ai_help import build_ai_help_context
from backend.app.services.ai_help_throttle import (
    AiHelpThrottle,
    AiHelpThrottleUnavailable,
)


router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


def get_bedrock_provider() -> BedrockAiHelpProvider:
    return BedrockAiHelpProvider(BedrockConfig.from_environment())


def get_ai_help_redis(redis: Redis = Depends(get_redis)) -> Redis:
    return redis


@router.post("/help", response_model=AiHelpResponse)
def ai_help_route(
    request: AiHelpRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_ai_help_redis),
):
    try:
        context = build_ai_help_context(db, request)
    except ValueError as exc:
        if str(exc) == "Problem not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    try:
        provider = get_bedrock_provider()
    except BedrockNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Help provider is not configured",
        ) from exc

    try:
        decision = AiHelpThrottle(redis).check(current_user.id)
    except AiHelpThrottleUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Help service unavailable",
        ) from exc

    if not decision.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI Help rate limit exceeded",
            headers={"Retry-After": str(decision.retry_after_seconds)},
        )

    try:
        return provider.generate(context)
    except BedrockProviderTimeout as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI Help provider timed out",
        ) from exc
    except (BedrockMalformedResponse, BedrockProviderError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI Help provider unavailable",
        ) from exc
