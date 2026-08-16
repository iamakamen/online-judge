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

export function CodeEditor({ starterCode }) {
  const editorElement = useRef(null)
  const viewRef = useRef(null)
  const sessionsRef = useRef(null)
  const activeLanguageRef = useRef('python')
  const [selectedLanguage, setSelectedLanguage] = useState('python')
  const [isExpanded, setIsExpanded] = useState(false)

  useEffect(() => {
    activeLanguageRef.current = 'python'
    setSelectedLanguage('python')
    setIsExpanded(false)

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
    <section className={`code-editor${isExpanded ? ' is-expanded' : ''}`} aria-labelledby="code-editor-title">
      <div className="code-editor-header">
        <div>
          <p className="eyebrow">Workspace</p>
          <h2 id="code-editor-title">Code editor</h2>
        </div>
        <label className="code-editor-language">
          <span>Language</span>
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
      </div>

      <div className="code-editor-toolbar">
        <button type="button" className="code-editor-button" onClick={resetCurrentLanguage}>Reset</button>
        <button type="button" className="code-editor-button" onClick={clearCurrentLanguage}>Clear</button>
        <button
          type="button"
          className="code-editor-button code-editor-expand"
          aria-expanded={isExpanded}
          onClick={() => setIsExpanded((expanded) => !expanded)}
        >
          {isExpanded ? 'Collapse editor' : 'Expand editor'}
        </button>
      </div>

      <div ref={editorElement} className="code-editor-surface" aria-label="Code editor" />
    </section>
  )
}
