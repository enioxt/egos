import { NextRequest, NextResponse } from 'next/server';

/**
 * GET /api/events — Fetch recent guard_brasil_events from Supabase
 * Query params: limit (default 50), since (optional timestamp)
 */

let supabase: any = null;
let supabaseInitialized = false;

function initSupabase() {
  if (supabaseInitialized) return supabase;

  try {
    const { createClient } = require('@supabase/supabase-js');
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_ROLE_KEY;

    if (!url || !key) {
      console.warn('[api/events] Supabase credentials not configured');
      supabaseInitialized = true;
      return null;
    }

    supabase = createClient(url, key);
    supabaseInitialized = true;
    return supabase;
  } catch (e) {
    console.warn('[api/events] Failed to initialize Supabase:', e);
    supabaseInitialized = true;
    return null;
  }
}

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const limit = Math.min(parseInt(searchParams.get('limit') || '50', 10), 200);
  const since = searchParams.get('since');

  const client = initSupabase();

  if (!client) {
    return NextResponse.json(
      { error: 'Supabase not configured', events: [] },
      { status: 503 }
    );
  }

  try {
    let query = client
      .from('guard_brasil_events')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(limit);

    if (since) {
      query = query.gt('created_at', since);
    }

    const { data, error } = await query;

    if (error) {
      console.error('[api/events] Supabase query error:', error);
      return NextResponse.json(
        { error: 'Failed to fetch events', events: [] },
        { status: 500 }
      );
    }

    // Transform data for frontend
    const events = (data || []).map((event: any) => ({
      id: event.id,
      event_type: event.event_type,
      timestamp: event.created_at,
      pii_types: event.pii_types || [],
      pii_count: event.pii_count || 0,
      verdict: event.verdict,
      cost_usd: event.cost_usd,
      duration_ms: event.duration_ms,
      atrian_score: event.atrian_score,
      status_code: event.status_code,
      model_id: event.model_id,
    }));

    return NextResponse.json({
      events,
      total: events.length,
      timestamp: new Date().toISOString(),
    });
  } catch (e) {
    console.error('[api/events] Error:', e);
    return NextResponse.json(
      { error: 'Internal server error', events: [] },
      { status: 500 }
    );
  }
}
