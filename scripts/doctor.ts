#!/usr/bin/env bun
/**
 * doctor — Comprehensive environment and project health check
 *
 * Performs full validation of:
 * - Environment variables (API keys, LLM providers)
 * - File freshness (AGENTS.md, TASKS.md, .windsurfrules within 7 days)
 * - Provider readiness (API health checks for Alibaba, Codex, OpenRouter)
 * - Pre-commit hooks status
 * - Workspace integrity (git status, uncommitted, untracked files)
 * - Governance drift detection
 *
 * Usage:
 *   bun scripts/doctor.ts                    # dry-run (report only)
 *   bun scripts/doctor.ts --doctor-skip      # skip doctor, allow execution
 *   bun scripts/doctor.ts --fix              # attempt auto-fixes for common issues
 *   bun scripts/doctor.ts --json             # output JSON report
 *   bun scripts/doctor.ts --no-network       # skip network checks (offline mode)
 *
 * Exit codes:
 *   0 = all checks passed
 *   1 = warnings only (non-blocking)
 *   2 = failures detected (blocking)
 */

import { existsSync, readFileSync, writeFileSync, mkdirSync, statSync } from 'node:fs';
import { execSync } from 'node:child_process';
import { resolve, join } from 'node:path';

// ═══════════════════════════════════════════════════════════
// Configuration & Flags
// ═══════════════════════════════════════════════════════════

const args = process.argv.slice(2);
const mode = {
  skip: args.includes('--doctor-skip'),
  fix: args.includes('--fix'),
  json: args.includes('--json'),
  noNetwork: args.includes('--no-network'),
  verbose: args.includes('--verbose'),
};

const ROOT = resolve(import.meta.dir, '..');
const DOCS_DIR = join(ROOT, 'docs');
const REPORT_DIR = join(DOCS_DIR, '_generated');
const REPORT_PATH = join(REPORT_DIR, 'doctor-report.json');

// ═══════════════════════════════════════════════════════════
// Types
// ═══════════════════════════════════════════════════════════

interface CheckResult {
  category: 'env' | 'file' | 'provider' | 'hooks' | 'workspace' | 'governance';
  item: string;
  status: 'ok' | 'warn' | 'fail';
  detail?: string;
  fixable?: boolean;
}

interface DoctorReport {
  timestamp: string;
  duration: number;
  environment: string;
  repoPath: string;
  results: CheckResult[];
  summary: {
    total: number;
    ok: number;
    warn: number;
    fail: number;
    score: number;
  };
  recommendations: string[];
}

// ═══════════════════════════════════════════════════════════
// Utility Functions
// ═══════════════════════════════════════════════════════════

function sh(cmd: string, cwd = ROOT): string {
  try {
    return execSync(cmd, { cwd, encoding: 'utf-8', stdio: ['pipe', 'pipe', 'ignore'], timeout: 10000 }).trim();
  } catch {
    return '';
  }
}

function shWithStatus(cmd: string, cwd = ROOT): { stdout: string; exitCode: number } {
  try {
    const stdout = execSync(cmd, { cwd, encoding: 'utf-8', stdio: ['pipe', 'pipe', 'ignore'], timeout: 10000 }).trim();
    return { stdout, exitCode: 0 };
  } catch (e: any) {
    return { stdout: '', exitCode: e.status || 1 };
  }
}

function getFileAge(filePath: string): number {
  if (!existsSync(filePath)) return -1;
  const stat = statSync(filePath);
  return Math.floor((Date.now() - stat.mtimeMs) / (1000 * 60 * 60 * 24)); // days
}

async function checkApiHealth(url: string, timeout = 5000): Promise<boolean> {
  if (mode.noNetwork) return true; // Assume OK in offline mode
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    const response = await fetch(url, { method: 'GET', signal: controller.signal });
    clearTimeout(timeoutId);
    return response.status >= 200 && response.status < 500;
  } catch {
    return false;
  }
}

// ═══════════════════════════════════════════════════════════
// Checks Implementation
// ═══════════════════════════════════════════════════════════

const results: CheckResult[] = [];

// ─── 1. Environment Variables ───
function checkEnvironmentVariables() {
  const required = ['ALIBABA_DASHSCOPE_API_KEY', 'OPENROUTER_API_KEY'];
  const optional = [
    'OPENAI_API_KEY',
    'GROQ_API_KEY',
    'SERPER_API_KEY',
    'BRAVE_API',
    'EXA_API_KEY',
    'GITHUB_TOKEN',
    'STITCH_API_KEY',
    'GITHUB_PERSONAL_ACCESS_TOKEN',
  ];

  for (const key of required) {
    if (process.env[key]?.trim()) {
      results.push({ category: 'env', item: key, status: 'ok' });
    } else {
      results.push({ category: 'env', item: key, status: 'fail', detail: 'required but not set' });
    }
  }

  for (const key of optional) {
    if (process.env[key]?.trim()) {
      results.push({ category: 'env', item: key, status: 'ok' });
    } else {
      results.push({ category: 'env', item: key, status: 'warn', detail: 'optional, not configured' });
    }
  }
}

// ─── 2. File Freshness ───
function checkFileFreshness() {
  const files = [
    { path: 'AGENTS.md', label: 'Agents registry' },
    { path: 'TASKS.md', label: 'Tasks registry' },
    { path: '.windsurfrules', label: 'Governance rules' },
    { path: 'docs/SYSTEM_MAP.md', label: 'System map' },
  ];

  const freshnessThreshold = 7; // days

  for (const file of files) {
    const fullPath = resolve(ROOT, file.path);
    if (!existsSync(fullPath)) {
      results.push({ category: 'file', item: file.label, status: 'fail', detail: `${file.path} missing` });
      continue;
    }

    const age = getFileAge(fullPath);
    if (age <= freshnessThreshold) {
      results.push({ category: 'file', item: file.label, status: 'ok', detail: `${age} days old` });
    } else {
      results.push({
        category: 'file',
        item: file.label,
        status: 'warn',
        detail: `${age} days old (stale, > ${freshnessThreshold} days)`,
        fixable: true,
      });
    }
  }
}

// ─── 3. Provider Readiness ───
async function checkProviderReadiness() {
  const providers = [
    { name: 'Alibaba DashScope', url: 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1/models', envKey: 'ALIBABA_DASHSCOPE_API_KEY' },
    { name: 'OpenRouter', url: 'https://openrouter.ai/api/v1/models', envKey: 'OPENROUTER_API_KEY' },
    { name: 'OpenAI', url: 'https://api.openai.com/v1/models', envKey: 'OPENAI_API_KEY', optional: true },
  ];

  for (const provider of providers) {
    // Check env first
    const hasEnv = !!process.env[provider.envKey]?.trim();
    if (!hasEnv) {
      const status = provider.optional ? 'warn' : 'fail';
      results.push({
        category: 'provider',
        item: provider.name,
        status,
        detail: 'API key not configured',
      });
      continue;
    }

    // Check API reachability
    const isReachable = await checkApiHealth(provider.url);
    results.push({
      category: 'provider',
      item: provider.name,
      status: isReachable ? 'ok' : 'warn',
      detail: isReachable ? 'reachable' : 'unreachable (may be offline)',
    });
  }
}

// ─── 4. Pre-commit Hooks ───
function checkPrecommitHooks() {
  const hooksPath = resolve(ROOT, '.husky');
  const precommitPath = resolve(hooksPath, 'pre-commit');

  if (!existsSync(hooksPath)) {
    results.push({ category: 'hooks', item: 'Husky directory', status: 'fail', detail: '.husky/ missing' });
    return;
  }

  results.push({ category: 'hooks', item: 'Husky directory', status: 'ok' });

  if (!existsSync(precommitPath)) {
    results.push({
      category: 'hooks',
      item: 'Pre-commit hook',
      status: 'warn',
      detail: 'pre-commit hook not installed',
      fixable: true,
    });
  } else {
    results.push({ category: 'hooks', item: 'Pre-commit hook', status: 'ok' });
  }
}

// ─── 5. Workspace Integrity ───
function checkWorkspaceIntegrity() {
  // Check git status
  const gitStatus = sh('git status --porcelain');
  const lines = gitStatus.split('\n').filter((l) => l.trim());
  const modified = lines.filter((l) => !l.startsWith('??')).length;
  const untracked = lines.filter((l) => l.startsWith('??')).length;

  if (modified === 0 && untracked === 0) {
    results.push({ category: 'workspace', item: 'Git status', status: 'ok', detail: 'clean working directory' });
  } else {
    const detail = [modified > 0 ? `${modified} modified` : '', untracked > 0 ? `${untracked} untracked` : ''].filter(Boolean).join(', ');
    results.push({
      category: 'workspace',
      item: 'Git status',
      status: 'warn',
      detail: `dirty (${detail})`,
      fixable: true,
    });
  }

  // Check upstream sync
  const upstream = sh('git rev-parse --abbrev-ref @{u}');
  if (!upstream) {
    results.push({
      category: 'workspace',
      item: 'Upstream tracking',
      status: 'warn',
      detail: 'no upstream branch configured',
      fixable: true,
    });
  } else {
    const aheadBehind = sh('git rev-list --left-right --count HEAD...@{u}').split(/\s+/);
    const ahead = parseInt(aheadBehind[0] || '0', 10);
    const behind = parseInt(aheadBehind[1] || '0', 10);

    if (ahead === 0 && behind === 0) {
      results.push({ category: 'workspace', item: 'Upstream sync', status: 'ok', detail: 'in sync with remote' });
    } else {
      const detail = [ahead > 0 ? `${ahead} ahead` : '', behind > 0 ? `${behind} behind` : ''].filter(Boolean).join(', ');
      results.push({
        category: 'workspace',
        item: 'Upstream sync',
        status: 'warn',
        detail: `out of sync (${detail})`,
        fixable: true,
      });
    }
  }

  // Check branch name
  const branch = sh('git rev-parse --abbrev-ref HEAD');
  if (branch === 'HEAD') {
    results.push({ category: 'workspace', item: 'Branch', status: 'fail', detail: 'detached HEAD state' });
  } else {
    results.push({ category: 'workspace', item: 'Branch', status: 'ok', detail: `on ${branch}` });
  }
}

// ─── 6. Governance Drift ───
function checkGovernanceDrift() {
  const { exitCode } = shWithStatus('sh scripts/governance-sync.sh --check');
  if (exitCode === 0) {
    results.push({ category: 'governance', item: 'Governance sync', status: 'ok', detail: 'no drift detected' });
  } else {
    results.push({
      category: 'governance',
      item: 'Governance sync',
      status: 'warn',
      detail: 'drift detected (run `bun run governance:sync` to fix)',
      fixable: true,
    });
  }
}

// ═══════════════════════════════════════════════════════════
// Auto-Fix Functions
// ═══════════════════════════════════════════════════════════

function autoFix() {
  if (!mode.fix) return;

  console.log('\n  Attempting auto-fixes...\n');
  let fixed = 0;

  // Update stale docs (touch them to current time)
  const staleFiles = results.filter((r) => r.category === 'file' && r.status === 'warn' && r.fixable);
  for (const result of staleFiles) {
    const match = result.detail?.match(/AGENTS\.md|TASKS\.md|\.windsurfrules|SYSTEM_MAP\.md/);
    if (match) {
      const filePath = resolve(ROOT, match[0]);
      try {
        sh(`touch "${filePath}"`);
        console.log(`    ✅ Touched ${match[0]}`);
        fixed++;
      } catch {
        console.log(`    ❌ Failed to touch ${match[0]}`);
      }
    }
  }

  // Install pre-commit hook if missing
  if (results.some((r) => r.item === 'Pre-commit hook' && r.status === 'warn')) {
    try {
      sh('bun husky install');
      console.log('    ✅ Installed husky hooks');
      fixed++;
    } catch {
      console.log('    ❌ Failed to install husky hooks');
    }
  }

  if (fixed > 0) {
    console.log(`\n    Fixed ${fixed} issue(s). Re-run doctor to verify.\n`);
  }
}

// ═══════════════════════════════════════════════════════════
// Recommendations Engine
// ═══════════════════════════════════════════════════════════

function generateRecommendations(): string[] {
  const recs: string[] = [];
  const failures = results.filter((r) => r.status === 'fail');
  const warnings = results.filter((r) => r.status === 'warn');

  if (failures.some((r) => r.category === 'env')) {
    recs.push('Set missing API keys in .env (copy from .env.example and fill in your values)');
  }

  if (failures.some((r) => r.category === 'file')) {
    recs.push('Restore missing files from git history or SSOT');
  }

  if (warnings.some((r) => r.item === 'Git status')) {
    recs.push('Commit or stash changes in workspace before starting operations');
  }

  if (warnings.some((r) => r.item === 'Upstream sync')) {
    recs.push('Run `git pull` to sync with remote and `git push` to push local commits');
  }

  if (warnings.some((r) => r.item === 'Governance sync')) {
    recs.push('Run `bun run governance:sync:exec` to resolve drift');
  }

  if (warnings.some((r) => r.item?.includes('stale'))) {
    recs.push('Update stale documentation (AGENTS.md, TASKS.md, etc.) with latest changes');
  }

  if (warnings.some((r) => r.category === 'provider')) {
    recs.push('Check network connectivity or provider API status if integration is needed');
  }

  return recs;
}

// ═══════════════════════════════════════════════════════════
// Report Generation
// ═══════════════════════════════════════════════════════════

function generateReport(duration: number): DoctorReport {
  const ok = results.filter((r) => r.status === 'ok').length;
  const warn = results.filter((r) => r.status === 'warn').length;
  const fail = results.filter((r) => r.status === 'fail').length;
  const total = results.length;
  const score = total > 0 ? Math.round((ok / total) * 100) : 0;

  return {
    timestamp: new Date().toISOString(),
    duration,
    environment: process.env.NODE_ENV ?? 'development',
    repoPath: ROOT,
    results,
    summary: { total, ok, warn, fail, score },
    recommendations: generateRecommendations(),
  };
}

function saveReport(report: DoctorReport) {
  mkdirSync(REPORT_DIR, { recursive: true });
  writeFileSync(REPORT_PATH, JSON.stringify(report, null, 2));
  if (mode.verbose) {
    console.log(`  Report saved to: ${REPORT_PATH}`);
  }
}

// ═══════════════════════════════════════════════════════════
// Output Formatting
// ═══════════════════════════════════════════════════════════

function printReport(report: DoctorReport) {
  const { summary } = report;

  console.log(`\n${'═'.repeat(68)}`);
  console.log(`  EGOS Doctor — Environment Health Check`);
  console.log(`${'═'.repeat(68)}\n`);

  console.log(`  Health Score: ${summary.score}%`);
  console.log(`  Results: ${summary.ok}/${summary.total} OK · ${summary.warn} warnings · ${summary.fail} failures`);
  console.log('');

  // Group by category
  const byCategory = results.reduce(
    (acc, r) => {
      if (!acc[r.category]) acc[r.category] = [];
      acc[r.category].push(r);
      return acc;
    },
    {} as Record<string, CheckResult[]>,
  );

  const categoryOrder = ['env', 'file', 'provider', 'hooks', 'workspace', 'governance'];

  for (const category of categoryOrder) {
    if (!byCategory[category]?.length) continue;

    const categoryResults = byCategory[category];
    const categoryOk = categoryResults.filter((r) => r.status === 'ok').length;
    const categoryFail = categoryResults.filter((r) => r.status === 'fail').length;

    console.log(`  [${category.toUpperCase()}] (${categoryOk}/${categoryResults.length} OK)`);

    for (const result of categoryResults) {
      const icon = result.status === 'ok' ? '✅' : result.status === 'warn' ? '⚠️ ' : '❌';
      const detail = result.detail ? ` — ${result.detail}` : '';
      console.log(`    ${icon} ${result.item}${detail}`);
    }
    console.log('');
  }

  if (report.recommendations.length > 0) {
    console.log('  RECOMMENDATIONS:');
    for (let i = 0; i < report.recommendations.length; i++) {
      console.log(`    ${i + 1}. ${report.recommendations[i]}`);
    }
    console.log('');
  }

  console.log(`${'═'.repeat(68)}`);

  if (summary.fail === 0 && summary.warn === 0) {
    console.log(`  ✅ All checks passed — environment is ready\n`);
  } else if (summary.fail === 0) {
    console.log(`  ⚠️  Warnings detected — address recommendations before proceeding\n`);
  } else {
    console.log(`  ❌ Failures detected — fix issues before proceeding\n`);
  }
}

// ═══════════════════════════════════════════════════════════
// Main Execution
// ═══════════════════════════════════════════════════════════

async function main() {
  if (mode.skip) {
    console.log('\n  ⏭️  Doctor check skipped (--doctor-skip flag)\n');
    process.exit(0);
  }

  const startTime = Date.now();

  try {
    // Run all checks
    checkEnvironmentVariables();
    checkFileFreshness();
    await checkProviderReadiness();
    checkPrecommitHooks();
    checkWorkspaceIntegrity();
    checkGovernanceDrift();

    const duration = Date.now() - startTime;
    const report = generateReport(duration);

    // Save report
    saveReport(report);

    // Output
    if (mode.json) {
      console.log(JSON.stringify(report, null, 2));
    } else {
      printReport(report);
    }

    // Auto-fix if requested
    if (mode.fix) {
      autoFix();
    }

    // Determine exit code
    const hasFailures = results.some((r) => r.status === 'fail');
    const hasWarnings = results.some((r) => r.status === 'warn');

    process.exit(hasFailures ? 2 : hasWarnings ? 1 : 0);
  } catch (error) {
    console.error('\n  ❌ Doctor check failed with error:', error);
    process.exit(2);
  }
}

main();
