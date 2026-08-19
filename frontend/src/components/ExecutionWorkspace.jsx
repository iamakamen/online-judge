const VIEWS = [
  { id: 'result', label: 'Result' },
  { id: 'input', label: 'Input' },
  { id: 'output', label: 'Output' },
]

export function ExecutionWorkspace({ mode, activeView, customInput, runInput, onCustomInputChange, onViewChange }) {
  const showTabs = mode === 'run'
  const visibleView = mode === 'custom' ? 'input' : mode === 'submit' ? 'result' : activeView

  return (
    <section className="execution-workspace" aria-label="Result, Input, and Output">
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
        className="execution-workspace-panel"
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
          mode === 'custom' ? (
            <label className="execution-workspace-input">
              <textarea
                value={customInput}
                onChange={(event) => onCustomInputChange(event.target.value)}
                placeholder="Enter your custom input here"
                rows="8"
                aria-label="Custom input"
              />
            </label>
          ) : (
            <pre className="execution-workspace-public-input">{customInput || runInput}</pre>
          )
        )}

        {visibleView === 'output' && (
          <div className="execution-workspace-empty">
            <h3>Output</h3>
            <p>No output yet.</p>
          </div>
        )}
      </div>
    </section>
  )
}
