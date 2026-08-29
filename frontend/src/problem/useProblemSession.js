import { useCallback, useEffect, useRef, useState } from 'react'
import {
  createProblemSession,
  PROBLEM_SESSION_TTL_MS,
  readProblemSession,
  writeProblemSession,
} from './problemSessionStorage'

const EDITOR_WRITE_DELAY_MS = 250

export function useProblemSession({ userId, problemSlug, starterCode, enabled }) {
  const key = enabled && userId !== null && userId !== undefined
    ? `${userId}:${problemSlug}`
    : null
  const [initialSession, setInitialSession] = useState(null)
  const [hydrated, setHydrated] = useState(false)
  const sessionRef = useRef(null)
  const keyRef = useRef(key)
  const timerRef = useRef(null)

  useEffect(() => {
    keyRef.current = key
    if (timerRef.current !== null) window.clearTimeout(timerRef.current)
    timerRef.current = null
    setInitialSession(null)
    setHydrated(false)
    sessionRef.current = null

    if (!key) return undefined

    const cached = readProblemSession(userId, problemSlug)
    const nextSession = cached || createProblemSession(userId, problemSlug, starterCode)
    sessionRef.current = nextSession
    setInitialSession(nextSession)
    setHydrated(true)

    return () => {
      if (timerRef.current !== null) window.clearTimeout(timerRef.current)
      timerRef.current = null
    }
  }, [key, problemSlug, starterCode, userId])

  const persist = useCallback((patch, immediate = false) => {
    const expectedKey = key
    if (!expectedKey || !sessionRef.current || !hydrated) return
    const now = Date.now()
    const nextSession = {
      ...sessionRef.current,
      ...patch,
      updatedAt: now,
      expiresAt: now + PROBLEM_SESSION_TTL_MS,
    }
    sessionRef.current = nextSession

    const write = () => {
      timerRef.current = null
      if (keyRef.current !== expectedKey || !sessionRef.current || sessionRef.current !== nextSession) return
      writeProblemSession(nextSession)
    }

    if (immediate) {
      if (timerRef.current !== null) window.clearTimeout(timerRef.current)
      write()
      return
    }
    if (timerRef.current !== null) window.clearTimeout(timerRef.current)
    timerRef.current = window.setTimeout(write, EDITOR_WRITE_DELAY_MS)
  }, [hydrated, key])

  const onEditorChange = useCallback(({ selectedLanguage, editorContents }) => {
    persist({ selectedLanguage, editorContents })
  }, [persist])

  useEffect(() => () => {
    if (timerRef.current !== null) window.clearTimeout(timerRef.current)
  }, [])

  return { initialSession, hydrated, onEditorChange, persist }
}
