import { useRef } from 'react'
import './PrimarySidebar.css'

export function LoomMark() {
  return (
    <svg viewBox="0 0 32 32" aria-hidden="true" className="practice-sidebar-logo">
      <path d="M8 7.5c3.7 0 6.5 1.7 8 4.8 1.5-3.1 4.3-4.8 8-4.8" />
      <path d="M8 24.5c3.7 0 6.5-1.7 8-4.8 1.5 3.1 4.3 4.8 8 4.8" />
      <path d="M7.5 8c0 3.7 1.7 6.5 4.8 8-3.1 1.5-4.8 4.3-4.8 8" />
      <path d="M24.5 8c0 3.7-1.7 6.5-4.8 8 3.1 1.5 4.8 4.3 4.8 8" />
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

function LearnIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="practice-sidebar-icon">
      <path d="m4 8 8-4 8 4-8 4-8-4Z" />
      <path d="M7 10v5c2.7 2.4 7.3 2.4 10 0v-5M20 8v7" />
    </svg>
  )
}

function ContestIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="practice-sidebar-icon">
      <path d="M8 4h8v4a4 4 0 0 1-8 0V4Z" />
      <path d="M8 6H5v1a3 3 0 0 0 3 3M16 6h3v1a3 3 0 0 1-3 3M12 12v4M8 20h8M9 16h6" />
    </svg>
  )
}

function ForumIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="practice-sidebar-icon">
      <path d="M5 5h14v10H9l-4 4V5Z" />
      <path d="M8 9h8M8 12h5" />
    </svg>
  )
}

function ProfileIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true" className="practice-sidebar-icon">
      <circle cx="12" cy="8" r="3.5" />
      <path d="M5 20c.7-3.5 3.1-5.5 7-5.5s6.3 2 7 5.5" />
    </svg>
  )
}

function SidebarItem({ label, icon, active = false, onClick }) {
  return (
    <button
      type="button"
      className={`practice-sidebar-item${active ? ' is-active' : ''}`}
      aria-current={active ? 'page' : undefined}
      onClick={onClick}
    >
      {icon}
      <span>{label}</span>
    </button>
  )
}

export function PrimarySidebar({ isExpanded, onExpand, onCollapse, navigate, onV2Click, activeItem = 'Practice' }) {
  const isPointerInside = useRef(false)
  const sidebarRef = useRef(null)

  const handleNavigate = (path) => {
    onCollapse()
    navigate(path)
  }

  const handleMouseEnter = () => {
    isPointerInside.current = true
    onExpand()
  }

  const handleMouseLeave = () => {
    isPointerInside.current = false
    if (!sidebarRef.current?.contains(document.activeElement)) {
      onCollapse()
    }
  }

  return (
    <aside
      ref={sidebarRef}
      className={`practice-sidebar${isExpanded ? ' is-expanded' : ''}`}
      aria-label="Primary navigation"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onFocus={onExpand}
      onBlur={(event) => {
        if (!event.currentTarget.contains(event.relatedTarget) && !isPointerInside.current) onCollapse()
      }}
    >
      <button
        type="button"
        className="practice-sidebar-brand"
        aria-label="Go to Dashboard"
        title="Dashboard"
        onClick={() => handleNavigate('/dashboard')}
      >
        <LoomMark />
        <span className="practice-sidebar-wordmark">encode</span>
      </button>

      <nav className="practice-sidebar-nav">
        <SidebarItem label="Practice" icon={<PracticeIcon />} active={activeItem === 'Practice'} onClick={() => handleNavigate('/practice')} />
        <SidebarItem label="Learn" icon={<LearnIcon />} active={activeItem === 'Learn'} onClick={() => onV2Click?.('Learn')} />
        <SidebarItem label="Contest" icon={<ContestIcon />} active={activeItem === 'Contest'} onClick={() => onV2Click?.('Contest')} />
        <SidebarItem label="Forum" icon={<ForumIcon />} active={activeItem === 'Forum'} onClick={() => onV2Click?.('Forum')} />
      </nav>

      <div className="practice-sidebar-profile">
        <SidebarItem label="Profile" icon={<ProfileIcon />} active={activeItem === 'Profile'} onClick={() => onV2Click?.('Profile')} />
      </div>
    </aside>
  )
}