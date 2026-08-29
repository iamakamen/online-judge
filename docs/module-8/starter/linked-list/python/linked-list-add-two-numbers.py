import sys

def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n, m = data[0], data[1]
    first = data[2:2 + n]
    second = data[2 + n:2 + n + m]

    # TODO: add the two reverse-digit serialized numbers.
    print(*first)

if __name__ == "__main__":
    main()
