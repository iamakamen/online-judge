import sys

def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n, m = data[0], data[1]
    left = data[2:2 + n]
    right = data[2 + n:2 + n + m]

    # TODO: merge both nondecreasing lists.
    print(*left)

if __name__ == "__main__":
    main()
