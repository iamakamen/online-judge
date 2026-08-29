# Module 8: Arrays Canonical Curriculum

This document defines the canonical V1 Arrays curriculum. Each starter is a
complete stdin/stdout program for the V1 Run Engine. No function-call harness
is assumed.

## A1. Two Sum

- Topic: Arrays
- Title: Two Sum
- Slug: `two-sum`
- Difficulty: Easy
- Tags: Hash Map; Complement Lookup; Linear-Time Search
- Time limit: 1000 ms
- Memory limit: 128 MB

### Statement

Given an array of integers and a target value, find the unique pair of
distinct indices whose values add up to the target. Return the two indices in
ascending order. The input guarantees that exactly one valid pair exists.

### Input format

The first line contains `n` and `target`. The second line contains `n`
integers `a1 a2 ... an`.

### Output format

Print two zero-based indices `i j` in ascending order such that
`a[i] + a[j] == target`.

### Constraints

- `2 <= n <= 100000`
- `-10^9 <= ai <= 10^9`
- `-10^9 <= target <= 10^9`
- Exactly one valid pair exists.

### Example 1

Input:

```text
4 9
2 7 11 15
```

Output:

```text
0 1
```

### Example 2

Input:

```text
5 6
3 2 4 7 1
```

Output:

```text
1 2
```

### Intended solution

Scan from left to right while storing each previously seen value and its
index in a hash map. For the current value `x`, look up `target - x` before
storing `x`.

- Intended time complexity: `O(n)` average time
- Intended auxiliary-space complexity: `O(n)`

### Python 3.12 stdin/stdout starter

```python
import sys


def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n, target = data[0], data[1]
    values = data[2:2 + n]

    seen = {}
    for index, value in enumerate(values):
        complement = target - value
        if complement in seen:
            left, right = seen[complement], index
            print(left, right)
            return
        seen[value] = index


if __name__ == "__main__":
    main()
```

### C++17 stdin/stdout starter

```cpp
#include <iostream>
#include <unordered_map>
#include <vector>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int n;
    long long target;
    std::cin >> n >> target;

    std::unordered_map<long long, int> seen;
    for (int index = 0; index < n; ++index) {
        long long value;
        std::cin >> value;
        long long complement = target - value;
        auto it = seen.find(complement);
        if (it != seen.end()) {
            std::cout << it->second << ' ' << index << '\n';
            return 0;
        }
        seen[value] = index;
    }
}
```

## A2. Best Time to Buy and Sell Stock

- Topic: Arrays
- Title: Best Time to Buy and Sell Stock
- Slug: `best-time-to-buy-and-sell-stock`
- Difficulty: Easy
- Tags: Greedy; Minimum Tracking; One-Pass Scan
- Time limit: 1000 ms
- Memory limit: 128 MB

### Statement

Given the daily price of one stock, choose at most one day to buy and one
later day to sell. Maximize the profit `sell_price - buy_price`. If no
profitable transaction exists, return zero. Buying and selling on the same
day is not allowed, although a zero-profit result is permitted.

### Input format

The first line contains `n`. The second line contains `n` integers
`p1 p2 ... pn` in chronological order.

### Output format

Print one integer, `maximum_profit`.

### Constraints

- `1 <= n <= 100000`
- `0 <= prices[i] <= 100000`

### Example 1

Input:

```text
6
7 1 5 3 6 4
```

Output:

```text
5
```

### Example 2

Input:

```text
5
7 6 4 3 1
```

Output:

```text
0
```

### Intended solution

Track the minimum price seen so far and the best profit obtainable by selling
at each later price.

- Intended time complexity: `O(n)`
- Intended auxiliary-space complexity: `O(1)`

### Python 3.12 stdin/stdout starter

```python
import sys


def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    prices = data[1:1 + n]

    minimum = prices[0]
    best = 0
    for price in prices[1:]:
        best = max(best, price - minimum)
        minimum = min(minimum, price)
    print(best)


if __name__ == "__main__":
    main()
```

### C++17 stdin/stdout starter

```cpp
#include <algorithm>
#include <iostream>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int n;
    std::cin >> n;

    int price;
    std::cin >> price;
    int minimum = price;
    int best = 0;

    for (int i = 1; i < n; ++i) {
        std::cin >> price;
        best = std::max(best, price - minimum);
        minimum = std::min(minimum, price);
    }

    std::cout << best << '\n';
}
```

## A3. Contains Duplicate

- Topic: Arrays
- Title: Contains Duplicate
- Slug: `contains-duplicate`
- Difficulty: Easy
- Tags: Hash Set; Membership Testing; Deduplication
- Time limit: 1000 ms
- Memory limit: 128 MB

### Statement

Determine whether an integer array contains at least one value that appears
more than once.

### Input format

The first line contains `n`. The second line contains `n` integers
`a1 a2 ... an`.

### Output format

Print `true` if any value occurs at least twice; otherwise print `false`.

### Constraints

- `1 <= n <= 100000`
- `-10^9 <= ai <= 10^9`

### Example 1

Input:

```text
4
1 2 3 1
```

Output:

```text
true
```

### Example 2

Input:

```text
4
1 2 3 4
```

Output:

```text
false
```

### Intended solution

Insert values into a hash set and return `true` as soon as a value is already
present.

- Intended time complexity: `O(n)` average time
- Intended auxiliary-space complexity: `O(n)`

### Python 3.12 stdin/stdout starter

```python
import sys


def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    values = data[1:1 + n]
    print("true" if len(set(values)) != n else "false")


if __name__ == "__main__":
    main()
```

### C++17 stdin/stdout starter

```cpp
#include <iostream>
#include <unordered_set>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int n;
    std::cin >> n;
    std::unordered_set<long long> seen;
    bool duplicate = false;

    for (int i = 0; i < n; ++i) {
        long long value;
        std::cin >> value;
        if (!seen.insert(value).second) {
            duplicate = true;
        }
    }

    std::cout << (duplicate ? "true" : "false") << '\n';
}
```

## A4. Product of Array Except Self

- Topic: Arrays
- Title: Product of Array Except Self
- Slug: `product-of-array-except-self`
- Difficulty: Medium
- Tags: Prefix/Suffix; Array Traversal; Space Optimization
- Time limit: 1000 ms
- Memory limit: 128 MB

### Statement

For each position in an integer array, compute the product of every input
element except the element at that position. Division is prohibited. The
result at position `i` is called `bi`.

### Input format

The first line contains `n`. The second line contains `n` integers
`a1 a2 ... an`.

### Output format

Print `n` integers `b1 b2 ... bn`, separated by single spaces, where each
`bi` is the product of all input elements except `ai`.

### Constraints

- `2 <= n <= 18`
- `-10 <= ai <= 10`

These exact limits guarantee that the maximum absolute product excluding one
element is at most `10^17`, which fits in signed 64-bit arithmetic.

Division is prohibited.

### Example 1

Input:

```text
4
1 2 3 4
```

Output:

```text
24 12 8 6
```

### Example 2

Input:

```text
5
-1 1 0 -3 3
```

Output:

```text
0 0 9 0 0
```

### Intended solution

Store the product of all values to the left of each index, then multiply by
the product of all values to the right in a reverse traversal. Do not use
division.

- Intended time complexity: `O(n)`
- Intended auxiliary-space complexity: `O(1)` excluding the output array

### Python 3.12 stdin/stdout starter

```python
import sys


def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    values = data[1:1 + n]

    result = [1] * n
    prefix = 1
    for i, value in enumerate(values):
        result[i] = prefix
        prefix *= value

    suffix = 1
    for i in range(n - 1, -1, -1):
        result[i] *= suffix
        suffix *= values[i]

    print(*result)


if __name__ == "__main__":
    main()
```

### C++17 stdin/stdout starter

```cpp
#include <iostream>
#include <vector>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int n;
    std::cin >> n;
    std::vector<long long> values(n), result(n, 1);
    for (long long& value : values) {
        std::cin >> value;
    }

    long long prefix = 1;
    for (int i = 0; i < n; ++i) {
        result[i] = prefix;
        prefix *= values[i];
    }

    long long suffix = 1;
    for (int i = n - 1; i >= 0; --i) {
        result[i] *= suffix;
        suffix *= values[i];
    }

    for (int i = 0; i < n; ++i) {
        if (i > 0) std::cout << ' ';
        std::cout << result[i];
    }
    std::cout << '\n';
}
```

## A5. Maximum Subarray

- Topic: Arrays
- Title: Maximum Subarray
- Slug: `maximum-subarray`
- Difficulty: Medium
- Tags: Kadane's Algorithm; Running Sum; Greedy
- Time limit: 1000 ms
- Memory limit: 128 MB

### Statement

Given an integer array, find the largest possible sum of a non-empty
contiguous subarray. The selected subarray must contain at least one element.

### Input format

The first line contains `n`. The second line contains `n` integers
`a1 a2 ... an`.

### Output format

Print one integer: the maximum sum of any non-empty contiguous subarray.

### Constraints

- `1 <= n <= 100000`
- `-10^4 <= ai <= 10^4`

### Example 1

Input:

```text
9
-2 1 -3 4 -1 2 1 -5 4
```

Output:

```text
6
```

### Example 2

Input:

```text
5
-8 -3 -6 -2 -5
```

Output:

```text
-2
```

### Intended solution

Use Kadane's algorithm. At each position, choose whether to extend the
previous subarray or start a new subarray at the current value. Track the
best non-empty sum seen so far.

- Intended time complexity: `O(n)`
- Intended auxiliary-space complexity: `O(1)`

### Python 3.12 stdin/stdout starter

```python
import sys


def main() -> None:
    data = list(map(int, sys.stdin.buffer.read().split()))
    n = data[0]
    values = data[1:1 + n]

    current = best = values[0]
    for value in values[1:]:
        current = max(value, current + value)
        best = max(best, current)
    print(best)


if __name__ == "__main__":
    main()
```

### C++17 stdin/stdout starter

```cpp
#include <algorithm>
#include <iostream>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int n;
    std::cin >> n;

    long long value;
    std::cin >> value;
    long long current = value;
    long long best = value;

    for (int i = 1; i < n; ++i) {
        std::cin >> value;
        current = std::max(value, current + value);
        best = std::max(best, current);
    }

    std::cout << best << '\n';
}
```
