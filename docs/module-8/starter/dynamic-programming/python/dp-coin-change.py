import sys

def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    m, amount = data[0], data[1]
    coins = data[2:2 + m]

    # TODO: compute the minimum number of reusable coins.
    print(-1)

if __name__ == "__main__":
    main()
