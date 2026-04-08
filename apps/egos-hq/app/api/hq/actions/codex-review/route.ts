import { NextResponse } from 'next/server';

// Triggers a constitutional review via Alibaba DashScope (qwen-plus)
// Migrated from Codex proxy → DashScope 2026-04-08 (CDX→HRM migration)
// POST /api/hq/actions/codex-review

const DASHSCOPE_BASE_URL = process.env.ALIBABA_DASHSCOPE_BASE_URL ?? 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1';
const DASHSCOPE_API_KEY = process.env.ALIBABA_DASHSCOPE_API_KEY ?? '';
const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY ?? '';

async function callLLM(prompt: string): Promise<string> {
  // Primary: Alibaba DashScope qwen-plus
  if (DASHSCOPE_API_KEY) {
    const res = await fetch(`${DASHSCOPE_BASE_URL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${DASHSCOPE_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'qwen-plus',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 512,
      }),
      signal: AbortSignal.timeout(30000),
    });
    if (res.ok) {
      const data = await res.json();
      return data?.choices?.[0]?.message?.content ?? '';
    }
  }

  // Fallback: OpenRouter (Gemma 4 26B free)
  if (OPENROUTER_API_KEY) {
    const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENROUTER_API_KEY}`,
        'Content-Type': 'application/json',
        'HTTP-Referer': 'https://hq.egos.ia.br',
      },
      body: JSON.stringify({
        model: 'google/gemma-4-26b-a4b-it:free',
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 512,
      }),
      signal: AbortSignal.timeout(30000),
    });
    if (res.ok) {
      const data = await res.json();
      return data?.choices?.[0]?.message?.content ?? '';
    }
  }

  throw new Error('No LLM provider available');
}

export async function POST() {
  try {
    const reviewPrompt = `You are the EGOS Constitutional Reviewer. Run a quick health check:
1. Check if TASKS.md line count is healthy (target: <500 lines)
2. Check if recent commits follow conventional commit format
3. Verify 90-day focus is maintained (Guard Brasil + Gem Hunter only)
4. Output: one-line status per check + overall score (0-100)
5. Sign with: REVIEWED_BY: DashScope-HQ-trigger / ${new Date().toISOString()}`;

    const content = await callLLM(reviewPrompt);

    return NextResponse.json({
      ok: true,
      review: content,
      provider: DASHSCOPE_API_KEY ? 'alibaba-dashscope/qwen-plus' : 'openrouter/gemma-4-26b',
      triggered_at: new Date().toISOString(),
    });
  } catch (err) {
    return NextResponse.json({
      ok: false,
      message: `Error: ${err instanceof Error ? err.message : 'Unknown error'}`,
    }, { status: 500 });
  }
}
