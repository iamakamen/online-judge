# Canonical Dataset Validator Audit v0

This is a read-only audit of the validator and its first validation results.
The canonical specification was not changed.

## Validator audit

The validator was inspected and rerun against the unchanged specification.

| Check | Result |
|---|---:|
| Problem sections parsed | 25/25 |
| Cases parsed | 250/250 |
| Topics | 5; each has 5 problems |
| Cases per problem | 10/10 for every problem |
| Public cases | 2/problem |
| Hidden cases | 8/problem |
| Python references extracted | 25/25 |
| C++17 references extracted | 25/25 |
| Unique slugs | yes |
| Empty-output markers | correctly mapped from `*(empty)*` to empty stdout |
| Escaped table newlines | decoded to stdin newlines |
| Reference-source escaped newlines | preserved inside quoted literals and decoded outside literals |
| Expected outputs | 250/250 |
| Duplicate pairs | 0 |
| C++ compilation | 25/25 |
| Execution timeout | none |

The extraction behavior is evidenced by the Q2 failures: the validator ran the
literal Python `\\n` output and the literal C++ multi-character newline
expression exactly as represented in the specification. It did not silently
repair either reference.

During this audit, the isolated validator tooling exposed two extraction
issues in its first local run: inline reference labels were not recognized and
the `*(empty)*` table marker was omitted, producing a temporary 247-case run.
Those tooling defects were corrected in the validator before the final run.
The final authoritative run is the 250-case result reported below; the
temporary parser run is not used for any classification.

Whitespace comparison is intentionally `re.findall(r"\\S+", output)`. This
matches the specification's ordinary token-comparison policy. It deliberately
does not preserve line boundaries. That is safe for scalar and array outputs,
but it is weaker than the stated group-line semantics for Group Anagrams; this
is an open design concern, not a validator parsing defect.

The explicit constraint validators cover all 25 slugs, including array sizes,
value bounds, exact-pair uniqueness, string alphabets and lengths, sorted list
inputs, cycle indices, operation validity, RPN stack shape, coin counts,
dictionary counts, and DP bounds. No reported failure is caused by parsing or
constraint-validator logic.

Two latent validator-hardening notes remain: the stack-operation validator
could diagnose a negative stack size immediately after `pop`, and the RPN
validator could explicitly reject division by zero. Neither condition occurs
in the current 250 cases and neither caused a reported result.

## Validation summary

- Problems: 25/25
- Cases: 250/250
- Python executions: 250
- C++ executions: 250
- Python expected-output matches: 223/250
- C++ expected-output matches: 222/250
- Python/C++ matches: 222/250
- Constraint violations: 9
- Malformed cases: 0
- Python runtime failures: 1
- C++ runtime failures: 0
- C++ compilation failures: 0
- Timeouts: 0
- Duplicate pairs: 0
- Structural failures: 0

The validator itself exited nonzero, as required when acceptance conditions are
not all zero.

## Failure classification

Categories:

- **A** — incorrect expected output
- **B** — incorrect test input
- **C** — constraint violation
- **D** — incorrect Python reference implementation
- **E** — incorrect C++ reference implementation
- **F** — incorrect problem contract/serialization
- **G** — validator/parsing defect
- **H** — ambiguous specification requiring design decision

The primary category is assigned per validator failure record. Where one case
contains multiple independent artifact defects, the case is listed once for
the input/contract defect and the language-reference defects are listed as
separate artifact findings with their own category.

## Failures grouped by problem

### A1 — Two Sum

- **P2 — C: constraint violation.** Input `4 6 / 3 3 1 5` has two valid
  pairs: indices 0,1 and 2,3. The contract requires exactly one pair. The
  references return `0 1`, but the test input is invalid. Wrong artifact:
  test input. Correct behavior: replace the input with one having exactly one
  pair, or change the contract only with human approval.
- **H3 — A: incorrect expected output.** Input `6 -3 / 4 -7 8 1 -2 9` has
  the unique pair at indices `0 1`; both references return `0 1`, while the
  specification says `1 4`. Wrong artifact: expected output. Correct output:
  `0 1`.
- **H4 — C: constraint violation.** Input `6 14 / 9 8 5 6 1 13` has more
  than one valid pair, including `0 2` and `1 3`. Wrong artifact: test input
  and its uniqueness assumption. Correct behavior: replace the case with a
  unique-pair case.
- **H6 — C: constraint violation.** Input `8 2 / 0 0 0 1 1 4 -2 9` has
  multiple valid pairs, including `3 4` and `5 6`. Wrong artifact: test input.
  Correct behavior: replace it with one unique pair.
- **H8 — C: constraint violation.** Input `10 17 / 1 4 6 8 10 12 13 14 16
  7` has several valid pairs. Both references return `1 6`, while expected
  output is `1 8`. Wrong artifact: test input/uniqueness assumption. Replace
  the case with a unique-pair case.

### A2 — Best Time to Buy and Sell Stock

- **H8 — A: incorrect expected output.** Input `8 / 3 8 2 5 1 7 0 6` has
  maximum profit `6` (buy at 1, sell at 7). Both references return `6`; the
  specification says `7`. Wrong artifact: expected output. Correct output:
  `6`.

### A4 — Product of Array Except Self

- **H7 — A: incorrect expected output.** Input `4 / -10 -10 1 1` produces
  `-10 -10 100 100`, not `10 10 100 100`. Wrong artifact: expected output.
- **H8 — A: incorrect expected output.** Input `7 / 2 3 0 4 5 6 7` produces
  `0 0 5040 0 0 0 0`; the zero-exclusion product is 5040. Wrong artifact:
  expected output. This is not a reference zero-handling defect.

### S4 — Group Anagrams

- **P1 — A: incorrect expected output.** Input `6 / neat tea tan ate nat
  bat` groups as `ate tea`, `bat`, `nat tan`, and `neat`, sorted by each
  group's first word. Both references produce those tokens. The specification
  says `ate neat / bat / nat tan / tea`, which incorrectly treats `neat` and
  `ate` as anagrams and separates `tea`. Wrong artifact: expected output.
  Correct output lines are `ate tea`, `bat`, `nat tan`, `neat`.

### L4 — Remove Nth Node From End

- **H8 — A: incorrect expected output.** Input `8 6 / 8 1 6 2 7 3 5 4`
  removes the sixth node from the end, value `6`, producing `8 1 2 7 3 5
  4`. Both references agree. Wrong artifact: expected output.

### L5 — Add Two Numbers

- **H4 — A: incorrect expected output.** Input `3 5 / 1 2 3 / 9 9 9 9 9`
  represents 321 + 99999 = 100320, whose reverse digits are `0 2 3 0 0 1`.
  The specification omits the final carry and says `0 2 3 0 0`. Wrong
  artifact: expected output.

### Q2 — Min Stack

These failures expose two independent reference defects. The contract requires
one query answer per line. The Python source contains a literal escaped `\\n`
inside the join string and therefore emits backslash-n text. The C++ source
contains a literal escaped newline represented as a multi-character constant
and emits numeric garbage such as `23662` instead of line breaks.

- **P1 — D:** Python reference emits `1\\n3\\n3` instead of three lines.
  Expected is `1 / 3 / 3`. Wrong artifact: Python reference.
- **P1 — E:** C++ reference emits `123662323662323662` instead of three
  lines. Wrong artifact: C++ reference.
- **P2 — D:** Python reference emits `-2\\n-2` instead of two lines. Wrong
  artifact: Python reference.
- **P2 — E:** C++ reference emits `-223662-223662`. Wrong artifact: C++
  reference.
- **H1 — E:** Expected `0` and Python matches; C++ emits `023662`. Wrong
  artifact: C++ reference.
- **H2 — C:** Input has `pop` followed by `top` after the second and final
  item is removed, violating the contract that queries are valid. Wrong
  artifact: test input. The expected `5 / 5 / 5` is not defined for this
  invalid operation sequence.
- **H2 — E:** Independently, the C++ reference emits `5236625236623323662`
  rather than line-separated output. Wrong artifact: C++ reference.
- **H3 — D:** Python emits literal backslash-n separators. Wrong artifact:
  Python reference.
- **H3 — E:** C++ emits `223662223662423662`. Wrong artifact: C++ reference.
- **H4 — D:** Python emits literal backslash-n separators. Wrong artifact:
  Python reference.
- **H4 — E:** C++ emits `-523662-123662-123662`. Wrong artifact: C++ reference.
- **H5 — D:** Python emits literal backslash-n separators. Wrong artifact:
  Python reference.
- **H5 — E:** C++ emits `923662123662`. Wrong artifact: C++ reference.
- **H6 — C:** The header says `6` operations but only five operation lines
  follow. Wrong artifact: test input. Correct behavior: fix the header to `5`
  or add a sixth valid operation.
- **H6 — D:** Python emits literal backslash-n separators. Wrong artifact:
  Python reference.
- **H6 — E:** C++ emits numeric garbage between answers. Wrong artifact: C++
  reference.
- **H7 — C:** The header says `9` operations but only eight operation lines
  follow. Wrong artifact: test input. Correct behavior: fix the header or add
  one valid operation.
- **H7 — D:** Python emits literal backslash-n separators. Wrong artifact:
  Python reference.
- **H7 — E:** C++ emits numeric garbage between answers. Wrong artifact: C++
  reference.
- **H8 — C:** The header says `4` operations but five operation lines follow.
  Wrong artifact: test input. Correct behavior: set the header to `5`.
- **H8 — D:** Python emits literal backslash-n separators. Wrong artifact:
  Python reference.
- **H8 — E:** C++ emits `723662` rather than two line-separated answers.
  Wrong artifact: C++ reference.

### Q4 — Daily Temperatures

- **H7 — C: constraint violation.** Input contains temperatures `101` and
  `102`, outside the declared `-100..100` range. It also documents `3 1 1
  2 1 0`, while both references correctly compute `3 2 1 2 1 0` for the
  supplied values. Primary wrong artifact: test input. Replace with in-range
  values or update the declared constraints only by design approval.

### D1 — Climbing Stairs

- **H7 — A: incorrect expected output.** For `n=44`, the recurrence gives
  `1134903170`, not `701408733`.
- **H8 — A: incorrect expected output.** For `n=45`, the recurrence gives
  `1836311903`, not `1134903170`.

### D2 — House Robber

- **H3 — A: incorrect expected output.** Input `6 / 5 1 1 5 1 1` has
  optimum `11` by choosing values at indices 0, 3, and 5. The specification
  says `10`. Both references agree on `11`. Wrong artifact: expected output.

### D3 — Coin Change

- **H5 — A: incorrect expected output.** `27` can be formed as `20+5+2`, so
  the minimum is `3`, not `4`.
- **H6 — A: incorrect expected output.** `8` can be formed as `3+5`, so the
  result is `2`, not `-1`.
- **H7 — A: incorrect expected output.** `30` can be formed with five `6`
  coins, so the result is `5`, not `2`.

### D4 — Longest Increasing Subsequence

- **H8 — A: incorrect expected output.** Input `9 / 3 10 2 1 20 4 6 7 8`
  has LIS length `5`, for example `3,4,6,7,8`. Both references return `5`;
  the specification says `6`.

## Category totals

At the validator case-record level:

- **A — incorrect expected output:** 14 cases.
- **B — incorrect test input:** 0 cases independently classified as B;
  input defects are contract violations under C.
- **C — constraint violation:** 9 cases.
- **D — incorrect Python reference implementation:** Q2 output defects on
  8 cases. The invalid-input H2 runtime failure is not counted as a reference
  defect.
- **E — incorrect C++ reference implementation:** Q2 output defects on 10
  cases.
- **F — incorrect problem contract/serialization:** 0 current root failures;
  Q2's intended newline contract is clear, but the references violate it.
- **G — validator/parsing defect:** 0.
- **H — ambiguous design decision:** 0 current root failures. The Group
  Anagrams line-boundary weakness is a design concern, not an observed
  mismatch.

## Recommended correction order

1. Correct the Q2 Python and C++ reference source text and repair Q2 headers /
   invalid operations.
2. Repair the A1 invalid uniqueness cases and expected indices.
3. Correct all scalar/array expected outputs listed above.
4. Replace Q4 H7 with an in-range temperature case or explicitly revise its
   constraints.
5. Rerun the unchanged validator and require all acceptance counters to reach
   zero before any specification edit is made.

No corrections were applied by this audit.
