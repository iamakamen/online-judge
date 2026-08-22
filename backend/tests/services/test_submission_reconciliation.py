import pytest
from sqlalchemy.dialects import postgresql

from backend.app.models import submission_result  # noqa: F401
from backend.app.services.submission_reconciliation import (
    DEFAULT_RECONCILIATION_BATCH_SIZE,
    SUBMISSION_RECONCILIATION_BATCH_SIZE,
    SubmissionReconciler,
)


class FakeSession:
    def __init__(self, ids=None, error=None):
        self.ids = list(ids or [])
        self.error = error
        self.statement = None
        self.rollback_calls = 0
        self.closed = False

    def scalars(self, statement):
        self.statement = statement
        if self.error is not None:
            raise self.error
        return self.ids

    def rollback(self):
        self.rollback_calls += 1

    def close(self):
        self.closed = True


class FakeDispatcher:
    def __init__(self, results=None, session=None):
        self.results = list(results or [])
        self.session = session
        self.dispatched = []

    def dispatch(self, submission_id):
        if self.session is not None:
            assert self.session.closed is True
        self.dispatched.append(submission_id)
        if self.results:
            return self.results.pop(0)
        return True


def reconciler(session, dispatcher, *, batch_size=50):
    return SubmissionReconciler(
        dispatcher,
        session_factory=lambda: session,
        batch_size=batch_size,
    )


def statement_sql(session):
    return str(
        session.statement.compile(
            dialect=postgresql.dialect(),
        )
    )


def test_reconciler_selects_only_queued_rows_in_created_id_order_and_batch():
    session = FakeSession(ids=[3, 7])
    dispatcher = FakeDispatcher()

    assert reconciler(session, dispatcher, batch_size=2).reconcile_once() == 2

    sql = statement_sql(session)
    assert 'submissions.status = %(status_1)s' in sql
    assert (
        'ORDER BY submissions.created_at ASC, submissions.id ASC'
        in sql
    )
    assert 'LIMIT %(param_1)s' in sql
    assert dispatcher.dispatched == [3, 7]


def test_default_batch_size_is_50():
    assert SUBMISSION_RECONCILIATION_BATCH_SIZE == 50
    assert DEFAULT_RECONCILIATION_BATCH_SIZE == 50


def test_session_is_closed_before_dispatch():
    session = FakeSession(ids=[11])
    dispatcher = FakeDispatcher(session=session)

    assert reconciler(session, dispatcher).reconcile_once() == 1
    assert session.rollback_calls >= 1
    assert session.closed is True


def test_successful_dispatch_processes_the_batch():
    session = FakeSession(ids=[1, 2, 3])
    dispatcher = FakeDispatcher()

    assert reconciler(session, dispatcher).reconcile_once() == 3
    assert dispatcher.dispatched == [1, 2, 3]


def test_dispatch_exhaustion_stops_the_current_batch():
    session = FakeSession(ids=[1, 2, 3])
    dispatcher = FakeDispatcher(results=[True, False, True])

    assert reconciler(session, dispatcher).reconcile_once() == 1
    assert dispatcher.dispatched == [1, 2]


def test_database_failure_causes_zero_dispatch_and_closes_session(caplog):
    session = FakeSession(error=RuntimeError("database unavailable"))
    dispatcher = FakeDispatcher()

    with caplog.at_level("ERROR"):
        assert reconciler(session, dispatcher).reconcile_once() == 0

    assert dispatcher.dispatched == []
    assert session.rollback_calls >= 1
    assert session.closed is True
    assert "database unavailable" in caplog.text


def test_reconciliation_does_not_modify_database_rows():
    session = FakeSession(ids=[5, 6])
    dispatcher = FakeDispatcher()

    reconciler(session, dispatcher).reconcile_once()

    assert session.ids == [5, 6]
    assert session.statement is not None


def test_duplicate_dispatch_is_harmless_at_reconciler_level():
    session = FakeSession(ids=[42])
    dispatcher = FakeDispatcher()
    instance = reconciler(session, dispatcher)

    assert instance.reconcile_once() == 1
    assert instance.reconcile_once() == 1
    assert dispatcher.dispatched == [42, 42]
