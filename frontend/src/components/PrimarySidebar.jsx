import { useEffect, useRef, useState } from 'react'
import { flushSync } from 'react-dom'
import './PrimarySidebar.css'

export function LoomMark({ viewBox = '0 0 32 32' }) {
  return (
    <svg viewBox={viewBox} aria-hidden="true" className="practice-sidebar-logo">
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

function SidebarItem({ label, icon, active = false, onClick, href, onContextMenu }) {
  const className = `practice-sidebar-item${active ? ' is-active' : ''}`

  if (href) {
    return (
      <a
        href={href}
        className={className}
        aria-current={active ? 'page' : undefined}
        onContextMenu={onContextMenu}
        onClick={(event) => {
          if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
          event.preventDefault()
          onClick?.()
        }}
      >
        {icon}
        <span>{label}</span>
      </a>
    )
  }

  return (
    <button
      type="button"
      className={className}
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
  const contextMenuRef = useRef(null)
  const [contextMenu, setContextMenu] = useState(null)

  useEffect(() => {
    if (!contextMenu || !contextMenuRef.current) return undefined
    const menuElement = contextMenuRef.current
    const handleOutsideClick = (event) => {
      if (!menuElement.contains(event.target)) setContextMenu(null)
    }
    const bounds = menuElement.getBoundingClientRect()
    const left = Math.max(0, Math.min(contextMenu.left, window.innerWidth - bounds.width))
    const top = Math.max(0, Math.min(contextMenu.top, window.innerHeight - bounds.height))
    if (left !== contextMenu.left || top !== contextMenu.top) {
      setContextMenu((current) => current ? { ...current, left, top } : current)
    }
    menuElement.querySelector('[role="menuitem"]')?.focus()
    window.addEventListener('click', handleOutsideClick)
    return () => window.removeEventListener('click', handleOutsideClick)
  }, [contextMenu])

  const handleNavigate = (path) => {
    onCollapse()
    navigate(path)
  }

  const handleContextMenu = (event, path) => {
    event.preventDefault()
    setContextMenu({ path, left: event.clientX, top: event.clientY })
  }

  const contextMenuItems = [
    { label: 'Open in New Tab', action: 'tab' },
    { label: 'Copy Link', action: 'copy' },
  ]

  const closeContextMenu = () => setContextMenu(null)

  const handleContextMenuAction = async (action) => {
    if (!contextMenu) return
    const destination = new URL(contextMenu.path, window.location.href).href
    flushSync(() => {
      closeContextMenu()
      onCollapse()
    })
    if (action === 'copy') {
      try {
        await navigator.clipboard.writeText(destination)
      } catch {
        // Clipboard access may be unavailable; leave unrelated state unchanged.
      }
      return
    }
    window.open(destination, '_blank', 'noopener,noreferrer')
  }

  const handleContextMenuKeyDown = (event) => {
    const items = contextMenuRef.current?.querySelectorAll('[role="menuitem"]')
    const currentIndex = [...(items || [])].indexOf(document.activeElement)
    if (event.key === 'Escape') {
      event.preventDefault()
      closeContextMenu()
    } else if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault()
      const nextIndex = event.key === 'ArrowDown'
        ? (currentIndex + 1) % contextMenuItems.length
        : (currentIndex - 1 + contextMenuItems.length) % contextMenuItems.length
      items?.[nextIndex]?.focus()
    } else if (event.key === 'Enter' && currentIndex >= 0) {
      event.preventDefault()
      handleContextMenuAction(contextMenuItems[currentIndex].action)
    }
  }

  const handleMouseEnter = () => {
    isPointerInside.current = true
    onExpand()
  }

  const handleMouseLeave = () => {
    isPointerInside.current = false
    if (contextMenu) return
    onCollapse()
  }

  return (
    <aside
      className={`practice-sidebar${isExpanded ? ' is-expanded' : ''}`}
      aria-label="Primary navigation"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onFocus={onExpand}
    >
      <a
        href="/dashboard"
        className="practice-sidebar-brand"
        aria-label="Go to Dashboard"
        title="Dashboard"
        onClick={(event) => {
          if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
          event.preventDefault()
          handleNavigate('/dashboard')
        }}
        onContextMenu={(event) => handleContextMenu(event, '/dashboard')}
      >
        <LoomMark viewBox="6 6 20 20" />
        <span className="practice-sidebar-wordmark">encode</span>
      </a>

      <nav className="practice-sidebar-nav">
        <SidebarItem label="Practice" icon={<PracticeIcon />} active={activeItem === 'Practice'} href="/practice" onClick={() => handleNavigate('/practice')} onContextMenu={(event) => handleContextMenu(event, '/practice')} />
        <SidebarItem label="Learn" icon={<LearnIcon />} active={activeItem === 'Learn'} onClick={() => onV2Click?.('Learn')} />
        <SidebarItem label="Contest" icon={<ContestIcon />} active={activeItem === 'Contest'} onClick={() => onV2Click?.('Contest')} />
        <SidebarItem label="Forum" icon={<ForumIcon />} active={activeItem === 'Forum'} onClick={() => onV2Click?.('Forum')} />
      </nav>

      <div className="practice-sidebar-profile">
        <SidebarItem label="Profile" icon={<ProfileIcon />} active={activeItem === 'Profile'} onClick={() => onV2Click?.('Profile')} />
      </div>
      {contextMenu && (
        <div
          ref={contextMenuRef}
          className="practice-sidebar-context-menu"
          role="menu"
          aria-label={`${contextMenu.path === '/dashboard' ? 'Dashboard' : 'Practice'} actions`}
          style={{ left: contextMenu.left, top: contextMenu.top }}
          tabIndex={-1}
          onBlur={(event) => {
            if (!event.currentTarget.contains(event.relatedTarget)) closeContextMenu()
          }}
          onKeyDown={handleContextMenuKeyDown}
        >
          {contextMenuItems.map((item) => (
            <button key={item.action} type="button" role="menuitem" onClick={() => handleContextMenuAction(item.action)}>
              {item.label}
            </button>
          ))}
        </div>
      )}
    </aside>
  )
}
