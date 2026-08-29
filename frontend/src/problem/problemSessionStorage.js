export const PROBLEM_SESSION_TTL_MS = 30 * 60 * 1000
export const PROBLEM_SESSION_SCHEMA_VERSION = 1
export const PROBLEM_SESSION_KEY_PREFIX = 'oj:problem-session:'

const TERMINAL_RUN_STATUSES = new Set([
  'passed',
  'failed',
  'compile_error',
  'runtime_error',
  'time_limit_exceeded',
  'memory_limit_exceeded',
  'output_limit_exceeded',
  'system_error',
])

function isObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

function isNullableNumber(value) {
  return value === null || typeof value === 'number'
}

function validRunResult(result) {
  return isObject(result)
    && TERMINAL_RUN_STATUSES.has(result.status)
    && (result.language === 'python' || result.language === 'cpp')
    && result.mode === 'run_tests'
    && Array.isArray(result.results)
    && result.results.every((testResult) => (
      isObject(testResult)
      && typeof testResult.status === 'string'
      && typeof testResult.input === 'string'
      && (testResult.expected_output === null || typeof testResult.expected_output === 'string')
      && typeof testResult.stdout === 'string'
      && typeof testResult.stderr === 'string'
      && isNullableNumber(testResult.execution_time_ms)
    ))
}

function validSubmitResult(result) {
  return isObject(result)
    && (result.status === 'completed' || result.status === 'failed')
    && (result.verdict === null || typeof result.verdict === 'string')
    && Array.isArray(result.results)
    && result.results.every((testResult) => (
      isObject(testResult)
      && typeof testResult.display_order === 'number'
      && typeof testResult.status === 'string'
      && isNullableNumber(testResult.execution_time_ms)
      && isNullableNumber(testResult.memory_used_mb)
    ))
}

function validStoredExecution(value, validator) {
  return value === null || (
    isObject(value)
    && typeof value.executionId === 'string'
    && (value.language === 'python' || value.language === 'cpp')
    && validator(value.result)
  )
}

function validAiHelp(value) {
  return value === null || (
    isObject(value)
    && typeof value.executionId === 'string'
    && isObject(value.response)
    && typeof value.response.summary === 'string'
    && Array.isArray(value.response.tips)
    && value.response.tips.length > 0
    && value.response.tips.every((tip) => typeof tip === 'string')
  )
}

export function problemSessionKey(userId, problemSlug) {
  return `${PROBLEM_SESSION_KEY_PREFIX}${userId}:${problemSlug}`
}

export function createProblemSession(userId, problemSlug, starterCode = {}) {
  const now = Date.now()
  return {
    schemaVersion: PROBLEM_SESSION_SCHEMA_VERSION,
    userId,
    problemSlug,
    selectedLanguage: 'python',
    editorContents: {
      python: typeof starterCode.python === 'string' ? starterCode.python : '',
      cpp: typeof starterCode.cpp === 'string' ? starterCode.cpp : '',
    },
    lastExecutionMode: null,
    lastExecutionView: null,
    latestRunResult: null,
    latestSubmitResult: null,
    aiHelp: null,
    updatedAt: now,
    expiresAt: now + PROBLEM_SESSION_TTL_MS,
  }
}

function validSession(value, userId, problemSlug, now) {
  return isObject(value)
    && value.schemaVersion === PROBLEM_SESSION_SCHEMA_VERSION
    && value.userId === userId
    && value.problemSlug === problemSlug
    && (value.selectedLanguage === 'python' || value.selectedLanguage === 'cpp')
    && isObject(value.editorContents)
    && typeof value.editorContents.python === 'string'
    && typeof value.editorContents.cpp === 'string'
    && (value.lastExecutionMode === null || value.lastExecutionMode === 'run' || value.lastExecutionMode === 'submit')
    && (value.lastExecutionView === null || typeof value.lastExecutionView === 'string')
    && validStoredExecution(value.latestRunResult, validRunResult)
    && validStoredExecution(value.latestSubmitResult, validSubmitResult)
    && validAiHelp(value.aiHelp)
    && Number.isFinite(value.updatedAt)
    && Number.isFinite(value.expiresAt)
    && value.expiresAt > now
}

function safeRemove(storage, key) {
  try { storage.removeItem(key) } catch { /* Storage is optional. */ }
}

function defaultStorage() {
  try { return window.localStorage } catch { return null }
}

export function readProblemSession(userId, problemSlug, storage, now = Date.now()) {
  const store = storage || defaultStorage()
  if (!store) return null
  const key = problemSessionKey(userId, problemSlug)
  let raw
  try { raw = store.getItem(key) } catch { return null }
  if (raw === null) return null

  let value
  try { value = JSON.parse(raw) } catch {
    safeRemove(store, key)
    return null
  }

  if (!validSession(value, userId, problemSlug, now)) {
    safeRemove(store, key)
    return null
  }

  const refreshed = { ...value, updatedAt: now, expiresAt: now + PROBLEM_SESSION_TTL_MS }
  try { store.setItem(key, JSON.stringify(refreshed)) } catch { /* A read must remain non-fatal. */ }
  return refreshed
}

export function writeProblemSession(session, storage) {
  const store = storage || defaultStorage()
  if (!store) return false
  const key = problemSessionKey(session.userId, session.problemSlug)
  try {
    store.setItem(key, JSON.stringify(session))
    return true
  } catch {
    return false
  }
}

export function removeProblemSessionsForUser(userId, storage) {
  const store = storage || defaultStorage()
  if (!store) return
  const prefix = `${PROBLEM_SESSION_KEY_PREFIX}${userId}:`
  try {
    const keys = []
    for (let index = 0; index < store.length; index += 1) {
      const key = store.key(index)
      if (key?.startsWith(prefix)) keys.push(key)
    }
    keys.forEach((key) => safeRemove(store, key))
  } catch { /* Storage is optional. */ }
}
