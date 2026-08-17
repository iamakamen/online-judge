import { useState } from 'react'

const VIEWS = [
  { id: 'result', label: 'Result' },
  { id: 'input', label: 'Input' },
  { id: 'output', label: 'Output' },
]

export function ExecutionWorkspace() {
  const [activeView, setActiveView] = useState('result')
  const [customInput, setCustomInput] = useState('')

  return (
    <section className="execution-workspace" aria-labelledby="execution-workspace-title">
      <div className="execution-workspace-header">
        <div>
          <p className="eyebrow">Execution</p>
          <h2 id="execution-workspace-title">Run your code</h2>
        </div>
        <button type="button" className="primary-button">Run</button>
      </div>

      <div className="execution-workspace-tabs" role="tablist" aria-label="Execution workspace views">
        {VIEWS.map((view) => (
          <button
            key={view.id}
            type="button"
            id={`execution-${view.id}-tab`}
            className={`execution-workspace-tab${activeView === view.id ? ' is-active' : ''}`}
            role="tab"
            aria-selected={activeView === view.id}
            aria-controls={`execution-${view.id}-panel`}
            onClick={() => setActiveView(view.id)}
          >
            {view.label}
          </button>
        ))}
      </div>

      <div
        className="execution-workspace-panel"
        role="tabpanel"
        id={`execution-${activeView}-panel`}
        aria-labelledby={`execution-${activeView}-tab`}
      >
        {activeView === 'result' && (
          <div className="execution-workspace-empty">
            <h3>Result</h3>
            <p>Run your code to see the result here.</p>
          </div>
        )}

        {activeView === 'input' && (
          <label className="execution-workspace-input">
            <span>Custom input</span>
            <textarea
              value={customInput}
              onChange={(event) => setCustomInput(event.target.value)}
              placeholder="Enter input for your code"
              rows="8"
            />
          </label>
        )}

        {activeView === 'output' && (
          <div className="execution-workspace-empty">
            <h3>Output</h3>
            <p>Output will appear here after your code runs.</p>
          </div>
        )}
      </div>
    </section>
  )
}
