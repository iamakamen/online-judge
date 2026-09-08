export const HISTORY_STATE_KEY = '__onlineJudge'

export function createEntryId() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`
}

export function getHistoryEntryId(historyState) {
  return historyState?.[HISTORY_STATE_KEY]?.entryId ?? null
}

export function createProblemPaneScrollKey(entryId, problemSlug) {
  return `problem-pane-scroll:${entryId}:${problemSlug}`
}

export function createScrollPositionStore() {
  const positions = new Map()

  return {
    get(key) {
      return positions.get(key) ?? null
    },
    has(key) {
      return positions.has(key)
    },
    set(key, position) {
      positions.set(key, position)
    },
  }
}
