import assert from 'node:assert/strict'
import { test } from 'node:test'
import { userFacingError } from './registerErrors.js'

test('registration errors use specific user-facing messages', () => {
  assert.equal(userFacingError({ status: 429, code: 'request_cooldown', message: 'Please wait before requesting another code' , retryAfter: '119' }), 'Please wait before requesting another verification code.')
  assert.equal(userFacingError({ status: 429, code: 'request_limit', message: 'OTP request limit exceeded' }), "You've reached the maximum of 5 verification-code requests for this 20-minute window. Please try again later.")
  assert.equal(userFacingError({ status: 400, message: 'Unable to send verification email' }), "We couldn't send the verification code. Please try again.")
  assert.equal(userFacingError({ status: 400, message: 'Registration session not found' }), 'Your signup session has expired. Please start again.')
  assert.equal(userFacingError({ status: 400, code: 'otp_invalid', message: 'The verification code is incorrect.' }), 'The verification code is incorrect.')
  assert.equal(userFacingError({ status: 400, code: 'otp_expired', message: 'This verification code has expired.' }), 'This verification code has expired. Please request a new code.')
  assert.equal(userFacingError({ status: 400, code: 'otp_superseded', message: 'This verification code is no longer valid because a newer code was requested.' }), 'This verification code is no longer valid because a newer code was requested.')
  assert.equal(userFacingError({ status: 400, code: 'verification_attempt_limit', message: 'Registration verification attempt limit exceeded' }), "You've reached the maximum number of verification attempts for this registration window. Please try again later.")
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
