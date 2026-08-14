const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export class ApiError extends Error {
  constructor(status, message) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request(path, options = {}) {
  const { accessToken, ...fetchOptions } = options
  const headers = new Headers(fetchOptions.headers || {})
  if (fetchOptions.body !== undefined) headers.set('Content-Type', 'application/json')
  if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`)

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...fetchOptions,
    headers,
    body: fetchOptions.body === undefined ? undefined : JSON.stringify(fetchOptions.body),
  })

  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    throw new ApiError(
      response.status,
      payload?.detail || payload?.message || 'Request failed',
    )
  }
  return payload
}

export function login(identifier, password) {
  return request('/auth/login', {
    method: 'POST',
    body: { identifier, password },
  })
}

export function refresh(refreshToken) {
  return request('/auth/refresh', {
    method: 'POST',
    body: { refresh_token: refreshToken },
  })
}

export function logout(refreshToken) {
  return request('/auth/logout', {
    method: 'POST',
    body: { refresh_token: refreshToken },
  })
}

export function getDashboard(accessToken) {
  return request('/api/v1/dashboard', { accessToken })
}
