import sys; s=sys.stdin.buffer.read().split()[0]; last={}; l=ans=0
for r,c in enumerate(s):
 l=max(l,last.get(c,-1)+1); last[c]=r; ans=max(ans,r-l+1)
print(ans)
