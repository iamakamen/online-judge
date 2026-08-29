import sys

def main() -> None:
    value = sys.stdin.buffer.read().decode().rstrip("\\n")

    # TODO: maintain a sliding window of distinct characters.
    print(0)

if __name__ == "__main__":
    main()
