import test from 'node:test'
import assert from 'node:assert/strict'

import { formatConstraints, normalizeConstraints } from './constraintFormatting.js'

test('formats a simple mathematical constraint without changing its meaning', () => {
  assert.deepEqual(normalizeConstraints('1 ≤ n ≤ 1000'), ['1 ≤ n ≤ 1000'])
})

test('separates independent semicolon-delimited constraints', () => {
  assert.deepEqual(
    normalizeConstraints('1≤n≤1000; every value is an integer; results fit signed 64-bit.'),
    ['1 ≤ n ≤ 1000', 'every value is an integer', 'results fit signed 64-bit'],
  )
})

test('removes ordinary terminal sentence periods', () => {
  assert.deepEqual(
    normalizeConstraints('`1≤|s|≤100000`; `s` contains only lowercase English letters.'),
    ['1 ≤ |s| ≤ 100000', 's contains only lowercase English letters'],
  )
  assert.deepEqual(
    normalizeConstraints('The expression is valid.'),
    ['The expression is valid'],
  )
  assert.deepEqual(
    normalizeConstraints('nums.length must be valid.'),
    ['nums.length must be valid'],
  )
  assert.deepEqual(
    normalizeConstraints('O(n).'),
    ['O(n)'],
  )
})

test('preserves meaningful periods inside technical content', () => {
  assert.deepEqual(normalizeConstraints('nums.length'), ['nums.length'])
  assert.deepEqual(normalizeConstraints('a.b'), ['a.b'])
  assert.deepEqual(normalizeConstraints('1.2'), ['1.2'])
  assert.deepEqual(
    normalizeConstraints('version 1.2 is supported.'),
    ['version 1.2 is supported'],
  )
})

test('keeps multiline logical clauses together when the next line continues the sentence', () => {
  assert.deepEqual(
    normalizeConstraints('tokens are integers or\n+ - * /; the expression is valid,\nleaves one result.'),
    ['tokens are integers or + - * /', 'the expression is valid, leaves one result'],
  )
})

test('does not split mathematical punctuation or comma-separated variables', () => {
  assert.deepEqual(
    normalizeConstraints('`-10^9≤ai,target≤10^9`; values may be `+ - * /`.'),
    ['-10⁹ ≤ ai,target ≤ 10⁹', 'values may be + - * /'],
  )
})

test('does not rewrite variable names or array indices', () => {
  assert.deepEqual(
    normalizeConstraints('0<=pi<=100000; -10^9<=nums[i], target<=10^9'),
    ['0 ≤ pi ≤ 100000', '-10⁹ ≤ nums[i], target ≤ 10⁹'],
  )
})

test('formats a representative canonical problem record', () => {
  assert.deepEqual(
    normalizeConstraints('`1≤n≤1000`; tokens are integers or `+ - * /`; the expression is valid; leaves one result; and never divides by zero; intermediate results fit signed 64-bit.'),
    [
      '1 ≤ n ≤ 1000',
      'tokens are integers or + - * /',
      'the expression is valid',
      'leaves one result',
      'and never divides by zero',
      'intermediate results fit signed 64-bit',
    ],
  )
})

test('formats the exact representative records from the problem catalog', () => {
  assert.deepEqual(
    normalizeConstraints('`1≤|s|≤100000`; `s` contains only lowercase English letters.'),
    ['1 ≤ |s| ≤ 100000', 's contains only lowercase English letters'],
  )
  assert.deepEqual(
    normalizeConstraints('`1≤|s|≤2000`; `s` contains only lowercase English letters.'),
    ['1 ≤ |s| ≤ 2000', 's contains only lowercase English letters'],
  )
  assert.deepEqual(
    normalizeConstraints('`1≤n≤1000`; tokens are integers or `+ - * /`; the expression is valid; leaves one result; and never divides by zero; intermediate results fit signed 64-bit.'),
    [
      '1 ≤ n ≤ 1000',
      'tokens are integers or + - * /',
      'the expression is valid',
      'leaves one result',
      'and never divides by zero',
      'intermediate results fit signed 64-bit',
    ],
  )
})

test('supports empty, null, and optional constraint content', () => {
  assert.deepEqual(normalizeConstraints(null), [])
  assert.deepEqual(normalizeConstraints(''), [])
  assert.deepEqual(normalizeConstraints('..'), [])
  assert.deepEqual(normalizeConstraints([]), [])
})

test('preserves long text as one item and leaves visual wrapping to CSS', () => {
  const longConstraint = 'every serialized input value must remain within the declared signed 64-bit range without being split because the browser wraps this sentence across several visual lines'
  assert.deepEqual(normalizeConstraints(longConstraint), [longConstraint])
})

test('does not split ordinary punctuation', () => {
  const constraint = 'Each test case contains one valid expression, including commas, periods, and parentheses.'
  assert.deepEqual(normalizeConstraints(constraint), [constraint.slice(0, -1)])
})

test('keeps the legacy newline-delimited data as independent items', () => {
  assert.deepEqual(
    normalizeConstraints('1 <= nums.length <= 100000\n-10^9 <= nums[i], target <= 10^9\nnums contains integers'),
    ['1 ≤ nums.length ≤ 100000', '-10⁹ ≤ nums[i], target ≤ 10⁹', 'nums contains integers'],
  )
})

test('retains the string formatter compatibility wrapper', () => {
  assert.equal(formatConstraints('1 <= n <= 10; values are integers.'), '1 ≤ n ≤ 10\nvalues are integers')
})
