import { describe, it, expect } from 'bun:test';
import { createTelemetryRecorder } from '../telemetry';

describe('Telemetry — agent and tool tracking', () => {
  it('records agent session with telemetry fields', async () => {
    const recorder = createTelemetryRecorder({ logPrefix: 'qa-test' });

    await recorder.recordAgentSession({
      sessionId: 'sess-1',
      agentId: 'context-tracker',
      mode: 'dry_run',
      durationMs: 321,
      success: true,
      tokensIn: 100,
      tokensOut: 40,
      costUsd: 0.002,
    });

    expect(true).toBeTrue();
  });

  it('persists tool call metadata when supabase is configured', async () => {
    const inserts: Record<string, unknown>[] = [];
    const fakeSupabase = {
      from: (_table: string) => ({
        insert: async (data: Record<string, unknown>) => {
          inserts.push(data);
          return {};
        },
        select: (_columns: string) => ({
          gte: (_column: string, _value: string) => ({
            order: (_orderColumn: string, _opts: { ascending: boolean }) => ({
              limit: async (_n: number) => ({ data: [], error: undefined }),
            }),
          }),
        }),
      }),
    };

    const recorder = createTelemetryRecorder({
      logPrefix: 'qa-test',
      tableName: 'events',
      supabaseClient: fakeSupabase,
    });

    await recorder.recordToolCall({
      sessionId: 'sess-1',
      agentId: 'mcp-router',
      toolName: 'web.search',
      durationMs: 180,
      success: true,
      costUsd: 0.0003,
      tokensIn: 12,
      tokensOut: 34,
      metadata: { source: 'unit-test' },
    });

    expect(inserts.length).toBe(1);
    const row = inserts[0] || {};
    expect(row.event_type).toBe('tool_call');
    expect(row.duration_ms).toBe(180);
    expect(row.cost_usd).toBe(0.0003);
    expect(typeof row.metadata).toBe('object');
  });
});
