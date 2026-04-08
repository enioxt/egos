/**
 * Hermes Agent LLM Provider Adapter
 * Bridges EGOS TypeScript codebase with the Hermes Python agent runner on VPS.
 *
 * Primary model: Alibaba DashScope qwen-plus
 * Fallback:      OpenRouter (google/gemma-4-26b-a4b-it:free, qwen/qwen3-coder:free)
 *
 * Migrated from Codex proxy — 2026-04-08 (CDX→HRM migration)
 */

const DASHSCOPE_BASE = process.env.ALIBABA_DASHSCOPE_BASE_URL
  ?? 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1';
const DASHSCOPE_KEY = process.env.ALIBABA_DASHSCOPE_API_KEY ?? '';
const OPENROUTER_KEY = process.env.OPENROUTER_API_KEY ?? '';

export type HermesModel =
  | 'qwen-plus'
  | 'qwen-max'
  | 'qwen-turbo'
  | 'google/gemma-4-26b-a4b-it:free'
  | 'google/gemma-4-31b-it:free'
  | 'qwen/qwen3-coder:free'
  | 'qwen/qwen3-next-80b-a3b-instruct:free';

export interface HermesMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface HermesOptions {
  model?: HermesModel;
  maxTokens?: number;
  systemPrompt?: string;
  timeoutMs?: number;
}

/**
 * Call DashScope (Alibaba qwen-plus) with OpenRouter fallback.
 * Mirrors the Hermes Python agent's provider chain.
 */
export async function callHermes(
  prompt: string,
  options: HermesOptions = {}
): Promise<{ content: string; provider: string; model: string }> {
  const { maxTokens = 1024, systemPrompt, timeoutMs = 30000 } = options;

  const messages: HermesMessage[] = [];
  if (systemPrompt) messages.push({ role: 'system', content: systemPrompt });
  messages.push({ role: 'user', content: prompt });

  // Primary: Alibaba DashScope
  if (DASHSCOPE_KEY) {
    try {
      const model = options.model && !options.model.includes('/') ? options.model : 'qwen-plus';
      const res = await fetch(`${DASHSCOPE_BASE}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${DASHSCOPE_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ model, messages, max_tokens: maxTokens }),
        signal: AbortSignal.timeout(timeoutMs),
      });
      if (res.ok) {
        const data = await res.json();
        const content = data?.choices?.[0]?.message?.content ?? '';
        if (content) return { content, provider: 'alibaba-dashscope', model };
      }
    } catch {
      // fall through to OpenRouter
    }
  }

  // Fallback: OpenRouter free models
  if (OPENROUTER_KEY) {
    const orModel = options.model ?? 'google/gemma-4-26b-a4b-it:free';
    const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENROUTER_KEY}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://egos.ia.br',
      },
      body: JSON.stringify({ model: orModel, messages, max_tokens: maxTokens }),
      signal: AbortSignal.timeout(timeoutMs),
    });
    if (res.ok) {
      const data = await res.json();
      const content = data?.choices?.[0]?.message?.content ?? '';
      if (content) return { content, provider: 'openrouter', model: orModel };
    }
  }

  throw new Error('Hermes: no LLM provider available (DashScope + OpenRouter both failed)');
}

/**
 * Simple text generation — convenience wrapper for single-prompt use cases.
 */
export async function generateText(prompt: string, systemPrompt?: string): Promise<string> {
  const result = await callHermes(prompt, { systemPrompt });
  return result.content;
}
