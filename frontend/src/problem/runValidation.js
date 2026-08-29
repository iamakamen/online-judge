export function resolveRunMode(mode, customInput) {
  if (mode === 'custom_input') {
    return typeof customInput === 'string' && customInput.trim() !== ''
      ? 'custom_input'
      : 'run_tests'
  }

  return mode
}
