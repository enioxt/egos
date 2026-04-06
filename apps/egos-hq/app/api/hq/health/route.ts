import { NextResponse } from 'next/server';
import { createServerClient } from '@/lib/supabase';

const TIMEOUT = 4000;
const BILLING_PROXY_URL = process.env.BILLING_PROXY_URL ?? 'http://127.0.0.1:18801';
const CODEX_PROXY_URL = process.env.CODEX_PROXY_URL ?? 'http://127.0.0.1:18802';
const GATEWAY_HEALTH_URL = process.env.GATEWAY_HEALTH_URL ?? 'https://gateway.egos.ia.br/health';
const OPENCLAW_HEALTH_URL = process.env.OPENCLAW_HEALTH_URL ?? 'https://openclaw.egos.ia.br';

async function ping(url: string, label: string) {
  try {
    const start = Date.now();
    const res = await fetch(url, { signal: AbortSignal.timeout(TIMEOUT) });
    const latency = Date.now() - start;
    const data = res.ok ? await res.json().catch(() => ({})) : {};
    return { label, url, ok: res.ok, latency, status: res.status, data };
  } catch {
    return { label, url, ok: false, latency: null, status: 0, data: {} };
  }
}

export async function GET() {
  const sb = createServerClient();
  const now = new Date();
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).toISOString();

  // Run all checks in parallel
  const [
    guardHealth, gatewayHealth, openclawHealth, billingProxyHealth, codexProxyHealth,
    guardStats, xStats, agentEvents, kbStats, kbLearnings, lastReview,
  ] = await Promise.all([
    ping('https://guard.egos.ia.br/health', 'Guard Brasil API'),
    ping(GATEWAY_HEALTH_URL, 'EGOS Gateway'),
    ping(OPENCLAW_HEALTH_URL, 'OpenClaw Gateway'),
    ping(`${BILLING_PROXY_URL}/health`, 'Billing Proxy (Claude)'),
    ping(`${CODEX_PROXY_URL}/health`, 'Codex Proxy (GPT-5.4)'),

    sb.from('guard_brasil_events')
      .select('cost_usd, verdict', { count: 'exact' })
      .gte('created_at', todayStart),

    sb.from('x_reply_runs')
      .select('status', { count: 'exact' })
      .gte('created_at', todayStart),

    sb.from('egos_agent_events')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(10),

    sb.from('egos_wiki_pages')
      .select('quality_score', { count: 'exact' }),

    sb.from('egos_learnings')
      .select('id', { count: 'exact' }),

    // Last constitutional review by Codex
    sb.from('egos_agent_events')
      .select('*')
      .eq('agent', 'codex-constitutional-reviewer')
      .order('created_at', { ascending: false })
      .limit(1),
  ]);

  const tenantsRes = await sb.from('guard_brasil_tenants').select('mrr_brl, status').eq('status', 'active');
  const mrr = (tenantsRes.data ?? []).reduce((s: number, t: { mrr_brl?: number }) => s + (t.mrr_brl ?? 0), 0);

  const xByStatus = ((xStats.data ?? []) as { status: string }[]).reduce<Record<string, number>>((acc, r) => {
    acc[r.status] = (acc[r.status] ?? 0) + 1;
    return acc;
  }, {});

  const guardData = guardStats.data ?? [];
  const callsToday = guardStats.count ?? 0;
  const revenueToday = guardData.reduce((s: number, e: { cost_usd?: number }) => s + (e.cost_usd ?? 0), 0);

  const kbPages = kbStats.data ?? [];
  const kbPageCount = kbStats.count ?? 0;
  const kbAvgQuality = kbPageCount > 0
    ? Math.round(kbPages.reduce((s: number, p: { quality_score?: number }) => s + (p.quality_score ?? 0), 0) / kbPageCount)
    : 0;

  // Codex quota from proxy health response
  type CodexProxyData = {
    quota?: {
      requests_in_window: number;
      requests_window_max: number;
      usage_pct: number;
      status: string;
      window_resets_in_minutes: number;
      requests_total: number;
      last_request_at: string | null;
      rate_limited_count: number;
    };
  };
  const codexData = codexProxyHealth.data as CodexProxyData;

  return NextResponse.json({
    timestamp: now.toISOString(),
    services: {
      guard_brasil: {
        ...guardHealth,
        calls_today: callsToday,
        revenue_today_usd: revenueToday,
        mrr_brl: mrr,
      },
      gateway: {
        ...gatewayHealth,
        channels: (gatewayHealth.data as { channels?: string[] })?.channels ?? [],
        uptime_seconds: (gatewayHealth.data as { uptime?: number })?.uptime ?? null,
      },
      openclaw: {
        ...openclawHealth,
        default_model: 'claude-haiku-4-5-20251001',
        fallback_chain: ['openrouter/qwen3-235b:free', 'dashscope/qwen-turbo', 'codex/gpt-5.4'],
      },
      billing_proxy: {
        ...billingProxyHealth,
        requests_served: (billingProxyHealth.data as { requestsServed?: number })?.requestsServed ?? null,
        token_expires_in_hours: (billingProxyHealth.data as { tokenExpiresInHours?: number })?.tokenExpiresInHours ?? null,
      },
      codex_proxy: {
        ...codexProxyHealth,
        model: 'gpt-5.4',
        quota: codexData?.quota ?? null,
        last_review: (lastReview.data ?? [])[0] ?? null,
      },
    },
    x_bot: {
      pending: xByStatus['pending'] ?? 0,
      sent_today: xByStatus['sent'] ?? 0,
      rejected_today: xByStatus['rejected'] ?? 0,
    },
    knowledge: {
      pages: kbPageCount,
      avg_quality: kbAvgQuality,
      learnings: kbLearnings.count ?? 0,
    },
    recent_events: agentEvents.data ?? [],
  });
}
