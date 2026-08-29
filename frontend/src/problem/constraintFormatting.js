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

const SUBSCRIPTS = {
  i: 'ᵢ',
  j: 'ⱼ',
  k: 'ₖ',
}

function normalizeConstraintText(text) {
  return text
    .replace(/\b([A-Za-z]+)\[([ijk])\]/g, (_, name, index) => `${name}${SUBSCRIPTS[index]}`)
    .replace(/\bai\b/g, 'aᵢ')
    .replace(/\bpi\b/g, 'pᵢ')
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

function formatConstraintLine(text) {
  if (!text || /^[.]+$/.test(text)) return ''
  if (/(≤|≥|<|>|=)/.test(text)) return text.replace(/[.]+$/, '').trim()

  const sentence = text.replace(/[.!?]+$/, '').trim()
  if (!sentence) return ''
  return `${sentence.charAt(0).toUpperCase()}${sentence.slice(1)}.`
}

function expandSharedBounds(text) {
  return text.replace(
    /(-?\d+(?:[⁰¹²³⁴⁵⁶⁷⁸⁹]+)?)\s(≤|≥|<|>|=)\s([^,;]+?),\s*([^,;]+?)\s\2\s([^,;]+)/g,
    (_, lower, operator, firstVariable, secondVariable, upper) => (
      `${lower} ${operator} ${firstVariable} ${operator} ${upper}\n${lower} ${operator} ${secondVariable} ${operator} ${upper}`
    ),
  )
}

export function formatConstraints(constraints) {
  if (!constraints) return ''

  const withoutLabel = String(constraints)
    .replace(/^\s*-\s*\*\*Constraints:\*\*\s*/i, '')
    .replace(/`([^`]*)`/g, '\n$1\n')
    .replace(/`/g, '')

  return withoutLabel
    .split(/[;\n]/)
    .flatMap((part) => {
      const normalized = normalizeConstraintText(part)
      if (!normalized) return []
      return [expandSharedBounds(normalized)]
    })
    .flatMap((part) => {
      if (!part.includes(',')) return [part]
      return part.split(',').map((item) => item.trim()).filter(Boolean)
    })
    .map(formatConstraintLine)
    .filter(Boolean)
    .join('\n')
}
