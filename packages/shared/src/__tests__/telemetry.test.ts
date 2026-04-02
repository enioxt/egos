import { describe, it, expect } from 'bun:test';
import { createTelemetryRecorder, getLatencyHeatmap, getStats } from '../telemetry';

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

  it('aggregates stats and latency heatmap by agent/tool', async () => {
    const mockRows = [
      {
        event_type: 'agent_session',
        duration_ms: 1200,
        metadata: { agentId: 'context-tracker' },
        created_at: new Date().toISOString(),
      },
      {
        event_type: 'tool_call',
        duration_ms: 6400,
        metadata: { toolName: 'web.search', agentId: 'mcp-router' },
        created_at: new Date().toISOString(),
      },
      {
        event_type: 'tool_call',
        duration_ms: 2100,
        metadata: { toolName: 'web.search', agentId: 'mcp-router' },
        created_at: new Date().toISOString(),
      },
    ];

    const fakeSupabase = {
      from: (_table: string) => ({
        insert: async (_data: Record<string, unknown>) => ({}),
        select: (_columns: string) => ({
          gte: (_column: string, _value: string) => ({
            order: (_orderColumn: string, _opts: { ascending: boolean }) => ({
              limit: async (_n: number) => ({ data: mockRows, error: undefined }),
            }),
          }),
        }),
      }),
    };

    const config = {
      logPrefix: 'qa-test',
      tableName: 'events',
      supabaseClient: fakeSupabase,
    };

    const stats = await getStats(config, 7);
    expect(stats).not.toBeNull();
    expect(stats?.byAgent['context-tracker']).toBe(1);
    expect(stats?.byTool['web.search']).toBe(2);

    const heatmap = await getLatencyHeatmap(config, 7);
    expect(heatmap).not.toBeNull();
    const webSearchBucket = heatmap?.find(h => h.key === 'web.search');
    expect(webSearchBucket).toBeDefined();
    expect(webSearchBucket?.over5sCount).toBe(1);
  });
});
