import { useEffect, useMemo, useRef, useState } from 'react'
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

function ProblemRow({ problem, navigate, visibleTags }) {
  return (
    <button
      type="button"
      className="practice-problem-row"
      onClick={() => navigate(`/problem/${problem.slug}`)}
    >
      <span className="practice-problem-title">{problem.title}</span>
      <span
        className={`practice-problem-status${problem.solved ? ' is-solved' : ''}`}
        aria-label={problem.solved ? 'Solved' : 'Not solved'}
      >
        {problem.solved ? '✓' : '○'}
      </span>
      <span className={`practice-problem-difficulty difficulty-${problem.difficulty.toLowerCase()}`}>
        {problem.difficulty}
      </span>
      <span className="practice-problem-tags">
        {visibleTags.map((tag) => <span key={tag} className="practice-problem-tag">{tag}</span>)}
      </span>
    </button>
  )
}

function TopicSection({ topic, problems, actualProblems, isFiltered, isExpanded, onToggle, navigate, topicTagNames }) {
  const solvedCount = actualProblems.filter((problem) => problem.solved).length
  const isComplete = actualProblems.length > 0 && solvedCount === actualProblems.length
  const summary = isFiltered ? `${problems.length}` : `${solvedCount} / ${actualProblems.length}`

  return (
    <section
      className={`practice-topic-section${isComplete ? ' is-complete' : ''}`}
      aria-labelledby={`practice-topic-${topic.id}`}
    >
      <button
        type="button"
        className="practice-topic-heading"
        aria-expanded={isExpanded}
        aria-controls={`practice-topic-body-${topic.id}`}
        onClick={onToggle}
      >
        <h2 id={`practice-topic-${topic.id}`}>{topic.name}</h2>
        <div className="practice-topic-summary">
          <span>{summary}</span>
          <span className={`practice-topic-chevron${isExpanded ? ' is-expanded' : ''}`} aria-hidden="true" />
        </div>
      </button>

      {isExpanded && (
        <div id={`practice-topic-body-${topic.id}`} className="practice-topic-body">
          <div className="practice-problem-list" role="list" aria-label={`${topic.name} problems`}>
            {problems.map((problem) => (
              <ProblemRow
                key={problem.id}
                problem={problem}
                navigate={navigate}
                visibleTags={problem.tags.filter((tag) => !topicTagNames.has(tag.trim().toLowerCase()))}
              />
            ))}
          </div>
        </div>
      )}
    </section>
  )
}

function PracticeFilters({ difficulties, tags, selectedDifficulty, selectedTags, onDifficultyChange, onTagToggle, onClear }) {
  const [isDifficultyMenuOpen, setIsDifficultyMenuOpen] = useState(false)
  const [isTagMenuOpen, setIsTagMenuOpen] = useState(false)
  const [tagSearch, setTagSearch] = useState('')
  const difficultyMenuRef = useRef(null)
  const tagMenuRef = useRef(null)
  const hasFilters = Boolean(selectedDifficulty) || selectedTags.length > 0
  const filteredTags = tags.filter((tag) => tag.toLowerCase().includes(tagSearch.trim().toLowerCase()))

  useEffect(() => {
    if (!isDifficultyMenuOpen && !isTagMenuOpen) return undefined

    const handlePointerDown = (event) => {
      if (isDifficultyMenuOpen && !difficultyMenuRef.current?.contains(event.target)) {
        setIsDifficultyMenuOpen(false)
      }
      if (isTagMenuOpen && !tagMenuRef.current?.contains(event.target)) {
        setIsTagMenuOpen(false)
      }
    }

    document.addEventListener('mousedown', handlePointerDown)
    return () => document.removeEventListener('mousedown', handlePointerDown)
  }, [isDifficultyMenuOpen, isTagMenuOpen])

  const handleDifficultyChange = (difficulty) => {
    onDifficultyChange(difficulty)
    setIsDifficultyMenuOpen(false)
  }

  return (
    <section className="practice-filters" aria-label="Practice filters">
      <div className="practice-filter-group practice-difficulty-filter" ref={difficultyMenuRef}>
        <span className="practice-filter-label">Difficulty</span>
        <button
          type="button"
          className={`practice-filter-trigger${isDifficultyMenuOpen ? ' is-open' : ''}`}
          aria-expanded={isDifficultyMenuOpen}
          aria-haspopup="listbox"
          onClick={() => {
            setIsDifficultyMenuOpen((open) => !open)
            setIsTagMenuOpen(false)
          }}
        >
          <span>{selectedDifficulty}</span>
          <span className={`practice-filter-chevron${isDifficultyMenuOpen ? ' is-open' : ''}`} aria-hidden="true" />
        </button>

        {isDifficultyMenuOpen && (
          <div className="practice-filter-menu" role="listbox" aria-label="Difficulty">
            {difficulties.map((difficulty) => (
              <button
                key={difficulty}
                type="button"
                className={`practice-filter-menu-option${selectedDifficulty === difficulty ? ' is-selected' : ''}`}
                onClick={() => handleDifficultyChange(difficulty)}
              >
                {difficulty}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="practice-filter-group practice-tag-filter" ref={tagMenuRef}>
        <span className="practice-filter-label">Tags</span>
        <button
          type="button"
          className={`practice-tag-trigger${isTagMenuOpen ? ' is-open' : ''}`}
          aria-expanded={isTagMenuOpen}
          aria-haspopup="listbox"
          onClick={() => {
            setIsTagMenuOpen((open) => !open)
            setIsDifficultyMenuOpen(false)
          }}
        >
          <span>{selectedTags.join(', ')}</span>
          <span className={`practice-filter-chevron${isTagMenuOpen ? ' is-open' : ''}`} aria-hidden="true" />
        </button>

        {isTagMenuOpen && (
          <div className="practice-tag-menu">
            <input
              className="practice-tag-search"
              type="search"
              value={tagSearch}
              onChange={(event) => setTagSearch(event.target.value)}
              placeholder="Search tags"
              aria-label="Search tags"
              autoFocus
            />
            <div className="practice-tag-options" role="listbox" aria-multiselectable="true" aria-label="Tags">
              {filteredTags.map((tag) => {
                const checked = selectedTags.includes(tag)
                return (
                  <label key={tag} className={`practice-tag-option${checked ? ' is-selected' : ''}`}>
                    <input
                      type="checkbox"
                      checked={checked}
                      onChange={() => onTagToggle(tag)}
                    />
                    <span>{tag.toLowerCase()}</span>
                  </label>
                )
              })}
              {filteredTags.length === 0 && <span className="practice-tag-no-results">No matching tags</span>}
            </div>
          </div>
        )}
      </div>

      {hasFilters && (
        <button type="button" className="practice-filter-clear" onClick={onClear}>
          Clear filters
        </button>
      )}
    </section>
  )
}

export function Practice({ navigate }) {
  const { requestAuthenticated } = useAuth()
  const [topics, setTopics] = useState([])
  const [problems, setProblems] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedTopics, setExpandedTopics] = useState({})
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(false)
  const [selectedDifficulty, setSelectedDifficulty] = useState('')
  const [selectedTags, setSelectedTags] = useState([])

  useEffect(() => {
    let cancelled = false

    async function loadPracticeCatalog() {
      setIsLoading(true)
      setError('')

      try {
        const [topicResponse, problemResponse] = await Promise.all([
          requestAuthenticated(getTopics),
          requestAuthenticated((accessToken) => getProblems(accessToken)),
        ])

        if (cancelled) return
        const nextProblems = problemResponse.items
        const problemsByTopic = new Map()

        for (const problem of nextProblems) {
          const topicProblems = problemsByTopic.get(problem.topic_id) || []
          topicProblems.push(problem)
          problemsByTopic.set(problem.topic_id, topicProblems)
        }

        setTopics(topicResponse)
        setProblems(nextProblems)
        setExpandedTopics(Object.fromEntries(topicResponse.map((topic) => {
          const topicProblems = problemsByTopic.get(topic.id) || []
          const solvedCount = topicProblems.filter((problem) => problem.solved).length
          const isComplete = topicProblems.length > 0 && solvedCount === topicProblems.length
          return [topic.id, !isComplete]
        })))
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

  const topicTagNames = useMemo(() => (
    new Set(topics.map((topic) => topic.name.trim().toLowerCase()))
  ), [topics])

  const difficulties = useMemo(() => (
    [...new Set(problems.map((problem) => problem.difficulty))]
      .sort((a, b) => a.localeCompare(b))
  ), [problems])

  const tags = useMemo(() => (
    [...new Set(problems.flatMap((problem) => problem.tags))]
      .filter((tag) => !topicTagNames.has(tag.trim().toLowerCase()))
      .sort((a, b) => a.localeCompare(b))
  ), [problems, topicTagNames])

  const isFiltered = Boolean(selectedDifficulty) || selectedTags.length > 0

  const filteredProblems = useMemo(() => problems.filter((problem) => {
    if (selectedDifficulty && problem.difficulty !== selectedDifficulty) return false
    return selectedTags.every((tag) => problem.tags.includes(tag))
  }), [problems, selectedDifficulty, selectedTags])

  const actualProblemsByTopic = useMemo(() => {
    const grouped = new Map(topics.map((topic) => [topic.id, []]))
    for (const problem of problems) {
      if (!grouped.has(problem.topic_id)) grouped.set(problem.topic_id, [])
      grouped.get(problem.topic_id).push(problem)
    }
    return grouped
  }, [topics, problems])

  const filteredProblemsByTopic = useMemo(() => {
    const grouped = new Map(topics.map((topic) => [topic.id, []]))
    for (const problem of filteredProblems) {
      if (!grouped.has(problem.topic_id)) grouped.set(problem.topic_id, [])
      grouped.get(problem.topic_id).push(problem)
    }
    return grouped
  }, [topics, filteredProblems])

  const visibleTopics = useMemo(() => (
    topics.filter((topic) => (filteredProblemsByTopic.get(topic.id) || []).length > 0)
  ), [topics, filteredProblemsByTopic])

  const toggleTag = (tag) => {
    setSelectedTags((current) => (
      current.includes(tag)
        ? current.filter((selectedTag) => selectedTag !== tag)
        : [...current, tag]
    ))
  }

  if (isLoading) return <main className="loading-page">Loading Practice…</main>

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

        <PracticeFilters
          difficulties={difficulties}
          tags={tags}
          selectedDifficulty={selectedDifficulty}
          selectedTags={selectedTags}
          onDifficultyChange={setSelectedDifficulty}
          onTagToggle={toggleTag}
          onClear={() => {
            setSelectedDifficulty('')
            setSelectedTags([])
          }}
        />

        <section className="practice-catalog" aria-label="Practice topics">
          {visibleTopics.map((topic) => (
            <TopicSection
              key={topic.id}
              topic={topic}
              problems={filteredProblemsByTopic.get(topic.id) || []}
              actualProblems={actualProblemsByTopic.get(topic.id) || []}
              isFiltered={isFiltered}
              isExpanded={expandedTopics[topic.id] ?? true}
              onToggle={() => setExpandedTopics((current) => ({
                ...current,
                [topic.id]: !(current[topic.id] ?? true),
              }))}
              navigate={navigate}
              topicTagNames={topicTagNames}
            />
          ))}
          {visibleTopics.length === 0 && (
            <div className="practice-empty-state">
              {isFiltered ? 'No problems match the selected filters.' : 'No problems are available.'}
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
