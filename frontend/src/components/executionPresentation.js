export function isPassedTest(testResult) {
  return testResult?.status === 'passed'
}

export function runTestState(testResult) {
  if (testResult?.status === 'passed') return 'is-passed'
  if (testResult?.status === 'failed') return 'is-failed'
  return 'is-neutral'
}

export function runStatusLabel(result) {
  const labels = {
    compile_error: 'Compilation Error',
    runtime_error: 'Runtime Error',
    time_limit_exceeded: 'Time Limit Exceeded',
    memory_limit_exceeded: 'Memory Limit Exceeded',
    output_limit_exceeded: 'Output Limit Exceeded',
    system_error: 'System Error',
  }
  return result?.status === 'passed' ? 'Passed' : labels[result?.status] || 'Failed'
}

export function runErrorText(result) {
  return result?.results?.find((testResult) => testResult?.status !== 'passed' && testResult?.stderr)?.stderr || ''
}

export function submitVerdictLabel(result) {
  return result?.verdict === 'accepted' ? 'Passed' : 'Failed'
}

const SUBMIT_ERROR_LABELS = {
  compile_error: 'Compilation Error',
  runtime_error: 'Runtime Error',
  time_limit_exceeded: 'Time Limit Exceeded',
  memory_limit_exceeded: 'Memory Limit Exceeded',
  output_limit_exceeded: 'Output Limit Exceeded',
  system_error: 'System Error',
}

export function submitStatusLabel(result) {
  const status = result?.verdict || result?.status
  if (status === 'accepted') return 'Passed'
  return SUBMIT_ERROR_LABELS[status] || 'Failed'
}

export function submitStatusKind(result) {
  const status = result?.verdict || result?.status
  if (status === 'accepted') return 'is-passed'
  if (SUBMIT_ERROR_LABELS[status]) return 'is-error'
  return 'is-failed'
}

export function submitErrorText(result) {
  if (result?.error) return result.error
  return result?.results?.find((testResult) => testResult?.stderr || testResult?.error)?.stderr
    || result?.results?.find((testResult) => testResult?.stderr || testResult?.error)?.error
    || ''
}

export function publicRunTestCases(result) {
  return result?.mode === 'run_tests' ? result.results || [] : []
}

export function formatRunInputs(result) {
  return publicRunTestCases(result)
    .map((testResult, index) => `Test Case ${testResult.display_order ?? index + 1}:\n${testResult.input}`)
    .join('\n\n')
}

export function formatRunOutputs(result) {
  return (result?.results || [])
    .map((testResult, index) => `Test Case ${testResult.display_order ?? index + 1}:\n${testResult.stdout}`)
    .join('\n\n')
}

export function runResultTestCases(result) {
  const first = result?.results?.[0] || null
  const second = first?.status === 'passed' ? result?.results?.[1] || null : null
  return [first, second]
}
