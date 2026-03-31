/**
 * EGOS Event Bus — Agent coordination via Supabase Realtime
 * Broadcasts events to Realtime channel AND persists to `agent_events` table.
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

  // Broadcast via Supabase Realtime (if available)
  const ch = getChannel();
  if (ch) {
    await ch.send({ type: 'broadcast', event: 'event', payload: event });
  }

  // Persist fire-and-forget (if Supabase available)
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

  // Always notify local subscribers
  subscriptions.forEach((sub, i) => {
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
  if (channel) {
    const client = getClient();
    if (client) client.removeChannel(channel);
    channel = undefined as any;
  }
}
