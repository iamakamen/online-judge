import { useEffect, useState } from 'react'
import { ApiError, getProblemBySlug } from '../api/client'
import { useAuth } from '../auth/useAuth'
import { CodeEditor } from '../components/CodeEditor'
import { ExecutionWorkspace } from '../components/ExecutionWorkspace'
import { PrimarySidebar } from '../components/PrimarySidebar'

export function ProblemPage({ slug, navigate }) {
  const { requestAuthenticated } = useAuth()
  const [problem, setProblem] = useState(null)
  const [error, setError] = useState(null)
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(false)
  const [isSubmissionsOpen, setIsSubmissionsOpen] = useState(false)
  const [executionView, setExecutionView] = useState(null)
  const [isCodingPaneExpanded, setIsCodingPaneExpanded] = useState(false)
  const [executionMode, setExecutionMode] = useState(null)

  useEffect(() => {
    let active = true

    setProblem(null)
    setError(null)
    setExecutionView(null)
    setExecutionMode(null)
    setIsCodingPaneExpanded(false)

    requestAuthenticated((accessToken) => getProblemBySlug(accessToken, slug))
      .then((response) => {
        if (active) setProblem(response)
      })
      .catch((requestError) => {
        if (!active) return
        setError({
          notFound: requestError instanceof ApiError && requestError.status === 404,
          message: requestError.message,
        })
      })

    return () => {
      active = false
    }
  }, [requestAuthenticated, slug])

  if (error?.notFound) {
    return (
      <main className="error-page">
        <h1>Problem not found</h1>
        <p className="error-message" role="alert">The requested problem does not exist.</p>
      </main>
    )
  }

  if (error) {
    return (
      <main className="error-page">
        <h1>Unable to load Problem</h1>
        <p className="error-message" role="alert">{error.message}</p>
      </main>
    )
  }

  if (!problem) return <main className="loading-page">Loading Problem…</main>

  return (
    <div className={`problem-shell${isSidebarExpanded ? ' sidebar-expanded' : ''}${isCodingPaneExpanded ? ' coding-expanded' : ''}`}>
      <PrimarySidebar
        isExpanded={isSidebarExpanded}
        onExpand={() => setIsSidebarExpanded(true)}
        onCollapse={() => setIsSidebarExpanded(false)}
        navigate={navigate}
      />

      <main className="problem-main">
        <section className="problem-pane" aria-labelledby="problem-title">
          <div className="problem-navigation">
            <button type="button" className="problem-navigation-submissions" onClick={() => setIsSubmissionsOpen(true)}>
              Submissions
            </button>
          </div>

          <header className="problem-header">
            <h1 id="problem-title">{problem.title}</h1>
            <div className="problem-meta">
              <div className="problem-tags" aria-label="Problem tags">
                {problem.tags.map((tag) => (
                  <span key={tag} className="problem-tag">{tag}</span>
                ))}
              </div>
            </div>
          </header>

          <section className="problem-section" aria-labelledby="problem-statement-title">
            <h2 id="problem-statement-title">Description</h2>
            <p>{problem.statement}</p>
          </section>

          <section className="problem-section" aria-labelledby="problem-examples-title">
            <h2 id="problem-examples-title">Examples</h2>
            <div className="problem-examples">
              {problem.test_cases.map((testCase) => (
                <article className="problem-example" key={testCase.id}>
                  <h3>Example {testCase.display_order}</h3>
                  <div className="problem-example-grid">
                    <div>
                      <h4>Input</h4>
                      <pre>{testCase.input}</pre>
                    </div>
                    <div>
                      <h4>Expected output</h4>
                      <pre>{testCase.expected_output}</pre>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </section>

          <section className="problem-section" aria-labelledby="problem-constraints-title">
            <h2 id="problem-constraints-title">Constraints</h2>
            <pre className="problem-constraints">{problem.constraints}</pre>
            <div className="problem-limits">
              <div className="problem-limit">
                <h3>Time Constraints</h3>
                <p>{problem.time_limit_ms} ms</p>
              </div>
              <div className="problem-limit">
                <h3>Memory Constraints</h3>
                <p>{problem.memory_limit_mb} MB</p>
              </div>
            </div>
          </section>
        </section>

        <section className="coding-pane" aria-label="Coding workspace">
          <CodeEditor
            starterCode={problem.starter_code}
            isExpanded={isCodingPaneExpanded}
            onToggleExpansion={() => setIsCodingPaneExpanded((expanded) => !expanded)}
            onCustomInput={() => {
              setExecutionMode('custom')
              setExecutionView('input')
            }}
            onRun={() => {
              setExecutionMode('run')
              setExecutionView('result')
            }}
            onSubmit={() => {
              setExecutionMode('submit')
              setExecutionView('result')
            }}
          />
          {executionMode !== null && (
            <ExecutionWorkspace
              mode={executionMode}
              activeView={executionView}
              runInput={problem.test_cases.find((testCase) => testCase.run_enabled)?.input || ''}
              onViewChange={setExecutionView}
            />
          )}
        </section>
      </main>

      {isSubmissionsOpen && (
        <div className="modal-backdrop" role="presentation" onClick={() => setIsSubmissionsOpen(false)}>
          <section
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="submissions-v2-title"
            onClick={(event) => event.stopPropagation()}
          >
            <p className="eyebrow">Future feature</p>
            <h2 id="submissions-v2-title">Submissions</h2>
            <p className="muted">Coming in V2</p>
            <button type="button" className="primary-button" onClick={() => setIsSubmissionsOpen(false)}>Close</button>
          </section>
        </div>
      )}
    </div>
  )
}
