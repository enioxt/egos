#!/usr/bin/env bun
/**
 * pr:audit — audit PR status across public repos for one GitHub owner.
 *
 * Usage:
 *   bun scripts/pr-ecosystem-audit.ts --owner enioxt --days 15
 */

interface Repo {
  name: string;
}

interface Pull {
  number: number;
  title: string;
  state: 'open' | 'closed';
  draft?: boolean;
  html_url: string;
  updated_at: string;
  merged_at: string | null;
}

const api = 'https://api.github.com';

function arg(flag: string, fallback?: string): string {
  const idx = process.argv.indexOf(flag);
  if (idx === -1) return fallback ?? '';
  return process.argv[idx + 1] ?? fallback ?? '';
}

async function gh<T>(path: string): Promise<T> {
  const res = await fetch(`${api}${path}`, {
    headers: {
      'User-Agent': 'egos-pr-audit',
      Accept: 'application/vnd.github+json',
    },
  });
  if (!res.ok) throw new Error(`GitHub API ${res.status} for ${path}`);
  return res.json() as Promise<T>;
}

function daysAgoIso(days: number): number {
  return Date.now() - days * 24 * 60 * 60 * 1000;
}

function isRecent(iso: string, days: number): boolean {
  return new Date(iso).getTime() >= daysAgoIso(days);
}

async function main(): Promise<void> {
  const owner = arg('--owner', 'enioxt');
  const days = Number(arg('--days', '15'));

  if (!Number.isFinite(days) || days <= 0) {
    throw new Error('--days must be a positive number');
  }

  const repos = await gh<Repo[]>(`/users/${owner}/repos?per_page=100&type=owner&sort=updated`);

  const activeOpen: string[] = [];
  const inactiveOpen: string[] = [];
  const recentMerged: string[] = [];
  const recentClosed: string[] = [];

  for (const repo of repos) {
    const open = await gh<Pull[]>(`/repos/${owner}/${repo.name}/pulls?state=open&per_page=100`);
    const closed = await gh<Pull[]>(`/repos/${owner}/${repo.name}/pulls?state=closed&per_page=100&sort=updated&direction=desc`);

    for (const pr of open) {
      const line = `${repo.name} #${pr.number} | ${pr.draft ? 'draft' : 'open'} | ${pr.updated_at} | ${pr.title} | ${pr.html_url}`;
      if (isRecent(pr.updated_at, days)) activeOpen.push(line);
      else inactiveOpen.push(line);
    }

    for (const pr of closed) {
      if (!isRecent(pr.updated_at, days)) continue;
      const line = `${repo.name} #${pr.number} | ${pr.merged_at ? 'merged' : 'closed'} | ${pr.updated_at} | ${pr.title} | ${pr.html_url}`;
      if (pr.merged_at) recentMerged.push(line);
      else recentClosed.push(line);
    }
  }

  const print = (title: string, rows: string[]) => {
    console.log(`\n## ${title} (${rows.length})`);
    if (rows.length === 0) {
      console.log('- none');
      return;
    }
    rows.sort((a, b) => b.localeCompare(a));
    for (const row of rows) console.log(`- ${row}`);
  };

  console.log(`# PR Ecosystem Audit\nowner=${owner} window=${days}d`);
  print('Active open PRs', activeOpen);
  print('Inactive open PRs', inactiveOpen);
  print('Recently merged PRs', recentMerged);
  print('Recently closed (unmerged) PRs', recentClosed);
}

main().catch((err) => {
  console.error(`❌ ${err instanceof Error ? err.message : String(err)}`);
  process.exit(1);
});
