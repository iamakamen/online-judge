import { useCallback, useEffect, useRef, useState } from 'react'
import './App.css'
import { AuthProvider } from './auth/AuthContext'
import { useAuth } from './auth/useAuth'
import { Dashboard } from './pages/Dashboard'

const HISTORY_STATE_KEY = '__onlineJudge'

function createEntryId() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`
}

function getHistoryEntryId() {
  return window.history.state?.[HISTORY_STATE_KEY]?.entryId ?? null
}

function ensureHistoryEntryId() {
  const entryId = getHistoryEntryId()
  if (entryId) return entryId

  const nextEntryId = createEntryId()
  const currentState = window.history.state
  const nextState = currentState && typeof currentState === 'object'
    ? { ...currentState, [HISTORY_STATE_KEY]: { entryId: nextEntryId } }
    : { [HISTORY_STATE_KEY]: { entryId: nextEntryId } }

  window.history.replaceState(nextState, '', window.location.href)
  return nextEntryId
}

function getLocation() {
  return {
    pathname: window.location.pathname,
    search: window.location.search,
    hash: window.location.hash,
  }
}

function usePathname() {
  const [location, setLocation] = useState(getLocation)
  const currentEntryIdRef = useRef(null)
  const positionsRef = useRef(new Map())
  const transitionRef = useRef('initial')

  const navigate = useCallback((path) => {
    const nextEntryId = createEntryId()
    const currentEntryId = currentEntryIdRef.current

    if (currentEntryId) {
      positionsRef.current.set(currentEntryId, {
        x: window.scrollX,
        y: window.scrollY,
      })
    }

    const currentState = window.history.state
    const nextState = currentState && typeof currentState === 'object'
      ? { ...currentState, [HISTORY_STATE_KEY]: { entryId: nextEntryId } }
      : { [HISTORY_STATE_KEY]: { entryId: nextEntryId } }

    window.history.pushState(nextState, '', path)
    currentEntryIdRef.current = nextEntryId
    positionsRef.current.set(nextEntryId, { x: 0, y: 0 })
    transitionRef.current = 'push'
    setLocation(getLocation())
  }, [])

  useEffect(() => {
    window.history.scrollRestoration = 'manual'

    const entryId = ensureHistoryEntryId()
    currentEntryIdRef.current = entryId
    positionsRef.current.set(entryId, { x: 0, y: 0 })
    window.scrollTo(0, 0)

    const onScroll = () => {
      const currentEntryId = currentEntryIdRef.current
      if (!currentEntryId || transitionRef.current === 'pop') return
      positionsRef.current.set(currentEntryId, {
        x: window.scrollX,
        y: window.scrollY,
      })
    }

    const onPopState = (event) => {
      const targetEntryId = event.state?.[HISTORY_STATE_KEY]?.entryId ?? ensureHistoryEntryId()
      currentEntryIdRef.current = targetEntryId
      if (!positionsRef.current.has(targetEntryId)) {
        positionsRef.current.set(targetEntryId, { x: 0, y: 0 })
      }
      transitionRef.current = 'pop'
      setLocation(getLocation())
    }

    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('popstate', onPopState)

    return () => {
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('popstate', onPopState)
    }
  }, [])

  useEffect(() => {
    const transition = transitionRef.current
    const targetEntryId = currentEntryIdRef.current
    const target = positionsRef.current.get(targetEntryId) ?? { x: 0, y: 0 }
    const hasHash = Boolean(location.hash)

    let frameId = 0
    let resizeObserver
    let attempts = 0

    const restoreHash = () => {
      const targetElement = document.getElementById(decodeURIComponent(location.hash.slice(1)))
      if (targetElement) {
        targetElement.scrollIntoView()
        transitionRef.current = 'idle'
        return true
      }
      return false
    }

    const restoreScroll = () => {
      attempts += 1
      window.scrollTo(target.x, target.y)
      if (window.scrollY === target.y || attempts >= 60) {
        transitionRef.current = 'idle'
        if (resizeObserver) resizeObserver.disconnect()
        return
      }
      frameId = requestAnimationFrame(restoreScroll)
    }

    if (transition === 'initial') return undefined

    if (hasHash) {
      const restoreAnchor = () => {
        if (restoreHash() || attempts >= 60) {
          if (resizeObserver) resizeObserver.disconnect()
          return
        }
        attempts += 1
        frameId = requestAnimationFrame(restoreAnchor)
      }

      frameId = requestAnimationFrame(restoreAnchor)
      if (typeof ResizeObserver !== 'undefined') {
        resizeObserver = new ResizeObserver(restoreAnchor)
        resizeObserver.observe(document.documentElement)
      }
      return () => {
        cancelAnimationFrame(frameId)
        if (resizeObserver) resizeObserver.disconnect()
      }
    }

    if (transition === 'push') {
      frameId = requestAnimationFrame(() => {
        window.scrollTo(0, 0)
        transitionRef.current = 'idle'
      })
      return () => cancelAnimationFrame(frameId)
    }

    frameId = requestAnimationFrame(restoreScroll)
    if (typeof ResizeObserver !== 'undefined') {
      resizeObserver = new ResizeObserver(() => {
        if (transitionRef.current === 'pop') window.scrollTo(target.x, target.y)
      })
      resizeObserver.observe(document.documentElement)
    }

    return () => {
      cancelAnimationFrame(frameId)
      if (resizeObserver) resizeObserver.disconnect()
    }
  }, [location])

  return { pathname: location.pathname, navigate }
}

function LinkButton({ children, href, navigate, className = '' }) {
  return (
    <button
      type="button"
      className={`link-button ${className}`}
      onClick={() => navigate(href)}
    >
      {children}
    </button>
  )
}

function LoginPage({ navigate }) {
  const { login, isAuthenticated } = useAuth()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    if (isAuthenticated) navigate('/dashboard')
  }, [isAuthenticated, navigate])

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login(identifier, password)
      navigate('/dashboard')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card" aria-labelledby="login-title">
        <p className="eyebrow">Online Judge</p>
        <h1 id="login-title">Welcome back</h1>
        <p className="muted">Sign in to continue to your dashboard.</p>
        <form onSubmit={handleSubmit}>
          <label>
            Username or email
            <input
              value={identifier}
              onChange={(event) => setIdentifier(event.target.value)}
              autoComplete="username"
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              required
            />
          </label>
          {error && <p className="error-message" role="alert">{error}</p>}
          <button className="primary-button" type="submit" disabled={submitting}>
            {submitting ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
        <p className="auth-footer">
          Need an account? <LinkButton href="/register" navigate={navigate}>Register</LinkButton>
        </p>
      </section>
    </main>
  )
}

function RegisterPage({ navigate }) {
  return (
    <main className="auth-page">
      <section className="auth-card" aria-labelledby="register-title">
        <p className="eyebrow">Online Judge</p>
        <h1 id="register-title">Create an account</h1>
        <p className="muted">Registration is handled by the existing email verification flow.</p>
        <p className="muted">The Dashboard module does not change that backend flow.</p>
        <LinkButton href="/login" navigate={navigate} className="primary-button">Back to sign in</LinkButton>
      </section>
    </main>
  )
}

function PracticePlaceholder({ navigate }) {
  return (
    <main className="placeholder-page">
      <p className="eyebrow">Practice</p>
      <h1>Practice is coming next</h1>
      <p className="muted">This route exists so Dashboard navigation has a destination.</p>
      <LinkButton href="/dashboard" navigate={navigate} className="primary-button">Back to Dashboard</LinkButton>
    </main>
  )
}

function ProtectedRoute({ children, navigate }) {
  const { isAuthenticated, isLoading } = useAuth()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) navigate('/login')
  }, [isAuthenticated, isLoading, navigate])

  if (isLoading || !isAuthenticated) {
    return <main className="loading-page">Checking authentication…</main>
  }

  return children
}

function AppRoutes() {
  const { pathname, navigate } = usePathname()

  if (pathname === '/login' || pathname === '/') return <LoginPage navigate={navigate} />
  if (pathname === '/register') return <RegisterPage navigate={navigate} />
  if (pathname === '/practice') {
    return <ProtectedRoute navigate={navigate}><PracticePlaceholder navigate={navigate} /></ProtectedRoute>
  }
  if (pathname === '/dashboard') {
    return <ProtectedRoute navigate={navigate}><Dashboard navigate={navigate} /></ProtectedRoute>
  }

  return <LoginPage navigate={navigate} />
}

function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}

export default App
