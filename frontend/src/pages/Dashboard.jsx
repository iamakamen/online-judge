import { useEffect, useState } from 'react'
import { getDashboard } from '../api/client'
import { useAuth } from '../auth/useAuth'
import { LoomMark } from '../components/PrimarySidebar'

function ProfileIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="profile-icon">
      <circle cx="12" cy="8" r="3.5" />
      <path d="M5 20c.7-3.2 3.2-5 7-5s6.3 1.8 7 5" />
    </svg>
  )
}

function FeatureIcon({ item }) {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="modal-feature-logo">
      {item === 'Learn' && <>
        <path d="m4 8 8-4 8 4-8 4-8-4Z" />
        <path d="M7 10v5c2.7 2.4 7.3 2.4 10 0v-5M20 8v7" />
      </>}
      {item === 'Contest' && <>
        <path d="M8 4h8v4a4 4 0 0 1-8 0V4Z" />
        <path d="M8 6H5v1a3 3 0 0 0 3 3M16 6h3v1a3 3 0 0 1-3 3M12 12v4M8 20h8M9 16h6" />
      </>}
      {item === 'Forum' && <>
        <path d="M5 5h14v10H9l-4 4V5Z" />
        <path d="M8 9h8M8 12h5" />
      </>}
      {item === 'Profile' && <>
        <circle cx="12" cy="8" r="3.5" />
        <path d="M5 20c.7-3.5 3.1-5.5 7-5.5s6.3 2 7 5.5" />
      </>}
    </svg>
  )
}

function WorkProgressIllustration() {
  return (
    <svg viewBox="0 0 180 110" aria-hidden="true" className="work-progress-illustration">
      <defs>
        <clipPath id="roadwork-board">
          <rect x="30" y="35" width="102" height="30" rx="2" />
        </clipPath>
      </defs>
      <path d="M22 88h136" />
      <path d="M30 35h102v30H30z" />
      <g clipPath="url(#roadwork-board)">
        <path d="m24 64 32-34M46 70l32-34M68 70l32-34M90 70l32-34M112 70l32-34" />
      </g>
      <path d="M45 65v23M117 65v23M37 88h16M109 88h16" />
      <path d="m139 88 10-29 10 29M143 77h12M146 68h6" />
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
        <div className="modal-backdrop" role="presentation" onClick={() => setModalItem(null)}>
          <section className="modal" role="dialog" aria-modal="true" aria-labelledby="v2-title" onClick={(event) => event.stopPropagation()}>
            <FeatureIcon item={modalItem} />
            <h2 id="v2-title">{modalItem}</h2>
            <p className="muted">Arriving in V2</p>
            <WorkProgressIllustration />
            <button type="button" className="primary-button" onClick={() => setModalItem(null)}>Close</button>
          </section>
        </div>
      )}
    </div>
  )
}
