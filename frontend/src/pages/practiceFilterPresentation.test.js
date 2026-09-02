import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { fileURLToPath } from 'node:url'
import {
  DIFFICULTY_OPTIONS,
  formatDifficultyLabel,
  formatTagLabel,
  getPracticeAnalytics,
} from './practiceFilterPresentation.js'

const practiceSource = readFileSync(fileURLToPath(new URL('./Practice.jsx', import.meta.url)), 'utf8')
const practiceFiltersCss = readFileSync(fileURLToPath(new URL('./PracticeFilters.css', import.meta.url)), 'utf8')
const appCss = readFileSync(fileURLToPath(new URL('../App.css', import.meta.url)), 'utf8')

test('always exposes all supported difficulty options independently of problem data', () => {
  assert.deepEqual(DIFFICULTY_OPTIONS, ['EASY', 'MEDIUM', 'HARD'])
  assert.deepEqual(DIFFICULTY_OPTIONS.map(formatDifficultyLabel), ['Easy', 'Medium', 'Hard'])
  assert.match(practiceSource, /DIFFICULTY_OPTIONS\.map\(\(difficulty\)/)
  assert.doesNotMatch(practiceSource, /problems\.map\(\(problem\) => problem\.difficulty\)/)
})

test('formats tag labels without changing canonical values used for filtering', () => {
  assert.equal(formatTagLabel('ARRAY SCAN'), 'Array Scan')
  assert.equal(formatTagLabel('Bottom-Up DP'), 'Bottom-Up DP')
  assert.equal(formatTagLabel('canonical key'), 'Canonical Key')
  assert.match(practiceSource, /selectedTags\.includes\(tag\)/)
  assert.match(practiceSource, /problem\.tags\.includes\(tag\)/)
})

test('calculates Practice analytics from the loaded problem data', () => {
  const problems = [{ solved: true }, { solved: false }, { solved: true }, { solved: false }]
  assert.deepEqual(getPracticeAnalytics(problems), {
    total: 4, completed: 2, remaining: 2, percentage: 50,
  })
  assert.deepEqual(getPracticeAnalytics([]), {
    total: 0, completed: 0, remaining: 0, percentage: 0,
  })
  assert.deepEqual(getPracticeAnalytics([{ solved: true }, { solved: true }]), {
    total: 2, completed: 2, remaining: 0, percentage: 100,
  })
})

test('uses the Practice title without the redundant eyebrow', () => {
  assert.match(practiceSource, /<h1>Practice<\/h1>/)
  assert.doesNotMatch(practiceSource, /<p className="eyebrow">Practice<\/p>/)
})

test('preserves difficulty and tag filter semantics', () => {
  assert.match(practiceSource, /selectedDifficulty && problem\.difficulty !== selectedDifficulty/)
  assert.match(practiceSource, /selectedTags\.every\(\(tag\) => problem\.tags\.includes\(tag\)\)/)
})

test('gives selected tag pills a non-clipping line box', () => {
  const selectedTagStyles = practiceFiltersCss.slice(
    practiceFiltersCss.indexOf('.practice-selected-tag,'),
    practiceFiltersCss.indexOf('\n}', practiceFiltersCss.indexOf('.practice-selected-tag,')),
  )
  assert.match(selectedTagStyles, /line-height:\s*1\.35/)
  assert.match(selectedTagStyles, /align-items:\s*center/)
})

test('keeps tag menu geometry and uses grid-track sizing for complete option rows', () => {
  const tagMenuStyles = appCss.slice(
    appCss.indexOf('.practice-tag-menu {'),
    appCss.indexOf('\n}', appCss.indexOf('.practice-tag-menu {')),
  )
  const tagOptionStyles = practiceFiltersCss.slice(
    practiceFiltersCss.indexOf('.practice-filter-group .practice-tag-option {'),
    practiceFiltersCss.indexOf('\n}', practiceFiltersCss.indexOf('.practice-filter-group .practice-tag-option {')),
  )
  assert.match(tagMenuStyles, /padding:\s*10px/)
  assert.match(practiceFiltersCss, /\.practice-filter-group \.practice-tag-option \{/) 
  assert.match(tagOptionStyles, /padding:\s*6px 16px/)
  assert.doesNotMatch(practiceFiltersCss, /(^|\n)\.practice-tag-option \{/) 
  assert.match(tagOptionStyles, /justify-self:\s*stretch/)
  assert.match(tagOptionStyles, /width:\s*auto/)
  assert.doesNotMatch(tagOptionStyles, /width:\s*100%/)
  assert.match(practiceFiltersCss, /\.practice-main \.practice-tag-option:hover,\s*\n\.practice-main \.practice-tag-option\.is-selected,/) 
})

test('scopes the themed scrollbar to the tag options scroller', () => {
  const tagOptionsStyles = practiceFiltersCss.slice(
    practiceFiltersCss.indexOf('.practice-tag-options {'),
    practiceFiltersCss.indexOf('.practice-tag-option > span {'),
  )
  assert.match(tagOptionsStyles, /scrollbar-width:\s*thin/)
  assert.match(tagOptionsStyles, /scrollbar-color:\s*var\(--practice-accent\) transparent/)
  assert.match(tagOptionsStyles, /\.practice-tag-options::-webkit-scrollbar \{[\s\S]*width:\s*8px/)
  assert.match(tagOptionsStyles, /\.practice-tag-options::-webkit-scrollbar-thumb \{[\s\S]*border-radius:\s*999px/)
  assert.match(tagOptionsStyles, /\.practice-tag-options::-webkit-scrollbar-thumb:hover \{[\s\S]*var\(--practice-accent-hover\)/)
  assert.doesNotMatch(practiceFiltersCss, /(^|\n)\s*::-webkit-scrollbar\s*\{/)
})

test('keeps Practice topic and problem hierarchy within the blue theme', () => {
  const topicHeadingStyles = appCss.slice(
    appCss.indexOf('.practice-topic-heading {'),
    appCss.indexOf('\n}', appCss.indexOf('.practice-topic-heading {')),
  )
  const topicTitleStyles = appCss.slice(
    appCss.indexOf('.practice-topic-heading h2 {'),
    appCss.indexOf('\n}', appCss.indexOf('.practice-topic-heading h2 {')),
  )
  const problemRowStyles = appCss.slice(
    appCss.indexOf('.practice-problem-row {'),
    appCss.indexOf('\n}', appCss.indexOf('.practice-problem-row {')),
  )
  const problemTitleStyles = appCss.slice(
    appCss.indexOf('.practice-problem-title {'),
    appCss.indexOf('\n}', appCss.indexOf('.practice-problem-title {')),
  )

  assert.match(topicHeadingStyles, /background:\s*var\(--panel-raised\)/)
  assert.match(topicTitleStyles, /color:\s*var\(--text\)/)
  assert.match(topicTitleStyles, /font-weight:\s*800/)
  assert.match(problemRowStyles, /background:\s*var\(--surface\)/)
  assert.match(problemRowStyles, /color:\s*var\(--text-soft\)/)
  assert.match(problemTitleStyles, /color:\s*color-mix\(in srgb, var\(--text\) 82%, var\(--text-soft\)\)/)
  assert.match(appCss, /\.practice-topic-heading:hover, \.practice-topic-heading:focus-visible \{ background: var\(--panel-raised\); \}/)
  assert.match(appCss, /\.practice-problem-row:hover, \.practice-problem-row:focus-visible \{ background: var\(--panel-raised\); \}/)
})

test('preserves Practice difficulty, tag, solved, and completion styling', () => {
  assert.match(appCss, /\.practice-problem-status\.is-solved \{ color: var\(--green\); font-weight: var\(--font-weight-bold\); \}/)
  assert.match(appCss, /\.difficulty-easy \{ color: var\(--green\); \}/)
  assert.match(appCss, /\.difficulty-medium \{ color: #f2c667; \}/)
  assert.match(appCss, /\.difficulty-hard \{ color: #ff7777; \}/)
  assert.match(appCss, /\.practice-problem-tag \{[\s\S]*?color: var\(--text-muted\);/)
  assert.match(appCss, /\.practice-topic-section\.is-complete \{ border-color: #567641; \}/)
})

test('indents Practice problem rows without changing their right padding', () => {
  const problemRowStyles = appCss.slice(
    appCss.indexOf('.practice-problem-row {'),
    appCss.indexOf('\n}', appCss.indexOf('.practice-problem-row {')),
  )

  assert.match(problemRowStyles, /padding:\s*10px 22px 10px 36px/)
})

test('keeps the two filter controls mutually exclusive and dismissible outside their boundaries', () => {
  assert.match(practiceSource, /document\.addEventListener\('mousedown', handlePointerDown\)/)
  assert.match(practiceSource, /!difficultyMenuRef\.current\?\.contains\(event\.target\)/)
  assert.match(practiceSource, /!tagMenuRef\.current\?\.contains\(event\.target\)/)
  assert.match(practiceSource, /setIsTagMenuOpen\(false\)/)
  assert.match(practiceSource, /setIsDifficultyMenuOpen\(false\)/)
})
