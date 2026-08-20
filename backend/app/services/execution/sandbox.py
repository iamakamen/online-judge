"""Ephemeral Docker sandbox used by the execution engine.

This module owns container-level isolation and resource controls. It does not
know anything about Python or C++ semantics. Language runners supply the image
and command to execute.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

from backend.app.core.execution import (
    MAX_CONCURRENT_EXECUTIONS,
    MAX_EXECUTION_TIME_MS,
    MAX_MEMORY_LIMIT_MB,
    MAX_PROCESSES,
    MAX_STDERR_BYTES,
    MAX_STDOUT_BYTES,
    MAX_WORKSPACE_BYTES,
)


@dataclass(frozen=True)
class SandboxRequest:
    image: str
    command: tuple[str, ...]
    workspace: Path
    timeout_ms: int
    memory_limit_mb: int
    cpus: float = 1.0
    pids_limit: int = MAX_PROCESSES
    stdout_limit_bytes: int = MAX_STDOUT_BYTES
    stderr_limit_bytes: int = MAX_STDERR_BYTES


@dataclass(frozen=True)
class SandboxResult:
    exit_code: int | None
    stdout: str
    stderr: str
    execution_time_ms: int
    timed_out: bool = False
    output_limited: bool = False
    infrastructure_error: str | None = None


class SandboxExecutor:
    """Execute a command in one ephemeral, restricted Docker container.

    The caller is responsible for supplying a trusted execution image and a
    workspace containing only the files required for the current run.
    """

    def __init__(self, docker_binary: str = "docker") -> None:
        self._docker_binary = docker_binary

    def execute(self, request: SandboxRequest) -> SandboxResult:
        self._validate_request(request)
        if shutil.which(self._docker_binary) is None:
            return SandboxResult(
                exit_code=None,
                stdout="",
                stderr="",
                execution_time_ms=0,
                infrastructure_error="docker executable is unavailable",
            )

        request.workspace.mkdir(parents=True, exist_ok=True)
        command = self._build_command(request)
        started = time.monotonic()

        try:
            completed = subprocess.run(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
                timeout=request.timeout_ms / 1000,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            elapsed = self._elapsed_ms(started)
            stdout = self._decode_and_limit(exc.stdout or b"", request.stdout_limit_bytes)
            stderr = self._decode_and_limit(exc.stderr or b"", request.stderr_limit_bytes)
            self._force_cleanup_container(command)
            return SandboxResult(
                exit_code=None,
                stdout=stdout,
                stderr=stderr,
                execution_time_ms=elapsed,
                timed_out=True,
                output_limited=(
                    len(stdout.encode()) >= request.stdout_limit_bytes
                    or len(stderr.encode()) >= request.stderr_limit_bytes
                ),
            )
        except OSError as exc:
            return SandboxResult(
                exit_code=None,
                stdout="",
                stderr="",
                execution_time_ms=self._elapsed_ms(started),
                infrastructure_error=str(exc),
            )

        elapsed = self._elapsed_ms(started)
        stdout = self._decode_and_limit(
            completed.stdout, request.stdout_limit_bytes
        )
        stderr = self._decode_and_limit(
            completed.stderr, request.stderr_limit_bytes
        )
        output_limited = (
            len(completed.stdout) > request.stdout_limit_bytes
            or len(completed.stderr) > request.stderr_limit_bytes
        )

        return SandboxResult(
            exit_code=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            execution_time_ms=elapsed,
            output_limited=output_limited,
        )

    def _build_command(self, request: SandboxRequest) -> list[str]:
        return [
            self._docker_binary,
            "run",
            "--rm",
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--pids-limit",
            str(request.pids_limit),
            "--memory",
            f"{request.memory_limit_mb}m",
            "--cpus",
            str(request.cpus),
            "--user",
            "1000:1000",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=8m",
            "--mount",
            f"type=bind,src={request.workspace},dst=/workspace,rw,nosuid,nodev",
            "-w",
            "/workspace",
            request.image,
            *request.command,
        ]

    @staticmethod
    def _validate_request(request: SandboxRequest) -> None:
        if not request.command:
            raise ValueError("sandbox command must not be empty")
        if request.timeout_ms <= 0:
            raise ValueError("sandbox timeout must be positive")
        if request.timeout_ms > MAX_EXECUTION_TIME_MS:
            raise ValueError("sandbox timeout exceeds configured ceiling")
        if request.memory_limit_mb <= 0 or request.memory_limit_mb > MAX_MEMORY_LIMIT_MB:
            raise ValueError("sandbox memory limit exceeds configured ceiling")
        if request.cpus <= 0:
            raise ValueError("sandbox CPU limit must be positive")
        if request.pids_limit <= 0 or request.pids_limit > MAX_PROCESSES:
            raise ValueError("sandbox PID limit exceeds configured ceiling")
        if request.stdout_limit_bytes <= 0 or request.stdout_limit_bytes > MAX_STDOUT_BYTES:
            raise ValueError("sandbox stdout limit exceeds configured ceiling")
        if request.stderr_limit_bytes <= 0 or request.stderr_limit_bytes > MAX_STDERR_BYTES:
            raise ValueError("sandbox stderr limit exceeds configured ceiling")
        if not request.workspace.is_absolute():
            raise ValueError("sandbox workspace must be an absolute path")
        if request.workspace.exists() and not request.workspace.is_dir():
            raise ValueError("sandbox workspace must be a directory")

        # Keep the workspace inside a caller-managed temporary directory. The
        # size ceiling is a policy value here; actual enforcement is added by
        # the execution image/filesystem layer where it can be measured safely.
        if MAX_WORKSPACE_BYTES <= 0:
            raise ValueError("sandbox workspace ceiling must be positive")

    @staticmethod
    def _decode_and_limit(data: bytes, limit: int) -> str:
        return data[:limit].decode("utf-8", errors="replace")

    @staticmethod
    def _elapsed_ms(started: float) -> int:
        return int((time.monotonic() - started) * 1000)

    def _force_cleanup_container(self, command: list[str]) -> None:
        # docker run --rm normally removes the container. After a host-side
        # timeout, attempt a best-effort cleanup using the container name only
        # if a future implementation adds an explicit name. Currently there is
        # no safe deterministic container identifier to target here.
        return None


class SandboxWorkspace:
    """Create and clean a per-execution temporary workspace."""

    def __enter__(self) -> Path:
        self._temporary_directory = tempfile.TemporaryDirectory(
            prefix="online-judge-run-"
        )
        return Path(self._temporary_directory.name)

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._temporary_directory.cleanup()
