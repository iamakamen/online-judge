"""Redis-backed, user-scoped throttling for AI Help requests."""

from __future__ import annotations

from dataclasses import dataclass

from redis import Redis
from redis.exceptions import RedisError


AI_HELP_RATE_LIMIT = 5
AI_HELP_RATE_WINDOW_SECONDS = 10 * 60
AI_HELP_RATE_KEY_PREFIX = "ai:help:rate:"

_AI_HELP_RATE_SCRIPT = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
local ttl = redis.call('TTL', KEYS[1])
return {count, ttl}
"""


class AiHelpThrottleUnavailable(Exception):
    """Raised when Redis cannot evaluate the AI Help rate-limit script."""


@dataclass(frozen=True)
class AiHelpThrottleDecision:
    allowed: bool
    retry_after_seconds: int


class AiHelpThrottle:
    def __init__(
        self,
        redis: Redis,
        *,
        limit: int = AI_HELP_RATE_LIMIT,
        window_seconds: int = AI_HELP_RATE_WINDOW_SECONDS,
    ) -> None:
        self._redis = redis
        self._limit = limit
        self._window_seconds = window_seconds

    def check(self, user_id: int) -> AiHelpThrottleDecision:
        key = f"{AI_HELP_RATE_KEY_PREFIX}{user_id}"
        try:
            result = self._redis.eval(
                _AI_HELP_RATE_SCRIPT,
                1,
                key,
                self._window_seconds,
            )
            count = int(result[0])
            ttl = max(int(result[1]), 1)
        except (RedisError, IndexError, TypeError, ValueError) as exc:
            raise AiHelpThrottleUnavailable from exc

        return AiHelpThrottleDecision(
            allowed=count <= self._limit,
            retry_after_seconds=ttl,
        )
