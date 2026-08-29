import sys

def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    values = data[1:1 + n]

    # TODO: compute the maximum sum of a non-empty contiguous subarray.
    print(0)

if __name__ == "__main__":
    main()
