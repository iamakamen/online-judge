from pathlib import Path

from backend.app.services.execution.models import ExecutionRequest, ExecutionStatus
from backend.app.services.execution.python_runner import PythonRunner
from backend.app.services.execution.sandbox import SandboxExecutor


IMAGE = "online-judge-run-python:3.12"


def request(source_code: str, stdin: str = "", timeout_ms: int = 2_000) -> ExecutionRequest:
    return ExecutionRequest(
        source_code=source_code,
        stdin=stdin,
        time_limit_ms=timeout_ms,
        memory_limit_mb=64,
    )


def test_python_runner_executes_source_and_passes_stdin():
    runner = PythonRunner()
    result = runner.execute(
        request(
            "import sys\nprint(sys.stdin.read().strip().upper())\n",
            stdin="hello python\n",
        )
    )

    assert result.status is ExecutionStatus.PASSED
    assert result.stdout == "HELLO PYTHON\n"
    assert result.stderr == ""
    assert result.exit_code == 0


def test_python_runner_maps_runtime_error():
    result = PythonRunner().execute(request("raise ValueError('boom')\n"))

    assert result.status is ExecutionStatus.RUNTIME_ERROR
    assert result.exit_code != 0
    assert "ValueError" in result.stderr


def test_python_runner_maps_timeout():
    result = PythonRunner().execute(
        request("while True:\n    pass\n", timeout_ms=500)
    )

    assert result.status is ExecutionStatus.TIME_LIMIT_EXCEEDED
    assert result.exit_code is None


def test_python_runner_maps_output_limit():
    result = PythonRunner().execute(
        request("print('x' * 100_000)\n")
    )

    assert result.status is ExecutionStatus.OUTPUT_LIMIT_EXCEEDED
    assert len(result.stdout.encode("utf-8")) <= 64_000


def test_python_runner_does_not_execute_on_host(tmp_path):
    marker = tmp_path / "host-marker"
    source = (
        "from pathlib import Path\n"
        f"Path({str(marker)!r}).write_text('executed')\n"
    )

    result = PythonRunner().execute(request(source))

    assert result.status is ExecutionStatus.RUNTIME_ERROR
    assert result.exit_code != 0
    assert not marker.exists()
