import sys; a=sys.stdin.buffer.read().decode().split();s=a[0];m=int(a[1]);w=a[2:2+m];d=[False]*(len(s)+1);d[0]=True
for i in range(len(s)):
 if d[i]:
  for z in w:
   if s.startswith(z,i):d[i+len(z)]=True
print(str(d[-1]).lower())
