from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from threading import Event

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from backend.app.models.problem import Difficulty, Problem
from backend.app.models.submission import (
    Submission,
    SubmissionStatus,
    SubmissionVerdict,
)
from backend.app.models.submission_result import (
    SubmissionResult,
    SubmissionResultStatus,
)
from backend.app.models.test_case import TestCase as _TestCase
from backend.app.models.topic import Topic
from backend.app.services.submission import (
    claim_submission,
    reset_stale_submission,
    submission_execution_fence,
)


def create_problem(db):
    topic = Topic(
        name="Claim Topic",
        slug="claim-topic",
        display_order=1,
    )
    db.add(topic)
    db.flush()

    problem = Problem(
        topic_id=topic.id,
        title="Claim Problem",
        slug="claim-problem",
        statement="Test problem.",
        constraints="1 <= n <= 10",
        difficulty=Difficulty.EASY,
        tags=[],
        starter_code={"python": ""},
        time_limit_ms=1000,
        memory_limit_mb=64,
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


def create_submission(db, normal_user, problem, *, status=SubmissionStatus.QUEUED):
    created_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    submission = Submission(
        user_id=normal_user.id,
        problem_id=problem.id,
        language="python",
        source_code="print('ok')",
        status=status,
        verdict=(
            SubmissionVerdict.ACCEPTED
            if status is SubmissionStatus.COMPLETED
            else None
        ),
        created_at=created_at,
        updated_at=created_at,
        completed_at=(
            created_at if status is SubmissionStatus.COMPLETED else None
        ),
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def test_queued_submission_can_be_claimed_and_timestamp_is_updated(
    db,
    normal_user,
):
    problem = create_problem(db)
    submission = create_submission(db, normal_user, problem)
    original_updated_at = submission.updated_at

    claimed = claim_submission(db, submission.id)

    assert claimed.status is SubmissionStatus.RUNNING
    assert claimed.updated_at > original_updated_at
    assert claimed.created_at == submission.created_at
    assert claimed.completed_at is None


def test_only_one_concurrent_claim_succeeds(db, normal_user):
    problem = create_problem(db)
    submission = create_submission(db, normal_user, problem)
    session_factory = sessionmaker(
        bind=db.get_bind(),
        autoflush=False,
        autocommit=False,
    )

    def attempt_claim():
        session = session_factory()
        try:
            claimed = claim_submission(session, submission.id)
            return ("claimed", claimed.status)
        except ValueError as exc:
            return ("rejected", str(exc))
        finally:
            session.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(lambda _: attempt_claim(), range(2)))

    assert [outcome[0] for outcome in outcomes].count("claimed") == 1
    assert [outcome[0] for outcome in outcomes].count("rejected") == 1
    assert next(outcome[1] for outcome in outcomes if outcome[0] == "rejected") == (
        "Submission is not queued"
    )


@pytest.mark.parametrize(
    "status",
    [SubmissionStatus.COMPLETED, SubmissionStatus.FAILED],
)
def test_terminal_submission_cannot_be_claimed(db, normal_user, status):
    problem = create_problem(db)
    submission = create_submission(db, normal_user, problem, status=status)

    with pytest.raises(ValueError, match="Submission is not queued"):
        claim_submission(db, submission.id)


def test_missing_submission_is_reported(db):
    with pytest.raises(ValueError, match="Submission not found"):
        claim_submission(db, 999999)


def test_advisory_execution_fence_allows_only_one_concurrent_holder(db):
    session_factory = sessionmaker(
        bind=db.get_bind(),
        autoflush=False,
        autocommit=False,
    )
    entered = Event()
    release = Event()

    def first_holder():
        session = session_factory()
        try:
            with submission_execution_fence(session, 424242) as acquired:
                entered.set()
                release.wait(timeout=5)
                return acquired
        finally:
            session.close()

    def second_holder():
        entered.wait(timeout=5)
        session = session_factory()
        try:
            with submission_execution_fence(session, 424242) as acquired:
                return acquired
        finally:
            session.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(first_holder)
        second = executor.submit(second_holder)
        assert second.result(timeout=5) is False
        release.set()
        assert first.result(timeout=5) is True


def test_advisory_fence_uses_pinned_session_connection_and_survives_rollback(db):
    connection = db.get_bind().connect()
    session = Session(bind=connection, autoflush=False)
    other_connection = db.get_bind().connect()
    other_session = Session(bind=other_connection, autoflush=False)

    try:
        with submission_execution_fence(session, 424243) as acquired:
            assert acquired is True
            assert session.connection() is connection

            session.rollback()

            with submission_execution_fence(
                other_session,
                424243,
            ) as other_acquired:
                assert other_acquired is False

        with submission_execution_fence(
            other_session,
            424243,
        ) as other_acquired:
            assert other_acquired is True
    finally:
        session.close()
        other_session.close()
        connection.close()
        other_connection.close()


def test_stale_reset_clears_partial_results_and_is_conditional(
    db,
    normal_user,
):
    problem = create_problem(db)
    old_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    submission = create_submission(
        db,
        normal_user,
        problem,
        status=SubmissionStatus.RUNNING,
    )
    submission.updated_at = old_time
    test_case = _TestCase(
        problem_id=problem.id,
        input="1",
        expected_output="1",
        run_enabled=False,
        submit_enabled=True,
        is_sample=False,
        display_order=1,
    )
    db.add(test_case)
    db.flush()
    db.add(
        SubmissionResult(
            submission_id=submission.id,
            test_case_id=test_case.id,
            display_order=1,
            status=SubmissionResultStatus.PASSED,
            execution_time_ms=1,
            memory_used_mb=1,
            created_at=old_time,
        )
    )
    db.commit()

    assert reset_stale_submission(
        db,
        submission.id,
        stale_cutoff=datetime.now(timezone.utc) - timedelta(minutes=1),
    ) is True

    refreshed = db.get(Submission, submission.id)
    assert refreshed.status is SubmissionStatus.QUEUED
    assert db.scalars(
        select(SubmissionResult).where(
            SubmissionResult.submission_id == submission.id
        )
    ).all() == []

    refreshed.status = SubmissionStatus.RUNNING
    refreshed.updated_at = datetime.now(timezone.utc)
    db.commit()
    assert reset_stale_submission(
        db,
        submission.id,
        stale_cutoff=datetime.now(timezone.utc) - timedelta(minutes=1),
    ) is False
    assert db.get(Submission, submission.id).status is SubmissionStatus.RUNNING
