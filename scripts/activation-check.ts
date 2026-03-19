#!/usr/bin/env bun
/**
 * activation:check — Core Repo Activation Validator
 *
 * Verifies that all SSOT files, scripts, tools, env vars, and workflow
 * references are present and healthy before implementation work.
 *
 * Usage:
 *   bun scripts/activation-check.ts          # dry-run (report only)
 *   bun scripts/activation-check.ts --exec   # same (read-only check)
 */

import { existsSync, lstatSync, readFileSync, readlinkSync } from 'fs';
import { resolve } from 'path';
import { detectRepoRole, roleDescription } from '../packages/shared/src/repo-role';

const ROOT = resolve(import.meta.dir, '..');
const mode = process.argv.includes('--exec') ? 'exec' : 'dry';
const repoConfig = detectRepoRole(ROOT);
const HOME = process.env.HOME ?? '';
const SHARED_HOME = HOME ? resolve(HOME, '.egos') : '';

// ═══════════════════════════════════════════════════════════
// Required Files
// ═══════════════════════════════════════════════════════════

const REQUIRED_FILES = [
  // SSOT
  { path: '.windsurfrules', label: 'Governance rules' },
  { path: 'AGENTS.md', label: 'System map' },
  { path: 'TASKS.md', label: 'Task registry' },
  { path: 'CONTRIBUTING.md', label: 'Contribution guide' },
  { path: '.env', label: 'Environment variables' },
  { path: '.env.example', label: 'Env template' },
  // Governance DNA
  { path: '.guarani/IDENTITY.md', label: 'Agent identity' },
  { path: '.guarani/PREFERENCES.md', label: 'Coding standards' },
  { path: '.guarani/orchestration/PIPELINE.md', label: 'Orchestration pipeline' },
  { path: '.guarani/orchestration/GATES.md', label: 'Quality gates' },
  { path: '.guarani/orchestration/QUESTION_BANK.md', label: 'Question bank' },
  { path: '.guarani/orchestration/DOMAIN_RULES.md', label: 'Domain rules' },
  // Prompts
  { path: '.guarani/prompts/PROMPT_SYSTEM.md', label: 'Prompt system' },
  { path: '.guarani/prompts/meta/universal-strategist.md', label: 'Meta: Strategist' },
  { path: '.guarani/prompts/meta/brainet-collective.md', label: 'Meta: Brainet' },
  { path: '.guarani/prompts/meta/mycelium-orchestrator.md', label: 'Meta: Mycelium' },
  { path: '.guarani/prompts/meta/ecosystem-audit.md', label: 'Meta: Audit' },
  // Agent runtime
  { path: 'agents/runtime/runner.ts', label: 'Agent runner (frozen)' },
  { path: 'agents/runtime/event-bus.ts', label: 'Event bus (frozen)' },
  { path: 'agents/registry/agents.json', label: 'Agent registry' },
  { path: 'agents/cli.ts', label: 'Agent CLI' },
  // Shared packages
  { path: 'packages/shared/src/llm-provider.ts', label: 'LLM provider' },
  { path: 'packages/shared/src/model-router.ts', label: 'Model router' },
  { path: 'packages/shared/src/types.ts', label: 'Shared types' },
  { path: 'packages/shared/src/index.ts', label: 'Shared barrel' },
  { path: 'packages/shared/src/mycelium/reference-graph.ts', label: 'Reference graph' },
  // Docs
  { path: 'docs/SYSTEM_MAP.md', label: 'System map' },
  { path: 'docs/CAPABILITY_REGISTRY.md', label: 'Capability registry' },
  { path: 'docs/modules/CHATBOT_SSOT.md', label: 'Chatbot SSOT' },
  // Workflows
  { path: '.windsurf/workflows/start.md', label: '/start workflow' },
  { path: '.windsurf/workflows/end.md', label: '/end workflow' },
  { path: '.windsurf/workflows/mycelium.md', label: '/mycelium workflow' },
  // Scripts
  { path: 'scripts/governance-sync.sh', label: 'Governance sync' },
];

// ═══════════════════════════════════════════════════════════
// Required Env Vars
// ═══════════════════════════════════════════════════════════

const REQUIRED_ENV = [
  'ALIBABA_DASHSCOPE_API_KEY',
  'OPENROUTER_API_KEY',
];

const OPTIONAL_ENV = [
  'OPENAI_API_KEY',
  'GROQ_API_KEY',
  'SERPER_API_KEY',
  'BRAVE_API',
  'EXA_API_KEY',
  'GITHUB_TOKEN',
  'STITCH_API_KEY',
];

// ═══════════════════════════════════════════════════════════
// Check Logic
// ═══════════════════════════════════════════════════════════

interface CheckResult {
  category: string;
  item: string;
  status: 'ok' | 'warn' | 'fail';
  detail?: string;
}

const results: CheckResult[] = [];

// File checks
for (const f of REQUIRED_FILES) {
  const full = resolve(ROOT, f.path);
  if (existsSync(full)) {
    results.push({ category: 'file', item: f.label, status: 'ok' });
  } else {
    results.push({ category: 'file', item: f.label, status: 'fail', detail: f.path });
  }
}

// Env checks
for (const key of REQUIRED_ENV) {
  if (process.env[key]) {
    results.push({ category: 'env', item: key, status: 'ok' });
  } else {
    results.push({ category: 'env', item: key, status: 'fail', detail: 'not set' });
  }
}

for (const key of OPTIONAL_ENV) {
  if (process.env[key]) {
    results.push({ category: 'env', item: key, status: 'ok' });
  } else {
    results.push({ category: 'env', item: key, status: 'warn', detail: 'optional, not set' });
  }
}

const SHARED_MIRRORS = [
  { local: '.guarani/PREFERENCES.md', shared: 'guarani/PREFERENCES.md', item: 'Shared preferences mirror' },
  { local: '.windsurf/workflows/start.md', shared: 'workflows/start.md', item: 'Shared /start mirror' },
];

for (const mirror of SHARED_MIRRORS) {
  const localPath = resolve(ROOT, mirror.local);
  const sharedPath = resolve(SHARED_HOME, mirror.shared);
  if (!SHARED_HOME || !existsSync(sharedPath)) {
    results.push({ category: 'shared', item: mirror.item, status: 'warn', detail: `${mirror.shared} missing in ~/.egos` });
    continue;
  }
  const localContent = readFileSync(localPath, 'utf-8');
  const sharedContent = readFileSync(sharedPath, 'utf-8');
  results.push({
    category: 'shared',
    item: mirror.item,
    status: localContent === sharedContent ? 'ok' : 'fail',
    detail: localContent === sharedContent ? undefined : `${mirror.shared} drifted from kernel`,
  });
}

const LEAF_RULE_REPOS = ['egos-lab', '852', 'carteira-livre', 'br-acc', 'forja', 'egos-self'];
for (const repo of LEAF_RULE_REPOS) {
  const rulePath = resolve(HOME, repo, '.windsurfrules');
  if (!existsSync(rulePath)) continue;
  const isSharedSymlink = lstatSync(rulePath).isSymbolicLink() && readlinkSync(rulePath) === `${SHARED_HOME}/.windsurfrules`;
  results.push({
    category: 'shared',
    item: `${repo} .windsurfrules isolation`,
    status: isSharedSymlink ? 'fail' : 'ok',
    detail: isSharedSymlink ? 'repo-local rules are shadowed by ~/.egos/.windsurfrules' : undefined,
  });
}

// ═══════════════════════════════════════════════════════════
// Output
// ═══════════════════════════════════════════════════════════

const ok = results.filter(r => r.status === 'ok').length;
const warn = results.filter(r => r.status === 'warn').length;
const fail = results.filter(r => r.status === 'fail').length;
const total = results.length;
const score = Math.round((ok / total) * 100);

console.log(`\n  EGOS Activation Check (${mode} mode)\n`);
console.log(`  Repo: ${repoConfig.role} v${repoConfig.version}`);
console.log(`  Score: ${score}% (${ok}/${total} OK, ${warn} warnings, ${fail} failures)\n`);

if (fail > 0) {
  console.log('  FAILURES:');
  for (const r of results.filter(r => r.status === 'fail')) {
    console.log(`    ❌ [${r.category}] ${r.item} — ${r.detail}`);
  }
  console.log('');
}

if (warn > 0) {
  console.log('  WARNINGS:');
  for (const r of results.filter(r => r.status === 'warn')) {
    console.log(`    ⚠️  [${r.category}] ${r.item} — ${r.detail}`);
  }
  console.log('');
}

if (fail === 0) {
  console.log('  ✅ Activation check passed — kernel is ready for implementation work.\n');
} else {
  console.log(`  ⛔ ${fail} failure(s) — fix before proceeding.\n`);
  process.exit(1);
}
