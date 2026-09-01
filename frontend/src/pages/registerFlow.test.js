import assert from 'node:assert/strict'
import { test } from 'node:test'
import {
  createRegistrationState,
  REGISTER_STEPS,
  validateCompletion,
  validateDetails,
  validateOtp,
  normalizeUsername,
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
  assert.equal(validateCompletion({ username: 'jane', password: '', confirmPassword: '' }), 'Password is required')
  assert.equal(validateCompletion({ username: 'jane', password: 'short', confirmPassword: 'short' }), 'Password must be at least 12 characters')
  assert.equal(validateCompletion({ username: 'jane', password: 'a'.repeat(129), confirmPassword: 'a'.repeat(129) }), 'Password must not exceed 128 characters')
  assert.equal(validateCompletion({ username: 'jane', password: 'long-enough1', confirmPassword: '' }), 'Confirm password is required')
  assert.equal(validateCompletion({ username: 'jane', password: 'long-enough1', confirmPassword: 'different' }), 'Passwords do not match')
  assert.equal(validateCompletion({ username: 'jane', password: 'long-enough1', confirmPassword: 'long-enough1' }), '')
})

test('registration validation rejects unsafe names and usernames', () => {
  assert.equal(validateDetails({ firstName: 'Jane\n', lastName: 'Doe', email: 'a@b.com' }), 'First name contains invalid characters')
  assert.equal(validateCompletion({ username: 'not valid', password: 'long-enough1', confirmPassword: 'long-enough1' }), 'Username may contain only letters, numbers, and underscores')
  assert.equal(normalizeUsername('  Jane_Doe '), 'jane_doe')
})

test('password policy allows passphrases without composition rules', () => {
  const passphrase = 'correct horse battery staple'
  assert.equal(validateCompletion({ username: 'jane', password: passphrase, confirmPassword: passphrase }), '')
})
