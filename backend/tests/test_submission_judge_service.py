import subprocess
import sys
from datetime import datetime, timezone

import pytest

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
from backend.app.models.test_case import TestCase
from backend.app.models.topic import Topic
from backend.app.models.user_problem_progress import UserProblemProgress
from backend.app.services.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionRunner,
    ExecutionStatus,
)
from backend.app.services.submission import SubmissionJudgeService
import backend.app.services.submission as submission_service


class FakeRunner(ExecutionRunner):
    def __init__(self, results, on_execute=None):
        self.results = iter(results)
        self.requests: list[ExecutionRequest] = []
        self.on_execute = on_execute

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        self.requests.append(request)
        if self.on_execute is not None:
            self.on_execute()
        return next(self.results)


def create_problem(db):
    topic = Topic(
        name="Judge Topic",
        slug="judge-topic",
        display_order=1,
    )
    db.add(topic)
    db.flush()

    problem = Problem(
        topic_id=topic.id,
        title="Judge Problem",
        slug="judge-problem",
        statement="Test problem.",
        constraints="1 <= n <= 10",
        difficulty=Difficulty.EASY,
        tags=[],
        starter_code={"python": "", "cpp": ""},
        time_limit_ms=321,
        memory_limit_mb=64,
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


def create_case(db, problem, *, display_order, input_text, expected="ok"):
    test_case = TestCase(
        problem_id=problem.id,
        input=input_text,
        expected_output=expected,
        run_enabled=True,
        submit_enabled=True,
        is_sample=False,
        display_order=display_order,
    )
    db.add(test_case)
    db.commit()
    db.refresh(test_case)
    return test_case


def create_submission(db, normal_user, problem):
    now = datetime.now(timezone.utc)
    submission = Submission(
        user_id=normal_user.id,
        problem_id=problem.id,
        language="python",
        source_code="print('ok')",
        status=SubmissionStatus.QUEUED,
        created_at=now,
        updated_at=now,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def passed(stdout="ok"):
    return ExecutionResult(
        status=ExecutionStatus.PASSED,
        stdout=stdout,
        execution_time_ms=12,
        memory_used_mb=3,
    )


def test_all_passes_are_accepted_and_persisted(db, normal_user):
    problem = create_problem(db)
    first = create_case(db, problem, display_order=1, input_text="first")
    second = create_case(db, problem, display_order=2, input_text="second")
    submission = create_submission(db, normal_user, problem)
    runner = FakeRunner([passed(), passed()])

    before = submission.updated_at
    result = SubmissionJudgeService({"python": runner}).execute(
        db, submission.id
    )

    assert result.status is SubmissionStatus.COMPLETED
    assert result.verdict is SubmissionVerdict.ACCEPTED
    assert result.completed_at is not None
    assert result.updated_at >= result.completed_at
    assert result.updated_at > before
    persisted = db.query(SubmissionResult).filter_by(
        submission_id=submission.id
    ).order_by(SubmissionResult.display_order).all()
    assert [item.test_case_id for item in persisted] == [first.id, second.id]
    assert [item.status for item in persisted] == [
        SubmissionResultStatus.PASSED,
        SubmissionResultStatus.PASSED,
    ]
    progress = db.query(UserProblemProgress).filter_by(
        user_id=normal_user.id,
        problem_id=problem.id,
    ).one()
    assert progress.solved is True


def test_accepted_marks_existing_unsolved_progress_solved(db, normal_user):
    problem = create_problem(db)
    create_case(db, problem, display_order=1, input_text="first")
    progress = UserProblemProgress(
        user_id=normal_user.id,
        problem_id=problem.id,
        solved=False,
    )
    db.add(progress)
    db.commit()

    submission = create_submission(db, normal_user, problem)
    SubmissionJudgeService({"python": FakeRunner([passed()])}).execute(
        db, submission.id
    )

    db.refresh(progress)
    assert progress.solved is True


def test_accepted_never_downgrades_already_solved_progress(db, normal_user):
    problem = create_problem(db)
    create_case(db, problem, display_order=1, input_text="first")
    progress = UserProblemProgress(
        user_id=normal_user.id,
        problem_id=problem.id,
        solved=True,
    )
    db.add(progress)
    db.commit()

    submission = create_submission(db, normal_user, problem)
    SubmissionJudgeService({"python": FakeRunner([passed()])}).execute(
        db, submission.id
    )

    db.refresh(progress)
    assert progress.solved is True


def test_repeated_accepted_completion_is_idempotent(db, normal_user):
    problem = create_problem(db)
    create_case(db, problem, display_order=1, input_text="first")
    submission = create_submission(db, normal_user, problem)
    service = SubmissionJudgeService({"python": FakeRunner([passed()])})

    service.execute(db, submission.id)
    completed = db.get(Submission, submission.id)
    service._complete(db, completed, SubmissionVerdict.ACCEPTED)

    assert db.query(UserProblemProgress).filter_by(
        user_id=normal_user.id,
        problem_id=problem.id,
    ).count() == 1
    assert db.query(UserProblemProgress).filter_by(
        user_id=normal_user.id,
        problem_id=problem.id,
    ).one().solved is True


def test_accepted_progress_failure_rolls_back_terminal_completion(
    db,
    normal_user,
    monkeypatch,
):
    problem = create_problem(db)
    create_case(db, problem, display_order=1, input_text="first")
    submission = create_submission(db, normal_user, problem)

    def fail_progress(*args, **kwargs):
        raise RuntimeError("progress database failure")

    monkeypatch.setattr(
        submission_service,
        "upsert_solved_progress",
        fail_progress,
    )

    with pytest.raises(submission_service.AcceptedProgressPersistenceError):
        SubmissionJudgeService({"python": FakeRunner([passed()])}).execute(
            db, submission.id
        )

    db.refresh(submission)
    assert submission.status is SubmissionStatus.RUNNING
    assert submission.verdict is None
    assert submission.completed_at is None
    assert db.query(UserProblemProgress).filter_by(
        user_id=normal_user.id,
        problem_id=problem.id,
    ).count() == 0


@pytest.mark.parametrize(
    ("execution_status", "expected_result_status", "expected_verdict"),
    [
        (
            ExecutionStatus.PASSED,
            SubmissionResultStatus.WRONG_ANSWER,
            SubmissionVerdict.WRONG_ANSWER,
        ),
        (
            ExecutionStatus.COMPILE_ERROR,
            SubmissionResultStatus.COMPILE_ERROR,
            SubmissionVerdict.COMPILE_ERROR,
        ),
        (
            ExecutionStatus.RUNTIME_ERROR,
            SubmissionResultStatus.RUNTIME_ERROR,
            SubmissionVerdict.RUNTIME_ERROR,
        ),
        (
            ExecutionStatus.TIME_LIMIT_EXCEEDED,
            SubmissionResultStatus.TIME_LIMIT_EXCEEDED,
            SubmissionVerdict.TIME_LIMIT_EXCEEDED,
        ),
        (
            ExecutionStatus.MEMORY_LIMIT_EXCEEDED,
            SubmissionResultStatus.MEMORY_LIMIT_EXCEEDED,
            SubmissionVerdict.MEMORY_LIMIT_EXCEEDED,
        ),
        (
            ExecutionStatus.OUTPUT_LIMIT_EXCEEDED,
            SubmissionResultStatus.OUTPUT_LIMIT_EXCEEDED,
            SubmissionVerdict.OUTPUT_LIMIT_EXCEEDED,
        ),
        (
            ExecutionStatus.SYSTEM_ERROR,
            SubmissionResultStatus.SYSTEM_ERROR,
            SubmissionVerdict.SYSTEM_ERROR,
        ),
    ],
)
def test_first_non_pass_maps_to_verdict_and_stops(
    db,
    normal_user,
    execution_status,
    expected_result_status,
    expected_verdict,
):
    problem = create_problem(db)
    create_case(db, problem, display_order=1, input_text="first")
    create_case(db, problem, display_order=2, input_text="second")
    submission = create_submission(db, normal_user, problem)
    runner = FakeRunner([
        ExecutionResult(status=execution_status, stdout="wrong"),
    ] if execution_status is not ExecutionStatus.PASSED else [passed("wrong")])

    result = SubmissionJudgeService({"python": runner}).execute(
        db, submission.id
    )

    assert result.status is SubmissionStatus.COMPLETED
    assert result.verdict is expected_verdict
    assert len(runner.requests) == 1
    persisted = db.query(SubmissionResult).filter_by(
        submission_id=submission.id
    ).all()
    assert len(persisted) == 1
    assert persisted[0].status is expected_result_status
    assert db.query(UserProblemProgress).filter_by(
        user_id=normal_user.id,
        problem_id=problem.id,
    ).count() == 0


def test_submit_cases_are_ordered_and_run_limits_are_used(db, normal_user):
    problem = create_problem(db)
    create_case(db, problem, display_order=2, input_text="second")
    create_case(db, problem, display_order=1, input_text="first")
    create_case(db, problem, display_order=2, input_text="second-tie")
    run_only = TestCase(
        problem_id=problem.id,
        input="ignored",
        expected_output="ok",
        run_enabled=True,
        submit_enabled=False,
        is_sample=False,
        display_order=0,
    )
    db.add(run_only)
    db.commit()
    submission = create_submission(db, normal_user, problem)
    runner = FakeRunner([passed(), passed(), passed()])

    SubmissionJudgeService({"python": runner}).execute(db, submission.id)

    assert [request.stdin for request in runner.requests] == [
        "first",
        "second",
        "second-tie",
    ]
    assert all(request.time_limit_ms == 321 for request in runner.requests)
    assert all(request.memory_limit_mb == 64 for request in runner.requests)


def test_transition_to_running_is_committed_before_execution(db, normal_user):
    problem = create_problem(db)
    create_case(db, problem, display_order=1, input_text="first")
    submission = create_submission(db, normal_user, problem)
    observed_statuses = []

    def observe_running():
        observed_statuses.append(db.get(Submission, submission.id).status)

    runner = FakeRunner([passed()], on_execute=observe_running)

    SubmissionJudgeService({"python": runner}).execute(db, submission.id)

    assert observed_statuses == [SubmissionStatus.RUNNING]


def test_unexpected_execution_exception_marks_submission_failed(
    db,
    normal_user,
):
    problem = create_problem(db)
    create_case(db, problem, display_order=1, input_text="first")
    submission = create_submission(db, normal_user, problem)

    class RaisingRunner(ExecutionRunner):
        def execute(self, request):
            raise RuntimeError("sandbox unavailable")

    result = SubmissionJudgeService({"python": RaisingRunner()}).execute(
        db, submission.id
    )

    assert result.status is SubmissionStatus.FAILED
    assert result.verdict is SubmissionVerdict.SYSTEM_ERROR
    assert result.completed_at is not None
    assert db.query(SubmissionResult).filter_by(
        submission_id=submission.id
    ).count() == 0


def test_worker_import_registers_submission_foreign_key_models():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from backend.app.db.base import Base; "
                "import backend.app.services.execution.submission_worker; "
                "assert 'users' in Base.metadata.tables; "
                "assert 'submission_results' in Base.metadata.tables"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_missing_and_non_queued_submissions_are_rejected(db, normal_user):
    with pytest.raises(ValueError, match="Submission not found"):
        SubmissionJudgeService().execute(db, 999999)

    problem = create_problem(db)
    create_case(db, problem, display_order=1, input_text="first")
    submission = create_submission(db, normal_user, problem)
    submission.status = SubmissionStatus.RUNNING
    db.commit()

    with pytest.raises(ValueError, match="not queued"):
        SubmissionJudgeService().execute(db, submission.id)


def test_invalid_language_is_rejected_before_running(db, normal_user):
    problem = create_problem(db)
    create_case(db, problem, display_order=1, input_text="first")
    submission = create_submission(db, normal_user, problem)
    submission.language = "java"
    db.commit()

    with pytest.raises(ValueError, match="Unsupported language"):
        SubmissionJudgeService().execute(db, submission.id)

    db.refresh(submission)
    assert submission.status is SubmissionStatus.QUEUED
