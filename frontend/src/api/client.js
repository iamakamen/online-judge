const API_BASE_URL = import.meta.env?.VITE_API_BASE_URL || ''

export class ApiError extends Error {
  constructor(status, message, { endpoint = '', detail = null, headers = {}, code = '' } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.endpoint = endpoint
    this.detail = detail
    this.headers = headers
    this.retryAfter = headers['retry-after'] || null
    this.code = code
  }
}

function getErrorMessage(payload) {
  if (Array.isArray(payload?.detail)) {
    return payload.detail.map((item) => item.msg).filter(Boolean).join('. ') || 'Request failed'
  }
  return payload?.detail || payload?.message || 'Request failed'
}

async function request(path, options = {}) {
  const { accessToken, ...fetchOptions } = options
  const headers = new Headers(fetchOptions.headers || {})
  if (fetchOptions.body !== undefined) headers.set('Content-Type', 'application/json')
  if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`)

  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...fetchOptions,
      headers,
      body: fetchOptions.body === undefined ? undefined : JSON.stringify(fetchOptions.body),
    })
  } catch (error) {
    const networkError = new ApiError(null, error?.message || 'Network request failed', {
      endpoint: path,
      code: 'NETWORK_ERROR',
    })
    console.error('API request failed', { endpoint: path, status: null, detail: networkError.message, retryAfter: null })
    throw networkError
  }

  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    const responseHeaders = Object.fromEntries(response.headers.entries())
    const apiError = new ApiError(
      response.status,
      getErrorMessage(payload),
      { endpoint: path, detail: payload?.detail ?? null, headers: responseHeaders },
    )
    console.error('API request failed', {
      endpoint: path,
      status: apiError.status,
      detail: apiError.detail,
      retryAfter: apiError.retryAfter,
    })
    throw apiError
  }
  return payload
}

export function login(identifier, password) {
  return request('/auth/login', {
    method: 'POST',
    body: { identifier, password },
  })
}

export function startRegistration(firstName, lastName, email) {
  return request('/auth/register/start', {
    method: 'POST',
    body: { first_name: firstName, last_name: lastName, email },
  })
}

export function verifyRegistrationOtp(email, otp) {
  return request('/auth/register/verify-otp', {
    method: 'POST',
    body: { email, otp },
  })
}

export function completeRegistration(email, username, password, confirmPassword) {
  return request('/auth/register/complete', {
    method: 'POST',
    body: { email, username, password, confirm_password: confirmPassword },
  })
}

export function checkUsernameAvailability(username) {
  return request(`/auth/register/username-availability?username=${encodeURIComponent(username)}`)
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

export function getTopics(accessToken) {
  return request('/api/v1/topics', { accessToken })
}

export function getProblems(accessToken, {
  topicId,
  difficulty,
  tag,
  tags = [],
  page = 1,
  pageSize = 100,
} = {}) {
  const params = new URLSearchParams()
  if (topicId !== undefined && topicId !== null) params.set('topic_id', topicId)
  if (difficulty) params.set('difficulty', difficulty)
  if (tag) params.set('tag', tag)
  for (const selectedTag of tags) params.append('tags', selectedTag)
  params.set('page', page)
  params.set('page_size', pageSize)

  return request(`/api/v1/problems?${params.toString()}`, { accessToken })
}

export function getProblemBySlug(accessToken, slug) {
  return request(
    `/api/v1/problems/by-slug/${encodeURIComponent(slug)}`,
    { accessToken },
  )
}

export function getAcceptedSolutions(accessToken, problemId) {
  return request(`/api/v1/problems/${problemId}/accepted-solutions`, { accessToken })
}

export function runCode(accessToken, payload) {
  return request('/api/v1/run', {
    method: 'POST',
    accessToken,
    body: payload,
  })
}

export function createSubmission(accessToken, payload) {
  return request('/api/v1/submissions', {
    method: 'POST',
    accessToken,
    body: payload,
  })
}

export function getSubmission(accessToken, submissionId) {
  return request(`/api/v1/submissions/${submissionId}`, { accessToken })
}

export function requestAiHelp(accessToken, payload) {
  return request('/api/v1/ai/help', {
    method: 'POST',
    accessToken,
    body: payload,
  })
}
