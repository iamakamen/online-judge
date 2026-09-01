import assert from 'node:assert/strict'
import { test } from 'node:test'
import {
  REGISTER_DRAFT_STORAGE_KEY,
  clearRegistrationDraft,
  loadRegistrationDraft,
  normalizeRegistrationEmail,
  saveRegistrationDraft,
} from './registerStorage.js'

function createStorage() {
  const values = new Map()
  return {
    getItem: (key) => values.get(key) || null,
    setItem: (key, value) => values.set(key, value),
    removeItem: (key) => values.delete(key),
  }
}

const form = {
  firstName: 'Jane',
  lastName: 'Doe',
  email: 'jane@example.com',
  username: 'jane_doe',
  password: 'secret-password',
  confirmPassword: 'secret-password',
  otp: '123456',
}

test('registration draft restores safe form data and OTP request state', () => {
  const storage = createStorage()
  saveRegistrationDraft({
    form,
    emailStates: {
      'jane@example.com': {
        otpRequested: true,
        cooldownUntil: Date.now() + 90_000,
        remainingRequests: 3,
        emailVerified: false,
      },
    },
  }, storage)

  const restored = loadRegistrationDraft(storage)
  assert.deepEqual(restored.form, {
    firstName: 'Jane', lastName: 'Doe', email: 'jane@example.com', username: 'jane_doe',
  })
  assert.equal(restored.emailStates['jane@example.com'].otpRequested, true)
  assert.equal(restored.emailStates['jane@example.com'].emailVerified, false)
  assert.equal(restored.emailStates['jane@example.com'].remainingRequests, 3)
  assert.ok(restored.emailStates['jane@example.com'].cooldownUntil > Date.now())
  assert.doesNotMatch(storage.getItem(REGISTER_DRAFT_STORAGE_KEY), /secret-password|123456/)
})

test('session storage remains isolated between tabs', () => {
  const firstTab = createStorage()
  const secondTab = createStorage()
  saveRegistrationDraft({ form, emailStates: { 'jane@example.com': { otpRequested: true, cooldownUntil: Date.now() + 90_000, remainingRequests: 3 } } }, firstTab)

  assert.equal(loadRegistrationDraft(secondTab), null)
})

test('expired cooldowns restore without a visible active timer', () => {
  const storage = createStorage()
  saveRegistrationDraft({ form, emailStates: { 'jane@example.com': { otpRequested: true, cooldownUntil: Date.now() - 1, remainingRequests: 2 } } }, storage)

  const restored = loadRegistrationDraft(storage)
  assert.equal(restored.emailStates['jane@example.com'].cooldownUntil, 0)
  assert.equal(restored.emailStates['jane@example.com'].otpRequested, true)
})

test('verified state clears persisted request status while retaining safe form data', () => {
  const storage = createStorage()
  saveRegistrationDraft({ form, emailStates: { 'jane@example.com': { otpRequested: true, cooldownUntil: Date.now() + 90_000, remainingRequests: 1, emailVerified: true } } }, storage)

  const restored = loadRegistrationDraft(storage)
  assert.equal(restored.emailStates['jane@example.com'].otpRequested, true)
  assert.equal(restored.emailStates['jane@example.com'].cooldownUntil, 0)
  assert.equal(restored.emailStates['jane@example.com'].remainingRequests, null)
  assert.equal(restored.emailStates['jane@example.com'].emailVerified, true)
  assert.equal(restored.form.email, form.email)
})

test('completed registration can clear the UX-only draft', () => {
  const storage = createStorage()
  saveRegistrationDraft({ form, emailStates: {} }, storage)
  clearRegistrationDraft(storage)
  assert.equal(loadRegistrationDraft(storage), null)
})

test('email identities retain separate request state', () => {
  const storage = createStorage()
  saveRegistrationDraft({
    form,
    emailStates: {
      'a@example.com': { otpRequested: true, cooldownUntil: 0, remainingRequests: 4 },
      'b@example.com': { otpRequested: false, cooldownUntil: 0, remainingRequests: null },
    },
  }, storage)
  const restored = loadRegistrationDraft(storage)
  assert.equal(normalizeRegistrationEmail(' A@EXAMPLE.COM '), 'a@example.com')
  assert.equal(restored.emailStates['a@example.com'].otpRequested, true)
  assert.equal(restored.emailStates['b@example.com'].otpRequested, false)
})
