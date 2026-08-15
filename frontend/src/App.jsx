import { useCallback, useEffect, useState } from 'react'
import './App.css'
import { AuthProvider } from './auth/AuthContext'
import { useAuth } from './auth/useAuth'
import { Dashboard } from './pages/Dashboard'
import { Practice } from './pages/Practice'

function usePathname() {
  const [pathname, setPathname] = useState(window.location.pathname)

  const navigate = useCallback((path) => {
    window.history.pushState({}, '', path)
    setPathname(path)
  }, [])

  useEffect(() => {
    const onPopState = () => setPathname(window.location.pathname)
    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  }, [])

  return { pathname, navigate }
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
        <p className="muted">
          Registration is handled by the existing email verification flow.
        </p>
        <p className="muted">
          The Dashboard module does not change that backend flow.
        </p>
        <LinkButton href="/login" navigate={navigate} className="primary-button">Back to sign in</LinkButton>
      </section>
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
    return <ProtectedRoute navigate={navigate}><Practice /></ProtectedRoute>
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
