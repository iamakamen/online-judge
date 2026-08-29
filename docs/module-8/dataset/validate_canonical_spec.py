#!/usr/bin/env python3
"""Read-only validator for canonical-problem-spec-v0.md."""
from __future__ import annotations
import json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).parent
SPEC = ROOT / "canonical-problem-spec-v0.md"
JSON_OUT = ROOT / "canonical-problem-validation-v0.json"
MD_OUT = ROOT / "canonical-problem-validation-v0.md"

def table_decode(s):
    return s.replace("\\\\n", "\n")

def code_decode(s):
    """Decode statement line breaks outside quoted source strings."""
    out=[]; quote=None; esc=False; i=0
    while i<len(s):
        c=s[i]
        if quote:
            out.append(c)
            if esc: esc=False
            elif c=='\\\\': esc=True
            elif c==quote: quote=None
            i+=1; continue
        if c in "'\"": quote=c; out.append(c); i+=1
        elif s.startswith("\\n",i): out.append("\n"); i+=2
        elif s.startswith("\\\\n",i): out.append("\n"); i+=3
        else: out.append(c); i+=1
    return ''.join(out)

def extract_code(s, lang):
    if lang=='py':
        f=re.search(r"\*\*Python[^:]*:\*\*\s*\n```python\n(.*?)\n```",s,re.S)
        q=re.search(r"\*\*Python(?: 3\.12 reference)?(?::)?\*\*:?\s*`(.*?)`",s,re.S)
    else:
        f=re.search(r"\*\*C\+\+17[^:]*:\*\*\s*\n```cpp\n(.*?)\n```",s,re.S)
        q=re.search(r"\*\*C\+\+17(?::)?\*\*:?\s*`(.*?)`",s,re.S)
    return f.group(1) if f else (code_decode(q.group(1)) if q else None)

def parse():
    text=SPEC.read_text(); out=[]
    for s in re.split(r"(?=^### )",text,flags=re.M)[1:]:
        h=re.match(r"### (\S+) — (.+)\n",s)
        if not h: continue
        ident,title=h.groups(); sl=re.search(r"\*\*Slug:\*\*\s*`([^`]+)`",s)
        tp=re.search(r"\*\*Topic:\*\*\s*([^;]+)",s); df=re.search(r"\*\*Difficulty:\*\*\s*([^\.]+)",s)
        cases=[]
        for m in re.finditer(r"^\| (P[12]|H[1-8]) \| `(.*?)` \| (?:`([^`]*)`|\*\(empty\)\*) \| (.*?) \|$",s,re.M):
            cases.append({'case':m.group(1),'input':table_decode(m.group(2)),'expected':table_decode(m.group(3) or ''),'purpose':m.group(4)})
        out.append({'identifier':ident,'title':title,'slug':sl.group(1) if sl else None,'topic':tp.group(1).strip() if tp else None,'difficulty':df.group(1).strip() if df else None,'constraints':next((x for x in s.splitlines() if x.startswith('- **Constraints:**')),None),'python':extract_code(s,'py'),'cpp':extract_code(s,'cpp'),'cases':cases})
    return out

def ints(s): return list(map(int,s.split()))
def bad(p, text):
    """Explicit input-contract validation; returns diagnostics."""
    z=p['slug']; e=[]
    try:
        if z=='arrays-two-sum':
            a=ints(text); n,t=a[:2]; x=a[2:]
            if len(x)!=n: e+=['array length != n']
            if not 2<=n<=100000: e+=['n out of range']
            if any(not -10**9<=v<=10**9 for v in x+[t]): e+=['value out of range']
            if sum(x[i]+x[j]==t for i in range(n) for j in range(i+1,n))!=1:e+=['not exactly one pair']
        elif z in {'arrays-best-time-stock','arrays-contains-duplicate','arrays-maximum-subarray'}:
            a=ints(text); n=a[0]; x=a[1:]; lo,hi=(0,100000) if z=='arrays-best-time-stock' else ((-10**9,10**9) if z=='arrays-contains-duplicate' else (-10000,10000))
            if len(x)!=n:e+=['array length != n']
            if not 1<=n<=100000:e+=['n out of range']
            if any(not lo<=v<=hi for v in x):e+=['value out of range']
        elif z=='arrays-product-except-self':
            a=ints(text);n=a[0];x=a[1:]
            if len(x)!=n or not 2<=n<=18:e+=['n/length invalid']
            if any(not -10<=v<=10 for v in x):e+=['value out of range']
        elif z in {'strings-valid-anagram','strings-valid-palindrome','strings-longest-unique-substring','strings-longest-palindromic-substring'}:
            x=text.split(); want=2 if z=='strings-valid-anagram' else 1; lim=2000 if z=='strings-longest-palindromic-substring' else 100000
            if len(x)!=want:e+=['wrong token count']
            if any(not 1<=len(v)<=lim or not re.fullmatch('[a-z]+',v) for v in x):e+=['string constraint violated']
        elif z=='strings-group-anagrams':
            a=text.split();n=int(a[0]);x=a[1:]
            if len(x)!=n or not 1<=n<=1000 or sum(map(len,x))>100000 or any(not re.fullmatch('[a-z]+',v) for v in x):e+=['word constraint violated']
        elif z=='linked-list-reverse':
            a=ints(text);n=a[0]
            if len(a)!=n+1 or not 0<=n<=100:e+=['list length invalid']
        elif z=='linked-list-merge-sorted':
            a=ints(text);n,m=a[:2];x=a[2:2+n];y=a[2+n:]
            if len(a)!=n+m+2 or not 0<=n<=100 or not 0<=m<=100:e+=['list lengths invalid']
            if x!=sorted(x) or y!=sorted(y):e+=['list not sorted']
        elif z=='linked-list-cycle':
            a=ints(text);n,k=a[:2]
            if len(a)!=n+2 or not 0<=n<=100 or not -1<=k<n:e+=['cycle serialization invalid']
        elif z=='linked-list-remove-nth-from-end':
            a=ints(text);n,k=a[:2]
            if len(a)!=n+2 or not 1<=k<=n<=100:e+=['length/k invalid']
        elif z=='linked-list-add-two-numbers':
            a=ints(text);n,m=a[:2];x=a[2:2+n];y=a[2+n:]
            if len(a)!=n+m+2 or not 1<=n<=100 or not 1<=m<=100 or any(not 0<=v<=9 for v in x+y):e+=['digit/list constraint violated']
        elif z=='stack-valid-parentheses':
            x=text.split()
            if len(x)!=1 or not 1<=len(x[0])<=100000 or any(c not in '()[]{}' for c in x[0]):e+=['bracket constraint violated']
        elif z=='stack-min-stack':
            ls=text.splitlines();q=int(ls[0]); ops=ls[1:]; size=0
            if len(ops)!=q or not 1<=q<=100000:e+=['operation count invalid']
            for line in ops:
                a=line.split()
                if not a or a[0] not in {'push','pop','top','min'}:e+=['unknown operation']
                elif a[0]=='push':
                    if len(a)!=2 or not -10**9<=int(a[1])<=10**9:e+=['push invalid']
                    size+=1
                elif a[0]=='pop': size-=1
                elif size<=0:e+=['operation on empty stack']
        elif z=='stack-evaluate-rpn':
            a=text.split();n=int(a[0]);d=0
            if len(a[1:])!=n or not 1<=n<=1000:e+=['token count invalid']
            for v in a[1:]:
                if v.lstrip('-').isdigit():d+=1
                elif v in '+-*/' and d>=2:d-=1
                else:e+=['invalid RPN']
            if d!=1:e+=['RPN result count invalid']
        elif z in {'stack-daily-temperatures','queue-sliding-window-maximum'}:
            a=ints(text);n=a[0];k=a[1] if z.startswith('queue-') else None;x=a[2:] if k is not None else a[1:]
            if not 1<=n<=100000 or len(x)!=n:e+=['array/n invalid']
            if k is not None and not 1<=k<=n:e+=['k invalid']
            if z.startswith('stack-') and any(not -100<=v<=100 for v in x):e+=['temperature out of range']
        elif z=='dp-climbing-stairs':
            if not 1<=int(text)<=45:e+=['n out of range']
        elif z=='dp-house-robber':
            a=ints(text);n=a[0];x=a[1:]
            if len(x)!=n or not 1<=n<=100000 or any(not 0<=v<=10000 for v in x):e+=['house constraint violated']
        elif z=='dp-coin-change':
            a=ints(text);m,A=a[:2];c=a[2:]
            if len(c)!=m or not 1<=m<=20 or not 1<=A<=10000 or any(v<=0 for v in c):e+=['coin constraint violated']
        elif z=='dp-longest-increasing-subsequence':
            a=ints(text);n=a[0];x=a[1:]
            if len(x)!=n or not 1<=n<=100000 or any(not -10**9<=v<=10**9 for v in x):e+=['LIS constraint violated']
        elif z=='dp-word-break':
            a=text.split();s=a[0];m=int(a[1]);w=a[2:]
            if len(w)!=m or not 1<=len(s)<=100 or not 1<=m<=50 or any(not 1<=len(v)<=20 for v in w):e+=['word-break constraint violated']
        else:e+=['no validator for slug']
    except (ValueError,IndexError,TypeError) as ex:e+=[f'malformed input: {ex}']
    return e

def invoke(cmd, data):
    try:
        p=subprocess.run(cmd,input=data,text=True,capture_output=True,timeout=2)
        return {'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'timeout':False}
    except subprocess.TimeoutExpired as ex:
        return {'exit_code':None,'stdout':ex.stdout or '','stderr':str(ex),'timeout':True}

def toks(s):return re.findall(r'\S+',s or '')

def main():
    ps=parse(); tmp=Path(tempfile.mkdtemp(prefix='canonical-validator-')); cases=[]; compile_fail=[]
    for p in ps:
        py=tmp/(p['identifier']+'.py'); cc=tmp/(p['identifier']+'.cpp'); exe=tmp/(p['identifier']+'.out')
        py_ok=cc_ok=False
        if p['python']:
            py.write_text(p['python']); q=subprocess.run([sys.executable,'-m','py_compile',str(py)],capture_output=True,text=True);py_ok=q.returncode==0;p['python_compile_stderr']=q.stderr
        if p['cpp']:
            cc.write_text(p['cpp']);q=subprocess.run(['g++','-std=c++17','-O2','-pipe',str(cc),'-o',str(exe)],capture_output=True,text=True,timeout=30);cc_ok=q.returncode==0;p['cpp_compile_stderr']=q.stderr
        p['python_compile']=py_ok;p['cpp_compile']=cc_ok
        if not cc_ok:compile_fail.append(p['identifier'])
        seen=set()
        for c in p['cases']:
            dup=(c['input'],c['expected']) in seen;seen.add((c['input'],c['expected']))
            vr=bad(p,c['input']); pr=invoke([sys.executable,str(py)],c['input']) if py_ok else {'exit_code':None,'stdout':'','stderr':'not compiled','timeout':False}; cr=invoke([str(exe)],c['input']) if cc_ok else {'exit_code':None,'stdout':'','stderr':'not compiled','timeout':False}
            pm=pr['exit_code']==0 and not pr['timeout'] and toks(pr['stdout'])==toks(c['expected']);cm=cr['exit_code']==0 and not cr['timeout'] and toks(cr['stdout'])==toks(c['expected']);xm=pm and cm and toks(pr['stdout'])==toks(cr['stdout'])
            cases.append({'problem':p['identifier'],'title':p['title'],'case':c['case'],'input':c['input'],'expected':c['expected'],'constraint_violations':vr,'duplicate':dup,'python':pr,'cpp':cr,'python_match':pm,'cpp_match':cm,'cross_match':xm})
    topic_counts={t:sum(p['topic']==t for p in ps) for t in sorted({p['topic'] for p in ps})}
    structural=[]
    if len(ps)!=25: structural.append(f'problem sections={len(ps)}, expected 25')
    if len(topic_counts)!=5: structural.append(f'topics={len(topic_counts)}, expected 5')
    if any(v!=5 for v in topic_counts.values()): structural.append(f'topic counts={topic_counts}, expected five each')
    if any(len(p['cases'])!=10 for p in ps): structural.append('one or more problems do not have 10 parsed cases')
    if any(sum(c['case'].startswith('P') for c in p['cases'])!=2 for p in ps): structural.append('one or more problems do not have two public cases')
    if any(sum(c['case'].startswith('H') for c in p['cases'])!=8 for p in ps): structural.append('one or more problems do not have eight hidden cases')
    if any(not p['slug'] for p in ps): structural.append('missing slug')
    if len({p['slug'] for p in ps})!=len(ps): structural.append('duplicate slug')
    if any(not p['python'] or not p['cpp'] for p in ps): structural.append('missing reference')
    summary={'problems':len(ps),'cases':len(cases),'python_executions':len(cases),'cpp_executions':len(cases),'python_matches':sum(x['python_match'] for x in cases),'cpp_matches':sum(x['cpp_match'] for x in cases),'cross_matches':sum(x['cross_match'] for x in cases),'constraint_violations':sum(bool(x['constraint_violations']) for x in cases),'malformed_cases':sum(any('malformed' in e for e in x['constraint_violations']) for x in cases),'python_failures':sum(x['python']['exit_code']!=0 or x['python']['timeout'] for x in cases),'cpp_failures':sum(x['cpp']['exit_code']!=0 or x['cpp']['timeout'] for x in cases),'timeouts':sum(x['python']['timeout'] or x['cpp']['timeout'] for x in cases),'compile_failures':compile_fail,'duplicate_pairs':sum(x['duplicate'] for x in cases),'topic_counts':topic_counts,'structural_failures':structural}
    JSON_OUT.write_text(json.dumps({'summary':summary,'problems':ps,'cases':cases},indent=2))
    lines=['# Canonical Problem Validation v0','','## SUMMARY','',f"- Problems: {summary['problems']}/25",f"- Cases: {summary['cases']}/250",f"- Python executions: {summary['python_executions']}",f"- C++ executions: {summary['cpp_executions']}",f"- Python expected-output matches: {summary['python_matches']}/250",f"- C++ expected-output matches: {summary['cpp_matches']}/250",f"- Python/C++ matches: {summary['cross_matches']}/250",f"- Constraint violations: {summary['constraint_violations']}",f"- Malformed cases: {summary['malformed_cases']}",f"- Python failures: {summary['python_failures']}",f"- C++ failures: {summary['cpp_failures']}",f"- C++ compilation failures: {len(summary['compile_failures'])}",f"- Timeouts: {summary['timeouts']}",f"- Duplicate pairs: {summary['duplicate_pairs']}",f"- Topic counts: {summary['topic_counts']}",f"- Structural failures: {summary['structural_failures']}",'','## Per-problem results','']
    for p in ps:
        cs=[x for x in cases if x['problem']==p['identifier']];lines += [f"### {p['identifier']} — {p['title']}",f"- cases: {len(cs)}/10; Python: {sum(x['python_match'] for x in cs)}/10; C++: {sum(x['cpp_match'] for x in cs)}/10; cross-language: {sum(x['cross_match'] for x in cs)}/10; constraint violations: {sum(bool(x['constraint_violations']) for x in cs)}"]
        for x in cs:
            if not (x['python_match'] and x['cpp_match'] and x['cross_match'] and not x['constraint_violations'] and not x['duplicate']):
                lines += [f"- **{x['case']} failure**",f"  - input: `{x['input']}`",f"  - expected: `{x['expected']}`",f"  - Python: exit={x['python']['exit_code']} timeout={x['python']['timeout']} stdout={x['python']['stdout']!r} stderr={x['python']['stderr']!r}",f"  - C++: exit={x['cpp']['exit_code']} timeout={x['cpp']['timeout']} stdout={x['cpp']['stdout']!r} stderr={x['cpp']['stderr']!r}",f"  - constraints: {x['constraint_violations'] or 'none'}; cross-match={x['cross_match']}"]
    MD_OUT.write_text('\n'.join(lines)+'\n');print(json.dumps(summary,indent=2));return 0 if summary['python_matches']==250 and summary['cpp_matches']==250 and summary['cross_matches']==250 and not any(summary[k] for k in ('constraint_violations','malformed_cases','python_failures','cpp_failures','timeouts','duplicate_pairs','compile_failures')) else 1

if __name__=='__main__':raise SystemExit(main())
