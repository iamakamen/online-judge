import assert from 'node:assert/strict'
import { test } from 'node:test'
import { ApiError, completeRegistration, getRegistrationStatus, startRegistration } from './client.js'

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

test('registration client preserves server-derived request metadata', async () => {
  globalThis.fetch = async () => response(202, {
    status: 'otp_sent',
    message: 'Verification code sent to your email.',
    cooldown_seconds: 120,
    remaining_requests: 4,
  })
  const result = await startRegistration('Jane', 'Doe', 'jane@example.com')
  assert.deepEqual(result, {
    status: 'otp_sent',
    message: 'Verification code sent to your email.',
    cooldown_seconds: 120,
    remaining_requests: 4,
  })
})

test('registration completion relies on the HttpOnly verification cookie', async () => {
  let requestBody
  globalThis.fetch = async (_path, options) => {
    requestBody = JSON.parse(options.body)
    return response(200, { status: 'registration_complete' })
  }
  await completeRegistration('jane@example.com', 'janedoe1', 'longenough1A!', 'longenough1A!')
  assert.equal(requestBody.verification_proof, undefined)
})

test('registration requests include credentials for the HttpOnly proof cookie', async () => {
  let requestOptions
  globalThis.fetch = async (_path, options) => {
    requestOptions = options
    return response(200, { status: 'email_verified', email: 'jane@example.com' })
  }
  await getRegistrationStatus()
  assert.equal(requestOptions.credentials, 'include')
})

test('registration client preserves stable policy error codes', async () => {
  globalThis.fetch = async () => response(400, {
    detail: { code: 'otp_superseded', message: 'This verification code is no longer valid because a newer code was requested.' },
  })
  await assert.rejects(
    () => startRegistration('Jane', 'Doe', 'jane@example.com'),
    (error) => error.code === 'otp_superseded' && error.message.includes('newer code'),
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
