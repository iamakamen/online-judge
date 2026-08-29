import sys

def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n, target = data[0], data[1]
    values = data[2:2 + n]

    # TODO: implement the complement lookup algorithm.
    print("0 1")

if __name__ == "__main__":
    main()
