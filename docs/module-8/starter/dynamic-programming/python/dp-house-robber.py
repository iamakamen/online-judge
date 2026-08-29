import sys

def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    amounts = data[1:1 + n]

    # TODO: maximize the sum of non-adjacent house values.
    print(0)

if __name__ == "__main__":
    main()
