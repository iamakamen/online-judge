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

  useEffect(() => {
    let active = true

    setProblem(null)
    setError(null)

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
        <p className="eyebrow">Problem</p>
        <h1>Problem not found</h1>
        <p className="error-message" role="alert">The requested problem does not exist.</p>
      </main>
    )
  }

  if (error) {
    return (
      <main className="error-page">
        <p className="eyebrow">Problem</p>
        <h1>Unable to load Problem</h1>
        <p className="error-message" role="alert">{error.message}</p>
      </main>
    )
  }

  if (!problem) return <main className="loading-page">Loading Problem…</main>

  return (
    <div className={`problem-shell${isSidebarExpanded ? ' sidebar-expanded' : ''}`}>
      <PrimarySidebar
        isExpanded={isSidebarExpanded}
        onExpand={() => setIsSidebarExpanded(true)}
        onCollapse={() => setIsSidebarExpanded(false)}
        navigate={navigate}
      />

      <main className="problem-main">
        <div className="problem-navigation">
          <button type="button" className="problem-navigation-back" onClick={() => navigate('/practice')}>
            ← Practice
          </button>
          <button type="button" className="problem-navigation-submissions" onClick={() => setIsSubmissionsOpen(true)}>
            Submissions
          </button>
        </div>

        <header className="problem-header">
          <p className="eyebrow">Problem</p>
          <h1 id="problem-title">{problem.title}</h1>
          <div className="problem-meta">
            <span className={`problem-difficulty difficulty-${problem.difficulty.toLowerCase()}`}>
              {problem.difficulty}
            </span>
            <div className="problem-tags" aria-label="Problem tags">
              {problem.tags.map((tag) => (
                <span key={tag} className="problem-tag">{tag}</span>
              ))}
            </div>
          </div>
        </header>

        <section className="problem-section" aria-labelledby="problem-statement-title">
          <h2 id="problem-statement-title">Statement</h2>
          <p>{problem.statement}</p>
        </section>

        <section className="problem-section" aria-labelledby="problem-examples-title">
          <h2 id="problem-examples-title">Examples</h2>
          <div className="problem-examples">
            {problem.test_cases.map((testCase) => (
              <article className="problem-example" key={testCase.id}>
                <h3>{testCase.is_sample ? 'Sample' : 'Example'} {testCase.display_order}</h3>
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
        </section>

        <CodeEditor starterCode={problem.starter_code} />
        <ExecutionWorkspace />
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
