import sys

def main() -> None:
    value = sys.stdin.buffer.read().decode().strip()

    # TODO: expand around candidate centers and apply the tie rule.
    print()

if __name__ == "__main__":
    main()
