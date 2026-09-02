import { useCallback, useEffect, useState } from 'react'
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

function usePathname() {
  const [pathname, setPathname] = useState(window.location.pathname)

  const navigate = useCallback((path, { replace = false } = {}) => {
    window.history[replace ? 'replaceState' : 'pushState']({}, '', path)
    setPathname(path)
  }, [])

  useEffect(() => {
    const onPopState = () => setPathname(window.location.pathname)
    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  }, [])

  return { pathname, navigate }
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

function ProtectedRoute({ children, navigate }) {
  const { isAuthenticated, isLoading } = useAuth()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) navigate('/signin')
  }, [isAuthenticated, isLoading, navigate])

  if (isLoading || !isAuthenticated) {
    return <main className="loading-page">Checking authentication…</main>
  }

  return children
}

function AppRoutes() {
  const { pathname, navigate } = usePathname()
  const problemMatch = pathname.match(/^\/problems\/([^/]+)$/)

  if (pathname === '/') return <LandingPage navigate={navigate} />
  if (pathname === '/login') return <RouteRedirect navigate={navigate} to="/signin" />
  if (pathname === '/register') return <RouteRedirect navigate={navigate} to="/signup" />
  if (pathname === '/signin') return <LoginPage navigate={navigate} />
  if (pathname === '/signup') return <RegisterPage navigate={navigate} />
  if (pathname === '/practice') {
    return <ProtectedRoute navigate={navigate}><Practice navigate={navigate} /></ProtectedRoute>
  }
  if (pathname === '/dashboard') {
    return <ProtectedRoute navigate={navigate}><Dashboard navigate={navigate} /></ProtectedRoute>
  }
  if (problemMatch) {
    return (
      <ProtectedRoute navigate={navigate}>
        <ProblemPage
          slug={decodeURIComponent(problemMatch[1])}
          navigate={navigate}
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
