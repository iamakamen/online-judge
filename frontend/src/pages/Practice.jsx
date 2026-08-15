import { useEffect, useState } from 'react'
import { getProblems, getTopics } from '../api/client'
import { useAuth } from '../auth/useAuth'

export function Practice() {
  const { requestAuthenticated } = useAuth()
  const [topics, setTopics] = useState([])
  const [problems, setProblems] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

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

        setTopics(topicResponse)
        setProblems(problemResponse.items)
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
      <main className="placeholder-page">
        <p className="eyebrow">Practice</p>
        <h1>Unable to load Practice</h1>
        <p className="error-message" role="alert">{error}</p>
      </main>
    )
  }

  return (
    <main className="placeholder-page">
      <p className="eyebrow">Practice</p>
      <h1>Practice</h1>
      <p className="muted">Practice catalog data is connected.</p>
      <p className="muted">Topics loaded: {topics.length}</p>
      <p className="muted">Problems loaded: {problems.length}</p>
    </main>
  )
}
