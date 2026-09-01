import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import assert from 'node:assert/strict'

const pageSource = readFileSync(new URL('./RegisterPage.jsx', import.meta.url), 'utf8')

test('Sign-up page contains the complete registration form contract', () => {
  for (const label of ['First Name', 'Last Name', 'Email', 'Enter OTP', 'Username', 'Password', 'Confirm Password', 'Sign up', 'Sign in']) {
    assert.match(pageSource, new RegExp(label))
  }
  assert.match(pageSource, /Get OTP/)
  assert.match(pageSource, /Verify/)
  assert.match(pageSource, /navigate\('\/dashboard'\)/)
})

test('Sign-up page uses the real registration API and has no placeholder copy', () => {
  assert.match(pageSource, /startRegistration/)
  assert.match(pageSource, /verifyRegistrationOtp/)
  assert.match(pageSource, /completeRegistration/)
  assert.doesNotMatch(pageSource, /Registration is handled by the existing email verification flow/)
  assert.doesNotMatch(pageSource, /The Dashboard module does not change that backend flow/)
})

test('Sign-up page preserves the guarded OTP lifecycle and fixed status area', () => {
  assert.match(pageSource, /OTP_STATES/)
  assert.match(pageSource, /OTP_REQUEST_LIMIT/)
  assert.match(pageSource, /OTP_COOLDOWN_SECONDS/)
  assert.match(pageSource, /disabled=\{emailVerified \|\| submitting\}/)
  assert.match(pageSource, /signup-message-region/)
  assert.match(pageSource, /is-verified/)
  assert.doesNotMatch(pageSource, /Sending/)
  assert.doesNotMatch(pageSource, /Max requests'/)
  assert.doesNotMatch(pageSource, /Email verified\. Complete your account details\./)
  assert.match(pageSource, /Creating account\.\.\./)
  assert.match(pageSource, /authenticate\(session\)/)
})

test('Sign-up page maps expected OTP failures without showing the generic request message', () => {
  assert.match(pageSource, /userFacingError/)
  assert.match(pageSource, /registerErrors/)
  assert.doesNotMatch(pageSource, /return message \|\| fallback/)
})
