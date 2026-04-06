import { NextResponse } from 'next/server';

// Triggers the local billing proxy token refresh script via SSH to VPS or local exec
// POST /api/hq/actions/billing-refresh

export async function POST() {
  try {
    // Trigger refresh by hitting the billing proxy health (it auto-refreshes if < threshold)
    const BILLING_PROXY_URL = process.env.BILLING_PROXY_URL ?? 'http://127.0.0.1:18801';
    const res = await fetch(`${BILLING_PROXY_URL}/health`, { signal: AbortSignal.timeout(5000) });
    const data = res.ok ? await res.json().catch(() => ({})) : {};

    return NextResponse.json({
      ok: true,
      message: 'Billing proxy health checked — refresh happens automatically when token expires',
      token_expires_in_hours: (data as { tokenExpiresInHours?: number }).tokenExpiresInHours ?? null,
    });
  } catch {
    return NextResponse.json({ ok: false, message: 'Billing proxy not reachable' }, { status: 503 });
  }
}
