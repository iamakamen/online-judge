import { readFileSync } from 'node:fs'
import assert from 'node:assert/strict'
import test from 'node:test'

const appSource = readFileSync(new URL('./App.jsx', import.meta.url), 'utf8')
const landingSource = readFileSync(new URL('./pages/LandingPage.jsx', import.meta.url), 'utf8')
const appStyles = readFileSync(new URL('./App.css', import.meta.url), 'utf8')
const dashboardSource = readFileSync(new URL('./pages/Dashboard.jsx', import.meta.url), 'utf8')
const practiceSource = readFileSync(new URL('./pages/Practice.jsx', import.meta.url), 'utf8')
const problemSource = readFileSync(new URL('./pages/ProblemPage.jsx', import.meta.url), 'utf8')
const registerSource = readFileSync(new URL('./pages/RegisterPage.jsx', import.meta.url), 'utf8')

test('uses the new sign-in and sign-up frontend routes', () => {
  assert.match(appSource, /pathname === '\/signin'/)
  assert.match(appSource, /pathname === '\/signup'/)
  assert.match(appSource, /navigate\('\/signup'\)/)
  assert.match(appSource, /navigate\('\/signin'\)/)
  assert.match(registerSource, /navigate\('\/signin'\)/)
  assert.match(dashboardSource, /navigate\('\/signin'\)/)
  assert.doesNotMatch(appSource, /navigate\('\/(login|register)'\)/)
  assert.doesNotMatch(registerSource, /navigate\('\/login'\)/)
  assert.doesNotMatch(dashboardSource, /navigate\('\/login'\)/)
  assert.doesNotMatch(appSource, /\/sigin\b/)
})

test('renders the dedicated landing page with only intentional navigation', () => {
  assert.match(appSource, /pathname === '\/'\) return <LandingPage navigate=\{navigate\} \/>/)
  assert.match(appSource, /pathname === '\/signin'\) return <LoginPage navigate=\{navigate\} \/>/)
  assert.match(appSource, /pathname === '\/signup'\) return <RegisterPage navigate=\{navigate\} \/>/)
  assert.match(landingSource, /className="landing-signin"[^>]*onClick=\{\(\) => navigate\('\/signin'\)\}/)
  assert.match(landingSource, /className="signup-submit landing-cta"[^>]*onClick=\{\(\) => navigate\('\/signup'\)\}/)
  assert.match(landingSource, /<span>Your next problem<\/span><span>awaits<\/span>/)
  assert.match(appStyles, /\.landing-page[^}]*font-family: 'Space Grotesk'/)
  assert.match(appStyles, /\.landing-hero h1[^}]*font-weight: 600/)
  assert.doesNotMatch(appStyles, /\.landing-hero h1[^}]*font-weight: (?:700|800|900)/)
  assert.match(appStyles, /\.landing-hero[^}]*gap: clamp\(68px/)
  assert.match(appStyles, /\.landing-brand span[^}]*transform: translateY\(-3px\)/)
  assert.match(appStyles, /\.landing-cta[^}]*position: relative[^}]*top: clamp\(24px, 6vh, 64px\)/)
  const brandMarkup = landingSource.slice(landingSource.indexOf('<div className="landing-brand"'), landingSource.indexOf('</div>', landingSource.indexOf('<div className="landing-brand"')))
  assert.doesNotMatch(brandMarkup, /href=|onClick|navigate\(/)
})

test('keeps clean backward-compatible redirects for old auth URLs', () => {
  assert.match(appSource, /pathname === '\/login'.*RouteRedirect/s)
  assert.match(appSource, /to="\/signin"/)
  assert.match(appSource, /pathname === '\/register'.*RouteRedirect/s)
  assert.match(appSource, /to="\/signup"/)
  assert.match(appSource, /navigate\(to, \{ replace: true \}\)/)
})

test('keeps authentication restoration neutral without mounting protected pages', () => {
  assert.match(appSource, /function AuthRestoringSurface\(/)
  assert.match(appSource, /auth-restoring-surface/)
  assert.doesNotMatch(appSource, /Checking authentication/)
  assert.match(appSource, /authStatus === 'temporarily_unavailable'/)
  assert.match(appSource, /authStatus === 'unauthenticated'/)
})

test('keeps Dashboard and Practice shells visible during initial data loading', () => {
  assert.match(dashboardSource, /dashboard-shell.*aria-busy=\{loading\}/s)
  assert.match(dashboardSource, /dashboard-loading-placeholder/)
  assert.match(dashboardSource, /dashboard-loading-value/)
  assert.doesNotMatch(dashboardSource, /Loading Dashboard/)

  assert.match(practiceSource, /practice-header.*aria-busy=\{isLoading\}/s)
  assert.match(practiceSource, /practice-loading-placeholder/)
  assert.match(practiceSource, /practice-catalog-loading/)
  assert.doesNotMatch(practiceSource, /Loading Practice/)
})

test('binds ProblemPage rendering to the current slug during loading and navigation', () => {
  assert.match(problemSource, /loadedProblemSlug/)
  assert.match(problemSource, /const displayedProblem = loadedProblemSlug === slug \? problem : null/)
  assert.match(problemSource, /<ProblemDetails problem=\{displayedProblem\} \/>/)
  assert.match(problemSource, /problem-loading-placeholder/)
  assert.doesNotMatch(problemSource, /Loading Problem/)
})

test('passes the current route hash through to ProblemPage', () => {
  assert.match(appSource, /const \{[\s\S]*?pathname,[\s\S]*?hash,[\s\S]*?\} = usePathname\(\)/)
  assert.match(appSource, /<ProblemPage[\s\S]*hash=\{hash\}/)
})
