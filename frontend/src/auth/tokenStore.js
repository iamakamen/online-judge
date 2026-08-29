const REFRESH_TOKEN_STORAGE_KEY = 'oj.auth.refresh-token'
const subscribers = new Set()
const authChannel = typeof BroadcastChannel !== 'undefined'
  ? new BroadcastChannel('oj-authentication')
  : null

function storedRefreshToken() {
  try { return window.sessionStorage.getItem(REFRESH_TOKEN_STORAGE_KEY) } catch { return null }
}

function notify() {
  subscribers.forEach((subscriber) => subscriber())
}

let tokens = storedRefreshToken()
  ? { accessToken: null, refreshToken: storedRefreshToken() }
  : null

if (authChannel) {
  authChannel.onmessage = (event) => {
    if (event.data?.type === 'request-session' && tokens?.refreshToken) {
      authChannel.postMessage({ type: 'session', refreshToken: tokens.refreshToken })
      return
    }
    if (event.data?.type === 'session' && event.data.refreshToken) {
      tokens = { accessToken: tokens?.accessToken || null, refreshToken: event.data.refreshToken }
      notify()
    }
    if (event.data?.type === 'logout') {
      tokens = null
      notify()
    }
  }
}

export function getTokens() {
  return tokens
}

export function setTokens(nextTokens) {
  tokens = nextTokens
  try {
    if (nextTokens?.refreshToken) window.sessionStorage.setItem(REFRESH_TOKEN_STORAGE_KEY, nextTokens.refreshToken)
    else window.sessionStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY)
  } catch { /* Browser storage is optional. */ }
  if (authChannel && nextTokens?.refreshToken) {
    authChannel.postMessage({ type: 'session', refreshToken: nextTokens.refreshToken })
  }
  notify()
}

export function clearTokens() {
  tokens = null
  try { window.sessionStorage.removeItem(REFRESH_TOKEN_STORAGE_KEY) } catch { /* Browser storage is optional. */ }
  if (authChannel) authChannel.postMessage({ type: 'logout' })
  notify()
}

export function subscribe(subscriber) {
  subscribers.add(subscriber)
  return () => subscribers.delete(subscriber)
}

export function requestSharedSession(timeoutMs = 300, previousRefreshToken = null) {
  if (!authChannel) return Promise.resolve(false)
  return new Promise((resolve) => {
    let settled = false
    const unsubscribe = subscribe(() => {
      const refreshToken = getTokens()?.refreshToken
      if (!refreshToken || settled || refreshToken === previousRefreshToken) return
      settled = true
      unsubscribe()
      resolve(true)
    })
    const timeoutId = window.setTimeout(() => {
      if (settled) return
      settled = true
      unsubscribe()
      resolve(false)
    }, timeoutMs)
    const originalResolve = resolve
    resolve = (value) => {
      window.clearTimeout(timeoutId)
      originalResolve(value)
    }
    authChannel.postMessage({ type: 'request-session' })
  })
}

export function getUserId() {
  const token = tokens?.accessToken
  if (!token) return null
  try {
    const encodedPayload = token.split('.')[1]
    if (!encodedPayload) return null
    const payload = JSON.parse(atob(encodedPayload.replace(/-/g, '+').replace(/_/g, '/')))
    const userId = Number(payload.sub)
    return Number.isInteger(userId) && userId > 0 ? userId : null
  } catch {
    return null
  }
}
