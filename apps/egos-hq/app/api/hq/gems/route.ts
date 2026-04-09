import { NextResponse } from 'next/server';

// HQV2-003 — proxy to gem-hunter API via gateway
export async function GET() {
  try {
    const gatewayBase = process.env.GATEWAY_INTERNAL_URL ?? 'http://egos-gateway:3050';
    const res = await fetch(`${gatewayBase}/gem-hunter/product`, {
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) throw new Error(`gateway ${res.status}`);
    const data = await res.json();
    return NextResponse.json(data);
  } catch (err) {
    return NextResponse.json({ error: (err as Error).message, gems: [], total: 0 }, { status: 503 });
  }
}
