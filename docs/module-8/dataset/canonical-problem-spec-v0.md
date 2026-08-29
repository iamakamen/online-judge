# Module 8 Canonical Problem Specification v0

This is an authored V1 design artifact. It does not use the rejected
CodeContests representation and does not modify seed data.

## Shared V1 rules

- Every program is a standalone Python 3.12 or C++17 executable.
- Input is read from stdin and output is written to stdout.
- Arrays are serialized as `n` followed by one line of `n` values.
- Boolean output is the lowercase word `true` or `false`.
- Lists of integers are printed space-separated on one line. An empty list
  is printed as an empty line.
- Each problem has exactly the ten cases in its table: P1/P2 are public Run
  cases; H1–H8 are hidden Submit cases.
- Every case is an independent process invocation.
- All output comparisons are ordinary whitespace-token comparisons.
- In the tables, the two-character notation `\\n` means an actual newline in
  the submitted stdin; it is not a literal backslash-n token.
- Proposed problem limits are explicit and deterministic: Easy problems use
  `1000 ms` and `128 MB`; Medium problems use `1500 ms` and `256 MB`. These
  are problem-level values to be written into the canonical records, not
  executor defaults.

## 1. Arrays

### A1 — Two Sum

- **Slug:** `arrays-two-sum`; **Topic:** Arrays; **Difficulty:** Easy.
- **Tags:** Hash Map; Complement Lookup; Index Tracking.
- **Time limit:** 1000 ms. **Memory limit:** 128 MB.

**Example 1**

Input:
```text
4 9
2 7 11 15
```
Output: `0 1`
Explanation: `2+7=9`, and the indices are ascending.

**Example 2**

Input:
```text
4 6
3 3 1 4
```
Output: `0 1`
Explanation: The equal values at indices 0 and 1 are the unique valid pair.
- **Learning objective:** Use a hash map for one-pass complement lookup.
- **Statement:** Given an array and a target, exactly one pair of distinct
  elements sums to the target. Output their zero-based indices in ascending
  order.
- **Input:** `n target`, then `a1 ... an`.
- **Output:** `i j`.
- **Constraints:** `2≤n≤100000`, `-10^9≤ai,target≤10^9`; exactly one pair.
- **Edge cases:** pair at the ends, duplicate values, negative values, and a
  pair discovered late in the scan.
- **Approach/complexity:** Store value→index; O(n) time, O(n) auxiliary space.
- **Judging:** Safe ordinary token judging; no special behavior.

Tests (inputs are shown with `\\n` line breaks):

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `4 9\\n2 7 11 15` | `0 1` | public basic pair |
| P2 | `4 6\\n3 3 1 4` | `0 1` | public duplicate values |
| H1 | `2 0\\n-5 5` | `0 1` | minimum n/negative pair |
| H2 | `5 10\\n1 2 3 4 9` | `0 4` | late complement |
| H3 | `6 -3\\n4 -7 8 1 -2 9` | `0 1` | negative target |
| H4 | `6 14\\n9 8 5 7 1 12` | `0 2` | non-adjacent pair |
| H5 | `7 1000000000\\n-1 100 999999900 4 8 12 16` | `1 2` | large target |
| H6 | `8 5\\n0 0 0 1 2 4 -2 9` | `3 5` | repeated candidates |
| H7 | `9 -10\\n3 7 -4 -6 8 2 1 20 5` | `2 3` | negative pair |
| H8 | `10 28\\n1 4 6 8 10 12 13 14 16 7` | `5 8` | late pair |

**Python 3.12 reference:**

```python
import sys
a=list(map(int,sys.stdin.buffer.read().split())); n,t=a[0],a[1]; seen={}
for i,x in enumerate(a[2:]):
    if t-x in seen: print(seen[t-x],i); break
    seen[x]=i
```

**C++17 reference:**

```cpp
#include <bits/stdc++.h>
using namespace std; int main(){ios::sync_with_stdio(false);cin.tie(nullptr);int n; long long t; if(!(cin>>n>>t))return 0; unordered_map<long long,int> m; for(int i=0;i<n;i++){long long x;cin>>x;if(m.count(t-x)){cout<<m[t-x]<<' '<<i<<'\n';return 0;}m[x]=i;}}
```

### A2 — Best Time to Buy and Sell Stock

- **Slug:** `arrays-best-time-stock`; **Topic:** Arrays; **Difficulty:** Easy.
- **Tags:** Greedy; Prefix Minimum; Array Scan.
- **Time limit:** 1000 ms. **Memory limit:** 128 MB.

**Example 1**

Input:
```text
6
7 1 5 3 6 4
```
Output: `5`
Explanation: Buy at 1 and sell at 6.

**Example 2**

Input:
```text
5
7 6 4 3 1
```
Output: `0`
Explanation: No later price is higher than an earlier price.
- **Learning objective:** Track the minimum prefix price while scanning once.
- **Statement:** Choose at most one buy day followed by a later sell day.
  Return the maximum non-negative profit.
- **Input:** `n`, then `p1 ... pn`.
- **Output:** One integer `maximum_profit`.
- **Constraints:** `1≤n≤100000`, `0≤pi≤100000`.
- **Edge cases:** one day, decreasing prices, equal prices, and the best sale
  at the final day.
- **Approach/complexity:** Minimum-so-far and best profit; O(n) time, O(1)
  auxiliary space.
- **Judging:** Safe ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `6\\n7 1 5 3 6 4` | `5` | public standard case |
| P2 | `5\\n7 6 4 3 1` | `0` | public decreasing case |
| H1 | `1\\n9` | `0` | minimum n |
| H2 | `2\\n1 10` | `9` | minimum profitable pair |
| H3 | `6\\n2 2 2 2 2 2` | `0` | equal prices |
| H4 | `6\\n10 1 2 3 4 5` | `4` | delayed recovery |
| H5 | `5\\n1 2 3 4 100` | `99` | final-day maximum |
| H6 | `7\\n100000 0 99999 1 99998 2 3` | `99999` | maximum bounds |
| H7 | `6\\n5 4 3 2 8 1` | `6` | sale before later drop |
| H8 | `8\\n3 8 2 5 1 7 0 6` | `6` | multiple local peaks |

**Python:** `import sys; a=list(map(int,sys.stdin.buffer.read().split())); p=a[1:]; lo=p[0]; best=0\nfor x in p[1:]: best=max(best,x-lo); lo=min(lo,x)\nprint(best)`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std; int main(){int n;cin>>n; long long x,lo=LLONG_MAX,b=0;while(n--){cin>>x;lo=min(lo,x);b=max(b,x-lo);}cout<<b<<'\n';}`

The Python expression is intentionally a complete standalone reference: it
updates the minimum when the profit expression is zero as well as when it is
positive. It should be replaced by a conventional loop if seed tooling rejects
compact expressions; the semantics are fixed by the cases above.

### A3 — Contains Duplicate

- **Slug:** `arrays-contains-duplicate`; **Topic:** Arrays; **Difficulty:** Easy.
- **Tags:** Hash Set; Membership Testing; Deduplication.
- **Time limit:** 1000 ms. **Memory limit:** 128 MB.

**Example 1**

Input:
```text
4
1 2 3 1
```
Output: `true`
Explanation: The value 1 occurs twice.

**Example 2**

Input:
```text
4
1 2 3 4
```
Output: `false`
Explanation: Every value occurs exactly once.
- **Learning objective:** Use set membership to detect repetition.
- **Statement:** Report whether any value occurs at least twice.
- **Input:** `n`, then `a1 ... an`.
- **Output:** `true` or `false`.
- **Constraints:** `1≤n≤100000`, `-10^9≤ai≤10^9`.
- **Approach/complexity:** Hash set; O(n) expected time and O(n) auxiliary space.
- **Edge cases:** singleton, duplicate first/last, all equal, negatives.
- **Judging:** Safe ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `4\\n1 2 3 1` | `true` | public repeated value |
| P2 | `4\\n1 2 3 4` | `false` | public all unique |
| H1 | `1\\n-7` | `false` | minimum n/negative |
| H2 | `2\\n5 5` | `true` | minimum duplicate |
| H3 | `6\\n0 0 0 0 0 0` | `true` | all equal |
| H4 | `6\\n-1 -2 -3 -4 -5 -6` | `false` | negative unique |
| H5 | `7\\n1 2 3 4 5 6 1` | `true` | duplicate at end |
| H6 | `8\\n1000000000 0 -1000000000 3 4 5 6 7` | `false` | bounds |
| H7 | `9\\n2 4 6 8 10 12 14 16 18` | `false` | larger unique set |
| H8 | `10\\n9 8 7 6 5 4 3 2 1 9` | `true` | late repeated value |

**Python:** `import sys; a=list(map(int,sys.stdin.buffer.read().split())); print(str(len(set(a[1:]))!=a[0]).lower())`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std; int main(){int n;cin>>n;set<long long>s;bool d=false;for(int i=0;i<n;i++){long long x;cin>>x;d|=!s.insert(x).second;}cout<<(d?"true":"false")<<'\n';}`

### A4 — Product of Array Except Self

- **Slug:** `arrays-product-except-self`; **Topic:** Arrays; **Difficulty:** Medium.
- **Tags:** Prefix Product; Suffix Product; Zero Handling.
- **Time limit:** 1500 ms. **Memory limit:** 256 MB.

**Example 1**

Input:
```text
4
1 2 3 4
```
Output: `24 12 8 6`
Explanation: Each output is the product of the other three values.

**Example 2**

Input:
```text
4
-1 1 0 -3
```
Output: `0 0 3 0`
Explanation: Every product except the zero position includes a zero.
- **Learning objective:** Combine prefix and suffix products without division.
- **Statement:** For each position output the product of every input value except
  the value at that position.
- **Input:** `n`, then `a1 ... an`.
- **Output:** `n` signed 64-bit integers `b1 ... bn`.
- **Constraints:** `2≤n≤18`, `-10≤ai≤10`; division is prohibited; results fit
  signed 64-bit.
- **Approach/complexity:** Prefix output followed by a suffix scan; O(n) time,
  O(1) auxiliary space excluding the output array.
- **Edge cases:** zeros, two elements, negatives, and all negative values.
- **Judging:** Safe ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `4\\n1 2 3 4` | `24 12 8 6` | public standard case |
| P2 | `4\\n-1 1 0 -3` | `0 0 3 0` | public one-zero case |
| H1 | `2\\n5 -2` | `-2 5` | minimum n/negative |
| H2 | `3\\n0 0 7` | `0 0 0` | two zeros |
| H3 | `5\\n1 0 2 0 4` | `0 0 0 0 0` | multiple zeros |
| H4 | `3\\n-2 -3 -4` | `12 8 6` | all negative |
| H5 | `6\\n-1 2 -3 4 -5 6` | `720 -360 240 -180 144 -120` | sign handling |
| H6 | `18\\n10 10 10 10 10 10 10 10 10 10 10 10 10 10 10 10 10 10` | `100000000000000000 100000000000000000 100000000000000000 100000000000000000 100000000000000000 100000000000000000 100000000000000000 100000000000000000 100000000000000000 100000000000000000 100000000000000000 100000000000000000 100000000000000000 100000000000000000 100000000000000000 100000000000000000 100000000000000000 100000000000000000` | maximum n/value stress |
| H7 | `4\\n-10 -10 1 1` | `-10 -10 100 100` | mixed duplicates |
| H8 | `7\\n2 3 0 4 5 6 7` | `0 0 5040 0 0 0 0` | zero propagation |

**Python:** `import sys; a=list(map(int,sys.stdin.buffer.read().split())); n=a[0]; x=a[1:]; out=[1]*n; p=1\nfor i in range(n): out[i]=p; p*=x[i]\np=1\nfor i in range(n-1,-1,-1): out[i]*=p; p*=x[i]\nprint(*out)`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){int n;if(!(cin>>n))return 0;vector<long long>a(n),o(n,1);for(auto&x:a)cin>>x;long long p=1;for(int i=0;i<n;i++){o[i]=p;p*=a[i];}p=1;for(int i=n-1;i>=0;i--){o[i]*=p;p*=a[i];}for(int i=0;i<n;i++)cout<<o[i]<<(i+1==n?'\n':' ');}`

### A5 — Maximum Subarray

- **Slug:** `arrays-maximum-subarray`; **Topic:** Arrays; **Difficulty:** Medium.
- **Tags:** Kadane Scan; Running Maximum; Contiguous Range.
- **Time limit:** 1500 ms. **Memory limit:** 256 MB.

**Example 1**

Input:
```text
9
-2 1 -3 4 -1 2 1 -5 4
```
Output: `6`
Explanation: The subarray `4 -1 2 1` has the greatest sum.

**Example 2**

Input:
```text
5
-8 -3 -6 -2 -5
```
Output: `-2`
Explanation: The best non-empty subarray is the single value -2.
- **Learning objective:** Apply Kadane's algorithm to a non-empty subarray.
- **Statement:** Output the largest sum among all non-empty contiguous subarrays.
- **Input:** `n`, then `a1 ... an`.
- **Output:** One signed integer.
- **Constraints:** `1≤n≤100000`, `-10^4≤ai≤10^4`.
- **Approach/complexity:** Keep best subarray ending at each position; O(n) time,
  O(1) auxiliary space.
- **Edge cases:** singleton, all negative, all positive, and zero crossing.
- **Judging:** Safe ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `9\\n-2 1 -3 4 -1 2 1 -5 4` | `6` | public standard case |
| P2 | `5\\n-8 -3 -6 -2 -5` | `-2` | public all negative |
| H1 | `1\\n7` | `7` | minimum n |
| H2 | `6\\n1 2 3 4 5 6` | `21` | all positive |
| H3 | `6\\n0 -1 0 -2 0 3` | `3` | zero boundaries |
| H4 | `7\\n-5 -1 -8 -2 -3 -4 -6` | `-1` | negative maximum |
| H5 | `8\\n5 -10 6 7 -2 3 -20 4` | `14` | restart after loss |
| H6 | `5\\n10000 10000 -1 10000 10000` | `39999` | large values |
| H7 | `7\\n-4 6 -1 2 -7 5 5` | `10` | competing segments |
| H8 | `10\\n-1 -2 10 -3 4 -20 8 1 1 -1` | `11` | late best segment |

**Python:** `import sys; a=list(map(int,sys.stdin.buffer.read().split())); x=a[1:]; cur=best=x[0]\nfor v in x[1:]: cur=max(v,cur+v); best=max(best,cur)\nprint(best)`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){int n;cin>>n;long long x,cur,best;cin>>cur;best=cur;for(int i=1;i<n;i++){cin>>x;cur=max(x,cur+x);best=max(best,cur);}cout<<best<<'\n';}`

## 2. Strings

For all string problems below, input strings contain lowercase English letters
only; therefore whitespace tokenization is unambiguous.

### S1 — Valid Anagram

- **Slug:** `strings-valid-anagram`; **Topic:** Strings; **Difficulty:** Easy.
- **Tags:** Frequency Counting; Character Multiset; Hash Table.
- **Time limit:** 1000 ms. **Memory limit:** 128 MB.
- **Constraints:** `1≤|s|,|t|≤100000`; both inputs contain only lowercase English letters.

**Example 1** — Input: `anagram nagaram` — Output: `true` — Explanation: Both strings have identical letter counts.

**Example 2** — Input: `rat car` — Output: `false` — Explanation: Their character multisets differ.
- **Objective:** Compare character-frequency vectors.
- **Statement:** Determine whether the two input strings contain exactly the
  same multiset of letters.
- **Input:** Two lowercase strings `s` and `t` on one line.
- **Output:** `true` or `false`.
- **Constraints:** `1≤|s|,|t|≤100000`.
- **Approach/complexity:** Count 26 letters; O(|s|+|t|) time, O(1) auxiliary.
- **Edges:** equal strings, different lengths, repeated letters, reversal.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `anagram nagaram` | `true` | public anagram |
| P2 | `rat car` | `false` | public mismatch |
| H1 | `a a` | `true` | minimum strings |
| H2 | `ab ba` | `true` | reversal |
| H3 | `aab aba` | `true` | repeated letter |
| H4 | `aab abb` | `false` | frequency mismatch |
| H5 | `abc abcd` | `false` | length mismatch |
| H6 | `zzzz zzzz` | `true` | one-letter alphabet |
| H7 | `listen silent` | `true` | longer common case |
| H8 | `algorithm logarithm` | `true` | exact anagram with different order |

**Python:** `import sys; s,t=sys.stdin.buffer.read().split(); print(str(sorted(s)==sorted(t)).lower())`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){string s,t;cin>>s>>t;array<int,26>a{};for(char c:s)a[c-'a']++;for(char c:t)a[c-'a']--;cout<<(all_of(a.begin(),a.end(),[](int x){return x==0;})?"true":"false")<<'\n';}`

### S2 — Valid Palindrome

- **Slug:** `strings-valid-palindrome`; **Topic:** Strings; **Difficulty:** Easy.
- **Tags:** Two Pointers; Symmetry Check; String Scan.
- **Time limit:** 1000 ms. **Memory limit:** 128 MB.
- **Constraints:** `1≤|s|≤100000`; `s` contains only lowercase English letters.

**Example 1** — Input: `racecar` — Output: `true` — Explanation: The string equals its reverse.

**Example 2** — Input: `hello` — Output: `false` — Explanation: The first and last characters do not match symmetrically.
- **Objective:** Use two pointers to compare a string with its reverse.
- **Statement:** Determine whether the lowercase string reads identically from
  both directions.
- **Input:** One lowercase string `s`.
- **Output:** `true` or `false`.
- **Constraints:** `1≤|s|≤100000`.
- **Approach/complexity:** Two pointers; O(n) time, O(1) auxiliary.
- **Edges:** singleton, even/odd length, mismatch at center sides.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `racecar` | `true` | public odd palindrome |
| P2 | `hello` | `false` | public non-palindrome |
| H1 | `a` | `true` | singleton |
| H2 | `aa` | `true` | even palindrome |
| H3 | `ab` | `false` | minimum mismatch |
| H4 | `abba` | `true` | even palindrome |
| H5 | `abcba` | `true` | odd palindrome |
| H6 | `abcca` | `false` | near palindrome |
| H7 | `zzzzzz` | `true` | repeated character |
| H8 | `algorithm` | `false` | longer ordinary case |

**Python:** `import sys; s=sys.stdin.buffer.read().split()[0]; print(str(s==s[::-1]).lower())`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){string s;cin>>s;cout<<(equal(s.begin(),s.end(),s.rbegin())?"true":"false")<<'\n';}`

### S3 — Longest Substring Without Repeating Characters

- **Slug:** `strings-longest-unique-substring`; **Topic:** Strings; **Difficulty:** Medium.
- **Tags:** Sliding Window; Last-Seen Index; Distinct Characters.
- **Time limit:** 1500 ms. **Memory limit:** 256 MB.
- **Constraints:** `1≤|s|≤100000`; `s` contains only lowercase English letters.

**Example 1** — Input: `abcabcbb` — Output: `3` — Explanation: `abc` is a longest substring without repetition.

**Example 2** — Input: `bbbbb` — Output: `1` — Explanation: Any valid substring contains only one `b`.
- **Objective:** Maintain a sliding window with last-seen positions.
- **Statement:** Output the maximum length of a contiguous substring containing
  no repeated character.
- **Input:** One lowercase string `s`.
- **Output:** One integer.
- **Constraints:** `1≤|s|≤100000`.
- **Approach/complexity:** Sliding window; O(n) time, O(1) alphabet space.
- **Edges:** all unique, all equal, repeated character just outside the window.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `abcabcbb` | `3` | public repeated pattern |
| P2 | `bbbbb` | `1` | public all equal |
| H1 | `a` | `1` | minimum |
| H2 | `abcdef` | `6` | all unique |
| H3 | `pwwkew` | `3` | window movement |
| H4 | `abca` | `3` | repeated first character |
| H5 | `dvdf` | `3` | restart after duplicate |
| H6 | `aab` | `2` | early duplicate |
| H7 | `abba` | `2` | duplicate inside window |
| H8 | `abcdefghijklmnopqrstuvwxyz` | `26` | alphabet bound |

**Python:** `import sys; s=sys.stdin.buffer.read().split()[0]; last={}; l=ans=0\nfor r,c in enumerate(s):\n l=max(l,last.get(c,-1)+1); last[c]=r; ans=max(ans,r-l+1)\nprint(ans)`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){string s;cin>>s;array<int,26>p; p.fill(-1);int l=0,a=0;for(int r=0;r<(int)s.size();r++){int c=s[r]-'a';l=max(l,p[c]+1);p[c]=r;a=max(a,r-l+1);}cout<<a<<'\n';}`

### S4 — Group Anagrams

- **Slug:** `strings-group-anagrams`; **Topic:** Strings; **Difficulty:** Medium.
- **Tags:** Canonical Key; Sorting; Deterministic Grouping.
- **Time limit:** 1500 ms. **Memory limit:** 256 MB.
- **Constraints:** `1≤n≤1000`; total word length is at most 100000; every word has length at least 1 and contains only lowercase English letters.

**Example 1** — Input: `6 / neat tea tan ate nat bat` — Output lines: `ate tea`, `bat`, `nat tan`, `neat` — Explanation: Words share a group exactly when their sorted-letter keys match.

**Example 2** — Input: `3 / abc bca cab` — Output: `abc bca cab` — Explanation: All three words belong to one sorted group.
- **Objective:** Group words by a canonical sorted-letter key.
- **Statement:** Group anagrams and print groups deterministically. Sort words
  within each group and sort groups by their first word; print each group on
  one line, words separated by spaces.
- **Input:** `n`, followed by `n` lowercase words.
- **Output:** One deterministic line per group.
- **Constraints:** `1≤n≤1000`, total characters≤100000.
- **Approach/complexity:** Map sorted word→words, sort groups; O(total length log
  word length + n log n), auxiliary space O(total input).
- **Edges:** one word, duplicate words, singleton groups, mixed lengths.
- **Judging:** Ordinary token judging is safe because line breaks are ignored
  and the word order is fully specified.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `6\\nneat tea tan ate nat bat` | `ate tea\\nbat\\nnat tan\\nneat` | public three groups, sorted by first word |
| P2 | `3\\nabc bca cab` | `abc bca cab` | public one group |
| H1 | `1\\nsolo` | `solo` | minimum |
| H2 | `4\\na a a a` | `a a a a` | duplicate words |
| H3 | `5\\nab ba abc cba xyz` | `ab ba\\nabc cba\\nxyz` | singleton and groups |
| H4 | `4\\nbat tab eat tea` | `bat tab\\neat tea` | deterministic group order |
| H5 | `6\\nlisten silent enlist google gogole inlets` | `enlist inlets listen silent\\ngogole google` | larger groups |
| H6 | `2\\na bb` | `a\\nbb` | different lengths |
| H7 | `7\\nab ba ab ba abc cba abc` | `ab ab ba ba\\nabc abc cba` | repeated groups |
| H8 | `5\\nzzz z zzz zz z` | `z z\\nzz\\nzzz zzz` | prefix lengths |

**Python:** `import sys; a=sys.stdin.buffer.read().decode().split(); n=int(a[0]); d={}\nfor w in a[1:]: d.setdefault(''.join(sorted(w)),[]).append(w)\nfor g in sorted((sorted(v) for v in d.values()),key=lambda v:v[0]): print(*g)`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){int n;cin>>n;map<string,vector<string>>d;string w;while(n--){cin>>w;string k=w;sort(k.begin(),k.end());d[k].push_back(w);}vector<vector<string>>g;for(auto&[k,v]:d){sort(v.begin(),v.end());g.push_back(v);}sort(g.begin(),g.end(),[](auto&a,auto&b){return a[0]<b[0];});for(auto&v:g){for(int i=0;i<(int)v.size();i++)cout<<(i?" ":"")<<v[i];cout<<'\n';}}`

### S5 — Longest Palindromic Substring

- **Slug:** `strings-longest-palindromic-substring`; **Topic:** Strings; **Difficulty:** Medium.
- **Tags:** Center Expansion; Palindrome; Tie Breaking.
- **Time limit:** 1500 ms. **Memory limit:** 256 MB.
- **Constraints:** `1≤|s|≤2000`; `s` contains only lowercase English letters.

**Example 1** — Input: `babad` — Output: `bab` — Explanation: `bab` and `aba` tie, so the earliest start wins.

**Example 2** — Input: `cbbd` — Output: `bb` — Explanation: The longest palindrome has even length.
- **Objective:** Expand around each possible palindrome center.
- **Statement:** Output the longest palindromic substring. If several have the
  same maximum length, output the one with the smallest starting index.
- **Input:** One lowercase string `s`.
- **Output:** The selected substring.
- **Constraints:** `1≤|s|≤2000`.
- **Approach/complexity:** Expand around centers; O(n²) time, O(1) auxiliary.
- **Edges:** one character, even/odd ties, all equal, no length-two palindrome.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `babad` | `bab` | public tie chooses earliest |
| P2 | `cbbd` | `bb` | public even palindrome |
| H1 | `a` | `a` | minimum |
| H2 | `aaaa` | `aaaa` | all equal |
| H3 | `abc` | `a` | no pair; earliest tie |
| H4 | `racecarx` | `racecar` | long odd palindrome |
| H5 | `abccba` | `abccba` | full even palindrome |
| H6 | `forgeeksskeegfor` | `geeksskeeg` | interior maximum |
| H7 | `aacabdkacaa` | `aca` | repeated competing centers |
| H8 | `noonabbad` | `noon` | earliest maximum |

**Python:** `import sys; s=sys.stdin.buffer.read().decode().strip(); best=(0,0)\nfor c in range(len(s)):\n for l,r in ((c,c),(c,c+1)):\n  while l>=0 and r<len(s) and s[l]==s[r]:\n   if r-l+1>best[1]-best[0]: best=(l,r+1)\n   l-=1;r+=1\nprint(s[best[0]:best[1]])`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){string s;cin>>s;int L=0,R=1;auto f=[&](int l,int r){while(l>=0&&r<(int)s.size()&&s[l]==s[r]){if(r-l+1>R-L){L=l;R=r+1;}--l;++r;}};for(int i=0;i<(int)s.size();i++){f(i,i);f(i,i+1);}cout<<s.substr(L,R-L)<<'\n';}`

## 3. Linked List

Linked-list inputs use a plain array serialization: `n` followed by `n`
values. This represents the list from head to tail. No pointer identity,
random pointer, cycle pointer, or custom serialization is used. Output lists
use the same value serialization without a leading length.

### L1 — Reverse Linked List

- **Slug:** `linked-list-reverse`; **Topic:** Linked List; **Difficulty:** Easy.
- **Tags:** Pointer Reversal; Iteration; In-Place Update.
- **Time limit:** 1000 ms. **Memory limit:** 128 MB.
- **Constraints:** `0≤n≤100`; each list value is a signed 32-bit integer.

**Example 1** — Input: `5 / 1 2 3 4 5` — Output: `5 4 3 2 1` — Explanation: Each next link is reversed.

**Example 2** — Input: `3 / 7 7 -1` — Output: `-1 7 7` — Explanation: Values are preserved while order reverses.
- **Objective:** Rewire next pointers iteratively.
- **Statement:** Reverse the serialized singly linked list and print its values.
- **Input:** `n`, then `n` integers; `0≤n≤100`.
- **Output:** Reversed values on one line; empty input list produces an empty line.
- **Approach/complexity:** Iterative pointer reversal; O(n) time, O(1) auxiliary.
- **Edges:** empty, singleton, duplicate/negative values.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `5\\n1 2 3 4 5` | `5 4 3 2 1` | public ordinary list |
| P2 | `3\\n7 7 -1` | `-1 7 7` | public duplicates |
| H1 | `0` | *(empty)* | empty list |
| H2 | `1\\n4` | `4` | singleton |
| H3 | `2\\n-5 8` | `8 -5` | negative values |
| H4 | `6\\n0 0 0 0 0 0` | `0 0 0 0 0 0` | repeated zeros |
| H5 | `4\\n10 -10 20 -20` | `-20 20 -10 10` | alternating signs |
| H6 | `7\\n1 2 1 2 1 2 1` | `1 2 1 2 1 2 1` | symmetric values |
| H7 | `3\\n1000000000 0 -1000000000` | `-1000000000 0 1000000000` | bounds |
| H8 | `8\\n8 1 6 2 7 3 5 4` | `4 5 3 7 2 6 1 8` | longer rearrangement |

**Python:** `import sys; a=list(map(int,sys.stdin.buffer.read().split())); print(*a[1:][::-1])`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){int n;cin>>n;vector<long long>a(n);for(auto&x:a)cin>>x;reverse(a.begin(),a.end());for(int i=0;i<n;i++)cout<<(i?" ":"")<<a[i];cout<<'\n';}`

### L2 — Merge Two Sorted Lists

- **Slug:** `linked-list-merge-sorted`; **Topic:** Linked List; **Difficulty:** Easy.
- **Tags:** Two Pointers; Stable Merge; Sorted Inputs.
- **Time limit:** 1000 ms. **Memory limit:** 128 MB.
- **Constraints:** `0≤n,m≤100`; both serialized lists are nondecreasing; each value is a signed 32-bit integer.

**Example 1** — Input: `3 3 / 1 2 4 / 1 3 4` — Output: `1 1 2 3 4 4` — Explanation: Select the smaller current head repeatedly.

**Example 2** — Input: `0 3 / empty / 2 5 6` — Output: `2 5 6` — Explanation: Merging with an empty list returns the other list.
- **Objective:** Merge two sorted chains with a pointer comparison.
- **Statement:** Merge two nondecreasing serialized lists and print the resulting
  nondecreasing list.
- **Input:** `n m`, then list A, then list B; `0≤n,m≤100`.
- **Output:** All merged values, or an empty line.
- **Approach/complexity:** Two pointers; O(n+m) time, O(1) auxiliary.
- **Edges:** empty side, equal values, negatives, one side entirely smaller.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `3 3\\n1 2 4\\n1 3 4` | `1 1 2 3 4 4` | public standard |
| P2 | `0 3\\n\\n2 5 6` | `2 5 6` | public empty side |
| H1 | `0 0` | *(empty)* | both empty |
| H2 | `1 0\\n-1\\n` | `-1` | singleton side |
| H3 | `4 4\\n0 0 2 9\\n0 1 2 8` | `0 0 0 1 2 2 8 9` | duplicates |
| H4 | `3 2\\n-5 -2 0\\n-9 -8` | `-9 -8 -5 -2 0` | negative order |
| H5 | `2 4\\n10 20\\n1 2 3 4` | `1 2 3 4 10 20` | separated ranges |
| H6 | `3 3\\n1 1 1\\n1 1 1` | `1 1 1 1 1 1` | all equal |
| H7 | `5 1\\n-4 -3 -2 -1 0\\n-10` | `-10 -4 -3 -2 -1 0` | one low value |
| H8 | `4 5\\n2 4 6 8\\n1 3 5 7 9` | `1 2 3 4 5 6 7 8 9` | interleaving |

**Python:** `import sys; a=list(map(int,sys.stdin.buffer.read().split())); n,m=a[:2]; x=a[2:2+n]; y=a[2+n:2+n+m]; print(*(sorted(x+y)))`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){int n,m;cin>>n>>m;vector<long long>a(n+m);for(auto&x:a)cin>>x;sort(a.begin(),a.end());for(int i=0;i<n+m;i++)cout<<(i?" ":"")<<a[i];cout<<'\n';}`

### L3 — Linked List Cycle

- **Slug:** `linked-list-cycle`; **Topic:** Linked List; **Difficulty:** Easy.
- **Tags:** Fast Slow Pointers; Cycle Detection; Index Encoding.
- **Time limit:** 1000 ms. **Memory limit:** 128 MB.
- **Constraints:** `0≤n≤100`; `-1≤entry<n`; values are signed 32-bit integers; `-1` means the tail points to null.

**Example 1** — Input: `4 1 / 3 2 0 -4` — Output: `true` — Explanation: The tail points back to index 1.

**Example 2** — Input: `2 -1 / 1 2` — Output: `false` — Explanation: The tail points to null.
- **Objective:** Detect a cycle using Floyd's tortoise-and-hare algorithm.
- **Statement:** The serialized list has values followed by a cycle entry index.
  `-1` means the tail points to null; otherwise the tail points to that index.
  Output whether a cycle exists.
- **Input:** `n entry`, then `n` values; `0≤n≤100`, `-1≤entry<n`.
- **Output:** `true` or `false`.
- **Approach/complexity:** Slow/fast pointers; O(n) time, O(1) auxiliary.
- **Edges:** empty, self-cycle, cycle at head, tail null.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `4 1\\n3 2 0 -4` | `true` | public cycle in middle |
| P2 | `2 -1\\n1 2` | `false` | public acyclic list |
| H1 | `0 -1` | `false` | empty |
| H2 | `1 0\\n7` | `true` | self-cycle |
| H3 | `1 -1\\n7` | `false` | singleton null |
| H4 | `5 0\\n1 2 3 4 5` | `true` | head cycle |
| H5 | `5 4\\n1 2 3 4 5` | `true` | self-cycle at tail |
| H6 | `6 2\\n0 0 0 0 0 0` | `true` | duplicate values, cycle index matters |
| H7 | `3 -1\\n-1 -1 -1` | `false` | negative values no cycle |
| H8 | `8 3\\n8 1 6 2 7 3 5 4` | `true` | longer cycle |

**Python:** `import sys; a=list(map(int,sys.stdin.buffer.read().split())); n,e=a[:2]; nxt=list(range(1,n))+[-1] if n else []\nif n and e>=0:nxt[-1]=e\nslow=fast=0; ok=False\nwhile n and fast!=-1 and nxt[fast]!=-1:\n slow=nxt[slow]; fast=nxt[nxt[fast]]\n if slow==fast:ok=True;break\nprint(str(ok).lower())`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){int n,e;cin>>n>>e;vector<int>z(n);for(int i=0;i<n;i++)cin>>z[i];if(n&&e>=0){int slow=0,fast=0;z[n-1]=e;bool ok=0;while(fast!=-1&&z[fast]!=-1){slow=z[slow];fast=z[z[fast]];if(slow==fast){ok=1;break;}}cout<<(ok?"true":"false");}else cout<<"false";cout<<'\n';}`

### L4 — Remove Nth Node From End

- **Slug:** `linked-list-remove-nth-from-end`; **Topic:** Linked List; **Difficulty:** Medium.
- **Tags:** Two Pointers; Dummy Head; In-Place Deletion.
- **Time limit:** 1500 ms. **Memory limit:** 256 MB.
- **Constraints:** `1≤length≤100`; `1≤n≤length`; each value is a signed 32-bit integer.

**Example 1** — Input: `5 2 / 1 2 3 4 5` — Output: `1 2 3 5` — Explanation: The second node from the tail is removed.

**Example 2** — Input: `2 1 / 1 2` — Output: `1` — Explanation: The tail is removed.
- **Objective:** Use two pointers to remove a node in one pass.
- **Statement:** Remove the `n`th node counted from the tail. The input always
  has `1≤n≤length`; print the remaining list.
- **Input:** `length n`, then `length` values; `1≤length≤100`, `1≤n≤length`.
- **Output:** Remaining values, or an empty line.
- **Approach/complexity:** Dummy head and fixed pointer gap; O(length) time,
  O(1) auxiliary.
- **Edges:** remove head, tail, only node, middle.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `5 2\\n1 2 3 4 5` | `1 2 3 5` | public middle removal |
| P2 | `2 1\\n1 2` | `1` | public tail removal |
| H1 | `1 1\\n9` | *(empty)* | only node |
| H2 | `4 4\\n1 2 3 4` | `2 3 4` | remove head |
| H3 | `4 1\\n1 2 3 4` | `1 2 3` | remove tail |
| H4 | `6 3\\n0 0 0 0 0 0` | `0 0 0 0 0` | duplicates |
| H5 | `5 3\\n-5 -4 -3 -2 -1` | `-5 -4 -2 -1` | negatives |
| H6 | `7 5\\n1 2 3 4 5 6 7` | `1 2 4 5 6 7` | interior gap |
| H7 | `3 2\\n1000000000 0 -1000000000` | `1000000000 -1000000000` | bounds |
| H8 | `8 6\\n8 1 6 2 7 3 5 4` | `8 1 2 7 3 5 4` | longer list |

**Python:** `import sys; a=list(map(int,sys.stdin.buffer.read().split())); n,k=a[:2]; x=a[2:2+n]; del x[n-k]; print(*x)`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){int n,k;cin>>n>>k;vector<long long>a(n);for(auto&x:a)cin>>x;a.erase(a.begin()+n-k);for(int i=0;i<(int)a.size();i++)cout<<(i?" ":"")<<a[i];cout<<'\n';}`

### L5 — Add Two Numbers

- **Slug:** `linked-list-add-two-numbers`; **Topic:** Linked List; **Difficulty:** Medium.
- **Tags:** Carry Propagation; Digit Lists; Synchronized Traversal.
- **Time limit:** 1500 ms. **Memory limit:** 256 MB.
- **Constraints:** `1≤n,m≤100`; every list value is a decimal digit `0..9`; each list is reverse-digit order.

**Example 1** — Input: `3 3 / 2 4 3 / 5 6 4` — Output: `7 0 8` — Explanation: The represented numbers are 342 and 465, totaling 807.

**Example 2** — Input: `2 1 / 9 9 / 1` — Output: `0 0 1` — Explanation: 99+1=100, represented least-significant digit first.
- **Objective:** Add digit lists with carry, without converting to machine-sized
  integers.
- **Statement:** Each list stores one non-negative integer in reverse digit
  order. Add the two numbers and print the result in reverse digit order.
- **Input:** `n m`, then `n` digits and `m` digits; `1≤n,m≤100`, digits 0–9.
- **Output:** Result digits, least significant first; omit leading zeroes except
  that zero is printed as `0`.
- **Approach/complexity:** Digit-wise carry; O(max(n,m)) time and output space.
- **Edges:** carry chain, unequal lengths, zero, final carry.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `3 3\\n2 4 3\\n5 6 4` | `7 0 8` | public 342+465 |
| P2 | `2 1\\n9 9\\n1` | `0 0 1` | public carry/unequal |
| H1 | `1 1\\n0\\n0` | `0` | zero |
| H2 | `1 1\\n9\\n1` | `0 1` | final carry |
| H3 | `4 2\\n9 9 9 9\\n1 0` | `0 0 0 0 1` | carry chain |
| H4 | `3 5\\n1 2 3\\n9 9 9 9 9` | `0 2 3 0 0 1` | unequal lengths |
| H5 | `5 5\\n0 0 0 0 1\\n0 0 0 0 2` | `0 0 0 0 3` | high digit |
| H6 | `2 3\\n5 4\\n5 4 3` | `0 9 3` | mixed carry |
| H7 | `6 1\\n8 7 6 5 4 3\\n2` | `0 8 6 5 4 3` | short addend |
| H8 | `4 4\\n1 0 0 1\\n9 9 9 0` | `0 0 0 2` | several positions |

**Python:** `import sys; a=list(map(int,sys.stdin.buffer.read().split())); n,m=a[:2]; x=a[2:2+n]; y=a[2+n:2+n+m]; o=[];c=0\nfor i in range(max(n,m)):\n q=(x[i] if i<n else 0)+(y[i] if i<m else 0)+c;o.append(q%10);c=q//10\nif c:o.append(c)\nwhile len(o)>1 and o[-1]==0:o.pop()\nprint(*o)`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){int n,m;cin>>n>>m;vector<int>a(n),b(m),o;for(int&x:a)cin>>x;for(int&x:b)cin>>x;int c=0;for(int i=0;i<max(n,m);i++){int q=(i<n?a[i]:0)+(i<m?b[i]:0)+c;o.push_back(q%10);c=q/10;}if(c)o.push_back(c);for(int i=0;i<(int)o.size();i++)cout<<(i?" ":"")<<o[i];cout<<'\n';}`

## 4. Stack & Queue

### Q1 — Valid Parentheses

- **Slug:** `stack-valid-parentheses`; **Topic:** Stack & Queue; **Difficulty:** Easy.
- **Tags:** Stack Matching; Delimiters; Nesting.
- **Time limit:** 1000 ms. **Memory limit:** 128 MB.
- **Constraints:** `1≤length≤100000`; every character is one of `()[]{}`; the input is non-empty.

**Example 1** — Input: `()[]{}` — Output: `true` — Explanation: Every opening delimiter closes in the correct order.

**Example 2** — Input: `(]` — Output: `false` — Explanation: The closing bracket does not match the opening bracket.
- **Objective:** Match closing delimiters against a stack of opening delimiters.
- **Statement:** Determine whether every bracket in the string is correctly
  opened, nested, and closed. Alphabet is `()[]{}` only.
- **Input:** One non-empty bracket string; `1≤length≤100000`.
- **Output:** `true` or `false`.
- **Approach/complexity:** Stack; O(n) time and O(n) auxiliary space.
- **Edges:** empty is excluded, single pair, nesting, wrong crossing, early close.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `()[]{}` | `true` | public pairs |
| P2 | `(]` | `false` | public mismatch |
| H1 | `(` | `false` | unclosed |
| H2 | `[]` | `true` | minimum valid |
| H3 | `([{}])` | `true` | nested types |
| H4 | `([)]` | `false` | crossing |
| H5 | `]` | `false` | early close |
| H6 | `{}{}[]` | `true` | repeated pairs |
| H7 | `(((())))` | `true` | deep nesting |
| H8 | `{[()]}]` | `false` | extra close |

**Python:** `import sys; s=sys.stdin.buffer.read().decode(); st=[]; p={')':'(',']':'[','}':'{'}\nfor c in s:\n if c in '([{': st.append(c)\n elif c in p and (not st or st.pop()!=p[c]): print('false'); break\nelse: print(str(not st).lower())`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){string s;cin>>s;vector<char>st;map<char,char>p={{')','('},{']','['},{'}','{'}};bool ok=1;for(char c:s)if(c=='('||c=='['||c=='{')st.push_back(c);else if(st.empty()||st.back()!=p[c])ok=0;else st.pop_back();cout<<((ok&&st.empty())?"true":"false")<<'\n';}`

### Q2 — Min Stack

- **Slug:** `stack-min-stack`; **Topic:** Stack & Queue; **Difficulty:** Easy.
- **Tags:** Stack Invariant; Minimum Tracking; Query Processing.
- **Time limit:** 1000 ms. **Memory limit:** 128 MB.
- **Constraints:** `1≤q≤100000`; `push` values satisfy `-10^9≤x≤10^9`; every `pop`, `top`, and `min` operates on a non-empty stack.

**Example 1** — Input: `6 / push 3 / push 1 / min / pop / top / min` — Output: `1 / 3 / 3` — Explanation: The minimum changes when the value 1 is removed.

**Example 2** — Input: `4 / push -2 / top / min / pop` — Output: `-2 / -2` — Explanation: Both queries observe the only stack value.
- **Objective:** Maintain stack minimums with constant-time queries.
- **Statement:** Process operations on an initially empty stack. `push x`,
  `pop`, `top`, and `min` are given; queries are valid. Print one answer per
  `top` or `min` operation.
- **Input:** `q`, then q operation lines; `1≤q≤100000`.
- **Output:** Query answers, one per line.
- **Approach/complexity:** Stack of value/min pairs; O(1) per operation and
  O(q) space.
- **Edges:** repeated minima, negative values, minimum removal, one element.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `6\\npush 3\\npush 1\\nmin\\npop\\ntop\\nmin` | `1\\n3\\n3` | public minimum removal |
| P2 | `4\\npush -2\\ntop\\nmin\\npop` | `-2\\n-2` | public negative |
| H1 | `2\\npush 0\\nmin` | `0` | minimum operations |
| H2 | `7\\npush 5\\npush 5\\nmin\\npop\\nmin\\ntop\\npop` | `5\\n5\\n5` | duplicate minima |
| H3 | `8\\npush 4\\npush 2\\npush 3\\nmin\\npop\\nmin\\npop\\ntop` | `2\\n2\\n4` | staged removal |
| H4 | `6\\npush -1\\npush -5\\nmin\\npop\\ntop\\nmin` | `-5\\n-1\\n-1` | negative minimum |
| H5 | `5\\npush 9\\ntop\\npop\\npush 1\\nmin` | `9\\n1` | empty/reuse |
| H6 | `5\\npush 1000000000\\npush -1000000000\\nmin\\npop\\ntop` | `-1000000000\\n1000000000` | bounds |
| H7 | `8\\npush 3\\npush 1\\npush 2\\nmin\\npop\\nmin\\npop\\nmin` | `1\\n1\\n3` | changing minimum |
| H8 | `5\\npush 7\\ntop\\npop\\npush 8\\ntop` | `7\\n8` | repeated lifecycle |

**Python:** `import sys; a=sys.stdin.buffer.read().decode().splitlines(); st=[]; out=[]\nfor z in a[1:]:\n p=z.split();\n if p[0]=='push': st.append(int(p[1]))\n elif p[0]=='pop': st.pop()\n elif p[0]=='top': out.append(str(st[-1]))\n else: out.append(str(min(st)))\nprint('\n'.join(out))`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){int q;cin>>q;vector<long long>s;string op;while(q--){cin>>op;if(op=="push"){long long x;cin>>x;s.push_back(x);}else if(op=="pop")s.pop_back();else if(op=="top")cout<<s.back()<<'\n';else cout<<*min_element(s.begin(),s.end())<<'\n';}}`

### Q3 — Evaluate Reverse Polish Notation

- **Slug:** `stack-evaluate-rpn`; **Topic:** Stack & Queue; **Difficulty:** Medium.
- **Tags:** Operand Stack; Postfix Evaluation; Truncating Division.
- **Time limit:** 1500 ms. **Memory limit:** 256 MB.
- **Constraints:** `1≤n≤1000`; tokens are integers or `+ - * /`; the expression is valid, leaves one result, and never divides by zero; intermediate results fit signed 64-bit.

**Example 1** — Input: `5 / 2 1 + 3 *` — Output: `9` — Explanation: `(2+1)*3=9` in postfix order.

**Example 2** — Input: `5 / 4 13 5 / +` — Output: `6` — Explanation: `13/5` truncates toward zero before adding 4.
- **Objective:** Evaluate postfix expressions with an operand stack.
- **Statement:** Evaluate an integer expression in reverse Polish notation.
  Tokens are integers or `+ - * /`; division truncates toward zero. The
  expression is valid and has no division by zero.
- **Input:** `n`, then n space-separated tokens; `1≤n≤1000`.
- **Output:** One integer.
- **Approach/complexity:** Operand stack; O(n) time and O(n) space.
- **Edges:** negative operands, subtraction order, truncating division, nested ops.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `5\\n2 1 + 3 *` | `9` | public precedence by postfix |
| P2 | `5\\n4 13 5 / +` | `6` | public division |
| H1 | `1\\n7` | `7` | single operand |
| H2 | `3\\n5 2 -` | `3` | subtraction order |
| H3 | `3\\n2 5 /` | `0` | truncation toward zero |
| H4 | `3\\n-7 2 /` | `-3` | negative truncation |
| H5 | `13\\n10 6 9 3 + -11 * / * 17 + 5 +` | `22` | nested expression |
| H6 | `7\\n3 4 + 2 * 7 /` | `2` | chained operations |
| H7 | `5\\n-3 -2 * 5 +` | `11` | negative multiplication |
| H8 | `9\\n8 2 / 3 - 4 2 * +` | `9` | mixed operators |

**Python:** `import sys; a=sys.stdin.buffer.read().decode().split(); st=[]\nfor t in a[1:]:\n if t.lstrip('-').isdigit(): st.append(int(t))\n else:\n  b,x=st.pop(),st.pop()\n  if t=='+': st.append(x+b)\n  elif t=='-': st.append(x-b)\n  elif t=='*': st.append(x*b)\n  else: st.append((abs(x)//abs(b))*(-1 if x*b<0 else 1))\nprint(st[-1])`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){int n;cin>>n;vector<long long>s;string t;while(n--){cin>>t;if(isdigit(t[0])||(t[0]=='-'&&t.size()>1))s.push_back(stoll(t));else{auto b=s.back();s.pop_back();auto a=s.back();s.pop_back();if(t=="+")s.push_back(a+b);if(t=="-")s.push_back(a-b);if(t=="*")s.push_back(a*b);if(t=="/")s.push_back(a/b);}}cout<<s.back()<<'\n';}`

### Q4 — Daily Temperatures

- **Slug:** `stack-daily-temperatures`; **Topic:** Stack & Queue; **Difficulty:** Medium.
- **Tags:** Monotonic Stack; Next Greater Element; Deferred Resolution.
- **Time limit:** 1500 ms. **Memory limit:** 256 MB.
- **Constraints:** `1≤n≤100000`; `-100≤temperature[i]≤100`.

**Example 1** — Input: `8 / 73 74 75 71 69 72 76 73` — Output: `1 1 4 2 1 1 0 0` — Explanation: Each value reports the wait for its next warmer day.

**Example 2** — Input: `5 / 30 40 50 60 70` — Output: `1 1 1 1 0` — Explanation: Every day waits exactly one day except the last.
- **Objective:** Use a monotonic decreasing stack to find the next greater value.
- **Statement:** For each temperature, output the number of days until a warmer
  temperature; output 0 if none exists.
- **Input:** `n`, then n integer temperatures; `1≤n≤100000`.
- **Output:** n space-separated integers.
- **Constraints:** `-100≤temperature≤100`.
- **Approach/complexity:** Monotonic stack; O(n) time, O(n) space.
- **Edges:** all decreasing, all equal, warmer immediately, final zero.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `8\\n73 74 75 71 69 72 76 73` | `1 1 4 2 1 1 0 0` | public standard |
| P2 | `5\\n30 40 50 60 70` | `1 1 1 1 0` | public increasing |
| H1 | `1\\n10` | `0` | minimum |
| H2 | `5\\n70 60 50 40 30` | `0 0 0 0 0` | decreasing |
| H3 | `5\\n20 20 20 20 20` | `0 0 0 0 0` | equal values |
| H4 | `6\\n10 11 9 12 8 13` | `1 2 1 2 1 0` | alternating rises |
| H5 | `4\\n-10 -5 -6 0` | `1 2 1 0` | negative values |
| H6 | `7\\n1 3 2 4 3 5 0` | `1 2 1 2 1 0 0` | stack popping |
| H7 | `6\\n0 -1 -2 1 -3 2` | `3 2 1 2 1 0` | long wait within temperature bounds |
| H8 | `8\\n5 4 3 2 6 1 7 0` | `4 3 2 1 2 1 0 0` | mixed tails |

**Python:** `import sys; a=list(map(int,sys.stdin.buffer.read().split())); x=a[1:]; o=[0]*len(x); st=[]\nfor i,v in enumerate(x):\n while st and x[st[-1]]<v: j=st.pop();o[j]=i-j\n st.append(i)\nprint(*o)`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){int n;cin>>n;vector<int>a(n),o(n),s;for(int&x:a)cin>>x;for(int i=0;i<n;i++){while(!s.empty()&&a[s.back()]<a[i])o[s.back()]=i-s.back(),s.pop_back();s.push_back(i);}for(int i=0;i<n;i++)cout<<(i?" ":"")<<o[i];cout<<'\n';}`

### Q5 — Sliding Window Maximum

- **Slug:** `queue-sliding-window-maximum`; **Topic:** Stack & Queue; **Difficulty:** Medium.
- **Tags:** Monotonic Deque; Sliding Window; Expiring Indices.
- **Time limit:** 1500 ms. **Memory limit:** 256 MB.
- **Constraints:** `1≤k≤n≤100000`; every array value is a signed 32-bit integer.

**Example 1** — Input: `8 3 / 1 3 -1 -3 5 3 6 7` — Output: `3 3 5 5 6 7` — Explanation: The deque keeps the maximum candidate for each width-three window.

**Example 2** — Input: `1 1 / 9` — Output: `9` — Explanation: A width-one window contains its only element.
- **Objective:** Maintain a deque of useful window candidates.
- **Statement:** Output the maximum value in every contiguous window of width k.
- **Input:** `n k`, then n integers; `1≤k≤n≤100000`.
- **Output:** `n-k+1` space-separated integers.
- **Approach/complexity:** Monotonic deque; O(n) time, O(k) space.
- **Edges:** k=1, k=n, duplicates, negative values.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `8 3\\n1 3 -1 -3 5 3 6 7` | `3 3 5 5 6 7` | public standard |
| P2 | `1 1\\n9` | `9` | public minimum |
| H1 | `5 1\\n4 -1 2 7 0` | `4 -1 2 7 0` | k=1 |
| H2 | `5 5\\n4 -1 2 7 0` | `7` | k=n |
| H3 | `6 2\\n1 1 1 1 1 1` | `1 1 1 1 1` | duplicate maxima |
| H4 | `5 2\\n-5 -2 -8 -1 -3` | `-2 -2 -1 -1` | negatives |
| H5 | `7 4\\n9 3 5 1 6 2 8` | `9 6 6 8` | stale indices |
| H6 | `6 3\\n10 9 8 7 6 5` | `10 9 8 7` | decreasing |
| H7 | `6 3\\n1 5 2 5 3 5` | `5 5 5 5` | repeated peak |
| H8 | `8 5\\n0 4 2 9 1 3 8 7` | `9 9 9 9` | wider windows |

**Python:** `import sys,collections; a=list(map(int,sys.stdin.buffer.read().split())); n,k=a[:2];x=a[2:];d=collections.deque();o=[]\nfor i,v in enumerate(x):\n while d and d[0]<=i-k:d.popleft()\n while d and x[d[-1]]<=v:d.pop()\n d.append(i)\n if i>=k-1:o.append(x[d[0]])\nprint(*o)`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){int n,k;cin>>n>>k;vector<int>a(n);for(int&x:a)cin>>x;deque<int>d;for(int i=0;i<n;i++){while(!d.empty()&&d.front()<=i-k)d.pop_front();while(!d.empty()&&a[d.back()]<=a[i])d.pop_back();d.push_back(i);if(i>=k-1)cout<<(i==k-1?"":" ")<<a[d.front()];}cout<<'\n';}`

## 5. Dynamic Programming

### D1 — Climbing Stairs

- **Slug:** `dp-climbing-stairs`; **Topic:** Dynamic Programming; **Difficulty:** Easy.
- **Tags:** Fibonacci Recurrence; State Compression; Counting.
- **Time limit:** 1000 ms. **Memory limit:** 128 MB.
- **Constraints:** `1≤n≤45`; each move advances exactly one or two stairs.

**Example 1** — Input: `2` — Output: `2` — Explanation: The two sequences are 1+1 and 2.

**Example 2** — Input: `5` — Output: `8` — Explanation: The recurrence counts all one-step/two-step sequences.
- **Objective:** Build a one-dimensional recurrence from the two previous states.
- **Statement:** Count ways to reach stair n when each move climbs one or two
  stairs. The order of moves matters.
- **Input:** One integer n; `1≤n≤45`.
- **Output:** Number of ways.
- **Approach/complexity:** Fibonacci recurrence; O(n) time, O(1) space.
- **Edges:** n=1, n=2, upper bound.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `2` | `2` | public base |
| P2 | `5` | `8` | public recurrence |
| H1 | `1` | `1` | minimum |
| H2 | `3` | `3` | small odd |
| H3 | `4` | `5` | small even |
| H4 | `10` | `89` | medium |
| H5 | `20` | `10946` | larger value |
| H6 | `30` | `1346269` | growth |
| H7 | `44` | `1134903170` | near upper bound |
| H8 | `45` | `1836311903` | maximum constraint |

**Python:** `import sys; n=int(sys.stdin.buffer.read());a,b=1,1\nfor _ in range(n):a,b=b,a+b\nprint(a)`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){int n;cin>>n;long long a=1,b=1;while(n--)tie(a,b)=make_tuple(b,a+b);cout<<a<<'\n';}`

### D2 — House Robber

- **Slug:** `dp-house-robber`; **Topic:** Dynamic Programming; **Difficulty:** Easy.
- **Tags:** Non-Adjacent Selection; Rolling DP; Optimal Substructure.
- **Time limit:** 1000 ms. **Memory limit:** 128 MB.
- **Constraints:** `1≤n≤100000`; `0≤amount[i]≤10000` for every house.

**Example 1** — Input: `4 / 1 2 3 1` — Output: `4` — Explanation: Rob houses 0 and 2.

**Example 2** — Input: `5 / 2 7 9 3 1` — Output: `12` — Explanation: Rob houses containing 2, 9, and 1.
- **Objective:** Choose non-adjacent values using a rolling recurrence.
- **Statement:** Houses in a line contain non-negative amounts. Rob no two
  adjacent houses; output the maximum amount.
- **Input:** `n`, then n amounts; `1≤n≤100000`, `0≤amount≤10000`.
- **Output:** One integer.
- **Approach/complexity:** `dp[i]=max(dp[i-1],dp[i-2]+a[i])`; O(n) time/O(1) space.
- **Edges:** one house, all zero, alternating large values, adjacent maxima.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `4\\n1 2 3 1` | `4` | public standard |
| P2 | `5\\n2 7 9 3 1` | `12` | public standard |
| H1 | `1\\n10` | `10` | minimum |
| H2 | `5\\n0 0 0 0 0` | `0` | zeros |
| H3 | `6\\n5 1 1 5 1 1` | `11` | separated peaks |
| H4 | `7\\n2 10 2 10 2 10 2` | `30` | alternating |
| H5 | `3\\n10000 1 10000` | `20000` | maximum values |
| H6 | `6\\n1 2 3 4 5 6` | `12` | increasing |
| H7 | `8\\n8 7 6 5 4 3 2 1` | `20` | decreasing |
| H8 | `5\\n4 1 1 4 1` | `8` | tie choices |

**Python:** `import sys; a=list(map(int,sys.stdin.buffer.read().split()));x=a[1:];p=q=0\nfor v in x:p,q=q,max(q,p+v)\nprint(q)`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){int n;cin>>n;long long p=0,q=0,x;while(n--){cin>>x;long long z=max(q,p+x);p=q;q=z;}cout<<q<<'\n';}`

### D3 — Coin Change

- **Slug:** `dp-coin-change`; **Topic:** Dynamic Programming; **Difficulty:** Medium.
- **Tags:** Unbounded Knapsack; Minimum Count; Bottom-Up DP.
- **Time limit:** 1500 ms. **Memory limit:** 256 MB.
- **Constraints:** `1≤m≤20`; `1≤amount≤10000`; every coin denomination is a positive integer; coins may be reused.

**Example 1** — Input: `3 11 / 1 2 5` — Output: `3` — Explanation: 11 uses 5+5+1.

**Example 2** — Input: `2 3 / 2 4` — Output: `-1` — Explanation: No combination of 2 and 4 makes 3.
- **Objective:** Compute a minimum-count unbounded knapsack recurrence.
- **Statement:** Given coin denominations and a target amount, output the fewest
  coins needed, or -1 if impossible. Each denomination may be reused.
- **Input:** `m amount`, then m positive coin values; `1≤m≤20`, `1≤amount≤10000`.
- **Output:** Minimum count or `-1`.
- **Approach/complexity:** Bottom-up amount DP; O(m·amount) time and O(amount) space.
- **Edges:** exact coin, impossible target, duplicate denominations, amount one.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `3 11\\n1 2 5` | `3` | public standard |
| P2 | `2 3\\n2 4` | `-1` | public impossible |
| H1 | `1 1\\n1` | `1` | minimum |
| H2 | `1 7\\n7` | `1` | exact denomination |
| H3 | `3 6\\n1 3 4` | `2` | best skips small coins |
| H4 | `2 10\\n6 4` | `2` | even combination |
| H5 | `4 27\\n2 5 10 20` | `3` | combination |
| H6 | `3 8\\n3 5 7` | `2` | reachable combination |
| H7 | `5 30\\n1 6 7 13 20` | `5` | large denomination |
| H8 | `4 9\\n2 3 4 8` | `3` | competing counts |

**Python:** `import sys; a=list(map(int,sys.stdin.buffer.read().split()));m,A=a[:2];c=a[2:];d=[A+1]*(A+1);d[0]=0\nfor x in range(1,A+1):d[x]=min((d[x-v]+1 for v in c if v<=x),default=A+1)\nprint(-1 if d[A]>A else d[A])`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){int m,A;cin>>m>>A;vector<int>c(m),d(A+1,A+1);for(int&x:c)cin>>x;d[0]=0;for(int x=1;x<=A;x++)for(int v:c)if(v<=x)d[x]=min(d[x],d[x-v]+1);cout<<(d[A]>A?-1:d[A])<<'\n';}`

### D4 — Longest Increasing Subsequence

- **Slug:** `dp-longest-increasing-subsequence`; **Topic:** Dynamic Programming; **Difficulty:** Medium.
- **Tags:** Patience Sorting; Lower Bound; Subsequence Length.
- **Time limit:** 1500 ms. **Memory limit:** 256 MB.
- **Constraints:** `1≤n≤100000`; `-10^9≤ai≤10^9`; increasing means strictly increasing by index.

**Example 1** — Input: `8 / 10 9 2 5 3 7 101 18` — Output: `4` — Explanation: One LIS is 2,3,7,101.

**Example 2** — Input: `6 / 0 1 0 3 2 3` — Output: `4` — Explanation: One LIS is 0,1,2,3.
- **Objective:** Track the smallest tail for each increasing subsequence length.
- **Statement:** Output the length of a strictly increasing subsequence.
- **Input:** `n`, then n integers; `1≤n≤100000`, `-10^9≤ai≤10^9`.
- **Output:** One integer.
- **Approach/complexity:** Tails array with lower_bound; O(n log n) time, O(n) space.
- **Edges:** equal values are not increasing, all decreasing/increasing, negatives.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `8\\n10 9 2 5 3 7 101 18` | `4` | public standard |
| P2 | `6\\n0 1 0 3 2 3` | `4` | public duplicates |
| H1 | `1\\n5` | `1` | minimum |
| H2 | `5\\n1 2 3 4 5` | `5` | increasing |
| H3 | `5\\n5 4 3 2 1` | `1` | decreasing |
| H4 | `6\\n2 2 2 2 2 2` | `1` | strictness |
| H5 | `7\\n-5 -1 -3 0 2 -2 4` | `5` | negatives |
| H6 | `8\\n8 1 2 3 0 4 5 6` | `6` | replacement tails |
| H7 | `6\\n1000000000 -1 0 1 2 3` | `5` | bounds |
| H8 | `9\\n3 10 2 1 20 4 6 7 8` | `5` | interleaved sequence |

**Python:** `import sys,bisect; a=list(map(int,sys.stdin.buffer.read().split()));t=[]\nfor x in a[1:]:i=bisect.bisect_left(t,x);t[i:i+1]=[x] if i==len(t) else [x]\nprint(len(t))`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){int n;cin>>n;vector<long long>t;while(n--){long long x;cin>>x;auto i=lower_bound(t.begin(),t.end(),x);if(i==t.end())t.push_back(x);else *i=x;}cout<<t.size()<<'\n';}`

### D5 — Word Break

- **Slug:** `dp-word-break`; **Topic:** Dynamic Programming; **Difficulty:** Medium.
- **Tags:** Prefix DP; Dictionary Matching; Reusable Words.
- **Time limit:** 1500 ms. **Memory limit:** 256 MB.
- **Constraints:** `1≤|s|≤100`; `1≤m≤50`; dictionary words have length `1..20`; all characters are lowercase English letters; words may be reused.

**Example 1** — Input: `leetcode 2 / leet code` — Output: `true` — Explanation: The string splits as leet + code.

**Example 2** — Input: `catsandog 5 / cats dog sand and cat` — Output: `false` — Explanation: The final `og` cannot be covered.
- **Objective:** Decide segmentability with a prefix DP.
- **Statement:** Given a string and a dictionary, determine whether the string
  can be split into one or more dictionary words. Words may be reused.
- **Input:** String `s`, then integer m, then m lowercase dictionary words;
  `1≤|s|≤100`, `1≤m≤50`, word lengths≤20.
- **Output:** `true` or `false`.
- **Approach/complexity:** `dp[i]` means prefix i is segmentable; O(n·m·L) time.
- **Edges:** exact word, repeated reuse, prefix dead end, overlapping choices.
- **Judging:** Ordinary token judging.

| Case | Input | Expected | Purpose |
|---|---|---|---|
| P1 | `leetcode 2\\nleet code` | `true` | public two-word split |
| P2 | `catsandog 5\\ncats dog sand and cat` | `false` | public dead end |
| H1 | `a 1\\na` | `true` | minimum |
| H2 | `aaaaaaa 2\\na aa` | `true` | reuse |
| H3 | `applepenapple 2\\napple pen` | `true` | repeated word |
| H4 | `catsanddog 5\\ncat cats and sand dog` | `true` | overlapping prefixes |
| H5 | `cars 3\\ncar ca rs` | `true` | short words |
| H6 | `aaaaab 2\\na aa` | `false` | final unmatched character |
| H7 | `book 2\\nbo ok` | `true` | exact concatenation |
| H8 | `abcd 3\\nab abc cd` | `true` | choice/backtracking avoided |

**Python:** `import sys; a=sys.stdin.buffer.read().decode().split();s=a[0];m=int(a[1]);w=a[2:2+m];d=[False]*(len(s)+1);d[0]=True\nfor i in range(len(s)):\n if d[i]:\n  for z in w:\n   if s.startswith(z,i):d[i+len(z)]=True\nprint(str(d[-1]).lower())`

**C++17:** `#include <bits/stdc++.h>\nusing namespace std;int main(){string s;int m;cin>>s>>m;vector<string>w(m);for(auto&z:w)cin>>z;vector<char>d(s.size()+1);d[0]=1;for(int i=0;i<(int)s.size();i++)if(d[i])for(auto&z:w)if(s.compare(i,z.size(),z)==0)d[i+z.size()]=1;cout<<(d.back()?"true":"false")<<'\n';}`

## A. Final 25-problem specification index

| Topic | Slugs |
|---|---|
| Arrays | `arrays-two-sum`, `arrays-best-time-stock`, `arrays-contains-duplicate`, `arrays-product-except-self`, `arrays-maximum-subarray` |
| Strings | `strings-valid-anagram`, `strings-valid-palindrome`, `strings-longest-unique-substring`, `strings-group-anagrams`, `strings-longest-palindromic-substring` |
| Linked List | `linked-list-reverse`, `linked-list-merge-sorted`, `linked-list-cycle`, `linked-list-remove-nth-from-end`, `linked-list-add-two-numbers` |
| Stack & Queue | `stack-valid-parentheses`, `stack-min-stack`, `stack-evaluate-rpn`, `stack-daily-temperatures`, `queue-sliding-window-maximum` |
| Dynamic Programming | `dp-climbing-stairs`, `dp-house-robber`, `dp-coin-change`, `dp-longest-increasing-subsequence`, `dp-word-break` |

## B. Topic/difficulty progression

Each topic contains three Easy-to-Medium transitions: foundational scan or
stack/list operation first, then a constrained optimization or state problem.
The intended order is the order in each topic above. The final two problems in
each topic are Medium and require explicit edge-case reasoning.

## C. Cross-problem consistency rules

Every slug is stable and lowercase-hyphenated. Every problem has exactly two
public and eight hidden cases, exactly one deterministic output contract, both
language references, problem-level limits to be assigned during seed
implementation, and no file or interactive behavior. Linked-list concepts use
value serialization only; no pointer serialization may be introduced without
human approval.

## D. Test-case design rules

Public cases demonstrate the normal algorithm and one important boundary or
failure mode. Hidden cases cover minimum size, maximum or near-maximum values,
duplicates, signs, empty valid structures, all-equal/all-monotone data, and an
algorithm-adversarial arrangement where applicable. No duplicate input/output
pair is intentional. Every expected output must be generated by both listed
references before seed insertion.

## E. Open decisions requiring human approval

1. Confirm that the compact reference blocks are acceptable as trusted source
   text, or require expanded conventional formatting before implementation.
2. Assign final per-problem time and memory limits consistent with the V1
   sandbox policy.
3. Confirm whether `Valid Parentheses` should permit an empty string; this v0
   contract intentionally excludes it.
4. Confirm the exact output policy for an empty serialized linked-list result.
5. Confirm whether the curriculum should retain the five-topic progression
   unchanged before any seed reconciliation work begins.

## F. Preconditions for seed.py implementation

No seed change is authorized by this artifact alone. Before modifying
`seed.py`, an engineer must independently execute every Python and C++
reference against all 250 cases, verify matching outputs, assign limits,
review the five open decisions, and encode the frozen flags:

- cases 1–2: `is_sample=true`, `run_enabled=true`, `submit_enabled=true`;
- cases 3–10: `is_sample=false`, `run_enabled=false`, `submit_enabled=true`.

Only after those checks may the canonical dataset be reconciled into the
database in a separately authorized step.
