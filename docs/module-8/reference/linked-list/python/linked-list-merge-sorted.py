import sys; a=list(map(int,sys.stdin.buffer.read().split())); n,m=a[:2]; x=a[2:2+n]; y=a[2+n:2+n+m]; print(*(sorted(x+y)))
