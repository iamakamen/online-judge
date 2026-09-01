import assert from 'node:assert/strict'
import { test } from 'node:test'
import { ApiError, startRegistration } from './client.js'

function response(status, payload, headers = {}) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: new Headers(headers),
    json: async () => payload,
  }
}

async function rejectsWith(status, payload, headers = {}) {
  globalThis.fetch = async () => response(status, payload, headers)
  return assert.rejects(
    () => startRegistration('Jane', 'Doe', 'jane@example.com'),
    (error) => error instanceof ApiError && error.status === status,
  )
}

test('registration client preserves backend detail and Retry-After metadata', async () => {
  globalThis.fetch = async () => response(429, { detail: 'Please wait 119 seconds before requesting another code' }, { 'Retry-After': '119' })
  await assert.rejects(
    () => startRegistration('Jane', 'Doe', 'jane@example.com'),
    (error) => error.status === 429
      && error.detail === 'Please wait 119 seconds before requesting another code'
      && error.retryAfter === '119'
      && error.endpoint === '/auth/register/start',
  )
})

test('registration client preserves each expected HTTP failure status', async () => {
  await rejectsWith(429, { detail: 'OTP request limit exceeded' })
  await rejectsWith(400, { detail: 'Registration session not found' })
  await rejectsWith(422, { detail: [{ msg: 'Enter a valid email address' }] })
  await rejectsWith(500, { detail: 'Internal Server Error' })
})

test('registration client represents network failures separately', async () => {
  globalThis.fetch = async () => { throw new TypeError('Failed to fetch') }
  await assert.rejects(
    () => startRegistration('Jane', 'Doe', 'jane@example.com'),
    (error) => error instanceof ApiError && error.code === 'NETWORK_ERROR' && error.status === null,
  )
})

test('registration client handles malformed error payloads without losing status', async () => {
  globalThis.fetch = async () => ({
    ok: false,
    status: 500,
    headers: new Headers(),
    json: async () => { throw new SyntaxError('invalid JSON') },
  })
  await assert.rejects(
    () => startRegistration('Jane', 'Doe', 'jane@example.com'),
    (error) => error.status === 500 && error.message === 'Request failed',
  )
})
