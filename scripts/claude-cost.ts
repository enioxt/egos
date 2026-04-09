#!/usr/bin/env bun
/**
 * COST-001 — Claude Code Usage & Cost Tracker
 *
 * Reads ~/.claude/projects/**\/*.jsonl and computes:
 *   - Token usage per project/session/model
 *   - Estimated cost (Haiku / Sonnet / Opus pricing)
 *   - Top 5 most expensive sessions
 *   - Weekly trend
 *
 * Usage:
 *   bun scripts/claude-cost.ts               # summary for all projects
 *   bun scripts/claude-cost.ts --project egos # filter to one project
 *   bun scripts/claude-cost.ts --days 7       # last N days
 *   bun scripts/claude-cost.ts --json         # output JSON for Supabase
 */

export {};

import { readFileSync, readdirSync, statSync } from 'fs';
import { join, dirname, basename } from 'path';
import { homedir } from 'os';

// ── Pricing (per 1M tokens, USD as of 2026-04) ───────────────────────────────
const PRICING: Record<string, { input: number; output: number; cache_write: number; cache_read: number }> = {
  'claude-haiku-4':    { input: 0.80,  output: 4.00,  cache_write: 1.00,  cache_read: 0.08  },
  'claude-haiku':      { input: 0.80,  output: 4.00,  cache_write: 1.00,  cache_read: 0.08  },
  'claude-sonnet-4':   { input: 3.00,  output: 15.00, cache_write: 3.75,  cache_read: 0.30  },
  'claude-sonnet':     { input: 3.00,  output: 15.00, cache_write: 3.75,  cache_read: 0.30  },
  'claude-opus-4':     { input: 15.00, output: 75.00, cache_write: 18.75, cache_read: 1.50  },
  'claude-opus':       { input: 15.00, output: 75.00, cache_write: 18.75, cache_read: 1.50  },
  'default':           { input: 3.00,  output: 15.00, cache_write: 3.75,  cache_read: 0.30  },
};

function getPrice(model: string) {
  const key = Object.keys(PRICING).find((k) => k !== 'default' && model.includes(k));
  return PRICING[key ?? 'default'];
}

function calcCost(usage: Usage, model: string): number {
  const p = getPrice(model);
  const M = 1_000_000;
  return (
    (usage.input_tokens / M) * p.input +
    (usage.output_tokens / M) * p.output +
    ((usage.cache_creation_input_tokens ?? 0) / M) * p.cache_write +
    ((usage.cache_read_input_tokens ?? 0) / M) * p.cache_read
  );
}

// ── Types ────────────────────────────────────────────────────────────────────
type Usage = {
  input_tokens: number;
  output_tokens: number;
  cache_creation_input_tokens?: number;
  cache_read_input_tokens?: number;
};

type SessionEntry = {
  project: string;
  sessionId: string;
  model: string;
  timestamp: string;
  input: number;
  output: number;
  cache_write: number;
  cache_read: number;
  cost_usd: number;
};

// ── JSONL Reader ─────────────────────────────────────────────────────────────
function readJsonlFile(filePath: string, projectName: string): SessionEntry[] {
  const entries: SessionEntry[] = [];
  const lines = readFileSync(filePath, 'utf-8').split('\n');

  for (const line of lines) {
    if (!line.trim()) continue;
    try {
      const d = JSON.parse(line) as {
        message?: { usage?: Usage; model?: string };
        sessionId?: string;
        timestamp?: string;
        model?: string;
      };
      if (!d.message?.usage) continue;

      const usage = d.message.usage;
      const model = d.message.model ?? d.model ?? 'claude-sonnet';
      const sessionId = d.sessionId ?? 'unknown';
      const timestamp = d.timestamp ?? new Date().toISOString();

      entries.push({
        project: projectName,
        sessionId,
        model,
        timestamp,
        input: usage.input_tokens,
        output: usage.output_tokens,
        cache_write: usage.cache_creation_input_tokens ?? 0,
        cache_read: usage.cache_read_input_tokens ?? 0,
        cost_usd: calcCost(usage, model),
      });
    } catch {
      // skip malformed lines
    }
  }
  return entries;
}

function scanProjects(projectsDir: string, projectFilter: string | null, since: Date): SessionEntry[] {
  const allEntries: SessionEntry[] = [];

  try {
    const projects = readdirSync(projectsDir);
    for (const proj of projects) {
      if (projectFilter && !proj.includes(projectFilter)) continue;

      const projPath = join(projectsDir, proj);
      if (!statSync(projPath).isDirectory()) continue;

      const files = readdirSync(projPath).filter((f) => f.endsWith('.jsonl'));
      for (const file of files) {
        const filePath = join(projPath, file);
        const stat = statSync(filePath);
        if (stat.mtime < since) continue;

        const entries = readJsonlFile(filePath, proj);
        allEntries.push(...entries);
      }
    }
  } catch (e) {
    console.error('[claude-cost] Error scanning:', (e as Error).message);
  }

  return allEntries.filter((e) => new Date(e.timestamp) >= since);
}

// ── Aggregation ──────────────────────────────────────────────────────────────
type ProjectSummary = {
  project: string;
  sessions: number;
  input_tokens: number;
  output_tokens: number;
  cache_tokens: number;
  cost_usd: number;
  top_model: string;
};

function aggregate(entries: SessionEntry[]): { byProject: ProjectSummary[]; bySessions: SessionEntry[] } {
  // By project
  const projMap = new Map<string, ProjectSummary>();
  for (const e of entries) {
    const key = e.project;
    if (!projMap.has(key)) {
      projMap.set(key, { project: key, sessions: 0, input_tokens: 0, output_tokens: 0, cache_tokens: 0, cost_usd: 0, top_model: e.model });
    }
    const p = projMap.get(key)!;
    p.input_tokens += e.input;
    p.output_tokens += e.output;
    p.cache_tokens += e.cache_write + e.cache_read;
    p.cost_usd += e.cost_usd;
  }

  // Count unique sessions
  const uniqueSessions = new Map<string, string>();
  for (const e of entries) {
    uniqueSessions.set(e.sessionId, e.project);
  }
  for (const [sessionId, project] of uniqueSessions) {
    const p = projMap.get(project);
    if (p) p.sessions++;
  }

  // Top 5 sessions by cost
  const sessionMap = new Map<string, SessionEntry & { total_cost: number }>();
  for (const e of entries) {
    const key = e.sessionId;
    if (!sessionMap.has(key)) {
      sessionMap.set(key, { ...e, total_cost: 0 });
    }
    const s = sessionMap.get(key)!;
    s.total_cost += e.cost_usd;
  }

  const topSessions = [...sessionMap.values()]
    .sort((a, b) => b.total_cost - a.total_cost)
    .slice(0, 5);

  return {
    byProject: [...projMap.values()].sort((a, b) => b.cost_usd - a.cost_usd),
    bySessions: topSessions,
  };
}

// ── Formatting ───────────────────────────────────────────────────────────────
function fmtUSD(n: number): string {
  return '$' + n.toFixed(4);
}

function fmtTokens(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
  if (n >= 1_000) return (n / 1_000).toFixed(0) + 'k';
  return String(n);
}

function printReport(entries: SessionEntry[], days: number): void {
  const { byProject, bySessions } = aggregate(entries);
  const totalCost = byProject.reduce((sum, p) => sum + p.cost_usd, 0);
  const totalInput = byProject.reduce((sum, p) => sum + p.input_tokens, 0);
  const totalOutput = byProject.reduce((sum, p) => sum + p.output_tokens, 0);
  const totalSessions = new Set(entries.map((e) => e.sessionId)).size;

  console.log('\n╔══════════════════════════════════════════════╗');
  console.log(`║     Claude Code Usage — Last ${days} days         ║`);
  console.log('╚══════════════════════════════════════════════╝\n');

  console.log(`Total cost:     ${fmtUSD(totalCost)}`);
  console.log(`Total sessions: ${totalSessions}`);
  console.log(`Input tokens:   ${fmtTokens(totalInput)}`);
  console.log(`Output tokens:  ${fmtTokens(totalOutput)}`);

  console.log('\n── By Project ──────────────────────────────────');
  for (const p of byProject) {
    const name = p.project.replace('-home-enio-', '').substring(0, 25);
    console.log(`  ${name.padEnd(26)} ${fmtUSD(p.cost_usd).padStart(8)}  ${fmtTokens(p.input_tokens + p.output_tokens).padStart(7)} tokens  ${p.sessions} sessions`);
  }

  if (bySessions.length > 0) {
    console.log('\n── Top 5 Sessions by Cost ──────────────────────');
    for (const s of bySessions) {
      const date = s.timestamp.substring(0, 10);
      const model = s.model.replace('claude-', '').substring(0, 12);
      const proj = s.project.replace('-home-enio-', '').substring(0, 12);
      console.log(`  ${date}  ${proj.padEnd(13)} ${model.padEnd(13)} ${fmtUSD((s as SessionEntry & {total_cost: number}).total_cost).padStart(8)}`);
    }
  }

  console.log('');
}

// ── Entry ────────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
const projectFilter = args.find((_, i) => args[i - 1] === '--project') ?? null;
const daysArg = parseInt(args.find((_, i) => args[i - 1] === '--days') ?? '30', 10);
const outputJson = args.includes('--json');

const projectsDir = join(homedir(), '.claude', 'projects');
const since = new Date(Date.now() - daysArg * 24 * 60 * 60 * 1000);

const entries = scanProjects(projectsDir, projectFilter, since);

if (outputJson) {
  const { byProject } = aggregate(entries);
  console.log(JSON.stringify({ period_days: daysArg, by_project: byProject }, null, 2));
} else {
  printReport(entries, daysArg);
}
