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
  if (!sb) return NextResponse.json({ tenants: [], error: 'Supabase not configured' }, { status: 503 });

  const { data, error } = await sb
    .from('guard_brasil_tenants')
    .select('id, name, email, tier, calls_this_month, quota_limit, mrr_brl, status, created_at')
    .eq('status', 'active')
    .order('created_at', { ascending: false })
    .limit(100);

  if (error) return NextResponse.json({ tenants: [], error: error.message }, { status: 500 });

  const tenants = (data || []).map((t: any) => ({
    id: t.id,
    name: t.name,
    email: t.email,
    tier: t.tier,
    calls_this_month: t.calls_this_month ?? 0,
    quota_limit: t.quota_limit ?? 150,
    mrr: parseFloat(t.mrr_brl ?? 0),
    created_at: t.created_at,
  }));

  return NextResponse.json({ tenants, total: tenants.length });
}
