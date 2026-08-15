import { useEffect, useState } from 'react'
import { getProblems, getTopics } from '../api/client'
import { useAuth } from '../auth/useAuth'

function DashboardIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="practice-sidebar-icon">
      <path d="M4 10.5 12 4l8 6.5" />
      <path d="M6.5 9.5V20h11V9.5M9.5 20v-6h5v6" />
    </svg>
  )
}

function PracticeIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="practice-sidebar-icon">
      <rect x="4.5" y="4.5" width="15" height="15" rx="2" />
      <path d="M8 9h8M8 13h5M8 17h3" />
    </svg>
  )
}

function SidebarItem({ label, icon, active = false, disabled = false, onClick }) {
  return (
    <button
      type="button"
      className={`practice-sidebar-item${active ? ' is-active' : ''}`}
      disabled={disabled}
      aria-current={active ? 'page' : undefined}
      aria-disabled={disabled ? 'true' : undefined}
      onClick={onClick}
    >
      {icon}
      <span>{label}</span>
    </button>
  )
}

function PracticeSidebar({ isExpanded, onExpand, onCollapse, navigate }) {
  const [hoverSuppressed, setHoverSuppressed] = useState(false)

  const handleNavigate = (path) => {
    onCollapse()
    navigate(path)
  }

  const handleMouseEnter = () => {
    if (!hoverSuppressed) onExpand()
  }

  const handleMouseLeave = () => {
    setHoverSuppressed(false)
    onCollapse()
  }

  const handleCollapse = () => {
    setHoverSuppressed(true)
    onCollapse()
  }

  return (
    <aside
      className={`practice-sidebar${isExpanded ? ' is-expanded' : ''}`}
      aria-label="Primary navigation"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onFocus={() => {
        if (!hoverSuppressed) onExpand()
      }}
    >
      <button
        type="button"
        className="practice-sidebar-brand"
        aria-label="Go to Dashboard"
        title="Dashboard"
        onClick={() => handleNavigate('/dashboard')}
      >
        OJ
      </button>

      <nav className="practice-sidebar-nav">
        <SidebarItem label="Dashboard" icon={<DashboardIcon />} onClick={() => handleNavigate('/dashboard')} />
        <SidebarItem label="Practice" icon={<PracticeIcon />} active onClick={handleCollapse} />
      </nav>

      <div className="practice-sidebar-future" aria-label="Future navigation">
        <SidebarItem label="Learn" icon={<span className="practice-sidebar-placeholder">L</span>} disabled />
        <SidebarItem label="Contest" icon={<span className="practice-sidebar-placeholder">C</span>} disabled />
        <SidebarItem label="Forum" icon={<span className="practice-sidebar-placeholder">F</span>} disabled />
      </div>

      <div className="practice-sidebar-profile">
        <SidebarItem label="Profile" icon={<span className="practice-sidebar-placeholder">P</span>} disabled />
      </div>
    </aside>
  )
}

function TopicSection({ topic }) {
  return (
    <section className="practice-topic-section" aria-labelledby={`practice-topic-${topic.id}`}>
      <div className="practice-topic-heading">
        <div>
          <p className="practice-section-kicker">Topic</p>
          <h2 id={`practice-topic-${topic.id}`}>{topic.name}</h2>
        </div>
        <span className="practice-topic-chevron" aria-hidden="true">⌄</span>
      </div>
      <div className="practice-topic-body">
        <span>Problem catalog</span>
      </div>
    </section>
  )
}

export function Practice({ navigate }) {
  const { requestAuthenticated } = useAuth()
  const [topics, setTopics] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function loadPracticeCatalog() {
      setIsLoading(true)
      setError('')

      try {
        const [topicResponse] = await Promise.all([
          requestAuthenticated(getTopics),
          requestAuthenticated((accessToken) => getProblems(accessToken)),
        ])

        if (cancelled) return
        setTopics(topicResponse)
      } catch (requestError) {
        if (cancelled) return
        setError(requestError.message)
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    loadPracticeCatalog()

    return () => {
      cancelled = true
    }
  }, [requestAuthenticated])

  if (isLoading) {
    return <main className="loading-page">Loading Practice…</main>
  }

  if (error) {
    return (
      <main className="error-page">
        <p className="eyebrow">Practice</p>
        <h1>Unable to load Practice</h1>
        <p className="error-message" role="alert">{error}</p>
      </main>
    )
  }

  return (
    <div className={`practice-shell${isSidebarExpanded ? ' sidebar-expanded' : ''}`}>
      <PracticeSidebar
        isExpanded={isSidebarExpanded}
        onExpand={() => setIsSidebarExpanded(true)}
        onCollapse={() => setIsSidebarExpanded(false)}
        navigate={navigate}
      />
      <main className="practice-main">
        <header className="practice-header">
          <div>
            <p className="eyebrow">Practice</p>
            <h1>Problem Solving</h1>
            <p className="muted">Build consistency by working through problems topic by topic.</p>
          </div>
        </header>

        <section className="practice-catalog" aria-label="Practice topics">
          {topics.map((topic) => <TopicSection key={topic.id} topic={topic} />)}
        </section>
      </main>
    </div>
  )
}
