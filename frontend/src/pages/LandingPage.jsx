import { LoomMark } from '../components/PrimarySidebar'

export function LandingPage({ navigate }) {
  return (
    <main className="landing-page">
      <header className="landing-header">
        <div className="landing-brand" aria-label="encode">
          <LoomMark viewBox="6 6 20 20" />
          <span>encode</span>
        </div>
        <button className="landing-signin" type="button" onClick={() => navigate('/signin')}>Sign in</button>
      </header>

      <section className="landing-hero" aria-labelledby="landing-title">
        <h1 id="landing-title">Your next problem<br />awaits.</h1>
        <button className="signup-submit landing-cta" type="button" onClick={() => navigate('/signup')}>Get started</button>
      </section>
    </main>
  )
}
