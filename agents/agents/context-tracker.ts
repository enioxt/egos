/**
 * Context Tracker Agent — EGOS-060
 *
 * Estimates the remaining usable context window for the current IDE chat session
 * by counting committed + staged + unstaged file changes, handoff sizes, and
 * agent output volume since the last commit.
 *
 * Outputs a CTX score (0–280) with zone emoji and a recommendation:
 *   🟢 SAFE   (0–100)    — continue normally
 *   🟡 WARN   (101–180)  — wrap up current subtask, plan /end
 *   🔴 HIGH   (181–250)  — start /end soon
 *   ⛔ CRITICAL (251+)   — execute /end NOW autonomously
 *
 * Usage:
 *   bun agent:run context_tracker --dry
 *   bun agent:run context_tracker --dry --target=/path/to/repo
 */

import { existsSync, readdirSync, readFileSync, statSync } from 'fs';
import { execSync } from 'child_process';
import { join, extname } from 'path';
import { runAgent, printResult, log, type RunContext, type Finding } from '../runtime/runner';

// ─── Scoring weights ──────────────────────────────────────
const WEIGHTS = {
  uncommitted_file: 4,       // each uncommitted file
  commit_since_session: 2,   // each commit in last 6 hours
  handoff_kb: 0.5,           // per KB of latest handoff
  code_files_changed: 1,     // per changed code file in git diff
  large_agent_run: 8,        // per agent that ran (proxy: findings in last report)
};

const ZONES = [
  { max: 100, emoji: '🟢', label: 'SAFE',     advice: 'Continue normally.' },
  { max: 180, emoji: '🟡', label: 'WARN',     advice: 'Wrap up current subtask. Plan /end.' },
  { max: 250, emoji: '🔴', label: 'HIGH',     advice: 'Start /end soon — commit + handoff.' },
  { max: Infinity, emoji: '⛔', label: 'CRITICAL', advice: 'Execute /end NOW autonomously.' },
] as const;

// ─── Helpers ─────────────────────────────────────────────

function gitExec(cmd: string, cwd: string): string {
  try {
    return execSync(cmd, { cwd, stdio: ['pipe', 'pipe', 'ignore'] }).toString().trim();
  } catch {
    return '';
  }
}

function countUncommitted(root: string): number {
  const out = gitExec('git status --short', root);
  return out ? out.split('\n').filter(l => l.trim()).length : 0;
}

function countSessionCommits(root: string): number {
  const out = gitExec("git log --oneline --since='6 hours ago'", root);
  return out ? out.split('\n').filter(l => l.trim()).length : 0;
}

function countChangedCodeFiles(root: string): number {
  const out = gitExec('git diff --name-only HEAD', root);
  if (!out) return 0;
  const codeExts = new Set(['.ts', '.tsx', '.js', '.py', '.sh', '.json', '.md']);
  return out.split('\n').filter(f => codeExts.has(extname(f))).length;
}

function latestHandoffKb(root: string): number {
  const dir = join(root, 'docs', '_current_handoffs');
  if (!existsSync(dir)) return 0;
  try {
    const files = readdirSync(dir)
      .filter(f => f.endsWith('.md'))
      .map(f => ({ f, mtime: statSync(join(dir, f)).mtimeMs }))
      .sort((a, b) => b.mtime - a.mtime);
    if (!files.length) return 0;
    const content = readFileSync(join(dir, files[0].f), 'utf-8');
    return content.length / 1024;
  } catch {
    return 0;
  }
}

function countRecentAgentRuns(root: string): number {
  const reportsDir = join(root, 'docs', 'reports');
  if (!existsSync(reportsDir)) return 0;
  try {
    const cutoff = Date.now() - 6 * 60 * 60 * 1000;
    return readdirSync(reportsDir)
      .filter(f => f.endsWith('.md') && statSync(join(reportsDir, f)).mtimeMs > cutoff)
      .length;
  } catch {
    return 0;
  }
}

// ─── Agent Logic ─────────────────────────────────────────

async function trackContext(ctx: RunContext): Promise<Finding[]> {
  const targetArg = process.argv.find(a => a.startsWith('--target='));
  const root = targetArg ? targetArg.split('=')[1] : ctx.repoRoot;
  const findings: Finding[] = [];

  const uncommitted   = countUncommitted(root);
  const sessionCommits = countSessionCommits(root);
  const codeChanged   = countChangedCodeFiles(root);
  const handoffKb     = latestHandoffKb(root);
  const agentRuns     = countRecentAgentRuns(root);

  const ctxScore = Math.min(280,
    uncommitted   * WEIGHTS.uncommitted_file +
    sessionCommits * WEIGHTS.commit_since_session +
    codeChanged   * WEIGHTS.code_files_changed +
    handoffKb     * WEIGHTS.handoff_kb +
    agentRuns     * WEIGHTS.large_agent_run,
  );

  const zone = ZONES.find(z => ctxScore <= z.max)!;

  log(ctx, ctxScore > 180 ? 'warn' : 'info',
    `CTX ${Math.round(ctxScore)}/280 ${zone.emoji} ${zone.label} — ${zone.advice}`);
  log(ctx, 'info',
    `Breakdown: uncommitted=${uncommitted} commits=${sessionCommits} code_changed=${codeChanged} handoff=${handoffKb.toFixed(1)}kb agent_runs=${agentRuns}`);

  findings.push({
    severity: ctxScore > 250 ? 'error' : ctxScore > 180 ? 'warning' : 'info',
    category: 'ctx:score',
    message: `CTX ${Math.round(ctxScore)}/280 ${zone.emoji} ${zone.label}`,
    suggestion: zone.advice,
  });

  if (ctxScore > 250) {
    findings.push({
      severity: 'error',
      category: 'ctx:action',
      message: 'CRITICAL: execute /end NOW — commit all work, create handoff, switch chat.',
      suggestion: 'Run /end workflow immediately.',
    });
  } else if (ctxScore > 180) {
    findings.push({
      severity: 'warning',
      category: 'ctx:action',
      message: 'HIGH: plan /end for end of current subtask.',
      suggestion: 'Finish current task, then run /end.',
    });
  }

  return findings;
}

// ─── CLI Entry ────────────────────────────────────────────

const mode = process.argv.includes('--exec') ? 'execute' as const : 'dry_run' as const;
runAgent('context_tracker', mode, trackContext).then(result => {
  printResult(result);
  process.exit(result.success ? 0 : 1);
});
