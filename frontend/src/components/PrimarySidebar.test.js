import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'
import { fileURLToPath } from 'node:url'

const sidebarSource = readFileSync(fileURLToPath(new URL('./PrimarySidebar.jsx', import.meta.url)), 'utf8')
const brandSource = sidebarSource.slice(sidebarSource.indexOf('<a\n        href="/dashboard"'), sidebarSource.indexOf('</a>', sidebarSource.indexOf('<a\n        href="/dashboard"')))
const practiceSource = sidebarSource.slice(sidebarSource.indexOf('<SidebarItem label="Practice"'), sidebarSource.indexOf('\n', sidebarSource.indexOf('<SidebarItem label="Practice"')))
const disabledItemSources = ['Learn', 'Contest', 'Forum', 'Profile'].map((label) => {
  const start = sidebarSource.indexOf(`<SidebarItem label="${label}"`)
  return sidebarSource.slice(start, sidebarSource.indexOf('/>', start) + 2)
})

test('keeps Practice as a native link', () => {
  assert.match(practiceSource, /href="\/practice"/)
  assert.match(practiceSource, /onClick=\{\(\) => handleNavigate\('\/practice'\)\}/)
  assert.match(sidebarSource, /function SidebarItem\(\{ label, icon, active = false, onClick, href, onContextMenu \}\)/)
})

test('uses a native Dashboard link', () => {
  assert.match(brandSource, /href="\/dashboard"/)
  assert.match(brandSource, /onClick=\{\(event\) => \{[\s\S]*event\.preventDefault\(\)[\s\S]*handleNavigate\('\/dashboard'\)/)
})

test('keeps Learn, Contest, Forum, and Profile non-navigable buttons', () => {
  for (const itemSource of disabledItemSources) {
    assert.match(itemSource, /<SidebarItem label="(?:Learn|Contest|Forum|Profile)"/)
    assert.doesNotMatch(itemSource, /href=/)
    assert.doesNotMatch(itemSource, /onContextMenu=/)
  }
  assert.equal((sidebarSource.match(/<SidebarItem label=/g) || []).length, 5)
})

test('preserves the existing mouse and focus collapse state machine for real focus changes', () => {
  assert.match(sidebarSource, /onMouseEnter=\{handleMouseEnter\}/)
  assert.match(sidebarSource, /onMouseLeave=\{handleMouseLeave\}/)
  assert.match(sidebarSource, /onFocus=\{onExpand\}/)
  assert.match(sidebarSource, /const handleNavigate = \(path\) => \{\s*onCollapse\(\)\s*navigate\(path\)/)
})

test('limits custom context menus to Brand and Practice', () => {
  assert.match(brandSource, /onContextMenu=\{\(event\) => handleContextMenu\(event, '\/dashboard'\)\}/)
  assert.match(sidebarSource, /onContextMenu=\{\(event\) => handleContextMenu\(event, '\/practice'\)\}/)
  assert.doesNotMatch(sidebarSource, /document\.addEventListener\(['"]contextmenu/)
  assert.doesNotMatch(sidebarSource, /window\.addEventListener\(['"]contextmenu/)
  assert.doesNotMatch(sidebarSource, /window\.addEventListener\(['"]message/)
})

test('provides the required actions, destinations, dismissal, keyboard, and viewport handling', () => {
  assert.match(sidebarSource, /Open in New Tab/)
  assert.match(sidebarSource, /Copy Link/)
  assert.doesNotMatch(sidebarSource, /Open in New Window/)
  assert.doesNotMatch(sidebarSource, /popup/)
  assert.match(sidebarSource, /closeContextMenu\(\)\s*onCollapse\(\)/)
  assert.match(sidebarSource, /new URL\(contextMenu\.path, window\.location\.href\)/)
  assert.match(sidebarSource, /navigator\.clipboard\.writeText\(destination\)/)
  assert.match(sidebarSource, /event\.key === 'Escape'/)
  assert.match(sidebarSource, /event\.key === 'ArrowDown'/)
  assert.match(sidebarSource, /event\.key === 'ArrowUp'/)
  assert.match(sidebarSource, /event\.key === 'Enter'/)
  assert.match(sidebarSource, /getBoundingClientRect\(\)/)
  assert.match(sidebarSource, /window\.innerWidth/)
  assert.match(sidebarSource, /window\.innerHeight/)
  assert.match(sidebarSource, /!menuElement\.contains\(event\.target\)/)
})
