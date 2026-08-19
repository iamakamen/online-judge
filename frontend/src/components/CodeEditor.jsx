import { useEffect, useRef, useState } from 'react'
import { defaultKeymap, history, historyKeymap, indentWithTab } from '@codemirror/commands'
import { cppLanguage } from '@codemirror/lang-cpp'
import { pythonLanguage } from '@codemirror/lang-python'
import {
  bracketMatching,
  HighlightStyle,
  foldGutter,
  foldKeymap,
  indentOnInput,
  syntaxHighlighting,
} from '@codemirror/language'
import { tags } from '@lezer/highlight'
import { EditorState } from '@codemirror/state'
import { EditorView, keymap, lineNumbers } from '@codemirror/view'

const LANGUAGES = {
  python: { label: 'Python', language: pythonLanguage },
  cpp: { label: 'C++', language: cppLanguage },
}

const editorHighlightStyle = HighlightStyle.define([
  { tag: tags.keyword, color: '#72b8ff' },
  { tag: tags.controlKeyword, color: '#72b8ff' },
  { tag: tags.operatorKeyword, color: '#72b8ff' },
  { tag: tags.definition(tags.variableName), color: '#f5f8fc' },
  { tag: tags.function(tags.variableName), color: '#f2d27b' },
  { tag: tags.variableName, color: '#dbe8f5' },
  { tag: tags.typeName, color: '#75d0e8' },
  { tag: tags.className, color: '#75d0e8' },
  { tag: tags.propertyName, color: '#a9d5ff' },
  { tag: tags.string, color: '#9bd39a' },
  { tag: tags.number, color: '#d2b1ff' },
  { tag: tags.bool, color: '#d2b1ff' },
  { tag: tags.atom, color: '#d2b1ff' },
  { tag: tags.comment, color: '#8298b0', fontStyle: 'italic' },
  { tag: tags.docComment, color: '#90a9c0', fontStyle: 'italic' },
  { tag: tags.punctuation, color: '#d2deeb' },
  { tag: tags.paren, color: '#d2deeb' },
  { tag: tags.operator, color: '#d2deeb' },
  { tag: tags.meta, color: '#a7d2f5' },
  { tag: tags.invalid, color: '#ff9b9b' },
])

const editorTheme = EditorView.theme({
  '.cm-content': {
    caretColor: '#ffffff',
    color: '#edf4fb',
  },
  '.cm-cursor, .cm-dropCursor': {
    borderLeft: '2px solid #ffffff !important',
    boxShadow: '0 0 0 1px #07101d, 0 0 0 2px #61a9ff, 0 0 10px #61a9ff',
    opacity: '1 !important',
    visibility: 'visible !important',
  },
  '.cm-gutters': {
    backgroundColor: '#091321',
    color: '#71869d',
    borderRight: '1px solid #1d334c',
  },
  '.cm-lineNumbers .cm-gutterElement': {
    minWidth: '30px',
    padding: '0 0.5px 0 1px',
  },
  '.cm-foldGutter .cm-gutterElement': {
    width: '18px',
    padding: '0 1px 0 0.5px',
    textAlign: 'right',
  },
  '.cm-custom-fold-marker': {
    display: 'inline-block',
    width: '8px',
    height: '8px',
    boxSizing: 'border-box',
    borderRight: '1.5px solid #8da3bb',
    borderBottom: '1.5px solid #8da3bb',
    transform: 'rotate(-45deg)',
    transition: 'transform 120ms ease, border-color 120ms ease',
  },
  '.cm-custom-fold-marker.is-open': { transform: 'rotate(45deg)' },
  '.cm-custom-fold-marker:hover': { borderColor: '#f5f8fc' },
})

function createFoldMarker(open) {
  const marker = document.createElement('span')
  marker.className = `cm-custom-fold-marker${open ? ' is-open' : ''}`
  marker.setAttribute('aria-hidden', 'true')
  return marker
}

function createEditorState(language, document) {
  return EditorState.create({
    doc: document,
    extensions: [
      history(),
      keymap.of([...defaultKeymap, ...historyKeymap, indentWithTab, ...foldKeymap]),
      lineNumbers(),
      LANGUAGES[language].language,
      indentOnInput(),
      syntaxHighlighting(editorHighlightStyle),
      bracketMatching(),
      foldGutter({ markerDOM: createFoldMarker }),
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
    <svg className="editor-expand-icon" viewBox="0 0 40 20" aria-hidden="true">
      {isExpanded ? (
        <>
          <path d="M3 10h12M15 10l-5-5M15 10l-5 5" />
          <path d="M37 10H25M25 10l5-5M25 10l5 5" />
        </>
      ) : (
        <>
          <path d="M3 10h12M3 10l8-8M3 10l8 8" />
          <path d="M37 10H25M37 10l-8-8M37 10l-8 8" />
        </>
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

export function CodeEditor({ starterCode, isExpanded, onToggleExpansion, onCustomInput, onRun, onSubmit }) {
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
    const view = viewRef.current
    if (!view) return
    const language = activeLanguageRef.current
    view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: starterCode[language] } })
    sessionsRef.current[language] = view.state
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
            <select aria-label="Editor language" value={selectedLanguage} onChange={(event) => setSelectedLanguage(event.target.value)}>
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
        <button type="button" className="code-editor-button code-editor-expand" aria-label={isExpanded ? 'Collapse editor' : 'Expand editor'} aria-expanded={isExpanded} onClick={onToggleExpansion}>
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
