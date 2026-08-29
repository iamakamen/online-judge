import sys; a=list(map(int,sys.stdin.buffer.read().split()));x=a[1:];p=q=0
for v in x:p,q=q,max(q,p+v)
print(q)
