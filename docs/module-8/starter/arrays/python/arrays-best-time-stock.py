import sys

def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    prices = data[1:1 + n]

    # TODO: track the minimum price and maximum achievable profit.
    print(0)

if __name__ == "__main__":
    main()
