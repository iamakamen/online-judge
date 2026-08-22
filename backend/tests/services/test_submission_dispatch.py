from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import ResponseError

from backend.app.api.routes import submissions as submission_route
from backend.app.schemas.submission import SubmissionCreate
from backend.app.services.submission_dispatch import SubmissionDispatcher


class FakeTransport:
    def __init__(self, failures=0, error=None):
        self.failures = failures
        self.error = error or RedisConnectionError("redis unavailable")
        self.calls = []

    def enqueue(self, submission_id):
        self.calls.append(submission_id)
        if len(self.calls) <= self.failures:
            raise self.error


def test_dispatch_retries_transient_failures_with_bounded_backoff():
    transport = FakeTransport(failures=2)
    sleeps = []
    dispatcher = SubmissionDispatcher(
        transport,
        sleeper=sleeps.append,
    )

    assert dispatcher.dispatch(42) is True
    assert transport.calls == [42, 42, 42]
    assert sleeps == [0.05, 0.1]


def test_dispatch_exhaustion_has_exactly_three_attempts(caplog):
    transport = FakeTransport(failures=3)
    sleeps = []
    dispatcher = SubmissionDispatcher(
        transport,
        sleeper=sleeps.append,
    )

    with caplog.at_level("ERROR"):
        assert dispatcher.dispatch(42) is False

    assert transport.calls == [42, 42, 42]
    assert sleeps == [0.05, 0.1]
    assert "submission_id=42" in caplog.text
    assert "attempts=3" in caplog.text
    assert "redis unavailable" in caplog.text


def test_dispatch_does_not_retry_non_transient_redis_failures():
    transport = FakeTransport(failures=1, error=ResponseError("bad command"))
    dispatcher = SubmissionDispatcher(transport, sleeper=lambda _: pytest.fail())

    assert dispatcher.dispatch(42) is False
    assert transport.calls == [42]


def test_submission_route_dispatches_only_after_persistence_returns(monkeypatch):
    events = []

    def persist(*args, **kwargs):
        events.append("commit")
        return SimpleNamespace(
            submission=SimpleNamespace(id=42),
        )

    class Dispatcher:
        def dispatch(self, submission_id):
            events.append(("enqueue", submission_id))
            return True

    monkeypatch.setattr(submission_route, "create_submission", persist)
    result = submission_route.create_submission_route(
        SubmissionCreate(
            problem_id=1,
            language="python",
            source_code="print(1)",
        ),
        db=object(),
        current_user=SimpleNamespace(id=7),
        dispatcher=Dispatcher(),
    )

    assert result.id == 42
    assert events == ["commit", ("enqueue", 42)]


def test_submission_route_does_not_enqueue_when_persistence_fails(monkeypatch):
    def persist(*args, **kwargs):
        raise RuntimeError("database commit failed")

    class Dispatcher:
        def dispatch(self, submission_id):
            pytest.fail("enqueue must not be attempted")

    monkeypatch.setattr(submission_route, "create_submission", persist)

    with pytest.raises(RuntimeError, match="database commit failed"):
        submission_route.create_submission_route(
            SubmissionCreate(
                problem_id=1,
                language="python",
                source_code="print(1)",
            ),
            db=object(),
            current_user=SimpleNamespace(id=7),
            dispatcher=Dispatcher(),
        )


def test_submission_route_validation_failure_does_not_enqueue(monkeypatch):
    def persist(*args, **kwargs):
        raise ValueError("Unsupported language")

    class Dispatcher:
        def dispatch(self, submission_id):
            pytest.fail("enqueue must not be attempted")

    monkeypatch.setattr(submission_route, "create_submission", persist)

    with pytest.raises(HTTPException) as error:
        submission_route.create_submission_route(
            SubmissionCreate(
                problem_id=1,
                language="java",
                source_code="print(1)",
            ),
            db=object(),
            current_user=SimpleNamespace(id=7),
            dispatcher=Dispatcher(),
        )

    assert error.value.status_code == 400
    assert error.value.detail == "Unsupported language"
