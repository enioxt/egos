/**
 * Metrics Tracker Module
 * 
 * Tracks usage of all AI tools, APIs, and orchestration patterns across EGOS ecosystem.
 * Provides unified metrics collection for Codex, Alibaba, Claude Code, OpenRouter, etc.
 * 
 * @module metrics-tracker
 */

export interface ToolUsageMetric {
  tool: 'hermes' | 'alibaba' | 'claude_code' | 'openrouter' | 'dashscope' | 'gemini' | 'cascade' | 'other';
  operation: string;
  timestamp: string;
  durationMs?: number;
  tokensIn?: number;
  tokensOut?: number;
  costUsd?: number;
  model?: string;
  success: boolean;
  errorMessage?: string;
  metadata?: Record<string, unknown>;
}

export interface TaskMetric {
  taskId: string;
  taskType: 'feature' | 'bug' | 'docs' | 'refactor' | 'test' | 'deploy' | 'research';
  priority: 'P0' | 'P1' | 'P2';
  repo: string;
  startTime: string;
  endTime?: string;
  durationMs?: number;
  toolsUsed: string[];
  filesChanged: number;
  linesAdded: number;
  linesRemoved: number;
  commitsCreated: number;
  status: 'pending' | 'in_progress' | 'completed' | 'blocked' | 'failed';
  blockers?: string[];
}

export interface SessionMetric {
  sessionId: string;
  startTime: string;
  endTime?: string;
  durationMs?: number;
  tasksCompleted: number;
  toolUsage: Record<string, number>;
  totalTokensIn: number;
  totalTokensOut: number;
  totalCostUsd: number;
  reposModified: string[];
  totalCommits: number;
  totalFilesChanged: number;
}

export class MetricsTracker {
  private toolMetrics: ToolUsageMetric[] = [];
  private taskMetrics: TaskMetric[] = [];
  private sessionMetrics: SessionMetric | null = null;

  constructor(private sessionId: string) {
    this.sessionMetrics = {
      sessionId,
      startTime: new Date().toISOString(),
      tasksCompleted: 0,
      toolUsage: {},
      totalTokensIn: 0,
      totalTokensOut: 0,
      totalCostUsd: 0,
      reposModified: [],
      totalCommits: 0,
      totalFilesChanged: 0,
    };
  }

  trackToolUsage(metric: Omit<ToolUsageMetric, 'timestamp'>): void {
    const fullMetric: ToolUsageMetric = {
      ...metric,
      timestamp: new Date().toISOString(),
    };

    this.toolMetrics.push(fullMetric);

    if (this.sessionMetrics) {
      this.sessionMetrics.toolUsage[metric.tool] = (this.sessionMetrics.toolUsage[metric.tool] || 0) + 1;
      
      if (metric.tokensIn) this.sessionMetrics.totalTokensIn += metric.tokensIn;
      if (metric.tokensOut) this.sessionMetrics.totalTokensOut += metric.tokensOut;
      if (metric.costUsd) this.sessionMetrics.totalCostUsd += metric.costUsd;
    }
  }

  trackTask(metric: TaskMetric): void {
    this.taskMetrics.push(metric);

    if (metric.status === 'completed' && this.sessionMetrics) {
      this.sessionMetrics.tasksCompleted++;
      
      if (!this.sessionMetrics.reposModified.includes(metric.repo)) {
        this.sessionMetrics.reposModified.push(metric.repo);
      }
      
      this.sessionMetrics.totalCommits += metric.commitsCreated;
      this.sessionMetrics.totalFilesChanged += metric.filesChanged;
    }
  }

  endSession(): SessionMetric {
    if (this.sessionMetrics) {
      this.sessionMetrics.endTime = new Date().toISOString();
      this.sessionMetrics.durationMs = 
        new Date(this.sessionMetrics.endTime).getTime() - 
        new Date(this.sessionMetrics.startTime).getTime();
    }
    return this.sessionMetrics!;
  }

  getToolUsageReport(): Record<string, { count: number; totalCost: number; totalTokens: number }> {
    const report: Record<string, { count: number; totalCost: number; totalTokens: number }> = {};

    for (const metric of this.toolMetrics) {
      if (!report[metric.tool]) {
        report[metric.tool] = { count: 0, totalCost: 0, totalTokens: 0 };
      }

      report[metric.tool].count++;
      report[metric.tool].totalCost += metric.costUsd || 0;
      report[metric.tool].totalTokens += (metric.tokensIn || 0) + (metric.tokensOut || 0);
    }

    return report;
  }

  getTaskReport(): {
    total: number;
    byStatus: Record<string, number>;
    byPriority: Record<string, number>;
    byRepo: Record<string, number>;
    avgDurationMs: number;
  } {
    const report = {
      total: this.taskMetrics.length,
      byStatus: {} as Record<string, number>,
      byPriority: {} as Record<string, number>,
      byRepo: {} as Record<string, number>,
      avgDurationMs: 0,
    };

    let totalDuration = 0;
    let completedCount = 0;

    for (const task of this.taskMetrics) {
      report.byStatus[task.status] = (report.byStatus[task.status] || 0) + 1;
      report.byPriority[task.priority] = (report.byPriority[task.priority] || 0) + 1;
      report.byRepo[task.repo] = (report.byRepo[task.repo] || 0) + 1;

      if (task.durationMs) {
        totalDuration += task.durationMs;
        completedCount++;
      }
    }

    report.avgDurationMs = completedCount > 0 ? totalDuration / completedCount : 0;

    return report;
  }

  exportMetrics() {
    return {
      session: this.sessionMetrics!,
      tools: this.toolMetrics,
      tasks: this.taskMetrics,
      summary: {
        toolUsage: this.getToolUsageReport(),
        taskReport: this.getTaskReport(),
      },
    };
  }

  saveToFile(filepath: string): void {
    const fs = require('fs');
    const metrics = this.exportMetrics();
    fs.writeFileSync(filepath, JSON.stringify(metrics, null, 2));
  }

  printSummary(): string {
    const toolReport = this.getToolUsageReport();
    const taskReport = this.getTaskReport();
    
    const lines = [
      '=== METRICS SUMMARY ===',
      '',
      'Tool Usage:',
      ...Object.entries(toolReport).map(([tool, stats]) => 
        `  ${tool}: ${stats.count} calls, ${stats.totalTokens.toLocaleString()} tokens, $${stats.totalCost.toFixed(4)}`
      ),
      '',
      'Tasks:',
      `  Total: ${taskReport.total}`,
      `  Completed: ${taskReport.byStatus.completed || 0}`,
      `  In Progress: ${taskReport.byStatus.in_progress || 0}`,
      `  Avg Duration: ${(taskReport.avgDurationMs / 1000 / 60).toFixed(1)}min`,
      '',
      'Session:',
      `  Duration: ${this.sessionMetrics ? ((Date.now() - new Date(this.sessionMetrics.startTime).getTime()) / 1000 / 60).toFixed(1) : 0}min`,
      `  Repos Modified: ${this.sessionMetrics?.reposModified.length || 0}`,
      `  Total Commits: ${this.sessionMetrics?.totalCommits || 0}`,
      `  Total Cost: $${this.sessionMetrics?.totalCostUsd.toFixed(4) || '0.0000'}`,
    ];
    
    return lines.join('\n');
  }
}

// Singleton instance for current session
let globalTracker: MetricsTracker | null = null;

export function initMetricsTracker(sessionId: string): MetricsTracker {
  globalTracker = new MetricsTracker(sessionId);
  return globalTracker;
}

export function getMetricsTracker(): MetricsTracker {
  if (!globalTracker) {
    throw new Error('MetricsTracker not initialized. Call initMetricsTracker() first.');
  }
  return globalTracker;
}

export function trackToolUsage(metric: Omit<ToolUsageMetric, 'timestamp'>): void {
  getMetricsTracker().trackToolUsage(metric);
}

export function trackTask(metric: TaskMetric): void {
  getMetricsTracker().trackTask(metric);
}
