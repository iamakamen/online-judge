import sys

def main() -> None:
    value = sys.stdin.buffer.read().decode().strip()

    # TODO: normalize the input and check it from both ends.
    print("false")

if __name__ == "__main__":
    main()
