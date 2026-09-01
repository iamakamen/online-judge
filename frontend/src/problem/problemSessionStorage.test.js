import assert from 'node:assert/strict'
import { test } from 'node:test'
import {
  PROBLEM_SESSION_TTL_MS,
  contentWithAcceptedFallback,
  createProblemSession,
  problemSessionKey,
  readProblemSession,
  selectInitialLanguage,
  writeProblemSession,
} from './problemSessionStorage.js'

class MemoryStorage {
  constructor() { this.values = new Map() }
  get length() { return this.values.size }
  key(index) { return [...this.values.keys()][index] ?? null }
  getItem(key) { return this.values.get(key) ?? null }
  setItem(key, value) { this.values.set(key, value) }
  removeItem(key) { this.values.delete(key) }
}

function session(userId = 7, problemSlug = 'two-sum') {
  return createProblemSession(userId, problemSlug, { python: 'print(1)', cpp: 'int main() {}' })
}

test('constructs user- and problem-scoped keys', () => {
  assert.equal(problemSessionKey(7, 'two-sum'), 'oj:problem-session:7:two-sum')
  assert.notEqual(problemSessionKey(7, 'two-sum'), problemSessionKey(8, 'two-sum'))
  assert.notEqual(problemSessionKey(7, 'two-sum'), problemSessionKey(7, 'three-sum'))
})

test('selects Python by default unless only C++ is accepted', () => {
  assert.equal(selectInitialLanguage(null, { python: null, cpp: null }), 'python')
  assert.equal(selectInitialLanguage(null, { python: 'py', cpp: null }), 'python')
  assert.equal(selectInitialLanguage(null, { python: null, cpp: 'cpp' }), 'cpp')
  assert.equal(selectInitialLanguage(null, { python: 'py', cpp: 'cpp' }), 'python')
})

test('existing local language overrides accepted-solution availability', () => {
  assert.equal(selectInitialLanguage({ selectedLanguage: 'python' }, { python: null, cpp: 'cpp' }), 'python')
  assert.equal(selectInitialLanguage({ selectedLanguage: 'cpp' }, { python: 'py', cpp: null }), 'cpp')
  assert.equal(selectInitialLanguage({ selectedLanguage: 'cpp' }, { python: 'py', cpp: 'cpp' }), 'cpp')
  assert.equal(selectInitialLanguage({ selectedLanguage: 'python' }, { python: 'py', cpp: 'cpp' }), 'python')
  assert.equal(selectInitialLanguage({ selectedLanguage: 'cpp' }, { python: null, cpp: null }), 'cpp')
  assert.equal(selectInitialLanguage({ selectedLanguage: 'python' }, { python: null, cpp: null }), 'python')
})

test('last active language selects between simultaneous local sessions', () => {
  const localPython = { selectedLanguage: 'python' }
  const localCpp = { selectedLanguage: 'cpp' }
  assert.equal(selectInitialLanguage(localPython, { python: null, cpp: 'cpp' }), 'python')
  assert.equal(selectInitialLanguage(localCpp, { python: 'py', cpp: null }), 'cpp')
})

test('latest accepted sources remain isolated by language', () => {
  const contents = contentWithAcceptedFallback(
    { python: 'print(1)', cpp: 'int main() {}' },
    { python: 'print(1)', cpp: 'int main() {}' },
    { python: 'python #2', cpp: 'cpp #1' },
  )
  assert.deepEqual(contents, { python: 'python #2', cpp: 'cpp #1' })
})

test('uses accepted source only where the local content is still starter code', () => {
  const contents = contentWithAcceptedFallback(
    { python: 'unsaved python', cpp: 'int main() {}' },
    { python: 'print(1)', cpp: 'int main() {}' },
    { python: 'accepted python', cpp: 'accepted cpp' },
  )
  assert.deepEqual(contents, {
    python: 'unsaved python',
    cpp: 'accepted cpp',
  })
})

test('writes and reads a valid session, extending its sliding TTL', () => {
  const storage = new MemoryStorage()
  const original = session()
  writeProblemSession(original, storage)
  const restored = readProblemSession(7, 'two-sum', storage, original.updatedAt + 1_000)

  assert.equal(restored.editorContents.python, 'print(1)')
  assert.equal(restored.expiresAt, original.updatedAt + 1_000 + PROBLEM_SESSION_TTL_MS)
})

test('removes malformed, expired, and invalid-schema records', () => {
  const storage = new MemoryStorage()
  const key = problemSessionKey(7, 'two-sum')
  storage.setItem(key, '{not-json')
  assert.equal(readProblemSession(7, 'two-sum', storage), null)
  assert.equal(storage.getItem(key), null)

  const expired = session()
  expired.expiresAt = expired.updatedAt - 1
  writeProblemSession(expired, storage)
  assert.equal(readProblemSession(7, 'two-sum', storage), null)

  const invalid = session()
  invalid.schemaVersion = 99
  writeProblemSession(invalid, storage)
  assert.equal(readProblemSession(7, 'two-sum', storage), null)
})

test('rejects records for another user or problem', () => {
  const storage = new MemoryStorage()
  const value = session()
  writeProblemSession(value, storage)
  assert.equal(readProblemSession(8, 'two-sum', storage), null)
  assert.equal(readProblemSession(7, 'three-sum', storage), null)
})

test('rejects loading results and malformed AI responses', () => {
  const storage = new MemoryStorage()
  const loading = session()
  loading.latestRunResult = { executionId: 'run-1', result: { status: 'running' } }
  writeProblemSession(loading, storage)
  assert.equal(readProblemSession(7, 'two-sum', storage), null)

  const invalidAi = session()
  invalidAi.aiHelp = { executionId: 'run-1', response: { summary: '', tips: [] } }
  writeProblemSession(invalidAi, storage)
  assert.equal(readProblemSession(7, 'two-sum', storage), null)
})

test('persists public Run results but rejects custom-input results', () => {
  const storage = new MemoryStorage()
  const publicRun = session()
  publicRun.lastExecutionMode = 'run'
  publicRun.latestRunResult = {
    executionId: 'run-public',
    language: 'python',
    result: {
      status: 'passed', language: 'python', mode: 'run_tests', results: [],
    },
  }
  writeProblemSession(publicRun, storage)
  assert.ok(readProblemSession(7, 'two-sum', storage))

  const customRun = session()
  customRun.lastExecutionMode = 'run'
  customRun.latestRunResult = {
    executionId: 'run-custom',
    language: 'python',
    result: {
      status: 'failed', language: 'python', mode: 'custom_input', results: [],
    },
  }
  writeProblemSession(customRun, storage)
  assert.equal(readProblemSession(7, 'two-sum', storage), null)
})

test('storage failures are non-fatal', () => {
  const failingStorage = {
    getItem() { throw new Error('blocked') },
    setItem() { throw new DOMException('quota', 'QuotaExceededError') },
    removeItem() { throw new Error('blocked') },
  }
  assert.equal(readProblemSession(7, 'two-sum', failingStorage), null)
  assert.equal(writeProblemSession(session(), failingStorage), false)
})
