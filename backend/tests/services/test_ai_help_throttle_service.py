from concurrent.futures import ThreadPoolExecutor
from threading import Lock

import pytest
from redis.exceptions import RedisError

from backend.app.services.ai_help_throttle import (
    AI_HELP_RATE_KEY_PREFIX,
    AI_HELP_RATE_LIMIT,
    AI_HELP_RATE_WINDOW_SECONDS,
    AiHelpThrottle,
    AiHelpThrottleUnavailable,
)


class AtomicFakeRedis:
    def __init__(self, error=None):
        self.error = error
        self._lock = Lock()
        self.counts = {}
        self.keys = []

    def eval(self, script, number_of_keys, key, window_seconds):
        if self.error is not None:
            raise self.error
        with self._lock:
            self.keys.append(key)
            count = self.counts.get(key, 0) + 1
            self.counts[key] = count
            return [count, window_seconds]


def test_request_is_allowed_within_limit():
    redis = AtomicFakeRedis()
    throttle = AiHelpThrottle(redis)

    decision = throttle.check(42)

    assert decision.allowed is True
    assert decision.retry_after_seconds == AI_HELP_RATE_WINDOW_SECONDS
    assert redis.keys == [f"{AI_HELP_RATE_KEY_PREFIX}42"]


def test_request_is_rejected_after_limit():
    throttle = AiHelpThrottle(AtomicFakeRedis())

    decisions = [throttle.check(42) for _ in range(AI_HELP_RATE_LIMIT + 1)]

    assert all(decision.allowed for decision in decisions[:AI_HELP_RATE_LIMIT])
    assert decisions[-1].allowed is False
    assert decisions[-1].retry_after_seconds == AI_HELP_RATE_WINDOW_SECONDS


def test_users_have_separate_limits():
    redis = AtomicFakeRedis()
    throttle = AiHelpThrottle(redis)

    for _ in range(AI_HELP_RATE_LIMIT):
        assert throttle.check(1).allowed
    assert throttle.check(1).allowed is False
    assert throttle.check(2).allowed is True


def test_concurrent_requests_cannot_bypass_limit():
    throttle = AiHelpThrottle(AtomicFakeRedis())

    with ThreadPoolExecutor(max_workers=20) as executor:
        decisions = list(executor.map(lambda _: throttle.check(7), range(20)))

    assert sum(decision.allowed for decision in decisions) == AI_HELP_RATE_LIMIT
    assert sum(not decision.allowed for decision in decisions) == 15


def test_redis_failure_is_wrapped_without_details():
    throttle = AiHelpThrottle(
        AtomicFakeRedis(error=RedisError("redis://secret-internal-host"))
    )

    with pytest.raises(AiHelpThrottleUnavailable) as error:
        throttle.check(42)

    assert str(error.value) == ""
