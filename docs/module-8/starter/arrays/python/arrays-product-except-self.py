import sys

def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    values = data[1:1 + n]

    # TODO: build products without using division.
    print(*([0] * n))

if __name__ == "__main__":
    main()
