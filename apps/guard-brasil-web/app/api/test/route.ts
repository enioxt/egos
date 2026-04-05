import { NextResponse } from 'next/server';
import { GuardBrasil } from '@egosbr/guard-brasil';

const guard = GuardBrasil.create();

export async function POST(req: Request) {
  let body: { text?: string; checkout?: boolean; tier?: string; email?: string };

  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: 'Invalid JSON body.' }, { status: 400 });
  }

  // Handle Stripe checkout requests
  if (body.checkout && body.tier && body.email) {
    try {
      const res = await fetch('https://guard.egos.ia.br/v1/stripe/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tier: body.tier, email: body.email }),
      });
      const data = await res.json();
      return NextResponse.json(data);
    } catch {
      return NextResponse.json({ error: 'Falha ao criar checkout' }, { status: 500 });
    }
  }

  if (!body.text || typeof body.text !== 'string') {
    return NextResponse.json({ error: 'Missing required field: text' }, { status: 400 });
  }

  const start = Date.now();
  const result = guard.inspect(body.text);
  const durationMs = Date.now() - start;
  const piiFound = Array.from(new Set(result.masking.findings.map((finding: { category: string }) => finding.category)));

  return NextResponse.json({
    safe: result.safe,
    blocked: result.blocked,
    output: result.output,
    atrian: {
      score: result.atrian.score,
      reasoning: result.summary,
    },
    pii_found: piiFound,
    cost_usd: 0,
    duration_ms: durationMs,
    model_used: 'guard-brasil-local',
    summary: result.summary,
    lgpdDisclosure: result.lgpdDisclosure,
  });
}
