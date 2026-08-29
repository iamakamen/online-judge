import sys; s=sys.stdin.buffer.read().decode(); st=[]; p={')':'(',']':'[','}':'{'}
for c in s:
 if c in '([{': st.append(c)
 elif c in p and (not st or st.pop()!=p[c]): print('false'); break
else: print(str(not st).lower())
