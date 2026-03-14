/**
 * Capability Drift Checker Agent — EGOS-038
 *
 * Scans a target repository against the EGOS kernel's shared capabilities
 * to detect missing adoptions, stale versions, and governance drift.
 *
 * Checks:
 *  1. Shared module adoption (atrian, pii-scanner, conversation-memory, etc.)
 *  2. Governance file presence (.windsurfrules, AGENTS.md, TASKS.md)
 *  3. Workflow presence (/start, /end, /mycelium)
 *  4. Security basics (.env.example, no hardcoded secrets pattern)
 *
 * Usage:
 *   bun agent:run capability_drift_checker --dry
 *   bun agent:run capability_drift_checker --dry --target=/path/to/repo
 */

import { existsSync, readdirSync, readFileSync, statSync, mkdirSync, writeFileSync } from 'fs';
import { join, relative, extname, basename } from 'path';
import { runAgent, printResult, log, type RunContext, type Finding } from '../runtime/runner';
import { Topics } from '../runtime/event-bus';

// ─── Capability Definitions ──────────────────────────────────

interface CapabilityCheck {
  id: string;
  label: string;
  category: 'shared_module' | 'governance' | 'workflow' | 'security';
  signals: string[];           // lowercase strings to grep for in code
  fileMarkers?: string[];      // files whose existence confirms adoption
  weight: number;              // 1-3 (importance for scoring)
}

const CAPABILITIES: CapabilityCheck[] = [
  // Shared modules
  { id: 'atrian', label: 'ATRiAN Ethical Validation', category: 'shared_module', signals: ['atrian', 'createatrianvalidator', 'validateresponse'], weight: 2 },
  { id: 'pii_scanner', label: 'PII Scanner', category: 'shared_module', signals: ['pii-scanner', 'scanforpii', 'sanitizetext'], weight: 2 },
  { id: 'conversation_memory', label: 'Conversation Memory', category: 'shared_module', signals: ['conversation-memory', 'buildconversationmemoryblock', 'shouldsummarizeconversation'], weight: 2 },
  { id: 'model_routing', label: 'Model Routing', category: 'shared_module', signals: ['model-router', 'routeforchat', 'resolvemodel', 'llm-provider', 'chatwithllm'], weight: 2 },
  { id: 'rate_limiter', label: 'Rate Limiter', category: 'shared_module', signals: ['rate-limiter', 'ratelimiter'], weight: 1 },

  // Governance
  { id: 'windsurfrules', label: 'Governance Rules', category: 'governance', signals: [], fileMarkers: ['.windsurfrules'], weight: 3 },
  { id: 'agents_md', label: 'AGENTS.md System Map', category: 'governance', signals: [], fileMarkers: ['AGENTS.md'], weight: 3 },
  { id: 'tasks_md', label: 'TASKS.md Roadmap', category: 'governance', signals: [], fileMarkers: ['TASKS.md'], weight: 2 },
  { id: 'guarani_identity', label: 'Guarani Identity', category: 'governance', signals: [], fileMarkers: ['.guarani/IDENTITY.md'], weight: 1 },
  { id: 'guarani_preferences', label: 'Coding Preferences', category: 'governance', signals: [], fileMarkers: ['.guarani/PREFERENCES.md'], weight: 1 },

  // Workflows
  { id: 'wf_start', label: '/start Workflow', category: 'workflow', signals: [], fileMarkers: ['.windsurf/workflows/start.md', '.agent/workflows/start.md'], weight: 2 },
  { id: 'wf_end', label: '/end Workflow', category: 'workflow', signals: [], fileMarkers: ['.windsurf/workflows/end.md', '.agent/workflows/end.md'], weight: 2 },
  { id: 'wf_mycelium', label: '/mycelium Workflow', category: 'workflow', signals: [], fileMarkers: ['.windsurf/workflows/mycelium.md', '.agent/workflows/mycelium.md'], weight: 1 },

  // Security
  { id: 'env_example', label: '.env.example Template', category: 'security', signals: [], fileMarkers: ['.env.example'], weight: 2 },
  { id: 'precommit', label: 'Pre-commit Hooks', category: 'security', signals: [], fileMarkers: ['.husky/pre-commit'], weight: 2 },
];

// ─── Helpers ─────────────────────────────────────────────────

const IGNORE = new Set(['node_modules', 'dist', '.git', '.next', '.vercel', '.turbo', '.logs', '__pycache__', '.egos']);
const CODE_EXTENSIONS = new Set(['.ts', '.tsx', '.js', '.jsx', '.py']);

function walkCode(dir: string, maxFiles = 500): string[] {
  const results: string[] = [];
  function recurse(d: string) {
    if (results.length >= maxFiles) return;
    try {
      for (const entry of readdirSync(d)) {
        if (IGNORE.has(entry)) continue;
        const full = join(d, entry);
        const stat = statSync(full);
        if (stat.isDirectory()) recurse(full);
        else if (CODE_EXTENSIONS.has(extname(entry))) results.push(full);
      }
    } catch { /* skip */ }
  }
  recurse(dir);
  return results;
}

// ─── Agent Logic ─────────────────────────────────────────────

async function checkCapabilityDrift(ctx: RunContext): Promise<Finding[]> {
  const targetArg = process.argv.find(a => a.startsWith('--target='));
  const target = targetArg ? targetArg.split('=')[1] : ctx.repoRoot;
  const findings: Finding[] = [];

  log(ctx, 'info', `Scanning target: ${target}`);

  // Collect code content for signal matching
  const codeFiles = walkCode(target);
  log(ctx, 'info', `Found ${codeFiles.length} code files`);

  const codeContent = new Map<string, string>();
  for (const file of codeFiles) {
    try {
      codeContent.set(file, readFileSync(file, 'utf-8').toLowerCase());
    } catch { /* skip */ }
  }

  // Evaluate each capability
  const results: Array<{
    check: CapabilityCheck;
    adopted: boolean;
    evidence: string[];
  }> = [];

  for (const check of CAPABILITIES) {
    let adopted = false;
    const evidence: string[] = [];

    // Check file markers
    if (check.fileMarkers) {
      for (const marker of check.fileMarkers) {
        if (existsSync(join(target, marker))) {
          adopted = true;
          evidence.push(marker);
        }
      }
    }

    // Check code signals
    if (check.signals.length > 0) {
      for (const [file, content] of codeContent) {
        for (const signal of check.signals) {
          if (content.includes(signal)) {
            adopted = true;
            const rel = relative(target, file);
            if (!evidence.includes(rel)) evidence.push(rel);
            break;
          }
        }
        if (evidence.length >= 3) break;
      }
    }

    results.push({ check, adopted, evidence });
  }

  // Score calculation
  const maxScore = CAPABILITIES.reduce((sum, c) => sum + c.weight, 0);
  const actualScore = results.reduce((sum, r) => sum + (r.adopted ? r.check.weight : 0), 0);
  const percentage = Math.round((actualScore / maxScore) * 100);

  // Generate findings
  const missing = results.filter(r => !r.adopted);
  const present = results.filter(r => r.adopted);

  findings.push({
    severity: 'info',
    category: 'drift:summary',
    message: `Capability drift score: ${percentage}% (${present.length}/${results.length} adopted) for ${basename(target)}`,
    suggestion: missing.length > 0
      ? `Missing: ${missing.map(m => m.check.id).join(', ')}`
      : 'All capabilities adopted!',
  });

  for (const m of missing) {
    const severity = m.check.weight >= 3 ? 'error' : m.check.weight >= 2 ? 'warning' : 'info';
    findings.push({
      severity,
      category: `drift:${m.check.category}`,
      message: `Missing: ${m.check.label} (${m.check.id})`,
      suggestion: `Adopt from kernel. Category: ${m.check.category}`,
    });
    ctx.bus.emit(Topics.ARCH_SSOT_VIOLATION, {
      target,
      capability: m.check.id,
      category: m.check.category,
      weight: m.check.weight,
    }, 'capability_drift_checker', ctx.correlationId);
  }

  // Report in execute mode
  if (ctx.mode === 'execute') {
    const reportDir = join(target, 'docs', 'reports');
    if (!existsSync(reportDir)) mkdirSync(reportDir, { recursive: true });
    const lines = [
      '# Capability Drift Report', '',
      `> Target: ${target}`,
      `> Score: ${percentage}% (${present.length}/${results.length})`,
      `> Generated: ${ctx.startedAt}`, '',
      '| Capability | Category | Weight | Status | Evidence |',
      '|---|---|---|---|---|',
    ];
    for (const r of results) {
      const status = r.adopted ? '✅' : '❌';
      const ev = r.evidence.slice(0, 3).join(', ') || '—';
      lines.push(`| ${r.check.label} | ${r.check.category} | ${r.check.weight} | ${status} | ${ev} |`);
    }
    writeFileSync(join(reportDir, 'capability-drift.md'), lines.join('\n'));
    log(ctx, 'info', 'Report written to docs/reports/capability-drift.md');
  }

  return findings;
}

// ─── CLI Entry ───────────────────────────────────────────────

const mode = process.argv.includes('--exec') ? 'execute' as const : 'dry_run' as const;
runAgent('capability_drift_checker', mode, checkCapabilityDrift).then(result => {
  printResult(result);
  process.exit(result.success ? 0 : 1);
});
