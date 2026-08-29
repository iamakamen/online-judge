import sys

def main() -> None:
    tokens = sys.stdin.buffer.read().decode().split()
    n = int(tokens[0])
    expression = tokens[1:1 + n]

    # TODO: evaluate the valid postfix expression with truncating division.
    print(0)

if __name__ == "__main__":
    main()
