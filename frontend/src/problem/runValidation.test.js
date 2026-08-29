import assert from 'node:assert/strict'
import { test } from 'node:test'
import { resolveRunMode } from './runValidation.js'

test('public Run allows empty and whitespace-only input', () => {
  assert.equal(resolveRunMode('run_tests', ''), 'run_tests')
  assert.equal(resolveRunMode('run_tests', ' \n\t '), 'run_tests')
})

test('empty or whitespace-only custom input resolves to public Run', () => {
  assert.equal(resolveRunMode('custom_input', ''), 'run_tests')
  assert.equal(resolveRunMode('custom_input', ' \n\t '), 'run_tests')
})

test('non-empty custom input resolves to custom execution', () => {
  assert.equal(resolveRunMode('custom_input', '42\n'), 'custom_input')
})

test('Submit mode is not changed by Run mode resolution', () => {
  assert.equal(resolveRunMode('submit', ''), 'submit')
})
