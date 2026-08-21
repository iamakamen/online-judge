import os

import pytest

from backend.app.core.execution import MAX_STDOUT_BYTES
from backend.app.services.execution.cpp_runner import CppRunner
from backend.app.services.execution.models import ExecutionRequest, ExecutionStatus


CPP_IMAGE = os.getenv("CPP_TEST_IMAGE", "online-judge-run-cpp:17")


@pytest.fixture(scope="module")
def runner():
    return CppRunner()


def request(source_code: str, stdin: str = "", timeout_ms: int = 2_000):
    return ExecutionRequest(
        source_code=source_code,
        stdin=stdin,
        time_limit_ms=timeout_ms,
        memory_limit_mb=64,
    )


def test_cpp17_runner_executes_source_and_passes_stdin(runner):
    result = runner.execute(
        request(
            "#include <iostream>\n"
            "#include <string>\n"
            "int main() { std::string s; std::getline(std::cin, s); "
            "std::cout << s << '\\n'; }\n",
            stdin="hello cpp\n",
        )
    )

    assert result.status is ExecutionStatus.PASSED
    assert result.stdout == "hello cpp\n"
    assert result.stderr == ""
    assert result.exit_code == 0


def test_cpp17_compile_error_is_reported(runner):
    result = runner.execute(
        request("int main() { this is not valid C++; }\n")
    )

    assert result.status is ExecutionStatus.COMPILE_ERROR
    assert result.exit_code != 0
    assert result.stderr


def test_cpp_runtime_error_is_reported(runner):
    result = runner.execute(
        request("int main() { return 7; }\n")
    )

    assert result.status is ExecutionStatus.RUNTIME_ERROR
    assert result.exit_code == 7


def test_cpp_timeout_is_reported(runner):
    result = runner.execute(
        request("int main() { for (;;) {} }\n", timeout_ms=500)
    )

    assert result.status is ExecutionStatus.TIME_LIMIT_EXCEEDED
    assert result.exit_code is None


def test_cpp_output_limit_is_reported(runner):
    result = runner.execute(
        request(
            "#include <iostream>\n"
            "int main() { for (;;) std::cout << 'x'; }\n"
        )
    )

    assert result.status is ExecutionStatus.OUTPUT_LIMIT_EXCEEDED
    assert len(result.stdout.encode("utf-8")) <= MAX_STDOUT_BYTES


def test_cpp_memory_limit_is_reported(runner):
    result = runner.execute(
        request(
            "#include <cstddef>\n"
            "int main() {\n"
            "  const std::size_t size = 128ULL * 1024 * 1024;\n"
            "  volatile char* data = new char[size];\n"
            "  for (std::size_t i = 0; i < size; i += 4096) data[i] = 1;\n"
            "  return 0;\n"
            "}\n"
        )
    )

    assert result.status is ExecutionStatus.MEMORY_LIMIT_EXCEEDED
    assert result.exit_code != 0


def test_cpp_runtime_workspace_is_read_only(runner):
    source = (
        "#include <fstream>\n"
        "int main() { "
        "std::ofstream f(\"/workspace/blocked.txt\"); "
        "if (!f) return 7; "
        "f << \"executed\"; "
        "return 0; "
        "}\n"
    )

    result = runner.execute(request(source))

    assert result.status is ExecutionStatus.RUNTIME_ERROR
    assert result.exit_code == 7


def test_cpp_network_is_disabled(runner):
    source = (
        "#include <arpa/inet.h>\n"
        "#include <sys/socket.h>\n"
        "int main() {\n"
        "  int fd = socket(AF_INET, SOCK_STREAM, 0);\n"
        "  sockaddr_in addr{};\n"
        "  addr.sin_family = AF_INET;\n"
        "  addr.sin_port = htons(80);\n"
        "  inet_pton(AF_INET, \"1.1.1.1\", &addr.sin_addr);\n"
        "  int rc = connect(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr));\n"
        "  return rc == 0 ? 0 : 1;\n"
        "}\n"
    )

    result = runner.execute(request(source, timeout_ms=1_000))

    assert result.status is ExecutionStatus.RUNTIME_ERROR
    assert result.exit_code != 0
