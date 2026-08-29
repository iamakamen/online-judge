import sys


def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    prices = data[1:1 + n]

    minimum = prices[0]
    best = 0
    for price in prices[1:]:
        best = max(best, price - minimum)
        minimum = min(minimum, price)
    print(best)


if __name__ == "__main__":
    main()
