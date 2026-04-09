#!/usr/bin/env bun
/**
 * PLAT-MON-001 — Platform Monitor
 *
 * Checks for new versions/changelogs of platforms we depend on daily:
 *   - Claude Code (@anthropic-ai/claude-code on npm)
 *   - Notion MCP / Notion API (notion.so/releases or npm @notionhq/client)
 *   - Anthropic SDK (@anthropic-ai/sdk on npm)
 *   - Bun runtime (bun.sh/blog or GitHub releases)
 *
 * Stores in Supabase `platform_updates` table and sends Telegram alert.
 * Cron: VPS 9h BRT daily.
 *
 * Usage:
 *   bun scripts/platform-monitor.ts --dry      # preview without writing
 *   bun scripts/platform-monitor.ts --exec     # check + store + alert
 *   bun scripts/platform-monitor.ts --report   # print stored updates
 */

export {};

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';

// ── Config ──────────────────────────────────────────────────────────────────
const SUPABASE_URL = process.env.SUPABASE_URL ?? '';
const SUPABASE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? '';
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN ?? process.env.TELEGRAM_BOT_TOKEN_AI_AGENTS ?? '';
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_ADMIN_CHAT_ID ?? process.env.TELEGRAM_AUTHORIZED_USER_ID ?? '171767219';

// ── Types ────────────────────────────────────────────────────────────────────
type EgosImpact = 'low' | 'medium' | 'high' | 'critical';

type PlatformUpdate = {
  platform: string;
  current_version: string;
  previous_version: string | null;
  summary: string;
  changelog_url: string;
  egos_impact: EgosImpact;
  egos_notes: string;
};

// ── NPM Version Checker ──────────────────────────────────────────────────────
async function getNpmLatest(pkg: string): Promise<{ version: string; description: string }> {
  const res = await fetch(`https://registry.npmjs.org/${encodeURIComponent(pkg)}/latest`, {
    headers: { 'Accept': 'application/json' },
    signal: AbortSignal.timeout(8000),
  });
  if (!res.ok) throw new Error(`npm registry ${pkg} → HTTP ${res.status}`);
  const data = await res.json() as { version: string; description: string };
  return { version: data.version, description: data.description ?? '' };
}

// ── GitHub Release Checker ───────────────────────────────────────────────────
async function getGithubLatest(owner: string, repo: string): Promise<{ version: string; body: string }> {
  const res = await fetch(`https://api.github.com/repos/${owner}/${repo}/releases/latest`, {
    headers: { 'Accept': 'application/vnd.github.v3+json' },
    signal: AbortSignal.timeout(8000),
  });
  if (!res.ok) throw new Error(`GitHub ${owner}/${repo} → HTTP ${res.status}`);
  const data = await res.json() as { tag_name: string; body: string };
  const version = data.tag_name.replace(/^v/, '');
  return { version, body: (data.body ?? '').substring(0, 500) };
}

// ── Supabase Helpers ─────────────────────────────────────────────────────────
async function getStoredVersion(platform: string): Promise<string | null> {
  const res = await fetch(
    `${SUPABASE_URL}/rest/v1/platform_updates?platform=eq.${encodeURIComponent(platform)}&order=created_at.desc&limit=1&select=current_version`,
    {
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': 'Bearer ' + SUPABASE_KEY,
      },
    }
  );
  if (!res.ok) return null;
  const rows = await res.json() as Array<{ current_version: string }>;
  return rows[0]?.current_version ?? null;
}

async function storeUpdate(update: PlatformUpdate): Promise<void> {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/platform_updates`, {
    method: 'POST',
    headers: {
      'apikey': SUPABASE_KEY,
      'Authorization': 'Bearer ' + SUPABASE_KEY,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      platform: update.platform,
      current_version: update.current_version,
      previous_version: update.previous_version,
      summary: update.summary,
      changelog_url: update.changelog_url,
      egos_impact: update.egos_impact,
      egos_notes: update.egos_notes,
      alerted: false,
    }),
  });
  if (!res.ok) throw new Error('Supabase store failed: ' + await res.text());
}

async function markAlerted(platform: string, version: string): Promise<void> {
  await fetch(
    `${SUPABASE_URL}/rest/v1/platform_updates?platform=eq.${encodeURIComponent(platform)}&current_version=eq.${encodeURIComponent(version)}`,
    {
      method: 'PATCH',
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': 'Bearer ' + SUPABASE_KEY,
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal',
      },
      body: JSON.stringify({ alerted: true }),
    }
  );
}

// ── Telegram ─────────────────────────────────────────────────────────────────
// ── PLAT-MON-003: Auto-task in TASKS.md ──────────────────────────────────────
function appendTasksEntry(updates: PlatformUpdate[]): void {
  const tasksPath = join(import.meta.dir, '..', 'TASKS.md');
  if (!existsSync(tasksPath)) return;

  const existing = readFileSync(tasksPath, 'utf-8');
  const lines: string[] = [];

  for (const u of updates) {
    const id = 'PLAT-' + u.platform.toUpperCase().replace(/[^A-Z0-9]/g, '') + '-' + u.current_version.replace(/\./g, '');
    // Skip if already present
    if (existing.includes(id)) continue;
    const emoji = u.egos_impact === 'critical' ? '🚨' : '⚠️';
    lines.push(`- [ ] **${id} [P1]**: ${emoji} ${u.platform} atualizado ${u.previous_version ?? '?'} → ${u.current_version} — ${u.egos_notes} [auto-gerado por platform-monitor ${new Date().toISOString().slice(0, 10)}]`);
  }

  if (lines.length === 0) return;

  // Insert after the first "## Platform Monitor" heading, or append to end
  const marker = '## Platform Monitor\n';
  const insertAfter = existing.includes(marker)
    ? existing.indexOf(marker) + marker.length
    : existing.length;

  const newContent = existing.slice(0, insertAfter) + lines.join('\n') + '\n' + existing.slice(insertAfter);
  writeFileSync(tasksPath, newContent, 'utf-8');
  console.log('[platform-monitor] Auto-appended ' + lines.length + ' task(s) to TASKS.md');
}

async function sendTelegram(msg: string): Promise<void> {
  if (!TELEGRAM_BOT_TOKEN) {
    console.log('[telegram] No token — would send:', msg.substring(0, 100));
    return;
  }
  await fetch('https://api.telegram.org/bot' + TELEGRAM_BOT_TOKEN + '/sendMessage', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: TELEGRAM_CHAT_ID,
      text: msg,
      parse_mode: 'Markdown',
      disable_web_page_preview: true,
    }),
  }).catch(() => {});
}

// ── Impact Assessment ─────────────────────────────────────────────────────────
function assessImpact(platform: string, prevVersion: string | null, newVersion: string): { impact: EgosImpact; notes: string } {
  if (!prevVersion) return { impact: 'low', notes: 'First time tracking this platform version' };

  const [prevMajor, prevMinor] = prevVersion.split('.').map(Number);
  const [newMajor, newMinor] = newVersion.split('.').map(Number);

  if (newMajor > prevMajor) {
    return {
      impact: 'critical',
      notes: `Major version bump (${prevVersion} → ${newVersion}). Check breaking changes immediately. Update EGOS integrations.`,
    };
  }

  if (newMinor > prevMinor) {
    return {
      impact: 'high',
      notes: `Minor version bump (${prevVersion} → ${newVersion}). New features available — evaluate for EGOS integration.`,
    };
  }

  if (platform.includes('claude-code')) {
    return {
      impact: 'medium',
      notes: `Claude Code patch (${prevVersion} → ${newVersion}). Check if new tools, hooks, or MCP capabilities added.`,
    };
  }

  return { impact: 'low', notes: `Patch release (${prevVersion} → ${newVersion}). Monitor for bug fixes relevant to EGOS.` };
}

// ── Platform Definitions ──────────────────────────────────────────────────────
type PlatformDef = {
  name: string;
  check: () => Promise<{ version: string; summary: string; changelog_url: string }>;
};

const PLATFORMS: PlatformDef[] = [
  {
    name: 'claude-code',
    check: async () => {
      const { version, description } = await getNpmLatest('@anthropic-ai/claude-code');
      return {
        version,
        summary: description || 'Claude Code CLI by Anthropic',
        changelog_url: 'https://www.npmjs.com/package/@anthropic-ai/claude-code',
      };
    },
  },
  {
    name: 'anthropic-sdk',
    check: async () => {
      const { version } = await getNpmLatest('@anthropic-ai/sdk');
      return {
        version,
        summary: 'Anthropic TypeScript SDK',
        changelog_url: 'https://github.com/anthropics/anthropic-sdk-typescript/releases',
      };
    },
  },
  {
    name: 'notion-client',
    check: async () => {
      const { version } = await getNpmLatest('@notionhq/client');
      return {
        version,
        summary: 'Notion JavaScript SDK',
        changelog_url: 'https://github.com/makenotion/notion-sdk-js/releases',
      };
    },
  },
  {
    name: 'mcp-sdk',
    check: async () => {
      const { version } = await getNpmLatest('@modelcontextprotocol/sdk');
      return {
        version,
        summary: 'Model Context Protocol SDK',
        changelog_url: 'https://github.com/modelcontextprotocol/typescript-sdk/releases',
      };
    },
  },
  {
    name: 'bun',
    check: async () => {
      const { version, body } = await getGithubLatest('oven-sh', 'bun');
      return {
        version,
        summary: 'Bun JavaScript runtime: ' + body.split('\n')[0],
        changelog_url: 'https://bun.sh/blog',
      };
    },
  },
];

// ── Main ──────────────────────────────────────────────────────────────────────
async function runMonitor(dry: boolean): Promise<void> {
  console.log('[platform-monitor] Checking platforms...\n');

  const updates: PlatformUpdate[] = [];
  const errors: string[] = [];

  for (const platform of PLATFORMS) {
    try {
      const { version, summary, changelog_url } = await platform.check();
      const prevVersion = await getStoredVersion(platform.name);

      if (prevVersion === version) {
        console.log('  [=] ' + platform.name + ' v' + version + ' (no change)');
        continue;
      }

      const { impact, notes } = assessImpact(platform.name, prevVersion, version);
      const update: PlatformUpdate = {
        platform: platform.name,
        current_version: version,
        previous_version: prevVersion,
        summary,
        changelog_url,
        egos_impact: impact,
        egos_notes: notes,
      };

      console.log('  [' + impact.toUpperCase() + '] ' + platform.name + ': ' + (prevVersion ?? 'new') + ' → ' + version);
      updates.push(update);
    } catch (e) {
      const msg = platform.name + ': ' + (e as Error).message;
      console.error('  [ERR] ' + msg);
      errors.push(msg);
    }
  }

  if (updates.length === 0) {
    console.log('\n[platform-monitor] No updates detected');
    return;
  }

  console.log('\n[platform-monitor] ' + updates.length + ' update(s) detected');

  if (dry) {
    for (const u of updates) {
      console.log('\n  --- ' + u.platform + ' ---');
      console.log('  Impact: ' + u.egos_impact);
      console.log('  Notes:  ' + u.egos_notes);
    }
    return;
  }

  // Store and alert
  const highImpact = updates.filter((u) => u.egos_impact === 'high' || u.egos_impact === 'critical');

  for (const update of updates) {
    await storeUpdate(update);
  }

  // Alert only high/critical
  if (highImpact.length > 0) {
    const lines = ['🔔 *Platform Updates — EGOS Stack*', ''];
    for (const u of highImpact) {
      const emoji = u.egos_impact === 'critical' ? '🚨' : '⚠️';
      lines.push(emoji + ' *' + u.platform + '* `' + (u.previous_version ?? '?') + '` → `' + u.current_version + '`');
      lines.push('_' + u.egos_notes + '_');
      lines.push('[Changelog](' + u.changelog_url + ')');
      lines.push('');
    }
    await sendTelegram(lines.join('\n'));
    if (!dry) appendTasksEntry(highImpact); // PLAT-MON-003
    for (const u of highImpact) {
      await markAlerted(u.platform, u.current_version);
    }
  }

  // Low/medium: just log
  const lowMedium = updates.filter((u) => u.egos_impact === 'low' || u.egos_impact === 'medium');
  if (lowMedium.length > 0) {
    console.log('[platform-monitor] Low/medium updates stored (no Telegram alert):');
    for (const u of lowMedium) {
      console.log('  ' + u.platform + ' ' + u.current_version);
    }
  }

  console.log('[platform-monitor] Done');
}

async function printReport(): Promise<void> {
  const res = await fetch(
    SUPABASE_URL + '/rest/v1/platform_updates?order=created_at.desc&limit=50&select=platform,current_version,previous_version,egos_impact,egos_notes,created_at,alerted',
    {
      headers: {
        'apikey': SUPABASE_KEY,
        'Authorization': 'Bearer ' + SUPABASE_KEY,
      },
    }
  );
  if (!res.ok) throw new Error('Supabase fetch failed: ' + res.status);
  const rows = await res.json() as Array<{
    platform: string;
    current_version: string;
    previous_version: string | null;
    egos_impact: string;
    egos_notes: string;
    created_at: string;
    alerted: boolean;
  }>;

  console.log('\n=== Platform Monitor Report ===\n');
  for (const r of rows) {
    const date = r.created_at.substring(0, 10);
    const alert = r.alerted ? '📢' : '  ';
    console.log(alert + ' [' + r.egos_impact.toUpperCase() + '] ' + r.platform + ' v' + r.current_version + ' (' + date + ')');
    if (r.previous_version) console.log('      Was: ' + r.previous_version);
    console.log('      ' + r.egos_notes);
  }
}

// ── Entry ────────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);

if (!SUPABASE_URL || !SUPABASE_KEY) {
  console.error('[platform-monitor] Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY');
  process.exit(1);
}

if (args.includes('--report')) {
  await printReport();
} else {
  await runMonitor(args.includes('--dry'));
}
