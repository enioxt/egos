import type { AIAnalysisResult } from './types';

export type SharedLLMProvider = 'openrouter' | 'alibaba';

export const ALIBABA_TEST_MODELS = [
  'qwen-max',
  'qwen-plus',
  'qwen-flash',
  'qwen3-coder-plus',
  'qwen3.5-plus',
] as const;

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
  return {
    content: data.choices?.[0]?.message?.content ?? '',
    model: data.model ?? model,
    usage: data.usage ?? { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
    cost_usd: 0,
  };
}
