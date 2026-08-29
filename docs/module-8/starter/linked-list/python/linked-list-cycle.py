import sys

def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n, entry = data[0], data[1]
    values = data[2:2 + n]

    # TODO: detect whether the encoded list contains a cycle.
    print("false")

if __name__ == "__main__":
    main()
