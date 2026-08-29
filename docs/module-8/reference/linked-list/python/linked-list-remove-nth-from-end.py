import sys; a=list(map(int,sys.stdin.buffer.read().split())); n,k=a[:2]; x=a[2:2+n]; del x[n-k]; print(*x)
