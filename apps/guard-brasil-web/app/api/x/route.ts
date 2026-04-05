import { NextRequest, NextResponse } from 'next/server';

const X_BEARER = process.env.X_BEARER_TOKEN ?? '';
const X_API_KEY = process.env.X_API_KEY ?? '';
const X_API_SECRET = process.env.X_API_SECRET ?? '';
const X_ACCESS_TOKEN = process.env.X_ACCESS_TOKEN ?? '';
const X_ACCESS_SECRET = process.env.X_ACCESS_TOKEN_SECRET ?? '';
const DASHBOARD_SECRET = process.env.X_DASHBOARD_SECRET ?? 'egos-x-2026';

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

// Simple auth check
function isAuthed(req: NextRequest): boolean {
  const auth = req.headers.get('authorization')?.replace('Bearer ', '') ?? '';
  const query = req.nextUrl.searchParams.get('key') ?? '';
  return auth === DASHBOARD_SECRET || query === DASHBOARD_SECRET;
}

// OAuth 1.0a signing for X API v2 POST
async function oauthSign(method: string, url: string, body?: string): Promise<Record<string, string>> {
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

  // Create signature base string
  const sortedParams = Object.keys(params).sort().map(k => `${encodeURIComponent(k)}=${encodeURIComponent(params[k])}`).join('&');
  const baseString = `${method}&${encodeURIComponent(url)}&${encodeURIComponent(sortedParams)}`;
  const signingKey = `${encodeURIComponent(X_API_SECRET)}&${encodeURIComponent(X_ACCESS_SECRET)}`;

  // HMAC-SHA1
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey('raw', encoder.encode(signingKey), { name: 'HMAC', hash: 'SHA-1' }, false, ['sign']);
  const sig = await crypto.subtle.sign('HMAC', key, encoder.encode(baseString));
  const signature = btoa(String.fromCharCode(...new Uint8Array(sig)));

  params.oauth_signature = signature;

  const authHeader = 'OAuth ' + Object.keys(params).sort().map(k => `${encodeURIComponent(k)}="${encodeURIComponent(params[k])}"`).join(', ');

  return { Authorization: authHeader, 'Content-Type': 'application/json' };
}

export async function OPTIONS() {
  return new Response(null, { status: 204, headers: CORS });
}

export async function GET(req: NextRequest) {
  if (!isAuthed(req)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401, headers: CORS });
  }

  const action = req.nextUrl.searchParams.get('action') ?? 'search';

  // Search tweets
  if (action === 'search') {
    const query = req.nextUrl.searchParams.get('q') ?? 'LGPD API -is:retweet lang:pt';
    const max = req.nextUrl.searchParams.get('max') ?? '20';

    if (!X_BEARER) {
      return NextResponse.json({ error: 'X_BEARER_TOKEN not configured' }, { status: 500, headers: CORS });
    }

    const url = `https://api.twitter.com/2/tweets/search/recent?query=${encodeURIComponent(query)}&max_results=${max}&tweet.fields=created_at,public_metrics,author_id,conversation_id&expansions=author_id&user.fields=name,username,profile_image_url,public_metrics`;

    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${X_BEARER}` },
    });

    if (!res.ok) {
      const err = await res.text();
      return NextResponse.json({ error: `X API error: ${res.status}`, detail: err }, { status: res.status, headers: CORS });
    }

    const data = await res.json();

    // Merge user info into tweets
    const users = new Map<string, any>();
    for (const u of data.includes?.users ?? []) {
      users.set(u.id, u);
    }

    const tweets = (data.data ?? []).map((t: any) => ({
      id: t.id,
      text: t.text,
      created_at: t.created_at,
      author: users.get(t.author_id) ?? { name: 'Unknown', username: 'unknown' },
      metrics: t.public_metrics,
      conversation_id: t.conversation_id,
      url: `https://x.com/${users.get(t.author_id)?.username ?? 'i'}/status/${t.id}`,
    }));

    return NextResponse.json({
      tweets,
      count: tweets.length,
      query,
      rate_limit: {
        remaining: res.headers.get('x-rate-limit-remaining'),
        reset: res.headers.get('x-rate-limit-reset'),
      },
    }, { headers: CORS });
  }

  // Get mentions / notifications
  if (action === 'mentions') {
    const userId = req.nextUrl.searchParams.get('user_id') ?? process.env.X_USER_ID ?? '';
    if (!userId) {
      return NextResponse.json({ error: 'X_USER_ID not set' }, { status: 400, headers: CORS });
    }

    const url = `https://api.twitter.com/2/users/${userId}/mentions?max_results=20&tweet.fields=created_at,public_metrics,author_id,conversation_id&expansions=author_id&user.fields=name,username,profile_image_url`;

    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${X_BEARER}` },
    });

    if (!res.ok) {
      const err = await res.text();
      return NextResponse.json({ error: `X API error: ${res.status}`, detail: err }, { status: res.status, headers: CORS });
    }

    return NextResponse.json(await res.json(), { headers: CORS });
  }

  // Suggested queries for LGPD market
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
        { q: 'DPO Brasil vaga -is:retweet lang:pt', label: 'Vagas DPO Brasil' },
        { q: '#LGPD OR #ProteçãoDeDados -is:retweet lang:pt', label: 'Hashtags LGPD' },
        { q: '"Guard Brasil" OR "guard-brasil" OR @egosbr', label: 'Menções Guard Brasil' },
      ],
    }, { headers: CORS });
  }

  return NextResponse.json({ error: 'Unknown action' }, { status: 400, headers: CORS });
}

export async function POST(req: NextRequest) {
  if (!isAuthed(req)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401, headers: CORS });
  }

  const body = await req.json();
  const action = body.action ?? 'reply';

  // Post a reply
  if (action === 'reply') {
    const { tweet_id, text } = body;
    if (!tweet_id || !text) {
      return NextResponse.json({ error: 'Missing tweet_id or text' }, { status: 400, headers: CORS });
    }

    if (text.length > 280) {
      return NextResponse.json({ error: `Tweet too long: ${text.length}/280` }, { status: 400, headers: CORS });
    }

    const url = 'https://api.twitter.com/2/tweets';
    const payload = JSON.stringify({
      text,
      reply: { in_reply_to_tweet_id: tweet_id },
    });

    try {
      const headers = await oauthSign('POST', url, payload);
      const res = await fetch(url, { method: 'POST', headers, body: payload });

      if (!res.ok) {
        const err = await res.text();
        return NextResponse.json({ error: `X API error: ${res.status}`, detail: err }, { status: res.status, headers: CORS });
      }

      const data = await res.json();
      return NextResponse.json({
        success: true,
        tweet_id: data.data?.id,
        tweet_url: `https://x.com/anoineim/status/${data.data?.id}`,
      }, { headers: CORS });
    } catch (err) {
      return NextResponse.json({ error: `Post failed: ${String(err)}` }, { status: 500, headers: CORS });
    }
  }

  // Post a new tweet (not a reply)
  if (action === 'post') {
    const { text } = body;
    if (!text) {
      return NextResponse.json({ error: 'Missing text' }, { status: 400, headers: CORS });
    }

    const url = 'https://api.twitter.com/2/tweets';
    const payload = JSON.stringify({ text });

    try {
      const headers = await oauthSign('POST', url, payload);
      const res = await fetch(url, { method: 'POST', headers, body: payload });

      if (!res.ok) {
        const err = await res.text();
        return NextResponse.json({ error: `X API error: ${res.status}`, detail: err }, { status: res.status, headers: CORS });
      }

      const data = await res.json();
      return NextResponse.json({
        success: true,
        tweet_id: data.data?.id,
        tweet_url: `https://x.com/anoineim/status/${data.data?.id}`,
      }, { headers: CORS });
    } catch (err) {
      return NextResponse.json({ error: `Post failed: ${String(err)}` }, { status: 500, headers: CORS });
    }
  }

  // Generate AI reply suggestion
  if (action === 'suggest') {
    const { tweet_text, context } = body;
    if (!tweet_text) {
      return NextResponse.json({ error: 'Missing tweet_text' }, { status: 400, headers: CORS });
    }

    // Generate reply suggestion using simple template (no LLM dependency)
    const suggestions = generateSuggestions(tweet_text, context ?? '');
    return NextResponse.json({ suggestions }, { headers: CORS });
  }

  return NextResponse.json({ error: 'Unknown action' }, { status: 400, headers: CORS });
}

function generateSuggestions(tweetText: string, context: string): string[] {
  const lower = tweetText.toLowerCase();
  const suggestions: string[] = [];

  if (lower.includes('lgpd') || lower.includes('dados pessoais') || lower.includes('cpf')) {
    suggestions.push(
      `Construí uma ferramenta open-source que detecta e mascara 15 tipos de PII brasileiro (CPF, CNPJ, RG, etc.) em tempo real. Ainda em desenvolvimento, mas já funciona: guard.egos.ia.br — feedback é bem-vindo!`,
    );
    suggestions.push(
      `Tenho trabalhado nisso — @egosbr/guard-brasil no npm. Detecta CPF, CNPJ, RG, placa, processo judicial e mais. Open source, MIT. guard.egos.ia.br`,
    );
  }

  if (lower.includes('anpd') || lower.includes('multa') || lower.includes('fiscalização')) {
    suggestions.push(
      `Com as 40 ações de fiscalização da ANPD planejadas para 2026-2027, compliance automático vai ser essencial. Estou construindo uma API que gera receipts SHA-256 por inspeção — prova auditável de mascaramento. guard.egos.ia.br`,
    );
  }

  if (lower.includes('openai') || lower.includes('chatgpt') || lower.includes('llm') || lower.includes('claude')) {
    suggestions.push(
      `Antes de mandar dados brasileiros pra qualquer LLM, vale mascarar CPF/CNPJ automaticamente. Construí isso: npm install @egosbr/guard-brasil — 3 linhas de código. Ainda em beta, feedback é ouro.`,
    );
  }

  if (lower.includes('dev') || lower.includes('programação') || lower.includes('código') || lower.includes('npm')) {
    suggestions.push(
      `Show! Se precisar de detecção de PII brasileiro no seu projeto: npm install @egosbr/guard-brasil — detecta CPF, CNPJ, RG, placa e mais. Open source, MIT license.`,
    );
  }

  // Generic fallback
  if (suggestions.length === 0) {
    suggestions.push(
      `Interessante! Tenho trabalhado em ferramentas de compliance LGPD para devs. Se for relevante: guard.egos.ia.br — feedback sempre bem-vindo.`,
    );
  }

  return suggestions;
}
