"""Centralized configuration for the V1 Run execution boundary.

Problem-specific time and memory limits are supplied by the Problem model.
These values define process-wide safety ceilings and Run infrastructure policy.
"""


# Client-controlled payload ceilings.
MAX_SOURCE_CODE_BYTES = 100_000
MAX_CUSTOM_INPUT_BYTES = 100_000

# Maximum captured output from a user program, per stream.
MAX_STDOUT_BYTES = 200_000
MAX_STDERR_BYTES = 65_536

# Execution and compilation ceilings.
MAX_RUN_TIMEOUT_MS = 5_000
COMPILE_TIMEOUT_MS = 5_000
COMPILE_MEMORY_LIMIT_MB = 256
RUN_REQUEST_TIMEOUT_MS = 15_000

# Infrastructure ceiling for problem memory limits.
MAX_MEMORY_LIMIT_MB = 512

# Maximum number of processes/threads allowed inside a sandbox.
MAX_PIDS = 64

# Maximum writable temporary filesystem exposed to a single execution.
RUN_WORKSPACE_SIZE_MB = 64

# Maximum CPU capacity allocated to a single execution.
RUN_CPU_COUNT = 1.0

# Worker concurrency policy for the V1 EC2 baseline.
MAX_CONCURRENT_RUNS = 2
MAX_CONCURRENT_RUNS_PER_USER = 2

# Run API rate-limit policy.
RUN_RATE_LIMIT_PER_MINUTE = 10

# Redis transient result lifetime.
RUN_RESULT_TTL_SECONDS = 60


# Backward-compatible aliases for the lower-level sandbox implementation.
# New Run/worker code should use the canonical names above.
MAX_EXECUTION_TIME_MS = MAX_RUN_TIMEOUT_MS
MAX_PROCESSES = MAX_PIDS
MAX_WORKSPACE_BYTES = RUN_WORKSPACE_SIZE_MB * 1024 * 1024
RESULT_TTL_SECONDS = RUN_RESULT_TTL_SECONDS
API_RESULT_WAIT_TIMEOUT_MS = RUN_REQUEST_TIMEOUT_MS
