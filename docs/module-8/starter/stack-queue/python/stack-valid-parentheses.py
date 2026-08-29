import sys

def main() -> None:
    value = sys.stdin.buffer.read().decode().strip()

    # TODO: validate delimiter nesting with a stack.
    print("false")

if __name__ == "__main__":
    main()
