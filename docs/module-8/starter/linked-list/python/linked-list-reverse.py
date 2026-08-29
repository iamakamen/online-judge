import sys

def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    values = data[1:1 + n]

    # TODO: reverse the serialized linked list.
    print(*values)

if __name__ == "__main__":
    main()
