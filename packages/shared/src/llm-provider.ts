import type { AIAnalysisResult } from './types';

export type SharedLLMProvider = 'openrouter' | 'alibaba';

export const ALIBABA_TEST_MODELS = [
  'qwen-max',
  'qwen-plus',
  'qwen-flash',
  'qwen3-coder-plus',
  'qwen3.5-plus',
] as const;

// ── Fallback Chain ─────────────────────────────────────────────────────────
// Priority: cheapest/fastest first → escalate on rate limit or missing key.
// DashScope quota is a ONE-TIME 1M token grant per model (90-day validity).
// Rate limits are RPM/TPM sliding windows — retry after ~60s on 429.
//
// Tiers:
//   'fast'    — classify, summarize, lint (qwen-flash/turbo class)
//   'default' — analysis, synthesis (qwen-plus class)
//   'deep'    — planning, code review, reasoning (qwen-max/claude class)

interface ModelEntry {
  provider: SharedLLMProvider;
  model: string;
  tier: 'fast' | 'default' | 'deep';
}

const MODEL_CHAIN: ModelEntry[] = [
  // Fast tier — 30K RPM, 10M TPM (DashScope free 1M tokens one-time)
  { provider: 'alibaba',    model: 'qwen3.5-flash',                   tier: 'fast' },
  { provider: 'alibaba',    model: 'qwen-flash',                       tier: 'fast' },
  { provider: 'alibaba',    model: 'qwen-turbo',                       tier: 'fast' },
  { provider: 'openrouter', model: 'google/gemini-flash-1.5',          tier: 'fast' },

  // Default tier — 15K RPM, 5M TPM
  { provider: 'alibaba',    model: 'qwen-plus',                        tier: 'default' },
  { provider: 'alibaba',    model: 'qwen3.5-plus',                     tier: 'default' },
  { provider: 'openrouter', model: 'google/gemini-2.0-flash-001',      tier: 'default' },

  // Deep tier — 600 RPM, 1M TPM (reasoning/planning)
  { provider: 'alibaba',    model: 'qwen3-max',                        tier: 'deep' },
  { provider: 'alibaba',    model: 'qwq-plus',                         tier: 'deep' }, // reasoning model
  { provider: 'openrouter', model: 'anthropic/claude-sonnet-4-5',      tier: 'deep' },
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
    lower.includes('throttl')
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

  if (!apiKey) throw new Error(`SKIP: ${provider} key not set`);

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

  // Build chain from tier preference
  const tier = params.tier ?? 'default';
  let chain: ModelEntry[];
  if (tier === 'fast') {
    chain = MODEL_CHAIN.filter((e) => e.tier === 'fast');
  } else if (tier === 'deep') {
    chain = MODEL_CHAIN.filter((e) => e.tier === 'deep' || e.tier === 'default');
  } else {
    // default: try default-tier first, then fast as fallback (never deep)
    chain = MODEL_CHAIN.filter((e) => e.tier === 'default' || e.tier === 'fast');
  }

  // If a provider is forced, prioritize it in the chain order
  if (params.provider) {
    const pref = chain.filter((e) => e.provider === params.provider);
    const rest = chain.filter((e) => e.provider !== params.provider);
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
