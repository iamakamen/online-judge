import sys

def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    temperatures = data[1:1 + n]

    # TODO: resolve each next warmer day with a monotonic stack.
    print(*([0] * n))

if __name__ == "__main__":
    main()
