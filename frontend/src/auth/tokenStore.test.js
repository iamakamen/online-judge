import assert from 'node:assert/strict'
import { test } from 'node:test'

class MemoryStorage {
  constructor(initial = {}) {
    this.values = new Map(Object.entries(initial))
  }

  getItem(key) {
    return this.values.get(key) ?? null
  }

  setItem(key, value) {
    this.values.set(key, String(value))
  }

  removeItem(key) {
    this.values.delete(key)
  }
}

class FakeBroadcastChannel {
  static instances = []

  constructor() {
    this.messages = []
    FakeBroadcastChannel.instances.push(this)
  }

  postMessage(message) {
    this.messages.push(message)
  }
}

test('cross-tab predecessor failure can adopt a rotated token and logout clears storage', async () => {
  const sessionStorage = new MemoryStorage({ 'oj.auth.refresh-token': 'R1' })
  globalThis.window = {
    sessionStorage,
    setTimeout,
    clearTimeout,
  }
  globalThis.BroadcastChannel = FakeBroadcastChannel

  const store = await import(`./tokenStore.js?rotation-test=${Date.now()}`)
  const channel = FakeBroadcastChannel.instances.at(-1)

  const waitingForReplacement = store.requestSharedSession(100, 'R1')
  assert.deepEqual(channel.messages, [{ type: 'request-session' }])

  channel.onmessage({ data: { type: 'session', refreshToken: 'R2' } })
  assert.equal(await waitingForReplacement, true)
  assert.deepEqual(store.getTokens(), { accessToken: null, refreshToken: 'R2' })
  assert.equal(sessionStorage.getItem('oj.auth.refresh-token'), 'R2')

  channel.onmessage({ data: { type: 'logout' } })
  assert.equal(store.getTokens(), null)
  assert.equal(sessionStorage.getItem('oj.auth.refresh-token'), null)
})

test('automatic local cleanup does not broadcast logout or use localStorage', async () => {
  const sessionStorage = new MemoryStorage()
  globalThis.window = {
    sessionStorage,
    localStorage: new Proxy({}, {
      get() {
        throw new Error('localStorage must not be accessed')
      },
    }),
    setTimeout,
    clearTimeout,
  }
  globalThis.BroadcastChannel = FakeBroadcastChannel

  const store = await import(`./tokenStore.js?cleanup-test=${Date.now()}`)
  const channel = FakeBroadcastChannel.instances.at(-1)
  store.setTokens({ accessToken: 'A', refreshToken: 'R' })
  channel.messages.length = 0

  store.clearTokens({ broadcast: false })
  assert.equal(store.getTokens(), null)
  assert.deepEqual(channel.messages, [])
})

test('explicit local logout ignores later session messages', async () => {
  const sessionStorage = new MemoryStorage({ 'oj.auth.refresh-token': 'R1' })
  globalThis.window = {
    sessionStorage,
    setTimeout,
    clearTimeout,
  }
  globalThis.BroadcastChannel = FakeBroadcastChannel

  const store = await import(`./tokenStore.js?logout-order-test=${Date.now()}`)
  const channel = FakeBroadcastChannel.instances.at(-1)
  store.setTokens({ accessToken: 'A', refreshToken: 'R1' })
  store.clearTokens()

  channel.onmessage({ data: { type: 'session', refreshToken: 'R2' } })
  assert.equal(store.getTokens(), null)
  assert.equal(sessionStorage.getItem('oj.auth.refresh-token'), null)
})
