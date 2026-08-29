import sys

def main() -> None:
    lines = sys.stdin.buffer.read().decode().splitlines()
    q = int(lines[0])
    operations = lines[1:1 + q]
    answers = []

    for operation in operations:
        parts = operation.split()
        if parts and parts[0] in {"top", "min"}:
            answers.append("0")

    # TODO: maintain stack values and answer top/min queries.
    print("\\n".join(answers))

if __name__ == "__main__":
    main()
