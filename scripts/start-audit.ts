import { existsSync, mkdirSync, readFileSync, readdirSync, statSync, writeFileSync } from 'node:fs'
import { execSync } from 'node:child_process'
import { join, resolve } from 'node:path'
import { chatWithLLM } from '../packages/shared/src/llm-provider'

type RepoConfig = { name: string; path: string; healthUrl?: string }
type RepoState = { name: string; branch: string; head: string; upstream: string; modified: number; untracked: number; ahead: number; behind: number; modifiedFiles: string[]; docVersions: string[]; missingDocs: string[]; handoff?: string; health?: string }

const args = process.argv.slice(2)
const live = args.includes('--live')
const useAI = args.includes('--ai')
const json = args.includes('--json')
const root = resolve(import.meta.dir, '..')
const generatedDir = join(root, 'docs', '_generated')
const reportPath = join(generatedDir, 'start-audit-latest.json')
const docs = ['AGENTS.md', 'TASKS.md', '.windsurfrules', 'docs/SYSTEM_MAP.md']
const repos: RepoConfig[] = [
  { name: 'egos', path: root },
  { name: 'egos-lab', path: '/home/enio/egos-lab', healthUrl: 'https://egos.ia.br' },
  { name: '852', path: '/home/enio/852', healthUrl: 'https://852.egos.ia.br' },
  { name: 'br-acc', path: '/home/enio/br-acc', healthUrl: 'https://inteligencia.egos.ia.br/health' },
  { name: 'carteira-livre', path: '/home/enio/carteira-livre' },
  { name: 'forja', path: '/home/enio/forja', healthUrl: 'https://forja-orpin.vercel.app' },
  { name: 'policia', path: '/home/enio/policia' },
]

function sh(cmd: string, cwd?: string) { try { return execSync(cmd, { cwd, encoding: 'utf8', timeout: 15000 }).trim() } catch { return '' } }
function readVersion(path: string) { return existsSync(path) ? readFileSync(path, 'utf8').split('\n').slice(0, 4).join(' ').replace(/\s+/g, ' ').slice(0, 180) : '' }
function latestHandoff(repoPath: string) {
  const dir = join(repoPath, 'docs', '_current_handoffs')
  if (!existsSync(dir)) return undefined
  return readdirSync(dir).filter(name => name.endsWith('.md')).sort((a, b) => statSync(join(dir, b)).mtimeMs - statSync(join(dir, a)).mtimeMs)[0]
}
async function checkHealth(url?: string) {
  if (!live || !url) return 'skipped'
  try { const res = await fetch(url, { signal: AbortSignal.timeout(8000) }); return `${res.status}` } catch { return 'offline' }
}
async function inspect(repo: RepoConfig): Promise<RepoState> {
  const status = sh('git status --porcelain', repo.path).split('\n').filter(Boolean)
  const counts = status.reduce((acc, line) => { line.startsWith('??') ? acc.untracked++ : acc.modified++; acc.files.push(line.replace(/^..\s*/, '')); return acc }, { modified: 0, untracked: 0, files: [] as string[] })
  const upstream = sh('git rev-parse --abbrev-ref @{u}', repo.path)
  const aheadBehind = upstream ? sh('git rev-list --left-right --count HEAD...@{u}', repo.path).split(/\s+/) : ['0', '0']
  return {
    name: repo.name,
    branch: sh('git rev-parse --abbrev-ref HEAD', repo.path),
    head: sh('git rev-parse --short HEAD', repo.path),
    upstream,
    modified: counts.modified,
    untracked: counts.untracked,
    ahead: Number(aheadBehind[0] || 0),
    behind: Number(aheadBehind[1] || 0),
    modifiedFiles: counts.files.slice(0, 12),
    docVersions: docs.filter(doc => existsSync(join(repo.path, doc))).map(doc => `${doc}: ${readVersion(join(repo.path, doc))}`),
    missingDocs: docs.filter(doc => !existsSync(join(repo.path, doc))),
    handoff: latestHandoff(repo.path),
    health: await checkHealth(repo.healthUrl),
  }
}
async function aiSummary(states: RepoState[]) {
  const userPrompt = JSON.stringify(states.map(({ name, modified, untracked, ahead, behind, missingDocs, modifiedFiles, handoff, health }) => ({ name, modified, untracked, ahead, behind, missingDocs, modifiedFiles, handoff, health })), null, 2)
  const result = await chatWithLLM({ provider: 'alibaba', model: 'qwen-plus', temperature: 0.2, maxTokens: 900, systemPrompt: 'Você é o reconciliador de startup do EGOS. Analise o estado multi-repo e responda em markdown curto com: 1) riscos críticos, 2) drift entre local/docs/github/vps, 3) quais repos precisam commit/push, 4) próximas ações em ordem.', userPrompt })
  return result.content
}

const states = await Promise.all(repos.filter(repo => existsSync(repo.path)).map(inspect))
const summary = { generatedAt: new Date().toISOString(), criticalRepos: states.filter(state => state.modified + state.untracked > 0 || state.ahead > 0 || state.behind > 0).map(state => state.name), cleanRepos: states.filter(state => state.modified + state.untracked === 0 && state.ahead === 0 && state.behind === 0).map(state => state.name), states }
mkdirSync(generatedDir, { recursive: true })
writeFileSync(reportPath, JSON.stringify(summary, null, 2))
if (json) console.log(JSON.stringify(summary, null, 2))
else {
  console.log(`\n🔁 EGOS Start Audit\n${'═'.repeat(56)}`)
  for (const state of states) {
    console.log(`\n${state.name} @ ${state.branch} (${state.head})`)
    console.log(`  dirty: ${state.modified} modified / ${state.untracked} untracked | sync: +${state.ahead}/-${state.behind}`)
    if (state.modifiedFiles.length) console.log(`  files: ${state.modifiedFiles.join(', ')}`)
    if (state.missingDocs.length) console.log(`  missing docs: ${state.missingDocs.join(', ')}`)
    if (state.handoff) console.log(`  handoff: ${state.handoff}`)
    if (state.health && state.health !== 'skipped') console.log(`  live: ${state.health}`)
  }
  console.log(`\n${'═'.repeat(56)}`)
  console.log(`Critical attention: ${summary.criticalRepos.join(', ') || 'none'}`)
  console.log(`Clean: ${summary.cleanRepos.join(', ') || 'none'}`)
  console.log(`Snapshot: ${reportPath}`)
}
if (useAI) { console.log('\n## AI Reconciliation\n'); console.log(await aiSummary(states)) }
