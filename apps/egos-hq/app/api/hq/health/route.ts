import { NextResponse } from 'next/server';
import { createServerClient } from '@/lib/supabase';

const TIMEOUT = 4000;
const BILLING_PROXY_URL = process.env.BILLING_PROXY_URL ?? 'http://127.0.0.1:18801';
const CODEX_PROXY_URL = process.env.CODEX_PROXY_URL ?? 'http://127.0.0.1:18802';
const GATEWAY_HEALTH_URL = process.env.GATEWAY_HEALTH_URL ?? 'https://gateway.egos.ia.br/health';
const GATEWAY_INTERNAL_URL = process.env.GATEWAY_INTERNAL_URL ?? 'http://egos-gateway:3050';
const OPENCLAW_HEALTH_URL = process.env.OPENCLAW_HEALTH_URL ?? 'https://openclaw.egos.ia.br';
const GUARD_META_URL = process.env.GUARD_BRASIL_URL ?? 'https://guard.egos.ia.br';
// Internal VPS services (only reachable from inside Docker network)
const EAGLE_EYE_URL = process.env.EAGLE_EYE_URL ?? 'http://eagle-eye:3001';
const APP_852_URL = process.env.APP_852_URL ?? 'http://852-app:3000';
const SINAPI_URL = process.env.SINAPI_URL ?? 'http://egos-sinapi-api:8000';
const BRACC_URL = process.env.BRACC_URL ?? 'http://bracc-neo4j:7474';

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

  // Run all checks in parallel — core + extended services
  const [
    guardHealth, gatewayHealth, openclawHealth, billingProxyHealth, codexProxyHealth,
    // Extended services (placeholders until HQI-001..008 fully wired)
    eagleEyeHealth, app852Health, sinapiHealth, braccHealth,
    // Gateway channel details
    waHealth, tgHealth,
    // Guard meta (pattern count)
    guardMeta,
    // Supabase queries
    guardStats, xStats, agentEvents, kbStats, kbLearnings, lastReview,
  ] = await Promise.all([
    ping('https://guard.egos.ia.br/health', 'Guard Brasil API'),
    ping(GATEWAY_HEALTH_URL, 'EGOS Gateway'),
    ping(OPENCLAW_HEALTH_URL, 'OpenClaw Gateway'),
    ping(`${BILLING_PROXY_URL}/health`, 'Billing Proxy (Claude)'),
    ping(`${CODEX_PROXY_URL}/health`, 'Codex Proxy (GPT-5.4)'),
    // Extended services — HQI-001..004
    ping(`${EAGLE_EYE_URL}/api/health`, 'Eagle Eye'),
    ping(`${APP_852_URL}/api/health`, '852 Police Bot'),
    ping(`${SINAPI_URL}/health`, 'SINAPI API'),
    ping(`${BRACC_URL}/db/data/`, 'br-acc Neo4j'),
    // Gateway channel health — HQI-005
    ping(`${GATEWAY_INTERNAL_URL}/channels/whatsapp/health`, 'WhatsApp Channel'),
    ping(`${GATEWAY_INTERNAL_URL}/telegram/health`, 'Telegram Channel'),
    // Guard meta — HQI-006
    ping(`${GUARD_META_URL}/v1/meta`, 'Guard Brasil Meta'),

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

  // Eagle Eye tables health
  type EagleEyeData = { healthy?: boolean; tables?: { territories?: boolean; opportunities?: boolean; scans?: boolean } };
  const eeData = eagleEyeHealth.data as EagleEyeData;

  // Guard meta — capabilities + version (patterns not exposed by /v1/meta, use manifest count)
  type GuardMetaData = { capabilities?: string[]; version?: string };
  const guardMetaData = guardMeta.data as GuardMetaData;

  // Billing proxy enriched data — HQI-007
  type BillingProxyData = {
    requestsServed?: unknown;
    tokenExpiresInHours?: unknown;
    subscriptionType?: string;
    uptime?: string;
    replacementPatterns?: number;
    reverseMapPatterns?: number;
    status?: string;
  };
  const bpData = billingProxyHealth.data as BillingProxyData;

  // Gateway channel details — HQI-005
  type WAData = { instance?: string; authorizedNumber?: string; orchestrator?: string; capabilities?: string[] };
  type TGData = { bot?: string; polling_active?: boolean; authorized_user?: string };
  const waData = waHealth.data as WAData;
  const tgData = tgHealth.data as TGData;

  return NextResponse.json({
    timestamp: now.toISOString(),
    services: {
      guard_brasil: {
        ...guardHealth,
        calls_today: callsToday,
        revenue_today_usd: revenueToday,
        mrr_brl: mrr,
        // HQI-006: pattern count from meta
        // 15 PII patterns verified 2026-04-07 (manifest-backed); /v1/meta doesn't expose count
        pattern_count: 15,
        capabilities_count: Array.isArray(guardMetaData?.capabilities) ? guardMetaData.capabilities.length : null,
        version: (guardMeta.data as { version?: string })?.version ?? null,
      },
      gateway: {
        ...gatewayHealth,
        channels: (gatewayHealth.data as { channels?: string[] })?.channels ?? [],
        uptime_seconds: (gatewayHealth.data as { uptime?: number })?.uptime ?? null,
        // HQI-005: channel details
        whatsapp: {
          ok: waHealth.ok,
          instance: waData?.instance ?? null,
          authorized_number: waData?.authorizedNumber ?? null,
          orchestrator: waData?.orchestrator ?? null,
          capabilities: waData?.capabilities ?? [],
        },
        telegram: {
          ok: tgHealth.ok,
          bot: tgData?.bot ?? null,
          polling_active: tgData?.polling_active ?? false,
          authorized_user: tgData?.authorized_user ?? null,
        },
      },
      openclaw: {
        ...openclawHealth,
        default_model: (openclawHealth.data as { default_model?: string })?.default_model ?? 'claude-haiku-4-5-20251001',
        fallback_chain: (openclawHealth.data as { fallback_chain?: string[] })?.fallback_chain ?? ['openrouter/qwen3-235b:free', 'dashscope/qwen-turbo', 'codex/gpt-5.4'],
      },
      billing_proxy: {
        ...billingProxyHealth,
        requests_served: bpData?.requestsServed != null ? Number(bpData.requestsServed) : null,
        token_expires_in_hours: bpData?.tokenExpiresInHours != null ? Number(bpData.tokenExpiresInHours) : null,
        // HQI-007: enriched fields
        subscription_type: bpData?.subscriptionType ?? null,
        uptime_seconds: bpData?.uptime ? parseInt(bpData.uptime) : null,
        replacement_patterns: bpData?.replacementPatterns ?? null,
        token_status: bpData?.status ?? null,
      },
      codex_proxy: {
        ...codexProxyHealth,
        model: (codexProxyHealth.data as { model?: string })?.model ?? 'gpt-5.4',
        quota: codexData?.quota ?? null,
        last_review: (lastReview.data ?? [])[0] ?? null,
      },
      // Extended services — HQI-001..004
      eagle_eye: {
        ...eagleEyeHealth,
        tables_healthy: eeData?.healthy ?? false,
        territories_table: eeData?.tables?.territories ?? false,
        opportunities_table: eeData?.tables?.opportunities ?? false,
      },
      app_852: {
        ...app852Health,
      },
      sinapi: {
        ...sinapiHealth,
        last_sync: (sinapiHealth.data as { last_sync?: string })?.last_sync ?? null,
        scheduler: (sinapiHealth.data as { scheduler?: string })?.scheduler ?? null,
      },
      bracc_neo4j: {
        ...braccHealth,
        // Node count is manifest-verified: 83,773,683 (2026-04-07)
        node_count_manifest: 83773683,
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
