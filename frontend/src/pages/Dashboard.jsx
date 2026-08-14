import { useEffect, useState } from 'react'
import { getDashboard } from '../api/client'
import { useAuth } from '../auth/useAuth'

function ProfileIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="profile-icon">
      <circle cx="12" cy="8" r="3.5" />
      <path d="M5 20c.7-3.2 3.2-5 7-5s6.3 1.8 7 5" />
    </svg>
  )
}

export function Dashboard({ navigate }) {
  const { requestAuthenticated, logout } = useAuth()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [modalItem, setModalItem] = useState(null)

  useEffect(() => {
    let active = true
    requestAuthenticated(getDashboard)
      .then((response) => {
        if (active) setData(response)
      })
      .catch((requestError) => {
        if (active) setError(requestError.message)
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => { active = false }
  }, [requestAuthenticated])

  async function handleLogout() {
    await logout()
    navigate('/login')
  }

  if (loading) return <main className="loading-page">Loading Dashboard…</main>
  if (error) {
    return (
      <main className="error-page">
        <p className="eyebrow">Dashboard</p>
        <h1>Dashboard unavailable</h1>
        <p className="error-message" role="alert">{error}</p>
        <button type="button" className="primary-button" onClick={() => window.location.reload()}>
          Try again
        </button>
      </main>
    )
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <button type="button" className="brand" onClick={() => navigate('/dashboard')}>OJ</button>
        <nav aria-label="Account navigation" className="account-nav">
          <button type="button" className="icon-button" aria-label="Profile" title="Profile" onClick={() => setModalItem('Profile')}>
            <ProfileIcon />
          </button>
          <button type="button" className="text-button" onClick={handleLogout}>Sign out</button>
        </nav>
      </header>
      <main className="dashboard-page">
        <section className="dashboard-intro">
          <p className="eyebrow">Dashboard</p>
          <h1>Welcome, {data.first_name}</h1>
          <p className="muted">Keep building your problem-solving momentum.</p>
        </section>

        <section className="stat-grid" aria-label="Your progress">
          <article className="stat-card"><span>Solved</span><strong>{data.solved_count}</strong></article>
          <article className="stat-card"><span>Global Rank</span><strong>{data.global_rank}</strong></article>
          <article className="stat-card"><span>Day Streak</span><strong>{data.day_streak}</strong></article>
        </section>

        <section className="dashboard-actions" aria-label="Learning areas">
          <button type="button" className="action-card primary-action" onClick={() => navigate('/practice')}>
            <span>Practice</span><small>Explore problems</small>
          </button>
          {['Learn', 'Contest', 'Forum'].map((item) => (
            <button type="button" className="action-card" key={item} onClick={() => setModalItem(item)}>
              <span>{item}</span><small>Coming in V2</small>
            </button>
          ))}
        </section>
      </main>
      {modalItem && (
        <div className="modal-backdrop" role="presentation" onClick={() => setModalItem(null)}>
          <section className="modal" role="dialog" aria-modal="true" aria-labelledby="v2-title" onClick={(event) => event.stopPropagation()}>
            <p className="eyebrow">Future feature</p>
            <h2 id="v2-title">{modalItem}</h2>
            <p className="muted">Coming in V2</p>
            <button type="button" className="primary-button" onClick={() => setModalItem(null)}>Close</button>
          </section>
        </div>
      )}
    </div>
  )
}
