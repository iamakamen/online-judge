"""Ephemeral Docker sandbox used by the execution engine.

This module owns container-level isolation and resource controls. It does not
know anything about Python or C++ semantics. Language runners supply the image
and command to execute.
"""

from __future__ import annotations

import selectors
import shutil
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

from backend.app.core.execution import (
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
    stdin: str = ""
    cpus: float = 1.0
    pids_limit: int = MAX_PROCESSES
    stdout_limit_bytes: int = MAX_STDOUT_BYTES
    stderr_limit_bytes: int = MAX_STDERR_BYTES
    workspace_read_only: bool = True


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

    The caller supplies a trusted image and a workspace containing only the
    files required for the current run. The workspace is mounted read-only by
    default. A controlled writable mount is available for compiler phases
    that must materialize an executable in the temporary workspace.
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
        container_name = f"oj-run-{uuid.uuid4().hex}"
        command = self._build_command(request, container_name)
        started = time.monotonic()
        process: subprocess.Popen[bytes] | None = None

        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
            )
            if process.stdin is not None:
                try:
                    process.stdin.write(request.stdin.encode("utf-8"))
                    process.stdin.close()
                except BrokenPipeError:
                    process.stdin.close()

            stdout, stderr, output_limited, timed_out = self._collect_output(
                process,
                container_name,
                request,
                started,
            )
            return SandboxResult(
                exit_code=None if timed_out else process.returncode,
                stdout=stdout,
                stderr=stderr,
                execution_time_ms=self._elapsed_ms(started),
                timed_out=timed_out,
                output_limited=output_limited,
            )
        except OSError as exc:
            self._cleanup_container(container_name)
            if process is not None and process.poll() is None:
                process.kill()
                process.wait(timeout=1)
            return SandboxResult(
                exit_code=None,
                stdout="",
                stderr="",
                execution_time_ms=self._elapsed_ms(started),
                infrastructure_error=str(exc),
            )
        finally:
            self._cleanup_container(container_name)

    def _build_command(
        self, request: SandboxRequest, container_name: str
    ) -> list[str]:
        workspace_mode = "ro" if request.workspace_read_only else "rw"
        return [
            self._docker_binary,
            "run",
            "--rm",
            "--name",
            container_name,
            "--pull",
            "never",
            "--init",
            "-i",
            "--network",
            "none",
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges:true",
            "--security-opt",
            "seccomp=builtin",
            "--pids-limit",
            str(request.pids_limit),
            "--memory",
            f"{request.memory_limit_mb}m",
            "--memory-swap",
            f"{request.memory_limit_mb}m",
            "--cpus",
            str(request.cpus),
            "--user",
            "1000:1000",
            "--tmpfs",
            f"/tmp:rw,noexec,nosuid,nodev,size={MAX_WORKSPACE_BYTES}",
            "--mount",
            f"type=bind,src={request.workspace},dst=/workspace,{workspace_mode}",
            "-w",
            "/workspace",
            request.image,
            *request.command,
        ]

    def _collect_output(
        self,
        process: subprocess.Popen[bytes],
        container_name: str,
        request: SandboxRequest,
        started: float,
    ) -> tuple[str, str, bool, bool]:
        selector = selectors.DefaultSelector()
        if process.stdout is not None:
            selector.register(process.stdout, selectors.EVENT_READ, "stdout")
        if process.stderr is not None:
            selector.register(process.stderr, selectors.EVENT_READ, "stderr")

        buffers = {"stdout": bytearray(), "stderr": bytearray()}
        limits = {
            "stdout": request.stdout_limit_bytes,
            "stderr": request.stderr_limit_bytes,
        }
        output_limited = False
        timed_out = False

        try:
            while selector.get_map():
                remaining = request.timeout_ms / 1000 - (
                    time.monotonic() - started
                )
                if remaining <= 0:
                    timed_out = True
                    self._terminate_container(container_name, process)
                    break

                for key, _ in selector.select(timeout=min(remaining, 0.05)):
                    chunk = key.fileobj.read1(8192)
                    if not chunk:
                        selector.unregister(key.fileobj)
                        continue

                    stream = key.data
                    buffer = buffers[stream]
                    buffer.extend(chunk)
                    if len(buffer) > limits[stream]:
                        del buffer[limits[stream] :]
                        output_limited = True
                        self._terminate_container(container_name, process)
                        selector.close()
                        return (
                            self._decode(buffers["stdout"]),
                            self._decode(buffers["stderr"]),
                            True,
                            False,
                        )

                if process.poll() is not None:
                    for key, _ in selector.select(timeout=0):
                        chunk = key.fileobj.read1(8192)
                        if not chunk:
                            selector.unregister(key.fileobj)
                            continue
                        stream = key.data
                        buffer = buffers[stream]
                        remaining_limit = limits[stream] - len(buffer)
                        if remaining_limit <= 0:
                            output_limited = True
                            continue
                        buffer.extend(chunk[:remaining_limit])
                        if len(chunk) > remaining_limit:
                            output_limited = True
                    break
        finally:
            selector.close()

        if process.poll() is None:
            process.wait(timeout=1)

        return (
            self._decode(buffers["stdout"]),
            self._decode(buffers["stderr"]),
            output_limited,
            timed_out,
        )

    def _terminate_container(
        self, container_name: str, process: subprocess.Popen[bytes]
    ) -> None:
        self._cleanup_container(container_name)
        if process.poll() is None:
            process.kill()
            process.wait(timeout=1)

    def _cleanup_container(self, container_name: str) -> None:
        try:
            subprocess.run(
                [self._docker_binary, "rm", "-f", container_name],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass

    @staticmethod
    def _validate_request(request: SandboxRequest) -> None:
        if not request.command:
            raise ValueError("sandbox command must not be empty")
        if request.timeout_ms <= 0 or request.timeout_ms > MAX_EXECUTION_TIME_MS:
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

    @staticmethod
    def _decode(buffer: bytearray) -> str:
        return bytes(buffer).decode("utf-8", errors="replace")

    @staticmethod
    def _elapsed_ms(started: float) -> int:
        return int((time.monotonic() - started) * 1000)


class SandboxWorkspace:
    """Create and clean a per-execution temporary workspace."""

    def __enter__(self) -> Path:
        self._temporary_directory = tempfile.TemporaryDirectory(
            prefix="online-judge-run-"
        )
        return Path(self._temporary_directory.name)

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._temporary_directory.cleanup()
