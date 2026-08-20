"""Configuration for the V1 Run execution boundary.

Problem-specific limits are supplied by the Problem model. These values are
process-wide safety ceilings for the execution infrastructure itself.
"""


# Maximum source submitted in a single Run request.
MAX_SOURCE_CODE_BYTES = 100_000

# Maximum custom input accepted by the Run API.
MAX_CUSTOM_INPUT_BYTES = 100_000

# Maximum captured output from a user program, per stream.
MAX_STDOUT_BYTES = 64_000
MAX_STDERR_BYTES = 64_000

# Infrastructure ceilings. A problem may request a lower limit, never a
# higher one.
MAX_EXECUTION_TIME_MS = 5_000
MAX_MEMORY_LIMIT_MB = 512

# Compilation is separate from program execution for C++.
COMPILE_TIMEOUT_MS = 5_000

# Maximum number of processes/threads allowed inside a sandbox.
MAX_PROCESSES = 32

# Maximum filesystem space exposed to a single execution workspace.
MAX_WORKSPACE_BYTES = 16 * 1024 * 1024

# Maximum number of Run jobs one worker should execute concurrently on the
# V1 EC2 baseline. This is intentionally conservative for a 2-vCPU host.
MAX_CONCURRENT_EXECUTIONS = 2

# Redis result lifetime once a Run has completed.
RESULT_TTL_SECONDS = 300

# Maximum time the API layer should wait for a synchronous Run result before
# returning an infrastructure timeout to the caller.
API_RESULT_WAIT_TIMEOUT_MS = 10_000
