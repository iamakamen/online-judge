from backend.app.core import execution


def test_run_payload_limits_are_centralized():
    assert execution.MAX_SOURCE_CODE_BYTES == 100_000
    assert execution.MAX_CUSTOM_INPUT_BYTES == 100_000
    assert execution.MAX_STDOUT_BYTES == 200_000
    assert execution.MAX_STDERR_BYTES == 65_536


def test_run_time_and_resource_policy_is_centralized():
    assert execution.MAX_RUN_TIMEOUT_MS == 5_000
    assert execution.COMPILE_TIMEOUT_MS == 5_000
    assert execution.RUN_REQUEST_TIMEOUT_MS == 15_000
    assert execution.MAX_PIDS == 64
    assert execution.RUN_WORKSPACE_SIZE_MB == 64
    assert execution.RUN_CPU_COUNT == 1.0


def test_run_concurrency_and_rate_policy_is_centralized():
    assert execution.MAX_CONCURRENT_RUNS == 2
    assert execution.MAX_CONCURRENT_RUNS_PER_USER == 2
    assert execution.RUN_RATE_LIMIT_PER_MINUTE == 10
    assert execution.RUN_RESULT_TTL_SECONDS == 60


def test_lower_level_sandbox_aliases_match_canonical_policy():
    assert execution.MAX_EXECUTION_TIME_MS == execution.MAX_RUN_TIMEOUT_MS
    assert execution.MAX_PROCESSES == execution.MAX_PIDS
    assert execution.MAX_WORKSPACE_BYTES == 64 * 1024 * 1024
    assert execution.RESULT_TTL_SECONDS == execution.RUN_RESULT_TTL_SECONDS
    assert execution.API_RESULT_WAIT_TIMEOUT_MS == execution.RUN_REQUEST_TIMEOUT_MS
