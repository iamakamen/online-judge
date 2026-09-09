import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import test from 'node:test'

const indexHtml = fs.readFileSync(path.resolve('index.html'), 'utf8')

test('frontend metadata uses the encode browser tab branding', () => {
  assert.match(indexHtml, /<title>encode \| Solve it<\/title>/)
  assert.match(indexHtml, /<link rel="icon" type="image\/svg\+xml" href="\/favicon\.svg" \/>/)
  assert.equal((indexHtml.match(/<title>/g) || []).length, 1)
})
