export const DIFFICULTY_OPTIONS = ['EASY', 'MEDIUM', 'HARD']

export function getPracticeAnalytics(problems) {
  const total = problems.length
  const completed = problems.filter((problem) => problem.solved === true).length
  const remaining = total - completed
  const percentage = total === 0 ? 0 : Math.round((completed / total) * 100)

  return { total, completed, remaining, percentage }
}

export function formatDifficultyLabel(difficulty) {
  if (!difficulty) return ''
  return String(difficulty).charAt(0).toUpperCase() + String(difficulty).slice(1).toLowerCase()
}

export function formatTagLabel(tag) {
  return String(tag).trim().split(/(\s+)/).map((part) => {
    if (/\s+/.test(part)) return part
    return part.split('-').map((word) => {
      if (!word) return word
      if (word.length > 1 && word.length <= 3 && word === word.toUpperCase()) return word
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    }).join('-')
  }).join('')
}
