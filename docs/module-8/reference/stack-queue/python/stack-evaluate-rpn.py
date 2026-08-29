import sys; a=sys.stdin.buffer.read().decode().split(); st=[]
for t in a[1:]:
 if t.lstrip('-').isdigit(): st.append(int(t))
 else:
  b,x=st.pop(),st.pop()
  if t=='+': st.append(x+b)
  elif t=='-': st.append(x-b)
  elif t=='*': st.append(x*b)
  else: st.append((abs(x)//abs(b))*(-1 if x*b<0 else 1))
print(st[-1])
