import {
  formatRunInputs,
  formatRunOutputs,
  isPassedTest,
  runErrorText,
  runStatusLabel,
  runResultTestCases,
  runTestState,
  submitErrorText,
  submitStatusKind,
  submitStatusLabel,
} from './executionPresentation'

const VIEWS = [
  { id: 'result', label: 'Result' },
  { id: 'input', label: 'Input' },
  { id: 'output', label: 'Output' },
]

function RunResult({ result }) {
  return (
    <div className="execution-workspace-result execution-workspace-run-result">
      <p className="execution-workspace-status">Status: <span className={isPassedTest(result) ? 'is-passed' : 'is-failed'}>{runStatusLabel(result)}</span></p>
      <div className="execution-workspace-test-cards" aria-label="Run test cases">
        {runResultTestCases(result).map((testResult, index) => (
          <article className={`execution-workspace-test-card ${runTestState(testResult)}`} key={`run-test-${index}`}>
            Test Case {index + 1}
          </article>
        ))}
      </div>
      {runErrorText(result) && (
        <div className="execution-workspace-run-error" role="alert">
          <p>Error:</p>
          <div>{runErrorText(result)}</div>
        </div>
      )}
    </div>
  )
}

function SubmissionResult({ result }) {
  const errorText = submitErrorText(result)
  return (
    <div className="execution-workspace-result execution-workspace-submit-result">
      <p className="execution-workspace-status">Status: <span className={submitStatusKind(result)}>{submitStatusLabel(result)}</span></p>
      <div className="execution-workspace-test-cards" aria-label="Submit test cases">
        {result.results.map((testResult, index) => (
          <article className={`execution-workspace-test-card ${runTestState(testResult)}`} key={`${testResult.display_order ?? 'test'}-${index}`}>
            Test Case {testResult.display_order ?? index + 1}
          </article>
        ))}
      </div>
      {errorText && <div className="execution-workspace-submit-error" role="alert"><p>Error:</p><div>{errorText}</div></div>}
    </div>
  )
}

function AiHelp({ state, canRequest, onRequest }) {
  if (!canRequest) return null

  if (state.status === 'loading') {
    return <div className="execution-workspace-ai-content"><p className="execution-workspace-ai-status" role="status">AI Help is thinking…</p></div>
  }

  if (state.status === 'error') {
    return <div className="execution-workspace-ai-content"><p className="execution-workspace-ai-status" role="alert">{state.error}</p></div>
  }

  if (state.status === 'success') {
    return (
      <div className="execution-workspace-ai-content">
        <aside className="execution-workspace-ai-result" aria-label="AI Help">
          <p className="execution-workspace-ai-summary">{state.result.summary}</p>
          <ul>{state.result.tips.map((tip, index) => <li key={`${index}-${tip}`}>{tip}</li>)}</ul>
        </aside>
      </div>
    )
  }

  return (
    <div className="execution-workspace-ai-content">
      <div className="execution-workspace-ai-action">
        <button type="button" className="execution-workspace-ai-button" onClick={onRequest}>AI Help?</button>
      </div>
    </div>
  )
}

function RunIcon() {
  return (
    <svg className="execution-workspace-run-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="m8 5 11 7-11 7V5Z" />
    </svg>
  )
}

function CustomInputWorkspace({ customInput, customInputError, phase, result, error, aiHelpState, canRequestAiHelp, onAiHelp, onCustomInputChange, onCustomRun }) {
  const customResult = result?.results?.[0]
  const output = customResult?.stdout || ''
  const diagnostic = customResult?.stderr || error || ''
  const hasExecutionError = phase === 'error' || (phase === 'completed' && result?.status !== 'passed')

  return (
    <div className="execution-workspace-custom-panel">
      <div className="execution-workspace-custom-toolbar">
        <button type="button" className="code-editor-button execution-workspace-custom-run" onClick={onCustomRun} disabled={phase === 'running'}>
          <RunIcon />
          Run
        </button>
      </div>
      <div className="execution-workspace-custom-panes">
        <div className="execution-workspace-custom-pane">
          <h3>Input</h3>
          <textarea value={customInput ?? ''} onChange={(event) => onCustomInputChange(event.target.value)} placeholder="Enter your custom input here" aria-label="Custom input" />
          {customInputError && <p className="execution-workspace-input-error" role="alert">{customInputError}</p>}
        </div>
        <div className="execution-workspace-custom-pane">
          <h3>Output</h3>
          <div className="execution-workspace-custom-output" aria-label="Custom output">
            <AiHelp state={aiHelpState} canRequest={canRequestAiHelp} onRequest={onAiHelp} />
            {phase === 'running' ? 'Running…' : output || (!hasExecutionError ? 'No output yet.' : '')}
            {hasExecutionError && (
              <div className="execution-workspace-custom-error" role="alert">
                {diagnostic && <div>{diagnostic}</div>}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export function ExecutionWorkspace({ mode, activeView, customInput, customInputError, phase, result, error, aiHelpState, canRequestAiHelp, onAiHelp, onCustomInputChange, onCustomRun, onViewChange }) {
  if (mode === 'custom') {
    return (
      <section className="execution-workspace is-custom" aria-label="Custom Input workspace">
        <CustomInputWorkspace
          customInput={customInput}
          customInputError={customInputError}
          phase={phase}
          result={result}
          error={error}
          aiHelpState={aiHelpState}
          canRequestAiHelp={canRequestAiHelp}
          onAiHelp={onAiHelp}
          onCustomInputChange={onCustomInputChange}
          onCustomRun={onCustomRun}
        />
      </section>
    )
  }

  const showTabs = mode === 'run'
  const visibleView = mode === 'custom' ? 'input' : mode === 'submit' ? 'result' : activeView
  const hasAiResponse = aiHelpState.status === 'success'
  const panelClassName = `execution-workspace-panel ${showTabs ? 'is-tabbed' : 'is-full-height'}${hasAiResponse ? ' has-ai-response' : ''}`
  const inputClassName = `execution-workspace-input ${mode === 'custom' ? 'execution-workspace-input--custom' : 'execution-workspace-input--run'}`
  const input = formatRunInputs(result)
  const output = mode === 'run' && phase === 'completed' ? formatRunOutputs(result) : ''

  return (
    <section className={`execution-workspace${showTabs ? ' has-tabs' : ''}${mode === 'submit' ? ' is-submit' : ''}`} aria-label="Result, Input, and Output">
      {showTabs && (
        <div className="execution-workspace-tabs" role="tablist" aria-label="Views">
          {VIEWS.map((view) => (
            <button
              key={view.id}
              type="button"
              id={`execution-${view.id}-tab`}
              className={`execution-workspace-tab${visibleView === view.id ? ' is-active' : ''}`}
              role="tab"
              aria-selected={visibleView === view.id}
              aria-controls={`execution-${view.id}-panel`}
              onClick={() => onViewChange(view.id)}
            >
              {view.label}
            </button>
          ))}
        </div>
      )}

      <div
        className={panelClassName}
        role={showTabs ? 'tabpanel' : undefined}
        id={`execution-${visibleView}-panel`}
        aria-labelledby={showTabs ? `execution-${visibleView}-tab` : undefined}
      >
        {visibleView === 'result' && (
          phase === 'idle' ? (
            <div className="execution-workspace-empty"><p>No result yet.</p></div>
          ) : phase === 'running' ? (
            <div className="execution-workspace-empty"><p>Running…</p></div>
          ) : phase === 'error' ? (
            <div className="execution-workspace-empty"><p role="alert">{error}</p></div>
          ) : mode === 'run' ? (
            <div className={`execution-workspace-run-result-container${aiHelpState.status === 'success' ? ' has-ai-response' : ''}`}>
              <div className={`execution-workspace-run-ai${aiHelpState.status === 'success' ? ' has-ai-response' : ''}`}>
                <AiHelp state={aiHelpState} canRequest={canRequestAiHelp} onRequest={onAiHelp} />
              </div>
              <div className="execution-workspace-run-result-scroll">
                <RunResult result={result} />
              </div>
            </div>
          ) : (
            <div className={`execution-workspace-submit-result-container${aiHelpState.status === 'success' ? ' has-ai-response' : ''}`}>
              <div className={`execution-workspace-submit-ai${aiHelpState.status === 'success' ? ' has-ai-response' : ''}`}>
                <AiHelp state={aiHelpState} canRequest={canRequestAiHelp} onRequest={onAiHelp} />
              </div>
              <div className="execution-workspace-submit-result-scroll">
                <SubmissionResult result={result} />
              </div>
            </div>
          )
        )}

        {visibleView === 'input' && (
          <div className={`${inputClassName}${mode === 'run' ? ' execution-workspace-input--fill' : ''}`}>
            {mode === 'custom' ? (
              <textarea value={customInput ?? ''} onChange={(event) => onCustomInputChange(event.target.value)} placeholder="Enter your custom input here" aria-label="Custom input" />
            ) : (
              <div className="execution-workspace-readonly-content" aria-label="Run input">{input || 'No input yet.'}</div>
            )}
            {mode === 'custom' && customInputError && (
              <p className="execution-workspace-input-error" role="alert">{customInputError}</p>
            )}
          </div>
        )}

        {visibleView === 'output' && (
          <div className="execution-workspace-input execution-workspace-input--run execution-workspace-input--fill">
            <div className="execution-workspace-readonly-content" aria-label="Run output">{output || 'No output yet.'}</div>
          </div>
        )}
      </div>
    </section>
  )
}
