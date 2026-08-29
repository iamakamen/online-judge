import sys

def main() -> None:
    tokens = sys.stdin.buffer.read().decode().split()
    value = tokens[0]
    m = int(tokens[1])
    words = tokens[2:2 + m]

    # TODO: determine whether the string can be segmented using the dictionary.
    print("false")

if __name__ == "__main__":
    main()
