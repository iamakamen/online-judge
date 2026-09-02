import { useEffect, useRef, useState } from 'react'
import { checkUsernameAvailability, completeRegistration, getRegistrationStatus, startRegistration, verifyRegistrationOtp } from '../api/client'
import { useAuth } from '../auth/useAuth'
import { userFacingError } from './registerErrors'
import { LoomMark } from '../components/PrimarySidebar'
import codingWorkshop from '../assets/signup/coding-workshop-8429809.png'
import {
  createRegistrationState,
  validateCompletion,
  isUsernameValid,
  isPasswordValid,
  validateDetails,
  validateOtp,
  normalizeUsername,
  formatOtpRequestMessage,
  OTP_STATES,
} from './registerFlow'
import { clearRegistrationDraft, loadRegistrationDraft, normalizeRegistrationEmail, saveRegistrationDraft } from './registerStorage'

function Field({ label, ...props }) {
  return (
    <label className="signup-field">
      <span>{label}</span>
      <input required {...props} />
    </label>
  )
}

function ValidationIndicator({ valid, label, guidance, tooltipId }) {
  return (
    <span className={`signup-validation-indicator ${valid ? 'is-valid' : 'is-invalid'}`} role="img" aria-label={label} tabIndex="0">
      {valid ? '✓' : '×'}
      {!valid && <span id={tooltipId} className="signup-validation-tooltip" role="tooltip">{guidance}</span>}
    </span>
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
  const [savedDraft] = useState(loadRegistrationDraft)
  const [form, setForm] = useState(() => ({ ...createRegistrationState(), ...savedDraft?.form }))
  const initialEmailState = savedDraft?.emailStates?.[normalizeRegistrationEmail(savedDraft?.form?.email)]
  const [otpRequested, setOtpRequested] = useState(() => initialEmailState?.otpRequested === true)
  const [emailVerified, setEmailVerified] = useState(() => initialEmailState?.emailVerified === true)
  const [restoringVerification, setRestoringVerification] = useState(() => initialEmailState?.emailVerified === true)
  const [otpState, setOtpState] = useState(() => initialEmailState?.emailVerified ? OTP_STATES.verified : initialEmailState?.otpRequested ? OTP_STATES.sent : OTP_STATES.initial)
  const [remainingRequests, setRemainingRequests] = useState(() => initialEmailState?.remainingRequests ?? null)
  const [hasCurrentRequestQuota, setHasCurrentRequestQuota] = useState(false)
  const [cooldownUntil, setCooldownUntil] = useState(() => initialEmailState?.cooldownUntil ?? 0)
  const [cooldownSeconds, setCooldownSeconds] = useState(() => initialEmailState?.cooldownUntil ? Math.ceil((initialEmailState.cooldownUntil - Date.now()) / 1000) : 0)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [passwordVisible, setPasswordVisible] = useState(false)
  const [confirmPasswordVisible, setConfirmPasswordVisible] = useState(false)
  const [usernameAvailability, setUsernameAvailability] = useState(null)
  const [usernameChecking, setUsernameChecking] = useState(false)
  const emailStatesRef = useRef({ ...(savedDraft?.emailStates || {}) })
  const switchingEmailRef = useRef(false)

  useEffect(() => {
    const email = normalizeRegistrationEmail(form.email)
    if (!email) return
    if (switchingEmailRef.current) {
      switchingEmailRef.current = false
      return
    }
    emailStatesRef.current[email] = { otpRequested, cooldownUntil, remainingRequests, emailVerified }
    saveRegistrationDraft({ form, emailStates: emailStatesRef.current })
  }, [form, otpRequested, cooldownUntil, remainingRequests, emailVerified])

  useEffect(() => {
    const state = emailStatesRef.current[normalizeRegistrationEmail(form.email)] || {}
    setOtpRequested(state.otpRequested === true)
    setEmailVerified(state.emailVerified === true)
    setRestoringVerification(state.emailVerified === true)
    setOtpState(state.emailVerified ? OTP_STATES.verified : state.otpRequested ? OTP_STATES.sent : OTP_STATES.initial)
    setRemainingRequests(state.remainingRequests ?? null)
    setHasCurrentRequestQuota(false)
    setCooldownUntil(state.cooldownUntil ?? 0)
    setCooldownSeconds(state.cooldownUntil ? Math.ceil((state.cooldownUntil - Date.now()) / 1000) : 0)
    setError('')
    setNotice('')
  }, [form.email])

  useEffect(() => {
    if (!restoringVerification) return undefined
    let active = true
    getRegistrationStatus()
      .then((result) => {
        if (!active) return
        if (result.email !== form.email.trim()) throw new Error('Registration email does not match')
        setRestoringVerification(false)
        setEmailVerified(true)
        setOtpRequested(true)
        setOtpState(OTP_STATES.verified)
        setCooldownUntil(0)
        setCooldownSeconds(0)
        setRemainingRequests(null)
        setNotice('')
      })
      .catch(() => {
        if (!active) return
        setRestoringVerification(false)
        setEmailVerified(false)
        setOtpRequested(false)
        setCooldownUntil(0)
        setCooldownSeconds(0)
        setRemainingRequests(null)
        setError('Your registration session is missing or expired. Please request a new verification code.')
      })
    return () => { active = false }
  }, [form.email, restoringVerification])

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
    if (!emailVerified || !isUsernameValid(form.username)) {
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
    if (['firstName', 'lastName'].includes(field)) {
      setOtpRequested(false)
      setEmailVerified(false)
      setOtpState(OTP_STATES.initial)
      setRemainingRequests(null)
      setHasCurrentRequestQuota(false)
      setCooldownUntil(0)
      setCooldownSeconds(0)
      setForm((current) => ({ ...current, otp: '' }))
    } else if (field === 'email') {
      switchingEmailRef.current = true
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
      const result = await startRegistration(form.firstName.trim(), form.lastName.trim(), form.email.trim())
      setOtpRequested(true)
      setEmailVerified(false)
      setForm((current) => ({ ...current, otp: '' }))
      setRemainingRequests(Number(result.remaining_requests))
      setHasCurrentRequestQuota(true)
      setOtpState(result.remaining_requests === 0 ? OTP_STATES.maxRequestsReached : OTP_STATES.sent)
      const cooldown = Number(result.cooldown_seconds) || 0
      setCooldownUntil(Date.now() + cooldown * 1000)
      setNotice(formatOtpRequestMessage(Number(result.remaining_requests)))
    } catch (requestError) {
      if (requestError.code === 'request_limit') {
        setOtpState(OTP_STATES.maxRequestsReached)
        setHasCurrentRequestQuota(true)
      }
      else setOtpState(OTP_STATES.requestError)
      if (requestError.code === 'request_cooldown' || requestError.retryAfter) {
        const retryAfter = Number(requestError.retryAfter)
        if (retryAfter > 0) setCooldownUntil(Date.now() + retryAfter * 1000)
      }
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
      setCooldownUntil(0)
      setCooldownSeconds(0)
      setRemainingRequests(null)
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
      clearRegistrationDraft()
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
                <div className="signup-otp-request">
                  <button className="secondary-button" type="button" onClick={handleGetOtp} disabled={submitting || emailVerified || restoringVerification || cooldownSeconds > 0 || (hasCurrentRequestQuota && remainingRequests === 0)}>
                    {otpRequested ? 'Resend OTP' : 'Get OTP'}
                  </button>
                  {cooldownSeconds > 0 && <p className="signup-otp-cooldown" role="status">Available in {String(Math.floor(cooldownSeconds / 60)).padStart(2, '0')}:{String(cooldownSeconds % 60).padStart(2, '0')}</p>}
                </div>
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
                  <span className={`signup-validation-control ${form.username ? 'has-validation' : ''} ${form.username && !isUsernameValid(form.username) ? 'has-guidance' : ''}`}>
                    <input required value={form.username} onChange={(event) => update('username', event.target.value)} autoComplete="username" disabled={!emailVerified} aria-describedby={form.username && !isUsernameValid(form.username) ? 'username-format-guidance' : undefined} title={form.username && !isUsernameValid(form.username) ? 'Username must be 8–16 characters using only letters and numbers.' : undefined} />
                    {emailVerified && form.username && (
                      <ValidationIndicator
                        valid={isUsernameValid(form.username)}
                        label={isUsernameValid(form.username) ? 'Username format valid' : 'Username format invalid'}
                        guidance="Username must be 8–16 characters using only letters and numbers."
                        tooltipId="username-format-guidance"
                      />
                    )}
                  </span>
                </span>
              </label>
            </div>
            <div className="signup-row signup-row-two">
              <label className="signup-field signup-password-field">
                <span>Password</span>
                <span className={`signup-input-with-icon signup-validation-control ${form.password ? 'has-validation' : ''} ${form.password && !isPasswordValid(form.password) ? 'has-guidance' : ''}`}>
                  <input type={passwordVisible ? 'text' : 'password'} value={form.password} onChange={(event) => update('password', event.target.value)} autoComplete="new-password" disabled={!emailVerified} aria-describedby={form.password && !isPasswordValid(form.password) ? 'password-format-guidance' : undefined} title={form.password && !isPasswordValid(form.password) ? 'Password must be 12–24 characters using only letters, numbers, and !@#$%^&*()' : undefined} />
                  {form.password && <ValidationIndicator valid={isPasswordValid(form.password)} label={isPasswordValid(form.password) ? 'Password format valid' : 'Password format invalid'} guidance="Password must be 12–24 characters using only letters, numbers, and !@#$%^&*()" tooltipId="password-format-guidance" />}
                  <button className="signup-icon-button" type="button" onClick={() => setPasswordVisible((visible) => !visible)} aria-label={passwordVisible ? 'Hide password' : 'Show password'} disabled={!emailVerified}>
                    <EyeIcon />
                  </button>
                </span>
              </label>
              <label className="signup-field signup-password-field">
                <span>Confirm Password</span>
                <span className={`signup-input-with-icon signup-validation-control ${form.confirmPassword ? 'has-validation' : ''} ${form.password && form.confirmPassword && form.password !== form.confirmPassword ? 'has-guidance' : ''}`}>
                  <input type={confirmPasswordVisible ? 'text' : 'password'} value={form.confirmPassword} onChange={(event) => update('confirmPassword', event.target.value)} autoComplete="new-password" disabled={!emailVerified} aria-describedby={form.password && form.confirmPassword && form.password !== form.confirmPassword ? 'password-match-guidance' : undefined} />
                  {form.password && form.confirmPassword && <ValidationIndicator valid={form.password === form.confirmPassword} label={form.password === form.confirmPassword ? 'Passwords match' : 'Passwords do not match'} guidance="Passwords do not match." tooltipId="password-match-guidance" />}
                  <button className="signup-icon-button" type="button" onClick={() => setConfirmPasswordVisible((visible) => !visible)} aria-label={confirmPasswordVisible ? 'Hide confirm password' : 'Show confirm password'} disabled={!emailVerified}>
                    <EyeIcon />
                  </button>
                </span>
              </label>
            </div>
            <div className="signup-message-region" aria-live="polite">
              {(error || notice) && <p className={error ? 'error-message' : 'success-message'} role={error ? 'alert' : 'status'}>{error || notice}</p>}
              {!error && !notice && !emailVerified && otpRequested && remainingRequests !== null && (
                <p className="success-message" role="status">{formatOtpRequestMessage(remainingRequests)}</p>
              )}
            </div>
            <div className="signup-actions">
              <button className="signup-submit" type="submit" disabled={submitting}>Sign up</button>
              <span className="signup-or" aria-hidden="true">or</span>
              <button className="signup-signin" type="button" onClick={() => navigate('/signin')}>Sign in</button>
            </div>
          </form>
        </section>
      </section>
    </main>
  )
}
