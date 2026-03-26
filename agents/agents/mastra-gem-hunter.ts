/**
 * Mastra Gem Hunter — EGOS-115
 *
 * Extracts practical, non-bloat patterns from mastra-ai/mastra and maps
 * them to EGOS keep/drop adoption strategy.
 */

import { runAgent, printResult, log, type Finding, type RunContext } from '../runtime/runner';

interface RepoInfo { default_branch: string; stargazers_count: number; pushed_at: string }
interface TreeNode { path: string; type: 'blob' | 'tree' }

const TARGET = { owner: 'mastra-ai', repo: 'mastra' };
const SIGNALS = {
  workflow: /\.then\(|\.parallel\(|\.branch\(|workflow/i,
  evals: /evals?|model-graded|rule-based|statistical/i,
  observability: /observability|opentelemetry|tracing/i,
  mcp: /\bMCP\b|Model Context Protocol|tools-mcp/i,
  humanLoop: /human-in-the-loop|suspend|resume/i,
};

type SignalKey = keyof typeof SIGNALS;

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url, { headers: { 'User-Agent': 'egos-mastra-gem-hunter' } });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} @ ${url}`);
  return await res.json() as T;
}

function shouldScan(path: string): boolean {
  return /\.(md|ts|tsx|js|json|ya?ml)$/i.test(path)
    && /(readme|docs|packages|examples|workflow|eval|observability|mcp|memory|human)/i.test(path)
    && !/(node_modules|dist|coverage)/i.test(path);
}

async function runHunt(ctx: RunContext): Promise<Finding[]> {
  const findings: Finding[] = [];
  const { owner, repo } = TARGET;

  const meta = await getJson<RepoInfo>(`https://api.github.com/repos/${owner}/${repo}`);
  findings.push({
    severity: 'info',
    category: 'mastra:meta',
    message: `${owner}/${repo} stars=${meta.stargazers_count}, pushed_at=${meta.pushed_at}`,
    suggestion: 'Use as benchmark input; avoid full-stack copy into kernel.',
  });

  const tree = await getJson<{ tree: TreeNode[] }>(`https://api.github.com/repos/${owner}/${repo}/git/trees/${meta.default_branch}?recursive=1`)
    .catch(() => ({ tree: [] as TreeNode[] }));

  const files = tree.tree.filter(t => t.type === 'blob' && shouldScan(t.path)).slice(0, 140);
  log(ctx, 'info', `Scanning ${files.length} candidate files from ${owner}/${repo}`);

  const totals: Record<SignalKey, number> = {
    workflow: 0,
    evals: 0,
    observability: 0,
    mcp: 0,
    humanLoop: 0,
  };
  const sampleRefs: string[] = [];

  for (const file of files) {
    const raw = `https://raw.githubusercontent.com/${owner}/${repo}/${meta.default_branch}/${file.path}`;
    const txt = await fetch(raw, { headers: { 'User-Agent': 'egos-mastra-gem-hunter' } })
      .then(r => (r.ok ? r.text() : ''))
      .catch(() => '');
    if (!txt) continue;

    let fileScore = 0;
    for (const k of Object.keys(SIGNALS) as SignalKey[]) {
      const hits = txt.match(new RegExp(SIGNALS[k].source, 'gim'))?.length ?? 0;
      totals[k] += hits;
      fileScore += hits;
    }

    if (fileScore > 0 && sampleRefs.length < 8) sampleRefs.push(file.path);
  }

  findings.push({
    severity: 'info',
    category: 'mastra:signals',
    message: `Signals summary workflow=${totals.workflow}, evals=${totals.evals}, observability=${totals.observability}, mcp=${totals.mcp}, human_loop=${totals.humanLoop}`,
    suggestion: `Sample refs: ${sampleRefs.join(', ') || 'none'}`,
  });

  findings.push({
    severity: 'info',
    category: 'mastra:keep-drop',
    message: 'KEEP candidates: workflow graph syntax, eval wrappers, observability baseline, MCP server pattern, human-loop suspend/resume. DROP for now: heavy memory/RAG and enterprise-coupled surfaces.',
    suggestion: 'Implement as bridge contracts in isolated package/agent; validate by gate metrics before scale-out.',
  });

  return findings;
}

const mode = process.argv.includes('--exec') ? 'execute' as const : 'dry_run' as const;
runAgent('mastra_gem_hunter', mode, runHunt).then((result) => {
  printResult(result);
  process.exit(result.success ? 0 : 1);
});
