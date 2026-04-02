import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

function getSupabase() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) return null;
  return createClient(url, key);
}

export async function GET() {
  const sb = getSupabase();
  if (!sb) return NextResponse.json({ error: 'Supabase not configured' }, { status: 503 });

  const [eventsRes, tenantsRes] = await Promise.all([
    sb.from('guard_brasil_events').select('cost_usd, duration_ms, verdict, pii_types, created_at'),
    sb.from('guard_brasil_tenants').select('calls_this_month, mrr_brl, tier').eq('status', 'active'),
  ]);

  const events = eventsRes.data ?? [];
  const tenants = tenantsRes.data ?? [];

  const totalCost = events.reduce((s: number, e: any) => s + parseFloat(e.cost_usd ?? 0), 0);
  const avgLatency = events.length
    ? Math.round(events.reduce((s: number, e: any) => s + (e.duration_ms ?? 0), 0) / events.length)
    : 0;
  const blocked = events.filter((e: any) => e.verdict === 'blocked').length;
  const totalMrr = tenants.reduce((s: number, t: any) => s + parseFloat(t.mrr_brl ?? 0), 0);
  const totalCallsMonth = tenants.reduce((s: number, t: any) => s + (t.calls_this_month ?? 0), 0);
  const piiBreakdown: Record<string, number> = {};
  events.forEach((e: any) => {
    (e.pii_types ?? []).forEach((p: string) => { piiBreakdown[p] = (piiBreakdown[p] ?? 0) + 1; });
  });

  const tierCounts: Record<string, number> = {};
  tenants.forEach((t: any) => { tierCounts[t.tier] = (tierCounts[t.tier] ?? 0) + 1; });

  return NextResponse.json({
    total_events: events.length,
    total_cost_usd: totalCost,
    avg_latency_ms: avgLatency,
    blocked_count: blocked,
    block_rate: events.length ? Math.round((blocked / events.length) * 100) : 0,
    total_mrr_brl: totalMrr,
    total_calls_this_month: totalCallsMonth,
    active_customers: tenants.length,
    tier_breakdown: tierCounts,
    pii_breakdown: piiBreakdown,
    updated_at: new Date().toISOString(),
  });
}
