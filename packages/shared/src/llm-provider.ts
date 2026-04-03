import type { AIAnalysisResult } from './types';

export type SharedLLMProvider = 'openrouter' | 'alibaba';

// ── Architecture ────────────────────────────────────────────────────────────
// ORCHESTRATOR: Claude Code (Opus + Sonnet + Haiku) - R$550/mês plan
//   → Unlimited rate limit on all 3 models
//   → Opus: complex reasoning, architecture decisions
//   → Sonnet: code generation, analysis
//   → Haiku: fast classification, quick tasks
//   → This session IS the primary orchestrator, not routed through here
//
// BACKGROUND AGENTS (VPS): Use this fallback chain
//   Priority: Alibaba (free tier) → OpenRouter (cheap models only)
//   Rule: Exhaust ALL Alibaba models before trying OpenRouter
//
// Alibaba DashScope: ONE-TIME 1M token grant per model (90-day validity)
//   Models: qwen-flash, qwen-plus, qwen-max, qwq-plus (reasoning)
//   Rate limits: 30K RPM (fast), 15K RPM (default), 600 RPM (deep)
//
// OpenRouter: Only for when Alibaba quota exhausted
//   Models: Gemini Flash (free/cheap), Hermes-3 (BRAID executor)
//   NO Claude models - orchestrator already has Opus/Sonnet/Haiku

export const ALIBABA_MODELS = [
  'qwen-max',
  'qwen-plus',
  'qwen-flash',
  'qwen3-coder-plus',
  'qwen3.5-plus',
  'qwen-turbo',
  'qwq-plus',
] as const;

// ── Fallback Chain ─────────────────────────────────────────────────────────
// Priority: Alibaba (all models) → OpenRouter (cheap models only)
// Claude Code Opus is the orchestrator - not in this chain

interface ModelEntry {
  provider: SharedLLMProvider;
  model: string;
  tier: 'fast' | 'default' | 'deep';
}

// Tier 1: Alibaba (FREE - exhaust all before OpenRouter)
const ALIBABA_CHAIN: ModelEntry[] = [
  // Fast tier — 30K RPM, 10M TPM (free 1M tokens)
  { provider: 'alibaba', model: 'qwen3.5-flash',   tier: 'fast' },
  { provider: 'alibaba', model: 'qwen-flash',       tier: 'fast' },
  { provider: 'alibaba', model: 'qwen-turbo',        tier: 'fast' },
  { provider: 'alibaba', model: 'qwen3-coder-plus', tier: 'fast' },

  // Default tier — 15K RPM, 5M TPM
  { provider: 'alibaba', model: 'qwen-plus',    tier: 'default' },
  { provider: 'alibaba', model: 'qwen3.5-plus', tier: 'default' },

  // Deep tier — 600 RPM, 1M TPM (reasoning/planning)
  { provider: 'alibaba', model: 'qwen-max',  tier: 'deep' },
  { provider: 'alibaba', model: 'qwq-plus',  tier: 'deep' },
];

// Tier 2: OpenRouter (CHEAP - only after Alibaba exhausted)
// NO Claude models - use orchestrator (Claude Code Opus) for complex tasks
const OPENROUTER_CHAIN: ModelEntry[] = [
  // Fast tier - Gemini Flash (essentially free)
  { provider: 'openrouter', model: 'google/gemini-flash-1.5',     tier: 'fast' },
  { provider: 'openrouter', model: 'google/gemini-2.0-flash-001', tier: 'default' },

  // Default tier - Hermes-3 for BRAID/structured output
  { provider: 'openrouter', model: 'nousresearch/hermes-3-llama-3.1-70b', tier: 'default' },

  // Deep tier - High capability, low cost (no Claude)
  { provider: 'openrouter', model: 'google/gemini-2.5-pro',     tier: 'deep' },
  { provider: 'openrouter', model: 'meta-llama/llama-4-maverick', tier: 'deep' },
];

/** Detect rate-limit or quota exhaustion from HTTP status + response body */
function isRateLimitError(status: number, body: string): boolean {
  if (status === 429) return true;
  const lower = body.toLowerCase();
  return (
    lower.includes('rate limit exceeded') ||
    lower.includes('requests rate limit') ||
    lower.includes('allocated quota exceeded') ||
    lower.includes('request rate increased too quickly') ||
    lower.includes('throttl') ||
    lower.includes('quota') ||
    lower.includes('insufficient funds') ||
    lower.includes('credit exhausted')
  );
}

// ── Single model caller ────────────────────────────────────────────────────

async function callModel(
  entry: ModelEntry,
  params: {
    systemPrompt: string;
    userPrompt: string;
    maxTokens?: number;
    temperature?: number;
    responseFormat?: 'json_object' | 'text';
  }
): Promise<AIAnalysisResult> {
  const { provider, model } = entry;
  const baseUrl =
    provider === 'alibaba'
      ? `${(process.env.ALIBABA_DASHSCOPE_BASE_URL || 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1').replace(/\/+$/, '')}/chat/completions`
      : 'https://openrouter.ai/api/v1/chat/completions';
  const apiKey =
    provider === 'alibaba'
      ? process.env.ALIBABA_DASHSCOPE_API_KEY
      : process.env.OPENROUTER_API_KEY;

  if (!apiKey) throw new Error(`SKIP: ${provider === 'alibaba' ? 'ALIBABA_DASHSCOPE_API_KEY' : 'OPENROUTER_API_KEY'} not set`);

  const body: Record<string, unknown> = {
    model,
    messages: [
      { role: 'system', content: params.systemPrompt },
      { role: 'user', content: params.userPrompt },
    ],
    max_tokens: params.maxTokens ?? 2000,
    temperature: params.temperature ?? 0.3,
  };

  if (params.responseFormat === 'json_object' && provider !== 'alibaba') {
    body.response_format = { type: 'json_object' };
  }

  const response = await fetch(baseUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`,
      ...(provider === 'openrouter'
        ? { 'HTTP-Referer': 'https://egos.dev', 'X-Title': 'egos' }
        : {}),
    },
    body: JSON.stringify(body),
  });

  const responseText = await response.text();

  if (!response.ok) {
    if (isRateLimitError(response.status, responseText)) {
      throw new Error(`RATE_LIMIT: ${provider}/${model} (HTTP ${response.status})`);
    }
    // Auth errors — don't bother continuing chain
    if (response.status === 401 || response.status === 403) {
      throw new Error(`AUTH_ERROR: ${provider}/${model} (HTTP ${response.status}): ${responseText.slice(0, 200)}`);
    }
    throw new Error(`API_ERROR: ${provider}/${model} (HTTP ${response.status}): ${responseText.slice(0, 200)}`);
  }

  const data = JSON.parse(responseText) as {
    model?: string;
    usage?: AIAnalysisResult['usage'];
    choices?: Array<{ message?: { content?: string } }>;
  };
  return {
    content: data.choices?.[0]?.message?.content ?? '',
    model: data.model ?? model,
    usage: data.usage ?? { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
    cost_usd: 0,
  };
}

// ── Main export with automatic fallback chain ─────────────────────────────

export async function chatWithLLM(params: {
  systemPrompt: string;
  userPrompt: string;
  model?: string;
  maxTokens?: number;
  temperature?: number;
  provider?: SharedLLMProvider;
  responseFormat?: 'json_object' | 'text';
  /** Task tier — controls which models are tried first. Default: 'default' */
  tier?: 'fast' | 'default' | 'deep';
}): Promise<AIAnalysisResult> {
  // Explicit model: single attempt, no fallback chain
  if (params.model) {
    const explicitProvider: SharedLLMProvider =
      params.provider ??
      (params.model.startsWith('qwen') ? 'alibaba' : 'openrouter');
    return callModel(
      { provider: explicitProvider, model: params.model, tier: params.tier ?? 'default' },
      params
    );
  }

  // Build chain: ALL Alibaba models first (exhaustive), then OpenRouter
  const tier = params.tier ?? 'default';
  let alibabaModels: ModelEntry[];
  let openrouterModels: ModelEntry[];

  if (tier === 'fast') {
    alibabaModels = ALIBABA_CHAIN.filter((e: ModelEntry) => e.tier === 'fast');
    openrouterModels = OPENROUTER_CHAIN.filter((e: ModelEntry) => e.tier === 'fast');
  } else if (tier === 'deep') {
    alibabaModels = ALIBABA_CHAIN.filter((e: ModelEntry) => e.tier === 'deep' || e.tier === 'default');
    openrouterModels = OPENROUTER_CHAIN.filter((e: ModelEntry) => e.tier === 'deep' || e.tier === 'default');
  } else {
    // default: try default-tier first, then fast as fallback (never deep)
    alibabaModels = ALIBABA_CHAIN.filter((e: ModelEntry) => e.tier === 'default' || e.tier === 'fast');
    openrouterModels = OPENROUTER_CHAIN.filter((e: ModelEntry) => e.tier === 'default' || e.tier === 'fast');
  }

  // Chain order: Alibaba first (exhaustive), then OpenRouter
  let chain: ModelEntry[] = [...alibabaModels, ...openrouterModels];

  // If a provider is forced, prioritize it in the chain order
  if (params.provider) {
    const pref = chain.filter((e: ModelEntry) => e.provider === params.provider);
    const rest = chain.filter((e: ModelEntry) => e.provider !== params.provider);
    chain = [...pref, ...rest];
  }

  let lastError = '';
  for (const entry of chain) {
    try {
      const result = await callModel(entry, params);
      if (lastError) {
        console.warn(`[llm-provider] Used ${entry.provider}/${entry.model} after fallback. Prior error: ${lastError}`);
      }
      return result;
    } catch (err: any) {
      lastError = err?.message ?? String(err);
      // Hard auth errors — abort chain immediately
      if (lastError.startsWith('AUTH_ERROR:')) throw err;
      // Rate limit or missing key — continue to next in chain
      continue;
    }
  }
  throw new Error(`[llm-provider] All models in chain exhausted. Last error: ${lastError}`);
}
