const SUPERSCRIPTS = {
  0: '⁰',
  1: '¹',
  2: '²',
  3: '³',
  4: '⁴',
  5: '⁵',
  6: '⁶',
  7: '⁷',
  8: '⁸',
  9: '⁹',
}

function normalizeConstraintText(text) {
  return text
    .replace(/(\d+)\^([0-9]+)/g, (_, number, exponent) => (
      `${number}${[...exponent].map((digit) => SUPERSCRIPTS[digit]).join('')}`
    ))
    .replace(/\s*(<=|>=|==|!=|≤|≥|<|>)(?!=)\s*/g, (_, operator) => {
      const symbols = { '<=': '≤', '>=': '≥', '==': '=', '!=': '≠' }
      return ` ${symbols[operator] || operator} `
    })
    .replace(/\s+/g, ' ')
    .trim()
}

function removeSentenceTerminalPeriod(text) {
  if (!text.endsWith('.')) return text
  return text.slice(0, -1)
}

function splitTopLevel(text, separator) {
  const parts = []
  let start = 0
  let inCode = false

  for (let index = 0; index < text.length; index += 1) {
    if (text[index] === '`') {
      inCode = !inCode
    } else if (!inCode && text[index] === separator) {
      parts.push(text.slice(start, index))
      start = index + 1
    }
  }

  parts.push(text.slice(start))
  return parts
}

function splitLegacyLines(text) {
  const lines = text.split(/\r?\n/).map((line) => line.trim()).filter(Boolean)
  if (lines.length <= 1) return lines

  const items = []
  for (const line of lines) {
    const previous = items.at(-1)
    const continuesPrevious = previous && (
      /\b(?:and|are|be|by|contains|for|from|in|is|of|only|or|that|the|to|with|within)\s*$/i.test(previous)
      || /[,：:]$/.test(previous)
      || /^[+*/]/.test(line)
    )

    if (items.length === 0 || !continuesPrevious) {
      items.push(line)
    } else {
      items[items.length - 1] = `${previous} ${line}`
    }
  }
  return items
}

function cleanConstraintItem(item) {
  return removeSentenceTerminalPeriod(normalizeConstraintText(item.replace(/`/g, '')))
}

export function normalizeConstraints(constraints) {
  if (constraints == null) return []

  const source = Array.isArray(constraints) ? constraints.join('\n') : String(constraints)
  const withoutLabel = source.replace(/^\s*-\s*\*\*Constraints:\*\*\s*/i, '')

  return splitTopLevel(withoutLabel, ';')
    .flatMap(splitLegacyLines)
    .map(cleanConstraintItem)
    .filter((item) => item && !/^[.]+$/.test(item))
}

export function formatConstraints(constraints) {
  return normalizeConstraints(constraints).join('\n')
}
