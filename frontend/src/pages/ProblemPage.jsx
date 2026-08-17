import { useEffect, useState } from 'react'
import { ApiError, getProblemBySlug } from '../api/client'
import { useAuth } from '../auth/useAuth'
import { CodeEditor } from '../components/CodeEditor'
import { ExecutionWorkspace } from '../components/ExecutionWorkspace'

export function ProblemPage({ slug }) {
  const { requestAuthenticated } = useAuth()
  const [problem, setProblem] = useState(null)
  const [error, setError] = useState(null)

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
    <main className="problem-page" aria-labelledby="problem-title">
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
  )
}
