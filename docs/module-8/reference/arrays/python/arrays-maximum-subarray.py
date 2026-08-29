import sys


def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    values = data[1:1 + n]

    current = best = values[0]
    for value in values[1:]:
        current = max(value, current + value)
        best = max(best, current)
    print(best)


if __name__ == "__main__":
    main()
