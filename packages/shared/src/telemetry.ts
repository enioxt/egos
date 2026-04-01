/**
 * 📊 Telemetry Module — @egos/shared
 *
 * Structured telemetry with dual output:
 * 1. Supabase persistence (when configured)
 * 2. Structured JSON console logs (always — parseable from docker logs)
 *
 * Generalized from 852 Inteligência for use across all EGOS leaf repos.
 */

// ── Types ──────────────────────────────────────────────────

export type TelemetryEventType =
  | 'chat_completion'
  | 'chat_error'
  | 'rate_limit_hit'
  | 'report_generation'
  | 'report_error'
  | 'provider_unavailable'
  | 'atrian_violation'
  | 'user_action'
  | 'api_call'
  | 'agent_run'
  | 'agent_session'
  | 'tool_call'
  | 'custom';

export interface TelemetryEvent {
  event_type: TelemetryEventType;
  model_id?: string;
  provider?: string;
  tokens_in?: number;
  tokens_out?: number;
  cost_usd?: number;
  duration_ms?: number;
  client_ip_hash?: string;
  status_code?: number;
  error_message?: string;
  metadata?: Record<string, unknown>;
}

export interface TelemetryConfig {
  /** Prefix for log entries, e.g., '852', 'forja', 'carteira' */
  logPrefix: string;
  /** Supabase table name for persistence */
  tableName?: string;
  /** Supabase client (optional, for persistence) */
  supabaseClient?: {
    from: (table: string) => {
      insert: (data: Record<string, unknown>) => Promise<{ error?: Error }>;
      select: (columns: string) => {
        gte: (column: string, value: string) => {
          order: (column: string, opts: { ascending: boolean }) => {
            limit: (n: number) => Promise<{ data?: Record<string, unknown>[]; error?: Error }>;
          };
        };
      };
    };
  };
}

// ── IP Hashing (privacy-safe) ─────────────────────────────

function hashIp(ip: string): string {
  let hash = 0;
  for (let i = 0; i < ip.length; i++) {
    const char = ip.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash |= 0;
  }
  return Math.abs(hash).toString(36);
}

// ── Telemetry Factory ─────────────────────────────────────

export interface TelemetryRecorder {
  recordEvent: (event: TelemetryEvent) => Promise<void>;
  recordChatCompletion: (opts: {
    modelId: string;
    provider: string;
    tokensIn: number;
    tokensOut: number;
    costUsd: number;
    durationMs?: number;
    clientIp?: string;
  }) => Promise<void>;
  recordRateLimitHit: (clientIp: string, endpoint: string) => Promise<void>;
  recordChatError: (error: string, clientIp?: string) => Promise<void>;
  recordAgentRun: (opts: {
    agentId: string;
    mode: 'dry_run' | 'execute';
    durationMs: number;
    success: boolean;
    findings?: number;
  }) => Promise<void>;
  recordAgentSession: (opts: {
    sessionId: string;
    agentId: string;
    mode: 'dry_run' | 'execute';
    durationMs: number;
    success: boolean;
    tokensIn?: number;
    tokensOut?: number;
    costUsd?: number;
  }) => Promise<void>;
  recordToolCall: (opts: {
    sessionId?: string;
    agentId?: string;
    toolName: string;
    durationMs: number;
    success: boolean;
    costUsd?: number;
    tokensIn?: number;
    tokensOut?: number;
    metadata?: Record<string, unknown>;
  }) => Promise<void>;
}

export function createTelemetryRecorder(config: TelemetryConfig): TelemetryRecorder {
  const { logPrefix, tableName, supabaseClient } = config;

  async function recordEvent(event: TelemetryEvent): Promise<void> {
    const timestamp = new Date().toISOString();
    const ipHash = event.client_ip_hash ? hashIp(event.client_ip_hash) : undefined;

    // 1. Always emit structured JSON log
    const logEntry = {
      t: timestamp,
      ev: event.event_type,
      model: event.model_id,
      provider: event.provider,
      in: event.tokens_in,
      out: event.tokens_out,
      cost: event.cost_usd,
      ms: event.duration_ms,
      ip: ipHash,
      status: event.status_code,
      err: event.error_message,
      meta: event.metadata,
    };
    const clean = Object.fromEntries(Object.entries(logEntry).filter(([, v]) => v !== undefined));
    console.log(`[${logPrefix}-telemetry] ${JSON.stringify(clean)}`);

    // 2. Persist to Supabase if configured
    if (!supabaseClient || !tableName) return;

    try {
      await supabaseClient.from(tableName).insert({
        event_type: event.event_type,
        model_id: event.model_id || null,
        provider: event.provider || null,
        tokens_in: event.tokens_in || null,
        tokens_out: event.tokens_out || null,
        cost_usd: event.cost_usd || null,
        duration_ms: event.duration_ms || null,
        client_ip_hash: ipHash || null,
        status_code: event.status_code || null,
        error_message: event.error_message || null,
        metadata: event.metadata || null,
        created_at: timestamp,
      });
    } catch {
      // Silent fail — telemetry must never break the app
    }
  }

  async function recordChatCompletion(opts: {
    modelId: string;
    provider: string;
    tokensIn: number;
    tokensOut: number;
    costUsd: number;
    durationMs?: number;
    clientIp?: string;
  }) {
    return recordEvent({
      event_type: 'chat_completion',
      model_id: opts.modelId,
      provider: opts.provider,
      tokens_in: opts.tokensIn,
      tokens_out: opts.tokensOut,
      cost_usd: opts.costUsd,
      duration_ms: opts.durationMs,
      client_ip_hash: opts.clientIp,
      status_code: 200,
    });
  }

  async function recordRateLimitHit(clientIp: string, endpoint: string) {
    return recordEvent({
      event_type: 'rate_limit_hit',
      client_ip_hash: clientIp,
      status_code: 429,
      metadata: { endpoint },
    });
  }

  async function recordChatError(error: string, clientIp?: string) {
    return recordEvent({
      event_type: 'chat_error',
      error_message: error,
      client_ip_hash: clientIp,
      status_code: 500,
    });
  }

  async function recordAgentRun(opts: {
    agentId: string;
    mode: 'dry_run' | 'execute';
    durationMs: number;
    success: boolean;
    findings?: number;
  }) {
    return recordEvent({
      event_type: 'agent_run',
      duration_ms: opts.durationMs,
      status_code: opts.success ? 200 : 500,
      metadata: {
        agentId: opts.agentId,
        mode: opts.mode,
        findings: opts.findings,
      },
    });
  }

  async function recordAgentSession(opts: {
    sessionId: string;
    agentId: string;
    mode: 'dry_run' | 'execute';
    durationMs: number;
    success: boolean;
    tokensIn?: number;
    tokensOut?: number;
    costUsd?: number;
  }) {
    return recordEvent({
      event_type: 'agent_session',
      duration_ms: opts.durationMs,
      status_code: opts.success ? 200 : 500,
      tokens_in: opts.tokensIn,
      tokens_out: opts.tokensOut,
      cost_usd: opts.costUsd,
      metadata: {
        sessionId: opts.sessionId,
        agentId: opts.agentId,
        mode: opts.mode,
      },
    });
  }

  async function recordToolCall(opts: {
    sessionId?: string;
    agentId?: string;
    toolName: string;
    durationMs: number;
    success: boolean;
    costUsd?: number;
    tokensIn?: number;
    tokensOut?: number;
    metadata?: Record<string, unknown>;
  }) {
    return recordEvent({
      event_type: 'tool_call',
      duration_ms: opts.durationMs,
      status_code: opts.success ? 200 : 500,
      cost_usd: opts.costUsd,
      tokens_in: opts.tokensIn,
      tokens_out: opts.tokensOut,
      metadata: {
        ...opts.metadata,
        toolName: opts.toolName,
        sessionId: opts.sessionId,
        agentId: opts.agentId,
      },
    });
  }

  return {
    recordEvent,
    recordChatCompletion,
    recordRateLimitHit,
    recordChatError,
    recordAgentRun,
    recordAgentSession,
    recordToolCall,
  };
}

// ── Stats Query ───────────────────────────────────────────

export interface TelemetryStats {
  totalEvents: number;
  totalChats: number;
  totalTokensIn: number;
  totalTokensOut: number;
  totalCostUsd: number;
  rateLimitHits: number;
  errors: number;
  byModel: Record<string, number>;
  byProvider: Record<string, number>;
  byAgent: Record<string, number>;
  byTool: Record<string, number>;
  recentEvents: Array<Record<string, unknown>>;
}

export async function getStats(
  config: TelemetryConfig,
  days: number = 7
): Promise<TelemetryStats | null> {
  const { tableName, supabaseClient } = config;
  if (!supabaseClient || !tableName) return null;

  const since = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();

  try {
    const { data: events, error } = await supabaseClient
      .from(tableName)
      .select('*')
      .gte('created_at', since)
      .order('created_at', { ascending: false })
      .limit(500);

    if (error || !events) return null;

    const stats: TelemetryStats = {
      totalEvents: events.length,
      totalChats: 0,
      totalTokensIn: 0,
      totalTokensOut: 0,
      totalCostUsd: 0,
      rateLimitHits: 0,
      errors: 0,
      byModel: {},
      byProvider: {},
      byAgent: {},
      byTool: {},
      recentEvents: events.slice(0, 20),
    };

    for (const e of events) {
      if (e.event_type === 'chat_completion') {
        stats.totalChats++;
        stats.totalTokensIn += (e.tokens_in as number) || 0;
        stats.totalTokensOut += (e.tokens_out as number) || 0;
        stats.totalCostUsd += (e.cost_usd as number) || 0;
        const modelId = e.model_id as string;
        const provider = e.provider as string;
        if (modelId) stats.byModel[modelId] = (stats.byModel[modelId] || 0) + 1;
        if (provider) stats.byProvider[provider] = (stats.byProvider[provider] || 0) + 1;
      }
      if (e.event_type === 'rate_limit_hit') stats.rateLimitHits++;
      if (e.event_type === 'chat_error' || e.event_type === 'report_error') stats.errors++;

      if (e.event_type === 'agent_run' || e.event_type === 'agent_session') {
        const metadata = (e.metadata || {}) as Record<string, unknown>;
        const agentId = metadata.agentId as string | undefined;
        if (agentId) stats.byAgent[agentId] = (stats.byAgent[agentId] || 0) + 1;
      }

      if (e.event_type === 'tool_call') {
        const metadata = (e.metadata || {}) as Record<string, unknown>;
        const toolName = metadata.toolName as string | undefined;
        if (toolName) stats.byTool[toolName] = (stats.byTool[toolName] || 0) + 1;
      }
    }

    return stats;
  } catch {
    return null;
  }
}
