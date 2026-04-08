/**
 * agents/runtime/heartbeat.ts — EGOS Heartbeat Loop (PAP-001)
 *
 * Provides native 30min wake/sleep cycles for EGOS agents, inspired by
 * Paperclip's heartbeat daemon pattern (PAP-001).
 *
 * Usage:
 *   import { startHeartbeat } from './heartbeat';
 *
 *   await startHeartbeat({
 *     agentId: 'gem-hunter',
 *     intervalMs: 30 * 60 * 1000,  // 30 minutes
 *     handler: async (ctx) => { ... return findings; },
 *     checkWorkQueue: async () => true, // optional: skip cycle if no work
 *   });
 *
 * The heartbeat loop:
 *   1. wake → call checkWorkQueue()
 *   2. if work available → runAgent() → emit event on bus
 *   3. sleep intervalMs
 *   4. repeat until signal or maxRuns reached
 */

import { runAgent, type AgentHandler, type RunResult } from './runner';
import { getGlobalBus } from './event-bus';

export interface HeartbeatConfig {
  /** Agent ID in registry */
  agentId: string;
  /** Wake interval in ms. Default: 30 minutes */
  intervalMs?: number;
  /** Optional: skip run if no work is available */
  checkWorkQueue?: () => Promise<boolean>;
  /** The agent's main handler */
  handler: AgentHandler;
  /** Stop after N runs (for testing / bounded loops) */
  maxRuns?: number;
  /** Run once immediately on start, then wait. Default: true */
  runImmediately?: boolean;
  /** Mode: dry_run | execute */
  mode?: 'dry_run' | 'execute';
  /** Called after every run result */
  onResult?: (result: RunResult, cycleIndex: number) => Promise<void>;
}

export interface HeartbeatHandle {
  stop: () => void;
  status: () => HeartbeatStatus;
}

export interface HeartbeatStatus {
  agentId: string;
  cycleCount: number;
  skippedCount: number;
  lastRunAt: string | null;
  lastResult: RunResult | null;
  running: boolean;
  nextRunAt: string | null;
}

// ── Implementation ────────────────────────────────────────────────────────────

export function startHeartbeat(config: HeartbeatConfig): HeartbeatHandle {
  const {
    agentId,
    intervalMs = 30 * 60 * 1000,
    checkWorkQueue,
    handler,
    maxRuns,
    runImmediately = true,
    mode = 'execute',
    onResult,
  } = config;

  let running = true;
  let cycleCount = 0;
  let skippedCount = 0;
  let lastRunAt: string | null = null;
  let lastResult: RunResult | null = null;
  let nextRunAt: string | null = null;
  let timeoutHandle: ReturnType<typeof setTimeout> | null = null;

  const bus = getGlobalBus();

  function computeNextRunAt(): string {
    return new Date(Date.now() + intervalMs).toISOString();
  }

  async function cycle(): Promise<void> {
    if (!running) return;
    if (maxRuns !== undefined && cycleCount >= maxRuns) {
      running = false;
      console.log(`[heartbeat:${agentId}] maxRuns (${maxRuns}) reached — stopping`);
      return;
    }

    cycleCount++;
    const cycleIndex = cycleCount;
    console.log(`[heartbeat:${agentId}] cycle #${cycleIndex} starting`);

    // Check work queue — skip if nothing to do
    if (checkWorkQueue) {
      let hasWork: boolean;
      try {
        hasWork = await checkWorkQueue();
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : String(err);
        console.warn(`[heartbeat:${agentId}] checkWorkQueue failed: ${msg} — running anyway`);
        hasWork = true;
      }
      if (!hasWork) {
        skippedCount++;
        console.log(`[heartbeat:${agentId}] no work in queue — skipping cycle #${cycleIndex}`);
        scheduleNext();
        return;
      }
    }

    lastRunAt = new Date().toISOString();

    try {
      const result = await runAgent(agentId, mode, handler);
      lastResult = result;

      // Emit heartbeat event on bus
      bus.emit(
        'agent.heartbeat.complete',
        {
          agentId,
          cycleIndex,
          mode,
          success: result.success,
          findingsCount: result.findings.length,
          durationMs: result.durationMs,
        },
        `heartbeat:${agentId}`,
        result.correlationId
      );

      console.log(
        `[heartbeat:${agentId}] cycle #${cycleIndex} done — ${result.findings.length} findings, ${result.durationMs}ms`
      );

      if (onResult) {
        await onResult(result, cycleIndex).catch((err: unknown) => {
          console.error(`[heartbeat:${agentId}] onResult callback failed:`, err);
        });
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      console.error(`[heartbeat:${agentId}] cycle #${cycleIndex} threw: ${msg}`);
    }

    scheduleNext();
  }

  function scheduleNext(): void {
    if (!running) return;
    if (maxRuns !== undefined && cycleCount >= maxRuns) {
      running = false;
      return;
    }
    nextRunAt = computeNextRunAt();
    timeoutHandle = setTimeout(() => {
      cycle().catch((err: unknown) => {
        console.error(`[heartbeat:${agentId}] unhandled cycle error:`, err);
      });
    }, intervalMs);
  }

  // Boot
  if (runImmediately) {
    nextRunAt = new Date().toISOString();
    setImmediate(() => {
      cycle().catch((err: unknown) => {
        console.error(`[heartbeat:${agentId}] initial cycle error:`, err);
      });
    });
  } else {
    nextRunAt = computeNextRunAt();
    scheduleNext();
  }

  return {
    stop(): void {
      running = false;
      if (timeoutHandle !== null) {
        clearTimeout(timeoutHandle);
        timeoutHandle = null;
      }
      console.log(`[heartbeat:${agentId}] stopped after ${cycleCount} cycles`);
    },
    status(): HeartbeatStatus {
      return {
        agentId,
        cycleCount,
        skippedCount,
        lastRunAt,
        lastResult,
        running,
        nextRunAt,
      };
    },
  };
}
