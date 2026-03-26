/**
 * GTM Harvester Agent — EGOS-098 (partial)
 *
 * Scans public GitHub repos for market/GTM strategy artifacts and returns
 * a distilled map of reusable business execution signals.
 *
 * Usage:
 *   bun agent:run gtm_harvester --dry
 *   bun agent:run gtm_harvester --dry --owner=enioxt
 */

import { runAgent, printResult, log, type Finding, type RunContext } from '../runtime/runner';

interface RepoMeta { name: string; default_branch: string }
interface TreeNode { path: string; type: 'blob' | 'tree' }

const TEXT_EXT = /\.(md|txt|yml|yaml|json|ts|tsx|js|py)$/i;
const PATH_HINT = /(readme|tasks|roadmap|agents|handoff|strategy|market|go[-_ ]to[-_ ]market|gtm|docs)/i;

const SIGNALS = {
  gtm: /\bGTM\b|go[- ]to[- ]market|ICP|pricing|acquisition|funnel/i,
  market: /mercado|market strategy|estrat[ée]gia|posicionamento|proposta de valor/i,
  siberia: /Siberia Institute/i,
  vagner: /Vagner Campos/i,
};

type SignalKey = keyof typeof SIGNALS;

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url, { headers: { 'User-Agent': 'egos-gtm-harvester' } });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} @ ${url}`);
  return await res.json() as T;
}

function shouldScan(path: string): boolean {
  return TEXT_EXT.test(path) && PATH_HINT.test(path);
}

async function runHarvest(ctx: RunContext): Promise<Finding[]> {
  const ownerArg = process.argv.find(a => a.startsWith('--owner='));
  const owner = ownerArg ? ownerArg.split('=')[1] : 'enioxt';

  const repos = await getJson<RepoMeta[]>(`https://api.github.com/users/${owner}/repos?per_page=100&type=owner`);
  log(ctx, 'info', `Scanning ${repos.length} public repos from ${owner}`);

  const findings: Finding[] = [];
  let reposWithSignals = 0;
  let siberiaHits = 0;
  let vagnerHits = 0;
  const repoTotals: Array<{ repo: string; total: number; gtm: number; market: number }> = [];

  for (const repo of repos) {
    const treeResp = await getJson<{ tree: TreeNode[] }>(
      `https://api.github.com/repos/${owner}/${repo.name}/git/trees/${repo.default_branch}?recursive=1`
    ).catch(() => ({ tree: [] as TreeNode[] }));

    const files = treeResp.tree
      .filter(n => n.type === 'blob' && shouldScan(n.path))
      .slice(0, 120);

    const sample: string[] = [];
    const counts: Record<SignalKey, number> = { gtm: 0, market: 0, siberia: 0, vagner: 0 };

    for (const node of files) {
      const rawUrl = `https://raw.githubusercontent.com/${owner}/${repo.name}/${repo.default_branch}/${node.path}`;
      const txt = await fetch(rawUrl, { headers: { 'User-Agent': 'egos-gtm-harvester' } })
        .then(r => (r.ok ? r.text() : ''))
        .catch(() => '');
      if (!txt) continue;

      const lines = txt.split('\n');
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        (Object.keys(SIGNALS) as SignalKey[]).forEach((k) => {
          if (SIGNALS[k].test(line)) {
            counts[k]++;
            if (sample.length < 4) sample.push(`${node.path}:${i + 1}`);
          }
        });
      }
    }

    const total = counts.gtm + counts.market + counts.siberia + counts.vagner;
    if (total > 0) {
      reposWithSignals++;
      siberiaHits += counts.siberia;
      vagnerHits += counts.vagner;
      repoTotals.push({ repo: repo.name, total, gtm: counts.gtm, market: counts.market });
      findings.push({
        severity: 'info',
        category: 'gtm:repo-signals',
        message: `${repo.name}: gtm=${counts.gtm}, market=${counts.market}, siberia=${counts.siberia}, vagner=${counts.vagner}`,
        suggestion: sample.length ? `Sample refs: ${sample.join(', ')}` : 'No sample refs collected',
      });
    }
  }

  findings.unshift({
    severity: 'info',
    category: 'gtm:summary',
    message: `Public repo scan complete: ${reposWithSignals}/${repos.length} repos with GTM/market signals`,
    suggestion: `Specific hits — Siberia Institute: ${siberiaHits}, Vagner Campos: ${vagnerHits}. Prioritize EGOS/egos-lab/FORJA strategy artifacts for automation.`
  });

  if (siberiaHits === 0) {
    findings.push({
      severity: 'warning',
      category: 'gtm:gaps',
      message: 'No direct public references found for "Siberia Institute" in scanned repos',
      suggestion: 'If this should exist, add explicit canonical references in TASKS/strategy docs to make it machine-searchable.'
    });
  }

  if (vagnerHits === 0) {
    findings.push({
      severity: 'warning',
      category: 'gtm:gaps',
      message: 'No direct public references found for "Vagner Campos" in scanned repos',
      suggestion: 'If relevant to strategy, encode as named pattern in roadmap/backlog with explicit owner and expected output.'
    });
  }

  const topRepos = repoTotals
    .sort((a, b) => b.total - a.total)
    .slice(0, 4)
    .map(r => `${r.repo}(gtm=${r.gtm},market=${r.market})`)
    .join(', ');

  findings.push({
    severity: 'info',
    category: 'gtm:next-actions',
    message: `Top strategic repos by signal density: ${topRepos || 'none'}`,
    suggestion: 'Create/refresh GTM tasks first in these repos. If repo mismatch, register in kernel TASKS backlog with target_repo tag then migrate.'
  });

  return findings;
}

const mode = process.argv.includes('--exec') ? 'execute' as const : 'dry_run' as const;
runAgent('gtm_harvester', mode, runHarvest).then((result) => {
  printResult(result);
  process.exit(result.success ? 0 : 1);
});
