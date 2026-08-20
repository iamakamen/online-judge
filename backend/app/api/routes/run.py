from fastapi import APIRouter, Depends, HTTPException, status
from redis import Redis
from redis.exceptions import RedisError

from backend.app.api.dependencies import get_current_user
from backend.app.core.execution import RUN_RATE_LIMIT_PER_MINUTE
from backend.app.models.user import User
from backend.app.schemas.run import RunRequest, RunResponse
from backend.app.services.execution.redis_transport import RunTransport


router = APIRouter(prefix="/api/v1/run", tags=["run"])


def get_run_transport() -> RunTransport:
    return RunTransport(Redis.from_url("redis://localhost:6379/0"))


def _rate_limit_key(user_id: int) -> str:
    return f"run:rate:{user_id}"


@router.post("", response_model=RunResponse)
def run_route(
    request: RunRequest,
    current_user: User = Depends(get_current_user),
    transport: RunTransport = Depends(get_run_transport),
):
    try:
        rate_limit_key = _rate_limit_key(current_user.id)
        count = transport._redis.incr(rate_limit_key)
        if count == 1:
            transport._redis.expire(rate_limit_key, 60)
        if count > RUN_RATE_LIMIT_PER_MINUTE:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Run rate limit exceeded",
            )

        request_id = transport.enqueue(current_user.id, request)
        result = transport.wait_for_result(request_id)
    except HTTPException:
        raise
    except RedisError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Run infrastructure unavailable",
        ) from exc

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Run execution timed out",
        )

    return result
