import { useState } from 'react'

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

export function PrimarySidebar({ isExpanded, onExpand, onCollapse, navigate }) {
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
