import { NextResponse } from 'next/server';
import { createServerClient } from '@/lib/supabase';

const TIMEOUT = 4000;
const BILLING_PROXY_URL = process.env.BILLING_PROXY_URL ?? 'http://127.0.0.1:18801';

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
  const [guardHealth, gatewayHealth, openclawHealth, billingProxyHealth, guardStats, xStats, agentEvents, kbStats, kbLearnings] = await Promise.all([
    ping('https://guard.egos.ia.br/health', 'Guard Brasil API'),
    ping('https://gateway.egos.ia.br/health', 'EGOS Gateway'),
    ping('https://openclaw.egos.ia.br', 'OpenClaw Gateway'),
    ping(`${BILLING_PROXY_URL}/health`, 'Billing Proxy'),

    // Guard Brasil today's stats
    sb.from('guard_brasil_events')
      .select('cost_usd, verdict', { count: 'exact' })
      .gte('created_at', todayStart),

    // X reply stats
    sb.from('x_reply_runs')
      .select('status', { count: 'exact' })
      .gte('created_at', todayStart),

    // Last 5 agent events
    sb.from('egos_agent_events')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(5),

    // Knowledge Base stats (KB-009)
    sb.from('egos_wiki_pages')
      .select('quality_score', { count: 'exact' }),

    // Learnings count
    sb.from('egos_learnings')
      .select('id', { count: 'exact' }),
  ]);

  // Calculate Guard Brasil MRR from tenants
  const tenantsRes = await sb.from('guard_brasil_tenants').select('mrr_brl, status').eq('status', 'active');
  const mrr = (tenantsRes.data ?? []).reduce((s: number, t: { mrr_brl?: number }) => s + (t.mrr_brl ?? 0), 0);

  // X reply counts by status
  const xByStatus = ((xStats.data ?? []) as { status: string }[]).reduce<Record<string, number>>((acc, r) => {
    acc[r.status] = (acc[r.status] ?? 0) + 1;
    return acc;
  }, {});

  // Guard Brasil call counts and revenue today
  const guardData = guardStats.data ?? [];
  const callsToday = guardStats.count ?? 0;
  const revenueToday = guardData.reduce((s: number, e: { cost_usd?: number }) => s + (e.cost_usd ?? 0), 0);

  // Knowledge Base stats
  const kbPages = kbStats.data ?? [];
  const kbPageCount = kbStats.count ?? 0;
  const kbAvgQuality = kbPageCount > 0
    ? Math.round(kbPages.reduce((s: number, p: { quality_score?: number }) => s + (p.quality_score ?? 0), 0) / kbPageCount)
    : 0;

  return NextResponse.json({
    timestamp: now.toISOString(),
    services: {
      guard_brasil: { ...guardHealth, calls_today: callsToday, revenue_today_usd: revenueToday, mrr_brl: mrr },
      gateway: gatewayHealth,
      openclaw: {
        ...openclawHealth,
        default_model: 'claude-haiku-4-5-20251001',
        fallback_chain: ['openrouter/qwen3-235b:free', 'dashscope/qwen-turbo'],
      },
      billing_proxy: {
        ...billingProxyHealth,
        requests_served: (billingProxyHealth.data as { requestsServed?: number })?.requestsServed ?? null,
        token_expires_in_hours: (billingProxyHealth.data as { tokenExpiresInHours?: number })?.tokenExpiresInHours ?? null,
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
