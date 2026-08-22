from dataclasses import dataclass
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import time
from types import SimpleNamespace

import pytest

from backend.app.models.submission import SubmissionStatus
from backend.app.services.execution.submission_transport import (
    SubmissionDelivery,
    SubmissionJob,
    SubmissionReclaimResult,
)
from backend.app.services.execution.submission_worker import SubmissionWorker
from backend.app.services.submission import (
    SubmissionJudgeService,
    _submission_fence_connection_invalidated,
    submission_execution_fence,
)


class FakeDb:
    def __init__(self, submission=None):
        self.submission = submission
        self.closed = False

    def get(self, model, submission_id):
        if self.submission is not None and self.submission.id == submission_id:
            return self.submission
        return None

    def close(self):
        self.closed = True


class FakeTransport:
    def __init__(self):
        self.acknowledged = []
        self.ack_error = None

    def acknowledge(self, stream_id):
        if self.ack_error is not None:
            raise self.ack_error
        self.acknowledged.append(stream_id)
        return 1


class FakeFenceResult:
    def scalar(self):
        return True


class FakeFenceConnection:
    def __init__(self):
        self.invalidated = False
        self.unlocks = 0

    def execute(self, *args, **kwargs):
        if "unlock" in str(args[0]).lower():
            self.unlocks += 1
        return FakeFenceResult()


class FakeFenceDb:
    def __init__(self, connection):
        self.connection_object = connection
        self.info = {}

    def connection(self):
        return self.connection_object

    def consume(self, *args, **kwargs):
        return []


@dataclass
class FakeJudge:
    events: list[str]
    error: Exception | None = None

    def execute_claimed(self, db, submission):
        self.events.append("judge")
        if self.error:
            raise self.error
        submission.status = SubmissionStatus.COMPLETED
        return submission


def delivery(submission_id, *, attempts=1, stream_id="1-0"):
    return SubmissionDelivery(
        stream_id=stream_id,
        job=SubmissionJob(
            job_id="job-1",
            submission_id=submission_id,
            enqueued_at=datetime.now(timezone.utc),
        ),
        times_delivered=attempts,
    )


def make_worker(transport, db, judge, **kwargs):
    return SubmissionWorker(
        transport,
        consumer_name="worker-2",
        judge_service=judge,
        session_factory=lambda: db,
        **kwargs,
    )


def test_missing_reclaimed_submission_is_acknowledged_without_judging():
    transport = FakeTransport()
    judge = FakeJudge([])
    worker = make_worker(transport, FakeDb(), judge)

    worker.process_reclaimed_delivery(delivery(7))

    assert transport.acknowledged == ["1-0"]
    assert judge.events == []


def test_invalidated_fence_is_detected_without_releasing_or_reacquiring():
    connection = FakeFenceConnection()
    db = FakeFenceDb(connection)

    with submission_execution_fence(db, 7) as acquired:
        assert acquired is True
        assert db.connection() is connection
        connection.invalidated = True
        assert _submission_fence_connection_invalidated(db) is True

    assert connection.unlocks == 0


def test_invalidated_fence_does_not_fall_back_to_unfenced_failure_handling(
    monkeypatch,
):
    connection = SimpleNamespace(invalidated=True)
    db = SimpleNamespace(
        info={"submission_execution_connection": connection},
        get=lambda model, submission_id: None,
    )
    submission = SimpleNamespace(
        id=7,
        problem_id=11,
        language="python",
        status=SubmissionStatus.RUNNING,
    )

    monkeypatch.setattr(
        "backend.app.services.submission.get_problem",
        lambda db, problem_id: (_ for _ in ()).throw(RuntimeError("lost db")),
    )

    with pytest.raises(RuntimeError, match="lost db"):
        SubmissionJudgeService().execute_claimed(db, submission)


def test_terminal_reclaimed_submission_is_acknowledged_without_judging():
    transport = FakeTransport()
    submission = SimpleNamespace(id=7, status=SubmissionStatus.COMPLETED)
    judge = FakeJudge([])
    worker = make_worker(transport, FakeDb(submission), judge)

    worker.process_reclaimed_delivery(delivery(7))

    assert transport.acknowledged == ["1-0"]
    assert judge.events == []


def test_queued_reclaimed_submission_is_claimed_and_judged(monkeypatch):
    transport = FakeTransport()
    submission = SimpleNamespace(id=7, status=SubmissionStatus.QUEUED)
    db = FakeDb(submission)
    judge = FakeJudge([])
    claimed = SimpleNamespace(id=7, status=SubmissionStatus.RUNNING)
    monkeypatch.setattr(
        "backend.app.services.execution.submission_worker.claim_submission",
        lambda db, submission_id: claimed,
    )

    make_worker(transport, db, judge).process_reclaimed_delivery(delivery(7))

    assert judge.events == ["judge"]
    assert transport.acknowledged == ["1-0"]


def test_fresh_running_submission_is_left_pending():
    transport = FakeTransport()
    submission = SimpleNamespace(
        id=7,
        status=SubmissionStatus.RUNNING,
        updated_at=datetime.now(timezone.utc),
    )
    judge = FakeJudge([])

    make_worker(
        transport,
        FakeDb(submission),
        judge,
        reclaim_idle_time_ms=60_000,
    ).process_reclaimed_delivery(delivery(7))

    assert judge.events == []
    assert transport.acknowledged == []


def test_stale_running_submission_cleans_resets_and_reexecutes(monkeypatch):
    transport = FakeTransport()
    submission = SimpleNamespace(
        id=7,
        status=SubmissionStatus.RUNNING,
        updated_at=datetime.now(timezone.utc) - timedelta(minutes=5),
    )
    db = FakeDb(submission)
    judge = FakeJudge([])
    events = []

    def reset(db, submission_id, *, stale_cutoff):
        events.append("reset")
        submission.status = SubmissionStatus.QUEUED
        return True

    monkeypatch.setattr(
        "backend.app.services.execution.submission_worker.reset_stale_submission",
        reset,
    )
    monkeypatch.setattr(
        "backend.app.services.execution.submission_worker.claim_submission",
        lambda db, submission_id: (
            events.append("claim")
            or SimpleNamespace(id=submission_id, status=SubmissionStatus.RUNNING)
        ),
    )

    make_worker(transport, db, judge).process_reclaimed_delivery(
        delivery(7)
    )

    assert events == ["reset", "claim"]
    assert judge.events == ["judge"]
    assert transport.acknowledged == ["1-0"]


def test_reclaimed_judge_failure_leaves_message_pending(monkeypatch):
    transport = FakeTransport()
    submission = SimpleNamespace(id=7, status=SubmissionStatus.QUEUED)
    judge = FakeJudge([], error=RuntimeError("boom"))
    monkeypatch.setattr(
        "backend.app.services.execution.submission_worker.claim_submission",
        lambda db, submission_id: SimpleNamespace(
            id=submission_id,
            status=SubmissionStatus.RUNNING,
        ),
    )

    make_worker(transport, FakeDb(submission), judge).process_reclaimed_delivery(
        delivery(7)
    )

    assert judge.events == ["judge"]
    assert transport.acknowledged == []


def test_acknowledgement_failure_leaves_delivery_unacknowledged(monkeypatch):
    transport = FakeTransport()
    transport.ack_error = RuntimeError("redis unavailable")
    submission = SimpleNamespace(id=7, status=SubmissionStatus.QUEUED)
    judge = FakeJudge([])
    monkeypatch.setattr(
        "backend.app.services.execution.submission_worker.claim_submission",
        lambda db, submission_id: SimpleNamespace(
            id=submission_id,
            status=SubmissionStatus.RUNNING,
        ),
    )

    make_worker(transport, FakeDb(submission), judge).process_delivery(
        delivery(7)
    )

    assert transport.acknowledged == []


def test_retry_limit_marks_submission_failed_and_acknowledges(monkeypatch):
    transport = FakeTransport()
    submission = SimpleNamespace(id=7, status=SubmissionStatus.QUEUED)
    judge = FakeJudge([])
    events = []
    monkeypatch.setattr(
        "backend.app.services.execution.submission_worker.fail_submission_with_system_error",
        lambda db, submission_id: events.append("failed") or True,
    )

    make_worker(
        transport,
        FakeDb(submission),
        judge,
        max_delivery_attempts=2,
    ).process_reclaimed_delivery(delivery(7, attempts=3))

    assert events == ["failed"]
    assert judge.events == []
    assert transport.acknowledged == ["1-0"]


def test_two_recovery_workers_only_one_executes(monkeypatch):
    transport = FakeTransport()
    submission = SimpleNamespace(id=7, status=SubmissionStatus.QUEUED)
    judge = FakeJudge([])
    fence_lock = Lock()

    @contextmanager
    def fence(db, submission_id):
        acquired = fence_lock.acquire(blocking=False)
        try:
            yield acquired
        finally:
            if acquired:
                fence_lock.release()

    def claim(db, submission_id):
        if submission.status is not SubmissionStatus.QUEUED:
            raise ValueError("Submission is not queued")
        submission.status = SubmissionStatus.RUNNING
        return submission

    original_judge = judge.execute_claimed

    def slow_judge(db, claimed):
        result = original_judge(db, claimed)
        time.sleep(0.02)
        return result

    judge.execute_claimed = slow_judge
    monkeypatch.setattr(
        "backend.app.services.execution.submission_worker.submission_execution_fence",
        fence,
    )
    monkeypatch.setattr(
        "backend.app.services.execution.submission_worker.claim_submission",
        claim,
    )

    worker_one = make_worker(transport, FakeDb(submission), judge)
    worker_two = make_worker(transport, FakeDb(submission), judge)
    with ThreadPoolExecutor(max_workers=2) as executor:
        list(
            executor.map(
                lambda worker: worker.process_reclaimed_delivery(delivery(7)),
                (worker_one, worker_two),
            )
        )

    assert judge.events == ["judge"]


def test_reclaim_cursor_is_consumed_in_batches():
    class ReclaimTransport(FakeTransport):
        def __init__(self):
            super().__init__()
            self.cursors = []
            self.calls = 0

        def reclaim(self, consumer_name, **kwargs):
            self.cursors.append(kwargs["start_id"])
            self.calls += 1
            if self.calls == 1:
                return SubmissionReclaimResult((), "2-0")
            return SubmissionReclaimResult((), "0-0")

    transport = ReclaimTransport()
    worker = make_worker(transport, FakeDb(), FakeJudge([]))

    worker.recover_pending()

    assert transport.cursors == ["0-0", "2-0"]
