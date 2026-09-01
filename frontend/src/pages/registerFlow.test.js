import assert from 'node:assert/strict'
import { test } from 'node:test'
import {
  createRegistrationState,
  REGISTER_STEPS,
  validateCompletion,
  validateDetails,
  validateOtp,
  normalizeUsername,
  formatOtpRequestMessage,
  isUsernameValid,
  isPasswordValid,
} from './registerFlow.js'

test('registration starts on the details step with empty fields', () => {
  assert.deepEqual(createRegistrationState(), {
    step: REGISTER_STEPS.details,
    firstName: '', lastName: '', email: '', otp: '',
    username: '', password: '', confirmPassword: '',
  })
})

test('details validation requires names, email, and a valid email address', () => {
  assert.equal(validateDetails({ firstName: '', lastName: 'Doe', email: 'a@b.com' }), 'First name is required')
  assert.equal(validateDetails({ firstName: 'Jane', lastName: '', email: 'a@b.com' }), 'Last name is required')
  assert.equal(validateDetails({ firstName: 'Jane', lastName: 'Doe', email: '' }), 'Email is required')
  assert.equal(validateDetails({ firstName: 'Jane', lastName: 'Doe', email: 'not-an-email' }), 'Enter a valid email address')
})

test('OTP validation requires a code', () => {
  assert.equal(validateOtp('  '), 'Verification code is required')
  assert.equal(validateOtp('12ab56'), 'Enter the 6-digit verification code')
  assert.equal(validateOtp('12345'), 'Enter the 6-digit verification code')
  assert.equal(validateOtp('123456'), '')
})

test('completion validation handles required fields and password mismatch', () => {
  assert.equal(validateCompletion({ username: '', password: 'secret', confirmPassword: 'secret' }), 'Username is required')
  assert.equal(validateCompletion({ username: 'janedoe1', password: '', confirmPassword: '' }), 'Password is required')
  assert.equal(validateCompletion({ username: 'janedoe1', password: 'short', confirmPassword: 'short' }), 'Password must be at least 12 characters')
  assert.equal(validateCompletion({ username: 'janedoe1', password: 'a'.repeat(25), confirmPassword: 'a'.repeat(25) }), 'Password must not exceed 24 characters')
  assert.equal(validateCompletion({ username: 'janedoe1', password: 'longenough1A!', confirmPassword: '' }), 'Confirm password is required')
  assert.equal(validateCompletion({ username: 'janedoe1', password: 'longenough1A!', confirmPassword: 'different' }), 'Passwords do not match')
  assert.equal(validateCompletion({ username: 'janedoe1', password: 'longenough1A!', confirmPassword: 'longenough1A!' }), '')
})

test('registration validation rejects unsafe names and usernames', () => {
  assert.equal(validateDetails({ firstName: 'Jane\n', lastName: 'Doe', email: 'a@b.com' }), 'First name contains invalid characters')
  assert.equal(validateCompletion({ username: 'not valid', password: 'longenough1A!', confirmPassword: 'longenough1A!' }), 'Username must be 8-16 characters using only letters and numbers')
  assert.equal(normalizeUsername('  Jane_Doe '), 'jane_doe')
})

test('password policy allows passphrases without composition rules', () => {
  const passphrase = 'CorrectHorseBattery1'
  assert.equal(validateCompletion({ username: 'janedoe1', password: passphrase, confirmPassword: passphrase }), '')
})

test('credential format helpers enforce the signup username and password formats', () => {
  assert.equal(isUsernameValid('abcdefgh'), true)
  assert.equal(isUsernameValid('abcdefghijklmnop'), true)
  assert.equal(isUsernameValid('abc12345'), true)
  for (const username of ['abcdefg', 'abcdefghijklmnopq', 'abcd_123', 'abcd 123', 'abcd-123', 'abcd!123', 'abcdé123']) {
    assert.equal(isUsernameValid(username), false)
  }

  assert.equal(isPasswordValid('abcdefghijkl'), true)
  assert.equal(isPasswordValid('Abcdefgh1234'), true)
  assert.equal(isPasswordValid('!@#$%^&*()ab'), true)
  for (const password of ['a'.repeat(11), 'a'.repeat(25), 'abcdefghijk ', 'abcdefghij_', 'abcdefghij-', 'abcdefghij.', 'abcdefghij=']) {
    assert.equal(isPasswordValid(password), false)
  }
})

test('OTP request success message pluralizes remaining requests', () => {
  assert.equal(formatOtpRequestMessage(4), 'Verification code sent. 4 requests remaining.')
  assert.equal(formatOtpRequestMessage(3), 'Verification code sent. 3 requests remaining.')
  assert.equal(formatOtpRequestMessage(1), 'Verification code sent. 1 request remaining.')
  assert.equal(formatOtpRequestMessage(0), 'Verification code sent. No more requests remaining.')
})
