/**
 * EGOS Event Bus — Agent coordination via Supabase Realtime
 * Persists all events to `agent_events` table.
 * Only broadcasts warn/error/critical via Realtime to prevent quota exhaustion (INC-004).
 * Rate-limited per source to prevent runaway agents from flooding the DB.
 * @module event-bus
 */
export type Severity = 'info' | 'warn' | 'error' | 'critical';

export interface AgentEvent {
  id: string;
  type: string;
  source: string;
  payload: Record<string, unknown>;
  timestamp: string;
  severity: Severity;
}

type EventCallback = (event: AgentEvent) => void;
interface Subscription { pattern: string; callback: EventCallback; once: boolean }

const CHANNEL_NAME = 'egos-events';
const TABLE_NAME = 'agent_events';
let supabase: any;
let channel: any;
const subscriptions: Subscription[] = [];
let _supabaseAvailable: boolean | null = null;

// INC-004: only stream warn/error/critical via Realtime — info events are audit-only.
const SEVERITY_RANK: Record<Severity, number> = { info: 0, warn: 1, error: 2, critical: 3 };
const REALTIME_MIN_SEVERITY = SEVERITY_RANK['warn'];

function shouldBroadcast(severity: Severity): boolean {
  return SEVERITY_RANK[severity] >= REALTIME_MIN_SEVERITY;
}

// ── Rate Limiter (INC-004 hardening) ──────────────────────────────────────
// Prevents any single source from flooding DB writes.
// Max 100 events per source per 60-second window. Excess events are dropped
// with a single warning per window. warn/error/critical bypass the limiter.

const RATE_LIMIT_WINDOW_MS = 60_000;
const RATE_LIMIT_MAX_PER_WINDOW = 100;

interface RateBucket {
  count: number;
  windowStart: number;
  warned: boolean;
}

const rateBuckets = new Map<string, RateBucket>();

function checkRateLimit(source: string, severity: Severity): boolean {
  // warn/error/critical always pass — they're actionable and rare
  if (SEVERITY_RANK[severity] >= REALTIME_MIN_SEVERITY) return true;

  const now = Date.now();
  let bucket = rateBuckets.get(source);

  if (!bucket || now - bucket.windowStart > RATE_LIMIT_WINDOW_MS) {
    bucket = { count: 0, windowStart: now, warned: false };
    rateBuckets.set(source, bucket);
  }

  bucket.count++;

  if (bucket.count > RATE_LIMIT_MAX_PER_WINDOW) {
    if (!bucket.warned) {
      console.warn(
        `[event-bus] RATE LIMIT: source "${source}" exceeded ${RATE_LIMIT_MAX_PER_WINDOW} events/min — dropping DB writes until window resets`
      );
      bucket.warned = true;
    }
    return false;
  }

  return true;
}

// ── Supabase Setup ────────────────────────────────────────────────────────

function loadSupabase(): boolean {
  if (_supabaseAvailable !== null) return _supabaseAvailable;
  try {
    const mod = require('@supabase/supabase-js');
    const url = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
    if (!url || !key) {
      console.warn('[event-bus] SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set — running in local-only mode');
      _supabaseAvailable = false;
      return false;
    }
    supabase = mod.createClient(url, key);
    _supabaseAvailable = true;
    return true;
  } catch {
    console.warn('[event-bus] @supabase/supabase-js not installed — running in local-only mode');
    _supabaseAvailable = false;
    return false;
  }
}

function matchPattern(pattern: string, type: string): boolean {
  if (pattern === '*') return true;
  if (pattern.endsWith('.*')) return type.startsWith(pattern.slice(0, -1));
  return pattern === type;
}

function getClient(): any | null {
  if (!loadSupabase()) return null;
  return supabase;
}

function getChannel(): any | null {
  if (!loadSupabase()) return null;
  if (!channel) {
    channel = supabase.channel(CHANNEL_NAME);
    channel.on('broadcast', { event: 'event' }, ({ payload }: { payload: AgentEvent }) => {
      const toRemove: number[] = [];
      subscriptions.forEach((sub, i) => {
        if (matchPattern(sub.pattern, payload.type)) {
          sub.callback(payload);
          if (sub.once) toRemove.push(i);
        }
      });
      for (let i = toRemove.length - 1; i >= 0; i--) subscriptions.splice(toRemove[i], 1);
    });
    channel.subscribe();
  }
  return channel;
}

// ── Core API ──────────────────────────────────────────────────────────────

export async function emit(
  type: string,
  source: string,
  payload: Record<string, unknown> = {},
  severity: Severity = 'info',
): Promise<AgentEvent> {
  const event: AgentEvent = {
    id: crypto.randomUUID(),
    type,
    source,
    payload,
    timestamp: new Date().toISOString(),
    severity,
  };

  // Broadcast via Supabase Realtime only for warn/error/critical (INC-004)
  if (shouldBroadcast(severity)) {
    const ch = getChannel();
    if (ch) {
      await ch.send({ type: 'broadcast', event: 'event', payload: event });
    }
  }

  // Persist to DB — rate-limited per source to prevent runaway writes (INC-004)
  if (checkRateLimit(source, severity)) {
    const client = getClient();
    if (client) {
      client
        .from(TABLE_NAME)
        .insert({
          id: event.id,
          type: event.type,
          source: event.source,
          payload: event.payload,
          severity: event.severity,
          created_at: event.timestamp,
        })
        .then(({ error }: { error: { message: string } | null }) => {
          if (error) console.error('[event-bus] insert failed:', error.message);
        });
    }
  }

  // Always notify local subscribers (even if DB write was rate-limited)
  subscriptions.forEach((sub) => {
    if (matchPattern(sub.pattern, event.type)) {
      sub.callback(event);
    }
  });

  return event;
}

export function subscribe(pattern: string, callback: EventCallback): () => void {
  getChannel(); // init Realtime listener if available
  const sub: Subscription = { pattern, callback, once: false };
  subscriptions.push(sub);
  return () => {
    const idx = subscriptions.indexOf(sub);
    if (idx !== -1) subscriptions.splice(idx, 1);
  };
}

export function subscribeOnce(type: string, callback: EventCallback): () => void {
  getChannel(); // init Realtime listener if available
  const sub: Subscription = { pattern: type, callback, once: true };
  subscriptions.push(sub);
  return () => {
    const idx = subscriptions.indexOf(sub);
    if (idx !== -1) subscriptions.splice(idx, 1);
  };
}

export async function getRecentEvents(limit = 50, type?: string): Promise<AgentEvent[]> {
  const client = getClient();
  if (!client) return []; // No Supabase — return empty

  let query = client
    .from(TABLE_NAME)
    .select('id, type, source, payload, severity, created_at')
    .order('created_at', { ascending: false })
    .limit(limit);
  if (type) query = query.eq('type', type);

  const { data, error } = await query;
  if (error) throw new Error(`[event-bus] fetch failed: ${error.message}`);

  return (data ?? []).map((row: any) => ({
    id: row.id,
    type: row.type,
    source: row.source,
    payload: row.payload,
    timestamp: row.created_at,
    severity: row.severity,
  }));
}

export function cleanup(): void {
  subscriptions.length = 0;
  rateBuckets.clear();
  if (channel) {
    const client = getClient();
    if (client) client.removeChannel(channel);
    channel = undefined as any;
  }
}
