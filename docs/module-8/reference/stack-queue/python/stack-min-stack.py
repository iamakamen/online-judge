import sys; a=sys.stdin.buffer.read().decode().splitlines(); st=[]; out=[]
for z in a[1:]:
 p=z.split();
 if p[0]=='push': st.append(int(p[1]))
 elif p[0]=='pop': st.pop()
 elif p[0]=='top': out.append(str(st[-1]))
 else: out.append(str(min(st)))
print('\n'.join(out))
