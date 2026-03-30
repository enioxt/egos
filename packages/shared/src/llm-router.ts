/**
 * Multi-LLM Router — EGOS-072
 *
 * Utility function U(m,t) = wc*Capability + wr*Reliability - ck*Cost - cq*QuotaRisk
 *
 * Selects the optimal LLM model for a given task based on:
 * - Capability match (does this model excel at this task type?)
 * - Reliability (uptime, error rate)
 * - Cost per token
 * - Quota risk (how close are we to rate limits?)
 *
 * Lanes:
 * - Planner: complex reasoning, architecture (GPT, Claude)
 * - Executor: code generation, structured output (Claude, Qwen)
 * - Cheap: high-volume, low-complexity (Gemini Flash, Qwen-turbo)
 * - Sovereign: self-hosted or BR-compliant (Qwen via DashScope)
 *
 * First consumer: Guard Brasil API (PRI Layer 3)
 */

// ── Types ──────────────────────────────────────────────────

export type TaskType =
  | 'pii_detection'      // PII classification (cheap, fast)
  | 'bias_analysis'      // ATRiAN ethical review (needs reasoning)
  | 'text_generation'    // Content creation (mid-tier)
  | 'code_generation'    // Code output (needs precision)
  | 'summarization'      // Document summary (cheap is fine)
  | 'classification'     // Label/category (cheapest possible)
  | 'translation'        // PT-BR translation (mid-tier)
  | 'complex_reasoning'  // Multi-step analysis (top-tier)
  | 'structured_output'  // JSON/schema output (needs precision)
  | 'fallback';          // Default when type unknown

export type ModelLane = 'planner' | 'executor' | 'cheap' | 'sovereign';

export interface ModelConfig {
  id: string;
  name: string;
  provider: string;
  lane: ModelLane;
  costPer1kTokens: number;  // USD
  maxTokens: number;
  capabilities: Record<TaskType, number>;  // 0-100 score per task
  reliability: number;       // 0-100 (uptime + success rate)
  quotaLimit: number;        // requests per minute
  quotaUsed: number;         // current usage this minute
  enabled: boolean;
}

export interface RoutingDecision {
  selectedModel: ModelConfig;
  score: number;
  reasoning: string;
  alternatives: { model: string; score: number }[];
  fallbackChain: string[];
}

export interface RoutingWeights {
  capability: number;   // wc (default: 0.4)
  reliability: number;  // wr (default: 0.25)
  cost: number;         // ck (default: 0.2)
  quotaRisk: number;    // cq (default: 0.15)
}

// ── Default Model Registry ─────────────────────────────────

const DEFAULT_MODELS: ModelConfig[] = [
  {
    id: 'qwen-plus',
    name: 'Qwen Plus',
    provider: 'dashscope',
    lane: 'sovereign',
    costPer1kTokens: 0.0004,
    maxTokens: 32000,
    capabilities: {
      pii_detection: 85, bias_analysis: 75, text_generation: 80,
      code_generation: 80, summarization: 85, classification: 90,
      translation: 85, complex_reasoning: 70, structured_output: 85,
      fallback: 75,
    },
    reliability: 92,
    quotaLimit: 60,
    quotaUsed: 0,
    enabled: true,
  },
  {
    id: 'qwen-turbo',
    name: 'Qwen Turbo',
    provider: 'dashscope',
    lane: 'cheap',
    costPer1kTokens: 0.00008,
    maxTokens: 8000,
    capabilities: {
      pii_detection: 70, bias_analysis: 55, text_generation: 65,
      code_generation: 60, summarization: 75, classification: 85,
      translation: 70, complex_reasoning: 45, structured_output: 70,
      fallback: 60,
    },
    reliability: 95,
    quotaLimit: 120,
    quotaUsed: 0,
    enabled: true,
  },
  {
    id: 'gemini-flash',
    name: 'Gemini 2.0 Flash',
    provider: 'openrouter',
    lane: 'cheap',
    costPer1kTokens: 0.0001,
    maxTokens: 32000,
    capabilities: {
      pii_detection: 80, bias_analysis: 70, text_generation: 75,
      code_generation: 75, summarization: 80, classification: 88,
      translation: 80, complex_reasoning: 60, structured_output: 80,
      fallback: 70,
    },
    reliability: 90,
    quotaLimit: 60,
    quotaUsed: 0,
    enabled: true,
  },
  {
    id: 'claude-sonnet',
    name: 'Claude Sonnet 4.6',
    provider: 'openrouter',
    lane: 'executor',
    costPer1kTokens: 0.003,
    maxTokens: 200000,
    capabilities: {
      pii_detection: 90, bias_analysis: 95, text_generation: 95,
      code_generation: 98, summarization: 92, classification: 90,
      translation: 90, complex_reasoning: 92, structured_output: 95,
      fallback: 90,
    },
    reliability: 94,
    quotaLimit: 30,
    quotaUsed: 0,
    enabled: true,
  },
  {
    id: 'gpt-5.4',
    name: 'GPT 5.4',
    provider: 'openrouter',
    lane: 'planner',
    costPer1kTokens: 0.0025,
    maxTokens: 128000,
    capabilities: {
      pii_detection: 88, bias_analysis: 92, text_generation: 95,
      code_generation: 92, summarization: 90, classification: 88,
      translation: 92, complex_reasoning: 96, structured_output: 90,
      fallback: 88,
    },
    reliability: 93,
    quotaLimit: 30,
    quotaUsed: 0,
    enabled: true,
  },
];

// ── Router ─────────────────────────────────────────────────

const DEFAULT_WEIGHTS: RoutingWeights = {
  capability: 0.40,
  reliability: 0.25,
  cost: 0.20,
  quotaRisk: 0.15,
};

/**
 * Calculate utility score for a model given a task type.
 *
 * U(m,t) = wc * Capability(m,t) + wr * Reliability(m) - ck * CostNorm(m) - cq * QuotaRisk(m)
 */
function calculateUtility(
  model: ModelConfig,
  taskType: TaskType,
  weights: RoutingWeights,
  maxCost: number,
): number {
  const capability = model.capabilities[taskType] ?? model.capabilities.fallback;
  const reliability = model.reliability;

  // Normalize cost (0-100 where 100 = most expensive)
  const costNormalized = maxCost > 0 ? (model.costPer1kTokens / maxCost) * 100 : 0;

  // Quota risk: how close to limit (0 = safe, 100 = at limit)
  const quotaRisk = model.quotaLimit > 0
    ? (model.quotaUsed / model.quotaLimit) * 100
    : 100; // no quota info = assume risky

  return (
    weights.capability * capability +
    weights.reliability * reliability -
    weights.cost * costNormalized -
    weights.quotaRisk * quotaRisk
  );
}

/**
 * Select the optimal model for a given task.
 */
export function routeTask(
  taskType: TaskType,
  options?: {
    preferLane?: ModelLane;
    maxCostPer1k?: number;
    weights?: Partial<RoutingWeights>;
    models?: ModelConfig[];
  },
): RoutingDecision {
  const models = (options?.models ?? DEFAULT_MODELS).filter((m) => m.enabled);
  const weights = { ...DEFAULT_WEIGHTS, ...options?.weights };
  const maxCost = options?.maxCostPer1k ?? Math.max(...models.map((m) => m.costPer1kTokens));

  // Filter by lane preference if specified
  let candidates = options?.preferLane
    ? models.filter((m) => m.lane === options.preferLane)
    : models;

  // If no candidates in preferred lane, fall back to all
  if (candidates.length === 0) candidates = models;

  // Filter by max cost if specified
  if (options?.maxCostPer1k) {
    const affordable = candidates.filter((m) => m.costPer1kTokens <= options.maxCostPer1k!);
    if (affordable.length > 0) candidates = affordable;
  }

  // Score all candidates
  const scored = candidates
    .map((model) => ({
      model,
      score: calculateUtility(model, taskType, weights, maxCost),
    }))
    .sort((a, b) => b.score - a.score);

  const best = scored[0];
  const alternatives = scored.slice(1, 4).map((s) => ({
    model: s.model.id,
    score: Math.round(s.score * 100) / 100,
  }));

  // Build fallback chain (top 3, different providers if possible)
  const seenProviders = new Set<string>();
  const fallbackChain: string[] = [];
  for (const s of scored) {
    if (!seenProviders.has(s.model.provider) || fallbackChain.length < 2) {
      fallbackChain.push(s.model.id);
      seenProviders.add(s.model.provider);
    }
    if (fallbackChain.length >= 3) break;
  }

  return {
    selectedModel: best.model,
    score: Math.round(best.score * 100) / 100,
    reasoning: `Best for ${taskType}: ${best.model.name} (${best.model.lane} lane, $${best.model.costPer1kTokens}/1k tokens, capability ${best.model.capabilities[taskType]}/100)`,
    alternatives,
    fallbackChain,
  };
}

/**
 * Quick route for Guard Brasil API — optimized for cost.
 * PII detection → cheapest capable model.
 * Bias analysis → mid-tier with reasoning.
 */
export function routeGuardBrasil(taskType: 'pii_detection' | 'bias_analysis' | 'classification'): RoutingDecision {
  if (taskType === 'pii_detection' || taskType === 'classification') {
    return routeTask(taskType, {
      preferLane: 'cheap',
      weights: { capability: 0.30, reliability: 0.30, cost: 0.30, quotaRisk: 0.10 },
    });
  }
  // bias_analysis needs more reasoning power
  return routeTask(taskType, {
    preferLane: 'sovereign',
    weights: { capability: 0.45, reliability: 0.25, cost: 0.15, quotaRisk: 0.15 },
  });
}

/**
 * Update quota usage for a model (call after each API request).
 */
export function reportUsage(modelId: string, models?: ModelConfig[]): void {
  const registry = models ?? DEFAULT_MODELS;
  const model = registry.find((m) => m.id === modelId);
  if (model) model.quotaUsed++;
}

/**
 * Reset all quota counters (call every minute via setInterval).
 */
export function resetQuotas(models?: ModelConfig[]): void {
  const registry = models ?? DEFAULT_MODELS;
  for (const model of registry) model.quotaUsed = 0;
}

// ── Exports ────────────────────────────────────────────────

export { DEFAULT_MODELS, DEFAULT_WEIGHTS };
