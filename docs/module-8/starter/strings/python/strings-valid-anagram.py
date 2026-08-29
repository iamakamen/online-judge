import sys

def main() -> None:
    tokens = sys.stdin.buffer.read().decode().split()
    s, t = tokens[0], tokens[1]

    # TODO: compare the character frequencies of both strings.
    print("false")

if __name__ == "__main__":
    main()
