import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { fileURLToPath } from 'node:url'
import {
  formatRunInputs,
  formatRunOutputs,
  isPassedTest,
  runStatusLabel,
  runResultTestCases,
  runErrorText,
  runTestState,
  submitErrorText,
  submitStatusKind,
  submitStatusLabel,
  submitVerdictLabel,
} from './executionPresentation.js'

const workspaceSource = readFileSync(fileURLToPath(new URL('./ExecutionWorkspace.jsx', import.meta.url)), 'utf8')
const problemSource = readFileSync(fileURLToPath(new URL('../pages/ProblemPage.jsx', import.meta.url)), 'utf8')
const codeEditorSource = readFileSync(fileURLToPath(new URL('./CodeEditor.jsx', import.meta.url)), 'utf8')
const problemStyles = readFileSync(fileURLToPath(new URL('../pages/ProblemPage.css', import.meta.url)), 'utf8')
const runResultSource = workspaceSource.slice(
  workspaceSource.indexOf('function RunResult'),
  workspaceSource.indexOf('function SubmissionResult'),
)
const submitResultSource = workspaceSource.slice(
  workspaceSource.indexOf('function SubmissionResult'),
  workspaceSource.indexOf('function AiHelp'),
)

test('formats passed and failed run presentation states', () => {
  assert.equal(runStatusLabel({ status: 'passed' }), 'Passed')
  assert.equal(runStatusLabel({ status: 'failed' }), 'Failed')
  assert.equal(runStatusLabel({ status: 'runtime_error' }), 'Runtime Error')
  assert.equal(runStatusLabel({ status: 'compile_error' }), 'Compilation Error')
  assert.equal(isPassedTest({ status: 'passed' }), true)
  assert.equal(isPassedTest({ status: 'wrong_answer' }), false)
})

test('keeps unexecuted Run tests neutral and exposes exactly two Run cases', () => {
  assert.equal(runTestState({ status: 'passed' }), 'is-passed')
  assert.equal(runTestState({ status: 'failed' }), 'is-failed')
  assert.equal(runTestState({ status: 'not_executed' }), 'is-neutral')
  assert.equal(runTestState({}), 'is-neutral')
  assert.deepEqual(runResultTestCases({ results: [
    { display_order: 1, status: 'failed' },
    { display_order: 2, status: 'passed' },
    { display_order: 3, status: 'passed' },
  ] }).map((testResult) => testResult?.status ?? null), ['failed', null])
  assert.deepEqual(runResultTestCases({ results: [{ status: 'failed' }] }), [{ status: 'failed' }, null])
})

test('keeps accepted-solution loading errors separate from problem loading errors', () => {
  const acceptedRequest = problemSource.slice(
    problemSource.indexOf('const saved = await requestAuthenticated'),
    problemSource.indexOf('      })\n      .catch((requestError)', problemSource.indexOf('const saved = await requestAuthenticated')),
  )
  assert.match(acceptedRequest, /catch \{/)
  assert.match(acceptedRequest, /setAcceptedSolutions\(null\)/)
  assert.match(problemSource, /getProblemBySlug\(accessToken, slug\)/)
  assert.match(problemSource, /notFound: requestError instanceof ApiError && requestError.status === 404/)
})

test('maps the three fail-fast Run outcomes to card states', () => {
  const states = (result) => runResultTestCases(result).map(runTestState)
  assert.deepEqual(states({ status: 'failed', results: [{ status: 'failed' }] }), ['is-failed', 'is-neutral'])
  assert.deepEqual(states({ status: 'failed', results: [{ status: 'failed' }, { status: 'failed' }] }), ['is-failed', 'is-neutral'])
  assert.deepEqual(states({ status: 'failed', results: [{ status: 'failed' }, { status: 'passed' }] }), ['is-failed', 'is-neutral'])
  assert.deepEqual(states({ status: 'failed', results: [{ status: 'passed' }, { status: 'failed' }] }), ['is-passed', 'is-failed'])
  assert.deepEqual(states({ status: 'passed', results: [{ status: 'passed' }, { status: 'passed' }] }), ['is-passed', 'is-passed'])
})

test('formats passed and failed submit verdicts', () => {
  assert.equal(submitVerdictLabel({ verdict: 'accepted' }), 'Passed')
  assert.equal(submitVerdictLabel({ verdict: 'wrong_answer' }), 'Failed')
})

test('maps Submit verdicts and existing execution error classifications', () => {
  assert.equal(submitStatusLabel({ verdict: 'accepted' }), 'Passed')
  assert.equal(submitStatusKind({ verdict: 'accepted' }), 'is-passed')
  assert.equal(submitStatusLabel({ verdict: 'wrong_answer' }), 'Failed')
  assert.equal(submitStatusKind({ verdict: 'wrong_answer' }), 'is-failed')
  assert.equal(submitStatusLabel({ verdict: 'runtime_error' }), 'Runtime Error')
  assert.equal(submitStatusKind({ verdict: 'runtime_error' }), 'is-error')
  assert.equal(submitStatusLabel({ verdict: 'compile_error' }), 'Compilation Error')
  assert.equal(submitStatusLabel({ verdict: 'time_limit_exceeded' }), 'Time Limit Exceeded')
  assert.equal(submitStatusLabel({ verdict: 'system_error' }), 'System Error')
})

test('keeps Submit diagnostics ordinary content inside the result surface', () => {
  assert.equal(submitErrorText({ error: 'trace\nline' }), 'trace\nline')
  assert.equal(submitErrorText({ results: [{ status: 'runtime_error', stderr: 'trace' }] }), 'trace')
  assert.equal(submitErrorText({ results: [{ status: 'wrong_answer' }] }), '')
})

test('exposes only legitimate Run execution error details', () => {
  assert.equal(runErrorText({ status: 'runtime_error', results: [{ status: 'runtime_error', stderr: 'trace\nline' }] }), 'trace\nline')
  assert.equal(runErrorText({ status: 'failed', results: [{ status: 'failed', stderr: '' }] }), '')
})

test('formats only public Run input and preserves line breaks', () => {
  assert.equal(formatRunInputs({
    mode: 'run_tests',
    results: [
      { display_order: 1, input: '1\n2', expected_output: 'hidden' },
      { display_order: 2, input: '3', expected_output: 'hidden' },
    ],
  }), 'Test Case 1:\n1\n2\n\nTest Case 2:\n3')
  assert.equal(formatRunInputs({
    mode: 'custom_input',
    results: [{ input: 'custom input' }],
  }), '')
})

test('formats Run output without exposing diagnostics or Submit data', () => {
  const result = {
    results: [
      { display_order: 1, stdout: 'answer\nline', stderr: 'diagnostic', expected_output: 'hidden expected' },
      { display_order: 2, stdout: 'second', stderr: 'hidden stderr' },
    ],
  }
  const output = formatRunOutputs(result)
  assert.equal(output, 'Test Case 1:\nanswer\nline\n\nTest Case 2:\nsecond')
  assert.doesNotMatch(output, /diagnostic|hidden expected|hidden stderr/)
})

test('uses presentation-only cards and prevents horizontal overflow', () => {
  assert.match(workspaceSource, /Status: <span className=\{isPassedTest\(result\) \? 'is-passed' : 'is-failed'\}/)
  assert.match(workspaceSource, /execution-workspace-test-card \$\{runTestState\(testResult\)\}/)
  assert.match(workspaceSource, /runResultTestCases\(result\)/)
  assert.match(workspaceSource, /Test Case \{index \+ 1\}/)
  assert.doesNotMatch(workspaceSource, /formatRunResultText|<textarea[\s\S]*Test Case/)
  assert.match(workspaceSource, /execution-workspace-run-ai[\s\S]*<AiHelp/)
  assert.match(workspaceSource, /execution-workspace-run-result-scroll[\s\S]*<RunResult/)
  assert.match(workspaceSource, /execution-workspace-run-result-container[\s\S]*execution-workspace-run-ai[\s\S]*execution-workspace-run-result-scroll/)
  assert.match(workspaceSource, /runErrorText\(result\)[\s\S]*execution-workspace-run-error/)
  assert.match(workspaceSource, /has-ai-response/)
  assert.doesNotMatch(workspaceSource, /keepActionVisible|<AiHelp[^>]*success/)
  assert.match(workspaceSource, /execution-workspace-run-ai[\s\S]*<AiHelp[\s\S]*execution-workspace-run-result-scroll[\s\S]*<RunResult/)
  assert.doesNotMatch(runResultSource, /<AiHelp/)
  assert.doesNotMatch(workspaceSource, /execution_time_ms|memory_used_mb|expected_output|<pre>|execution-workspace-result-textarea/)
  assert.match(problemStyles, /execution-workspace-result[^\n]*overflow-y: auto[^\n]*overflow-x: hidden/)
  assert.match(problemStyles, /execution-workspace-run-result[^\n]*overflow-y: auto[^\n]*overflow-x: hidden/)
  assert.match(problemStyles, /execution-workspace-run-result-container[^\n]*overflow: hidden/)
  assert.match(problemStyles, /execution-workspace-run-result-container[^\n]*gap: 12px/)
  assert.match(problemStyles, /execution-workspace-panel\.is-tabbed\.has-ai-response[^\n]*overflow-y: auto/)
  assert.match(problemStyles, /--execution-ai-response-height: 90px/)
  assert.match(problemStyles, /execution-workspace-run-ai\.has-ai-response[^\n]*overflow: visible/)
  assert.match(problemStyles, /execution-workspace-run-result-container\.has-ai-response[^\n]*flex: 0 0 auto[^\n]*overflow: visible/)
  assert.match(problemStyles, /execution-workspace-run-result-container\.has-ai-response \.execution-workspace-run-result-scroll[^\n]*flex: 0 0 auto/)
  assert.match(problemStyles, /execution-workspace-run-result-container\.has-ai-response \.execution-workspace-run-result[^\n]*height: auto/)
  assert.match(problemStyles, /execution-workspace-panel\.is-tabbed[^\n]*display: flex[^\n]*flex-direction: column/)
  assert.match(problemStyles, /execution-workspace-ai-result[^\n]*overflow-y: auto[^\n]*overflow-x: hidden/)
  assert.match(problemStyles, /execution-workspace-run-result[^\n]*background: var\(--problem-surface\)/)
  assert.match(problemStyles, /execution-workspace-run-result \.execution-workspace-status \{[^}]*color: var\(--problem-text\)/)
  assert.match(problemStyles, /execution-workspace-run-result \.execution-workspace-status \.is-passed \{[^}]*color: #58d68d/)
  assert.match(problemStyles, /execution-workspace-run-result \.execution-workspace-status \.is-failed \{[^}]*color: #ff6b81/)
  assert.match(problemStyles, /execution-workspace-readonly-content[^\n]*overflow-x: hidden/)
})

test('fills Run Input and Output surfaces without horizontal overflow', () => {
  assert.match(workspaceSource, /execution-workspace-input--fill/)
  assert.match(problemStyles, /execution-workspace-input--fill[^\n]*min-height: 0[^\n]*flex: 1 1 auto/)
  assert.match(problemStyles, /execution-workspace-input--fill[^\n]*height: auto[^\n]*max-height: none/)
  assert.match(problemStyles, /execution-workspace-input--fill \.execution-workspace-readonly-content[^\n]*height: auto[^\n]*max-height: none[^\n]*min-height: 0[^\n]*flex: 1 1 auto/)
  assert.match(problemStyles, /execution-workspace-readonly-content[^\n]*overflow-y: auto[^\n]*overflow-x: hidden/)
})

test('keeps Custom Input as a static two-pane workspace with an internal Run button', () => {
  const customWorkspaceSource = workspaceSource.slice(
    workspaceSource.indexOf('function CustomInputWorkspace'),
    workspaceSource.indexOf("const showTabs = mode === 'run'"),
  )
  assert.match(workspaceSource, /mode === 'custom'/)
  assert.match(customWorkspaceSource, /execution-workspace-custom-panes/)
  assert.match(customWorkspaceSource, /<h3>Input<\/h3>[\s\S]*<textarea/)
  assert.match(customWorkspaceSource, /<h3>Output<\/h3>[\s\S]*execution-workspace-custom-output/)
  assert.match(customWorkspaceSource, /execution-workspace-custom-run[\s\S]*onClick={onCustomRun}/)
  assert.doesNotMatch(customWorkspaceSource, /execution-workspace-tabs/)
})

test('renders custom stdout and existing execution diagnostics without correctness labels', () => {
  const customWorkspaceSource = workspaceSource.slice(
    workspaceSource.indexOf('function CustomInputWorkspace'),
    workspaceSource.indexOf("const showTabs = mode === 'run'"),
  )
  assert.match(customWorkspaceSource, /const customResult = result\?\.results\?\.\[0\]/)
  assert.match(customWorkspaceSource, /const output = customResult\?\.stdout \|\| ''/)
  assert.match(customWorkspaceSource, /const diagnostic = customResult\?\.stderr \|\| error \|\| ''/)
  assert.match(customWorkspaceSource, /hasExecutionError/)
  assert.doesNotMatch(customWorkspaceSource, /runStatusLabel\(result\)|>Passed<|>Failed</)
  assert.match(customWorkspaceSource, /No output yet\./)
  assert.match(customWorkspaceSource, /Custom Input workspace/)
})

test('places existing Custom Input AI Help inside Output before diagnostics', () => {
  const customWorkspaceSource = workspaceSource.slice(
    workspaceSource.indexOf('function CustomInputWorkspace'),
    workspaceSource.indexOf("const showTabs = mode === 'run'"),
  )
  assert.match(customWorkspaceSource, /execution-workspace-custom-output[\s\S]*<AiHelp[\s\S]*phase === 'running'/)
  assert.match(problemStyles, /execution-workspace-custom-output \.execution-workspace-ai-action[^\n]*justify-content: flex-end/)
  const aiHelpBoxRule = problemStyles.match(/execution-workspace-custom-output \.execution-workspace-ai-result[^\n]*/)?.[0] || ''
  assert.match(aiHelpBoxRule, /border: 1px solid/)
  assert.match(aiHelpBoxRule, /padding: 10px 12px/)
  assert.match(aiHelpBoxRule, /overflow: visible/)
  assert.match(aiHelpBoxRule, /overflow-wrap: anywhere/)
  assert.doesNotMatch(aiHelpBoxRule, /height:|max-height:|overflow-y: auto|overflow-y: scroll/)
  assert.match(customWorkspaceSource, /<AiHelp[\s\S]*phase === 'running'[\s\S]*execution-workspace-custom-error/)
  assert.match(problemStyles, /execution-workspace-custom-output[^\n]*overflow-y: auto[^\n]*overflow-x: hidden/)
})

test('keeps external Run public and routes internal Run through custom mode resolution', () => {
  assert.match(problemSource, /onRun=\{\(payload\) => handleRun\(payload, 'run_tests'\)\}/)
  assert.match(problemSource, /onCustomRun=\{handleCustomRun\}/)
  const customRunHandlerSource = problemSource.slice(
    problemSource.indexOf('function handleCustomRun'),
    problemSource.indexOf('async function handleAiHelp'),
  )
  assert.match(customRunHandlerSource, /customInput\.trim\(\) === ''\) return/)
  assert.match(customRunHandlerSource, /handleRun\(editorPayloadRef\.current, 'custom_input'\)/)
  assert.doesNotMatch(customRunHandlerSource, /resolveRunMode|run_tests/)
  assert.match(problemSource, /const mode = resolveRunMode\(requestedMode, customInput\)/)
  assert.match(problemSource, /setExecutionMode\('custom'\)/)
  assert.match(problemSource, /setExecutionMode\('run'\)/)
  assert.match(codeEditorSource, /onClick={handleRun}[\s\S]*>\s*<RunIcon \/>\s*Run/)
})

test('lays out the Custom Input Run icon and label in one centered row', () => {
  const customRunRule = problemStyles.match(/execution-workspace-custom-run \{[^}]*\}/)?.[0] || ''
  const customRunIconRule = problemStyles.match(/execution-workspace-custom-run \.execution-workspace-run-icon \{[^}]*\}/)?.[0] || ''
  assert.match(customRunRule, /display: flex/)
  assert.match(customRunRule, /flex-direction: row/)
  assert.match(customRunRule, /align-items: center/)
  assert.match(customRunRule, /gap: 6px/)
  assert.match(customRunRule, /flex-wrap: nowrap/)
  assert.match(customRunRule, /white-space: nowrap/)
  assert.match(customRunRule, /width: fit-content/)
  assert.match(customRunRule, /font-size: \.82rem/)
  assert.match(customRunRule, /font-weight: var\(--font-weight-semibold\)/)
  assert.match(customRunRule, /line-height: 1/)
  assert.match(customRunIconRule, /display: block/)
  assert.match(customRunIconRule, /flex: 0 0 14px/)
})

test('keeps public and Custom Input execution state and AI state separate', () => {
  assert.match(problemSource, /customExecutionState.*idleExecutionState/)
  assert.match(problemSource, /customAiHelpState.*idleAiHelpState/)
  assert.match(problemSource, /customAiHelpRequest.*null/)
  assert.match(problemSource, /setCustomExecutionState\(\{ phase: 'running'/)
  assert.match(problemSource, /setCustomExecutionState\(\{ phase: 'completed', result, error: null \}\)/)
  assert.match(problemSource, /setExecutionState\(\{ phase: 'running', result: null, error: null \}\)/)
  assert.match(problemSource, /const workspaceExecutionState = workspaceIsCustom \? customExecutionState : executionState/)
  assert.match(problemSource, /const workspaceAiHelpState = workspaceIsCustom \? customAiHelpState : aiHelpState/)
  assert.match(problemSource, /const workspaceAiHelpRequest = workspaceIsCustom \? customAiHelpRequest : aiHelpRequest/)
  assert.match(problemSource, /onAiHelp=\{workspaceIsCustom \? handleCustomAiHelp : handleAiHelp\}/)
})

test('applies custom pane scrolling and wrapping constraints', () => {
  assert.match(problemStyles, /execution-workspace-custom-pane textarea, \.problem-page-v2 \.execution-workspace-custom-output[^\n]*overflow-y: auto[^\n]*overflow-x: hidden/)
  assert.match(problemStyles, /execution-workspace-custom-pane textarea, \.problem-page-v2 \.execution-workspace-custom-output[^\n]*overflow-wrap: anywhere/)
  assert.match(problemStyles, /execution-workspace-custom-panes[^\n]*grid-template-columns: repeat\(2, minmax\(0, 1fr\)/)
  assert.match(problemStyles, /execution-workspace-custom-panel[^\n]*min-height: 0/)
})

test('keeps Submit presentation separate from Run and preserves every Submit case', () => {
  assert.match(workspaceSource, /execution-workspace-submit-result-container[\s\S]*execution-workspace-submit-ai[\s\S]*execution-workspace-submit-result-scroll[\s\S]*<SubmissionResult/)
  assert.match(submitResultSource, /Status: <span className=\{submitStatusKind\(result\)\}/)
  assert.match(submitResultSource, /result\.results\.map/)
  assert.match(submitResultSource, /Test Case \{testResult\.display_order \?\? index \+ 1\}/)
  assert.match(submitResultSource, /runTestState\(testResult\)/)
  assert.match(workspaceSource, /execution-workspace\$\{showTabs \? ' has-tabs' : ''\}\$\{mode === 'submit' \? ' is-submit' : ''\}/)
  assert.match(problemStyles, /execution-workspace\.is-submit[^\n]*overflow-y: auto[^\n]*overflow-x: hidden/)
  assert.match(problemStyles, /execution-workspace\.is-submit \.execution-workspace-panel\.is-full-height[^\n]*height: auto[^\n]*min-height: 100%[^\n]*flex: 0 0 auto[^\n]*overflow: visible/)
  assert.match(problemStyles, /execution-workspace-submit-result-container[^\n]*gap: 12px/)
  assert.match(problemStyles, /execution-workspace-submit-result[^\n]*border: 1px solid var\(--problem-border-strong\)[^\n]*overflow-y: auto[^\n]*overflow-x: hidden/)
  assert.match(problemStyles, /execution-workspace\.is-submit \.execution-workspace-submit-result-scroll[^\n]*flex: 0 0 auto[^\n]*min-height: 120px[^\n]*overflow: visible/)
  assert.match(problemStyles, /execution-workspace-submit-result[^\n]*min-height: 120px/)
  assert.match(problemStyles, /execution-workspace-submit-result \.execution-workspace-status \.is-passed[^\n]*color: #58d68d/)
  assert.match(problemStyles, /execution-workspace-submit-result \.execution-workspace-status \.is-failed[^\n]*color: #ff6b81/)
  assert.match(problemStyles, /execution-workspace-submit-result \.execution-workspace-status \.is-error[^\n]*color: #ff6b81/)
  assert.match(submitResultSource, /submitErrorText\(result\)[\s\S]*Error:/)
  assert.doesNotMatch(submitResultSource, /execution-workspace-submit-error[^\n]*border|execution-workspace-submit-error[^\n]*textarea/)
  assert.match(problemStyles, /execution-workspace-test-card\.is-neutral[^\n]*border-color: #ffffff/)
  assert.match(workspaceSource, /execution-workspace-submit-ai[\s\S]*<AiHelp[\s\S]*execution-workspace-submit-result-scroll[\s\S]*<SubmissionResult/)
  assert.doesNotMatch(submitResultSource, /execution-workspace-ai|execution-workspace-submit-result-container/)
})

test('bounds Submit AI response without compressing the result surface', () => {
  assert.match(problemStyles, /execution-workspace-submit-ai\.has-ai-response[^\n]*overflow: visible/)
  assert.match(problemStyles, /execution-workspace-submit-result-container\.has-ai-response[^\n]*flex: 0 0 auto[^\n]*overflow: visible/)
  assert.match(problemStyles, /execution-workspace\.is-submit \.execution-workspace-submit-result-container[^\n]*flex: 0 0 auto[^\n]*overflow: visible/)
  assert.match(problemStyles, /execution-workspace\.is-submit \.execution-workspace-submit-result-container, \.problem-page-v2 \.execution-workspace\.is-submit \.execution-workspace-submit-ai, \.problem-page-v2 \.execution-workspace\.is-submit \.execution-workspace-submit-result-scroll, \.problem-page-v2 \.execution-workspace\.is-submit \.execution-workspace-submit-result[^\n]*width: 100%[^\n]*min-width: 0/)
  assert.match(problemStyles, /execution-workspace\.is-submit \.execution-workspace-submit-ai\.has-ai-response \.execution-workspace-ai-result[^\n]*width: 100%[^\n]*min-width: 0[^\n]*min-height: var\(--execution-ai-response-height\)[^\n]*height: auto[^\n]*max-height: none[^\n]*overflow: visible/)
  assert.match(problemStyles, /execution-workspace\.is-submit \.execution-workspace-submit-result[^\n]*width: 100%[^\n]*min-width: 0[^\n]*min-height: 120px[^\n]*height: auto[^\n]*max-height: none[^\n]*flex: 0 0 auto/)
  assert.match(problemStyles, /execution-workspace\.is-submit:not\(:has\(\.execution-workspace-submit-ai\.has-ai-response\)\):has\(\.execution-workspace-submit-result \.execution-workspace-status \.is-passed\) \.execution-workspace-panel\.is-full-height[^\n]*height: 100%[^\n]*min-height: 0[^\n]*flex: 0 0 auto/)
  assert.match(problemStyles, /execution-workspace\.is-submit:not\(:has\(\.execution-workspace-submit-ai\.has-ai-response\)\):has\(\.execution-workspace-submit-result \.execution-workspace-status \.is-passed\) \.execution-workspace-submit-result-container[^\n]*flex: 1 1 auto[^\n]*min-height: 0/)
  assert.match(problemStyles, /execution-workspace\.is-submit:not\(:has\(\.execution-workspace-submit-ai\.has-ai-response\)\):has\(\.execution-workspace-submit-result \.execution-workspace-status \.is-passed\) \.execution-workspace-submit-result-scroll[^\n]*flex: 1 1 auto[^\n]*min-height: 0/)
  assert.match(problemStyles, /execution-workspace\.is-submit:not\(:has\(\.execution-workspace-submit-ai\.has-ai-response\)\):has\(\.execution-workspace-submit-result \.execution-workspace-status \.is-passed\) \.execution-workspace-submit-result-scroll \.execution-workspace-submit-result[^\n]*height: 100%[^\n]*flex: 1 1 auto/)
  assert.match(problemStyles, /execution-workspace\.is-submit:not\(:has\(\.execution-workspace-submit-ai\.has-ai-response\)\):has\(\.execution-workspace-submit-result \.execution-workspace-status :is\(\.is-failed, \.is-error\)\) \.execution-workspace-panel\.is-full-height[^\n]*height: 100%[^\n]*min-height: 0[^\n]*flex: 0 0 auto/)
  assert.match(problemStyles, /execution-workspace\.is-submit:not\(:has\(\.execution-workspace-submit-ai\.has-ai-response\)\):has\(\.execution-workspace-submit-result \.execution-workspace-status :is\(\.is-failed, \.is-error\)\) \.execution-workspace-submit-result-container[^\n]*flex: 1 1 auto[^\n]*min-height: 0/)
  assert.match(problemStyles, /execution-workspace\.is-submit:not\(:has\(\.execution-workspace-submit-ai\.has-ai-response\)\):has\(\.execution-workspace-submit-result \.execution-workspace-status :is\(\.is-failed, \.is-error\)\) \.execution-workspace-submit-result-scroll[^\n]*flex: 1 1 auto[^\n]*min-height: 0/)
  assert.match(problemStyles, /execution-workspace\.is-submit:not\(:has\(\.execution-workspace-submit-ai\.has-ai-response\)\):has\(\.execution-workspace-submit-result \.execution-workspace-status :is\(\.is-failed, \.is-error\)\) \.execution-workspace-submit-result-scroll \.execution-workspace-submit-result[^\n]*height: 100%[^\n]*flex: 1 1 auto/)
  assert.doesNotMatch(problemStyles, /execution-workspace\.is-submit \.execution-workspace-submit-ai\.has-ai-response \.execution-workspace-ai-result[^\n]*overflow-y: auto/)
  assert.match(problemStyles, /execution-workspace\.is-submit[^\n]*overflow-y: auto[^\n]*overflow-x: hidden/)
  assert.match(problemStyles, /execution-workspace-submit-ai[^\n]*flex: 0 0 auto/)
  assert.match(problemStyles, /execution-workspace-submit-result-scroll[^\n]*display: flex/)
  assert.doesNotMatch(workspaceSource, /<AiHelp[\s\S]*execution-workspace-submit-result[\s\S]*<\/AiHelp>/)
})
