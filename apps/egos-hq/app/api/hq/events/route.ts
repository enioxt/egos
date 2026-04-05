import { NextRequest, NextResponse } from 'next/server';
import { createServerClient } from '@/lib/supabase';

export async function GET(req: NextRequest) {
  const sb = createServerClient();
  const limit = parseInt(req.nextUrl.searchParams.get('limit') ?? '50');
  const severity = req.nextUrl.searchParams.get('severity');

  let query = sb.from('egos_agent_events')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(limit);

  if (severity && severity !== 'all') {
    query = query.eq('severity', severity);
  }

  const { data, error } = await query;
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  return NextResponse.json({ events: (data ?? []).reverse(), count: data?.length ?? 0 });
}
