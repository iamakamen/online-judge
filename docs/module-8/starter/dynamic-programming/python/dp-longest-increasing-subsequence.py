import sys

def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    values = data[1:1 + n]

    # TODO: compute the length of a strictly increasing subsequence.
    print(0)

if __name__ == "__main__":
    main()
