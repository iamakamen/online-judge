import sys,collections; a=list(map(int,sys.stdin.buffer.read().split())); n,k=a[:2];x=a[2:];d=collections.deque();o=[]
for i,v in enumerate(x):
 while d and d[0]<=i-k:d.popleft()
 while d and x[d[-1]]<=v:d.pop()
 d.append(i)
 if i>=k-1:o.append(x[d[0]])
print(*o)
