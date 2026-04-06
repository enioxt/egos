import type { AIAnalysisResult } from './types';

export type SharedLLMProvider = 'openrouter' | 'alibaba' | 'google';

// ── Architecture ────────────────────────────────────────────────────────────
// ORCHESTRATOR: Claude Code (Opus + Sonnet + Haiku) - R$550/mês plan
//   → Unlimited rate limit on all 3 models
//   → This session IS the primary orchestrator, not routed through here
//
// BACKGROUND AGENTS (VPS): Use this fallback chain
//   Priority: Google AI Studio → Alibaba DashScope → OpenRouter
//
// Google AI Studio (PRIORITY 1 — Completely Free, No Expiry):
//   Models: gemma-4-31b-it (1,500 req/day), gemini-2.5-flash (500 req/day)
//   Key: GOOGLE_AI_STUDIO_API_KEY | Base: generativelanguage.googleapis.com
//   WARNING: gemma-4-31b is excellent for reasoning/coding but weak on tool-calling
//
// Alibaba DashScope (PRIORITY 2 — Free One-Time Grant):
//   Models: qwen-flash, qwen-plus, qwen-max, qwq-plus (reasoning)
//   ONE-TIME 1M token grant per model (90-day validity)
//   Rate limits: 30K RPM (fast), 15K RPM (default), 600 RPM (deep)
//
// OpenRouter (PRIORITY 3 — Paid Fallback):
//   qwen3.6-plus:free → $0/token, unlimited rate (primary free option here)
//   Hermes-3, Gemini Flash, Llama 4 — only when others exhausted
//   NO Claude models — orchestrator handles Claude via Claude Code plan

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

interface ModelEntry {
  provider: SharedLLMProvider;
  model: string;
  tier: 'fast' | 'default' | 'deep';
}

// Tier 0: Google AI Studio (FREE — no expiry, 1500 req/day for 31B model)
// NOTE: gemma-4-31b-it weak on tool-calling → use for reasoning/coding only
const GOOGLE_CHAIN: ModelEntry[] = [
  // Fast tier — gemini-2.5-flash (500 req/day free, multimodal)
  { provider: 'google', model: 'gemini-2.5-flash', tier: 'fast' },
  // Default tier — gemma-4-31b-it (1,500 req/day free, best coding/reasoning)
  { provider: 'google', model: 'gemma-4-31b-it',   tier: 'default' },
  // Deep tier — gemini-2.5-pro (50 req/day free, strongest reasoning)
  { provider: 'google', model: 'gemini-2.5-pro',   tier: 'deep' },
];

// Tier 1: Alibaba (FREE one-time grant — exhaust before OpenRouter)
const ALIBABA_CHAIN: ModelEntry[] = [
  // Fast tier — 30K RPM, 10M TPM (free 1M tokens)
  { provider: 'alibaba', model: 'qwen3.5-flash',   tier: 'fast' },
  { provider: 'alibaba', model: 'qwen-flash',       tier: 'fast' },
  { provider: 'alibaba', model: 'qwen-turbo',       tier: 'fast' },
  { provider: 'alibaba', model: 'qwen3-coder-plus', tier: 'fast' },

  // Default tier — 15K RPM, 5M TPM
  { provider: 'alibaba', model: 'qwen-plus',    tier: 'default' },
  { provider: 'alibaba', model: 'qwen3.5-plus', tier: 'default' },

  // Deep tier — 600 RPM, 1M TPM (reasoning/planning)
  { provider: 'alibaba', model: 'qwen-max',  tier: 'deep' },
  { provider: 'alibaba', model: 'qwq-plus',  tier: 'deep' },
];

// Tier 2: OpenRouter — free model first, then cheap paid
const OPENROUTER_CHAIN: ModelEntry[] = [
  // FREE — Qwen 3.6 Plus (prompt=0, completion=0, no rate limit published)
  { provider: 'openrouter', model: 'qwen/qwen3.6-plus:free', tier: 'fast' },
  { provider: 'openrouter', model: 'qwen/qwen3.6-plus:free', tier: 'default' },

  // Gemini Flash (essentially free)
  { provider: 'openrouter', model: 'google/gemini-2.0-flash-001', tier: 'default' },

  // Hermes-3 for BRAID/structured output (BRAID mechanical executor)
  { provider: 'openrouter', model: 'nousresearch/hermes-3-llama-3.1-70b', tier: 'default' },

  // Deep tier — High capability, low cost (no Claude)
  { provider: 'openrouter', model: 'google/gemini-2.5-pro',       tier: 'deep' },
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

  let baseUrl: string;
  let apiKey: string | undefined;

  if (provider === 'alibaba') {
    baseUrl = `${(process.env.ALIBABA_DASHSCOPE_BASE_URL || 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1').replace(/\/+$/, '')}/chat/completions`;
    apiKey = process.env.ALIBABA_DASHSCOPE_API_KEY;
  } else if (provider === 'google') {
    // Google AI Studio: OpenAI-compatible endpoint
    baseUrl = 'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions';
    apiKey = process.env.GOOGLE_AI_STUDIO_API_KEY;
  } else {
    baseUrl = 'https://openrouter.ai/api/v1/chat/completions';
    apiKey = process.env.OPENROUTER_API_KEY;
  }

  if (!apiKey) {
    const keyName = provider === 'alibaba' ? 'ALIBABA_DASHSCOPE_API_KEY' : provider === 'google' ? 'GOOGLE_AI_STUDIO_API_KEY' : 'OPENROUTER_API_KEY';
    throw new Error(`SKIP: ${keyName} not set`);
  }

  const body: Record<string, unknown> = {
    model,
    messages: [
      { role: 'system', content: params.systemPrompt },
      { role: 'user', content: params.userPrompt },
    ],
    max_tokens: params.maxTokens ?? 2000,
    temperature: params.temperature ?? 0.3,
  };

  if (params.responseFormat === 'json_object' && provider === 'openrouter') {
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
      (params.model.startsWith('qwen') && !params.model.includes(':') ? 'alibaba'
        : params.model.startsWith('gemma') || params.model.startsWith('gemini') ? 'google'
        : 'openrouter');
    return callModel(
      { provider: explicitProvider, model: params.model, tier: params.tier ?? 'default' },
      params
    );
  }

  // Build chain: Google (free/daily limit) → Alibaba (free grant) → OpenRouter (paid fallback)
  const tier = params.tier ?? 'default';

  const googleModels = GOOGLE_CHAIN.filter((e: ModelEntry) =>
    tier === 'fast' ? e.tier === 'fast'
    : tier === 'deep' ? true
    : e.tier !== 'deep'
  );

  let alibabaModels: ModelEntry[];
  let openrouterModels: ModelEntry[];

  if (tier === 'fast') {
    alibabaModels = ALIBABA_CHAIN.filter((e: ModelEntry) => e.tier === 'fast');
    openrouterModels = OPENROUTER_CHAIN.filter((e: ModelEntry) => e.tier === 'fast');
  } else if (tier === 'deep') {
    alibabaModels = ALIBABA_CHAIN.filter((e: ModelEntry) => e.tier === 'deep' || e.tier === 'default');
    openrouterModels = OPENROUTER_CHAIN.filter((e: ModelEntry) => e.tier === 'deep' || e.tier === 'default');
  } else {
    alibabaModels = ALIBABA_CHAIN.filter((e: ModelEntry) => e.tier === 'default' || e.tier === 'fast');
    openrouterModels = OPENROUTER_CHAIN.filter((e: ModelEntry) => e.tier === 'default' || e.tier === 'fast');
  }

  // Chain order: Google (free) → Alibaba (free grant) → OpenRouter
  let chain: ModelEntry[] = [...googleModels, ...alibabaModels, ...openrouterModels];

  // If a provider is forced, prioritize it at front of chain
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
