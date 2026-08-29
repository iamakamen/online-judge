import { useEffect, useRef, useState } from 'react'
import {
  ApiError,
  createSubmission,
  getProblemBySlug,
  getSubmission,
  requestAiHelp,
  runCode,
} from '../api/client'
import { useAuth } from '../auth/useAuth'
import { CodeEditor } from '../components/CodeEditor'
import { ExecutionWorkspace } from '../components/ExecutionWorkspace'
import { PrimarySidebar } from '../components/PrimarySidebar'
import { resolveRunMode } from '../problem/runValidation'
import { useProblemSession } from '../problem/useProblemSession'
import { formatConstraints } from '../problem/constraintFormatting'
import './ProblemPage.css'

const SUBMISSION_POLL_INTERVAL_MS = 500
const SUBMISSION_POLL_TIMEOUT_MS = 60_000
const MAX_AI_DIAGNOSTIC_CHARS = 8_192
const MAX_AI_OUTPUT_CHARS = 16_384

function isTerminalSubmission(status) {
  return status === 'completed' || status === 'failed'
}

function formatDifficulty(difficulty) {
  if (!difficulty) return null
  const normalized = String(difficulty).toLowerCase()
  return normalized.charAt(0).toUpperCase() + normalized.slice(1)
}

function idleExecutionState() {
  return { phase: 'idle', result: null, error: null }
}

function idleAiHelpState() {
  return { status: 'idle', result: null, error: null }
}

function boundedText(value, limit) {
  return String(value || '').slice(0, limit)
}

function firstFailedRunResult(result) {
  return result?.results?.find((testResult) => testResult.status !== 'passed') || null
}

function buildRunAiHelpPayload(problemId, language, sourceCode, result) {
  const failedResult = firstFailedRunResult(result)
  const failedStatus = failedResult?.status || result.status
  const diagnostic = [
    `Run status: ${result.status}`,
    `Failed test status: ${failedStatus}`,
    failedResult?.stderr ? `Runtime diagnostic:\n${failedResult.stderr}` : '',
  ].filter(Boolean).join('\n')

  return {
    problem_id: problemId,
    language,
    operation: 'run',
    source_code: sourceCode,
    failure_status: failedStatus,
    diagnostic: boundedText(diagnostic, MAX_AI_DIAGNOSTIC_CHARS),
    stdout: boundedText(failedResult?.stdout, MAX_AI_OUTPUT_CHARS),
    stderr: boundedText(failedResult?.stderr, MAX_AI_OUTPUT_CHARS),
  }
}

function buildSubmitAiHelpPayload(problemId, language, sourceCode, result) {
  const failureStatus = result.verdict || 'system_error'
  const diagnostic = [
    `Submit status: ${result.status}`,
    `Submission verdict: ${failureStatus}`,
  ].join('\n')

  return {
    problem_id: problemId,
    language,
    operation: 'submit',
    source_code: sourceCode,
    failure_status: failureStatus,
    diagnostic: boundedText(diagnostic, MAX_AI_DIAGNOSTIC_CHARS),
    stdout: '',
    stderr: '',
  }
}

function isFailedRunResult(result) {
  return Boolean(result && result.status !== 'passed')
}

function isFailedSubmitResult(result) {
  return Boolean(
    result
    && (result.status === 'failed' || (result.verdict && result.verdict !== 'accepted'))
  )
}

function createExecutionId() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') return crypto.randomUUID()
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`
}

export function ProblemPage({ slug, navigate }) {
  const { requestAuthenticated, userId } = useAuth()
  const [problem, setProblem] = useState(null)
  const [error, setError] = useState(null)
  const [isSidebarExpanded, setIsSidebarExpanded] = useState(false)
  const [v2Feature, setV2Feature] = useState(null)
  const [isSubmissionsOpen, setIsSubmissionsOpen] = useState(false)
  const [executionView, setExecutionView] = useState(null)
  const [isCodingPaneExpanded, setIsCodingPaneExpanded] = useState(false)
  const [executionMode, setExecutionMode] = useState(null)
  const [customInput, setCustomInput] = useState(null)
  const [customInputError, setCustomInputError] = useState('')
  const [executionState, setExecutionState] = useState(idleExecutionState)
  const [aiHelpState, setAiHelpState] = useState(idleAiHelpState)
  const [aiHelpRequest, setAiHelpRequest] = useState(null)
  const [customExecutionState, setCustomExecutionState] = useState(idleExecutionState)
  const [customAiHelpState, setCustomAiHelpState] = useState(idleAiHelpState)
  const [customAiHelpRequest, setCustomAiHelpRequest] = useState(null)
  const [submissionId, setSubmissionId] = useState(null)
  const editorPayloadRef = useRef(null)
  const executionGenerationRef = useRef(0)
  const executionBusyRef = useRef(false)
  const aiHelpBusyRef = useRef(false)
  const customAiHelpBusyRef = useRef(false)
  const submissionContextRef = useRef(null)
  const currentExecutionIdRef = useRef(null)
  const customExecutionIdRef = useRef(null)
  const restoredSessionKeyRef = useRef(null)
  const { initialSession, hydrated, onEditorChange, persist } = useProblemSession({
    userId,
    problemSlug: slug,
    starterCode: problem?.starter_code,
    enabled: problem !== null,
  })

  useEffect(() => {
    let active = true

    setProblem(null)
    setError(null)
    setExecutionView(null)
    setExecutionMode(null)
    setCustomInput(null)
    setCustomInputError('')
    setIsCodingPaneExpanded(false)
    setExecutionState(idleExecutionState())
    setAiHelpState(idleAiHelpState())
    setAiHelpRequest(null)
    setCustomExecutionState(idleExecutionState())
    setCustomAiHelpState(idleAiHelpState())
    setCustomAiHelpRequest(null)
    setSubmissionId(null)
    submissionContextRef.current = null
    executionGenerationRef.current += 1
    executionBusyRef.current = false
    aiHelpBusyRef.current = false
    customAiHelpBusyRef.current = false
    currentExecutionIdRef.current = null
    customExecutionIdRef.current = null
    restoredSessionKeyRef.current = null

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
      executionGenerationRef.current += 1
    }
  }, [requestAuthenticated, slug])

  useEffect(() => {
    if (!problem || !hydrated || !initialSession) return
    const sessionKey = `${initialSession.userId}:${initialSession.problemSlug}`
    if (restoredSessionKeyRef.current === sessionKey) return
    restoredSessionKeyRef.current = sessionKey

    const mode = initialSession.lastExecutionMode
    const restoredMode = mode || (initialSession.latestRunResult ? 'run' : 'submit')
    const storedExecution = restoredMode === 'run'
      ? initialSession.latestRunResult
      : restoredMode === 'submit'
        ? initialSession.latestSubmitResult
        : null

    if (restoredMode && storedExecution) {
      currentExecutionIdRef.current = storedExecution.executionId
      setExecutionMode(mode)
      setExecutionView(initialSession.lastExecutionView || 'result')
      setExecutionState({ phase: 'completed', result: storedExecution.result, error: null })
      if (initialSession.aiHelp?.executionId === storedExecution.executionId) {
        setAiHelpState({ status: 'success', result: initialSession.aiHelp.response, error: null })
      } else if (isFailedRunResult(storedExecution.result) || isFailedSubmitResult(storedExecution.result)) {
        const sourceCode = initialSession.editorContents[storedExecution.language]
        const request = restoredMode === 'run'
          ? buildRunAiHelpPayload(problem.id, storedExecution.language, sourceCode, storedExecution.result)
          : buildSubmitAiHelpPayload(problem.id, storedExecution.language, sourceCode, storedExecution.result)
        setAiHelpRequest(request)
      }
    }
  }, [hydrated, initialSession, problem])

  useEffect(() => {
    if (submissionId === null) return undefined

    let active = true
    let timerId = null
    const deadline = Date.now() + SUBMISSION_POLL_TIMEOUT_MS

    async function pollSubmission() {
      try {
        const result = await requestAuthenticated((accessToken) => (
          getSubmission(accessToken, submissionId)
        ))

        if (!active) return

        if (isTerminalSubmission(result.status)) {
          const submissionContext = submissionContextRef.current
          setExecutionState({ phase: 'completed', result, error: null })
          persist({
            lastExecutionMode: 'submit',
            lastExecutionView: 'result',
            latestSubmitResult: {
              executionId: currentExecutionIdRef.current,
              language: submissionContext?.language,
              result,
            },
            aiHelp: null,
          }, true)
          if (isFailedSubmitResult(result) && submissionContext) {
            setAiHelpRequest(buildSubmitAiHelpPayload(
              problem.id,
              submissionContext.language,
              submissionContext.sourceCode,
              result,
            ))
          } else {
            setAiHelpRequest(null)
          }
          setAiHelpState(idleAiHelpState())
          setSubmissionId(null)
          executionBusyRef.current = false
          return
        }

        if (Date.now() >= deadline) {
          setExecutionState({
            phase: 'error',
            result: null,
            error: 'Submission polling timed out',
          })
          setSubmissionId(null)
          executionBusyRef.current = false
          return
        }

        timerId = window.setTimeout(pollSubmission, SUBMISSION_POLL_INTERVAL_MS)
      } catch (requestError) {
        if (!active) return
        setExecutionState({ phase: 'error', result: null, error: requestError.message })
        setSubmissionId(null)
        executionBusyRef.current = false
      }
    }

    pollSubmission()

    return () => {
      active = false
      if (timerId !== null) window.clearTimeout(timerId)
    }
  }, [problem?.id, persist, requestAuthenticated, submissionId])

  async function handleRun({ language, sourceCode }, requestedMode = 'run_tests') {
    if (executionBusyRef.current) return
    const mode = resolveRunMode(requestedMode, customInput)
    executionBusyRef.current = true
    executionGenerationRef.current += 1
    const generation = executionGenerationRef.current
    const executionId = createExecutionId()
    setCustomInputError('')
    if (mode === 'custom_input') {
      customExecutionIdRef.current = executionId
      persist({
        lastExecutionMode: null,
        lastExecutionView: null,
        latestRunResult: null,
        aiHelp: null,
      }, true)
    }
    const payload = {
      problem_id: problem.id,
      language,
      mode,
      source_code: sourceCode,
    }
    if (mode === 'custom_input') payload.custom_input = customInput

    if (mode === 'custom_input') {
      setExecutionMode('custom')
      setExecutionView(null)
      setSubmissionId(null)
      submissionContextRef.current = null
      setCustomAiHelpState(idleAiHelpState())
      setCustomAiHelpRequest(null)
      customAiHelpBusyRef.current = false
      setCustomExecutionState({ phase: 'running', result: null, error: null })

      try {
        const result = await requestAuthenticated((accessToken) => runCode(accessToken, payload))
        if (generation !== executionGenerationRef.current) return
        setCustomExecutionState({ phase: 'completed', result, error: null })
        if (isFailedRunResult(result)) {
          setCustomAiHelpRequest(buildRunAiHelpPayload(problem.id, language, sourceCode, result))
        } else {
          setCustomAiHelpRequest(null)
        }
        setCustomAiHelpState(idleAiHelpState())
        executionBusyRef.current = false
      } catch (requestError) {
        if (generation !== executionGenerationRef.current) return
        setCustomExecutionState({ phase: 'error', result: null, error: requestError.message })
        executionBusyRef.current = false
      }
      return
    }

    currentExecutionIdRef.current = executionId

    setExecutionMode('run')
    setExecutionView('result')
    setSubmissionId(null)
    submissionContextRef.current = null
    setAiHelpState(idleAiHelpState())
    setAiHelpRequest(null)
    aiHelpBusyRef.current = false
    setExecutionState({ phase: 'running', result: null, error: null })

    try {
      const result = await requestAuthenticated((accessToken) => runCode(accessToken, payload))
      if (generation !== executionGenerationRef.current) return
      setExecutionState({ phase: 'completed', result, error: null })
      persist({
        lastExecutionMode: 'run',
        lastExecutionView: 'result',
        latestRunResult: { executionId, language, result },
        aiHelp: null,
      }, true)
      if (isFailedRunResult(result)) {
        setAiHelpRequest(buildRunAiHelpPayload(problem.id, language, sourceCode, result))
      } else {
        setAiHelpRequest(null)
      }
      setAiHelpState(idleAiHelpState())
      executionBusyRef.current = false
    } catch (requestError) {
      if (generation !== executionGenerationRef.current) return
      setExecutionState({ phase: 'error', result: null, error: requestError.message })
      executionBusyRef.current = false
    }
  }

  async function handleSubmit({ language, sourceCode }) {
    if (executionBusyRef.current || executionState.phase === 'running') return
    executionBusyRef.current = true
    executionGenerationRef.current += 1
    const generation = executionGenerationRef.current
    const executionId = createExecutionId()
    currentExecutionIdRef.current = executionId
    setExecutionMode('submit')
    setExecutionView('result')
    setExecutionState({ phase: 'running', result: null, error: null })
    setSubmissionId(null)
    submissionContextRef.current = { language, sourceCode }
    setAiHelpState(idleAiHelpState())
    setAiHelpRequest(null)
    aiHelpBusyRef.current = false

    try {
      const result = await requestAuthenticated((accessToken) => (
        createSubmission(accessToken, {
          problem_id: problem.id,
          language,
          source_code: sourceCode,
        })
      ))
      if (generation !== executionGenerationRef.current) return
      setSubmissionId(result.id)
    } catch (requestError) {
      if (generation !== executionGenerationRef.current) return
      setExecutionState({ phase: 'error', result: null, error: requestError.message })
      executionBusyRef.current = false
    }
  }

  async function handleCustomAiHelp() {
    if (!customAiHelpRequest || customAiHelpBusyRef.current) return
    customAiHelpBusyRef.current = true
    const generation = executionGenerationRef.current
    setCustomAiHelpState({ status: 'loading', result: null, error: null })

    try {
      const result = await requestAuthenticated((accessToken) => (
        requestAiHelp(accessToken, customAiHelpRequest)
      ))
      if (generation !== executionGenerationRef.current) return
      setCustomAiHelpState({ status: 'success', result, error: null })
      persist({
        aiHelp: { executionId: customExecutionIdRef.current, response: result },
      }, true)
    } catch {
      if (generation !== executionGenerationRef.current) return
      setCustomAiHelpState({
        status: 'error',
        result: null,
        error: 'AI Help is temporarily unavailable. Please try again later.',
      })
    } finally {
      if (generation === executionGenerationRef.current) {
        customAiHelpBusyRef.current = false
      }
    }
  }

  function handleCustomRun() {
    if (typeof customInput !== 'string' || customInput.trim() === '') return
    if (editorPayloadRef.current) handleRun(editorPayloadRef.current, 'custom_input')
  }

  async function handleAiHelp() {
    if (!aiHelpRequest || aiHelpBusyRef.current) return
    aiHelpBusyRef.current = true
    const generation = executionGenerationRef.current
    setAiHelpState({ status: 'loading', result: null, error: null })

    try {
      const result = await requestAuthenticated((accessToken) => (
        requestAiHelp(accessToken, aiHelpRequest)
      ))
      if (generation !== executionGenerationRef.current) return
      setAiHelpState({ status: 'success', result, error: null })
      persist({
        aiHelp: { executionId: currentExecutionIdRef.current, response: result },
      }, true)
    } catch {
      if (generation !== executionGenerationRef.current) return
      setAiHelpState({
        status: 'error',
        result: null,
        error: 'AI Help is temporarily unavailable. Please try again later.',
      })
    } finally {
      if (generation === executionGenerationRef.current) {
        aiHelpBusyRef.current = false
      }
    }
  }

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

  const workspaceIsCustom = executionMode === 'custom'
  const workspaceExecutionState = workspaceIsCustom ? customExecutionState : executionState
  const workspaceAiHelpState = workspaceIsCustom ? customAiHelpState : aiHelpState
  const workspaceAiHelpRequest = workspaceIsCustom ? customAiHelpRequest : aiHelpRequest

  return (
    <div className={`problem-shell problem-page-v2${isSidebarExpanded ? ' sidebar-expanded' : ''}${isCodingPaneExpanded ? ' coding-expanded' : ''}`}>
      <PrimarySidebar
        isExpanded={isSidebarExpanded}
        onExpand={() => setIsSidebarExpanded(true)}
        onCollapse={() => setIsSidebarExpanded(false)}
        navigate={navigate}
        activeItem={null}
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
              {formatDifficulty(problem.difficulty) && (
                <span className="problem-tag problem-difficulty" aria-label="Problem difficulty">
                  {formatDifficulty(problem.difficulty)}
                </span>
              )}
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
            <pre className="problem-constraints">{formatConstraints(problem.constraints)}</pre>
            <div className="problem-limits">
              <div className="problem-limit">
                <h3>Time Constraint</h3>
                <p>{problem.time_limit_ms} ms</p>
              </div>
              <div className="problem-limit">
                <h3>Memory Constraint</h3>
                <p>{problem.memory_limit_mb} MB</p>
              </div>
            </div>
          </section>
        </section>

        <section className="coding-pane" aria-label="Coding workspace">
          <CodeEditor
            starterCode={problem.starter_code}
            initialSession={initialSession}
            isExpanded={isCodingPaneExpanded}
            onToggleExpansion={() => setIsCodingPaneExpanded((expanded) => !expanded)}
            onCustomInput={() => {
              if (executionMode === 'custom') {
                setExecutionMode(null)
                setExecutionView(null)
                return
              }
              setCustomInput((input) => input ?? '')
              setCustomInputError('')
              setExecutionMode('custom')
              setExecutionView('input')
            }}
            onRun={(payload) => handleRun(payload, 'run_tests')}
            onSubmit={handleSubmit}
            onEditorChange={(payload) => {
              editorPayloadRef.current = {
                language: payload.selectedLanguage,
                sourceCode: payload.editorContents[payload.selectedLanguage],
              }
              onEditorChange(payload)
            }}
            executionDisabled={executionState.phase === 'running' || customExecutionState.phase === 'running'}
          />
          {executionMode !== null && (
            <ExecutionWorkspace
              mode={executionMode}
              activeView={executionView}
              customInput={customInput}
              phase={workspaceExecutionState.phase}
              result={workspaceExecutionState.result}
              error={workspaceExecutionState.error}
              aiHelpState={workspaceAiHelpState}
              canRequestAiHelp={workspaceAiHelpRequest !== null || workspaceAiHelpState.status === 'success'}
              onAiHelp={workspaceIsCustom ? handleCustomAiHelp : handleAiHelp}
              customInputError={customInputError}
              onCustomInputChange={(value) => {
                setCustomInput(value)
                setCustomInputError('')
              }}
              onCustomRun={handleCustomRun}
              onViewChange={setExecutionView}
            />
          )}
        </section>
      </main>

      {(isSubmissionsOpen || v2Feature) && (
        <div
          className="modal-backdrop"
          role="presentation"
          onClick={() => {
            setIsSubmissionsOpen(false)
            setV2Feature(null)
          }}
        >
          <section
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="problem-future-feature-title"
            onClick={(event) => event.stopPropagation()}
          >
            <h2 id="problem-future-feature-title">{v2Feature || 'Submissions'}</h2>
            <p className="muted">Arriving in V2</p>
            <button
              type="button"
              className="primary-button"
              onClick={() => {
                setIsSubmissionsOpen(false)
                setV2Feature(null)
              }}
            >
              Close
            </button>
          </section>
        </div>
      )}
    </div>
  )
}
