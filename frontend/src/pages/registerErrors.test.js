import assert from 'node:assert/strict'
import { test } from 'node:test'
import { userFacingError } from './registerErrors.js'

test('registration errors use specific user-facing messages', () => {
  assert.equal(userFacingError({ status: 429, message: 'Please wait 119 seconds' , retryAfter: '119' }), 'Please wait 2 minutes before requesting another verification code.')
  assert.equal(userFacingError({ status: 429, message: 'OTP request limit exceeded' }), 'You have reached the maximum of 3 verification-code requests for this signup.')
  assert.equal(userFacingError({ status: 400, message: 'Unable to send verification email' }), "We couldn't send the verification code. Please try again.")
  assert.equal(userFacingError({ status: 400, message: 'Registration session not found' }), 'Your signup session has expired. Please start again.')
  assert.equal(userFacingError({ status: 422, message: 'Enter a valid email address' }), 'Enter a valid email address')
  assert.equal(userFacingError({ status: 500, message: 'Internal Server Error' }), 'Something went wrong while sending the verification code. Please try again.')
  assert.equal(userFacingError({ code: 'NETWORK_ERROR', message: 'Failed to fetch' }), "We couldn't contact the server. Check your connection and try again.")
})

test('registration errors never expose the generic request fallback', () => {
  for (const error of [
    { status: 400, message: 'Request failed' },
    { status: 422, message: 'Request failed' },
    { status: 500, message: 'Request failed' },
    { code: 'NETWORK_ERROR', message: '' },
  ]) assert.notEqual(userFacingError(error), 'Request failed')
})
