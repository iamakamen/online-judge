import sys; a=list(map(int,sys.stdin.buffer.read().split())); n,m=a[:2]; x=a[2:2+n]; y=a[2+n:2+n+m]; o=[];c=0
for i in range(max(n,m)):
 q=(x[i] if i<n else 0)+(y[i] if i<m else 0)+c;o.append(q%10);c=q//10
if c:o.append(c)
while len(o)>1 and o[-1]==0:o.pop()
print(*o)
