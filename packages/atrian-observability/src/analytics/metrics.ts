/**
 * ATRiAN Core Metrics — OBS-004
 *
 * 10 core metrics for agent runtime observability.
 * These are computed from spans and never contain payload data.
 */

export interface MetricPoint {
  metric: MetricName;
  value: number;
  unit: MetricUnit;
  session_id: string;
  agent_id?: string;
  window_start: string; // ISO 8601
  window_end: string;
  labels?: Record<string, string>;
}

export type MetricUnit =
  | "ms"        // milliseconds
  | "tokens"    // LLM token count
  | "count"     // occurrence count
  | "ratio"     // 0.0–1.0
  | "bytes";    // byte size

/** The 10 canonical EGOS observability metrics. */
export type MetricName =
  | "session.latency_p50"         // Median turn latency (ms)
  | "session.latency_p95"         // p95 turn latency (ms)
  | "session.tokens_total"        // Total tokens consumed in session
  | "session.tool_call_count"     // Number of tool calls per session
  | "session.failure_rate"        // Error spans / total spans (ratio)
  | "session.override_rate"       // User denials / total tool requests (ratio)
  | "agent.spawn_count"           // Sub-agents spawned per session
  | "agent.stuck_loops"           // Repeated identical tool calls detected (count)
  | "hook.trigger_count"          // Hook fires per session
  | "llm.tokens_per_turn";        // Average tokens per turn

export const METRIC_DEFINITIONS: Record<
  MetricName,
  { unit: MetricUnit; description: string; alertThreshold?: number }
> = {
  "session.latency_p50": {
    unit: "ms",
    description: "Median turn latency",
  },
  "session.latency_p95": {
    unit: "ms",
    description: "95th percentile turn latency",
    alertThreshold: 30_000, // 30s = likely stuck
  },
  "session.tokens_total": {
    unit: "tokens",
    description: "Total tokens consumed in session",
    alertThreshold: 150_000, // near context limit
  },
  "session.tool_call_count": {
    unit: "count",
    description: "Tool calls per session",
  },
  "session.failure_rate": {
    unit: "ratio",
    description: "Error spans / total spans",
    alertThreshold: 0.2, // > 20% failures
  },
  "session.override_rate": {
    unit: "ratio",
    description: "User denials / total tool requests",
    alertThreshold: 0.3, // > 30% overrides suggests permission config issue
  },
  "agent.spawn_count": {
    unit: "count",
    description: "Sub-agents spawned per session",
  },
  "agent.stuck_loops": {
    unit: "count",
    description: "Repeated identical tool calls detected",
    alertThreshold: 3, // 3+ identical calls = stuck loop
  },
  "hook.trigger_count": {
    unit: "count",
    description: "Hook fires per session",
  },
  "llm.tokens_per_turn": {
    unit: "tokens",
    description: "Average tokens per turn",
    alertThreshold: 8_000, // unusually large turns
  },
};

/** Check if a metric value exceeds its alert threshold. */
export function isAlertable(metric: MetricName, value: number): boolean {
  const def = METRIC_DEFINITIONS[metric];
  return def.alertThreshold !== undefined && value >= def.alertThreshold;
}
