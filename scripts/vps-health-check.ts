#!/usr/bin/env bun
/**
 * VPS-005 — VPS Health Check
 *
 * Runs 2x/day (09:00 + 21:00 BRT) on the VPS.
 * Checks:
 *   1. Docker containers status (running vs expected)
 *   2. Disk usage (warn >80%, critical >90%)
 *   3. RAM usage (warn >80%, critical >90%)
 *   4. Key service HTTP health endpoints
 *   5. Certbot certificate expiry (warn <30 days)
 *
 * Reports via Telegram. Silent on green (no noise).
 * Alert on yellow/red only.
 *
 * Usage:
 *   bun scripts/vps-health-check.ts [--exec] [--report]
 *   --exec    Run checks and send Telegram (default in cron)
 *   --report  Print full status without Telegram
 *
 * Env: TELEGRAM_BOT_TOKEN, TELEGRAM_ADMIN_CHAT_ID
 */

export {};

import { execSync } from 'child_process';

const TELEGRAM_TOKEN = process.env.TELEGRAM_BOT_TOKEN ?? process.env.TELEGRAM_BOT_TOKEN_AI_AGENTS ?? '';
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_ADMIN_CHAT_ID ?? '171767219';

const ARGS = process.argv.slice(2);
const isReport = ARGS.includes('--report');

// ── Config ────────────────────────────────────────────────────────────────────

// Expected running containers (subset that should always be up)
const EXPECTED_CONTAINERS = [
  'guard-brasil',
  'egos-gateway',
  'egos-hq',
];

// Service health endpoints (relative to VPS localhost)
// Use localhost ports when running on VPS (avoids Caddy reverse-proxy loop)
// External domains may timeout from inside the VPS
const HEALTH_ENDPOINTS: Array<{ name: string; url: string }> = [
  { name: 'Guard Brasil', url: 'http://localhost:3099/health' },
  { name: 'EGOS Gateway', url: 'http://localhost:3050/health' },
  { name: 'EGOS HQ', url: 'http://localhost:3060/api/health' },
];

// ── Types ─────────────────────────────────────────────────────────────────────
type CheckResult = {
  name: string;
  status: 'ok' | 'warn' | 'critical';
  message: string;
};

// ── Checks ────────────────────────────────────────────────────────────────────
function checkDisk(): CheckResult {
  try {
    const output = execSync("df -h / | awk 'NR==2 {print $5, $3, $2}'", { encoding: 'utf-8' }).trim();
    const [usedPct, used, total] = output.split(' ');
    const pct = parseInt(usedPct, 10);
    const status = pct >= 90 ? 'critical' : pct >= 80 ? 'warn' : 'ok';
    return { name: 'Disk /', status, message: `${usedPct} (${used}/${total})` };
  } catch (e) {
    return { name: 'Disk /', status: 'warn', message: 'check failed: ' + (e as Error).message };
  }
}

function checkRam(): CheckResult {
  try {
    const output = execSync("free -m | awk 'NR==2 {printf \"%.0f %s %s\", $3*100/$2, $3, $2}'", { encoding: 'utf-8' }).trim();
    const [pctStr, used, total] = output.split(' ');
    const pct = parseInt(pctStr, 10);
    const status = pct >= 90 ? 'critical' : pct >= 80 ? 'warn' : 'ok';
    return { name: 'RAM', status, message: `${pct}% (${used}MB/${total}MB)` };
  } catch (e) {
    return { name: 'RAM', status: 'warn', message: 'check failed: ' + (e as Error).message };
  }
}

function checkContainers(): CheckResult[] {
  try {
    const output = execSync('docker ps --format "{{.Names}}" 2>/dev/null', { encoding: 'utf-8' });
    const running = new Set(output.split('\n').map((n) => n.trim()).filter(Boolean));
    const results: CheckResult[] = [];

    for (const expected of EXPECTED_CONTAINERS) {
      // Match partial name
      const found = [...running].some((name) => name.includes(expected));
      results.push({
        name: `Container: ${expected}`,
        status: found ? 'ok' : 'critical',
        message: found ? 'running' : 'NOT RUNNING',
      });
    }

    // Total container count
    results.push({
      name: 'Docker total',
      status: 'ok',
      message: `${running.size} containers running`,
    });

    return results;
  } catch {
    return [{ name: 'Docker', status: 'warn', message: 'docker ps failed (not root?)' }];
  }
}

async function checkEndpoint(name: string, url: string): Promise<CheckResult> {
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(5000) });
    return {
      name: `HTTP: ${name}`,
      status: res.ok ? 'ok' : 'warn',
      message: res.ok ? `${res.status} OK` : `HTTP ${res.status}`,
    };
  } catch (e) {
    return { name: `HTTP: ${name}`, status: 'critical', message: 'unreachable: ' + (e as Error).message.substring(0, 50) };
  }
}

function checkCertbot(): CheckResult {
  try {
    const output = execSync('certbot certificates 2>/dev/null | grep "Expiry Date" | head -3', { encoding: 'utf-8' });
    const matches = output.matchAll(/Expiry Date: (\d{4}-\d{2}-\d{2})/g);
    const results: string[] = [];
    let status: 'ok' | 'warn' | 'critical' = 'ok';

    for (const match of matches) {
      const expiry = new Date(match[1]);
      const daysLeft = Math.floor((expiry.getTime() - Date.now()) / (1000 * 60 * 60 * 24));
      if (daysLeft < 7) status = 'critical';
      else if (daysLeft < 30 && status !== 'critical') status = 'warn';
      results.push(`${daysLeft}d`);
    }

    return {
      name: 'TLS Certs',
      status: results.length > 0 ? status : 'ok',
      message: results.length > 0 ? `Expires in: ${results.join(', ')}` : 'no certs found',
    };
  } catch {
    return { name: 'TLS Certs', status: 'ok', message: 'certbot not available' };
  }
}

// ── Telegram ─────────────────────────────────────────────────────────────────
async function sendTelegram(msg: string): Promise<void> {
  if (!TELEGRAM_TOKEN) return;
  await fetch('https://api.telegram.org/bot' + TELEGRAM_TOKEN + '/sendMessage', {
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

// ── Main ──────────────────────────────────────────────────────────────────────
async function run(): Promise<void> {
  const allChecks: CheckResult[] = [];

  // System checks
  allChecks.push(checkDisk());
  allChecks.push(checkRam());
  allChecks.push(...checkContainers());
  allChecks.push(checkCertbot());

  // HTTP endpoint checks (parallel)
  const endpointResults = await Promise.all(
    HEALTH_ENDPOINTS.map((e) => checkEndpoint(e.name, e.url))
  );
  allChecks.push(...endpointResults);

  // Print report
  const emoji = (s: CheckResult['status']) => s === 'ok' ? '✅' : s === 'warn' ? '⚠️' : '🔴';
  console.log('\n[vps-health-check] ' + new Date().toISOString());
  for (const check of allChecks) {
    console.log(`  ${emoji(check.status)} ${check.name}: ${check.message}`);
  }

  // Only alert if there are non-ok results
  const problems = allChecks.filter((c) => c.status !== 'ok');
  if (problems.length === 0) {
    console.log('\n✅ All systems healthy — no alert sent');
    return;
  }

  const criticals = problems.filter((c) => c.status === 'critical');
  const warnings = problems.filter((c) => c.status === 'warn');
  const headerEmoji = criticals.length > 0 ? '🔴' : '⚠️';

  const lines = [
    `${headerEmoji} *VPS Health — EGOS* (${new Date().toISOString().slice(0, 16)})`,
    '',
  ];

  for (const p of problems) {
    lines.push(`${emoji(p.status)} \`${p.name}\`: ${p.message}`);
  }

  lines.push('');
  lines.push(`_${criticals.length} critical, ${warnings.length} warnings_`);
  lines.push('#vps #health #egos');

  if (!isReport) {
    await sendTelegram(lines.join('\n'));
    console.log(`\n  📨 Alert sent (${problems.length} issues)`);
  }
}

await run();
