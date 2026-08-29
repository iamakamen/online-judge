import sys; s=sys.stdin.buffer.read().decode().strip(); best=(0,0)
for c in range(len(s)):
 for l,r in ((c,c),(c,c+1)):
  while l>=0 and r<len(s) and s[l]==s[r]:
   if r-l+1>best[1]-best[0]: best=(l,r+1)
   l-=1;r+=1
print(s[best[0]:best[1]])
