import { useEffect, useRef, useState } from 'react'
import { defaultKeymap, history, historyKeymap, indentWithTab } from '@codemirror/commands'
import { cppLanguage } from '@codemirror/lang-cpp'
import { pythonLanguage } from '@codemirror/lang-python'
import {
  bracketMatching,
  defaultHighlightStyle,
  foldGutter,
  foldKeymap,
  indentOnInput,
  syntaxHighlighting,
} from '@codemirror/language'
import { EditorState } from '@codemirror/state'
import { EditorView, keymap } from '@codemirror/view'

const LANGUAGES = {
  python: {
    label: 'Python',
    language: pythonLanguage,
  },
  cpp: {
    label: 'C++',
    language: cppLanguage,
  },
}

function createEditorState(language, document) {
  return EditorState.create({
    doc: document,
    extensions: [
      history(),
      keymap.of([...defaultKeymap, ...historyKeymap, indentWithTab, ...foldKeymap]),
      LANGUAGES[language].language,
      indentOnInput(),
      syntaxHighlighting(defaultHighlightStyle),
      bracketMatching(),
      foldGutter(),
      EditorView.contentAttributes.of({ 'aria-label': `${LANGUAGES[language].label} code editor` }),
    ],
  })
}

export function CodeEditor({
  starterCode,
  isExpanded,
  onToggleExpansion,
  onCustomInput,
  onRun,
  onSubmit,
}) {
  const editorElement = useRef(null)
  const viewRef = useRef(null)
  const sessionsRef = useRef(null)
  const activeLanguageRef = useRef('python')
  const [selectedLanguage, setSelectedLanguage] = useState('python')

  useEffect(() => {
    activeLanguageRef.current = 'python'
    setSelectedLanguage('python')

    const sessions = {
      python: createEditorState('python', starterCode.python),
      cpp: createEditorState('cpp', starterCode.cpp),
    }
    const view = new EditorView({ state: sessions.python, parent: editorElement.current })

    sessionsRef.current = sessions
    viewRef.current = view

    return () => {
      view.destroy()
      sessionsRef.current = null
      viewRef.current = null
    }
  }, [starterCode])

  useEffect(() => {
    const view = viewRef.current
    const sessions = sessionsRef.current
    if (!view || !sessions || activeLanguageRef.current === selectedLanguage) return

    sessions[activeLanguageRef.current] = view.state
    view.setState(sessions[selectedLanguage])
    activeLanguageRef.current = selectedLanguage
  }, [selectedLanguage])

  function resetCurrentLanguage() {
    const language = activeLanguageRef.current
    const nextState = createEditorState(language, starterCode[language])
    sessionsRef.current[language] = nextState
    viewRef.current.setState(nextState)
  }

  function clearCurrentLanguage() {
    const view = viewRef.current
    view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: '' } })
  }

  return (
    <section className="code-editor" aria-label="Code editor">
      <div className="code-editor-toolbar">
        <label className="code-editor-language">
          <select
            aria-label="Editor language"
            value={selectedLanguage}
            onChange={(event) => setSelectedLanguage(event.target.value)}
          >
            {Object.entries(LANGUAGES).map(([language, details]) => (
              <option key={language} value={language}>{details.label}</option>
            ))}
          </select>
        </label>
        <div className="code-editor-controls">
          <button type="button" className="code-editor-button" onClick={resetCurrentLanguage}>Reset</button>
          <button type="button" className="code-editor-button" onClick={clearCurrentLanguage}>Clear</button>
        </div>
        <button
          type="button"
          className="code-editor-button code-editor-expand"
          aria-label={isExpanded ? 'Collapse editor' : 'Expand editor'}
          aria-expanded={isExpanded}
          onClick={onToggleExpansion}
        >
          <svg
            className="editor-expand-icon"
            viewBox="0 0 20 20"
            role="img"
            aria-label={isExpanded ? 'Collapse coding pane' : 'Expand coding pane'}
          >
            {isExpanded ? (
              <path d="M8 3H3v5M12 17h5v-5M3 8l5-5M17 12l-5 5" />
            ) : (
              <path d="M8 3H3v5M12 17h5v-5M3 3l5 5M17 17l-5-5" />
            )}
          </svg>
        </button>
      </div>

      <div ref={editorElement} className="code-editor-surface" />

      <div className="code-editor-actions" aria-label="Coding pane actions">
        <button type="button" className="code-editor-button" onClick={onCustomInput}>
          <svg className="action-icon" viewBox="0 0 20 20" aria-hidden="true">
            <path d="M4 4h12v9H8l-4 3V4Z" />
            <path d="m7 7 2 2-2 2M10 11h3" />
          </svg>
          Custom Input
        </button>
        <button type="button" className="code-editor-button" onClick={onRun}>
          <svg className="action-icon" viewBox="0 0 20 20" aria-hidden="true">
            <path d="m7 4 9 6-9 6V4Z" />
          </svg>
          Run
        </button>
        <button type="button" className="primary-button" onClick={onSubmit}>
          <svg className="action-icon" viewBox="0 0 20 20" aria-hidden="true">
            <path d="m3 10 14-6-4 12-3-5-7-1Z" />
            <path d="m10 11 4-4" />
          </svg>
          Submit
        </button>
      </div>
    </section>
  )
}
