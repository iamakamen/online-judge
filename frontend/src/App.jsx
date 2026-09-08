import { useCallback, useEffect, useRef, useState } from 'react'
import './App.css'
import { AuthProvider } from './auth/AuthContext'
import { useAuth } from './auth/useAuth'
import { Dashboard } from './pages/Dashboard'
import { Practice } from './pages/Practice'
import { ProblemPage } from './pages/ProblemPage'
import { RegisterPage } from './pages/RegisterPage'
import { LandingPage } from './pages/LandingPage'
import { LoomMark } from './components/PrimarySidebar'
import { V2PlaceholderModal } from './components/V2PlaceholderModal'
import codingWorkshop from './assets/signup/coding-workshop-8429809.png'
import {
  createEntryId,
  createProblemPaneScrollKey,
  createScrollPositionStore,
  getHistoryEntryId,
  HISTORY_STATE_KEY,
} from './scroll/scrollRestoration'

function getLocation() {
  return {
    pathname: window.location.pathname,
    search: window.location.search,
    hash: window.location.hash,
  }
}

function ensureHistoryEntryId() {
  const entryId = getHistoryEntryId(window.history.state)
  if (entryId) return entryId

  const nextEntryId = createEntryId()
  const currentState = window.history.state
  const nextState = currentState && typeof currentState === 'object'
    ? { ...currentState, [HISTORY_STATE_KEY]: { entryId: nextEntryId } }
    : { [HISTORY_STATE_KEY]: { entryId: nextEntryId } }

  window.history.replaceState(nextState, '', window.location.href)
  return nextEntryId
}

function usePathname() {
  const [location, setLocation] = useState(getLocation)
  const [historyEntryId, setHistoryEntryId] = useState(null)
  const [navigationType, setNavigationType] = useState('initial')
  const currentEntryIdRef = useRef(null)
  const windowPositionsRef = useRef(createScrollPositionStore())
  const problemPanePositionsRef = useRef(createScrollPositionStore())
  const problemPaneRef = useRef(null)

  const captureWindowPosition = useCallback(() => {
    const entryId = currentEntryIdRef.current
    if (!entryId) return
    windowPositionsRef.current.set(entryId, { x: window.scrollX, y: window.scrollY })
  }, [])

  const captureProblemPanePosition = useCallback(() => {
    const registration = problemPaneRef.current
    if (!registration || registration.entryId !== currentEntryIdRef.current) return
    problemPanePositionsRef.current.set(
      createProblemPaneScrollKey(registration.entryId, registration.slug),
      { top: registration.element.scrollTop },
    )
  }, [])

  const registerProblemPane = useCallback((element, slug, entryId) => {
    if (!element || !slug || !entryId) return undefined
    const registration = { element, slug, entryId }
    problemPaneRef.current = registration

    const onScroll = () => {
      if (problemPaneRef.current !== registration || currentEntryIdRef.current !== entryId) return
      problemPanePositionsRef.current.set(
        createProblemPaneScrollKey(entryId, slug),
        { top: element.scrollTop },
      )
    }
    element.addEventListener('scroll', onScroll, { passive: true })

    return () => {
      element.removeEventListener('scroll', onScroll)
      if (problemPaneRef.current === registration) problemPaneRef.current = null
    }
  }, [])

  const getProblemPanePosition = useCallback((entryId, slug) => {
    return problemPanePositionsRef.current.get(createProblemPaneScrollKey(entryId, slug))?.top ?? 0
  }, [])

  const navigate = useCallback((path, { replace = false } = {}) => {
    captureWindowPosition()
    captureProblemPanePosition()

    const nextEntryId = replace ? currentEntryIdRef.current || createEntryId() : createEntryId()
    const currentState = window.history.state
    const nextState = currentState && typeof currentState === 'object'
      ? { ...currentState, [HISTORY_STATE_KEY]: { entryId: nextEntryId } }
      : { [HISTORY_STATE_KEY]: { entryId: nextEntryId } }

    window.history[replace ? 'replaceState' : 'pushState'](nextState, '', path)
    currentEntryIdRef.current = nextEntryId
    setHistoryEntryId(nextEntryId)
    setNavigationType(replace ? 'replace' : 'push')
    setLocation(getLocation())
  }, [captureProblemPanePosition, captureWindowPosition])

  useEffect(() => {
    const previousScrollRestoration = window.history.scrollRestoration
    window.history.scrollRestoration = 'manual'

    const entryId = ensureHistoryEntryId()
    currentEntryIdRef.current = entryId
    setHistoryEntryId(entryId)

    const onScroll = () => captureWindowPosition()
    const onPopState = (event) => {
      captureWindowPosition()
      captureProblemPanePosition()

      const targetEntryId = getHistoryEntryId(event.state) || ensureHistoryEntryId()
      currentEntryIdRef.current = targetEntryId
      if (!windowPositionsRef.current.has(targetEntryId)) {
        windowPositionsRef.current.set(targetEntryId, { x: 0, y: 0 })
      }
      setHistoryEntryId(targetEntryId)
      setNavigationType('pop')
      setLocation(getLocation())
    }

    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('popstate', onPopState)

    return () => {
      window.history.scrollRestoration = previousScrollRestoration
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('popstate', onPopState)
    }
  }, [captureProblemPanePosition, captureWindowPosition])

  useEffect(() => {
    if (!historyEntryId || navigationType === 'initial' || navigationType === 'replace') return undefined

    let frameId = 0
    let resizeObserver
    let attempts = 0

    const restoreHash = () => {
      const targetElement = document.getElementById(decodeURIComponent(location.hash.slice(1)))
      if (!targetElement) return false
      targetElement.scrollIntoView()
      return true
    }

    const restoreWindowPosition = () => {
      attempts += 1
      const target = windowPositionsRef.current.get(historyEntryId) ?? { x: 0, y: 0 }
      window.scrollTo(target.x, target.y)
      const reachedTarget = window.scrollX === target.x && window.scrollY === target.y
      if (reachedTarget || attempts >= 60) {
        resizeObserver?.disconnect()
        return
      }
      frameId = requestAnimationFrame(restoreWindowPosition)
    }

    const restore = () => {
      if (location.hash) {
        if (restoreHash() || attempts >= 60) {
          resizeObserver?.disconnect()
          return
        }
        attempts += 1
        frameId = requestAnimationFrame(restore)
        return
      }

      if (navigationType === 'push') {
        window.scrollTo(0, 0)
        return
      }
      restoreWindowPosition()
    }

    frameId = requestAnimationFrame(restore)
    if (typeof ResizeObserver !== 'undefined') {
      resizeObserver = new ResizeObserver(() => {
        if (navigationType === 'pop') restoreWindowPosition()
      })
      resizeObserver.observe(document.documentElement)
    }

    return () => {
      cancelAnimationFrame(frameId)
      resizeObserver?.disconnect()
    }
  }, [historyEntryId, location, navigationType])

  return {
    pathname: location.pathname,
    hash: location.hash,
    navigate,
    historyEntryId,
    navigationType,
    registerProblemPane,
    getProblemPanePosition,
  }
}

function EyeIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="signup-eye-icon">
      <path d="M2.5 12s3.2-5 9.5-5 9.5 5 9.5 5-3.2 5-9.5 5-9.5-5-9.5-5Z" />
      <circle cx="12" cy="12" r="2.5" />
    </svg>
  )
}

function RouteRedirect({ navigate, to }) {
  useEffect(() => {
    navigate(to, { replace: true })
  }, [navigate, to])

  return <main className="loading-page">Redirecting…</main>
}

function LoginPage({ navigate }) {
  const { login, isAuthenticated } = useAuth()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [passwordVisible, setPasswordVisible] = useState(false)
  const [showForgotPassword, setShowForgotPassword] = useState(false)

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
    <main className="signup-page">
      <section className="signup-layout" aria-labelledby="login-title">
        <aside className="signup-intro">
          <a className="signup-brand" href="/" aria-label="encode">
            <LoomMark viewBox="6 6 20 20" />
            <span>encode</span>
          </a>
          <div className="signup-illustration-wrap">
            <img src={codingWorkshop} alt="Coding laptop and coffee cup" className="signup-illustration" />
          </div>
        </aside>

        <section className="signup-panel">
          <h1 id="login-title">Sign in</h1>
          <form className="signup-form login-form" onSubmit={handleSubmit}>
            <div className="signup-row signup-row-email">
              <label className="signup-field">
                <span>Username or Email</span>
                <input
                  value={identifier}
                  onChange={(event) => setIdentifier(event.target.value)}
                  autoComplete="username"
                  required
                />
              </label>
            </div>
            <div className="signup-row signup-row-email">
              <label className="signup-field">
                <span>Password</span>
                <span className="signup-input-with-icon">
                  <input
                    type={passwordVisible ? 'text' : 'password'}
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    autoComplete="current-password"
                    required
                  />
                  <button className="signup-icon-button" type="button" onClick={() => setPasswordVisible((visible) => !visible)} aria-label={passwordVisible ? 'Hide password' : 'Show password'}>
                    <EyeIcon />
                  </button>
                </span>
              </label>
            </div>
            <button className="login-forgot" type="button" onClick={() => setShowForgotPassword(true)}>Forgot Password?</button>
            <div className="signup-message-region login-message-region" aria-live="polite">
              {error && <p className="error-message" role="alert">{error}</p>}
            </div>
            <div className="signup-actions">
              <button className="signup-submit" type="submit" disabled={submitting}>
                {submitting ? 'Signing in…' : 'Sign in'}
              </button>
              <span className="signup-or" aria-hidden="true">or</span>
              <button className="signup-signin" type="button" onClick={() => navigate('/signup')}>Sign up</button>
            </div>
          </form>
        </section>
      </section>
      {showForgotPassword && (
        <V2PlaceholderModal feature="Forgot Password" onClose={() => setShowForgotPassword(false)} titleId="forgot-password-v2-title" theme="auth" />
      )}
    </main>
  )
}

function AuthRestoringSurface({ pathname }) {
  const routeKind = pathname === '/dashboard'
    ? 'dashboard'
    : pathname === '/practice'
      ? 'practice'
      : pathname.startsWith('/problems/')
        ? 'problem'
        : 'application'

  return (
    <main className={`auth-restoring-surface auth-restoring-surface-${routeKind}`} aria-busy="true" aria-label="Restoring session">
      <LoomMark viewBox="6 6 20 20" />
    </main>
  )
}

function ProtectedRoute({ children, navigate, pathname }) {
  const { authStatus, isAuthenticated, isLoading, retryAuthentication } = useAuth()

  useEffect(() => {
    if (authStatus === 'unauthenticated') navigate('/signin')
  }, [authStatus, navigate])

  if (authStatus === 'temporarily_unavailable') {
    return (
      <main className="loading-page">
        <p>Authentication is temporarily unavailable.</p>
        <button type="button" className="primary-button" onClick={() => retryAuthentication().catch(() => {})}>Retry authentication</button>
      </main>
    )
  }

  if (isLoading || !isAuthenticated) {
    return <AuthRestoringSurface pathname={pathname} />
  }

  return children
}

function AppRoutes() {
  const {
    pathname,
    hash,
    navigate,
    historyEntryId,
    navigationType,
    registerProblemPane,
    getProblemPanePosition,
  } = usePathname()
  const problemMatch = pathname.match(/^\/problems\/([^/]+)$/)

  if (pathname === '/') return <LandingPage navigate={navigate} />
  if (pathname === '/login') return <RouteRedirect navigate={navigate} to="/signin" />
  if (pathname === '/register') return <RouteRedirect navigate={navigate} to="/signup" />
  if (pathname === '/signin') return <LoginPage navigate={navigate} />
  if (pathname === '/signup') return <RegisterPage navigate={navigate} />
  if (pathname === '/practice') {
    return <ProtectedRoute navigate={navigate} pathname={pathname}><Practice navigate={navigate} /></ProtectedRoute>
  }
  if (pathname === '/dashboard') {
    return <ProtectedRoute navigate={navigate} pathname={pathname}><Dashboard navigate={navigate} /></ProtectedRoute>
  }
  if (problemMatch) {
    return (
      <ProtectedRoute navigate={navigate} pathname={pathname}>
        <ProblemPage
          slug={decodeURIComponent(problemMatch[1])}
          navigate={navigate}
          hash={hash}
          historyEntryId={historyEntryId}
          navigationType={navigationType}
          registerProblemPane={registerProblemPane}
          getProblemPanePosition={getProblemPanePosition}
        />
      </ProtectedRoute>
    )
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
