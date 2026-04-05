import { NextRequest, NextResponse } from 'next/server';

const GW = process.env.GATEWAY_INTERNAL_URL ?? process.env.NEXT_PUBLIC_GATEWAY_URL ?? 'https://gateway.egos.ia.br';

// Proxy POST /knowledge/learnings to the gateway
export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const res = await fetch(`${GW}/knowledge/learnings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(8000),
    });
    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}

// GET recent learnings
export async function GET() {
  try {
    const res = await fetch(`${GW}/knowledge/learnings?limit=20&order=created_at.desc`, {
      signal: AbortSignal.timeout(6000),
    });
    return NextResponse.json(await res.json(), { status: res.status });
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 500 });
  }
}
