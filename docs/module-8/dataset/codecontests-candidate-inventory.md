# CodeContests Candidate Inventory

## Scope and provenance

This is a read-only candidate inventory for Online Judge V1. It does not alter application data or select final seed records.

The primary dataset is [DeepMind CodeContests on Hugging Face](https://huggingface.co/datasets/deepmind/code_contests), the dataset used for AlphaCode. The official repository describes the original release as Riegeli protocol buffers and approximately 3 GiB; its canonical schema is [contest_problem.proto](https://github.com/google-deepmind/code_contests/blob/main/contest_problem.proto).

To avoid the full download, this report analyzes the 500-row `train` slice of [TheFactoryX/edition_2104_deepmind-code_contests-readymade](https://huggingface.co/datasets/TheFactoryX/edition_2104_deepmind-code_contests-readymade), a Hugging Face Parquet representation derived from CodeContests. The official Hugging Face viewer reports 4,044 rows total: 3,762 train, 117 valid, and 165 test. Therefore all counts below describe the 500-row sample, not the entire official corpus.

Important limitation: reference availability is determined from the dataset language metadata and non-empty source text. Reference programs were not bulk-compiled or executed. Dataset source integers are retained as stored because the sampled community representation contains legacy/remapped values; source normalization must be verified before final adoption.

## Fields inspected

| Field | Use |
|---|---|
| `name` | candidate identity |
| `description` | usable problem statement |
| `source` | original source code |
| `difficulty` | original difficulty enum |
| `cf_rating` | Codeforces rating when present |
| `cf_tags` | original tags |
| `public_tests` | public input/output pairs |
| `private_tests` | private input/output pairs |
| `generated_tests` | generated input/output pairs |
| `solutions` | reference language/source metadata |
| `time_limit` | original duration |
| `memory_limit_bytes` | original memory limit |
| `input_file` | non-stdin input indicator |
| `output_file` | non-stdout output indicator |

## Filtering rules

Rules are applied in the following disjoint order so rejection counts sum to the sample size:

1. Reject non-empty `input_file` or `output_file`.
2. Reject missing/short descriptions (`description` shorter than 100 non-whitespace characters).
3. Reject records without at least one non-empty Python3 (`language=3`) or C++ (`language=2`) reference.
4. Reject malformed test collections: missing input/output arrays, unequal pair lengths, or non-string pair members.
5. Reject fewer than 10 usable input/output pairs across public, private, and generated tests. Counts are summed without deduplicating cross-source pairs.
6. Reject special-judging/interactive indicators: `*special` tags, `interactive` tags, or interactive/output-protocol terms in name/description.
7. Reject records that do not look suitable for a DSA curriculum under a keyword/tag semantic triage.

## Candidate counts

| Stage | Count |
|---|---:|
| Sample rows before filtering | 500 |
| Rejected: file-based I/O | 0 |
| Rejected: unusable description | 6 |
| Rejected: no Python3/C++ reference | 92 |
| Rejected: malformed tests | 0 |
| Rejected: fewer than 10 usable tests | 24 |
| Rejected: special/interactive judging | 20 |
| Rejected: not DSA-curriculum suitable | 54 |
| Surviving candidates | 304 |

The official corpus size is 4,044 rows, but no full-corpus filtering claim is made from this 500-row sample.

## Distribution of surviving candidates

### Topic/category distribution

| Category | Count |
|---|---:|
| Graphs & Trees | 114 |
| Math & Number Theory | 61 |
| Strings | 57 |
| Arrays & Data Structures | 47 |
| Dynamic Programming | 25 |

### Difficulty distribution

| Original difficulty | Count |
|---|---:|
| 0 (UNKNOWN) | 103 |
| 1 (EASY) | 1 |
| 10 (D) | 39 |
| 11 (E) | 24 |
| 12 (F) | 15 |
| 13 (G) | 4 |
| 14 (H) | 3 |
| 15 (I) | 1 |
| 17 (K) | 1 |
| 2 (MEDIUM) | 6 |
| 3 (HARD) | 1 |
| 6 (EXTERNAL) | 8 |
| 7 (A) | 39 |
| 8 (B) | 30 |
| 9 (C) | 29 |

### Test-count distribution

| Total usable pairs | Count |
|---|---:|
| 10–49 | 34 |
| 50–99 | 93 |
| 100–149 | 151 |
| 150+ | 23 |

### Reference availability

| Availability | Count |
|---|---:|
| Python3 and C++ | 210 |
| C++ only | 94 |
| Python3 only | 0 |
| Neither | 0 |

All survivors pass the file-I/O and special-judging filters, so `stdin/stdout` is `yes (heuristic)` for every inventory row. This is eligibility triage, not a correctness proof.

## Top candidates by recommended category

The following are discovery rankings, favoring available Codeforces ratings at or below 1800, then lower rating and larger test inventory. They require semantic review before final adoption.

### Arrays & Data Structures

| Candidate | Rating | Difficulty | Original tags | Total tests | References |
|---|---:|---|---|---:|---|
| p02445 Swap | 800 | 7 (A) | constructive algorithms, greedy, implementation | 116 | Python3 + C++ |
| 526_A. King of Thieves | 800 | 0 (UNKNOWN) | — | 104 | Python3 + C++ |
| even-from-end-1 | 1000 | 0 (UNKNOWN) | two pointers | 106 | Python3 + C++ |
| seg003 | 1000 | 8 (B) | — | 51 | Python3 + C++ |
| cdva1502 | 1300 | 2 (MEDIUM) | — | 73 | Python3 + C++ |
| 893_A. Chess For Three | 1500 | 7 (A) | greedy | 127 | Python3 + C++ |
| 1053_C. Putting Boxes Together | 1800 | 0 (UNKNOWN) | — | 105 | — + C++ |
| 784_B. Kids' Riddle | 1800 | 0 (UNKNOWN) | implementation | 103 | Python3 + C++ |
| mind-palaces-3 | 1800 | 14 (H) | — | 61 | Python3 + C++ |
| 909_D. Colorful Points | 1800 | 0 (UNKNOWN) | greedy, sortings | 58 | Python3 + C++ |

### Strings

| Candidate | Rating | Difficulty | Original tags | Total tests | References |
|---|---:|---|---|---:|---|
| p02257 Prime Numbers | 800 | 9 (C) | greedy, implementation, sortings, strings | 111 | — + C++ |
| playing-with-substrings | 800 | 8 (B) | — | 102 | Python3 + C++ |
| 990_B. Micro-World | 800 | 0 (UNKNOWN) | — | 39 | Python3 + C++ |
| 80_C. Heroes | 900 | 8 (B) | dsu, math | 112 | — + C++ |
| p03371 AtCoder Beginner Contest 095 - Half and Half | 1100 | 7 (A) | brute force, implementation, strings | 101 | Python3 + C++ |
| p01083 RedBlue | 1200 | 9 (C) | — | 102 | Python3 + C++ |
| p02744 Panasonic Programming Contest 2020 - String Equivalence | 1400 | 8 (B) | geometry, math | 102 | — + C++ |
| 914_F. Substrings in a String | 1500 | 11 (E) | — | 101 | Python3 + C++ |
| tf01 | 1500 | 0 (UNKNOWN) | brute force, implementation | 83 | Python3 + C++ |
| p01262 Adaptive Time Slicing Quantization | 1600 | 8 (B) | brute force, implementation, strings | 138 | Python3 + C++ |

### Dynamic Programming

| Candidate | Rating | Difficulty | Original tags | Total tests | References |
|---|---:|---|---|---:|---|
| 990_E. Post Lamps | 800 | 7 (A) | binary search, dp, sortings, two pointers | 106 | — + C++ |
| 1007_E. Mini Metro | 1400 | 7 (A) | dp, greedy | 59 | Python3 + C++ |
| p01694 Step Aerobics | 1500 | 7 (A) | — | 103 | — + C++ |
| 662_C. Binary Table | 2000 | 0 (UNKNOWN) | dp, implementation, math, number theory | 41 | Python3 + C++ |
| 203_E. Transportation | 2200 | 11 (E) | — | 101 | — + C++ |
| muffins3 | 2200 | 9 (C) | bitmasks, brute force, dp, math | 53 | Python3 + C++ |
| 151_C. Win or Freeze | 2400 | 10 (D) | dp, games | 31 | Python3 + C++ |
| 593_C. Beautiful Function | 2500 | 0 (UNKNOWN) | dp, greedy, sortings | 57 | Python3 + C++ |
| p00638 Old Bridges | 2800 | 9 (C) | brute force, dp, math, number theory | 10 | Python3 + C++ |

### Graphs & Trees

| Candidate | Rating | Difficulty | Original tags | Total tests | References |
|---|---:|---|---|---:|---|
| p03225 Tenka1 Programmer Contest - Equilateral | 800 | 8 (B) | brute force | 107 | Python3 + C++ |
| 536_C. Tavas and Pashmaks | 1000 | 0 (UNKNOWN) | dp, flows, graph matchings, greedy | 132 | — + C++ |
| 235_A. LCM Challenge | 1000 | 6 (EXTERNAL) | brute force, data structures, dsu, graphs, sortings | 68 | — + C++ |
| 1070_C. Cloud Computing | 1000 | 11 (E) | dfs and similar, graphs, trees | 62 | Python3 + C++ |
| 405_E. Graph Cutting | 1000 | 9 (C) | — | 36 | Python3 + C++ |
| 1075_D. Intersecting Subtrees | 1100 | 0 (UNKNOWN) | geometry, math | 223 | Python3 + C++ |
| 1081_D. Maximum Distance | 1100 | 11 (E) | flows, shortest paths | 103 | Python3 + C++ |
| 284_B. Cows and Poker Game | 1200 | 7 (A) | — | 126 | Python3 + C++ |
| 670_B. Game of Robots | 1300 | 0 (UNKNOWN) | dp, graphs, greedy, math, trees | 89 | — + C++ |
| p02879 AtCoder Beginner Contest 144 - 9x9 | 1300 | 7 (A) | implementation, strings | 68 | — + C++ |

### Math & Number Theory

| Candidate | Rating | Difficulty | Original tags | Total tests | References |
|---|---:|---|---|---:|---|
| 1490_G. Old Floppy Drive | 800 | 11 (E) | greedy | 52 | Python3 + C++ |
| 980_E. The Number Games | 800 | 8 (B) | — | 13 | Python3 + C++ |
| 1269_E. K Integers | 900 | 0 (UNKNOWN) | number theory | 153 | Python3 + C++ |
| 464_D. World of Darkraft - 2 | 900 | 8 (B) | constructive algorithms, dsu, math | 106 | Python3 + C++ |
| p03294 AtCoder Beginner Contest 103 - Modulo Summation | 900 | 7 (A) | — | 103 | Python3 + C++ |
| 643_B. Bear and Two Paths | 900 | 6 (EXTERNAL) | implementation | 60 | Python3 + C++ |
| 1037_E. Trips | 1000 | 0 (UNKNOWN) | binary search, geometry, ternary search | 89 | Python3 + C++ |
| 1311_F. Moving Points | 1100 | 9 (C) | — | 182 | Python3 + C++ |
| 626_D. Jerry's Protest | 1100 | 8 (B) | greedy, math | 154 | Python3 + C++ |

## Candidates with enough tests

All 308 survivors have at least 10 usable test pairs by construction. The exact per-candidate counts are in the inventory below. The recommended V1 shape still requires selecting exactly two public pairs and eight hidden pairs; the dataset’s public/private/generated partition does not directly satisfy that shape and must be curated.

## Problems lacking suitable Python3/C++ references

92 sample rows were rejected before survivorship because neither a non-empty Python3 nor a non-empty C++ reference was present. Examples include: p03150 KEYENCE Programming Contest 2019 - KEYENCE String, substrings-count-3, 931_A. Friends Meeting, 1165_A. Remainder, class-homework, p00860 The Morning after Halloween, 1297_E. Modernization of Treeland, etmx05, p02807 Dwango Programming Contest 6th - Fusing Slimes, 470_C. Eval, 1540_C1. Converging Array (Easy Version), p03889 CODE FESTIVAL 2016 Relay (Parallel) - Mirror String, p02610 AIsing Programming Contest 2020 - Camel Train, p03819 AtCoder Regular Contest 068 - Snuke Line, 45_H. Road Problem, p03107 AtCoder Beginner Contest 120 - Unification, 530_C. Diophantine equation, 1136_D. Nastya Is Buying Lunch, 105_C. Item World, 687_D. Dividing Kingdom II, p02652 AtCoder Grand Contest 045 - 01 Unbalanced, 1281_B. Azamon Web Services, 855_D. Rowena Ravenclaw's Diadem, max-min, chandu-and-daspal-2, 592_E. BCPC, 886_D. Restoration of string, 1455_F. String and Operations, 470_F. Pairwise Sums, 1012_E. Cycle sort, battle-of-stalingrad-1, p03616 AtCoder Regular Contest 082 - Sandglass, 5_A. Chat Server's Outgoing Traffic, pcsc1, 79_D. Password, ism1, 650_B. Image Preview, 1110_E. Magic Stones, 1043_A. Elections, 219_A. k-String, 1170_B. Bad Days, 385_A. Bear and Raspberry, 25_D. Roads not only in Berland, 720_C. Homework, 101_C. Vectors, 1264_A. Beautiful Regional Contest, 1081_G. Mergesort Strikes Back, golu-and-coins-1, brcktsrm, 814_C. An impassioned circulation of affection, 1107_D. Compression, 820_D. Mister B and PR Shifts, 188_G. Array Sorting, 1325_B. CopyCopyCopyCopyCopy, 656_E. Out of Controls, 519_B. A and B and Compilation Errors, 1391_C. Cyclic Permutations, 133_D. Piet, 76_B. Mice, 7_B. Memory Manager, 415_E. Mashmokh and Reverse Operation, p00127 Pocket Pager Input, p02548 AtCoder Beginner Contest 179 - A x B + C, 425_A. Sereja and Swaps, p03194 CADDi 2018 for Beginners - Product and GCD, simple-prime-factorization, 789_A. Anastasia and pebbles, 85_D. Sum of Medians, 545_C. Woodcutters, 180_D. Name, 1184_B3. The Doctor Meets Vader (Hard), 1285_C. Fadi and LCM, p00822 Weather Forecast, p01179 Cousin's Aunt, 560_D. Equivalent Strings, chsparr, list-sort, 1420_D. Rescue Nibel!, p00950 Infallibly Crack Perplexing Cryptarithm, 178_A1. Educational Game, 830_A. Office Keys, 20_B. Equation, comm3, 40_B. Repaintings, stadium, 316_B2. EKG, 195_A. Let's Watch Football, 319_B. Psychos in a Line, bhavanas-and-bhuvanas-bet, p03455 AtCoder Beginner Contest 086 - Product, 1354_F. Summoning Minions, p02260 Selection Sort.

## Problems requiring special judging

The primary filter rejected 20 rows for `*special` tags, `interactive` tags, or interactive/output-protocol indicators. The relevant retained names were: insect-colony-2, 915_A. Garden, 1334_A. Level Statistics, 1208_D. Restore Permutation, 1369_D. TediousLee, 455_C. Civilization, 633_H. Fibonacci-ish II, 143_A. Help Vasilisa the Wise 2, digital-numbers, p02741 Panasonic Programming Contest 2020 - Kth Term, 1334_D. Minimum Euler Cycle, p02613 AtCoder Beginner Contest 173 - Judge Status Summary, 1003_D. Coins and Queries, 331_E2. Deja Vu, 1277_E. Two Fairs, p03343 AtCoder Regular Contest 098 - Range Minimum Queries, 1291_B. Array Sharpening, 67_E. Save the City!, p02876 AtCoder Grand Contest 040 - Balance Beam, 295_D. Greg and Caves.

## Recommended five categories

1. Arrays & Data Structures — 48 survivors.
2. Strings — 57 survivors.
3. Dynamic Programming — 26 survivors.
4. Graphs & Trees — 115 survivors.
5. Math & Number Theory — 62 survivors.

These categories are better supported by the sampled corpus than the provisional Linked List and Stack & Queue categories. Linked-list and stack/queue concepts can still be authored manually, but they are not strong independent categories in this sample inventory.

## Recommended 25-problem shortlist

This is a candidate shortlist, not final canonical content. Every row has at least 10 usable pairs, empty file-I/O fields, no special-judging indicator under the stated heuristic, and both Python3/C++ references.

| Topic | Problem | Source | Original tags | Difficulty/rating | Public | Private | Generated | Total | Time | Memory | Python | C++ | stdin/stdout | Selection rationale |
|---|---|---|---|---|---:|---:|---:|---:|---|---|---|---|---|---|
| Arrays & Data Structures | even-from-end-1 | 2 (CODEFORCES/legacy-code) | two pointers | 0 (UNKNOWN) / 1000 | 3 | 3 | 100 | 106 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) | Basic two-pointer/array traversal candidate. |
| Arrays & Data Structures | p00167 Bubble Sort | 2 (CODEFORCES/legacy-code) | data structures, greedy, implementation | 10 (D) / — | 1 | 2 | 93 | 96 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) | Direct sorting and simulation candidate with both references. |
| Arrays & Data Structures | 433_A. Kitahara Haruki's Gift | 2 (CODEFORCES/legacy-code) | implementation | 3 (HARD) / 1900 | 1 | 0 | 100 | 101 | 3000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) | Small array partition/counting candidate. |
| Arrays & Data Structures | 893_A. Chess For Three | 2 (CODEFORCES/legacy-code) | greedy | 7 (A) / 1500 | 1 | 26 | 100 | 127 | 2000 ms | 1,073,741,824 bytes | yes | yes | yes (heuristic) | Simple state simulation suitable for an introductory problem. |
| Arrays & Data Structures | p02445 Swap | 2 (CODEFORCES/legacy-code) | constructive algorithms, greedy, implementation | 7 (A) / 800 | 1 | 15 | 100 | 116 | 6000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) | Greedy/implementation candidate with ample generated tests. |
| Strings | 977_B. Two-gram | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) / — | 1 | 30 | 99 | 130 | 3000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) | Short string-frequency problem with a large test inventory. |
| Strings | playing-with-substrings | 3 (HACKEREARTH/legacy-code) | — | 8 (B) / 800 | 1 | 1 | 100 | 102 | 2000 ms | 134,217,728 bytes | yes | yes | yes (heuristic) | Introductory substring candidate with both references. |
| Strings | p01083 RedBlue | 5 (ATCODER/legacy-code) | — | 9 (C) / 1200 | 2 | 0 | 100 | 102 | 1000 ms | 268,435,456 bytes | yes | yes | yes (heuristic) | String construction candidate with moderate rating. |
| Strings | 1140_B. Good String | 2 (CODEFORCES/legacy-code) | implementation, math | 8 (B) / — | 3 | 0 | 37 | 40 | 1000 ms | 512,000,000 bytes | yes | yes | yes (heuristic) | Compact string-processing candidate. |
| Strings | p00206 Next Trip | 5 (ATCODER/legacy-code) | implementation, sortings, strings | 8 (B) / — | 3 | 2 | 100 | 105 | 3000 ms | unknown | yes | yes | yes (heuristic) | String/sorting candidate with both references. |
| Dynamic Programming | 1007_E. Mini Metro | 2 (CODEFORCES/legacy-code) | dp, greedy | 7 (A) / 1400 | 1 | 30 | 28 | 59 | 2000 ms | unknown | yes | yes | yes (heuristic) | DP/greedy candidate with both references. |
| Dynamic Programming | muffins3 | 2 (CODEFORCES/legacy-code) | bitmasks, brute force, dp, math | 9 (C) / 2200 | 3 | 0 | 50 | 53 | 2000 ms | 1,073,741,824 bytes | yes | yes | yes (heuristic) | Bitmask DP candidate for a more advanced slot. |
| Dynamic Programming | 151_C. Win or Freeze | 6 (AIZU/legacy-code) | dp, games | 10 (D) / 2400 | 4 | 1 | 26 | 31 | 4000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) | DP/game-state candidate. |
| Dynamic Programming | 593_C. Beautiful Function | 3 (HACKEREARTH/legacy-code) | dp, greedy, sortings | 0 (UNKNOWN) / 2500 | 1 | 0 | 56 | 57 | 2000 ms | 134,217,728 bytes | yes | yes | yes (heuristic) | DP/greedy candidate with both references. |
| Dynamic Programming | p03771 AtCoder Grand Contest 012 - Camel and Oases | 2 (CODEFORCES/legacy-code) | data structures, dp, greedy | 10 (D) / — | 5 | 15 | 100 | 120 | unknown | unknown | yes | yes | yes (heuristic) | Advanced DP/data-structure candidate with 120 test pairs. |
| Graphs & Trees | 687_A. NP-Hard Problem | 2 (CODEFORCES/legacy-code) | — | 7 (A) / 1800 | 1 | 32 | 100 | 133 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) | Bipartite graph traversal candidate. |
| Graphs & Trees | 1081_D. Maximum Distance | 2 (CODEFORCES/legacy-code) | flows, shortest paths | 11 (E) / 1100 | 3 | 0 | 100 | 103 | 2000 ms | unknown | yes | yes | yes (heuristic) | Shortest-path/graph candidate with both references. |
| Graphs & Trees | 1070_C. Cloud Computing | 3 (HACKEREARTH/legacy-code) | dfs and similar, graphs, trees | 11 (E) / 1000 | 2 | 15 | 45 | 62 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) | Graph/tree candidate with both references. |
| Graphs & Trees | 284_B. Cows and Poker Game | 2 (CODEFORCES/legacy-code) | — | 7 (A) / 1200 | 1 | 25 | 100 | 126 | unknown | unknown | yes | yes | yes (heuristic) | Lower-rated graph/state candidate. |
| Graphs & Trees | 1398_A. Bad Triangle | 2 (CODEFORCES/legacy-code) | dsu, graphs, shortest paths, sortings | 14 (H) / 1600 | 2 | 0 | 91 | 93 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) | DSU/graph candidate with both references. |
| Math & Number Theory | p03294 AtCoder Beginner Contest 103 - Modulo Summation | 2 (CODEFORCES/legacy-code) | — | 7 (A) / 900 | 3 | 0 | 100 | 103 | 2500 ms | 536,870,912 bytes | yes | yes | yes (heuristic) | Lower-rated modular arithmetic candidate. |
| Math & Number Theory | 1490_G. Old Floppy Drive | 2 (CODEFORCES/legacy-code) | greedy | 11 (E) / 800 | 1 | 0 | 51 | 52 | 1000 ms | 134,217,728 bytes | yes | yes | yes (heuristic) | Greedy prefix-sum/query candidate. |
| Math & Number Theory | 1269_E. K Integers | 6 (AIZU/legacy-code) | number theory | 0 (UNKNOWN) / 900 | 3 | 50 | 100 | 153 | 3000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) | Number-theory candidate with 153 test pairs. |
| Math & Number Theory | 1311_F. Moving Points | 2 (CODEFORCES/legacy-code) | — | 9 (C) / 1100 | 2 | 80 | 100 | 182 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) | Counting/geometry candidate with 182 test pairs. |
| Math & Number Theory | magic-gcd | 1 (CODECHEF) | — | 9 (C) / 1100 | 1 | 18 | 58 | 77 | 8000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) | GCD candidate with both references. |

## Full surviving-candidate inventory

The following table contains every surviving row from the 500-row sample. It intentionally omits descriptions and test contents.

| Topic | Name | Source | cf_rating | Difficulty | Original tags | Public | Private | Generated | Total | Time | Memory | Python3 ref | C++ ref | stdin/stdout |
|---|---|---|---:|---|---|---:|---:|---:|---:|---|---|---|---|---|
| Arrays & Data Structures | 1027_E. Inverse Coloring | 2 (CODEFORCES/legacy-code) | — | 6 (EXTERNAL) | — | 2 | 12 | 100 | 114 | 2000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Arrays & Data Structures | 1053_C. Putting Boxes Together | 2 (CODEFORCES/legacy-code) | 1800 | 0 (UNKNOWN) | — | 2 | 3 | 100 | 105 | unknown | unknown | no | yes | yes (heuristic) |
| Arrays & Data Structures | 1091_G. New Year and the Factorisation Collaboration | 5 (ATCODER/legacy-code) | 2900 | 0 (UNKNOWN) | — | 1 | 10 | 52 | 63 | 2000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Arrays & Data Structures | 1100_D. Dasha and Chess | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | data structures, greedy, implementation | 3 | 0 | 100 | 103 | unknown | unknown | yes | yes | yes (heuristic) |
| Arrays & Data Structures | 1170_E. Sliding Doors | 6 (AIZU/legacy-code) | 2400 | 7 (A) | greedy | 2 | 45 | 79 | 126 | 2000 ms | 512,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | 1189_A. Keanu Reeves | 2 (CODEFORCES/legacy-code) | 2000 | 12 (F) | — | 3 | 1 | 100 | 104 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | 1216_D. Swords | 2 (CODEFORCES/legacy-code) | 3100 | 9 (C) | — | 4 | 10 | 49 | 63 | unknown | unknown | no | yes | yes (heuristic) |
| Arrays & Data Structures | 1386_A. Colors | 6 (AIZU/legacy-code) | 1900 | 0 (UNKNOWN) | data structures | 2 | 0 | 48 | 50 | 8000 ms | unknown | no | yes | yes (heuristic) |
| Arrays & Data Structures | 1439_C. Greedy Shopping | 6 (AIZU/legacy-code) | 2000 | 0 (UNKNOWN) | — | 3 | 0 | 200 | 203 | 2000 ms | 512,000,000 bytes | no | yes | yes (heuristic) |
| Arrays & Data Structures | 1466_C. Canine poetry | 2 (CODEFORCES/legacy-code) | 2700 | 0 (UNKNOWN) | — | 2 | 35 | 95 | 132 | 2000 ms | unknown | yes | yes | yes (heuristic) |
| Arrays & Data Structures | 1500_B. Two chandeliers | 6 (AIZU/legacy-code) | — | 0 (UNKNOWN) | greedy, implementation | 3 | 70 | 50 | 123 | unknown | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | 1513_C. Add One | 5 (ATCODER/legacy-code) | — | 8 (B) | brute force | 3 | 0 | 61 | 64 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | 157_A. Game Outcome | 3 (HACKEREARTH/legacy-code) | 2100 | 0 (UNKNOWN) | data structures, greedy | 1 | 8 | 100 | 109 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | 167_C. Wizards and Numbers | 2 (CODEFORCES/legacy-code) | 3000 | 9 (C) | data structures | 1 | 16 | 46 | 63 | 6000 ms | unknown | yes | yes | yes (heuristic) |
| Arrays & Data Structures | 248_A. Cupboards | 6 (AIZU/legacy-code) | 2000 | 8 (B) | greedy, sortings, two pointers | 3 | 48 | 92 | 143 | unknown | 256,000,000 bytes | no | yes | yes (heuristic) |
| Arrays & Data Structures | 378_C. Maze | 6 (AIZU/legacy-code) | 2800 | 8 (B) | brute force | 3 | 7 | 54 | 64 | 2000 ms | 134,217,728 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | 433_A. Kitahara Haruki's Gift | 2 (CODEFORCES/legacy-code) | 1900 | 3 (HARD) | implementation | 1 | 0 | 100 | 101 | 3000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | 526_A. King of Thieves | 3 (HACKEREARTH/legacy-code) | 800 | 0 (UNKNOWN) | — | 3 | 1 | 100 | 104 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | 609_B. The Best Gift | 2 (CODEFORCES/legacy-code) | — | 10 (D) | — | 1 | 14 | 100 | 115 | 1000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Arrays & Data Structures | 634_C. Factory Repairs | 2 (CODEFORCES/legacy-code) | 2300 | 11 (E) | — | 2 | 34 | 98 | 134 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | 730_J. Bottles | 1 (CODECHEF) | 2200 | 9 (C) | implementation | 2 | 0 | 100 | 102 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | 784_B. Kids' Riddle | 2 (CODEFORCES/legacy-code) | 1800 | 0 (UNKNOWN) | implementation | 3 | 0 | 100 | 103 | 2000 ms | 134,217,728 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | 820_A. Mister B and Book Reading | 2 (CODEFORCES/legacy-code) | 1900 | 11 (E) | data structures, implementation | 2 | 0 | 43 | 45 | 5000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Arrays & Data Structures | 893_A. Chess For Three | 2 (CODEFORCES/legacy-code) | 1500 | 7 (A) | greedy | 1 | 26 | 100 | 127 | 2000 ms | 1,073,741,824 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | 909_D. Colorful Points | 1 (CODECHEF) | 1800 | 0 (UNKNOWN) | greedy, sortings | 1 | 20 | 37 | 58 | 1000 ms | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | appu-and-sugarcane-farm | 3 (HACKEREARTH/legacy-code) | — | 9 (C) | brute force, greedy | 1 | 28 | 72 | 101 | 1000 ms | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | bogosort | 2 (CODEFORCES/legacy-code) | — | 10 (D) | — | 2 | 20 | 88 | 110 | 1000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Arrays & Data Structures | cdva1502 | 2 (CODEFORCES/legacy-code) | 1300 | 2 (MEDIUM) | — | 3 | 26 | 44 | 73 | 2000 ms | 64,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | even-from-end-1 | 2 (CODEFORCES/legacy-code) | 1000 | 0 (UNKNOWN) | two pointers | 3 | 3 | 100 | 106 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | gameaam | 2 (CODEFORCES/legacy-code) | 2300 | 0 (UNKNOWN) | bitmasks, dp | 1 | 0 | 100 | 101 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | give-me-my-test-monk | 2 (CODEFORCES/legacy-code) | — | 10 (D) | dp | 2 | 34 | 0 | 36 | unknown | 268,435,456 bytes | no | yes | yes (heuristic) |
| Arrays & Data Structures | laddu | 6 (AIZU/legacy-code) | 2100 | 9 (C) | — | 1 | 2 | 42 | 45 | unknown | 512,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | mind-palaces-3 | 2 (CODEFORCES/legacy-code) | 1800 | 14 (H) | — | 3 | 1 | 57 | 61 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | p00167 Bubble Sort | 2 (CODEFORCES/legacy-code) | — | 10 (D) | data structures, greedy, implementation | 1 | 2 | 93 | 96 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | p00320 Cuboid | 2 (CODEFORCES/legacy-code) | — | 7 (A) | binary search, greedy, ternary search | 1 | 34 | 64 | 99 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | p00323 Metal Recycling | 5 (ATCODER/legacy-code) | 2600 | 0 (UNKNOWN) | binary search, greedy, sortings | 1 | 0 | 45 | 46 | 2000 ms | unknown | no | yes | yes (heuristic) |
| Arrays & Data Structures | p01646 Dictionary | 2 (CODEFORCES/legacy-code) | 2000 | 10 (D) | — | 1 | 46 | 52 | 99 | unknown | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | p01838 Optimal Tournament | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | — | 2 | 0 | 59 | 61 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | p02014 Rough Sorting | 1 (CODECHEF) | — | 0 (UNKNOWN) | — | 2 | 21 | 100 | 123 | 10000 ms | 536,870,912 bytes | no | yes | yes (heuristic) |
| Arrays & Data Structures | p02445 Swap | 2 (CODEFORCES/legacy-code) | 800 | 7 (A) | constructive algorithms, greedy, implementation | 1 | 15 | 100 | 116 | 6000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | p03080 ExaWizards 2019 - Red or Blue | 5 (ATCODER/legacy-code) | — | 0 (UNKNOWN) | — | 2 | 41 | 53 | 96 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | p03153 KEYENCE Programming Contest 2019 - Connecting Cities | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | — | 3 | 0 | 69 | 72 | 2000 ms | unknown | no | yes | yes (heuristic) |
| Arrays & Data Structures | p03254 AtCoder Grand Contest 027 - Candy Distribution Again | 2 (CODEFORCES/legacy-code) | 2100 | 10 (D) | data structures | 1 | 37 | 200 | 238 | 2000 ms | unknown | no | yes | yes (heuristic) |
| Arrays & Data Structures | prpaln | 2 (CODEFORCES/legacy-code) | 2300 | 9 (C) | — | 1 | 0 | 100 | 101 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | seg003 | 2 (CODEFORCES/legacy-code) | 1000 | 8 (B) | — | 1 | 2 | 48 | 51 | unknown | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Arrays & Data Structures | sherlock-and-kgb | 2 (CODEFORCES/legacy-code) | 2000 | 13 (G) | brute force, sortings | 3 | 0 | 100 | 103 | 2000 ms | 268,435,456 bytes | no | yes | yes (heuristic) |
| Arrays & Data Structures | vowel | 5 (ATCODER/legacy-code) | — | 10 (D) | — | 4 | 0 | 100 | 104 | 2000 ms | 64,000,000 bytes | yes | yes | yes (heuristic) |
| Dynamic Programming | 1007_E. Mini Metro | 2 (CODEFORCES/legacy-code) | 1400 | 7 (A) | dp, greedy | 1 | 30 | 28 | 59 | 2000 ms | unknown | yes | yes | yes (heuristic) |
| Dynamic Programming | 1129_A2. Toy Train | 5 (ATCODER/legacy-code) | — | 0 (UNKNOWN) | brute force, implementation, strings | 2 | 22 | 100 | 124 | 1000 ms | 134,217,728 bytes | no | yes | yes (heuristic) |
| Dynamic Programming | 1227_D1. Optimal Subsequences (Easy Version) | 5 (ATCODER/legacy-code) | — | 0 (UNKNOWN) | — | 4 | 5 | 41 | 50 | 1000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Dynamic Programming | 1382_A. Common Subsequence | 5 (ATCODER/legacy-code) | 3100 | 10 (D) | — | 1 | 0 | 100 | 101 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Dynamic Programming | 151_C. Win or Freeze | 6 (AIZU/legacy-code) | 2400 | 10 (D) | dp, games | 4 | 1 | 26 | 31 | 4000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Dynamic Programming | 168_A. Wizards and Demonstration | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | bitmasks, brute force, divide and conquer, dp, fft, math | 2 | 20 | 100 | 122 | 2000 ms | unknown | yes | yes | yes (heuristic) |
| Dynamic Programming | 203_E. Transportation | 2 (CODEFORCES/legacy-code) | 2200 | 11 (E) | — | 1 | 0 | 100 | 101 | 1000 ms | unknown | no | yes | yes (heuristic) |
| Dynamic Programming | 209_B. Pixels | 5 (ATCODER/legacy-code) | — | 10 (D) | dp, probabilities | 1 | 24 | 100 | 125 | unknown | 1,073,741,824 bytes | yes | yes | yes (heuristic) |
| Dynamic Programming | 277_C. Game | 2 (CODEFORCES/legacy-code) | — | 9 (C) | — | 1 | 70 | 74 | 145 | 1000 ms | unknown | no | yes | yes (heuristic) |
| Dynamic Programming | 331_D2. Escaping on Beaveractor | 3 (HACKEREARTH/legacy-code) | — | 7 (A) | — | 3 | 13 | 100 | 116 | 2000 ms | 1,073,741,824 bytes | yes | yes | yes (heuristic) |
| Dynamic Programming | 442_C. Artem and Array | 3 (HACKEREARTH/legacy-code) | — | 10 (D) | implementation | 4 | 7 | 100 | 111 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Dynamic Programming | 593_C. Beautiful Function | 3 (HACKEREARTH/legacy-code) | 2500 | 0 (UNKNOWN) | dp, greedy, sortings | 1 | 0 | 56 | 57 | 2000 ms | 134,217,728 bytes | yes | yes | yes (heuristic) |
| Dynamic Programming | 662_C. Binary Table | 3 (HACKEREARTH/legacy-code) | 2000 | 0 (UNKNOWN) | dp, implementation, math, number theory | 2 | 2 | 37 | 41 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Dynamic Programming | 851_B. Arpa and an exam about geometry | 1 (CODECHEF) | — | 8 (B) | dp, greedy, strings | 2 | 46 | 42 | 90 | 2000 ms | 536,870,912 bytes | yes | yes | yes (heuristic) |
| Dynamic Programming | 937_D. Sleepy Game | 2 (CODEFORCES/legacy-code) | — | 11 (E) | brute force, dp, strings, two pointers | 2 | 3 | 100 | 105 | 2000 ms | 512,000,000 bytes | yes | yes | yes (heuristic) |
| Dynamic Programming | 990_E. Post Lamps | 2 (CODEFORCES/legacy-code) | 800 | 7 (A) | binary search, dp, sortings, two pointers | 1 | 5 | 100 | 106 | 2000 ms | unknown | no | yes | yes (heuristic) |
| Dynamic Programming | muffins3 | 2 (CODEFORCES/legacy-code) | 2200 | 9 (C) | bitmasks, brute force, dp, math | 3 | 0 | 50 | 53 | 2000 ms | 1,073,741,824 bytes | yes | yes | yes (heuristic) |
| Dynamic Programming | p00638 Old Bridges | 5 (ATCODER/legacy-code) | 2800 | 9 (C) | brute force, dp, math, number theory | 3 | 7 | 0 | 10 | unknown | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Dynamic Programming | p00720 Earth Observation with a Mobile Robot Team | 2 (CODEFORCES/legacy-code) | — | 7 (A) | brute force, combinatorics, dp, probabilities | 3 | 45 | 100 | 148 | unknown | 134,217,728 bytes | no | yes | yes (heuristic) |
| Dynamic Programming | p01694 Step Aerobics | 2 (CODEFORCES/legacy-code) | 1500 | 7 (A) | — | 3 | 0 | 100 | 103 | 5000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Dynamic Programming | p01738 Gravity Point | 1 (CODECHEF) | — | 12 (F) | combinatorics, dp, math, probabilities | 1 | 0 | 46 | 47 | 1000 ms | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Dynamic Programming | p03771 AtCoder Grand Contest 012 - Camel and Oases | 2 (CODEFORCES/legacy-code) | — | 10 (D) | data structures, dp, greedy | 5 | 15 | 100 | 120 | unknown | unknown | yes | yes | yes (heuristic) |
| Dynamic Programming | p03940 AtCoder Grand Contest 007 - Shik and Game | 2 (CODEFORCES/legacy-code) | — | 7 (A) | dp, implementation | 3 | 1 | 100 | 104 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Dynamic Programming | professor-sharma | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | binary search, brute force, dp, two pointers | 1 | 2 | 200 | 203 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Dynamic Programming | rams-love-for-sita-2 | 2 (CODEFORCES/legacy-code) | — | 10 (D) | dp, math | 1 | 0 | 75 | 76 | 4000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 1046_D. Interstellar battle | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | constructive algorithms, implementation | 1 | 0 | 100 | 101 | 1000 ms | 1,073,741,824 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 1065_F. Up and Down the Tree | 5 (ATCODER/legacy-code) | — | 0 (UNKNOWN) | — | 2 | 0 | 53 | 55 | 5000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 1070_C. Cloud Computing | 3 (HACKEREARTH/legacy-code) | 1000 | 11 (E) | dfs and similar, graphs, trees | 2 | 15 | 45 | 62 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 1075_D. Intersecting Subtrees | 3 (HACKEREARTH/legacy-code) | 1100 | 0 (UNKNOWN) | geometry, math | 3 | 20 | 200 | 223 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 1081_D. Maximum Distance | 2 (CODEFORCES/legacy-code) | 1100 | 11 (E) | flows, shortest paths | 3 | 0 | 100 | 103 | 2000 ms | unknown | yes | yes | yes (heuristic) |
| Graphs & Trees | 1096_E. The Top Scorer | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | combinatorics, dp, graphs, math | 4 | 25 | 100 | 129 | unknown | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 1101_A. Minimum Integer | 2 (CODEFORCES/legacy-code) | 2100 | 0 (UNKNOWN) | — | 2 | 0 | 85 | 87 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 1144_B. Parity Alternated Deletions | 6 (AIZU/legacy-code) | 1600 | 10 (D) | brute force, sortings | 3 | 0 | 20 | 23 | 1000 ms | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 1155_A. Reverse a Substring | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | constructive algorithms, dfs and similar, dsu, graphs, matrices | 1 | 9 | 53 | 63 | 1000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 1199_E. Matching vs Independent Set | 2 (CODEFORCES/legacy-code) | 2400 | 11 (E) | data structures, trees | 5 | 4 | 100 | 109 | 1000 ms | 1,073,741,824 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 1202_C. You Are Given a WASD-string... | 3 (HACKEREARTH/legacy-code) | — | 11 (E) | — | 3 | 2 | 100 | 105 | 2000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 1208_A. XORinacci | 2 (CODEFORCES/legacy-code) | 2200 | 7 (A) | combinatorics, dp, trees | 1 | 0 | 46 | 47 | 1000 ms | 1,073,741,824 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 1211_I. Unusual Graph | 2 (CODEFORCES/legacy-code) | 3000 | 0 (UNKNOWN) | — | 3 | 0 | 46 | 49 | 2000 ms | 1,073,741,824 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 1219_H. Function Composition | 2 (CODEFORCES/legacy-code) | 2500 | 0 (UNKNOWN) | trees | 2 | 43 | 19 | 64 | 2000 ms | 512,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 1227_A. Math Problem | 2 (CODEFORCES/legacy-code) | 2300 | 11 (E) | data structures, greedy, sortings | 2 | 221 | 38 | 261 | 1500 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 1239_E. Turtle | 2 (CODEFORCES/legacy-code) | 1700 | 0 (UNKNOWN) | graphs, shortest paths | 1 | 1 | 100 | 102 | 1000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 1244_C. The Football Season | 2 (CODEFORCES/legacy-code) | — | 9 (C) | binary search, brute force, geometry, math | 1 | 8 | 44 | 53 | 2000 ms | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 124_D. Squares | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | — | 1 | 1 | 69 | 71 | 1000 ms | 512,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 1301_B. Motarack's Birthday | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | — | 4 | 1 | 100 | 105 | 3000 ms | unknown | yes | yes | yes (heuristic) |
| Graphs & Trees | 1304_E. 1-Trees and Queries | 2 (CODEFORCES/legacy-code) | — | 10 (D) | math, probabilities, trees | 3 | 0 | 100 | 103 | unknown | unknown | yes | yes | yes (heuristic) |
| Graphs & Trees | 1311_C. Perform the Combo | 2 (CODEFORCES/legacy-code) | 2500 | 10 (D) | — | 1 | 0 | 100 | 101 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 1320_F. Blocks and Sensors | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | dfs and similar, dp, trees | 1 | 0 | 84 | 85 | 1000 ms | 1,073,741,824 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 1348_F. Phoenix and Memory | 2 (CODEFORCES/legacy-code) | 2500 | 11 (E) | bitmasks, dfs and similar, dsu, graphs, greedy, math, sortings | 2 | 1 | 98 | 101 | unknown | 134,217,728 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 1374_B. Multiply by 2, divide by 6 | 3 (HACKEREARTH/legacy-code) | 1800 | 6 (EXTERNAL) | brute force, constructive algorithms, implementation, strings | 4 | 67 | 100 | 171 | 2000 ms | unknown | yes | yes | yes (heuristic) |
| Graphs & Trees | 1374_E1. Reading Books (easy version) | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | binary search, data structures | 3 | 9 | 96 | 108 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 1398_A. Bad Triangle | 2 (CODEFORCES/legacy-code) | 1600 | 14 (H) | dsu, graphs, shortest paths, sortings | 2 | 0 | 91 | 93 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 1402_A. Fancy Fence | 2 (CODEFORCES/legacy-code) | 3100 | 7 (A) | constructive algorithms, dp, flows, graph matchings, greedy, sortings | 2 | 0 | 100 | 102 | 4000 ms | unknown | no | yes | yes (heuristic) |
| Graphs & Trees | 1413_F. Roads and Ramen | 2 (CODEFORCES/legacy-code) | 1900 | 9 (C) | — | 2 | 0 | 41 | 43 | 3000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 1428_D. Bouncing Boomerangs | 2 (CODEFORCES/legacy-code) | — | 2 (MEDIUM) | graphs, greedy, sortings | 2 | 0 | 100 | 102 | 2000 ms | unknown | yes | yes | yes (heuristic) |
| Graphs & Trees | 1431_I. Cyclic Shifts | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | data structures, greedy, trees | 1 | 10 | 16 | 27 | 1000 ms | 1,073,741,824 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 1451_D. Circle Game | 6 (AIZU/legacy-code) | 1800 | 7 (A) | implementation, strings | 2 | 24 | 0 | 26 | 2000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 1497_D. Genius | 5 (ATCODER/legacy-code) | 2900 | 0 (UNKNOWN) | brute force, implementation | 2 | 0 | 86 | 88 | 500 ms | 134,217,728 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 1512_G. Short Task | 3 (HACKEREARTH/legacy-code) | — | 10 (D) | dfs and similar, dsu, graphs | 1 | 26 | 64 | 91 | 1000 ms | 1,073,741,824 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 152_E. Garden | 2 (CODEFORCES/legacy-code) | 2000 | 0 (UNKNOWN) | dfs and similar, dsu, graphs | 3 | 16 | 100 | 119 | 5000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 161_B. Discounts | 6 (AIZU/legacy-code) | 1400 | 0 (UNKNOWN) | binary search, graphs, matrices | 1 | 21 | 100 | 122 | 2000 ms | 512,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 174_E. Ancient Berland Hieroglyphs | 2 (CODEFORCES/legacy-code) | 1900 | 9 (C) | — | 1 | 2 | 100 | 103 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 188_D. Asterisks | 2 (CODEFORCES/legacy-code) | 2600 | 0 (UNKNOWN) | bitmasks, dp, shortest paths | 3 | 41 | 100 | 144 | 2000 ms | unknown | yes | yes | yes (heuristic) |
| Graphs & Trees | 235_A. LCM Challenge | 2 (CODEFORCES/legacy-code) | 1000 | 6 (EXTERNAL) | brute force, data structures, dsu, graphs, sortings | 2 | 5 | 61 | 68 | 2525 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 235_D. Graph Game | 2 (CODEFORCES/legacy-code) | 2400 | 0 (UNKNOWN) | graphs | 4 | 33 | 100 | 137 | 2000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 252_B. Unsorting Array | 6 (AIZU/legacy-code) | — | 12 (F) | — | 1 | 0 | 100 | 101 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 272_B. Dima and Sequence | 2 (CODEFORCES/legacy-code) | 1700 | 0 (UNKNOWN) | constructive algorithms, graphs, implementation | 3 | 0 | 100 | 103 | 1000 ms | 134,217,728 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 284_B. Cows and Poker Game | 2 (CODEFORCES/legacy-code) | 1200 | 7 (A) | — | 1 | 25 | 100 | 126 | unknown | unknown | yes | yes | yes (heuristic) |
| Graphs & Trees | 306_C. White, Black and White Again | 3 (HACKEREARTH/legacy-code) | — | 0 (UNKNOWN) | dfs and similar | 3 | 0 | 100 | 103 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 309_B. Context Advertising | 3 (HACKEREARTH/legacy-code) | 1700 | 0 (UNKNOWN) | constructive algorithms, graphs, math, shortest paths, sortings | 2 | 0 | 100 | 102 | 3000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 323_C. Two permutations | 2 (CODEFORCES/legacy-code) | 1900 | 12 (F) | — | 2 | 0 | 59 | 61 | 5000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 343_B. Alternating Current | 1 (CODECHEF) | — | 11 (E) | dfs and similar, graphs, hashing, shortest paths | 3 | 42 | 46 | 91 | unknown | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 354_B. Game with Strings | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | — | 1 | 0 | 200 | 201 | 2000 ms | 134,217,728 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 354_E. Lucky Number Representation | 2 (CODEFORCES/legacy-code) | 2900 | 10 (D) | implementation | 2 | 11 | 85 | 98 | 3000 ms | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 366_D. Dima and Trap Graph | 2 (CODEFORCES/legacy-code) | — | 1 (EASY) | — | 1 | 0 | 32 | 33 | unknown | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 379_A. New Year Candles | 1 (CODECHEF) | 2200 | 11 (E) | data structures, dfs and similar, dp, trees | 2 | 4 | 100 | 106 | 8000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 38_C. Blinds | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | binary search, brute force, implementation | 1 | 2 | 100 | 103 | 1000 ms | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 405_E. Graph Cutting | 6 (AIZU/legacy-code) | 1000 | 9 (C) | — | 1 | 35 | 0 | 36 | 5000 ms | 512,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 425_D. Sereja and Squares | 2 (CODEFORCES/legacy-code) | 2500 | 6 (EXTERNAL) | greedy, strings | 3 | 16 | 100 | 119 | 500 ms | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 449_D. Jzzhu and Numbers | 2 (CODEFORCES/legacy-code) | 3400 | 9 (C) | — | 1 | 0 | 100 | 101 | 1000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 44_B. Cola | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | implementation, math | 2 | 0 | 60 | 62 | unknown | unknown | yes | yes | yes (heuristic) |
| Graphs & Trees | 483_B. Friends and Presents | 1 (CODECHEF) | — | 12 (F) | dfs and similar, divide and conquer, implementation | 1 | 55 | 94 | 150 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 494_D. Birthday | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | — | 4 | 14 | 100 | 118 | unknown | unknown | yes | yes | yes (heuristic) |
| Graphs & Trees | 536_C. Tavas and Pashmaks | 2 (CODEFORCES/legacy-code) | 1000 | 0 (UNKNOWN) | dp, flows, graph matchings, greedy | 1 | 31 | 100 | 132 | 2000 ms | 268,435,456 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 578_C. Weakness and Poorness | 2 (CODEFORCES/legacy-code) | 1500 | 7 (A) | graphs | 3 | 0 | 97 | 100 | 2000 ms | unknown | no | yes | yes (heuristic) |
| Graphs & Trees | 604_A. Uncowed Forces | 2 (CODEFORCES/legacy-code) | 2500 | 0 (UNKNOWN) | binary search, combinatorics, data structures, dp, graphs, implementation, two pointers | 2 | 0 | 54 | 56 | unknown | unknown | no | yes | yes (heuristic) |
| Graphs & Trees | 615_A. Bulbs | 5 (ATCODER/legacy-code) | — | 11 (E) | — | 1 | 0 | 48 | 49 | 1000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 670_B. Game of Robots | 5 (ATCODER/legacy-code) | 1300 | 0 (UNKNOWN) | dp, graphs, greedy, math, trees | 3 | 38 | 48 | 89 | 2000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 675_E. Trains and Statistic | 2 (CODEFORCES/legacy-code) | 2200 | 0 (UNKNOWN) | brute force, constructive algorithms, math | 4 | 0 | 100 | 104 | 2000 ms | 134,217,728 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 687_A. NP-Hard Problem | 2 (CODEFORCES/legacy-code) | 1800 | 7 (A) | — | 1 | 32 | 100 | 133 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 702_E. Analysis of Pathes in Functional Graph | 3 (HACKEREARTH/legacy-code) | — | 7 (A) | — | 1 | 43 | 80 | 124 | 2000 ms | unknown | no | yes | yes (heuristic) |
| Graphs & Trees | 724_F. Uniformly Branched Trees | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | — | 2 | 11 | 45 | 58 | 2000 ms | 268,435,456 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 746_F. Music in Car | 2 (CODEFORCES/legacy-code) | — | 9 (C) | — | 3 | 1 | 200 | 204 | 2000 ms | 512,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 776_A. A Serial Killer | 2 (CODEFORCES/legacy-code) | 1900 | 12 (F) | constructive algorithms, expression parsing, greedy, math | 1 | 86 | 43 | 130 | 2000 ms | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 805_A. Fake NP | 2 (CODEFORCES/legacy-code) | 1600 | 10 (D) | binary search, dp, greedy, sortings | 1 | 8 | 69 | 78 | 2000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | 846_E. Chemistry in Berland | 2 (CODEFORCES/legacy-code) | 2400 | 6 (EXTERNAL) | — | 1 | 14 | 100 | 115 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 868_A. Bark to Unlock | 2 (CODEFORCES/legacy-code) | 1700 | 11 (E) | implementation | 2 | 5 | 100 | 107 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 925_E. May Holidays | 6 (AIZU/legacy-code) | — | 10 (D) | graphs | 1 | 0 | 100 | 101 | 2000 ms | unknown | yes | yes | yes (heuristic) |
| Graphs & Trees | 938_B. Run For Your Prize | 1 (CODECHEF) | — | 0 (UNKNOWN) | bitmasks, dp, graphs, number theory | 3 | 29 | 100 | 132 | unknown | unknown | no | yes | yes (heuristic) |
| Graphs & Trees | 949_C. Data Center Maintenance | 2 (CODEFORCES/legacy-code) | 1900 | 8 (B) | brute force, greedy | 1 | 0 | 100 | 101 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 962_F. Simple Cycles Edges | 2 (CODEFORCES/legacy-code) | — | 11 (E) | greedy | 1 | 10 | 49 | 60 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 963_B. Destruction of a Tree | 2 (CODEFORCES/legacy-code) | 2600 | 9 (C) | — | 2 | 20 | 100 | 122 | 2000 ms | 536,870,912 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 996_F. Game | 2 (CODEFORCES/legacy-code) | 1700 | 0 (UNKNOWN) | graphs | 1 | 17 | 50 | 68 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | 9_E. Interesting Graph and Apples | 2 (CODEFORCES/legacy-code) | — | 6 (EXTERNAL) | — | 2 | 4 | 56 | 62 | 8000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | ankit-and-race-team-10 | 2 (CODEFORCES/legacy-code) | — | 2 (MEDIUM) | data structures, dfs and similar, graphs, greedy | 2 | 0 | 100 | 102 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | discover-the-monk | 2 (CODEFORCES/legacy-code) | 2500 | 0 (UNKNOWN) | data structures, graphs | 1 | 9 | 54 | 64 | unknown | 1,073,741,824 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | gcd2 | 6 (AIZU/legacy-code) | 2600 | 0 (UNKNOWN) | implementation, math | 3 | 0 | 100 | 103 | 2000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | ig01 | 1 (CODECHEF) | — | 7 (A) | games, graphs | 1 | 12 | 100 | 113 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | lexicographically-preceding-permutation | 3 (HACKEREARTH/legacy-code) | 1700 | 11 (E) | — | 2 | 40 | 100 | 142 | 1000 ms | 512,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | lucky5 | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | constructive algorithms, math, sortings | 4 | 0 | 100 | 104 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | once-upon-a-time-in-time-land | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | — | 2 | 0 | 100 | 102 | 3000 ms | unknown | yes | yes | yes (heuristic) |
| Graphs & Trees | p00074 Videotape | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | combinatorics, dfs and similar, dsu, graphs | 1 | 127 | 94 | 222 | unknown | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | p00573 Commuter Pass | 2 (CODEFORCES/legacy-code) | — | 8 (B) | binary search, brute force, dp, greedy, sortings | 1 | 30 | 100 | 131 | unknown | unknown | yes | yes | yes (heuristic) |
| Graphs & Trees | p00676 KND is So Sexy | 3 (HACKEREARTH/legacy-code) | 1800 | 0 (UNKNOWN) | — | 4 | 0 | 49 | 53 | 500 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | p00914 Equal Sum Sets | 2 (CODEFORCES/legacy-code) | 2000 | 0 (UNKNOWN) | combinatorics, data structures, sortings | 1 | 0 | 100 | 101 | 1000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | p00953 Animal Companion in Maze | 2 (CODEFORCES/legacy-code) | — | 10 (D) | combinatorics, divide and conquer | 4 | 8 | 100 | 112 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | p01123 Let's Move Tiles! | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | bitmasks, brute force, fft, strings, trees | 3 | 0 | 99 | 102 | unknown | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | p01484 Icy Composer | 2 (CODEFORCES/legacy-code) | 2200 | 7 (A) | binary search, data structures, dfs and similar, dsu, shortest paths, two pointers | 3 | 47 | 100 | 150 | 1000 ms | unknown | yes | yes | yes (heuristic) |
| Graphs & Trees | p01535 Markup language has Declined | 2 (CODEFORCES/legacy-code) | 1400 | 15 (I) | — | 3 | 1 | 45 | 49 | 2000 ms | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | p01538 Kakezan | 2 (CODEFORCES/legacy-code) | — | 11 (E) | binary search, data structures, graph matchings, greedy, implementation, math, trees | 4 | 45 | 62 | 111 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | p01576 Exciting Bicycle | 2 (CODEFORCES/legacy-code) | — | 8 (B) | constructive algorithms, graphs | 1 | 21 | 54 | 76 | unknown | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | p01931 Check answers | 2 (CODEFORCES/legacy-code) | 2100 | 9 (C) | binary search, dsu, graphs, shortest paths, trees | 4 | 124 | 51 | 179 | 2000 ms | unknown | no | yes | yes (heuristic) |
| Graphs & Trees | p02069 Universal and Existential Quantifiers | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | dfs and similar, dp, dsu, ternary search, trees | 2 | 44 | 50 | 96 | 2000 ms | unknown | yes | yes | yes (heuristic) |
| Graphs & Trees | p02405 Print a Chessboard | 2 (CODEFORCES/legacy-code) | 2500 | 10 (D) | — | 1 | 11 | 100 | 112 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | p02781 AtCoder Beginner Contest 154 - Almost Everywhere Zero | 2 (CODEFORCES/legacy-code) | — | 13 (G) | brute force, greedy, math | 1 | 0 | 63 | 64 | 1000 ms | 1,073,741,824 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | p02879 AtCoder Beginner Contest 144 - 9x9 | 2 (CODEFORCES/legacy-code) | 1300 | 7 (A) | implementation, strings | 2 | 66 | 0 | 68 | 1000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | p02943 AtCoder Grand Contest 037 - Reversing and Concatenating | 2 (CODEFORCES/legacy-code) | — | 10 (D) | constructive algorithms, dfs and similar, dp | 2 | 1 | 78 | 81 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | p03010 diverta 2019 Programming Contest 2 - Diverta City | 5 (ATCODER/legacy-code) | 1800 | 12 (F) | dfs and similar | 2 | 11 | 77 | 90 | 2000 ms | 134,217,728 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | p03225 Tenka1 Programmer Contest - Equilateral | 6 (AIZU/legacy-code) | 800 | 8 (B) | brute force | 1 | 6 | 100 | 107 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | p03297 AtCoder Grand Contest 026 - rng_10s | 6 (AIZU/legacy-code) | 2000 | 7 (A) | — | 2 | 0 | 38 | 40 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | p03407 AtCoder Beginner Contest 091 - Two Coins | 5 (ATCODER/legacy-code) | — | 12 (F) | — | 2 | 30 | 55 | 87 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | p03452 AtCoder Regular Contest 090 - People on a Line | 5 (ATCODER/legacy-code) | 2500 | 7 (A) | constructive algorithms, graphs, greedy, implementation | 4 | 21 | 100 | 125 | 2000 ms | 268,435,456 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | p03503 AtCoder Beginner Contest 080 - Shopping Street | 6 (AIZU/legacy-code) | 1600 | 2 (MEDIUM) | dp, math, number theory | 2 | 0 | 52 | 54 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | p03664 AtCoder Regular Contest 078 - Mole and Abandoned Mine | 6 (AIZU/legacy-code) | — | 0 (UNKNOWN) | — | 2 | 1 | 53 | 56 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | p04048 AtCoder Grand Contest 001 - Mysterious Light | 2 (CODEFORCES/legacy-code) | — | 7 (A) | dfs and similar, graphs | 3 | 33 | 49 | 85 | 2000 ms | 64,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | palin-pairs | 2 (CODEFORCES/legacy-code) | — | 17 (K) | dfs and similar, dp | 2 | 7 | 100 | 109 | 2000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | subtraction-game-theory-1 | 3 (HACKEREARTH/legacy-code) | 2100 | 11 (E) | implementation, math | 4 | 48 | 100 | 152 | 5000 ms | 536,870,912 bytes | yes | yes | yes (heuristic) |
| Graphs & Trees | tech07 | 6 (AIZU/legacy-code) | — | 11 (E) | — | 4 | 0 | 100 | 104 | 3000 ms | unknown | no | yes | yes (heuristic) |
| Graphs & Trees | trailing-zero-problem-1 | 2 (CODEFORCES/legacy-code) | 1500 | 9 (C) | — | 1 | 37 | 100 | 138 | 2000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Graphs & Trees | walk | 3 (HACKEREARTH/legacy-code) | 1800 | 10 (D) | constructive algorithms, dfs and similar, dp, greedy, trees | 3 | 95 | 0 | 98 | unknown | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 1012_B. Chemical table | 1 (CODECHEF) | 2100 | 10 (D) | math | 2 | 0 | 100 | 102 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 1037_E. Trips | 6 (AIZU/legacy-code) | 1000 | 0 (UNKNOWN) | binary search, geometry, ternary search | 1 | 1 | 87 | 89 | unknown | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 1060_A. Phone Numbers | 2 (CODEFORCES/legacy-code) | 1800 | 10 (D) | implementation, math | 2 | 4 | 100 | 106 | 2000 ms | unknown | yes | yes | yes (heuristic) |
| Math & Number Theory | 1176_F. Destroy it! | 2 (CODEFORCES/legacy-code) | 2000 | 0 (UNKNOWN) | — | 1 | 15 | 33 | 49 | 3000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 1180_E. Serge and Dining Room | 3 (HACKEREARTH/legacy-code) | — | 10 (D) | games, geometry, math | 1 | 1 | 100 | 102 | unknown | 256,000,000 bytes | no | yes | yes (heuristic) |
| Math & Number Theory | 1253_F. Cheap Robot | 2 (CODEFORCES/legacy-code) | 2000 | 11 (E) | binary search, data structures, greedy, implementation | 1 | 0 | 100 | 101 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 1269_B. Modulo Equality | 2 (CODEFORCES/legacy-code) | — | 8 (B) | — | 1 | 21 | 36 | 58 | unknown | 256,000,000 bytes | no | yes | yes (heuristic) |
| Math & Number Theory | 1269_E. K Integers | 6 (AIZU/legacy-code) | 900 | 0 (UNKNOWN) | number theory | 3 | 50 | 100 | 153 | 3000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 1311_F. Moving Points | 2 (CODEFORCES/legacy-code) | 1100 | 9 (C) | — | 2 | 80 | 100 | 182 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 1344_A. Hilbert's Hotel | 2 (CODEFORCES/legacy-code) | 2300 | 0 (UNKNOWN) | combinatorics, math, number theory | 1 | 1 | 98 | 100 | unknown | 134,217,728 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 1446_D2. Frequency Problem (Hard Version) | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | — | 1 | 3 | 100 | 104 | unknown | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 1490_G. Old Floppy Drive | 2 (CODEFORCES/legacy-code) | 800 | 11 (E) | greedy | 1 | 0 | 51 | 52 | 1000 ms | 134,217,728 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 228_D. Zigzag | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | games, math, number theory | 1 | 1 | 97 | 99 | 3000 ms | 512,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 242_C. King's Path | 2 (CODEFORCES/legacy-code) | 2200 | 7 (A) | geometry, math | 2 | 18 | 56 | 76 | 8000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 260_B. Ancient Prophesy | 1 (CODECHEF) | 2100 | 2 (MEDIUM) | — | 3 | 0 | 100 | 103 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 348_A. Mafia | 2 (CODEFORCES/legacy-code) | — | 10 (D) | math | 3 | 0 | 200 | 203 | 1000 ms | 512,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 392_D. Three Arrays | 2 (CODEFORCES/legacy-code) | 1800 | 7 (A) | — | 3 | 25 | 100 | 128 | unknown | 256,000,000 bytes | no | yes | yes (heuristic) |
| Math & Number Theory | 39_E. What Has Dirichlet Got to Do with That? | 2 (CODEFORCES/legacy-code) | 1900 | 10 (D) | — | 3 | 37 | 100 | 140 | unknown | unknown | yes | yes | yes (heuristic) |
| Math & Number Theory | 39_H. Multiplication Table | 2 (CODEFORCES/legacy-code) | 2100 | 7 (A) | — | 1 | 16 | 100 | 117 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 464_D. World of Darkraft - 2 | 6 (AIZU/legacy-code) | 900 | 8 (B) | constructive algorithms, dsu, math | 2 | 4 | 100 | 106 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 488_C. Fight the Monster | 6 (AIZU/legacy-code) | 1600 | 0 (UNKNOWN) | — | 1 | 13 | 30 | 44 | 2000 ms | 1,073,741,824 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 512_B. Fox And Jumping | 2 (CODEFORCES/legacy-code) | 2700 | 11 (E) | games, math | 1 | 0 | 100 | 101 | unknown | unknown | yes | yes | yes (heuristic) |
| Math & Number Theory | 582_A. GCD Table | 2 (CODEFORCES/legacy-code) | 2200 | 12 (F) | — | 1 | 0 | 100 | 101 | 1000 ms | unknown | yes | yes | yes (heuristic) |
| Math & Number Theory | 614_C. Peter and Snow Blower | 1 (CODECHEF) | 2600 | 8 (B) | implementation | 1 | 0 | 100 | 101 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 626_D. Jerry's Protest | 2 (CODEFORCES/legacy-code) | 1100 | 8 (B) | greedy, math | 3 | 51 | 100 | 154 | 8000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 643_B. Bear and Two Paths | 2 (CODEFORCES/legacy-code) | 900 | 6 (EXTERNAL) | implementation | 2 | 0 | 58 | 60 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 663_A. Rebus | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | — | 3 | 0 | 100 | 103 | 2000 ms | 134,217,728 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 691_D. Swaps in Permutation | 3 (HACKEREARTH/legacy-code) | — | 9 (C) | combinatorics, math, number theory | 2 | 0 | 78 | 80 | unknown | 1,073,741,824 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 70_C. Lucky Tickets | 2 (CODEFORCES/legacy-code) | — | 10 (D) | math | 1 | 63 | 100 | 164 | 5000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 730_G. Car Repair Shop | 5 (ATCODER/legacy-code) | 1500 | 10 (D) | — | 1 | 0 | 100 | 101 | unknown | unknown | no | yes | yes (heuristic) |
| Math & Number Theory | 754_B. Ilya and tic-tac-toe game | 2 (CODEFORCES/legacy-code) | — | 7 (A) | constructive algorithms, greedy, sortings | 3 | 0 | 62 | 65 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 760_F. Bacterial Melee | 6 (AIZU/legacy-code) | — | 0 (UNKNOWN) | brute force, constructive algorithms, greedy, math | 1 | 0 | 53 | 54 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 765_D. Artsem and Saunders | 2 (CODEFORCES/legacy-code) | — | 8 (B) | math, number theory | 4 | 0 | 32 | 36 | 4000 ms | 134,217,728 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 835_A. Key races | 2 (CODEFORCES/legacy-code) | — | 10 (D) | binary search, brute force, chinese remainder theorem, math, number theory | 2 | 0 | 79 | 81 | 2000 ms | 134,217,728 bytes | no | yes | yes (heuristic) |
| Math & Number Theory | 954_F. Runner's Problem | 2 (CODEFORCES/legacy-code) | — | 8 (B) | brute force, math | 2 | 0 | 49 | 51 | 3000 ms | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | 980_E. The Number Games | 5 (ATCODER/legacy-code) | 800 | 8 (B) | — | 5 | 0 | 8 | 13 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | chefrp | 2 (CODEFORCES/legacy-code) | — | 9 (C) | — | 0 | 10 | 100 | 110 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | cost-of-data-11 | 2 (CODEFORCES/legacy-code) | 3000 | 0 (UNKNOWN) | — | 1 | 0 | 100 | 101 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | hermione-vs-draco | 5 (ATCODER/legacy-code) | 2300 | 0 (UNKNOWN) | constructive algorithms, math | 1 | 4 | 62 | 67 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | magic-gcd | 1 (CODECHEF) | 1100 | 9 (C) | — | 1 | 18 | 58 | 77 | 8000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | monks-birthday-party | 2 (CODEFORCES/legacy-code) | 1600 | 10 (D) | binary search, math | 3 | 2 | 100 | 105 | 1000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Math & Number Theory | p00163 Highway Toll | 2 (CODEFORCES/legacy-code) | 1300 | 13 (G) | math | 1 | 9 | 66 | 76 | unknown | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | p00447 Searching Constellation | 3 (HACKEREARTH/legacy-code) | 2600 | 13 (G) | brute force, math, number theory | 2 | 0 | 100 | 102 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | p00490 Best Pizza | 2 (CODEFORCES/legacy-code) | — | 9 (C) | data structures, math | 4 | 1 | 49 | 54 | 1000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Math & Number Theory | p00819 Unreliable Message | 2 (CODEFORCES/legacy-code) | — | 7 (A) | constructive algorithms, greedy, number theory | 3 | 0 | 100 | 103 | 2000 ms | unknown | yes | yes | yes (heuristic) |
| Math & Number Theory | p01086 Short Phrase | 3 (HACKEREARTH/legacy-code) | 2400 | 14 (H) | math | 1 | 10 | 56 | 67 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | p01353 Rabbit Plays Games! | 2 (CODEFORCES/legacy-code) | 1900 | 10 (D) | binary search, geometry, two pointers | 3 | 0 | 80 | 83 | 6000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Math & Number Theory | p01356 Nearest Station | 1 (CODECHEF) | — | 8 (B) | math | 2 | 7 | 46 | 55 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | p01691 Disappear Drive | 2 (CODEFORCES/legacy-code) | 1200 | 8 (B) | greedy, two pointers | 4 | 0 | 100 | 104 | 2000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Math & Number Theory | p01835 Donut Decoration | 6 (AIZU/legacy-code) | 2700 | 0 (UNKNOWN) | geometry, math | 3 | 0 | 39 | 42 | 3000 ms | 512,000,000 bytes | no | yes | yes (heuristic) |
| Math & Number Theory | p01878 Destiny Draw | 2 (CODEFORCES/legacy-code) | — | 10 (D) | — | 1 | 17 | 100 | 118 | 2000 ms | unknown | no | yes | yes (heuristic) |
| Math & Number Theory | p01970 The Diversity of Prime Factorization | 2 (CODEFORCES/legacy-code) | — | 8 (B) | — | 1 | 14 | 100 | 115 | 2000 ms | 1,073,741,824 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | p02574 AtCoder Beginner Contest 177 - Coprime | 5 (ATCODER/legacy-code) | — | 7 (A) | data structures, divide and conquer, dp | 2 | 0 | 58 | 60 | 3000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Math & Number Theory | p02679 AtCoder Beginner Contest 168 - ∙ (Bullet) | 6 (AIZU/legacy-code) | — | 0 (UNKNOWN) | greedy, two pointers | 2 | 0 | 58 | 60 | 2000 ms | 512,000,000 bytes | no | yes | yes (heuristic) |
| Math & Number Theory | p02971 AtCoder Beginner Contest 134 - Exception Handling | 2 (CODEFORCES/legacy-code) | 1900 | 0 (UNKNOWN) | binary search, data structures, sortings, two pointers | 2 | 0 | 100 | 102 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | p03294 AtCoder Beginner Contest 103 - Modulo Summation | 2 (CODEFORCES/legacy-code) | 900 | 7 (A) | — | 3 | 0 | 100 | 103 | 2500 ms | 536,870,912 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | p03612 AtCoder Beginner Contest 072 - Derangement | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | number theory | 3 | 49 | 0 | 52 | 2000 ms | 512,000,000 bytes | no | yes | yes (heuristic) |
| Math & Number Theory | p03774 AtCoder Beginner Contest 057 - Checkpoints | 2 (CODEFORCES/legacy-code) | 1100 | 0 (UNKNOWN) | binary search, data structures, math | 2 | 0 | 41 | 43 | 3000 ms | unknown | yes | yes | yes (heuristic) |
| Math & Number Theory | proposal | 2 (CODEFORCES/legacy-code) | — | 8 (B) | — | 3 | 11 | 100 | 114 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | special-matrix-1 | 6 (AIZU/legacy-code) | 2400 | 0 (UNKNOWN) | — | 4 | 25 | 47 | 76 | 2000 ms | 1,073,741,824 bytes | yes | yes | yes (heuristic) |
| Math & Number Theory | vibhu-and-his-mathematics | 3 (HACKEREARTH/legacy-code) | — | 0 (UNKNOWN) | — | 4 | 0 | 46 | 50 | 2000 ms | unknown | yes | yes | yes (heuristic) |
| Strings | 1037_B. Reach Median | 2 (CODEFORCES/legacy-code) | 1900 | 0 (UNKNOWN) | math | 2 | 1 | 43 | 46 | unknown | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | 1088_D. Ehab and another another xor problem | 2 (CODEFORCES/legacy-code) | 3200 | 11 (E) | greedy | 3 | 2 | 44 | 49 | 4000 ms | 134,217,728 bytes | yes | yes | yes (heuristic) |
| Strings | 1117_F. Crisp String | 6 (AIZU/legacy-code) | 2000 | 12 (F) | dp | 4 | 145 | 100 | 249 | 1000 ms | 64,000,000 bytes | no | yes | yes (heuristic) |
| Strings | 1140_B. Good String | 2 (CODEFORCES/legacy-code) | — | 8 (B) | implementation, math | 3 | 0 | 37 | 40 | 1000 ms | 512,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | 1158_F. Density of subarrays | 3 (HACKEREARTH/legacy-code) | 3000 | 7 (A) | — | 3 | 9 | 90 | 102 | 8000 ms | 1,073,741,824 bytes | yes | yes | yes (heuristic) |
| Strings | 1195_D2. Submarine in the Rybinsk Sea (hard edition) | 2 (CODEFORCES/legacy-code) | 2400 | 12 (F) | brute force, data structures, implementation | 1 | 10 | 42 | 53 | 2000 ms | 134,217,728 bytes | no | yes | yes (heuristic) |
| Strings | 1257_G. Divisor Set | 1 (CODECHEF) | 2200 | 7 (A) | — | 2 | 6 | 96 | 104 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | 1328_F. Make k Equal | 6 (AIZU/legacy-code) | 2300 | 12 (F) | math | 3 | 0 | 100 | 103 | 4000 ms | 268,435,456 bytes | no | yes | yes (heuristic) |
| Strings | 1354_C2. Not So Simple Polygon Embedding | 3 (HACKEREARTH/legacy-code) | — | 2 (MEDIUM) | binary search, dp | 2 | 0 | 54 | 56 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | 1361_E. James and the Chase | 5 (ATCODER/legacy-code) | — | 9 (C) | constructive algorithms, implementation | 0 | 31 | 100 | 131 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | 1366_A. Shovels and Swords | 2 (CODEFORCES/legacy-code) | 1900 | 10 (D) | divide and conquer, hashing, sortings, strings | 1 | 2 | 90 | 93 | 5000 ms | 1,073,741,824 bytes | yes | yes | yes (heuristic) |
| Strings | 1408_A. Circle Coloring | 3 (HACKEREARTH/legacy-code) | 2700 | 7 (A) | bitmasks, combinatorics, dp | 1 | 61 | 100 | 162 | 8000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | 1466_F. Euclid's nightmare | 6 (AIZU/legacy-code) | — | 9 (C) | greedy | 1 | 23 | 41 | 65 | unknown | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | 1490_D. Permutation Transformation | 2 (CODEFORCES/legacy-code) | 2000 | 10 (D) | — | 2 | 0 | 100 | 102 | unknown | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | 1525_D. Armchairs | 3 (HACKEREARTH/legacy-code) | 2500 | 10 (D) | brute force, implementation | 1 | 30 | 100 | 131 | 2000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Strings | 1547_C. Pair Programming | 2 (CODEFORCES/legacy-code) | 1800 | 6 (EXTERNAL) | games, implementation | 1 | 163 | 100 | 264 | 2000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Strings | 438_A. The Child and Toy | 1 (CODECHEF) | — | 8 (B) | data structures | 2 | 14 | 0 | 16 | 2000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Strings | 494_A. Treasure | 2 (CODEFORCES/legacy-code) | — | 8 (B) | — | 3 | 61 | 100 | 164 | 2000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Strings | 544_E. Remembering Strings | 2 (CODEFORCES/legacy-code) | 3100 | 0 (UNKNOWN) | — | 1 | 1 | 200 | 202 | 1500 ms | 1,073,741,824 bytes | no | yes | yes (heuristic) |
| Strings | 551_B. ZgukistringZ | 2 (CODEFORCES/legacy-code) | — | 12 (F) | constructive algorithms | 1 | 67 | 100 | 168 | unknown | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | 571_B. Minimization | 2 (CODEFORCES/legacy-code) | 1900 | 0 (UNKNOWN) | brute force, greedy, implementation | 4 | 9 | 91 | 104 | 3000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | 571_E. Geometric Progressions | 2 (CODEFORCES/legacy-code) | 1700 | 0 (UNKNOWN) | — | 1 | 16 | 32 | 49 | 1000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Strings | 621_D. Rat Kwesh and Cheese | 2 (CODEFORCES/legacy-code) | — | 8 (B) | combinatorics, number theory | 1 | 0 | 99 | 100 | 3000 ms | unknown | yes | yes | yes (heuristic) |
| Strings | 709_E. Centroids | 6 (AIZU/legacy-code) | 2200 | 0 (UNKNOWN) | — | 3 | 29 | 71 | 103 | 2000 ms | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Strings | 80_C. Heroes | 6 (AIZU/legacy-code) | 900 | 8 (B) | dsu, math | 3 | 17 | 92 | 112 | 1000 ms | unknown | no | yes | yes (heuristic) |
| Strings | 83_C. Track | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | implementation | 2 | 0 | 73 | 75 | unknown | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | 875_D. High Cry | 6 (AIZU/legacy-code) | 2200 | 9 (C) | constructive algorithms, math | 4 | 0 | 42 | 46 | 1000 ms | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Strings | 914_F. Substrings in a String | 2 (CODEFORCES/legacy-code) | 1500 | 11 (E) | — | 1 | 0 | 100 | 101 | 3000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | 977_B. Two-gram | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | — | 1 | 30 | 99 | 130 | 3000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | 990_B. Micro-World | 2 (CODEFORCES/legacy-code) | 800 | 0 (UNKNOWN) | — | 3 | 3 | 33 | 39 | 2000 ms | unknown | yes | yes | yes (heuristic) |
| Strings | colarr | 2 (CODEFORCES/legacy-code) | 2100 | 12 (F) | brute force | 2 | 11 | 49 | 62 | unknown | 134,217,728 bytes | yes | yes | yes (heuristic) |
| Strings | find-the-nth-prime | 2 (CODEFORCES/legacy-code) | — | 7 (A) | binary search, bitmasks, combinatorics, data structures, divide and conquer | 3 | 39 | 84 | 126 | unknown | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | jumping-frog | 5 (ATCODER/legacy-code) | — | 9 (C) | implementation | 1 | 0 | 46 | 47 | 1000 ms | unknown | yes | yes | yes (heuristic) |
| Strings | luckybal | 1 (CODECHEF) | 1600 | 7 (A) | brute force, greedy | 3 | 0 | 100 | 103 | 1000 ms | 512,000,000 bytes | no | yes | yes (heuristic) |
| Strings | monks-choice-of-numbers-1 | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | binary search, data structures, hashing | 1 | 3 | 52 | 56 | 1000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Strings | new-world-11 | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | implementation, strings | 2 | 75 | 76 | 153 | unknown | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | nopc10 | 2 (CODEFORCES/legacy-code) | 1600 | 12 (F) | bitmasks, brute force, data structures, string suffix structures, strings | 3 | 0 | 100 | 103 | unknown | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Strings | p00032 Plastic Board | 5 (ATCODER/legacy-code) | 2200 | 0 (UNKNOWN) | — | 1 | 7 | 66 | 74 | 2000 ms | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Strings | p00206 Next Trip | 5 (ATCODER/legacy-code) | — | 8 (B) | implementation, sortings, strings | 3 | 2 | 100 | 105 | 3000 ms | unknown | yes | yes | yes (heuristic) |
| Strings | p00991 Grid | 3 (HACKEREARTH/legacy-code) | 2700 | 10 (D) | data structures, dp | 2 | 0 | 42 | 44 | 6000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Strings | p01083 RedBlue | 5 (ATCODER/legacy-code) | 1200 | 9 (C) | — | 2 | 0 | 100 | 102 | 1000 ms | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Strings | p01262 Adaptive Time Slicing Quantization | 2 (CODEFORCES/legacy-code) | 1600 | 8 (B) | brute force, implementation, strings | 3 | 35 | 100 | 138 | unknown | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | p02211 Apple Adventure | 2 (CODEFORCES/legacy-code) | 1900 | 8 (B) | — | 1 | 9 | 100 | 110 | 2000 ms | 134,217,728 bytes | yes | yes | yes (heuristic) |
| Strings | p02257 Prime Numbers | 5 (ATCODER/legacy-code) | 800 | 9 (C) | greedy, implementation, sortings, strings | 3 | 20 | 88 | 111 | 4000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Strings | p02744 Panasonic Programming Contest 2020 - String Equivalence | 2 (CODEFORCES/legacy-code) | 1400 | 8 (B) | geometry, math | 1 | 1 | 100 | 102 | unknown | 256,000,000 bytes | no | yes | yes (heuristic) |
| Strings | p02916 AtCoder Beginner Contest 140 - Buffet | 3 (HACKEREARTH/legacy-code) | — | 0 (UNKNOWN) | — | 1 | 97 | 100 | 198 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | p03013 AtCoder Beginner Contest 129 - Typical Stairs | 2 (CODEFORCES/legacy-code) | — | 0 (UNKNOWN) | brute force, implementation | 2 | 0 | 100 | 102 | 2000 ms | unknown | no | yes | yes (heuristic) |
| Strings | p03371 AtCoder Beginner Contest 095 - Half and Half | 5 (ATCODER/legacy-code) | 1100 | 7 (A) | brute force, implementation, strings | 1 | 0 | 100 | 101 | 2000 ms | 134,217,728 bytes | yes | yes | yes (heuristic) |
| Strings | p03570 CODE FESTIVAL 2017 qual C - Yet Another Palindrome Partitioning | 2 (CODEFORCES/legacy-code) | 2700 | 0 (UNKNOWN) | brute force | 2 | 2 | 49 | 53 | 2000 ms | 268,435,456 bytes | yes | yes | yes (heuristic) |
| Strings | p03986 AtCoder Grand Contest 005 - STring | 5 (ATCODER/legacy-code) | — | 7 (A) | data structures, greedy | 1 | 0 | 66 | 67 | 2000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | play-with-string | 2 (CODEFORCES/legacy-code) | 3200 | 0 (UNKNOWN) | — | 2 | 14 | 100 | 116 | 5000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Strings | playing-with-substrings | 3 (HACKEREARTH/legacy-code) | 800 | 8 (B) | — | 1 | 1 | 100 | 102 | 2000 ms | 134,217,728 bytes | yes | yes | yes (heuristic) |
| Strings | reversemerge-shuffle-reverse | 2 (CODEFORCES/legacy-code) | — | 7 (A) | — | 2 | 0 | 100 | 102 | 1000 ms | 256,000,000 bytes | no | yes | yes (heuristic) |
| Strings | roy-and-wobbly-numbers | 2 (CODEFORCES/legacy-code) | 2300 | 0 (UNKNOWN) | combinatorics, dp | 2 | 0 | 66 | 68 | 1000 ms | 256,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | tf01 | 2 (CODEFORCES/legacy-code) | 1500 | 0 (UNKNOWN) | brute force, implementation | 3 | 0 | 80 | 83 | unknown | 134,217,728 bytes | yes | yes | yes (heuristic) |
| Strings | the-competitive-class-3 | 6 (AIZU/legacy-code) | 1900 | 7 (A) | — | 1 | 18 | 100 | 119 | unknown | 512,000,000 bytes | yes | yes | yes (heuristic) |
| Strings | xenny-and-range-sums | 2 (CODEFORCES/legacy-code) | 2300 | 0 (UNKNOWN) | math, number theory, sortings | 1 | 29 | 91 | 121 | 500 ms | 1,073,741,824 bytes | yes | yes | yes (heuristic) |

## Implementation recommendation

Do not copy these records directly into the canonical seed. First manually verify each selected problem’s statement, I/O contract, reference compilation under Python 3.12 and C++17, time/memory normalization, public-example quality, and whether eight hidden tests can be curated without leaking private data. Then author the final five-topic, five-problem-per-topic curriculum and exactly ten test cases per problem.

## Sources

- [DeepMind CodeContests dataset card](https://huggingface.co/datasets/deepmind/code_contests)
- [CodeContests GitHub repository and README](https://github.com/google-deepmind/code_contests)
- [Canonical ContestProblem schema](https://github.com/google-deepmind/code_contests/blob/main/contest_problem.proto)
- [Analyzed 500-row Hugging Face representation](https://huggingface.co/datasets/TheFactoryX/edition_2104_deepmind-code_contests-readymade)
