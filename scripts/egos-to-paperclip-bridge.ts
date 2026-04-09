/**
 * DASH-003 — EGOS agent_events → Paperclip issue bridge
 *
 * Polls the EGOS agent_events table (Supabase) and creates Paperclip issues
 * for events matching configurable severity/type filters.
 *
 * Usage:
 *   bun scripts/egos-to-paperclip-bridge.ts --dry       # preview mapping
 *   bun scripts/egos-to-paperclip-bridge.ts --exec      # create issues
 *   bun scripts/egos-to-paperclip-bridge.ts --watch     # continuous mode
 *
 * Env vars (required in exec/watch mode):
 *   PAPERCLIP_API_URL     e.g. http://204.168.217.125:3100
 *   PAPERCLIP_API_KEY     agent API key from Paperclip
 *   PAPERCLIP_COMPANY_ID  company UUID from Paperclip
 *   SUPABASE_URL          Supabase project URL
 *   SUPABASE_SERVICE_KEY  Supabase service role key
 */

// No external deps — uses Supabase REST API via fetch directly
export {};

// ── Config ─────────────────────────────────────────────────────────────────

const PAPERCLIP_API_URL = process.env.PAPERCLIP_API_URL ?? 'http://127.0.0.1:3100';
const PAPERCLIP_API_KEY = process.env.PAPERCLIP_API_KEY ?? '';
const PAPERCLIP_COMPANY_ID = process.env.PAPERCLIP_COMPANY_ID ?? '';
const SUPABASE_URL = process.env.SUPABASE_URL ?? '';
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY ?? '';

/** Minimum severity to bridge. 'warn' bridges warn+error+critical. */
const BRIDGE_SEVERITY_THRESHOLD: 'info' | 'warn' | 'error' | 'critical' =
  (process.env.BRIDGE_SEVERITY_THRESHOLD as any) ?? 'warn';

/** Look back this many minutes for new events */
const LOOKBACK_MINUTES = parseInt(process.env.BRIDGE_LOOKBACK_MINUTES ?? '60', 10);

/** Watch interval in ms */
const WATCH_INTERVAL_MS = parseInt(process.env.BRIDGE_WATCH_INTERVAL_MS ?? '60000', 10);

// ── Severity ordering ──────────────────────────────────────────────────────

const SEVERITY_RANK: Record<string, number> = { info: 0, warn: 1, error: 2, critical: 3 };

function meetsThreshold(severity: string): boolean {
  return (SEVERITY_RANK[severity] ?? 0) >= (SEVERITY_RANK[BRIDGE_SEVERITY_THRESHOLD] ?? 1);
}

// ── AgentEvent → Paperclip issue mapping ──────────────────────────────────

type AgentEvent = {
  id: string;
  type: string;
  source: string;
  payload: Record<string, unknown>;
  severity: string;
  created_at: string;
};

type PaperclipIssuePriority = 'urgent' | 'high' | 'medium' | 'low' | 'no_priority';

function severityToPriority(severity: string): PaperclipIssuePriority {
  switch (severity) {
    case 'critical': return 'urgent';
    case 'error':    return 'high';
    case 'warn':     return 'medium';
    default:         return 'low';
  }
}

function eventToIssue(event: AgentEvent) {
  const payloadLines = Object.entries(event.payload)
    .map(([k, v]) => `- **${k}**: ${JSON.stringify(v)}`)
    .join('\n');

  const title = `[${event.severity.toUpperCase()}] ${event.type} — ${event.source}`;
  const description = [
    `## EGOS Agent Event`,
    ``,
    `| Field | Value |`,
    `|-------|-------|`,
    `| **Event ID** | \`${event.id}\` |`,
    `| **Type** | \`${event.type}\` |`,
    `| **Source** | \`${event.source}\` |`,
    `| **Severity** | \`${event.severity}\` |`,
    `| **Timestamp** | ${event.created_at} |`,
    ``,
    `### Payload`,
    payloadLines || '_empty_',
  ].join('\n');

  return {
    title,
    description,
    status: 'backlog' as const,
    priority: severityToPriority(event.severity),
  };
}

// ── Paperclip API client ───────────────────────────────────────────────────

async function createPaperclipIssue(issue: ReturnType<typeof eventToIssue>) {
  const url = `${PAPERCLIP_API_URL}/api/companies/${PAPERCLIP_COMPANY_ID}/issues`;
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${PAPERCLIP_API_KEY}`,
    },
    body: JSON.stringify(issue),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Paperclip API ${res.status}: ${body}`);
  }

  return res.json() as Promise<{ id: string; title: string }>;
}

// ── Supabase REST helpers ──────────────────────────────────────────────────

async function supabaseGet(path: string): Promise<unknown[]> {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    headers: {
      'apikey': SUPABASE_SERVICE_KEY,
      'Authorization': `Bearer ${SUPABASE_SERVICE_KEY}`,
    },
  });
  if (!res.ok) throw new Error(`Supabase GET ${path} → ${res.status}`);
  return res.json() as Promise<unknown[]>;
}

async function supabaseUpsert(table: string, row: Record<string, unknown>): Promise<void> {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${table}`, {
    method: 'POST',
    headers: {
      'apikey': SUPABASE_SERVICE_KEY,
      'Authorization': `Bearer ${SUPABASE_SERVICE_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': 'resolution=merge-duplicates',
    },
    body: JSON.stringify(row),
  });
  if (!res.ok) throw new Error(`Supabase upsert ${table} → ${res.status}`);
}

// ── Deduplication: track bridged event IDs in Supabase ────────────────────

async function getBridgedIds(eventIds: string[]): Promise<Set<string>> {
  const inClause = eventIds.map(id => `"${id}"`).join(',');
  const rows = await supabaseGet(
    `paperclip_bridged_events?select=event_id&event_id=in.(${inClause})`,
  ) as Array<{ event_id: string }>;
  return new Set(rows.map(r => r.event_id));
}

async function markBridged(eventId: string, paperclipIssueId: string): Promise<void> {
  await supabaseUpsert('paperclip_bridged_events', {
    event_id: eventId,
    paperclip_issue_id: paperclipIssueId,
    bridged_at: new Date().toISOString(),
  });
}

// ── Main bridge logic ──────────────────────────────────────────────────────

async function runBridge(dry: boolean) {
  const since = new Date(Date.now() - LOOKBACK_MINUTES * 60 * 1000).toISOString();

  const events = await supabaseGet(
    `agent_events?select=id,type,source,payload,severity,created_at&created_at=gte.${since}&order=created_at.asc`,
  ) as AgentEvent[];

  const eligible = events.filter(e => meetsThreshold(e.severity));

  if (eligible.length === 0) {
    console.log(`[bridge] No events above threshold '${BRIDGE_SEVERITY_THRESHOLD}' in last ${LOOKBACK_MINUTES}m`);
    return;
  }

  if (dry) {
    console.log(`[bridge] DRY — ${eligible.length} event(s) would be bridged:\n`);
    for (const event of eligible) {
      const issue = eventToIssue(event as AgentEvent);
      console.log(`  [${event.severity}] ${issue.title}`);
      console.log(`    priority: ${issue.priority}`);
      console.log(`    event_id: ${event.id}`);
      console.log();
    }
    return;
  }

  // Check which events are already bridged
  const alreadyBridged = await getBridgedIds(eligible.map(e => e.id));
  const toCreate = eligible.filter(e => !alreadyBridged.has(e.id));

  if (toCreate.length === 0) {
    console.log(`[bridge] All ${eligible.length} eligible event(s) already bridged`);
    return;
  }

  console.log(`[bridge] Creating ${toCreate.length} Paperclip issue(s)...`);

  let created = 0;
  let failed = 0;
  for (const event of toCreate) {
    try {
      const issue = eventToIssue(event as AgentEvent);
      const result = await createPaperclipIssue(issue);
      await markBridged(event.id, result.id);
      console.log(`  ✅ ${result.id}: ${result.title}`);
      created++;
    } catch (err) {
      console.error(`  ❌ event ${event.id}:`, (err as Error).message);
      failed++;
    }
  }

  console.log(`[bridge] Done — ${created} created, ${failed} failed`);
}

// ── Entry point ────────────────────────────────────────────────────────────

const args = process.argv.slice(2);
const isDry = args.includes('--dry');
const isWatch = args.includes('--watch');
const isExec = args.includes('--exec') || isWatch;

if (!isDry && (!SUPABASE_URL || !SUPABASE_SERVICE_KEY)) {
  console.error('[bridge] Missing SUPABASE_URL or SUPABASE_SERVICE_KEY');
  process.exit(1);
}
if (!isDry && (!PAPERCLIP_API_KEY || !PAPERCLIP_COMPANY_ID)) {
  console.error('[bridge] Missing PAPERCLIP_API_KEY or PAPERCLIP_COMPANY_ID');
  process.exit(1);
}

if (isWatch) {
  console.log(`[bridge] Watch mode — polling every ${WATCH_INTERVAL_MS / 1000}s`);
  await runBridge(false);
  setInterval(() => runBridge(false), WATCH_INTERVAL_MS);
} else {
  await runBridge(isDry);
}
