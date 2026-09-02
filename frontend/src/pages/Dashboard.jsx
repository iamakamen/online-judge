import { useEffect, useState } from 'react'
import { getDashboard } from '../api/client'
import { useAuth } from '../auth/useAuth'
import { LoomMark } from '../components/PrimarySidebar'
import { V2PlaceholderModal } from '../components/V2PlaceholderModal'

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
    navigate('/signin')
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
    <div className="app-shell dashboard-shell">
      <header className="topbar dashboard-topbar">
        <div className="dashboard-brand">
          <LoomMark />
          <span>encode</span>
        </div>
        <nav aria-label="Account navigation" className="account-nav">
          <button type="button" className="icon-button" aria-label="Profile" title="Profile" onClick={() => setModalItem('Profile')}>
            <ProfileIcon />
          </button>
          <button type="button" className="text-button" onClick={handleLogout}>Sign out</button>
        </nav>
      </header>
      <main className="dashboard-page">
        <section className="dashboard-intro">
          <h1>Welcome, {data.first_name.toLowerCase()}</h1>
          <p className="muted">Keep building your problem-solving momentum.</p>
        </section>

        <section className="stat-grid" aria-label="Your progress">
          <article className="stat-card"><span>Solved</span><strong>{data.solved_count}</strong></article>
          <article className="stat-card"><span>Global Rank</span><strong>{data.global_rank}</strong></article>
          <article className="stat-card"><span>Day Streak</span><strong>{data.day_streak}</strong></article>
        </section>

        <section className="dashboard-actions" aria-label="Learning areas">
          <a
            href="/practice"
            className="action-card primary-action"
            onClick={(event) => {
              if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
              event.preventDefault()
              navigate('/practice')
            }}
          >
            <span>Practice</span><small>Explore problems</small>
          </a>
          {['Learn', 'Contest', 'Forum'].map((item) => (
            <button type="button" className="action-card" key={item} onClick={() => setModalItem(item)}>
              <span>{item}</span><small>Arriving in V2</small>
            </button>
          ))}
        </section>
      </main>
      {modalItem && (
        <V2PlaceholderModal feature={modalItem} onClose={() => setModalItem(null)} />
      )}
    </div>
  )
}
