from dataclasses import dataclass
from types import SimpleNamespace

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
