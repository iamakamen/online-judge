import os
import time
from pathlib import Path

import pytest

from backend.app.services.execution.sandbox import SandboxExecutor, SandboxRequest


SANDBOX_TEST_IMAGE = os.getenv("SANDBOX_TEST_IMAGE", "oj-sandbox-test:latest")


@pytest.fixture(scope="module")
def sandbox():
    return SandboxExecutor(image=SANDBOX_TEST_IMAGE)


@pytest.fixture(scope="module")
def workspace(tmp_path_factory):
    root = tmp_path_factory.mktemp("sandbox-workspace")
    (root / "main.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    return root


def run(sandbox, workspace, command, **kwargs):
    return sandbox.execute(
        SandboxRequest(
            workspace=Path(workspace),
            command=command,
            **kwargs,
        )
    )


def test_normal_execution(sandbox, workspace):
    result = run(sandbox, workspace, ("/bin/sh", "-c", "printf hello"))

    assert result.exit_code == 0
    assert result.stdout == "hello"
    assert result.timed_out is False
    assert result.output_limited is False


def test_nonzero_exit_is_captured(sandbox, workspace):
    result = run(sandbox, workspace, ("/bin/sh", "-c", "printf error >&2; exit 7"))

    assert result.exit_code == 7
    assert result.stderr == "error"


def test_workspace_is_read_only(sandbox, workspace):
    result = run(
        sandbox,
        workspace,
        ("/bin/sh", "-c", "printf blocked > /workspace/blocked.txt"),
    )

    assert result.exit_code != 0
    assert not (workspace / "blocked.txt").exists()


def test_tmp_is_writable(sandbox, workspace):
    result = run(
        sandbox,
        workspace,
        ("/bin/sh", "-c", "printf allowed > /tmp/runtime.txt && cat /tmp/runtime.txt"),
    )

    assert result.exit_code == 0
    assert result.stdout == "allowed"


def test_timeout_terminates_execution(sandbox, workspace):
    started = time.monotonic()
    result = run(
        sandbox,
        workspace,
        ("/bin/sh", "-c", "sleep 5"),
        timeout_ms=500,
    )
    elapsed = time.monotonic() - started

    assert result.timed_out is True
    assert elapsed < 3


def test_stdout_limit_terminates_execution(sandbox, workspace):
    result = run(
        sandbox,
        workspace,
        ("/bin/sh", "-c", "head -c 70000 /dev/zero"),
        stdout_limit_bytes=64_000,
    )

    assert result.output_limited is True
    assert len(result.stdout.encode()) <= 64_000


def test_network_is_disabled(sandbox, workspace):
    result = run(
        sandbox,
        workspace,
        ("/bin/sh", "-c", "wget -q -T 1 -O - http://1.1.1.1/"),
    )

    assert result.exit_code != 0


def test_container_is_cleaned_up(sandbox, workspace):
    result = run(sandbox, workspace, ("/bin/sh", "-c", "printf cleanup"))

    assert result.exit_code == 0

    # SandboxExecutor uses --rm and therefore should not leave its named
    # execution container behind after a normal completion.
    assert not sandbox.container_exists(result.container_name)
