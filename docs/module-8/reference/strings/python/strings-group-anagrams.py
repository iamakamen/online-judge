import sys; a=sys.stdin.buffer.read().decode().split(); n=int(a[0]); d={}
for w in a[1:]: d.setdefault(''.join(sorted(w)),[]).append(w)
for g in sorted((sorted(v) for v in d.values()),key=lambda v:v[0]): print(*g)
