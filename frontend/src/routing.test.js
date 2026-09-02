import { readFileSync } from 'node:fs'
import assert from 'node:assert/strict'
import test from 'node:test'

const appSource = readFileSync(new URL('./App.jsx', import.meta.url), 'utf8')
const landingSource = readFileSync(new URL('./pages/LandingPage.jsx', import.meta.url), 'utf8')
const appStyles = readFileSync(new URL('./App.css', import.meta.url), 'utf8')
const dashboardSource = readFileSync(new URL('./pages/Dashboard.jsx', import.meta.url), 'utf8')
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
  assert.match(landingSource, /Your next problem<br \/>awaits\./)
  assert.match(appStyles, /\.landing-page[^}]*font-family: 'Space Grotesk'/)
  assert.match(appStyles, /\.landing-hero h1[^}]*font-weight: 600/)
  assert.doesNotMatch(appStyles, /\.landing-hero h1[^}]*font-weight: (?:700|800|900)/)
  assert.match(appStyles, /\.landing-hero[^}]*gap: clamp\(32px/)
  assert.match(appStyles, /\.landing-brand span[^}]*transform: translateY\(-4\.5px\)/)
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
