from datetime import datetime, timezone

from backend.app.services.execution.submission_transport import (
    SUBMISSION_CONSUMER_GROUP,
    SUBMISSION_STREAM_KEY,
    SubmissionDelivery,
    SubmissionJob,
    SubmissionTransport,
)


class FakeStreamsRedis:
    def __init__(self):
        self.streams: dict[str, list[tuple[str, dict[str, str]]]] = {}
        self.groups: set[tuple[str, str]] = set()
        self.pending: dict[tuple[str, str], dict[str, str]] = {}
        self.acknowledged: list[tuple[str, str, str]] = []
        self.pending_counts: dict[str, int] = {}
        self.xautoclaim_calls = []
        self.next_id = 0

    def xadd(self, key, fields, id="*"):
        self.next_id += 1
        stream_id = f"{self.next_id}-0"
        self.streams.setdefault(key, []).append((stream_id, dict(fields)))
        return stream_id

    def xgroup_create(self, key, group, id="0-0", mkstream=False):
        self.streams.setdefault(key, [])
        group_key = (key, group)
        if group_key in self.groups:
            from redis.exceptions import ResponseError

            raise ResponseError("BUSYGROUP Consumer Group name already exists")
        self.groups.add(group_key)

    def xreadgroup(self, group, consumer, streams, count=1, block=None):
        key = next(iter(streams))
        messages = self.streams[key][:count]
        self.streams[key] = self.streams[key][len(messages):]
        for stream_id, _ in messages:
            self.pending[(key, stream_id)] = consumer
        return [(key, messages)] if messages else []

    def xack(self, key, group, stream_id):
        self.acknowledged.append((key, group, stream_id))
        self.pending.pop((key, stream_id), None)
        return 1

    def xautoclaim(
        self,
        key,
        group,
        consumer,
        min_idle_time,
        start_id="0-0",
        count=10,
    ):
        self.xautoclaim_calls.append((start_id, count))
        messages = [
            message
            for message in self.streams.get(key, [])[:count]
        ]
        return ["9-0", messages, []]

    def xpending_range(self, key, group, min, max, count):
        stream_id = min
        return [
            {
                "message_id": stream_id,
                "consumer": "worker-2",
                "time_since_delivered": 1000,
                "times_delivered": self.pending_counts.get(stream_id, 1),
            }
        ]


def transport(fake_redis):
    return SubmissionTransport(fake_redis)


def test_submission_job_serialization_round_trips_only_job_fields():
    job = SubmissionJob(
        job_id="job-1",
        submission_id=42,
        enqueued_at=datetime(2026, 8, 22, tzinfo=timezone.utc),
    )

    payload = SubmissionTransport.serialize_job(job)
    restored = SubmissionTransport.deserialize_job(payload)

    assert restored == job
    assert set(payload) == {"job_id", "submission_id", "enqueued_at"}
    assert "source_code" not in payload
    assert "test_cases" not in payload
    assert "expected_output" not in payload


def test_enqueue_and_consume_preserve_submission_and_job_ids():
    fake_redis = FakeStreamsRedis()
    queue = transport(fake_redis)

    enqueued = queue.enqueue(123)
    deliveries = queue.consume("worker-1")

    assert len(deliveries) == 1
    assert deliveries[0].job.job_id == enqueued.job_id
    assert deliveries[0].job.submission_id == 123
    assert deliveries[0].stream_id == "1-0"


def test_submission_jobs_use_dedicated_stream_key():
    fake_redis = FakeStreamsRedis()
    queue = transport(fake_redis)

    queue.enqueue(7)

    assert list(fake_redis.streams) == [SUBMISSION_STREAM_KEY]
    assert SUBMISSION_STREAM_KEY == "submission:jobs"
    assert SUBMISSION_CONSUMER_GROUP == "submission-workers"


def test_acknowledge_removes_delivery_from_pending():
    fake_redis = FakeStreamsRedis()
    queue = transport(fake_redis)
    queue.enqueue(7)
    delivery = queue.consume("worker-1")[0]

    assert queue.acknowledge(delivery.stream_id) == 1
    assert fake_redis.acknowledged == [
        (SUBMISSION_STREAM_KEY, SUBMISSION_CONSUMER_GROUP, delivery.stream_id)
    ]
    assert fake_redis.pending == {}


def test_reclaim_uses_stream_pending_support():
    fake_redis = FakeStreamsRedis()
    queue = transport(fake_redis)
    queue.enqueue(99)
    delivery = queue.consume("worker-1")[0]

    fake_redis.streams[SUBMISSION_STREAM_KEY].append(
        (delivery.stream_id, SubmissionTransport.serialize_job(delivery.job))
    )
    reclaimed = queue.reclaim("worker-2", min_idle_time_ms=1)

    assert reclaimed[0].job.submission_id == 99
    assert reclaimed[0].times_delivered == 1
    assert reclaimed.next_cursor == "9-0"


def test_reclaim_preserves_delivery_count_and_cursor_batching():
    fake_redis = FakeStreamsRedis()
    queue = transport(fake_redis)
    job = queue.enqueue(100)
    delivery = queue.consume("worker-1")[0]
    fake_redis.streams[SUBMISSION_STREAM_KEY].append(
        (delivery.stream_id, SubmissionTransport.serialize_job(job))
    )
    fake_redis.pending_counts[delivery.stream_id] = 4

    reclaimed = queue.reclaim(
        "worker-2",
        min_idle_time_ms=1,
        count=1,
        start_id="4-0",
    )

    assert reclaimed[0].times_delivered == 4
    assert fake_redis.xautoclaim_calls == [("4-0", 1)]
