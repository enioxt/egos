/**
 * LLM Router MCP Client
 *
 * Multi-provider LLM orchestration with cost tracking and intelligent model selection
 * Supports: Alibaba Qwen, OpenRouter (Claude, Llama, etc.)
 *
 * Responsibilities:
 * - Estimate token usage and costs
 * - Select optimal model based on criteria (speed, cost, quality)
 * - Track API call usage for billing
 * - Budget enforcement and alerts
 */

export interface ModelConfig {
  provider: string;
  model: string;
  costPer1mTokens: number;
  tier: 'fast-cheap' | 'balanced' | 'premium';
}

export interface CostEstimate {
  model: string;
  tokens: number;
  costUsd: number;
  provider: string;
}

export interface UsageRecord {
  timestamp: number;
  model: string;
  tokens: number;
  costUsd: number;
  taskId?: string;
}

export interface CostSummary {
  period: 'day' | 'week' | 'month';
  totalCostUsd: number;
  totalTokens: number;
  recordCount: number;
  topModels: Array<{
    model: string;
    costUsd: number;
    percentage: number;
  }>;
}

export interface ModelSelection {
  model: string;
  provider: string;
  reasoning: string;
  costUsd: number;
  estimatedTokens: number;
}

export class LLMRouterMCPClient {
  private models: Map<string, ModelConfig> = new Map();
  private usageHistory: UsageRecord[] = [];
  private monthlyBudget: number = 100;
  private perTaskMaxUsd: number = 10;
  private alertThreshold: number = 80; // percent

  constructor(config: {
    models?: ModelConfig[];
    monthlyBudget?: number;
    perTaskMaxUsd?: number;
    alertThresholdPercent?: number;
  } = {}) {
    // Initialize default models
    const defaultModels: ModelConfig[] = [
      {
        provider: 'alibaba',
        model: 'qwen-plus',
        costPer1mTokens: 0.0005,
        tier: 'fast-cheap',
      },
      {
        provider: 'openrouter',
        model: 'anthropic/claude-opus',
        costPer1mTokens: 15.0,
        tier: 'premium',
      },
      {
        provider: 'openrouter',
        model: 'meta-llama/llama-2-70b',
        costPer1mTokens: 0.80,
        tier: 'balanced',
      },
    ];

    const modelsToRegister = config.models || defaultModels;
    modelsToRegister.forEach(m => {
      this.models.set(m.model, m);
    });

    this.monthlyBudget = config.monthlyBudget || 100;
    this.perTaskMaxUsd = config.perTaskMaxUsd || 10;
    this.alertThreshold = config.alertThresholdPercent || 80;

    console.log(`[LLMRouter] Initialized with ${this.models.size} models`);
  }

  /**
   * Estimate token usage and cost for a prompt
   */
  estimateCost(prompt: string, model?: string): CostEstimate {
    const selectedModel = model || 'alibaba/qwen-plus';
    const config = this.models.get(selectedModel);

    if (!config) {
      throw new Error(`Model ${selectedModel} not found`);
    }

    // Rough estimation: ~4 chars per token on average
    const estimatedTokens = Math.ceil(prompt.length / 4);
    const costUsd = (estimatedTokens / 1_000_000) * config.costPer1mTokens;

    console.log(`[LLMRouter] Cost estimate for ${selectedModel}: ${estimatedTokens} tokens, $${costUsd.toFixed(6)}`);

    return {
      model: selectedModel,
      tokens: estimatedTokens,
      costUsd,
      provider: config.provider,
    };
  }

  /**
   * Select optimal model based on criteria
   */
  selectModel(criteria: {
    task: string;
    priority: 'speed' | 'cost' | 'quality' | 'balanced';
    maxCostUsd?: number;
  }): ModelSelection {
    let selectedModel: ModelConfig | null = null;
    let reasoning = '';

    const maxCost = criteria.maxCostUsd || this.perTaskMaxUsd;

    // Filter by cost constraint
    const eligibleModels = Array.from(this.models.values()).filter(
      m => (m.costPer1mTokens / 1_000_000) * 1000 <= maxCost
    );

    if (eligibleModels.length === 0) {
      throw new Error(`No models available within cost constraint of $${maxCost}`);
    }

    // Select based on priority
    switch (criteria.priority) {
      case 'cost':
        selectedModel = eligibleModels.reduce((a, b) =>
          a.costPer1mTokens < b.costPer1mTokens ? a : b
        );
        reasoning = 'Selected cheapest model';
        break;

      case 'speed':
        selectedModel = eligibleModels.find(m => m.tier === 'fast-cheap') ||
          eligibleModels.find(m => m.tier === 'balanced') ||
          eligibleModels[0];
        reasoning = 'Selected fastest available model';
        break;

      case 'quality':
        selectedModel = eligibleModels.find(m => m.tier === 'premium') ||
          eligibleModels.find(m => m.tier === 'balanced') ||
          eligibleModels[0];
        reasoning = 'Selected highest quality model';
        break;

      case 'balanced':
        selectedModel = eligibleModels.find(m => m.tier === 'balanced') ||
          eligibleModels[0];
        reasoning = 'Selected balanced tradeoff model';
        break;
    }

    if (!selectedModel) {
      selectedModel = eligibleModels[0];
      reasoning = 'Selected first eligible model';
    }

    // Estimate cost for a typical request (~1000 tokens)
    const estimatedTokens = 1000;
    const costUsd = (estimatedTokens / 1_000_000) * selectedModel.costPer1mTokens;

    console.log(`[LLMRouter] Selected ${selectedModel.model}: ${reasoning}`);

    return {
      model: selectedModel.model,
      provider: selectedModel.provider,
      reasoning,
      costUsd,
      estimatedTokens,
    };
  }

  /**
   * Track API call usage for billing
   */
  trackUsage(model: string, tokens: number, costUsd: number, taskId?: string): void {
    const record: UsageRecord = {
      timestamp: Date.now(),
      model,
      tokens,
      costUsd,
      taskId,
    };

    this.usageHistory.push(record);

    console.log(`[LLMRouter] Tracked usage: ${model}, ${tokens} tokens, $${costUsd.toFixed(6)}`);

    // Check budget
    this.checkBudgetStatus();
  }

  /**
   * Get cost summary for a time period
   */
  getCostSummary(period: 'day' | 'week' | 'month', endDate?: Date): CostSummary {
    const now = endDate ? new Date(endDate) : new Date();
    const periodMs = {
      day: 24 * 60 * 60 * 1000,
      week: 7 * 24 * 60 * 60 * 1000,
      month: 30 * 24 * 60 * 60 * 1000,
    }[period];

    const startTime = now.getTime() - periodMs;

    const relevantRecords = this.usageHistory.filter(r => r.timestamp >= startTime);

    // Calculate totals
    const totalCostUsd = relevantRecords.reduce((sum, r) => sum + r.costUsd, 0);
    const totalTokens = relevantRecords.reduce((sum, r) => sum + r.tokens, 0);

    // Group by model
    const modelStats = new Map<string, { costUsd: number; count: number }>();
    relevantRecords.forEach(r => {
      const existing = modelStats.get(r.model) || { costUsd: 0, count: 0 };
      existing.costUsd += r.costUsd;
      existing.count += 1;
      modelStats.set(r.model, existing);
    });

    const topModels = Array.from(modelStats.entries())
      .map(([model, stats]) => ({
        model,
        costUsd: stats.costUsd,
        percentage: totalCostUsd > 0 ? (stats.costUsd / totalCostUsd) * 100 : 0,
      }))
      .sort((a, b) => b.costUsd - a.costUsd)
      .slice(0, 5);

    return {
      period,
      totalCostUsd,
      totalTokens,
      recordCount: relevantRecords.length,
      topModels,
    };
  }

  /**
   * Check if budget is available for operation
   */
  checkBudget(estimatedCostUsd: number): {
    available: boolean;
    remainingBudget: number;
    percentageUsed: number;
  } {
    const currentMonth = new Date();
    const summary = this.getCostSummary('month', currentMonth);

    const totalUsedThisMonth = summary.totalCostUsd;
    const remainingBudget = this.monthlyBudget - totalUsedThisMonth;
    const percentageUsed = (totalUsedThisMonth / this.monthlyBudget) * 100;

    const available = remainingBudget >= estimatedCostUsd;

    console.log(
      `[LLMRouter] Budget check: $${totalUsedThisMonth.toFixed(2)}/$${this.monthlyBudget} used (${percentageUsed.toFixed(1)}%)`
    );

    return {
      available,
      remainingBudget,
      percentageUsed,
    };
  }

  /**
   * Check budget status and alert if threshold exceeded
   */
  private checkBudgetStatus(): void {
    const summary = this.getCostSummary('month');
    const percentageUsed = (summary.totalCostUsd / this.monthlyBudget) * 100;

    if (percentageUsed >= this.alertThreshold) {
      console.warn(
        `[LLMRouter] ALERT: Budget threshold (${this.alertThreshold}%) exceeded: ${percentageUsed.toFixed(1)}%`
      );
    }
  }

  /**
   * Get model configuration
   */
  getModelConfig(model: string): ModelConfig | undefined {
    return this.models.get(model);
  }

  /**
   * List all registered models
   */
  listModels(): ModelConfig[] {
    return Array.from(this.models.values());
  }

  /**
   * Register a new model
   */
  registerModel(config: ModelConfig): void {
    this.models.set(config.model, config);
    console.log(`[LLMRouter] Registered model: ${config.model}`);
  }

  /**
   * Get usage history
   */
  getUsageHistory(limit: number = 100): UsageRecord[] {
    return this.usageHistory.slice(-limit);
  }

  /**
   * Clear usage history (for testing)
   */
  clearHistory(): void {
    this.usageHistory = [];
    console.log('[LLMRouter] Cleared usage history');
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    return this.models.size > 0;
  }
}

export default LLMRouterMCPClient;
