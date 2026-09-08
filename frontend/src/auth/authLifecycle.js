export const AUTH_STATES = Object.freeze({
  AUTHENTICATED: 'authenticated',
  RESTORING: 'restoring',
  TEMPORARILY_UNAVAILABLE: 'temporarily_unavailable',
  UNAUTHENTICATED: 'unauthenticated',
})

export function initialAuthState() {
  return AUTH_STATES.RESTORING
}

export function isAuthenticatedState(state) {
  return state === AUTH_STATES.AUTHENTICATED
}

export function createAuthGeneration() {
  let generation = 0

  return {
    current() {
      return generation
    },
    invalidate() {
      generation += 1
      return generation
    },
    isCurrent(candidate) {
      return candidate === generation
    },
  }
}

export class StaleAuthOperationError extends Error {
  constructor() {
    super('Authentication operation is no longer current')
    this.name = 'StaleAuthOperationError'
  }
}
