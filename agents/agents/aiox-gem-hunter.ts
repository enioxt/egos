/**
 * AIOX Gem Hunter Agent — EGOS-109
 *
 * Purpose:
 * - Analyze SynkraAI/aiox-core surfaces for reusable orchestration gems
 * - Cross-check local NotebookLM export artifacts used during EGOS commons prep
 * - Emit an actionable keep/drop implementation diagnosis for EGOS kernel
 *
 * Usage:
 *   bun agent:run aiox_gem_hunter --dry
 *   bun agent:run aiox_gem_hunter --exec
 */

import { existsSync, readFileSync } from 'fs';
import { join } from 'path';
import { runAgent, printResult, log, type Finding, type RunContext } from '../runtime/runner';

interface RepoInfo { default_branch: string; stargazers_count: number; pushed_at: string; html_url: string }
interface TreeNode { path: string; type: 'blob' | 'tree' }

const TARGET = { owner: 'SynkraAI', repo: 'aiox-core' };
const KEYWORDS = {
  squads: /\bsquad(s)?\b|multi-agent|team of agents/i,
  worktree: /\bworktree(s)?\b|parallel development|parallel lanes/i,
  specPipeline: /\banalyst\b|\bpm\b|\barchitect\b|\bsm\b|PRD|spec pipeline/i,
  doctor: /\bdoctor\b|health check|installation check/i,
  installer: /\bnpx aiox-core\b|install|init|setup wizard/i,
};

const NOTEBOOK_HINTS = {
  commons: /commons|egos commons|\/commons/i,
  notebooklm: /NotebookLM|notebooklm_export/i,
  gemHunter: /gem-hunter|gem hunter/i,
  worktree: /worktree/i,
  squad: /squad/i,
};

type KeywordKey = keyof typeof KEYWORDS;

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url, { headers: { 'User-Agent': 'egos-aiox-gem-hunter' } });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} @ ${url}`);
  return await res.json() as T;
}

function candidateFile(path: string): boolean {
  return /(README|docs\/|guides\/|workflow|agent|squad|install|doctor)/i.test(path)
    && /\.(md|txt|json|ya?ml)$/i.test(path)
    && !/node_modules|dist|coverage/i.test(path);
}

function scanText(text: string): Record<KeywordKey, number> {
  const counts: Record<KeywordKey, number> = {
    squads: 0,
    worktree: 0,
    specPipeline: 0,
    doctor: 0,
    installer: 0,
  };

  for (const [k, regex] of Object.entries(KEYWORDS) as Array<[KeywordKey, RegExp]>) {
    const matches = text.match(new RegExp(regex.source, 'gim'));
    counts[k] = matches ? matches.length : 0;
  }

  return counts;
}

function aggregateCounts(items: Record<KeywordKey, number>[]): Record<KeywordKey, number> {
  const total: Record<KeywordKey, number> = {
    squads: 0,
    worktree: 0,
    specPipeline: 0,
    doctor: 0,
    installer: 0,
  };
  for (const row of items) {
    (Object.keys(total) as KeywordKey[]).forEach((k) => { total[k] += row[k]; });
  }
  return total;
}

function scanNotebookExport(repoRoot: string): Finding[] {
  const findings: Finding[] = [];
  const notebookPath = join(repoRoot, 'notebooklm_export_egos.md');

  if (!existsSync(notebookPath)) {
    findings.push({
      severity: 'warning',
      category: 'aiox:notebooklm-missing',
      message: 'notebooklm_export_egos.md not found in current repo root',
      suggestion: 'If Commons prep evidence exists elsewhere, add pointer in TASKS/HARVEST for deterministic retrieval.',
    });
    return findings;
  }

  const text = readFileSync(notebookPath, 'utf-8');
  const lines = text.split('\n');

  const counters = Object.entries(NOTEBOOK_HINTS).reduce((acc, [key, regex]) => {
    acc[key] = lines.reduce((n, line) => n + (regex.test(line) ? 1 : 0), 0);
    return acc;
  }, {} as Record<string, number>);

  findings.push({
    severity: 'info',
    category: 'aiox:notebooklm-scan',
    message: `NotebookLM export scanned: commons=${counters.commons}, notebooklm=${counters.notebooklm}, gem-hunter=${counters.gemHunter}, worktree=${counters.worktree}, squad=${counters.squad}`,
    file: 'notebooklm_export_egos.md',
    suggestion: 'Use these counts to prioritize migration into executable contracts, not narrative-only docs.',
  });

  if (counters.commons === 0) {
    findings.push({
      severity: 'warning',
      category: 'aiox:notebooklm-gap',
      message: 'No explicit Commons hits found in notebooklm_export_egos.md',
      file: 'notebooklm_export_egos.md',
      suggestion: 'Backfill Commons prep decisions into TASKS/HARVEST with task IDs and owner.',
    });
  }

  return findings;
}

async function runHunt(ctx: RunContext): Promise<Finding[]> {
  const findings: Finding[] = [];
  const { owner, repo } = TARGET;

  log(ctx, 'info', `Scanning ${owner}/${repo} for reusable gems`);

  const meta = await getJson<RepoInfo>(`https://api.github.com/repos/${owner}/${repo}`);
  findings.push({
    severity: 'info',
    category: 'aiox:repo-meta',
    message: `${owner}/${repo} stars=${meta.stargazers_count}, default_branch=${meta.default_branch}, pushed_at=${meta.pushed_at}`,
    suggestion: `Reference source: ${meta.html_url}`,
  });

  const treeResp = await getJson<{ tree: TreeNode[] }>(
    `https://api.github.com/repos/${owner}/${repo}/git/trees/${meta.default_branch}?recursive=1`
  ).catch(() => ({ tree: [] as TreeNode[] }));

  const candidates = treeResp.tree.filter(n => n.type === 'blob' && candidateFile(n.path)).slice(0, 120);
  const scanned: Array<{ path: string; counts: Record<KeywordKey, number> }> = [];

  for (const node of candidates) {
    const rawUrl = `https://raw.githubusercontent.com/${owner}/${repo}/${meta.default_branch}/${node.path}`;
    const txt = await fetch(rawUrl, { headers: { 'User-Agent': 'egos-aiox-gem-hunter' } })
      .then(r => (r.ok ? r.text() : ''))
      .catch(() => '');
    if (!txt) continue;

    const counts = scanText(txt);
    const score = Object.values(counts).reduce((a, b) => a + b, 0);
    if (score > 0) scanned.push({ path: node.path, counts });
  }

  const aggregate = aggregateCounts(scanned.map(s => s.counts));
  findings.push({
    severity: 'info',
    category: 'aiox:signal-summary',
    message: `Signals in ${scanned.length} files: squads=${aggregate.squads}, worktree=${aggregate.worktree}, spec_pipeline=${aggregate.specPipeline}, doctor=${aggregate.doctor}, installer=${aggregate.installer}`,
    suggestion: 'Keep only high-signal primitives that reduce lead time and preserve governance discipline.',
  });

  const top = scanned
    .map(s => ({ path: s.path, score: Object.values(s.counts).reduce((a, b) => a + b, 0) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 6)
    .map(s => `${s.path}(${s.score})`)
    .join(', ');

  findings.push({
    severity: 'info',
    category: 'aiox:top-files',
    message: `Top files for gem extraction: ${top || 'none'}`,
    suggestion: 'Use these as source-of-truth when drafting bridge contracts and validating no-bloat adoption.',
  });

  findings.push({
    severity: 'info',
    category: 'aiox:keep-drop',
    message: 'Recommended KEEP: squads pattern, worktree orchestration, spec pipeline, doctor installer checks. Recommended DROP: pro-lock features, memory-layer coupling, mandatory external platform dependencies.',
    suggestion: 'Route implementation into isolated contracts/workflows first, then run pr:gate evidence validation before merge.',
  });

  findings.push(...scanNotebookExport(ctx.repoRoot));

  return findings;
}

const mode = process.argv.includes('--exec') ? 'execute' as const : 'dry_run' as const;
runAgent('aiox_gem_hunter', mode, runHunt).then((result) => {
  printResult(result);
  process.exit(result.success ? 0 : 1);
});
