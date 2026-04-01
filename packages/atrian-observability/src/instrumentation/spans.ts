/**
 * ATRiAN Span Definitions — OBS-003
 *
 * 12 trace spans covering the full session lifecycle.
 * OTel-compatible format (compatible with Jaeger, Zipkin, OTLP).
 *
 * Principle: no payload in spans — only metadata.
 */

export type SpanStatus = "ok" | "error" | "timeout" | "cancelled";

export interface Span {
  name: SpanName;
  session_id: string;
  agent_id?: string;
  model_id?: string;
  turn_index?: number;
  tool_name?: string;
  tokens_input?: number;
  tokens_output?: number;
  latency_ms?: number;
  status: SpanStatus;
  error_type?: string;
  error_code?: string;
  timestamp: string; // ISO 8601
  duration_ms: number;
  attributes?: Record<string, string | number | boolean>;
}

/** The 12 canonical EGOS session spans. */
export type SpanName =
  | "session.start"      // Session initialized
  | "session.close"      // Session ended (normal or timeout)
  | "turn.start"         // User message received
  | "turn.end"           // Response delivered
  | "tool.call"          // Tool invoked (name only, no args)
  | "tool.result"        // Tool returned (status only, no result)
  | "llm.request"        // Model API request sent
  | "llm.response"       // Model API response received
  | "agent.spawn"        // Sub-agent launched
  | "agent.complete"     // Sub-agent finished
  | "hook.trigger"       // Claude Code hook fired
  | "hook.result";       // Hook completed

export const SPAN_NAMES: SpanName[] = [
  "session.start",
  "session.close",
  "turn.start",
  "turn.end",
  "tool.call",
  "tool.result",
  "llm.request",
  "llm.response",
  "agent.spawn",
  "agent.complete",
  "hook.trigger",
  "hook.result",
];

/** Create a new span with required fields. */
export function createSpan(
  name: SpanName,
  session_id: string,
  overrides: Partial<Omit<Span, "name" | "session_id" | "timestamp">> = {}
): Span {
  return {
    name,
    session_id,
    status: "ok",
    timestamp: new Date().toISOString(),
    duration_ms: 0,
    ...overrides,
  };
}

/** Finish a span by computing duration_ms from start time. */
export function finishSpan(
  span: Span,
  startMs: number,
  status: SpanStatus = "ok",
  overrides: Partial<Span> = {}
): Span {
  return {
    ...span,
    duration_ms: Date.now() - startMs,
    status,
    ...overrides,
  };
}
