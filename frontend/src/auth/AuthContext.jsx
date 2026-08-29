import { createContext, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { ApiError, login as loginRequest, logout as logoutRequest, refresh } from '../api/client'
import { clearTokens, getTokens, getUserId, requestSharedSession, setTokens, subscribe } from './tokenStore'

const AuthContext = createContext(null)

function tokenPayload(payload) {
  return {
    accessToken: payload.access_token,
    refreshToken: payload.refresh_token,
  }
}

export function AuthProvider({ children }) {
  const [tokens, setAuthTokens] = useState(getTokens)
  const [isLoading, setIsLoading] = useState(() => !getTokens()?.accessToken)
  const refreshInFlightRef = useRef(null)

  const updateTokens = useCallback((payload) => {
    const nextTokens = tokenPayload(payload)
    setTokens(nextTokens)
    setAuthTokens(nextTokens)
    return nextTokens
  }, [])

  const login = useCallback(async (identifier, password) => {
    return updateTokens(await loginRequest(identifier, password))
  }, [updateTokens])

  const refreshSession = useCallback(async () => {
    if (refreshInFlightRef.current) return refreshInFlightRef.current
    const currentTokens = getTokens()
    if (!currentTokens?.refreshToken) throw new ApiError(401, 'Authentication required')
    const attemptedRefreshToken = currentTokens.refreshToken
    refreshInFlightRef.current = (async () => {
      let refreshToken = attemptedRefreshToken
      let lastError
      try {
        for (let attempt = 0; attempt < 3; attempt += 1) {
          try {
            return updateTokens(await refresh(refreshToken))
          } catch (error) {
            lastError = error
            const currentRefreshToken = getTokens()?.refreshToken
            if (currentRefreshToken && currentRefreshToken !== refreshToken) {
              refreshToken = currentRefreshToken
              continue
            }

            await requestSharedSession(500, refreshToken)
            const sharedRefreshToken = getTokens()?.refreshToken
            if (sharedRefreshToken && sharedRefreshToken !== refreshToken) {
              refreshToken = sharedRefreshToken
              continue
            }
            break
          }
        }

        // No tab produced a replacement token, so this is a genuine refresh
        // failure and the existing logout semantics apply.
        clearTokens()
        setAuthTokens(null)
        throw lastError
      } finally {
        refreshInFlightRef.current = null
      }
    })()
    return refreshInFlightRef.current
  }, [updateTokens])

  const requestAuthenticated = useCallback(async (requestFunction) => {
    const currentTokens = getTokens()
    if (!currentTokens?.accessToken) throw new ApiError(401, 'Authentication required')

    try {
      return await requestFunction(currentTokens.accessToken)
    } catch (error) {
      if (!(error instanceof ApiError) || error.status !== 401) throw error
      const nextTokens = await refreshSession()
      return requestFunction(nextTokens.accessToken)
    }
  }, [refreshSession])

  const logout = useCallback(async () => {
    const currentTokens = getTokens()
    try {
      if (currentTokens?.refreshToken) await logoutRequest(currentTokens.refreshToken)
    } finally {
      clearTokens()
      setAuthTokens(null)
    }
  }, [])

  useEffect(() => {
    const unsubscribe = subscribe(() => setAuthTokens(getTokens()))
    let active = true

    async function restoreSession() {
      if (!getTokens()?.refreshToken) await requestSharedSession()
      if (!getTokens()?.refreshToken) {
        if (active) setIsLoading(false)
        return
      }
      try {
        await refreshSession()
      } catch {
        // refreshSession clears invalid or expired refresh credentials.
      } finally {
        if (active) setIsLoading(false)
      }
    }

    if (!getTokens()?.accessToken) restoreSession()
    else setIsLoading(false)
    return () => {
      active = false
      unsubscribe()
    }
  }, [refreshSession])

  const userId = getUserId()
  const value = useMemo(() => ({
    isAuthenticated: Boolean(tokens?.accessToken),
    userId,
    isLoading,
    login,
    logout,
    requestAuthenticated,
  }), [isLoading, login, logout, requestAuthenticated, tokens, userId])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export { AuthContext }
