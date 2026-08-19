const VIEWS = [
  { id: 'result', label: 'Result' },
  { id: 'input', label: 'Input' },
  { id: 'output', label: 'Output' },
]

export function ExecutionWorkspace({ mode, activeView, customInput, runInput, onCustomInputChange, onViewChange }) {
  const showTabs = mode === 'run'
  const visibleView = mode === 'custom' ? 'input' : mode === 'submit' ? 'result' : activeView
  const panelClassName = `execution-workspace-panel ${showTabs ? 'is-tabbed' : 'is-full-height'}`

  return (
    <section className={`execution-workspace${showTabs ? ' has-tabs' : ''}`} aria-label="Result, Input, and Output">
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
          <div className="execution-workspace-empty">
            <h3>Result</h3>
            <p>No result yet.</p>
          </div>
        )}

        {visibleView === 'input' && (
          <label className="execution-workspace-input">
            <textarea
              value={mode === 'custom' ? customInput : customInput || runInput}
              onChange={mode === 'custom' ? (event) => onCustomInputChange(event.target.value) : undefined}
              placeholder={mode === 'custom' ? 'Enter your custom input here' : 'No input yet.'}
              readOnly={mode !== 'custom'}
              aria-label={mode === 'custom' ? 'Custom input' : 'Run input'}
            />
          </label>
        )}

        {visibleView === 'output' && (
          <label className="execution-workspace-input">
            <textarea
              value=""
              placeholder="No output yet."
              readOnly
              aria-label="Run output"
            />
          </label>
        )}
      </div>
    </section>
  )
}
