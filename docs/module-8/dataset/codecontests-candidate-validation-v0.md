# CodeContests Candidate Validation v0

Status: rejected as a source for canonical V1 content.

This report validates only the 25 rows in Candidate Shortlist v0 from
`codecontests-candidate-inventory.md`. It does not approve any row for
seeding.

## Validation method

The complete row was loaded from the cached 500-row Hugging Face
representation used by the inventory. For each row, the validator inspected
the description, file-I/O fields, limits, all public/private/generated input
and output pairs, and the language-tagged solutions. Python language 3
sources were syntax-checked and executed with Python 3. C++ language 2
sources were compiled with `g++ -std=c++17 -O2` and executed. Each available
pair was run against both references with a bounded execution timeout.

Outputs were compared by whitespace-separated tokens. This is appropriate for
ordinary token-based stdin/stdout judging, but it does not make a malformed
or special-judge record valid.

The source representation is not trustworthy enough for canonical content.
For example, the row named `893_A. Chess For Three` has a factorial-factorization
description and matching-looking factorial test data rather than a three-player
game. The row named `muffins3` describes convex polygons. The row named
`1398_A. Bad Triangle` describes a sandglass/data-structure operation. These
are record-level identity failures, not merely reference implementation bugs.

## Aggregate result

- Candidates inspected: 25.
- PASS: 0.
- FAIL: 25.
- Python sources syntactically valid: 25/25.
- C++17 references compiled: 24/25.
- Candidates with zero duplicate exact input/output pairs: 25/25.
- Candidates with empty input or expected-output strings: 0 detected.
- Candidates with a clean reference-agreement and expected-output pass: 0/25.
- Candidates with at least 10 raw pairs: 25/25, but raw count is not strong-test eligibility.
- Candidate-visible pairs available by count: the shortlist's first one or two public pairs.
- Candidate-hidden pairs available by count: selected from private then generated pairs.
- Canonical strong tests identified: 0/25, because the associated record identity and reference/output consistency must first be repaired.

## A. 25 candidate validation table

`py bad/exec` counts expected-output mismatches and non-zero/timeout executions
respectively. `cpp bad/exec` has the same meaning. `T` is the combined timeout
count. The visible/hidden columns are only the mechanical candidate selection
indices; they are **not approved tests**.

| Candidate | Result/reason | Python reference | C++ reference | Valid pairs | Duplicate pairs | Candidate visible tests | Candidate hidden tests | Suspected inconsistency / normalization |
|---|---|---:|---:|---:|---:|---|---|---|
| even-from-end-1 | FAIL: Python mismatched all 106; C++ mismatched 35 and failed/timeout on 71 | syntax valid; bad 106/106 | compiled; bad 35/exec 71 | 106 | 0 | public[0..1] | private[0..2] + generated[0..4] | Name/description/test/reference identity must be rejoined; discard all pairs until repaired. |
| p00167 Bubble Sort | FAIL: Python timed out on all 96; C++ bad 16 and failed/timeout on 79 | syntax valid; exec 96 failures | compiled; bad 16/exec 79 | 96 | 0 | public[0..0] | private[0..1] + generated[0..5] | Row describes three sequences, while name and reference identity do not establish a coherent standalone contract. |
| 433_A. Kitahara Haruki's Gift | FAIL: Python had one mismatch and 100 execution failures; C++ failed all executions | syntax valid; bad 1/exec 100 | compiled; bad 0/exec 101 | 101 | 0 | public[0..0] | generated[0..7] | Inputs visibly contain multiple unrelated sections; no reliable stdin contract. |
| 893_A. Chess For Three | FAIL: references and expected outputs disagree on most pairs | syntax valid; bad 126/exec 1 | compiled; bad 123 | 127 | 0 | public[0..0] | private[0..7] | Name says chess, description/tests are factorial factorization; reject identity. |
| p02445 Swap | FAIL: Python failed all executions; C++ expected-output mismatch on all pairs | syntax valid; exec 116 | compiled; bad 116 | 116 | 0 | public[0..0] | private[0..7] | Description is a people/keys optimization problem, while the first input is a multi-record text dataset; normalize by replacement. |
| 977_B. Two-gram | FAIL: Python failed all executions; C++ failed or timed out on 115 | syntax valid; exec 130 | compiled; bad 15/exec 115 | 130 | 0 | public[0..0] | private[0..7] | Name is Two-gram, description is a game; source row is not internally coherent. |
| playing-with-substrings | FAIL: both references failed almost all executions; one mismatch each | syntax valid; bad 1/exec 101 | compiled; bad 1/exec 101 | 102 | 0 | public[0..0] | private[0..0] + generated[0..6] | Description concerns towns/cream, not a clear substring contract. |
| p01083 RedBlue | FAIL: Python had two mismatches; C++ mismatched all 102 | syntax valid; bad 2/exec 100 | compiled; bad 102 | 102 | 0 | public[0..1] | generated[0..7] | Description and test data concern bracket ratios, not a stable RedBlue contract. |
| 1140_B. Good String | FAIL: Python had three mismatches; C++ mismatched all 40 | syntax valid; bad 3/exec 37 | compiled; bad 40 | 40 | 0 | public[0..1] | generated[0..7] | Description is factorial trailing-zero processing, not Good String. |
| p00206 Next Trip | FAIL: Python failed all executions; C++ mismatched all 105 | syntax valid; exec 105 | compiled; bad 105 | 105 | 0 | public[0..1] | private[0..1] + generated[0..5] | Description concerns colored-pixel fights; name, tests, and references do not form one problem. |
| 1007_E. Mini Metro | FAIL: Python failed all executions; C++ mismatched all 59 | syntax valid; exec 59 | compiled; bad 59/exec 0 | 59 | 0 | public[0..0] | private[0..7] | Description is an insect-splitting problem, not Mini Metro. |
| muffins3 | FAIL: both references disagree with every expected output | syntax valid; bad 53 | compiled; bad 53 | 53 | 0 | public[0..1] | generated[0..7] | Description is convex-polygon classification; shortlist name is unrelated. |
| 151_C. Win or Freeze | FAIL: Python failed all executions; C++ bad 4 and failed/timeout on 27 | syntax valid; exec 31 | compiled; bad 4/exec 27 | 31 | 0 | public[0..1] | private[0..0] + generated[0..6] | Description concerns credit-card balances, but tests/reference do not provide a stable V1 contract. |
| 593_C. Beautiful Function | FAIL: Python failed all executions; C++ had one mismatch and failed/timeout on 56 | syntax valid; exec 57 | compiled; bad 1/exec 56 | 57 | 0 | public[0..0] | generated[0..7] | Description is a railway/stations problem; name and test data are not coherent. |
| p03771 AtCoder Grand Contest 012 - Camel and Oases | FAIL: Python failed all executions; C++ bad 6 and failed/timeout on 114 | syntax valid; exec 120 | compiled; bad 6/exec 114 | 120 | 0 | public[0..1] | private[0..7] | Description is a soccer penalty-shootout problem, not a verified camel/oases contract. |
| 687_A. NP-Hard Problem | FAIL: Python bad 100 and failed 33; C++ failed all 133 | syntax valid; bad 100/exec 33 | compiled; exec 133 | 133 | 0 | public[0..0] | private[0..7] | Description discusses sorting; name implies bipartiteness. Reject identity. |
| 1081_D. Maximum Distance | FAIL: Python failed all executions; C++ bad 19 and failed/timeout on 84 | syntax valid; exec 103 | compiled; bad 19/exec 84 | 103 | 0 | public[0..1] | generated[0..7] | Description is binary-matrix compression, not a verified graph-distance contract. |
| 1070_C. Cloud Computing | FAIL: Python failed all executions; C++ bad 58 | syntax valid; exec 62 | compiled; bad 58 | 62 | 0 | public[0..1] | generated[0..7] | Description concerns a 2×n turtle field; name and references are not aligned. |
| 284_B. Cows and Poker Game | FAIL: Python had one mismatch and 125 failures; C++ bad 64 and failed/timeout on 61 | syntax valid; bad 1/exec 125 | compiled; bad 64/exec 61 | 126 | 0 | public[0..0] | private[0..7] | Description is a narrative unrelated to a reliable graph/state contract; inputs contain unrelated formats. |
| 1398_A. Bad Triangle | FAIL: Python failed all executions; C++ mismatched all 93 | syntax valid; exec 93 | compiled; bad 93 | 93 | 0 | public[0..1] | generated[0..7] | Description is sandglass/data-structure operations, not Bad Triangle. |
| p03294 AtCoder Beginner Contest 103 - Modulo Summation | FAIL: Python failed all executions; C++ did not compile and failed all executions | syntax valid; exec 103 | compile failed; exec 103 | 103 | 0 | public[0..1] | generated[0..7] | Description concerns three stone heaps; C++ source is unusable; reject until complete record replacement. |
| 1490_G. Old Floppy Drive | FAIL: Python failed all executions; C++ bad 51 and failed/timeout on 1 | syntax valid; exec 52 | compiled; bad 51/exec 1 | 52 | 0 | public[0..0] | generated[0..7] | Description is a two-number operation problem, not Old Floppy Drive. |
| 1269_E. K Integers | FAIL: Python had three mismatches and 150 failures; C++ failed all 153 | syntax valid; bad 3/exec 150 | compiled; exec 153 | 153 | 0 | public[0..1] | private[0..7] | Description is a password/device problem; no reliable K-integers contract. |
| 1311_F. Moving Points | FAIL: Python failed all executions; C++ bad 101 and failed/timeout on 81 | syntax valid; exec 182 | compiled; bad 101/exec 81 | 182 | 0 | public[0..1] | private[0..7] | Description concerns wizards/numbers, not Moving Points; replace record. |
| magic-gcd | FAIL: Python had one mismatch and 76 failures; C++ mismatched all 77 | syntax valid; bad 1/exec 76 | compiled; bad 77 | 77 | 0 | public[0..0] | private[0..7] | Description is a hard-version contest problem with unrelated multi-line tests; not canonical-ready. |

### Interpretation of test counts

The raw pair counts above are syntactically paired input/output entries. They
are not valid-test counts for V1. A test is strong only when the complete
record statement, reference behavior, expected output, and standalone stdin/
stdout contract agree. Under that standard, every candidate has zero approved
tests at this stage. Exact duplicate pair count was zero, but that does not
mitigate the cross-record corruption.

## B. Rejected candidates

All 25 candidates are rejected from Candidate Shortlist v0. The reasons are:

- cross-record identity corruption between name, description, tests, and
  references;
- reference execution failures or expected-output mismatches;
- at least one C++ compilation failure;
- apparent multi-problem concatenation or non-standard test serialization;
- inability to prove a standalone stdin/stdout contract;
- inability to identify two trustworthy public examples and eight hidden
  judge cases.

No candidate should be copied into `seed.py` or used as an oracle.

## C. Replacement candidates

No CodeContests row is approved as a direct replacement. The safe replacement
pool is project-authored, deterministic curriculum content with independently
written references and tests. If external discovery remains desirable, the
next candidates must be extracted from a verified official export and
revalidated record-by-record, rather than from this representation.

The following are replacement *concepts*, not imported CodeContests records:

- Arrays: Two Sum; Best Time to Buy and Sell Stock; Contains Duplicate;
  Product of Array Except Self; Maximum Subarray.
- Strings: Valid Anagram; Valid Palindrome; Longest Substring Without
  Repeating Characters; Group Anagrams; Longest Palindromic Substring.
- Linked List: Reverse Linked List; Merge Two Sorted Lists; Linked List
  Cycle; Remove Nth Node From End; Add Two Numbers.
- Stack & Queue: Valid Parentheses; Min Stack; Evaluate Reverse Polish
  Notation; Daily Temperatures; Sliding Window Maximum.
- Dynamic Programming: Climbing Stairs; House Robber; Coin Change; Longest
  Increasing Subsequence; Word Break.

## Curriculum-quality review

| Proposed category | Coherence | Progression | Technique diversity | V1 suitability | Decision |
|---|---|---|---|---|---|
| Arrays & Data Structures | Broad but foundational | Strong from scans to hashing/prefix structures | High | Excellent for simple stdin/stdout | Retain, with a narrower “Arrays” definition. |
| Strings | Coherent around sequence/text processing | Strong from frequency checks to windows and pattern methods | High | Excellent if serialization stays plain text | Retain. |
| Dynamic Programming | Coherent if scoped from 1D to state/compression | Strong when ordered from recurrence to optimization | High | Good, but avoid advanced contest-only statements | Retain. |
| Graphs & Trees | Coherent as a major domain | Can progress traversal → shortest path → DSU/tree DP | High | Good, but requires careful input contracts | Not recommended for the frozen five-topic V1 curriculum unless replacing a provisional topic explicitly. |
| Math & Number Theory | Too broad for one beginner-facing topic | Uneven; arithmetic and number theory have different prerequisites | Medium | Plain I/O is easy, but curriculum fit varies | Use techniques inside other topics or a later topic, not as a frozen core topic. |

Linked List and Stack & Queue should not be removed merely because this sample
has fewer matching records. They are pedagogically coherent, directly useful
for V1 practice, and support simple deterministic serialization. They should
remain in the core five-topic curriculum in place of Graphs & Trees and Math &
Number Theory.

## D. Final recommended five topics

1. Arrays
2. Strings
3. Linked List
4. Stack & Queue
5. Dynamic Programming

This preserves the provisional project curriculum and gives a better
beginner-to-intermediate progression than treating the noisy dataset's topic
frequency as the curriculum decision.

## E. Final recommended 25 problems

The following is a curriculum recommendation, not approval of the failed
CodeContests rows:

| Topic | Problems in progression order |
|---|---|
| Arrays | Two Sum; Best Time to Buy and Sell Stock; Contains Duplicate; Product of Array Except Self; Maximum Subarray |
| Strings | Valid Anagram; Valid Palindrome; Longest Substring Without Repeating Characters; Group Anagrams; Longest Palindromic Substring |
| Linked List | Reverse Linked List; Merge Two Sorted Lists; Linked List Cycle; Remove Nth Node From End; Add Two Numbers |
| Stack & Queue | Valid Parentheses; Min Stack; Evaluate Reverse Polish Notation; Daily Temperatures; Sliding Window Maximum |
| Dynamic Programming | Climbing Stairs; House Robber; Coin Change; Longest Increasing Subsequence; Word Break |

## F. Exact test-selection plan for each problem

For every replacement problem, create exactly ten hand-reviewed cases:

- cases 1–2: the two public examples, stored as `is_sample=true`,
  `run_enabled=true`, and `submit_enabled=true`;
- cases 3–10: eight independently designed hidden cases, stored as
  `is_sample=false`, `run_enabled=false`, and `submit_enabled=true`.

Each set must include minimum size, ordinary behavior, boundary values,
duplicates where meaningful, negative values where meaningful, empty/singleton
valid cases, and an adversarial case for the intended algorithm. All ten must
be executed against both trusted references before seeding. The mechanical
CodeContests indices in section A are not to be used because all 25 rows fail
this validation.

## G. Unresolved risks

- The 500-row representation appears to contain severe row-level corruption;
  its metadata cannot be treated as provenance for canonical content.
- A non-empty reference source is not evidence that the source matches the
  named problem or accepts the stored test format.
- Raw public/private/generated counts overstate usable tests when records are
  misjoined.
- Numeric source values in the representation require normalization against
  the official schema before any future discovery pass.
- Time and memory metadata are not actionable for these rows until problem
  identity and input contract are repaired.
- Custom-checker and interactive detection cannot be proven from this noisy
  representation alone.

## H. Conditions required before `seed.py` can be modified

1. Obtain a verified official dataset export or author the content in the
   repository; do not use this corrupted representation as a source.
2. Establish one complete, internally consistent record per problem:
   statement, input, output, constraints, limits, examples, and references.
3. Require standalone Python 3.12 and C++17 references to compile/run under
   the V1 stdin/stdout contract.
4. Independently validate all ten selected cases against both references and
   confirm exact expected outputs.
5. Confirm no interactive, output-only, custom-checker, file-I/O, or hidden
   serialization requirement exists.
6. Curate exactly two public/run cases and eight hidden/submit cases with the
   frozen flags.
7. Add focused static/reference validation before changing the seed
   reconciliation logic.
8. Only then update `seed.py`, with explicit reconciliation behavior and
   database verification performed in a separate authorized step.

