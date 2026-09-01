export function userFacingError(requestError, fallback = 'Something went wrong. Please try again.') {
  const message = String(requestError?.message || '')
  const detail = message || String(requestError?.detail || '')
  if (requestError?.code === 'NETWORK_ERROR') return 'We couldn\'t contact the server. Check your connection and try again.'
  if (requestError?.code === 'otp_invalid') return 'The verification code is incorrect.'
  if (requestError?.code === 'otp_expired') return 'This verification code has expired. Please request a new code.'
  if (requestError?.code === 'otp_superseded') return 'This verification code is no longer valid because a newer code was requested.'
  if (requestError?.code === 'otp_attempt_limit') return 'Too many incorrect attempts. This verification code is no longer valid. Please request a new code.'
  if (requestError?.code === 'verification_attempt_limit') return "You've reached the maximum number of verification attempts for this registration window. Please try again later."
  if (requestError?.status === 429) {
    if (requestError.code === 'request_limit') return "You've reached the maximum of 5 verification-code requests for this 20-minute window. Please try again later."
    if (requestError.code === 'request_cooldown') return 'Please wait before requesting another verification code.'
    const retryAfter = Number(requestError.retryAfter || detail.match(/(\d+) seconds?/i)?.[1])
    if (retryAfter > 0) {
      const time = retryAfter >= 60
        ? `${Math.ceil(retryAfter / 60)} minute${Math.ceil(retryAfter / 60) === 1 ? '' : 's'}`
        : `${retryAfter} second${retryAfter === 1 ? '' : 's'}`
      return `Please wait ${time} before requesting another verification code.`
    }
  }
  const replacements = [
    ['Email already registered', 'That email is already registered.'],
    ['Username already taken', 'Username is already taken.'],
    ['Registration session not found', 'Your signup session has expired. Please start again.'],
    ['OTP expired', 'Your verification code expired. Request a new code.'],
    ['OTP attempt limit exceeded', 'Too many incorrect attempts. This verification code is no longer valid. Please request a new code.'],
    ['OTP superseded by newer OTP', 'This verification code is no longer valid because a newer code was requested.'],
    ['Registration verification attempt limit exceeded', "You've reached the maximum number of verification attempts for this registration window. Please try again later."],
    ['OTP request limit exceeded', "You've reached the maximum of 5 verification-code requests for this 20-minute window. Please try again later."],
    ['Unable to send verification email', "We couldn't send the verification code. Please try again."],
    ['Email already verified', 'This email is already verified.'],
    ['Invalid OTP', 'That verification code is invalid.'],
  ]
  const replacement = replacements.find(([source]) => message.includes(source))
  if (replacement) return replacement[1]
  if (requestError?.status >= 500) return 'Something went wrong while sending the verification code. Please try again.'
  if (requestError?.status === 422) return detail === 'Request failed' ? 'Enter valid signup details and try again.' : detail
  if (requestError?.status === 400) return detail === 'Request failed' ? 'The signup details were not accepted. Check them and try again.' : detail
  if (detail && detail !== 'Request failed') return detail
  return fallback
}
