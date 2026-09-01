export function userFacingError(requestError, fallback = 'Something went wrong. Please try again.') {
  const message = String(requestError?.message || '')
  const detail = message || String(requestError?.detail || '')
  if (requestError?.code === 'NETWORK_ERROR') return 'We couldn\'t contact the server. Check your connection and try again.'
  if (requestError?.status === 429) {
    if (/OTP request limit exceeded/i.test(detail)) return 'You have reached the maximum of 3 verification-code requests for this signup.'
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
    ['OTP attempt limit exceeded', 'Too many incorrect attempts. Request a new code.'],
    ['OTP request limit exceeded', 'You have reached the maximum of 3 verification-code requests for this signup.'],
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
