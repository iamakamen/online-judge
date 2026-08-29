import sys; s=sys.stdin.buffer.read().split()[0]; print(str(s==s[::-1]).lower())
