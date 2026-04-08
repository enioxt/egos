#!/usr/bin/env bun
/**
 * tasks-archive.ts — Auto-archive completed sections from TASKS.md
 *
 * Moves sections where ALL tasks are [x]/✅ into TASKS_ARCHIVE.md.
 * Sections with any [ ] or [/] task are kept as active.
 *
 * Usage:
 *   bun scripts/tasks-archive.ts [--dry]
 */
export {}

import { readFileSync, writeFileSync, existsSync } from 'fs'
import { join } from 'path'

const DRY = process.argv.includes('--dry')
const ROOT = new URL('..', import.meta.url).pathname
const TASKS_PATH = join(ROOT, 'TASKS.md')
const ARCHIVE_PATH = join(ROOT, 'TASKS_ARCHIVE.md')

const content = readFileSync(TASKS_PATH, 'utf8')
const archiveExists = existsSync(ARCHIVE_PATH)
const archiveHeader = archiveExists ? '' : `# TASKS_ARCHIVE.md — Completed sections\n\n`

// Split into sections by ### headers
const sections = content.split(/(?=^###\s)/m)
const headerBlock = sections.shift() ?? ''

const active: string[] = []
const archive: string[] = []

for (const section of sections) {
  const hasActiveTasks = /- \[[ /]\]/.test(section)
  const hasAnyTasks = /- \[[x ✅/]\]/i.test(section)

  if (!hasAnyTasks || hasActiveTasks) {
    active.push(section)
  } else {
    // All tasks [x] or ✅ — candidate for archiving
    archive.push(section)
  }
}

const activeContent = headerBlock + active.join('')
const archiveContent = archive.join('\n---\n\n')

if (archive.length === 0) {
  console.log('ℹ️  No fully-completed sections found to archive.')
  console.log(`   TASKS.md: ${content.split('\n').length} lines`)
  process.exit(0)
}

console.log(`📦 Found ${archive.length} completed section(s) to archive:`)
for (const s of archive) {
  const title = s.match(/^###\s(.+)/m)?.[1] ?? '?'
  console.log(`   - ${title}`)
}

const beforeLines = content.split('\n').length
const afterLines = activeContent.split('\n').length
console.log(`\n📉 TASKS.md: ${beforeLines} → ${afterLines} lines (-${beforeLines - afterLines})`)

if (DRY) {
  console.log('\n[DRY RUN] No files written. Remove --dry to apply.')
  process.exit(0)
}

writeFileSync(TASKS_PATH, activeContent, 'utf8')
writeFileSync(
  ARCHIVE_PATH,
  (archiveExists ? readFileSync(ARCHIVE_PATH, 'utf8') : archiveHeader) +
  `\n## Archived ${new Date().toISOString().slice(0, 10)}\n\n` + archiveContent,
  'utf8'
)

console.log('\n✅ Done. Run `git add TASKS.md TASKS_ARCHIVE.md && git commit -m "chore: archive completed tasks"`')
