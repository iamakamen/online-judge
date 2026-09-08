export function isTransientRefreshError(error) {
  if (!error) return false
  if (error.code === 'NETWORK_ERROR' || error.status === null) return true
  return error.status === 408
    || error.status === 425
    || error.status === 429
    || error.status >= 500
}

export function createSingleFlight() {
  let inFlight = null

  return (operation) => {
    if (inFlight) return inFlight

    const promise = Promise.resolve().then(operation)
    inFlight = promise
    promise.then(
      () => { if (inFlight === promise) inFlight = null },
      () => { if (inFlight === promise) inFlight = null },
    )
    return promise
  }
}
