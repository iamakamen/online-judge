export const REGISTER_STEPS = {
  details: 1,
  verification: 2,
  completion: 3,
}

export const OTP_STATES = {
  initial: 'initial',
  requesting: 'otp-requesting',
  sent: 'otp-sent',
  verifying: 'verifying',
  verified: 'verified',
  otpError: 'otp-error',
  requestError: 'request-error',
  cooldownExpired: 'cooldown-expired',
  maxRequestsReached: 'max-requests-reached',
}

export const OTP_REQUEST_LIMIT = 3
export const OTP_COOLDOWN_SECONDS = 120
export const PASSWORD_MIN_LENGTH = 12
export const PASSWORD_MAX_LENGTH = 128

export function createRegistrationState() {
  return {
    step: REGISTER_STEPS.details,
    firstName: '',
    lastName: '',
    email: '',
    otp: '',
    username: '',
    password: '',
    confirmPassword: '',
  }
}

export function validateDetails({ firstName, lastName, email }) {
  if (!firstName.trim()) return 'First name is required'
  if (firstName.trim().length > 100) return 'First name is too long'
  if ([...firstName].some((character) => character.charCodeAt(0) < 32 || character.charCodeAt(0) === 127)) return 'First name contains invalid characters'
  if (!lastName.trim()) return 'Last name is required'
  if (lastName.trim().length > 100) return 'Last name is too long'
  if ([...lastName].some((character) => character.charCodeAt(0) < 32 || character.charCodeAt(0) === 127)) return 'Last name contains invalid characters'
  if (!email.trim()) return 'Email is required'
  if (!/^\S+@\S+\.\S+$/.test(email.trim())) return 'Enter a valid email address'
  return ''
}

export function validateOtp(otp) {
  if (!otp.trim()) return 'Verification code is required'
  if (!/^\d{6}$/.test(otp.trim())) return 'Enter the 6-digit verification code'
  return ''
}

export function validateCompletion({ username, password, confirmPassword }) {
  if (!username.trim()) return 'Username is required'
  if (!/^[A-Za-z0-9_]{1,100}$/.test(username.trim())) return 'Username may contain only letters, numbers, and underscores'
  if (!password) return 'Password is required'
  if (password.length < PASSWORD_MIN_LENGTH) return 'Password must be at least 12 characters'
  if (password.length > PASSWORD_MAX_LENGTH) return 'Password must not exceed 128 characters'
  if (!confirmPassword) return 'Confirm password is required'
  if (password !== confirmPassword) return 'Passwords do not match'
  return ''
}

export function normalizeUsername(username) {
  return username.trim().toLowerCase()
}
