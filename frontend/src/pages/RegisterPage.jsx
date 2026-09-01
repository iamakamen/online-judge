import { useEffect, useState } from 'react'
import { checkUsernameAvailability, completeRegistration, startRegistration, verifyRegistrationOtp } from '../api/client'
import { useAuth } from '../auth/useAuth'
import { userFacingError } from './registerErrors'
import { LoomMark } from '../components/PrimarySidebar'
import codingWorkshop from '../assets/signup/coding-workshop-8429809.png'
import {
  createRegistrationState,
  validateCompletion,
  validateDetails,
  validateOtp,
  normalizeUsername,
  OTP_COOLDOWN_SECONDS,
  OTP_REQUEST_LIMIT,
  OTP_STATES,
} from './registerFlow'

function Field({ label, ...props }) {
  return (
    <label className="signup-field">
      <span>{label}</span>
      <input required {...props} />
    </label>
  )
}

function EyeIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="signup-eye-icon">
      <path d="M2.5 12s3.2-5 9.5-5 9.5 5 9.5 5-3.2 5-9.5 5-9.5-5-9.5-5Z" />
      <circle cx="12" cy="12" r="2.5" />
    </svg>
  )
}

function SignupIllustration() {
  return (
    <div className="signup-illustration-wrap">
      <img src={codingWorkshop} alt="Coding laptop and coffee cup" className="signup-illustration" />
    </div>
  )
}

export function RegisterPage({ navigate }) {
  const { authenticate } = useAuth()
  const [form, setForm] = useState(createRegistrationState)
  const [otpRequested, setOtpRequested] = useState(false)
  const [emailVerified, setEmailVerified] = useState(false)
  const [otpState, setOtpState] = useState(OTP_STATES.initial)
  const [otpRequestCount, setOtpRequestCount] = useState(0)
  const [cooldownUntil, setCooldownUntil] = useState(0)
  const [cooldownSeconds, setCooldownSeconds] = useState(0)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [passwordVisible, setPasswordVisible] = useState(false)
  const [confirmPasswordVisible, setConfirmPasswordVisible] = useState(false)
  const [usernameAvailability, setUsernameAvailability] = useState(null)
  const [usernameChecking, setUsernameChecking] = useState(false)

  useEffect(() => {
    if (!cooldownUntil) return undefined
    const updateCooldown = () => {
      const remaining = Math.max(0, Math.ceil((cooldownUntil - Date.now()) / 1000))
      setCooldownSeconds(remaining)
      if (!remaining) {
        setCooldownUntil(0)
        setOtpState((current) => [OTP_STATES.sent, OTP_STATES.requestError].includes(current) ? OTP_STATES.cooldownExpired : current)
      }
    }
    updateCooldown()
    const timer = window.setInterval(updateCooldown, 1000)
    return () => window.clearInterval(timer)
  }, [cooldownUntil])

  useEffect(() => {
    const username = normalizeUsername(form.username)
    if (!emailVerified || !/^[A-Za-z0-9_]{1,100}$/.test(username)) {
      setUsernameAvailability(null)
      setUsernameChecking(false)
      return undefined
    }
    let active = true
    setUsernameAvailability(null)
    setUsernameChecking(true)
    const timer = window.setTimeout(async () => {
      try {
        const result = await checkUsernameAvailability(username)
        if (active) setUsernameAvailability(Boolean(result.available))
      } catch {
        if (active) setUsernameAvailability(null)
      } finally {
        if (active) setUsernameChecking(false)
      }
    }, 400)
    return () => {
      active = false
      window.clearTimeout(timer)
    }
  }, [emailVerified, form.username])

  function update(field, value) {
    setForm((current) => ({ ...current, [field]: value }))
    setError('')
    setNotice('')
    if (['firstName', 'lastName', 'email'].includes(field)) {
      setOtpRequested(false)
      setEmailVerified(false)
      setOtpState(OTP_STATES.initial)
      setOtpRequestCount(0)
      setCooldownUntil(0)
      setCooldownSeconds(0)
      setForm((current) => ({ ...current, otp: '' }))
    }
  }

  async function handleGetOtp() {
    const validationError = validateDetails(form)
    if (validationError) {
      setError(validationError)
      return
    }
    setSubmitting(true)
    setOtpState(OTP_STATES.requesting)
    setError('')
    setNotice('')
    try {
      await startRegistration(form.firstName.trim(), form.lastName.trim(), form.email.trim())
      setOtpRequested(true)
      setEmailVerified(false)
      setForm((current) => ({ ...current, otp: '' }))
      const nextCount = otpRequestCount + 1
      setOtpRequestCount(nextCount)
      setOtpState(nextCount >= OTP_REQUEST_LIMIT ? OTP_STATES.maxRequestsReached : OTP_STATES.sent)
      setCooldownUntil(Date.now() + OTP_COOLDOWN_SECONDS * 1000)
      setNotice(`Verification code sent to ${form.email.trim()}.`)
    } catch (requestError) {
      if (requestError.status === 429 && /limit exceeded/i.test(requestError.message)) setOtpState(OTP_STATES.maxRequestsReached)
      else setOtpState(OTP_STATES.requestError)
      setError(userFacingError(requestError, 'Unable to send verification code'))
    } finally {
      setSubmitting(false)
    }
  }

  async function handleVerifyOtp() {
    const validationError = validateOtp(form.otp)
    if (validationError) {
      setError(validationError)
      return
    }
    setSubmitting(true)
    setOtpState(OTP_STATES.verifying)
    setError('')
    setNotice('')
    try {
      await verifyRegistrationOtp(form.email.trim(), form.otp.trim())
      setEmailVerified(true)
      setOtpState(OTP_STATES.verified)
      setNotice('')
    } catch (requestError) {
      setOtpState(OTP_STATES.otpError)
      setError(userFacingError(requestError, 'Unable to verify your email'))
    } finally {
      setSubmitting(false)
    }
  }

  async function handleSignup(event) {
    event.preventDefault()
    if (!emailVerified) {
      setError('Verify your email before signing up')
      return
    }
    if (usernameAvailability !== true) {
      setError(usernameChecking ? 'Wait for username availability to finish' : 'Choose an available username')
      return
    }
    const validationError = validateCompletion(form)
    if (validationError) {
      setError(validationError)
      return
    }
    setSubmitting(true)
    setError('')
    setNotice('Creating account...')
    try {
      const session = await completeRegistration(form.email.trim(), normalizeUsername(form.username), form.password, form.confirmPassword)
      authenticate(session)
      navigate('/dashboard')
    } catch (requestError) {
      setError(userFacingError(requestError, 'Unable to create your account'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="signup-page">
      <section className="signup-layout" aria-labelledby="signup-title">
        <aside className="signup-intro">
          <div className="signup-brand" aria-label="encode">
            <LoomMark viewBox="6 6 20 20" />
            <span>encode</span>
          </div>
          <SignupIllustration />
        </aside>

        <section className="signup-panel">
          <h1 id="signup-title">Sign up</h1>
          <form className="signup-form" onSubmit={handleSignup}>
            <div className="signup-row signup-row-two">
              <Field label="First Name" value={form.firstName} onChange={(event) => update('firstName', event.target.value)} autoComplete="given-name" />
              <Field label="Last Name" value={form.lastName} onChange={(event) => update('lastName', event.target.value)} autoComplete="family-name" />
            </div>
            <div className="signup-row signup-row-email">
              <div className="signup-email-group">
                <Field label="Email" type="email" value={form.email} onChange={(event) => update('email', event.target.value)} autoComplete="email" disabled={emailVerified || submitting} />
                <button className="secondary-button" type="button" onClick={handleGetOtp} disabled={submitting || emailVerified || cooldownSeconds > 0 || otpRequestCount >= OTP_REQUEST_LIMIT}>
                  {otpRequested ? 'Resend OTP' : 'Get OTP'}
                </button>
              </div>
            </div>
            <div className="signup-row signup-row-otp">
              <div className="signup-otp-group">
                <Field label="Enter OTP" value={form.otp} onChange={(event) => update('otp', event.target.value)} inputMode="numeric" autoComplete="one-time-code" disabled={!otpRequested || emailVerified} />
                <button className={`secondary-button signup-verify-button${emailVerified ? ' is-verified' : ''}`} type="button" onClick={handleVerifyOtp} disabled={!otpRequested || emailVerified || submitting}>
                  {emailVerified ? 'Verified' : otpState === OTP_STATES.verifying ? 'Verifying…' : 'Verify'}
                </button>
              </div>
              <label className="signup-field">
                <span>Username</span>
                <span className="signup-username-input">
                  <input required value={form.username} onChange={(event) => update('username', event.target.value)} autoComplete="username" disabled={!emailVerified} aria-describedby="username-availability" />
                  {emailVerified && usernameAvailability !== null && !usernameChecking && (
                    <span
                      id="username-availability"
                      className={`signup-username-indicator ${usernameAvailability ? 'is-available' : 'is-taken'}`}
                      title={usernameAvailability ? 'Username available' : 'Username already taken'}
                      aria-label={usernameAvailability ? 'Username available' : 'Username already taken'}
                      tabIndex="0"
                    >
                      {usernameAvailability ? '✓' : '×'}
                    </span>
                  )}
                </span>
              </label>
            </div>
            <div className="signup-row signup-row-two">
              <label className="signup-field signup-password-field">
                <span>Password</span>
                <span className="signup-input-with-icon">
                  <input type={passwordVisible ? 'text' : 'password'} value={form.password} onChange={(event) => update('password', event.target.value)} autoComplete="new-password" disabled={!emailVerified} />
                  <button className="signup-icon-button" type="button" onClick={() => setPasswordVisible((visible) => !visible)} aria-label={passwordVisible ? 'Hide password' : 'Show password'} disabled={!emailVerified}>
                    <EyeIcon />
                  </button>
                </span>
              </label>
              <label className="signup-field signup-password-field">
                <span>Confirm Password</span>
                <span className="signup-input-with-icon">
                  <input type={confirmPasswordVisible ? 'text' : 'password'} value={form.confirmPassword} onChange={(event) => update('confirmPassword', event.target.value)} autoComplete="new-password" disabled={!emailVerified} />
                  <button className="signup-icon-button" type="button" onClick={() => setConfirmPasswordVisible((visible) => !visible)} aria-label={confirmPasswordVisible ? 'Hide confirm password' : 'Show confirm password'} disabled={!emailVerified}>
                    <EyeIcon />
                  </button>
                </span>
              </label>
            </div>
            <div className="signup-message-region" aria-live="polite">
              {(error || notice) && <p className={error ? 'error-message' : 'success-message'} role={error ? 'alert' : 'status'}>{error || notice}</p>}
            </div>
            <div className="signup-actions">
              <button className="signup-submit" type="submit" disabled={submitting}>Sign up</button>
              <span className="signup-or" aria-hidden="true">or</span>
              <button className="signup-signin" type="button" onClick={() => navigate('/login')}>Sign in</button>
            </div>
          </form>
        </section>
      </section>
    </main>
  )
}
