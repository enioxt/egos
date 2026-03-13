/**
 * Model Router — Task-Aware LLM Selection
 *
 * Similar to OpenRouter's model routing but local and cost-aware.
 * Each task type maps to the optimal model/provider combo based on:
 *   - capability fit
 *   - cost per 1M tokens
 *   - latency profile
 *   - quota availability
 *
 * Usage:
 *   const route = resolveModel('code_review');
 *   const result = await chatWithLLM({ ...route, systemPrompt, userPrompt });
 */

import type { SharedLLMProvider } from './llm-provider';

// ═══════════════════════════════════════════════════════════
// Task Types
// ═══════════════════════════════════════════════════════════

export type TaskType =
  | 'orchestration'     // agent coordination, planning, complex reasoning
  | 'code_generation'   // writing new code
  | 'code_review'       // reviewing diffs, finding bugs
  | 'analysis'          // data analysis, research synthesis
  | 'summarization'     // condensing long text
  | 'classification'    // intent detection, categorization
  | 'chat'              // conversational, general purpose
  | 'translation'       // language translation
  | 'extraction'        // structured data extraction from text
  | 'fast_check'        // quick validation, yes/no, simple checks
  ;

// ═══════════════════════════════════════════════════════════
// Model Profiles
// ═══════════════════════════════════════════════════════════

export interface ModelProfile {
  id: string;
  provider: SharedLLMProvider;
  displayName: string;
  costPer1MInput: number;   // USD
  costPer1MOutput: number;  // USD
  maxContext: number;        // tokens
  strengths: TaskType[];
  tier: 'premium' | 'balanced' | 'economy';
  envKey: string;            // which env var holds the API key
}

export const MODEL_CATALOG: ModelProfile[] = [
  // ── Alibaba / DashScope ──
  {
    id: 'qwen-max',
    provider: 'alibaba',
    displayName: 'Qwen Max',
    costPer1MInput: 1.6,
    costPer1MOutput: 6.4,
    maxContext: 32768,
    strengths: ['orchestration', 'analysis', 'code_review'],
    tier: 'premium',
    envKey: 'ALIBABA_DASHSCOPE_API_KEY',
  },
  {
    id: 'qwen-plus',
    provider: 'alibaba',
    displayName: 'Qwen Plus',
    costPer1MInput: 0.8,
    costPer1MOutput: 2.0,
    maxContext: 131072,
    strengths: ['orchestration', 'code_generation', 'analysis', 'chat', 'extraction'],
    tier: 'balanced',
    envKey: 'ALIBABA_DASHSCOPE_API_KEY',
  },
  {
    id: 'qwen3-coder-plus',
    provider: 'alibaba',
    displayName: 'Qwen3 Coder Plus',
    costPer1MInput: 0.8,
    costPer1MOutput: 2.0,
    maxContext: 131072,
    strengths: ['code_generation', 'code_review'],
    tier: 'balanced',
    envKey: 'ALIBABA_DASHSCOPE_API_KEY',
  },
  {
    id: 'qwen-flash',
    provider: 'alibaba',
    displayName: 'Qwen Flash',
    costPer1MInput: 0.0,
    costPer1MOutput: 0.0,
    maxContext: 131072,
    strengths: ['fast_check', 'classification', 'summarization', 'translation', 'chat'],
    tier: 'economy',
    envKey: 'ALIBABA_DASHSCOPE_API_KEY',
  },
  // ── OpenRouter ──
  {
    id: 'google/gemini-2.0-flash-001',
    provider: 'openrouter',
    displayName: 'Gemini 2.0 Flash',
    costPer1MInput: 0.1,
    costPer1MOutput: 0.4,
    maxContext: 1048576,
    strengths: ['summarization', 'translation', 'chat', 'fast_check', 'extraction'],
    tier: 'economy',
    envKey: 'OPENROUTER_API_KEY',
  },
  {
    id: 'openai/gpt-4o-mini',
    provider: 'openrouter',
    displayName: 'GPT-4o Mini',
    costPer1MInput: 0.15,
    costPer1MOutput: 0.6,
    maxContext: 128000,
    strengths: ['chat', 'extraction', 'classification', 'fast_check'],
    tier: 'economy',
    envKey: 'OPENROUTER_API_KEY',
  },
  {
    id: 'anthropic/claude-sonnet-4-20250514',
    provider: 'openrouter',
    displayName: 'Claude Sonnet 4',
    costPer1MInput: 3.0,
    costPer1MOutput: 15.0,
    maxContext: 200000,
    strengths: ['orchestration', 'code_generation', 'code_review', 'analysis'],
    tier: 'premium',
    envKey: 'OPENROUTER_API_KEY',
  },
  {
    id: 'deepseek/deepseek-chat-v3-0324',
    provider: 'openrouter',
    displayName: 'DeepSeek V3',
    costPer1MInput: 0.27,
    costPer1MOutput: 1.1,
    maxContext: 65536,
    strengths: ['code_generation', 'code_review', 'analysis'],
    tier: 'balanced',
    envKey: 'OPENROUTER_API_KEY',
  },
];

// ═══════════════════════════════════════════════════════════
// Router Logic
// ═══════════════════════════════════════════════════════════

export type CostPreference = 'economy' | 'balanced' | 'premium';

export interface RouteOptions {
  task: TaskType;
  cost?: CostPreference;
  preferProvider?: SharedLLMProvider;
  minContext?: number;
}

export interface ResolvedRoute {
  model: string;
  provider: SharedLLMProvider;
  profile: ModelProfile;
}

function isAvailable(profile: ModelProfile): boolean {
  return !!process.env[profile.envKey];
}

const TIER_SCORE: Record<string, Record<string, number>> = {
  economy:  { economy: 3, balanced: 2, premium: 1 },
  balanced: { economy: 1, balanced: 3, premium: 2 },
  premium:  { economy: 1, balanced: 2, premium: 3 },
};

/**
 * Resolve the best model for a given task and cost preference.
 *
 * Scoring: strength match (4) + tier preference (1-3) + provider preference (1)
 * Ties broken by lower cost.
 */
export function resolveModel(taskOrOpts: TaskType | RouteOptions): ResolvedRoute {
  const opts: RouteOptions = typeof taskOrOpts === 'string'
    ? { task: taskOrOpts }
    : taskOrOpts;

  const { task, cost = 'balanced', preferProvider, minContext } = opts;
  const tierMap = TIER_SCORE[cost] ?? TIER_SCORE.balanced;

  const candidates = MODEL_CATALOG
    .filter(isAvailable)
    .filter(p => !minContext || p.maxContext >= minContext);

  if (candidates.length === 0) {
    throw new Error(
      `No LLM provider available. Set ALIBABA_DASHSCOPE_API_KEY or OPENROUTER_API_KEY in .env`
    );
  }

  const scored = candidates.map(p => {
    let score = 0;
    if (p.strengths.includes(task)) score += 4;
    score += tierMap[p.tier] ?? 1;
    if (preferProvider && p.provider === preferProvider) score += 1;
    const avgCost = (p.costPer1MInput + p.costPer1MOutput) / 2;
    return { profile: p, score, avgCost };
  });

  scored.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    return a.avgCost - b.avgCost;
  });

  const best = scored[0].profile;
  return { model: best.id, provider: best.provider, profile: best };
}

/**
 * Convenience: resolve + format for chatWithLLM params.
 */
export function routeForChat(taskOrOpts: TaskType | RouteOptions): {
  model: string;
  provider: SharedLLMProvider;
} {
  const { model, provider } = resolveModel(taskOrOpts);
  return { model, provider };
}

/**
 * List all available models with their task strengths and pricing.
 */
export function listAvailableModels(): Array<ModelProfile & { available: boolean }> {
  return MODEL_CATALOG.map(p => ({ ...p, available: isAvailable(p) }));
}
