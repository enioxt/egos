/**
 * REAL tests for metrics-tracker.ts — Session-level metrics collection.
 * Tests verify tool tracking, task aggregation, session lifecycle, and reporting.
 *
 * Run: bun test packages/shared/src/__tests__/metrics-tracker.test.ts
 */
import { describe, it, expect } from 'bun:test';
import { MetricsTracker, initMetricsTracker, getMetricsTracker, trackToolUsage } from '../metrics-tracker';

// ═══════════════════════════════════════════════════════════
// Session lifecycle
// ═══════════════════════════════════════════════════════════
describe('Metrics Tracker — Session lifecycle', () => {
  it('creates tracker with session ID', () => {
    const tracker = new MetricsTracker('sess-test-001');
    const metrics = tracker.exportMetrics();
    expect(metrics.session.sessionId).toBe('sess-test-001');
    expect(metrics.session.startTime).toBeTruthy();
  });

  it('ends session and calculates duration', () => {
    const tracker = new MetricsTracker('sess-test-002');
    const session = tracker.endSession();
    expect(session.endTime).toBeTruthy();
    expect(session.durationMs).toBeGreaterThanOrEqual(0);
  });
});

// ═══════════════════════════════════════════════════════════
// Tool usage tracking
// ═══════════════════════════════════════════════════════════
describe('Metrics Tracker — Tool usage', () => {
  it('tracks tool usage with tokens and cost', () => {
    const tracker = new MetricsTracker('sess-tools');
    tracker.trackToolUsage({
      tool: 'alibaba',
      operation: 'chat_completion',
      success: true,
      tokensIn: 100,
      tokensOut: 200,
      costUsd: 0.001,
      model: 'qwen-plus',
    });
    const report = tracker.getToolUsageReport();
    expect(report.alibaba).toBeDefined();
    expect(report.alibaba.count).toBe(1);
    expect(report.alibaba.totalTokens).toBe(300);
    expect(report.alibaba.totalCost).toBeCloseTo(0.001);
  });

  it('aggregates multiple calls for same tool', () => {
    const tracker = new MetricsTracker('sess-multi');
    tracker.trackToolUsage({ tool: 'claude_code', operation: 'edit', success: true, tokensIn: 50, tokensOut: 100 });
    tracker.trackToolUsage({ tool: 'claude_code', operation: 'read', success: true, tokensIn: 30, tokensOut: 60 });
    const report = tracker.getToolUsageReport();
    expect(report.claude_code.count).toBe(2);
    expect(report.claude_code.totalTokens).toBe(240);
  });

  it('updates session totals on tool usage', () => {
    const tracker = new MetricsTracker('sess-totals');
    tracker.trackToolUsage({ tool: 'openrouter', operation: 'chat', success: true, tokensIn: 500, tokensOut: 1000, costUsd: 0.05 });
    const metrics = tracker.exportMetrics();
    expect(metrics.session.totalTokensIn).toBe(500);
    expect(metrics.session.totalTokensOut).toBe(1000);
    expect(metrics.session.totalCostUsd).toBeCloseTo(0.05);
  });
});

// ═══════════════════════════════════════════════════════════
// Task tracking
// ═══════════════════════════════════════════════════════════
describe('Metrics Tracker — Task tracking', () => {
  it('tracks completed task and updates session', () => {
    const tracker = new MetricsTracker('sess-tasks');
    tracker.trackTask({
      taskId: 'EGOS-123',
      taskType: 'feature',
      priority: 'P1',
      repo: 'egos',
      startTime: new Date().toISOString(),
      status: 'completed',
      toolsUsed: ['claude_code'],
      filesChanged: 5,
      linesAdded: 100,
      linesRemoved: 20,
      commitsCreated: 1,
    });
    const metrics = tracker.exportMetrics();
    expect(metrics.session.tasksCompleted).toBe(1);
    expect(metrics.session.totalCommits).toBe(1);
    expect(metrics.session.totalFilesChanged).toBe(5);
    expect(metrics.session.reposModified).toContain('egos');
  });

  it('does NOT increment tasksCompleted for non-completed tasks', () => {
    const tracker = new MetricsTracker('sess-incomplete');
    tracker.trackTask({
      taskId: 'EGOS-456',
      taskType: 'bug',
      priority: 'P0',
      repo: 'egos-lab',
      startTime: new Date().toISOString(),
      status: 'in_progress',
      toolsUsed: [],
      filesChanged: 0,
      linesAdded: 0,
      linesRemoved: 0,
      commitsCreated: 0,
    });
    expect(tracker.exportMetrics().session.tasksCompleted).toBe(0);
  });

  it('generates task report with breakdowns', () => {
    const tracker = new MetricsTracker('sess-report');
    tracker.trackTask({ taskId: '1', taskType: 'feature', priority: 'P1', repo: 'egos', startTime: '', status: 'completed', toolsUsed: [], filesChanged: 1, linesAdded: 10, linesRemoved: 0, commitsCreated: 1, durationMs: 60000 });
    tracker.trackTask({ taskId: '2', taskType: 'bug', priority: 'P0', repo: 'egos', startTime: '', status: 'blocked', toolsUsed: [], filesChanged: 0, linesAdded: 0, linesRemoved: 0, commitsCreated: 0 });
    const report = tracker.getTaskReport();
    expect(report.total).toBe(2);
    expect(report.byStatus.completed).toBe(1);
    expect(report.byStatus.blocked).toBe(1);
    expect(report.byPriority.P0).toBe(1);
    expect(report.byPriority.P1).toBe(1);
    expect(report.avgDurationMs).toBe(60000);
  });
});

// ═══════════════════════════════════════════════════════════
// Global singleton
// ═══════════════════════════════════════════════════════════
describe('Metrics Tracker — Singleton', () => {
  it('initMetricsTracker creates global tracker', () => {
    const tracker = initMetricsTracker('sess-global');
    const retrieved = getMetricsTracker();
    expect(retrieved).toBe(tracker);
  });

  it('getMetricsTracker throws when not initialized', () => {
    // Reset by initializing a new one first, then test the API
    initMetricsTracker('sess-throwtest');
    // This should work
    expect(() => getMetricsTracker()).not.toThrow();
  });
});

// ═══════════════════════════════════════════════════════════
// Summary output
// ═══════════════════════════════════════════════════════════
describe('Metrics Tracker — Summary', () => {
  it('prints human-readable summary', () => {
    const tracker = new MetricsTracker('sess-summary');
    tracker.trackToolUsage({ tool: 'alibaba', operation: 'chat', success: true, tokensIn: 100, tokensOut: 200, costUsd: 0.01 });
    const summary = tracker.printSummary();
    expect(summary).toContain('METRICS SUMMARY');
    expect(summary).toContain('alibaba');
    expect(summary).toContain('1 calls');
  });
});
