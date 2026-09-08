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
  assert.match(pageSource, /remaining_requests/)
  assert.match(pageSource, /cooldown_seconds/)
  assert.match(pageSource, /disabled=\{emailVerified \|\| submitting\}/)
  assert.match(pageSource, /signup-message-region/)
  assert.match(pageSource, /is-verified/)
  assert.doesNotMatch(pageSource, /Sending/)
  assert.doesNotMatch(pageSource, /Max requests'/)
  assert.doesNotMatch(pageSource, /Email verified\. Complete your account details\./)
  assert.match(pageSource, /Creating account\.\.\./)
  assert.match(pageSource, /authenticate\(session\)/)
  assert.match(pageSource, /Resend OTP/)
  assert.match(pageSource, /Available in/)
  assert.match(pageSource, /signup-otp-request/)
  assert.match(pageSource, /formatOtpRequestMessage/)
  assert.doesNotMatch(pageSource, /verification_proof/)
  assert.match(pageSource, /setCooldownUntil\(0\)/)
  assert.match(pageSource, /setCooldownSeconds\(0\)/)
  assert.match(pageSource, /setRemainingRequests\(null\)/)
  assert.doesNotMatch(pageSource, /Verification code sent to \$\{form\.email\.trim\(\)\}/)
  assert.doesNotMatch(pageSource, /Sending\.\.\./)
})

test('Sign-up page maps expected OTP failures without showing the generic request message', () => {
  assert.match(pageSource, /userFacingError/)
  assert.match(pageSource, /registerErrors/)
  assert.doesNotMatch(pageSource, /return message \|\| fallback/)
})

test('Sign-up page restores only safe refresh state and clears request status after verification', () => {
  assert.match(pageSource, /loadRegistrationDraft/)
  assert.match(pageSource, /saveRegistrationDraft/)
  assert.match(pageSource, /savedDraft\?\.emailStates/)
  assert.match(pageSource, /normalizeRegistrationEmail/)
  assert.doesNotMatch(pageSource, /Last known:/)
  assert.match(pageSource, /formatOtpRequestMessage\(remainingRequests\)/)
  assert.doesNotMatch(pageSource, /savedDraft\?\.password/)
  assert.doesNotMatch(pageSource, /savedDraft\?\.otp\W/)
  assert.doesNotMatch(pageSource, /savedDraft\?\.verificationProof/)
  assert.match(pageSource, /saveRegistrationDraft\(\{ form, emailStates: emailStatesRef\.current, lastActivityAt: draftLastActivityAtRef\.current \}\)/)
  assert.match(pageSource, /!emailVerified && otpRequested && remainingRequests !== null/)
  assert.match(pageSource, /getRegistrationStatus/)
  assert.match(pageSource, /setEmailVerified\(true\)/)
  assert.match(pageSource, /setRemainingRequests\(null\)/)
  assert.match(pageSource, /setCooldownSeconds\(0\)/)
  assert.match(pageSource, /setNotice\(''\)/)
})

test('Sign-up draft expires by inactivity and tracks only form-scoped activity', () => {
  assert.match(pageSource, /REGISTER_DRAFT_INACTIVITY_MS/)
  assert.match(pageSource, /lastActivityAt/)
  assert.match(pageSource, /onFocusCapture=\{recordActivity\}/)
  assert.match(pageSource, /onPointerDownCapture=\{recordActivity\}/)
  assert.match(pageSource, /onKeyDownCapture=\{recordActivity\}/)
  assert.match(pageSource, /const expired = draftExpiredRef\.current \|\| expireDraftIfInactive\(\)/)
  assert.match(pageSource, /if \(expired && !allowRecreate\) return/)
  assert.match(pageSource, /recordActivity\(\{ allowRecreate: true, persist: false \}\)/)
  assert.match(pageSource, /document\.addEventListener\('visibilitychange'/)
  assert.match(pageSource, /document\.removeEventListener\('visibilitychange'/)
  assert.match(pageSource, /window\.clearTimeout/)
  assert.match(pageSource, /clearRegistrationDraft\(\)/)
})

test('Sign-up page provides non-shifting credential validation indicators and guidance', () => {
  assert.match(pageSource, /signup-validation-indicator/)
  assert.match(pageSource, /signup-validation-tooltip/)
  assert.match(pageSource, /Username must be 8–16 characters using only letters and numbers\./)
  assert.match(pageSource, /guidance="Password must be 12–24 characters using only letters, numbers, and !@#\$%\^&\*\(\)"/)
  assert.match(pageSource, /Passwords do not match\./)
  assert.match(pageSource, /isUsernameValid/)
  assert.match(pageSource, /isPasswordValid/)
  assert.match(pageSource, /form\.password && form\.confirmPassword/)
  assert.match(pageSource, /signup-input-with-icon signup-validation-control/)
})
