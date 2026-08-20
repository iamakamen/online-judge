from pathlib import Path

import pytest

from backend.app.services.execution.sandbox import SandboxExecutor, SandboxRequest


@pytest.fixture()
def sandbox_request(tmp_path: Path) -> SandboxRequest:
    return SandboxRequest(
        image="online-judge-runner:test",
        command=("python3", "/workspace/main.py"),
        workspace=tmp_path,
        timeout_ms=1000,
        memory_limit_mb=128,
    )


def test_build_command_enforces_container_isolation(
    sandbox_request: SandboxRequest,
) -> None:
    command = SandboxExecutor()._build_command(sandbox_request, "oj-run-test")

    assert "--network" in command
    assert command[command.index("--network") + 1] == "none"
    assert "--read-only" in command
    assert command[command.index("--cap-drop") + 1] == "ALL"
    assert "--init" in command
    assert "--security-opt" in command
    assert "no-new-privileges:true" in command
    assert "seccomp=builtin" in command
    assert command[command.index("--memory") + 1] == "128m"
    assert command[command.index("--memory-swap") + 1] == "128m"
    assert command[command.index("--cpus") + 1] == "1.0"
    assert command[command.index("--user") + 1] == "1000:1000"
    assert "--pids-limit" in command
    assert "--pull" in command
    assert command[command.index("--pull") + 1] == "never"


def test_rejects_timeout_above_global_ceiling(
    sandbox_request: SandboxRequest,
) -> None:
    request = SandboxRequest(
        **{**sandbox_request.__dict__, "timeout_ms": 5001}
    )

    with pytest.raises(ValueError, match="timeout"):
        SandboxExecutor._validate_request(request)


def test_rejects_memory_above_global_ceiling(
    sandbox_request: SandboxRequest,
) -> None:
    request = SandboxRequest(
        **{**sandbox_request.__dict__, "memory_limit_mb": 513}
    )

    with pytest.raises(ValueError, match="memory"):
        SandboxExecutor._validate_request(request)


def test_rejects_relative_workspace(
    sandbox_request: SandboxRequest,
) -> None:
    request = SandboxRequest(
        **{**sandbox_request.__dict__, "workspace": Path("relative")}
    )

    with pytest.raises(ValueError, match="absolute"):
        SandboxExecutor._validate_request(request)
