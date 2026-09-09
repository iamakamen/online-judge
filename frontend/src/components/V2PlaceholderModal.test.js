import { readFileSync } from 'node:fs'
import { test } from 'node:test'
import assert from 'node:assert/strict'

const modalSource = readFileSync(new URL('./V2PlaceholderModal.jsx', import.meta.url), 'utf8')
const appSource = readFileSync(new URL('../App.jsx', import.meta.url), 'utf8')
const dashboardSource = readFileSync(new URL('../pages/Dashboard.jsx', import.meta.url), 'utf8')
const problemPageSource = readFileSync(new URL('../pages/ProblemPage.jsx', import.meta.url), 'utf8')

test('Forgot Password uses the isolated authentication modal presentation', () => {
  assert.match(appSource, /feature="Forgot Password"/)
  assert.match(appSource, /theme="auth"/)
  assert.match(modalSource, /theme = 'default'/)
  assert.match(modalSource, /theme === 'auth' \? ' modal-auth' : ''/)
})

test('Dashboard V2 popups retain the default presentation and close callback', () => {
  assert.match(dashboardSource, /<V2PlaceholderModal feature=\{modalItem\} onClose=\{\(\) => setModalItem\(null\)\} \/>/)
  assert.match(modalSource, /onClick=\{onClose\}/)
  assert.match(modalSource, /onClick=\{\(event\) => event\.stopPropagation\(\)\}/)
  assert.doesNotMatch(dashboardSource, /theme="auth"/)
})

test('Problem Page Submissions uses the shared V2 illustration without a symbol', () => {
  assert.match(problemPageSource, /import \{ V2PlaceholderModal \} from '\.\.\/components\/V2PlaceholderModal'/)
  assert.match(problemPageSource, /<V2PlaceholderModal[\s\S]*feature=\{v2Feature \|\| 'Submissions'\}[\s\S]*titleId="problem-future-feature-title"/)
  assert.match(modalSource, /\{\['Learn', 'Contest', 'Forum', 'Profile'\]\.includes\(feature\) && <FeatureIcon feature=\{feature\} \/>\}/)
  assert.match(modalSource, /<WorkProgressIllustration \/>/)
  assert.doesNotMatch(problemPageSource, /problem-future-feature-title"\}>\{v2Feature \|\| 'Submissions'\}<\/h2>/)
})
