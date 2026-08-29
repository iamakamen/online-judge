# Canonical Metadata Completion v0

Metadata completion report for `canonical-problem-spec-v0.md`.

| Problem | Tags | Time | Memory | Constraints | Examples | Decision |
|---|---|---:|---:|---|---|---|
| A1 Two Sum | Hash Map; Complement Lookup; Index Tracking | 1000 ms | 128 MB | PASS | 2 explicit | Audited existing public cases retained |
| A2 Best Time to Buy and Sell Stock | Greedy; Prefix Minimum; Array Scan | 1000 ms | 128 MB | PASS | 2 explicit | Existing corpus retained |
| A3 Contains Duplicate | Hash Set; Membership Testing; Deduplication | 1000 ms | 128 MB | PASS | 2 explicit | Existing corpus retained |
| A4 Product of Array Except Self | Prefix Product; Suffix Product; Zero Handling | 1500 ms | 256 MB | PASS | 2 explicit | Existing corpus retained |
| A5 Maximum Subarray | Kadane Scan; Running Maximum; Contiguous Range | 1500 ms | 256 MB | PASS | 2 explicit | Existing corpus retained |
| S1 Valid Anagram | Frequency Counting; Character Multiset; Hash Table | 1000 ms | 128 MB | PASS | 2 explicit | Existing corpus retained |
| S2 Valid Palindrome | Two Pointers; Symmetry Check; String Scan | 1000 ms | 128 MB | PASS | 2 explicit | Existing corpus retained |
| S3 Longest Substring Without Repeating Characters | Sliding Window; Last-Seen Index; Distinct Characters | 1500 ms | 256 MB | PASS | 2 explicit | Existing corpus retained |
| S4 Group Anagrams | Canonical Key; Sorting; Deterministic Grouping | 1500 ms | 256 MB | PASS | 2 explicit | Existing deterministic ordering retained |
| S5 Longest Palindromic Substring | Center Expansion; Palindrome; Tie Breaking | 1500 ms | 256 MB | PASS | 2 explicit | Existing corpus retained |
| L1 Reverse Linked List | Pointer Reversal; Iteration; In-Place Update | 1000 ms | 128 MB | PASS | 2 explicit | Plain value serialization retained |
| L2 Merge Two Sorted Lists | Two Pointers; Stable Merge; Sorted Inputs | 1000 ms | 128 MB | PASS | 2 explicit | Empty-side serialization retained |
| L3 Linked List Cycle | Fast Slow Pointers; Cycle Detection; Index Encoding | 1000 ms | 128 MB | PASS | 2 explicit | Entry-index serialization retained |
| L4 Remove Nth Node From End | Two Pointers; Dummy Head; In-Place Deletion | 1500 ms | 256 MB | PASS | 2 explicit | Existing corpus retained |
| L5 Add Two Numbers | Carry Propagation; Digit Lists; Synchronized Traversal | 1500 ms | 256 MB | PASS | 2 explicit | Reverse-digit serialization retained |
| Q1 Valid Parentheses | Stack Matching; Delimiters; Nesting | 1000 ms | 128 MB | PASS | 2 explicit | Existing corpus retained |
| Q2 Min Stack | Stack Invariant; Minimum Tracking; Query Processing | 1000 ms | 128 MB | PASS | 2 explicit | Newline query output retained |
| Q3 Evaluate Reverse Polish Notation | Operand Stack; Postfix Evaluation; Truncating Division | 1500 ms | 256 MB | PASS | 2 explicit | Truncation contract retained |
| Q4 Daily Temperatures | Monotonic Stack; Next Greater Element; Deferred Resolution | 1500 ms | 256 MB | PASS | 2 explicit | Existing corpus retained |
| Q5 Sliding Window Maximum | Monotonic Deque; Sliding Window; Expiring Indices | 1500 ms | 256 MB | PASS | 2 explicit | Existing corpus retained |
| D1 Climbing Stairs | Fibonacci Recurrence; State Compression; Counting | 1000 ms | 128 MB | PASS | 2 explicit | Existing corpus retained |
| D2 House Robber | Non-Adjacent Selection; Rolling DP; Optimal Substructure | 1000 ms | 128 MB | PASS | 2 explicit | Existing corpus retained |
| D3 Coin Change | Unbounded Knapsack; Minimum Count; Bottom-Up DP | 1500 ms | 256 MB | PASS | 2 explicit | Existing corpus retained |
| D4 Longest Increasing Subsequence | Patience Sorting; Lower Bound; Subsequence Length | 1500 ms | 256 MB | PASS | 2 explicit | Existing corpus retained |
| D5 Word Break | Prefix DP; Dictionary Matching; Reusable Words | 1500 ms | 256 MB | PASS | 2 explicit | Existing corpus retained |

## Completion checks

- Topics: 5, with 5 problems each.
- Unique slugs: 25/25.
- Exactly three semantically useful tags: 25/25.
- Explicit per-problem time and memory limits: 25/25.
- Explicit constraints: 25/25.
- Explicit examples: 2/problem, 50 total.
- Existing validated test corpus changed: no.
- Existing Python/C++ references changed: no.
- Executable validator: fully green.
