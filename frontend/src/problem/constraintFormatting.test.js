import test from 'node:test'
import assert from 'node:assert/strict'

import { formatConstraints } from './constraintFormatting.js'

test('formats mathematical constraints as separate readable lines', () => {
  assert.equal(
    formatConstraints('`2≤n≤100000`, `-10^9≤ai,target≤10^9`; exactly one pair.'),
    '2 ≤ n ≤ 100000\n-10⁹ ≤ aᵢ ≤ 10⁹\n-10⁹ ≤ target ≤ 10⁹\nExactly one pair.',
  )
})

test('preserves natural-language constraints and removes formatting artifacts', () => {
  assert.equal(
    formatConstraints('`1≤|s|,|t|≤100000`; both inputs contain only lowercase English letters.'),
    '1 ≤ |s| ≤ 100000\n1 ≤ |t| ≤ 100000\nBoth inputs contain only lowercase English letters.',
  )
})

test('preserves existing lines and wraps only through CSS', () => {
  assert.equal(
    formatConstraints('1 <= n <= 100000\n-10^4 <= nums[i] <= 10^4'),
    '1 ≤ n ≤ 100000\n-10⁴ ≤ numsᵢ ≤ 10⁴',
  )
})

test('normalizes natural-language punctuation and removes placeholders', () => {
  assert.equal(
    formatConstraints('1≤n≤100000; -10^4≤ai≤10^4; .; division is prohibited; results fit signed 64-bit.'),
    '1 ≤ n ≤ 100000\n-10⁴ ≤ aᵢ ≤ 10⁴\nDivision is prohibited.\nResults fit signed 64-bit.',
  )
  assert.equal(formatConstraints('..'), '')
})

test('keeps mathematical variables intact while formatting bounds', () => {
  assert.equal(
    formatConstraints('0≤pi≤100000; -10^9≤target≤10^9'),
    '0 ≤ pᵢ ≤ 100000\n-10⁹ ≤ target ≤ 10⁹',
  )
})
