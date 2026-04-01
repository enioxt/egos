/**
 * @egos/atrian-observability
 *
 * OTel-compatible telemetry for EGOS agents.
 * Principle: collect metadata, not payload.
 *
 * Quick start:
 *   import { SpanCollector, createSpan, finishSpan } from '@egos/atrian-observability';
 *   const collector = new SpanCollector({ export: 'file' });
 *   const span = createSpan('tool.call', sessionId, { tool_name: 'Bash' });
 *   const startMs = Date.now();
 *   // ... do work ...
 *   collector.emit(finishSpan(span, startMs));
 */

// Instrumentation
export { createSpan, finishSpan, SPAN_NAMES } from "./instrumentation/spans.ts";
export type { Span, SpanName, SpanStatus } from "./instrumentation/spans.ts";

// Collector
export { SpanCollector } from "./collector/span-collector.ts";
export type { CollectorConfig, ExportTarget } from "./collector/span-collector.ts";

// Analytics
export { METRIC_DEFINITIONS, isAlertable } from "./analytics/metrics.ts";
export type { MetricName, MetricUnit, MetricPoint } from "./analytics/metrics.ts";

// Policies
export {
  TELEMETRY_POLICY,
  isTelemetryEnabled,
  sanitizeForTelemetry,
} from "./policies/telemetry-policy.ts";
export type { AllowedField } from "./policies/telemetry-policy.ts";
