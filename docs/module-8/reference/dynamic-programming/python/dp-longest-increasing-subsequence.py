import sys,bisect; a=list(map(int,sys.stdin.buffer.read().split()));t=[]
for x in a[1:]:i=bisect.bisect_left(t,x);t[i:i+1]=[x] if i==len(t) else [x]
print(len(t))
