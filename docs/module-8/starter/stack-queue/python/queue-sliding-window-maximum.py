import sys

def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n, k = data[0], data[1]
    values = data[2:2 + n]

    # TODO: maintain a deque of candidate maximum indices.
    print(*([0] * (n - k + 1)))

if __name__ == "__main__":
    main()
