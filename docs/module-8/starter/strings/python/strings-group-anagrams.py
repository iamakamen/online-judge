import sys

def main() -> None:
    tokens = sys.stdin.buffer.read().decode().split()
    n = int(tokens[0])
    words = tokens[1:1 + n]

    # TODO: group words by a deterministic anagram key.
    print()

if __name__ == "__main__":
    main()
