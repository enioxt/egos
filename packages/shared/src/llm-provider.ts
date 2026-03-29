import type { AIAnalysisResult } from './types';

export type SharedLLMProvider = 'openrouter' | 'alibaba';

export const ALIBABA_TEST_MODELS = [
  'qwen-max',
  'qwen-plus',
  'qwen-flash',
  'qwen3-coder-plus',
  'qwen3.5-plus',
] as const;

/** Cost per 1M tokens (input, output) — USD */
const MODEL_COSTS: Record<string, [number, number]> = {
  'qwen-max': [1.6, 6.4],
  'qwen-plus': [0.8, 2.0],
  'qwen3-coder-plus': [0.8, 2.0],
  'qwen3.5-plus': [0.8, 2.0],
  'qwen-flash': [0, 0],
  'google/gemini-2.0-flash-001': [0.1, 0.4],
  'openai/gpt-4o-mini': [0.15, 0.6],
  'anthropic/claude-sonnet-4-20250514': [3.0, 15.0],
  'deepseek/deepseek-chat-v3-0324': [0.27, 1.1],
};

function estimateCost(model: string, tokensIn: number, tokensOut: number): number {
  const costs = MODEL_COSTS[model];
  if (!costs) return 0;
  return (tokensIn * costs[0] + tokensOut * costs[1]) / 1_000_000;
}

export async function chatWithLLM(params: {
  systemPrompt: string;
  userPrompt: string;
  model?: string;
  maxTokens?: number;
  temperature?: number;
  provider?: SharedLLMProvider;
  responseFormat?: 'json_object' | 'text';
}): Promise<AIAnalysisResult> {
  const provider = params.provider ?? (params.model?.startsWith('qwen') ? 'alibaba' : process.env.LLM_PROVIDER === 'alibaba' ? 'alibaba' : 'openrouter');
  const baseUrl = provider === 'alibaba'
    ? `${(process.env.ALIBABA_DASHSCOPE_BASE_URL || 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1').replace(/\/+$/, '')}/chat/completions`
    : 'https://openrouter.ai/api/v1/chat/completions';
  const apiKey = provider === 'alibaba' ? process.env.ALIBABA_DASHSCOPE_API_KEY : process.env.OPENROUTER_API_KEY;
  const model = params.model ?? (provider === 'alibaba' ? 'qwen-plus' : 'google/gemini-2.0-flash-001');

  if (!apiKey) {
    throw new Error(`${provider === 'alibaba' ? 'ALIBABA_DASHSCOPE_API_KEY' : 'OPENROUTER_API_KEY'} not set`);
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

  if (params.responseFormat === 'json_object' && provider !== 'alibaba') {
    body.response_format = { type: 'json_object' };
  }

  const response = await fetch(baseUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKey}`,
      ...(provider === 'openrouter' ? { 'HTTP-Referer': 'https://egos.dev', 'X-Title': 'egos' } : {}),
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error(`${provider} API error (${response.status}): ${await response.text()}`);
  }

  const data = await response.json() as { model?: string; usage?: AIAnalysisResult['usage']; choices?: Array<{ message?: { content?: string } }> };
  const usage = data.usage ?? { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 };
  const costUsd = estimateCost(model, usage.prompt_tokens, usage.completion_tokens);
  return {
    content: data.choices?.[0]?.message?.content ?? '',
    model: data.model ?? model,
    usage,
    cost_usd: costUsd,
  };
}
