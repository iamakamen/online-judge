import sys


def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    values = data[1:1 + n]

    result = [1] * n
    prefix = 1
    for i, value in enumerate(values):
        result[i] = prefix
        prefix *= value

    suffix = 1
    for i in range(n - 1, -1, -1):
        result[i] *= suffix
        suffix *= values[i]

    print(*result)


if __name__ == "__main__":
    main()
