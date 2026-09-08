import { useEffect, useMemo, useRef, useState } from 'react'
import './PracticeFilters.css'
import { getProblems, getTopics } from '../api/client'
import { useAuth } from '../auth/useAuth'
import { PrimarySidebar } from '../components/PrimarySidebar'
import {
  DIFFICULTY_OPTIONS,
  formatDifficultyLabel,
  formatTagLabel,
  getPracticeAnalytics,
} from './practiceFilterPresentation'

function ProblemRow({ problem, navigate }) {
  return (
    <a
      href={`/problems/${encodeURIComponent(problem.slug)}`}
      className="practice-problem-row"
      onClick={(event) => {
        if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
        event.preventDefault()
        navigate(`/problems/${problem.slug}`)
      }}
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
        {problem.tags.map((tag) => <span key={tag} className="practice-problem-tag">{tag}</span>)}
      </span>
    </a>
  )
}

function TopicSection({ topic, problems, actualProblems, isFiltered, isExpanded, onToggle, navigate }) {
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
              />
            ))}
          </div>
        </div>
      )}
    </section>
  )
}

function PracticeFilters({ tags, selectedDifficulty, selectedTags, onDifficultyChange, onTagToggle, onClear }) {
  const [isDifficultyMenuOpen, setIsDifficultyMenuOpen] = useState(false)
  const [isTagMenuOpen, setIsTagMenuOpen] = useState(false)
  const [tagSearch, setTagSearch] = useState('')
  const difficultyMenuRef = useRef(null)
  const tagMenuRef = useRef(null)
  const hasFilters = Boolean(selectedDifficulty) || selectedTags.length > 0
  const filteredTags = tags.filter((tag) => tag.toLowerCase().includes(tagSearch.trim().toLowerCase()))
  const visibleSelectedTags = selectedTags.slice(0, 3)
  const hiddenSelectedTagCount = Math.max(selectedTags.length - visibleSelectedTags.length, 0)

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
          <span>{formatDifficultyLabel(selectedDifficulty)}</span>
          <span className={`practice-filter-chevron${isDifficultyMenuOpen ? ' is-open' : ''}`} aria-hidden="true" />
        </button>

        {isDifficultyMenuOpen && (
          <div className="practice-filter-menu practice-difficulty-menu" role="listbox" aria-label="Difficulty">
            {DIFFICULTY_OPTIONS.map((difficulty) => (
              <button
                key={difficulty}
                type="button"
                className={`practice-difficulty-option${selectedDifficulty === difficulty ? ' is-selected' : ''}`}
                role="option"
                aria-selected={selectedDifficulty === difficulty}
                onClick={() => handleDifficultyChange(difficulty)}
              >
                {formatDifficultyLabel(difficulty)}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="practice-filter-group practice-tag-filter" ref={tagMenuRef}>
        <span className="practice-filter-label">Tags</span>
        <div className={`practice-tag-control${isTagMenuOpen ? ' is-open' : ''}`}>
          <div className="practice-tag-pills" aria-label="Selected tags">
            {visibleSelectedTags.map((tag) => (
              <span key={tag} className="practice-selected-tag">
                <span>{formatTagLabel(tag)}</span>
                <button
                  type="button"
                  className="practice-selected-tag-remove"
                  aria-label={`Remove ${tag} filter`}
                  onClick={() => onTagToggle(tag)}
                >
                  ×
                </button>
              </span>
            ))}
            {hiddenSelectedTagCount > 0 && (
              <span className="practice-selected-tag-more">+{hiddenSelectedTagCount} more</span>
            )}
          </div>
          <button
            type="button"
            className="practice-add-tag"
            aria-expanded={isTagMenuOpen}
            aria-haspopup="listbox"
            onClick={() => {
              setIsTagMenuOpen((open) => !open)
              setIsDifficultyMenuOpen(false)
            }}
          >
            + Add tag
          </button>
          {selectedTags.length === 0 && (
            <button
              type="button"
              className="practice-tag-open-area"
              aria-label="Open tag filters"
              aria-expanded={isTagMenuOpen}
              onClick={() => {
                setIsTagMenuOpen((open) => !open)
                setIsDifficultyMenuOpen(false)
              }}
            />
          )}
        </div>

        {isTagMenuOpen && (
          <div className="practice-tag-menu">
            <input
              className="practice-tag-search"
              type="search"
              value={tagSearch}
              onChange={(event) => setTagSearch(event.target.value)}
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
                    <span>{formatTagLabel(tag)}</span>
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

  const tags = useMemo(() => (
    [...new Set(problems.flatMap((problem) => problem.tags))]
      .sort((a, b) => a.localeCompare(b))
  ), [problems])

  const analytics = useMemo(() => getPracticeAnalytics(problems), [problems])

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

  if (error) {
    return (
      <main className="error-page">
        <h1>Unable to load Practice</h1>
        <p className="error-message" role="alert">{error}</p>
      </main>
    )
  }

  return (
    <div className={`practice-shell${isSidebarExpanded ? ' sidebar-expanded' : ''}`}>
      <PrimarySidebar
        isExpanded={isSidebarExpanded}
        onExpand={() => setIsSidebarExpanded(true)}
        onCollapse={() => setIsSidebarExpanded(false)}
        navigate={navigate}
      />
      <main className="practice-main">
        <header className="practice-header" aria-busy={isLoading}>
          <div className="practice-hero-content">
            <h1>Practice</h1>
            <p className="muted">Build consistency by working through problems topic by topic.</p>
          </div>
          <div className="practice-analytics-card" aria-label="Practice progress">
            {isLoading ? (
              <div className="practice-loading-placeholder" role="status">Loading progress…</div>
            ) : (
              <>
                <div className="practice-analytics-summary">
                  <p><span>Completed</span><strong>{analytics.completed}</strong></p>
                  <p><span>Remaining</span><strong>{analytics.remaining}</strong></p>
                </div>
                <div
                  className="practice-analytics-progress"
                  role="img"
                  aria-label={`${analytics.percentage}% solved`}
                  style={{ '--practice-progress-offset': 194.78 - ((194.78 * analytics.percentage) / 100) }}
                >
                  <svg viewBox="0 0 76 76" aria-hidden="true">
                    <circle className="practice-analytics-track" cx="38" cy="38" r="31" />
                    <circle className="practice-analytics-value" cx="38" cy="38" r="31" />
                  </svg>
                  <div className="practice-analytics-progress-label">
                    <strong>{analytics.percentage}%</strong>
                    <span>Solved</span>
                  </div>
                </div>
              </>
            )}
          </div>
        </header>

        <PracticeFilters
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

        {isLoading ? (
          <section className="practice-catalog practice-catalog-loading" aria-label="Practice topics" aria-busy="true">
            <p role="status">Loading problem catalog…</p>
          </section>
        ) : (
          <section className="practice-catalog" aria-label="Practice topics">
            {visibleTopics.map((topic) => (
              <TopicSection
                key={topic.id}
                topic={topic}
                problems={filteredProblemsByTopic.get(topic.id) || []}
                actualProblems={actualProblemsByTopic.get(topic.id) || []}
                isFiltered={isFiltered}
                isExpanded={expandedTopics[topic.id] ?? true}
                onToggle={() => setExpandedTopics((current) => ({ ...current, [topic.id]: !current[topic.id] }))}
                navigate={navigate}
              />
            ))}
          </section>
        )}
      </main>
    </div>
  )
}
