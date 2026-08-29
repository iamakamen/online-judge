import sys

def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n, k = data[0], data[1]
    values = data[2:2 + n]

    # TODO: remove the kth node from the end.
    print(*values)

if __name__ == "__main__":
    main()
