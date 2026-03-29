/**
 * REAL tests for telemetry.ts — Structured telemetry with dual output.
 * Tests verify event recording, convenience methods, IP hashing, and stats.
 * Uses mock Supabase client to test persistence path.
 *
 * Run: bun test packages/shared/src/__tests__/telemetry.test.ts
 */
import { describe, it, expect } from 'bun:test';
import { createTelemetryRecorder, getStats, type TelemetryConfig } from '../telemetry';

// Mock Supabase client that stores inserts
function createMockSupabase() {
  const inserts: Record<string, unknown>[] = [];
  return {
    inserts,
    client: {
      from: (table: string) => ({
        insert: async (data: Record<string, unknown>) => {
          inserts.push({ ...data, _table: table });
          return { error: undefined };
        },
        select: (columns: string) => ({
          gte: (column: string, value: string) => ({
            order: (col: string, opts: { ascending: boolean }) => ({
              limit: (n: number) => Promise.resolve({
                data: inserts.filter(i => i._table === table).slice(0, n),
                error: undefined,
              }),
            }),
          }),
        }),
      }),
    },
  };
}

// ═══════════════════════════════════════════════════════════
// Event recording — basic
// ═══════════════════════════════════════════════════════════
describe('Telemetry — Event recording', () => {
  it('records event without Supabase (log-only mode)', async () => {
    const recorder = createTelemetryRecorder({ logPrefix: 'test' });
    // Should not throw
    await recorder.recordEvent({ event_type: 'custom', metadata: { test: true } });
  });

  it('records event to Supabase when configured', async () => {
    const mock = createMockSupabase();
    const recorder = createTelemetryRecorder({
      logPrefix: 'test',
      tableName: 'telemetry',
      supabaseClient: mock.client as any,
    });
    await recorder.recordEvent({
      event_type: 'chat_completion',
      model_id: 'qwen-plus',
      provider: 'alibaba',
      tokens_in: 100,
      tokens_out: 200,
    });
    expect(mock.inserts.length).toBe(1);
    expect(mock.inserts[0].event_type).toBe('chat_completion');
    expect(mock.inserts[0].model_id).toBe('qwen-plus');
  });
});

// ═══════════════════════════════════════════════════════════
// Convenience methods
// ═══════════════════════════════════════════════════════════
describe('Telemetry — Convenience methods', () => {
  it('recordChatCompletion stores all fields', async () => {
    const mock = createMockSupabase();
    const recorder = createTelemetryRecorder({
      logPrefix: 'egos',
      tableName: 'events',
      supabaseClient: mock.client as any,
    });
    await recorder.recordChatCompletion({
      modelId: 'qwen-flash',
      provider: 'alibaba',
      tokensIn: 50,
      tokensOut: 150,
      costUsd: 0,
      durationMs: 500,
      clientIp: '192.168.1.1',
    });
    expect(mock.inserts.length).toBe(1);
    expect(mock.inserts[0].tokens_in).toBe(50);
    expect(mock.inserts[0].tokens_out).toBe(150);
    expect(mock.inserts[0].status_code).toBe(200);
    // IP should be hashed, not raw
    expect(mock.inserts[0].client_ip_hash).not.toBe('192.168.1.1');
    expect(mock.inserts[0].client_ip_hash).toBeTruthy();
  });

  it('recordRateLimitHit stores 429 status', async () => {
    const mock = createMockSupabase();
    const recorder = createTelemetryRecorder({
      logPrefix: 'test',
      tableName: 'events',
      supabaseClient: mock.client as any,
    });
    await recorder.recordRateLimitHit('10.0.0.1', '/api/chat');
    expect(mock.inserts[0].status_code).toBe(429);
    expect(mock.inserts[0].event_type).toBe('rate_limit_hit');
  });

  it('recordChatError stores error message', async () => {
    const mock = createMockSupabase();
    const recorder = createTelemetryRecorder({
      logPrefix: 'test',
      tableName: 'events',
      supabaseClient: mock.client as any,
    });
    await recorder.recordChatError('Model timeout', '10.0.0.2');
    expect(mock.inserts[0].error_message).toBe('Model timeout');
    expect(mock.inserts[0].status_code).toBe(500);
  });

  it('recordAgentRun stores agent metadata', async () => {
    const mock = createMockSupabase();
    const recorder = createTelemetryRecorder({
      logPrefix: 'test',
      tableName: 'events',
      supabaseClient: mock.client as any,
    });
    await recorder.recordAgentRun({
      agentId: 'dep_auditor',
      mode: 'dry_run',
      durationMs: 1500,
      success: true,
      findings: 3,
    });
    expect(mock.inserts[0].event_type).toBe('agent_run');
    expect((mock.inserts[0].metadata as any).agentId).toBe('dep_auditor');
    expect((mock.inserts[0].metadata as any).findings).toBe(3);
  });
});

// ═══════════════════════════════════════════════════════════
// IP hashing — privacy
// ═══════════════════════════════════════════════════════════
describe('Telemetry — IP privacy', () => {
  it('hashes IP addresses deterministically', async () => {
    const mock = createMockSupabase();
    const recorder = createTelemetryRecorder({
      logPrefix: 'test',
      tableName: 'events',
      supabaseClient: mock.client as any,
    });
    await recorder.recordChatCompletion({ modelId: 'm', provider: 'p', tokensIn: 0, tokensOut: 0, costUsd: 0, clientIp: '192.168.1.100' });
    await recorder.recordChatCompletion({ modelId: 'm', provider: 'p', tokensIn: 0, tokensOut: 0, costUsd: 0, clientIp: '192.168.1.100' });
    // Same IP should produce same hash
    expect(mock.inserts[0].client_ip_hash).toBe(mock.inserts[1].client_ip_hash);
  });
});

// ═══════════════════════════════════════════════════════════
// Stats query
// ═══════════════════════════════════════════════════════════
describe('Telemetry — Stats', () => {
  it('returns null when no Supabase configured', async () => {
    const stats = await getStats({ logPrefix: 'test' });
    expect(stats).toBeNull();
  });

  it('returns stats from Supabase', async () => {
    const mock = createMockSupabase();
    const config: TelemetryConfig = {
      logPrefix: 'test',
      tableName: 'events',
      supabaseClient: mock.client as any,
    };
    // Pre-populate
    const recorder = createTelemetryRecorder(config);
    await recorder.recordChatCompletion({ modelId: 'qwen-plus', provider: 'alibaba', tokensIn: 100, tokensOut: 200, costUsd: 0.01 });
    await recorder.recordRateLimitHit('1.2.3.4', '/api');

    const stats = await getStats(config, 7);
    expect(stats).not.toBeNull();
    expect(stats!.totalEvents).toBe(2);
  });
});
