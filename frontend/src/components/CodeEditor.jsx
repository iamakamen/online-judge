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
import { EditorView, keymap, lineNumbers } from '@codemirror/view'

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

const editorTheme = EditorView.theme({
  '.cm-cursor, .cm-dropCursor': {
    borderLeftColor: '#61a9ff !important',
    borderLeftWidth: '2px',
  },
  '.cm-gutters': {
    backgroundColor: '#07101d',
    color: '#66788f',
    borderRight: '1px solid #1d334c',
  },
  '.cm-lineNumbers .cm-gutterElement': {
    minWidth: '34px',
    padding: '0 8px 0 4px',
  },
  '.cm-foldGutter .cm-gutterElement': {
    width: '16px',
    padding: '0 2px',
  },
})

function createEditorState(language, document) {
  return EditorState.create({
    doc: document,
    extensions: [
      history(),
      keymap.of([...defaultKeymap, ...historyKeymap, indentWithTab, ...foldKeymap]),
      lineNumbers(),
      LANGUAGES[language].language,
      indentOnInput(),
      syntaxHighlighting(defaultHighlightStyle),
      bracketMatching(),
      foldGutter(),
      editorTheme,
      EditorView.contentAttributes.of({ 'aria-label': `${LANGUAGES[language].label} code editor` }),
    ],
  })
}

function ChevronIcon() {
  return (
    <svg className="select-chevron" viewBox="0 0 16 16" aria-hidden="true">
      <path d="M4 6.5L8 10.5L12 6.5" />
    </svg>
  )
}

function ExpandIcon({ isExpanded }) {
  return (
    <svg className="editor-expand-icon" viewBox="0 0 20 20" aria-hidden="true">
      {isExpanded ? (
        <path d="M8 3H3v5M12 17h5v-5M3 8l5-5M17 12l-5 5" />
      ) : (
        <path d="M8 3H3v5M12 17h5v-5M3 3l5 5M17 17l-5-5" />
      )}
    </svg>
  )
}

function CustomInputIcon() {
  return (
    <svg className="action-icon action-icon-terminal" viewBox="0 0 24 24" aria-hidden="true">
      <rect x="3.5" y="4.5" width="17" height="15" rx="2" />
      <path d="m7 9 3 3-3 3M12.5 15h4" />
    </svg>
  )
}

function RunIcon() {
  return (
    <svg className="action-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path d="m8 5 11 7-11 7V5Z" />
    </svg>
  )
}

function SubmitIcon() {
  return (
    <svg className="action-icon action-icon-submit" viewBox="0 0 24 24" aria-hidden="true">
      <path d="m3 11 18-7-5 16-4-6-9-3Z" />
      <path d="m12 14 5-7" />
    </svg>
  )
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
          <span className="code-editor-language-select">
            <select
              aria-label="Editor language"
              value={selectedLanguage}
              onChange={(event) => setSelectedLanguage(event.target.value)}
            >
              {Object.entries(LANGUAGES).map(([language, details]) => (
                <option key={language} value={language}>{details.label}</option>
              ))}
            </select>
            <ChevronIcon />
          </span>
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
          <ExpandIcon isExpanded={isExpanded} />
        </button>
      </div>

      <div ref={editorElement} className="code-editor-surface" />

      <div className="code-editor-actions" aria-label="Coding pane actions">
        <button type="button" className="code-editor-button" onClick={onCustomInput}>
          <CustomInputIcon />
          Custom Input
        </button>
        <button type="button" className="code-editor-button" onClick={onRun}>
          <RunIcon />
          Run
        </button>
        <button type="button" className="primary-button" onClick={onSubmit}>
          <SubmitIcon />
          Submit
        </button>
      </div>
    </section>
  )
}
