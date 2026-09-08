import assert from 'node:assert/strict'
import { test } from 'node:test'
import { createSingleFlight, isTransientRefreshError } from './refreshPolicy.js'

test('single-flight shares same-tab refresh work and releases after completion', async () => {
  const runSingleFlight = createSingleFlight()
  let operationCount = 0

  const first = runSingleFlight(async () => {
    operationCount += 1
    await Promise.resolve()
    return 'refreshed'
  })
  const second = runSingleFlight(async () => {
    operationCount += 1
    return 'unexpected'
  })

  assert.strictEqual(first, second)
  assert.equal(await first, 'refreshed')
  assert.equal(operationCount, 1)

  assert.equal(await runSingleFlight(async () => 'next-refresh'), 'next-refresh')
  assert.equal(operationCount, 1)
})

test('refresh policy distinguishes transient infrastructure failures', () => {
  for (const error of [
    { code: 'NETWORK_ERROR', status: null },
    { status: 408 },
    { status: 425 },
    { status: 429 },
    { status: 500 },
    { status: 502 },
    { status: 503 },
  ]) {
    assert.equal(isTransientRefreshError(error), true)
  }

  assert.equal(isTransientRefreshError({ status: 401 }), false)
  assert.equal(isTransientRefreshError({ status: 403 }), false)
  assert.equal(isTransientRefreshError({ status: 404 }), false)
})
