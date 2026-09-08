import assert from 'node:assert/strict'
import test from 'node:test'
import {
  createEntryId,
  createProblemPaneScrollKey,
  createScrollPositionStore,
  getHistoryEntryId,
  HISTORY_STATE_KEY,
} from './scrollRestoration.js'

test('creates unique application entry IDs', () => {
  const first = createEntryId()
  const second = createEntryId()

  assert.equal(typeof first, 'string')
  assert.equal(typeof second, 'string')
  assert.notEqual(first, second)
})

test('reads only application-owned history entry IDs', () => {
  const entryId = 'entry-a'

  assert.equal(getHistoryEntryId({ [HISTORY_STATE_KEY]: { entryId } }), entryId)
  assert.equal(getHistoryEntryId({}), null)
  assert.equal(getHistoryEntryId(null), null)
})

test('stores independent positions by key', () => {
  const positions = createScrollPositionStore()

  positions.set('entry-a', { x: 0, y: 800 })
  positions.set('entry-b', { x: 0, y: 300 })

  assert.deepEqual(positions.get('entry-a'), { x: 0, y: 800 })
  assert.deepEqual(positions.get('entry-b'), { x: 0, y: 300 })
  assert.equal(positions.get('missing'), null)
  assert.equal(positions.has('entry-a'), true)
})

test('scopes Problem Pane positions by history entry and slug', () => {
  assert.equal(
    createProblemPaneScrollKey('entry-a', 'problem-a'),
    'problem-pane-scroll:entry-a:problem-a',
  )
  assert.notEqual(
    createProblemPaneScrollKey('entry-a', 'problem-a'),
    createProblemPaneScrollKey('entry-b', 'problem-a'),
  )
  assert.notEqual(
    createProblemPaneScrollKey('entry-a', 'problem-a'),
    createProblemPaneScrollKey('entry-a', 'problem-b'),
  )
})
