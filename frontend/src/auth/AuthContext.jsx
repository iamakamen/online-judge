import { createContext, useMemo, useState } from 'react'
import { ApiError, login as loginRequest, logout as logoutRequest, refresh } from '../api/client'
import { clearTokens, getTokens, setTokens } from './tokenStore'

const AuthContext = createContext(null)

function tokenPayload(payload) {
  return {
    accessToken: payload.access_token,
    refreshToken: payload.refresh_token,
  }
}

export function AuthProvider({ children }) {
  const [tokens, setAuthTokens] = useState(getTokens)

  function updateTokens(payload) {
    const nextTokens = tokenPayload(payload)
    setTokens(nextTokens)
    setAuthTokens(nextTokens)
    return nextTokens
  }

  async function login(identifier, password) {
    return updateTokens(await loginRequest(identifier, password))
  }

  async function refreshSession() {
    const currentTokens = getTokens()
    if (!currentTokens?.refreshToken) throw new ApiError(401, 'Authentication required')
    try {
      return updateTokens(await refresh(currentTokens.refreshToken))
    } catch (error) {
      clearTokens()
      setAuthTokens(null)
      throw error
    }
  }

  async function requestAuthenticated(requestFunction) {
    const currentTokens = getTokens()
    if (!currentTokens?.accessToken) throw new ApiError(401, 'Authentication required')

    try {
      return await requestFunction(currentTokens.accessToken)
    } catch (error) {
      if (!(error instanceof ApiError) || error.status !== 401) throw error
      const nextTokens = await refreshSession()
      return requestFunction(nextTokens.accessToken)
    }
  }

  async function logout() {
    const currentTokens = getTokens()
    try {
      if (currentTokens?.refreshToken) await logoutRequest(currentTokens.refreshToken)
    } finally {
      clearTokens()
      setAuthTokens(null)
    }
  }

  const value = useMemo(() => ({
    isAuthenticated: Boolean(tokens?.accessToken),
    isLoading: false,
    login,
    logout,
    requestAuthenticated,
  }), [tokens])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export { AuthContext }
