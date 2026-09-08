import assert from 'node:assert/strict'
import { test } from 'node:test'
import {
  AUTH_STATES,
  createAuthGeneration,
  initialAuthState,
  isAuthenticatedState,
} from './authLifecycle.js'

test('startup begins in restoration and only authenticated state is authenticated', () => {
  assert.equal(initialAuthState(), AUTH_STATES.RESTORING)
  assert.equal(isAuthenticatedState(AUTH_STATES.RESTORING), false)
  assert.equal(isAuthenticatedState(AUTH_STATES.TEMPORARILY_UNAVAILABLE), false)
  assert.equal(isAuthenticatedState(AUTH_STATES.UNAUTHENTICATED), false)
  assert.equal(isAuthenticatedState(AUTH_STATES.AUTHENTICATED), true)
})

test('auth generation invalidation rejects late operations', () => {
  const generation = createAuthGeneration()
  const captured = generation.current()

  assert.equal(generation.isCurrent(captured), true)
  generation.invalidate()
  assert.equal(generation.isCurrent(captured), false)
  assert.equal(generation.isCurrent(generation.current()), true)
})
