import { NextResponse } from 'next/server';

// Triggers a constitutional review job via the Codex proxy
// POST /api/hq/actions/codex-review

const CODEX_PROXY_URL = process.env.CODEX_PROXY_URL ?? 'http://127.0.0.1:18802';

export async function POST() {
  try {
    // Check quota first
    const usageRes = await fetch(`${CODEX_PROXY_URL}/v1/usage`, { signal: AbortSignal.timeout(3000) });
    const usage = usageRes.ok ? await usageRes.json().catch(() => ({})) : {};

    if ((usage as { status?: string }).status === 'exhausted') {
      const mins = (usage as { window_resets_in_minutes?: number }).window_resets_in_minutes ?? '?';
      return NextResponse.json({
        ok: false,
        message: `Codex quota exhausted. Resets in ${mins} minutes.`,
        quota: usage,
      }, { status: 429 });
    }

    // Trigger a quick review via Codex proxy
    const reviewPrompt = `You are the EGOS Constitutional Reviewer. Run a quick health check:
1. Check if TASKS.md line count is healthy (target: <500 lines)
2. Check if recent commits follow conventional commit format
3. Verify 90-day focus is maintained (Guard Brasil + Gem Hunter only)
4. Output: one-line status per check + overall score (0-100)
5. Sign with: REVIEWED_BY: Codex-HQ-trigger / ${new Date().toISOString()}`;

    const reviewRes = await fetch(`${CODEX_PROXY_URL}/v1/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'gpt-5.4',
        messages: [{ role: 'user', content: reviewPrompt }],
      }),
      signal: AbortSignal.timeout(90000),
    });

    if (!reviewRes.ok) {
      const err = await reviewRes.json().catch(() => ({}));
      return NextResponse.json({ ok: false, message: 'Codex review failed', error: err }, { status: reviewRes.status });
    }

    const result = await reviewRes.json();
    const content = result?.choices?.[0]?.message?.content ?? '';

    return NextResponse.json({
      ok: true,
      review: content,
      quota: result?.codex_quota ?? null,
      triggered_at: new Date().toISOString(),
    });
  } catch (err) {
    return NextResponse.json({
      ok: false,
      message: `Error: ${err instanceof Error ? err.message : 'Unknown error'}`,
    }, { status: 500 });
  }
}
