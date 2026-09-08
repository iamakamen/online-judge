import { createContext, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { ApiError, login as loginRequest, logout as logoutRequest, refresh } from '../api/client'
import { clearTokens, getTokens, getUserId, requestSharedSession, setTokens, subscribe } from './tokenStore'
import {
  AUTH_STATES,
  StaleAuthOperationError,
  createAuthGeneration,
  initialAuthState,
  isAuthenticatedState,
} from './authLifecycle'
import { createSingleFlight, isTransientRefreshError } from './refreshPolicy'

const AuthContext = createContext(null)

function tokenPayload(payload) {
  return {
    accessToken: payload.access_token,
    refreshToken: payload.refresh_token,
  }
}

export function AuthProvider({ children }) {
  const [_tokens, setAuthTokens] = useState(getTokens)
  const [authStatus, setAuthStatus] = useState(initialAuthState)
  const authGenerationRef = useRef(createAuthGeneration())
  const refreshSingleFlightRef = useRef(createSingleFlight())

  const updateTokens = useCallback((payload, expectedGeneration = null) => {
    if (expectedGeneration !== null && !authGenerationRef.current.isCurrent(expectedGeneration)) return null
    const nextTokens = tokenPayload(payload)
    setTokens(nextTokens)
    setAuthTokens(nextTokens)
    setAuthStatus(AUTH_STATES.AUTHENTICATED)
    return nextTokens
  }, [])

  const login = useCallback(async (identifier, password) => {
    const generation = authGenerationRef.current.invalidate()
    return updateTokens(await loginRequest(identifier, password), generation)
  }, [updateTokens])

  const authenticate = useCallback((payload) => {
    const generation = authGenerationRef.current.invalidate()
    return updateTokens(payload, generation)
  }, [updateTokens])

  const refreshSession = useCallback(() => refreshSingleFlightRef.current(async () => {
    const currentTokens = getTokens()
    if (!currentTokens?.refreshToken) throw new ApiError(401, 'Authentication required')
    const generation = authGenerationRef.current.current()
    const attemptedRefreshToken = currentTokens.refreshToken
    let refreshToken = attemptedRefreshToken
    let lastError

    for (let attempt = 0; attempt < 3; attempt += 1) {
      try {
        const nextTokens = updateTokens(await refresh(refreshToken), generation)
        if (!nextTokens) throw new StaleAuthOperationError()
        return nextTokens
      } catch (error) {
        if (!authGenerationRef.current.isCurrent(generation)) throw new StaleAuthOperationError()
        lastError = error
        const currentRefreshToken = getTokens()?.refreshToken
        if (currentRefreshToken && currentRefreshToken !== refreshToken) {
          refreshToken = currentRefreshToken
          continue
        }

        await requestSharedSession(1500, refreshToken)
        const sharedRefreshToken = getTokens()?.refreshToken
        if (sharedRefreshToken && sharedRefreshToken !== refreshToken) {
          refreshToken = sharedRefreshToken
          continue
        }

        if (!isTransientRefreshError(error)) break
      }
    }

    if (!authGenerationRef.current.isCurrent(generation)) throw new StaleAuthOperationError()
    if (!isTransientRefreshError(lastError)) {
      clearTokens({ broadcast: false })
      setAuthTokens(null)
      setAuthStatus(AUTH_STATES.UNAUTHENTICATED)
    } else {
      setAuthStatus(AUTH_STATES.TEMPORARILY_UNAVAILABLE)
    }
    throw lastError
  }), [updateTokens])

  const requestAuthenticated = useCallback(async (requestFunction) => {
    const currentTokens = getTokens()
    if (!currentTokens?.accessToken) {
      const nextTokens = await refreshSession()
      return requestFunction(nextTokens.accessToken)
    }

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
    authGenerationRef.current.invalidate()
    clearTokens()
    setAuthTokens(null)
    setAuthStatus(AUTH_STATES.UNAUTHENTICATED)
    try {
      if (currentTokens?.refreshToken) await logoutRequest(currentTokens.refreshToken)
    } catch { /* Local logout remains effective if the server is unavailable. */ }
  }, [])

  useEffect(() => {
    const unsubscribe = subscribe(() => {
      const nextTokens = getTokens()
      if (!nextTokens) {
        authGenerationRef.current.invalidate()
        setAuthTokens(null)
        setAuthStatus(AUTH_STATES.UNAUTHENTICATED)
        return
      }
      setAuthTokens(nextTokens)
    })
    let active = true

    async function restoreSession() {
      if (!getTokens()?.refreshToken) await requestSharedSession()
      if (!getTokens()?.refreshToken) {
        if (active) setAuthStatus(AUTH_STATES.UNAUTHENTICATED)
        return
      }
      try {
        await refreshSession()
      } catch {
        // refreshSession records definitive and transient outcomes.
      }
    }

    if (!getTokens()?.accessToken) restoreSession()
    else setAuthStatus(AUTH_STATES.AUTHENTICATED)
    return () => {
      active = false
      unsubscribe()
    }
  }, [refreshSession])

  const retryAuthentication = useCallback(async () => {
    setAuthStatus(AUTH_STATES.RESTORING)
    return refreshSession()
  }, [refreshSession])

  const userId = getUserId()
  const value = useMemo(() => ({
    isAuthenticated: isAuthenticatedState(authStatus),
    userId,
    isLoading: authStatus === AUTH_STATES.RESTORING,
    authStatus,
    login,
    authenticate,
    logout,
    retryAuthentication,
    requestAuthenticated,
  }), [authStatus, authenticate, login, logout, requestAuthenticated, retryAuthentication, userId])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export { AuthContext }
