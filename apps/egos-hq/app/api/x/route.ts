import { NextRequest, NextResponse } from 'next/server';
import { createServerClient } from '@/lib/supabase';

const X_BEARER = process.env.X_BEARER_TOKEN ?? '';
const X_API_KEY = process.env.X_API_KEY ?? '';
const X_API_SECRET = process.env.X_API_SECRET ?? '';
const X_ACCESS_TOKEN = process.env.X_ACCESS_TOKEN ?? '';
const X_ACCESS_SECRET = process.env.X_ACCESS_TOKEN_SECRET ?? '';

// OAuth 1.0a signing for X API v2 POST
async function oauthSign(method: string, url: string): Promise<Record<string, string>> {
  const timestamp = Math.floor(Date.now() / 1000).toString();
  const nonce = crypto.randomUUID().replace(/-/g, '');

  const params: Record<string, string> = {
    oauth_consumer_key: X_API_KEY,
    oauth_nonce: nonce,
    oauth_signature_method: 'HMAC-SHA1',
    oauth_timestamp: timestamp,
    oauth_token: X_ACCESS_TOKEN,
    oauth_version: '1.0',
  };

  const sortedParams = Object.keys(params).sort()
    .map(k => `${encodeURIComponent(k)}=${encodeURIComponent(params[k])}`)
    .join('&');
  const baseString = `${method}&${encodeURIComponent(url)}&${encodeURIComponent(sortedParams)}`;
  const signingKey = `${encodeURIComponent(X_API_SECRET)}&${encodeURIComponent(X_ACCESS_SECRET)}`;

  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey('raw', encoder.encode(signingKey), { name: 'HMAC', hash: 'SHA-1' }, false, ['sign']);
  const sig = await crypto.subtle.sign('HMAC', key, encoder.encode(baseString));
  const signature = btoa(String.fromCharCode(...new Uint8Array(sig)));

  params.oauth_signature = signature;
  const authHeader = 'OAuth ' + Object.keys(params).sort()
    .map(k => `${encodeURIComponent(k)}="${encodeURIComponent(params[k])}"`)
    .join(', ');

  return { Authorization: authHeader, 'Content-Type': 'application/json' };
}

export async function GET(req: NextRequest) {
  const action = req.nextUrl.searchParams.get('action') ?? 'search';

  if (action === 'queue') {
    const sb = createServerClient();
    const status = req.nextUrl.searchParams.get('status') ?? 'pending';
    const limit = parseInt(req.nextUrl.searchParams.get('limit') ?? '20');

    const { data, error } = status === 'all'
      ? await sb.from('x_reply_runs').select('*').order('run_at', { ascending: false }).limit(limit)
      : await sb.from('x_reply_runs').select('*').eq('status', status).order('run_at', { ascending: false }).limit(limit);

    if (error) return NextResponse.json({ error: error.message }, { status: 500 });
    return NextResponse.json({ runs: data, count: data?.length ?? 0 });
  }

  if (action === 'search') {
    const query = req.nextUrl.searchParams.get('q') ?? 'LGPD API -is:retweet lang:pt';
    const max = req.nextUrl.searchParams.get('max') ?? '20';

    if (!X_BEARER) return NextResponse.json({ error: 'X_BEARER_TOKEN not configured' }, { status: 500 });

    const url = `https://api.twitter.com/2/tweets/search/recent?query=${encodeURIComponent(query)}&max_results=${max}&tweet.fields=created_at,public_metrics,author_id&expansions=author_id&user.fields=name,username,profile_image_url,public_metrics`;

    const res = await fetch(url, { headers: { Authorization: `Bearer ${X_BEARER}` } });
    if (!res.ok) {
      const err = await res.text();
      return NextResponse.json({ error: `X API error: ${res.status}`, detail: err }, { status: res.status });
    }

    const data = await res.json();
    const users = new Map<string, Record<string, unknown>>();
    for (const u of (data.includes?.users ?? [])) users.set(u.id, u);

    const tweets = (data.data ?? []).map((t: Record<string, unknown>) => ({
      id: t.id,
      text: t.text,
      created_at: t.created_at,
      author: users.get(t.author_id as string) ?? { name: 'Unknown', username: 'unknown' },
      metrics: t.public_metrics,
      url: `https://x.com/${(users.get(t.author_id as string) as Record<string, unknown>)?.username ?? 'i'}/status/${t.id}`,
    }));

    return NextResponse.json({ tweets, count: tweets.length, query });
  }

  if (action === 'suggestions') {
    return NextResponse.json({
      queries: [
        { q: 'LGPD API -is:retweet lang:pt', label: 'LGPD + API (PT-BR)' },
        { q: 'mascaramento CPF dados -is:retweet lang:pt', label: 'Mascaramento CPF' },
        { q: '"proteção de dados" startup Brasil -is:retweet', label: 'Proteção dados startup BR' },
        { q: 'ANPD multa fiscalização -is:retweet lang:pt', label: 'ANPD multas' },
        { q: 'LGPD compliance software -is:retweet', label: 'LGPD compliance software' },
        { q: 'CPF CNPJ API developer -is:retweet', label: 'CPF/CNPJ API dev' },
        { q: '"inteligência artificial" LGPD dados pessoais -is:retweet lang:pt', label: 'IA + LGPD' },
        { q: 'multi-agent framework -is:retweet lang:en', label: 'Multi-agent frameworks (EN)' },
        { q: '#LGPD OR #ProteçãoDeDados -is:retweet lang:pt', label: '#LGPD hashtags' },
        { q: '"Guard Brasil" OR "guard-brasil" OR @egosbr', label: 'Menções Guard Brasil' },
      ],
    });
  }

  return NextResponse.json({ error: 'Unknown action' }, { status: 400 });
}

export async function POST(req: NextRequest) {
  const body = await req.json();
  const action = body.action ?? 'reply';
  const sb = createServerClient();

  if (action === 'approve') {
    const { run_id, text } = body;
    if (!run_id || !text) return NextResponse.json({ error: 'Missing run_id or text' }, { status: 400 });

    // Get the run
    const { data: run } = await sb.from('x_reply_runs').select('*').eq('id', run_id).single();
    if (!run) return NextResponse.json({ error: 'Run not found' }, { status: 404 });

    const url = 'https://api.twitter.com/2/tweets';
    const payload = JSON.stringify({ text, reply: { in_reply_to_tweet_id: run.tweet_id } });

    try {
      const headers = await oauthSign('POST', url);
      const res = await fetch(url, { method: 'POST', headers, body: payload });

      if (!res.ok) {
        const err = await res.text();
        await sb.from('x_reply_runs').update({ status: 'approved', error: `${res.status}: ${err.slice(0, 200)}` }).eq('id', run_id);
        return NextResponse.json({ error: `X API error: ${res.status}`, detail: err }, { status: res.status });
      }

      const data = await res.json();
      await sb.from('x_reply_runs').update({
        status: 'sent',
        generated_reply: text,
        sent_at: new Date().toISOString(),
      }).eq('id', run_id);

      return NextResponse.json({ success: true, tweet_id: data.data?.id });
    } catch (err) {
      return NextResponse.json({ error: `Post failed: ${String(err)}` }, { status: 500 });
    }
  }

  if (action === 'reject') {
    const { run_id } = body;
    if (!run_id) return NextResponse.json({ error: 'Missing run_id' }, { status: 400 });
    await sb.from('x_reply_runs').update({ status: 'rejected' }).eq('id', run_id);
    return NextResponse.json({ success: true });
  }

  if (action === 'reply') {
    // Direct reply (from search tab manual compose)
    const { tweet_id, text } = body;
    if (!tweet_id || !text) return NextResponse.json({ error: 'Missing tweet_id or text' }, { status: 400 });
    if (text.length > 280) return NextResponse.json({ error: `Too long: ${text.length}/280` }, { status: 400 });

    const url = 'https://api.twitter.com/2/tweets';
    const payload = JSON.stringify({ text, reply: { in_reply_to_tweet_id: tweet_id } });

    try {
      const headers = await oauthSign('POST', url);
      const res = await fetch(url, { method: 'POST', headers, body: payload });
      if (!res.ok) {
        const err = await res.text();
        return NextResponse.json({ error: `X API error: ${res.status}`, detail: err }, { status: res.status });
      }
      const data = await res.json();

      // Log to x_reply_runs as sent
      await sb.from('x_reply_runs').insert({
        topic: 'manual',
        tweet_id,
        generated_reply: text,
        status: 'sent',
        sent_at: new Date().toISOString(),
      });

      return NextResponse.json({ success: true, tweet_id: data.data?.id });
    } catch (err) {
      return NextResponse.json({ error: `Post failed: ${String(err)}` }, { status: 500 });
    }
  }

  if (action === 'suggest') {
    const { tweet_text } = body;
    if (!tweet_text) return NextResponse.json({ error: 'Missing tweet_text' }, { status: 400 });

    const lower = (tweet_text as string).toLowerCase();
    const suggestions: string[] = [];

    if (lower.includes('lgpd') || lower.includes('cpf') || lower.includes('dados pessoais')) {
      suggestions.push(`Construí uma API open-source que detecta e mascara 15 tipos de PII brasileiro (CPF, CNPJ, RG, etc.) em tempo real, com receipt SHA-256 por inspeção — guard.egos.ia.br`);
      suggestions.push(`Trabalhando nisso há meses — @egosbr/guard-brasil detecta CPF, CNPJ, RG, placa, processo judicial e mais. Open source, MIT. guard.egos.ia.br`);
    }
    if (lower.includes('anpd') || lower.includes('multa')) {
      suggestions.push(`Com as fiscalizações da ANPD aumentando, compliance automático vira obrigação. Estou construindo uma API que gera receipts SHA-256 por inspeção como prova auditável. guard.egos.ia.br`);
    }
    if (lower.includes('llm') || lower.includes('openai') || lower.includes('claude') || lower.includes('ia')) {
      suggestions.push(`Antes de mandar dados brasileiros pra qualquer LLM, vale mascarar CPF/CNPJ automaticamente. 3 linhas de código: npm install @egosbr/guard-brasil — ainda em beta, feedback é ouro.`);
    }
    if (suggestions.length === 0) {
      suggestions.push(`Contexto relevante — tenho trabalhado em ferramentas de compliance LGPD para devs brasileiros. Se for útil: guard.egos.ia.br`);
    }

    return NextResponse.json({ suggestions });
  }

  return NextResponse.json({ error: 'Unknown action' }, { status: 400 });
}
