import sys; a=list(map(int,sys.stdin.buffer.read().split())); x=a[1:]; o=[0]*len(x); st=[]
for i,v in enumerate(x):
 while st and x[st[-1]]<v: j=st.pop();o[j]=i-j
 st.append(i)
print(*o)
