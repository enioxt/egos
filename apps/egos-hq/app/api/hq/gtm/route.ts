import { NextResponse } from 'next/server';
import { createServerClient } from '@/lib/supabase';

export async function GET() {
  const sb = createServerClient();
  const now = new Date();
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate()).toISOString();
  const weekStart = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString();

  // Fetch real GTM data from database
  const [
    tenantsRes,
    eventsRes,
    outreachRes,
    mrrRes,
  ] = await Promise.all([
    // Active customers
    sb.from('guard_brasil_tenants')
      .select('*')
      .eq('status', 'active'),
    
    // Recent events for activity check
    sb.from('egos_agent_events')
      .select('created_at, source')
      .gte('created_at', weekStart)
      .order('created_at', { ascending: false }),
    
    // M-007 outreach tracking (from x_reply_runs as proxy)
    sb.from('x_reply_runs')
      .select('created_at, status')
      .gte('created_at', weekStart),
    
    // MRR calculation
    sb.from('guard_brasil_tenants')
      .select('mrr_brl, status')
      .eq('status', 'active'),
  ]);

  const customers = tenantsRes.data ?? [];
  const events = eventsRes.data ?? [];
  const outreach = outreachRes.data ?? [];
  
  const mrr = customers.reduce((sum, t) => sum + (t.mrr_brl ?? 0), 0);
  
  // Check M-007 staleness
  const lastOutreach = outreach.length > 0 
    ? new Date(outreach[0].created_at)
    : null;
  const daysSinceOutreach = lastOutreach 
    ? Math.floor((now.getTime() - lastOutreach.getTime()) / (1000 * 60 * 60 * 24))
    : 999;
  
  // Activity indicators
  const hasRecentActivity = events.length > 0;
  const lastActivity = events.length > 0 
    ? events[0].created_at 
    : null;

  return NextResponse.json({
    revenue: {
      mrr_brl: mrr,
      formatted: `R$ ${mrr.toFixed(0)} MRR`,
    },
    customers: {
      count: customers.length,
      active: customers.filter(c => c.status === 'active').length,
    },
    outreach: {
      last_sent_days_ago: daysSinceOutreach,
      total_this_week: outreach.length,
      stale: daysSinceOutreach > 7,
    },
    activity: {
      has_recent: hasRecentActivity,
      last_event_at: lastActivity,
      events_this_week: events.length,
    },
    timestamp: now.toISOString(),
  });
}
