import sys


def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    values = data[1:1 + n]
    print("true" if len(set(values)) != n else "false")


if __name__ == "__main__":
    main()
