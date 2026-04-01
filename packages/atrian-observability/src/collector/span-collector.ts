/**
 * ATRiAN Span Collector — OBS-001 (core)
 *
 * In-memory span buffer with pluggable export.
 * Designed for zero-dependency use in Claude Code hooks.
 *
 * Export targets (pluggable):
 *   - console (default, for development)
 *   - file (append to JSONL)
 *   - http (POST to OTel collector endpoint)
 *
 * Usage:
 *   const collector = new SpanCollector({ export: 'file', path: '/tmp/atrian.jsonl' });
 *   const span = createSpan('tool.call', sessionId, { tool_name: 'Bash' });
 *   // ... do work ...
 *   collector.emit(finishSpan(span, startMs));
 */

import type { Span } from "../instrumentation/spans.ts";
import { isTelemetryEnabled, sanitizeForTelemetry } from "../policies/telemetry-policy.ts";

export type ExportTarget = "console" | "file" | "http" | "none";

export interface CollectorConfig {
  export?: ExportTarget;
  /** File path for 'file' export (JSONL format). */
  path?: string;
  /** HTTP endpoint for 'http' export. */
  endpoint?: string;
  /** Max spans to buffer before auto-flush (default: 100). */
  bufferSize?: number;
}

export class SpanCollector {
  private buffer: Span[] = [];
  private config: Required<CollectorConfig>;

  constructor(config: CollectorConfig = {}) {
    this.config = {
      export: config.export ?? "console",
      path: config.path ?? "/tmp/atrian-spans.jsonl",
      endpoint: config.endpoint ?? "",
      bufferSize: config.bufferSize ?? 100,
    };
  }

  /** Emit a finished span. Buffers and auto-flushes when full. */
  emit(span: Span): void {
    if (!isTelemetryEnabled()) return;

    // Sanitize before storing
    const safe = sanitizeForTelemetry(span as unknown as Record<string, unknown>);
    this.buffer.push(safe as unknown as Span);

    if (this.buffer.length >= this.config.bufferSize) {
      void this.flush();
    }
  }

  /** Flush buffer to configured export target. */
  async flush(): Promise<void> {
    if (this.buffer.length === 0) return;

    const spans = this.buffer.splice(0);

    switch (this.config.export) {
      case "console":
        for (const s of spans) {
          console.log("[atrian]", JSON.stringify(s));
        }
        break;

      case "file": {
        const { appendFileSync } = await import("fs");
        const lines = spans.map((s) => JSON.stringify(s)).join("\n") + "\n";
        appendFileSync(this.config.path, lines, "utf8");
        break;
      }

      case "http": {
        if (!this.config.endpoint) break;
        await fetch(this.config.endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ spans }),
        }).catch(() => {
          // silently drop — telemetry must never crash the host
        });
        break;
      }

      case "none":
        break;
    }
  }

  /** Return buffered spans without flushing (for testing). */
  peek(): readonly Span[] {
    return this.buffer;
  }

  /** Drain buffer and return all spans (for testing). */
  drain(): Span[] {
    return this.buffer.splice(0);
  }
}
