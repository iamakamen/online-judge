from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from backend.app.models.submission import SubmissionStatus
from backend.app.services.execution.submission_transport import (
    SubmissionDelivery,
    SubmissionJob,
)
from backend.app.services.execution.submission_worker import SubmissionWorker


class FakeDb:
    def __init__(self):
        self.closed = False

    def close(self):
        self.closed = True


class FakeTransport:
    def __init__(self):
        self.acknowledged = []
        self.events = []

    def consume(self, consumer_name, *, count=1, timeout_seconds=5):
        return []

    def acknowledge(self, stream_id):
        self.events.append("ack")
        self.acknowledged.append(stream_id)
        return 1


class StopWorker(Exception):
    pass


class FakeReconciler:
    def __init__(self, events, error=None):
        self.events = events
        self.error = error
        self.calls = 0

    def reconcile_once(self):
        self.calls += 1
        self.events.append("reconcile")
        if self.error is not None:
            raise self.error


def run_until_stopped(worker, events, *, consume_calls=1):
    worker.recover_pending = lambda: events.append("recover")
    calls = 0

    def consume(*args, **kwargs):
        nonlocal calls
        calls += 1
        events.append("consume")
        if calls >= consume_calls:
            raise StopWorker()
        return []

    worker._transport.consume = consume

    with pytest.raises(StopWorker):
        worker.run_forever()


@dataclass
class FakeJudge:
    result: object | None = None
    error: Exception | None = None
    events: list[str] | None = None

    def execute_claimed(self, db, submission):
        if self.events is not None:
            self.events.append("judge")
        if self.error is not None:
            raise self.error
        return self.result


def delivery(submission_id, job_id="job-1", stream_id="1-0"):
    return SubmissionDelivery(
        stream_id=stream_id,
        job=SubmissionJob(
            job_id=job_id,
            submission_id=submission_id,
            enqueued_at=SimpleNamespace(),
        ),
    )


def worker(transport, db, judge):
    return SubmissionWorker(
        transport,
        consumer_name="worker-1",
        judge_service=judge,
        session_factory=lambda: db,
    )


def test_successful_delivery_claims_judges_then_acknowledges(monkeypatch):
    transport = FakeTransport()
    transport.events = []
    db = FakeDb()
    events = transport.events
    judge = FakeJudge(
        result=SimpleNamespace(status=SubmissionStatus.COMPLETED),
        events=events,
    )
    claimed = SimpleNamespace(
        id=7,
        status=SubmissionStatus.RUNNING,
    )
    monkeypatch.setattr(
        "backend.app.services.execution.submission_worker.claim_submission",
        lambda db, submission_id: claimed,
    )

    worker(transport, db, judge).process_delivery(delivery(7))

    assert transport.acknowledged == ["1-0"]
    assert events == ["judge", "ack"]
    assert db.closed is True


def test_non_queued_submission_is_acknowledged_without_judging(monkeypatch):
    transport = FakeTransport()
    db = FakeDb()
    judge = FakeJudge(
        result=SimpleNamespace(status=SubmissionStatus.COMPLETED)
    )

    def reject_claim(db, submission_id):
        raise ValueError("Submission is not queued")

    monkeypatch.setattr(
        "backend.app.services.execution.submission_worker.claim_submission",
        reject_claim,
    )

    worker(transport, db, judge).process_delivery(delivery(7))

    assert transport.acknowledged == ["1-0"]
    assert judge.events is None


def test_missing_submission_is_acknowledged_without_judging(monkeypatch):
    transport = FakeTransport()
    db = FakeDb()
    judge = FakeJudge(
        result=SimpleNamespace(status=SubmissionStatus.COMPLETED)
    )

    def reject_claim(db, submission_id):
        raise ValueError("Submission not found")

    monkeypatch.setattr(
        "backend.app.services.execution.submission_worker.claim_submission",
        reject_claim,
    )

    worker(transport, db, judge).process_delivery(delivery(7))

    assert transport.acknowledged == ["1-0"]
    assert judge.events is None


def test_judge_failure_does_not_acknowledge(monkeypatch):
    transport = FakeTransport()
    db = FakeDb()
    judge = FakeJudge(error=RuntimeError("judge failed"))
    claimed = SimpleNamespace(
        id=7,
        status=SubmissionStatus.RUNNING,
    )
    monkeypatch.setattr(
        "backend.app.services.execution.submission_worker.claim_submission",
        lambda db, submission_id: claimed,
    )

    worker(transport, db, judge).process_delivery(delivery(7))

    assert transport.acknowledged == []
    assert db.closed is True


def test_multiple_deliveries_are_processed_independently(monkeypatch):
    transport = FakeTransport()
    dbs = [FakeDb(), FakeDb()]
    judged_ids = []
    claimed_by_id = {
        7: SimpleNamespace(id=7, status=SubmissionStatus.RUNNING),
        8: SimpleNamespace(id=8, status=SubmissionStatus.RUNNING),
    }

    def claim(db, submission_id):
        return claimed_by_id[submission_id]

    class Judge:
        def execute_claimed(self, db, submission):
            judged_ids.append(submission.id)
            return SimpleNamespace(status=SubmissionStatus.COMPLETED)

    monkeypatch.setattr(
        "backend.app.services.execution.submission_worker.claim_submission",
        claim,
    )

    worker_instance = SubmissionWorker(
        transport,
        consumer_name="worker-1",
        judge_service=Judge(),
        session_factory=iter(dbs).__next__,
    )
    worker_instance.process_delivery(delivery(7, stream_id="1-0"))
    worker_instance.process_delivery(delivery(8, stream_id="2-0"))

    assert judged_ids == [7, 8]
    assert transport.acknowledged == ["1-0", "2-0"]
    assert all(db.closed for db in dbs)


def test_reconciliation_runs_at_startup_before_recovery():
    events = []
    reconciler = FakeReconciler(events)
    worker_instance = SubmissionWorker(
        FakeTransport(),
        consumer_name="worker-1",
        reconciler=reconciler,
    )

    run_until_stopped(worker_instance, events)

    assert reconciler.calls == 1
    assert events == ["reconcile", "recover", "consume"]


def test_reconciliation_runs_periodically_from_monotonic_deadline(monkeypatch):
    events = []
    reconciler = FakeReconciler(events)
    worker_instance = SubmissionWorker(
        FakeTransport(),
        consumer_name="worker-1",
        reconciler=reconciler,
        reconciliation_interval_seconds=5,
    )
    monotonic_values = iter([0.0, 0.0, 0.0, 100.0, 100.0, 100.1])
    monkeypatch.setattr(
        "backend.app.services.execution.submission_worker.time.monotonic",
        lambda: next(monotonic_values),
    )

    run_until_stopped(worker_instance, events, consume_calls=3)

    assert reconciler.calls == 2
    assert events == [
        "reconcile",
        "recover",
        "consume",
        "reconcile",
        "recover",
        "consume",
        "recover",
        "consume",
    ]


def test_reconciliation_failure_is_logged_and_worker_continues(caplog):
    events = []
    reconciler = FakeReconciler(
        events,
        error=RuntimeError("reconciliation unavailable"),
    )
    worker_instance = SubmissionWorker(
        FakeTransport(),
        consumer_name="worker-1",
        reconciler=reconciler,
    )

    with caplog.at_level("ERROR"):
        run_until_stopped(worker_instance, events)

    assert events == ["reconcile", "recover", "consume"]
    assert "reconciliation unavailable" in caplog.text


def test_worker_without_reconciler_preserves_existing_loop(monkeypatch):
    events = []
    worker_instance = SubmissionWorker(
        FakeTransport(),
        consumer_name="worker-1",
    )
    monkeypatch.setattr(
        "backend.app.services.execution.submission_worker.time.monotonic",
        lambda: pytest.fail("monotonic must not be used without reconciler"),
    )

    run_until_stopped(worker_instance, events)

    assert events == ["recover", "consume"]


@pytest.mark.parametrize("interval", [0, -1, -0.1])
def test_worker_rejects_invalid_reconciliation_interval(interval):
    with pytest.raises(
        ValueError,
        match="reconciliation_interval_seconds",
    ):
        SubmissionWorker(
            FakeTransport(),
            consumer_name="worker-1",
            reconciliation_interval_seconds=interval,
        )
