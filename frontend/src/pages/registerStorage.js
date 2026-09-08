export const REGISTER_DRAFT_STORAGE_KEY = 'encode.signup.draft'
export const REGISTER_DRAFT_INACTIVITY_MS = 15 * 60 * 1000

function getSessionStorage() {
  try {
    return window.sessionStorage
  } catch {
    return null
  }
}

export function normalizeRegistrationEmail(email) {
  return typeof email === 'string' ? email.trim().toLowerCase() : ''
}

function isFiniteNumber(value) {
  return typeof value === 'number' && Number.isFinite(value)
}

function normalizeEmailState(state) {
  if (!state || typeof state !== 'object') return null
  return {
    otpRequested: state.otpRequested === true,
    emailVerified: state.emailVerified === true,
    cooldownUntil: isFiniteNumber(state.cooldownUntil) && state.cooldownUntil > Date.now() ? state.cooldownUntil : 0,
    remainingRequests: Number.isInteger(state.remainingRequests) && state.remainingRequests >= 0 ? state.remainingRequests : null,
  }
}

export function loadRegistrationDraft(storage = getSessionStorage(), now = Date.now()) {
  if (!storage) return null
  try {
    const parsed = JSON.parse(storage.getItem(REGISTER_DRAFT_STORAGE_KEY) || 'null')
    if (!parsed || !parsed.form) return null
    const lastActivityAt = isFiniteNumber(parsed.lastActivityAt) ? parsed.lastActivityAt : now
    if (now - lastActivityAt >= REGISTER_DRAFT_INACTIVITY_MS) {
      storage.removeItem(REGISTER_DRAFT_STORAGE_KEY)
      return null
    }
    const emailStates = {}
    if (parsed.version === 2 && parsed.emailStates && typeof parsed.emailStates === 'object') {
      for (const [email, state] of Object.entries(parsed.emailStates)) {
        const normalizedEmail = normalizeRegistrationEmail(email)
        const normalizedState = normalizeEmailState(state)
        if (normalizedEmail && normalizedState) emailStates[normalizedEmail] = normalizedState
      }
    } else if (parsed.version === 1) {
      const email = normalizeRegistrationEmail(parsed.form.email)
      const state = normalizeEmailState(parsed)
      if (email && state) emailStates[email] = state
    } else {
      return null
    }
    return {
      lastActivityAt,
      form: {
        firstName: typeof parsed.form.firstName === 'string' ? parsed.form.firstName : '',
        lastName: typeof parsed.form.lastName === 'string' ? parsed.form.lastName : '',
        email: typeof parsed.form.email === 'string' ? parsed.form.email : '',
        username: typeof parsed.form.username === 'string' ? parsed.form.username : '',
      },
      emailStates: Object.fromEntries(
        Object.entries(emailStates || {}).map(([email, state]) => [
          email,
          state?.emailVerified
            ? { ...state, cooldownUntil: 0, remainingRequests: null }
            : state,
        ]),
      ),
    }
  } catch {
    return null
  }
}

export function saveRegistrationDraft({ form, emailStates, lastActivityAt = Date.now() }, storage = getSessionStorage()) {
  if (!storage) return
  try {
    const safeEmailStates = Object.fromEntries(
      Object.entries(emailStates || {}).map(([email, state]) => [
        email,
        state?.emailVerified
          ? { ...state, cooldownUntil: 0, remainingRequests: null }
          : state,
      ]),
    )
    storage.setItem(REGISTER_DRAFT_STORAGE_KEY, JSON.stringify({
      version: 2,
      lastActivityAt,
      form: {
        firstName: form.firstName,
        lastName: form.lastName,
        email: form.email,
        username: form.username,
      },
      emailStates: safeEmailStates,
    }))
  } catch {
    // Browser storage is optional and must not affect registration.
  }
}

export function clearRegistrationDraft(storage = getSessionStorage()) {
  if (!storage) return
  try {
    storage.removeItem(REGISTER_DRAFT_STORAGE_KEY)
  } catch {
    // Browser storage is optional and must not affect registration.
  }
}
