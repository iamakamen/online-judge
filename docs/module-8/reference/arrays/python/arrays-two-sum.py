import sys


def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n, target = data[0], data[1]
    values = data[2:2 + n]

    seen = {}
    for index, value in enumerate(values):
        complement = target - value
        if complement in seen:
            print(seen[complement], index)
            return
        seen[value] = index


if __name__ == "__main__":
    main()
