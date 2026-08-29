import sys; a=list(map(int,sys.stdin.buffer.read().split())); n,e=a[:2]; nxt=list(range(1,n))+[-1] if n else []
if n and e>=0:nxt[-1]=e
slow=fast=0; ok=False
while n and fast!=-1 and nxt[fast]!=-1:
 slow=nxt[slow]; fast=nxt[nxt[fast]]
 if slow==fast:ok=True;break
print(str(ok).lower())
