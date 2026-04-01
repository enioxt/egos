/**
 * ATRiAN Telemetry Policy — OBS-002
 *
 * Principle: Collect metadata, not payload.
 * Telemetry mínima de conteúdo, máxima de comportamento.
 *
 * What CAN be logged:
 *   - Tool names (not tool arguments/results)
 *   - Token counts (input/output/total)
 *   - Latency (ms per turn, per session)
 *   - Error type + code (not error message body)
 *   - Span names (not span data)
 *   - Session ID (opaque, no user PII)
 *   - Agent ID, model ID
 *   - Turn sequence number
 *
 * What MUST NOT be logged:
 *   - User message content
 *   - Tool arguments or tool results
 *   - File contents or code snippets
 *   - Secrets, tokens, env vars
 *   - IP addresses or geographic data
 *   - Any PII (CPF, RG, name, email)
 *
 * Retention:
 *   - Raw spans: 7 days
 *   - Aggregated metrics: 90 days
 *   - Opt-out: set ATRIAN_TELEMETRY=off in env
 */

export const TELEMETRY_POLICY = {
  version: "1.0.0",
  retention: {
    rawSpansDays: 7,
    aggregatedMetricsDays: 90,
  },
  allowedFields: [
    "session_id",
    "agent_id",
    "model_id",
    "span_name",
    "tool_name",
    "turn_index",
    "tokens_input",
    "tokens_output",
    "tokens_total",
    "latency_ms",
    "error_type",
    "error_code",
    "timestamp",
    "duration_ms",
  ] as const,
  blockedPatterns: [
    /cpf/i,
    /rg\b/i,
    /email/i,
    /password/i,
    /secret/i,
    /token/i,
    /key\b/i,
    /auth/i,
  ],
} as const;

export type AllowedField = (typeof TELEMETRY_POLICY.allowedFields)[number];

/** Returns true if telemetry is enabled (default: on unless ATRIAN_TELEMETRY=off). */
export function isTelemetryEnabled(): boolean {
  return (
    typeof process !== "undefined" &&
    process.env["ATRIAN_TELEMETRY"] !== "off"
  );
}

/** Strips any blocked fields from an object before logging. */
export function sanitizeForTelemetry(
  obj: Record<string, unknown>
): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(obj)) {
    const blocked = TELEMETRY_POLICY.blockedPatterns.some((p) => p.test(k));
    if (!blocked) {
      result[k] = v;
    }
  }
  return result;
}
