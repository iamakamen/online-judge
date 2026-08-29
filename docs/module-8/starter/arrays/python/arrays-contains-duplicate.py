import sys

def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    values = data[1:1 + n]

    # TODO: detect whether any value occurs more than once.
    print("false")

if __name__ == "__main__":
    main()
