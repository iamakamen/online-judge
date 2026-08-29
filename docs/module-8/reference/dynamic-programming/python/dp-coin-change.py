import sys; a=list(map(int,sys.stdin.buffer.read().split()));m,A=a[:2];c=a[2:];d=[A+1]*(A+1);d[0]=0
for x in range(1,A+1):d[x]=min((d[x-v]+1 for v in c if v<=x),default=A+1)
print(-1 if d[A]>A else d[A])
