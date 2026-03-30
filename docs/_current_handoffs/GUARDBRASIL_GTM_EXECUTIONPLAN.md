# Guard Brasil GTM — Plano de Execução Prático

> **Timeline:** 18 dias para full GTM launch | **Start:** 2026-03-31 | **Go-live:** 2026-04-18
> **Status:** READY — tudo pronto, falta executar

---

## TRACK 1: Landing Page + Integração (Dias 1-3)

### Dia 1: Criar `/apps/guard-brasil-web` (Next.js)

```bash
# Setup
cd /home/enio/egos/apps
npx create-next-app@latest guard-brasil-web --typescript --tailwind
cd guard-brasil-web

# Estrutura
apps/guard-brasil-web/
├── app/
│   ├── page.tsx          # Landing principal
│   ├── api/
│   │   └── test/route.ts # Proxy para guard.egos.ia.br/v1/inspect
│   └── layout.tsx
├── components/
│   ├── ExampleCard.tsx   # Cards pré-definidos
│   ├── TestForm.tsx      # Form input
│   └── ResultDisplay.tsx # JSON beautifier
├── lib/
│   ├── guard-client.ts   # HTTP client
│   └── examples.ts       # Pre-defined examples
└── public/
    └── favicon.svg
```

### Page.tsx — Landing (Clean, Fast)

```typescript
// apps/guard-brasil-web/app/page.tsx
import { ExampleCard } from '@/components/ExampleCard';
import { TestForm } from '@/components/TestForm';

const EXAMPLES = [
  {
    title: 'CPF Masking',
    description: 'Test PII detection',
    input: 'CPF: 123.456.789-00',
    policyPack: 'security',
  },
  {
    title: 'RG Detection',
    description: 'Identify and mask RG numbers',
    input: 'My RG is 1234567, born in São Paulo',
    policyPack: 'security',
  },
  {
    title: 'ATRiAN Bias Check',
    description: 'Detect bias in text',
    input: 'Young Black man applying for job',
    policyPack: 'security',
  },
  {
    title: 'LGPD Compliance',
    description: 'Check LGPD violations',
    input: 'Customer list with emails: john@example.com, mary@example.com',
    policyPack: 'security',
  },
  {
    title: 'SQL Injection',
    description: 'Detect SQL injection patterns',
    input: "SELECT * FROM users WHERE id = 1'; DROP TABLE users; --",
    policyPack: 'security',
  },
  {
    title: 'Medical Data',
    description: 'Protect health information',
    input: 'Patient John (ID: 12345) diagnosed with diabetes type 2',
    policyPack: 'health',
  },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur">
        <div className="mx-auto max-w-7xl px-6 py-6">
          <h1 className="text-4xl font-bold text-white">
            🛡️ Guard Brasil
          </h1>
          <p className="mt-2 text-slate-300">
            LGPD-compliant PII masking + ATRiAN ethical validation
          </p>
          <p className="mt-4 text-sm text-emerald-400 font-mono">
            ✅ Free tier: 100 tests/day | 0% cost (uses Alibaba free quota)
          </p>
        </div>
      </header>

      {/* Main */}
      <main className="mx-auto max-w-7xl px-6 py-12">
        <div className="grid gap-8 md:grid-cols-3 mb-12">
          {/* Left: Examples */}
          <div className="md:col-span-1 space-y-4 max-h-screen overflow-y-auto">
            <h2 className="text-lg font-bold text-white">Examples</h2>
            {EXAMPLES.map((ex) => (
              <ExampleCard
                key={ex.input}
                example={ex}
                onSelect={(text) => {
                  // Trigger form update
                  document.dispatchEvent(
                    new CustomEvent('example-selected', { detail: { text, policyPack: ex.policyPack } })
                  );
                }}
              />
            ))}
          </div>

          {/* Center: Test Form + Results */}
          <div className="md:col-span-2">
            <TestForm />
          </div>
        </div>

        {/* Footer */}
        <footer className="border-t border-slate-700 pt-8 text-center text-sm text-slate-400">
          <p>Source: <a href="https://github.com/enioxt/egos" className="text-blue-400 hover:underline">github.com/enioxt/egos</a></p>
          <p className="mt-2">Powered by Alibaba Qwen-plus + OpenRouter fallback</p>
          <p className="mt-2 text-emerald-400">
            Every test is logged to our <a href="https://guard.egos.ia.br/dashboard" className="underline">real-time dashboard</a>
          </p>
        </footer>
      </main>
    </div>
  );
}
```

### TestForm.tsx — Interactive Testing

```typescript
// apps/guard-brasil-web/components/TestForm.tsx
'use client';

import { useState } from 'react';
import { ResultDisplay } from './ResultDisplay';

export function TestForm() {
  const [input, setText] = useState('');
  const [policyPack, setPolicyPack] = useState('security');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cost, setCost] = useState(0);

  const handleTest = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: input,
          policy_pack: policyPack,
          return_cost: true,
        }),
      });

      const data = await res.json();
      setResult(data);
      setCost(data.cost_usd || 0);
    } catch (error) {
      setResult({ error: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Input */}
      <div>
        <label className="block text-sm font-bold text-white mb-2">
          Your text to analyze:
        </label>
        <textarea
          value={input}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste your text here. Examples: CPF 123.456.789-00, RG 1234567, medical data, SQL queries..."
          className="w-full h-32 bg-slate-800 text-white border border-slate-600 rounded-lg p-4 focus:border-blue-500 focus:outline-none font-mono text-sm"
        />
      </div>

      {/* Policy Pack */}
      <div>
        <label className="block text-sm font-bold text-white mb-2">
          Policy Pack:
        </label>
        <select
          value={policyPack}
          onChange={(e) => setPolicyPack(e.target.value)}
          className="w-full bg-slate-800 text-white border border-slate-600 rounded-lg p-3 focus:border-blue-500 focus:outline-none"
        >
          <option value="security">🔒 Security (default: CPF, RG, MASP, placa)</option>
          <option value="health">🏥 Health (medical records, patient IDs)</option>
          <option value="judicial">⚖️ Judicial (case numbers, lawyer IDs)</option>
          <option value="financial">💰 Financial (account numbers, PIX keys)</option>
        </select>
      </div>

      {/* Test Button */}
      <button
        onClick={handleTest}
        disabled={!input.trim() || loading}
        className="w-full bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-600 text-white font-bold py-3 px-4 rounded-lg transition"
      >
        {loading ? 'Testing...' : `Test (${cost > 0 ? `$${cost.toFixed(5)}` : 'FREE'})`}
      </button>

      {/* Results */}
      {result && <ResultDisplay result={result} />}
    </div>
  );
}
```

### API Route: Proxy to Guard Brasil API

```typescript
// apps/guard-brasil-web/app/api/test/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();

    // Rate limiting: IP-based, 10 req/min
    const ip = req.headers.get('x-forwarded-for') || req.headers.get('x-client-ip') || 'unknown';
    const ipHash = await hashIp(ip);

    const cached = await checkRateLimit(ipHash);
    if (cached.count > 10) {
      return NextResponse.json(
        {
          error: 'Rate limit exceeded (10 req/min per IP)',
          quota_reset_in_seconds: 60 - cached.age,
        },
        { status: 429 }
      );
    }

    // Call Guard Brasil API
    const res = await fetch('https://guard.egos.ia.br/v1/inspect', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.GUARDBRASIL_API_KEY}`,
      },
      body: JSON.stringify({
        text: body.text,
        policy_pack: body.policy_pack,
        return_cost: true,
      }),
    });

    const result = await res.json();

    // Log to telemetry
    await logToTelemetry({
      event_type: 'web_test',
      origin: 'guard.egos.ia.br',
      policy_pack: body.policy_pack,
      cost_usd: result.cost_usd,
      user_ip_hash: ipHash,
      user_agent_type: detectUserAgent(req.headers.get('user-agent')),
      referrer: req.headers.get('referer'),
    });

    // Increment rate limit
    await incrementRateLimit(ipHash);

    return NextResponse.json({
      ...result,
      cost_usd: result.cost_usd,
      provider: result.provider || 'qwen-plus',
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

async function hashIp(ip: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(ip + process.env.RATE_LIMIT_SECRET);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(hashBuffer))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
    .substring(0, 16);
}
```

---

## TRACK 2: X.com Bot — Automated Social Proof (Dias 1-2)

### Criar Bot em apps/egos-lab ou novo agent

```typescript
// agents/agents/x-guardbrasil-bot.ts
import { Anthropic } from '@anthropic-ai/sdk';
import { TwitterApi } from 'twitter-api-v2';

interface GuardBrasilPost {
  title: string;
  description: string;
  example_input: string;
  example_output: string;
  cta: string;
}

const xClient = new TwitterApi({
  appKey: process.env.X_API_KEY!,
  appSecret: process.env.X_API_SECRET!,
  accessToken: process.env.X_ACCESS_TOKEN!,
  accessSecret: process.env.X_ACCESS_TOKEN_SECRET!,
});

const rwClient = xClient.readWrite;

// Daily posts — cycle through examples
const DAILY_POSTS: GuardBrasilPost[] = [
  {
    title: '🛡️ CPF Protection',
    description: 'Guard Brasil automatically detects and masks CPF numbers',
    example_input: 'Customer CPF: 123.456.789-00',
    example_output: 'CPF: ***.***.***-00 ✅ Safe to log',
    cta: 'Test it free: guard.egos.ia.br (100 tests/day)',
  },
  {
    title: '🚗 Plate Detection',
    description: 'Identify vehicle plates in text (important for govtech)',
    example_input: 'Police report: Car ABC-1234 seen at scene',
    example_output: 'Car ***-**** seen at scene ✅ Anonymized',
    cta: 'Try now: guard.egos.ia.br',
  },
  {
    title: '🧠 ATRiAN Bias Check',
    description: 'Detect ethical issues in AI training data',
    example_input: '"Young Black man" applying for loan',
    example_output: 'ATRiAN score: 42/100 ⚠️ Bias detected',
    cta: 'Test your text: guard.egos.ia.br',
  },
  {
    title: '🏥 Medical Privacy',
    description: 'Protect health data in clinical notes',
    example_input: 'Patient John (ID: 12345) has diabetes',
    example_output: 'Patient **** (ID: ***) has diabetes ✅',
    cta: 'Free HIPAA tool: guard.egos.ia.br',
  },
  {
    title: '⚖️ Judicial Anonymization',
    description: 'Mask case numbers, lawyer IDs for public docs',
    example_input: 'Case #2025001234 represented by OAB 123456',
    example_output: 'Case #******* represented by OAB ****** ✅',
    cta: 'Tool for Judiciário: guard.egos.ia.br',
  },
  {
    title: '💰 Financial Data',
    description: 'Anonymize PIX keys, account numbers',
    example_input: 'Transferência para PIX 12345678-1234-abcd',
    example_output: 'Transferência para PIX **-**** ✅ Safe',
    cta: 'Teste grátis: guard.egos.ia.br',
  },
];

export async function postDailyGuardBrasilUpdate(): Promise<void> {
  try {
    const dayOfWeek = new Date().getDay();
    const post = DAILY_POSTS[dayOfWeek % DAILY_POSTS.length];

    const tweetText = `${post.title}

"${post.example_input}"

↓ Guard Brasil processes:

"${post.example_output}"

${post.cta}

#LGPD #Security #IA #Govtech`;

    // Post to X
    const response = await rwClient.v2.tweet(tweetText);

    console.log(`✅ Posted to X.com: ${response.data.id}`);

    // Log to telemetry
    await recordEvent({
      event_type: 'social_post',
      platform: 'x.com',
      post_id: response.data.id,
      title: post.title,
      impressions_expected: 500, // Estimate
    });
  } catch (error) {
    console.error('❌ Failed to post to X.com:', error);
  }
}

// Schedule: Run daily at 9 AM São Paulo time
// Use: bun agent:run x-guardbrasil-bot --exec
```

### Schedule with cron (in Docker)

```dockerfile
# Dockerfile for Guard Brasil bot
FROM oven/bun:1.3.0-alpine

WORKDIR /app
COPY . .

RUN bun install

# Install ofelia (job scheduler)
RUN apk add --no-cache dcron

# Add cron job
RUN echo "0 9 * * * bun /app/agents/agents/x-guardbrasil-bot.ts >> /var/log/xbot.log 2>&1" | crontab -

CMD ["crond", "-f"]
```

Or use GitHub Actions (simpler):

```yaml
# .github/workflows/guardbrasil-daily-post.yml
name: Guard Brasil Daily X.com Post

on:
  schedule:
    - cron: '0 9 * * *' # 9 AM UTC (6 AM São Paulo... adjust!)

jobs:
  post:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1

      - name: Post to X.com
        env:
          X_API_KEY: ${{ secrets.X_API_KEY }}
          X_API_SECRET: ${{ secrets.X_API_SECRET }}
          X_ACCESS_TOKEN: ${{ secrets.X_ACCESS_TOKEN }}
          X_ACCESS_TOKEN_SECRET: ${{ secrets.X_ACCESS_TOKEN_SECRET }}
        run: bun run agents/agents/x-guardbrasil-bot.ts
```

---

## TRACK 3: Dashboard MVP — Real-time Telemetry (Dias 2-5)

### Create `/apps/guard-brasil-dashboard` (Next.js + Supabase)

```bash
cd /home/enio/egos/apps
npx create-next-app@latest guard-brasil-dashboard --typescript --tailwind
cd guard-brasil-dashboard
bun add @supabase/supabase-js recharts
```

### Structure

```
apps/guard-brasil-dashboard/
├── app/
│   ├── page.tsx              # Public showcase (limited data)
│   ├── dashboard/
│   │   └── page.tsx          # Auth-required full dashboard
│   ├── api/
│   │   ├── auth/route.ts     # API key authentication
│   │   └── events/route.ts   # Fetch events for customer
│   └── layout.tsx
├── components/
│   ├── ActivityFeed.tsx      # Real-time events
│   ├── CostChart.tsx         # Line chart of spending
│   ├── PolicyPackBreakdown.tsx # Pie chart
│   ├── AIInsights.tsx        # Qwen daily summaries
│   └── QuotaBar.tsx          # Visual quota usage
├── lib/
│   ├── supabase.ts           # Client
│   ├── auth.ts               # API key auth
│   └── formatters.ts         # Data formatting
└── public/
```

### Dashboard Main Page (Public)

```typescript
// apps/guard-brasil-dashboard/app/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@supabase/supabase-js';
import { ActivityFeed } from '@/components/ActivityFeed';
import { CostChart } from '@/components/CostChart';

export default function PublicDashboard() {
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState({ total: 0, cost: 0, providers: {} });

  useEffect(() => {
    // Fetch public stats (last 100 events, anonymized)
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    );

    const channel = supabase
      .channel('guard-brasil-public')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'guard_brasil_events',
          filter: `timestamp=gte.${new Date(Date.now() - 24 * 3600 * 1000).toISOString()}`,
        },
        (payload) => {
          // Anonymize and add
          const anonymized = {
            event_type: payload.new.event_type,
            cost_usd: payload.new.cost_usd,
            duration_ms: payload.new.duration_ms,
            model_id: payload.new.model_id,
            policy_pack: payload.new.policy_pack,
          };
          setEvents((prev) => [anonymized, ...prev].slice(0, 50));
        }
      )
      .subscribe();

    return () => supabase.removeChannel(channel);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white">Guard Brasil Live</h1>
          <p className="text-slate-300 mt-2">
            Real-time activity from users testing Guard Brasil
          </p>
        </div>

        {/* Public activity */}
        <div className="grid gap-8 md:grid-cols-2">
          <div>
            <h2 className="text-xl font-bold text-white mb-4">Last 24h Activity</h2>
            <ActivityFeed events={events} />
          </div>

          <div>
            <h2 className="text-xl font-bold text-white mb-4">Cost Breakdown</h2>
            <CostChart events={events} />
          </div>
        </div>

        {/* Stats */}
        <div className="mt-12 grid grid-cols-3 gap-4">
          <StatCard
            title="Total Inspections"
            value={events.length}
            unit="tests"
          />
          <StatCard
            title="Total Cost"
            value={events.reduce((sum, e) => sum + (e.cost_usd || 0), 0).toFixed(4)}
            unit="USD"
          />
          <StatCard
            title="Avg Response Time"
            value={Math.round(
              events.reduce((sum, e) => sum + (e.duration_ms || 0), 0) / events.length
            )}
            unit="ms"
          />
        </div>

        {/* CTA */}
        <div className="mt-12 text-center bg-slate-800 border border-emerald-600 rounded-lg p-8">
          <h3 className="text-2xl font-bold text-white">See YOUR data live</h3>
          <p className="text-slate-300 mt-2">
            Authenticate with your API key to see your inspections in real-time
          </p>
          <button className="mt-6 bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-3 px-8 rounded-lg">
            Sign in with API Key
          </button>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, unit }) {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
      <h3 className="text-slate-400 text-sm font-bold">{title}</h3>
      <p className="text-3xl font-bold text-white mt-2">{value}</p>
      <p className="text-slate-400 text-xs mt-1">{unit}</p>
    </div>
  );
}
```

### Customer Dashboard (Auth-required)

```typescript
// apps/guard-brasil-dashboard/app/dashboard/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { createClient } from '@supabase/supabase-js';
import { QuotaBar } from '@/components/QuotaBar';
import { AIInsights } from '@/components/AIInsights';

export default function CustomerDashboard() {
  const router = useRouter();
  const [customer, setCustomer] = useState(null);
  const [events, setEvents] = useState([]);
  const [apiKey, setApiKey] = useState('');
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    // Get API key from query or localStorage
    const key = new URLSearchParams(window.location.search).get('key') ||
                localStorage.getItem('guard_brasil_api_key');

    if (!key) {
      router.push('/');
      return;
    }

    // Authenticate
    authenticateCustomer(key);
  }, []);

  async function authenticateCustomer(key: string) {
    try {
      const res = await fetch('/api/auth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: key }),
      });

      if (!res.ok) throw new Error('Authentication failed');

      const { customer } = await res.json();
      setCustomer(customer);
      setApiKey(key);
      setAuthenticated(true);

      localStorage.setItem('guard_brasil_api_key', key);
      subscribeToEvents(key);
    } catch (error) {
      alert('Invalid API key');
      router.push('/');
    }
  }

  function subscribeToEvents(apiKeyHash: string) {
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    );

    const channel = supabase
      .channel(`customer:${apiKeyHash}`)
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'guard_brasil_events',
          filter: `api_key_hash=eq.${apiKeyHash}`,
        },
        (payload) => {
          setEvents((prev) => [payload.new, ...prev]);
        }
      )
      .subscribe();
  }

  if (!authenticated) {
    return <div className="text-white text-center py-12">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-white">Dashboard</h1>
            <p className="text-slate-300 mt-2">
              {customer?.email || 'Welcome back'}
            </p>
          </div>
          <button
            onClick={() => {
              localStorage.removeItem('guard_brasil_api_key');
              router.push('/');
            }}
            className="text-slate-400 hover:text-white"
          >
            Logout
          </button>
        </div>

        {/* Quota */}
        <div className="mb-8 bg-slate-800 border border-slate-700 rounded-lg p-6">
          <QuotaBar
            used={customer?.quota_used || 0}
            limit={customer?.quota_limit || 100000}
            cost={events.reduce((sum, e) => sum + (e.cost_usd || 0), 0)}
          />
        </div>

        {/* AI Insights */}
        <div className="mb-8">
          <AIInsights events={events} customer={customer} />
        </div>

        {/* Activity Feed */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
          <h2 className="text-xl font-bold text-white mb-4">Live Activity</h2>
          <ActivityFeed events={events} detailed={true} />
        </div>
      </div>
    </div>
  );
}
```

---

## TRACK 4: Database & Supabase (Dia 1 — Preparação)

### Create guard_brasil_events table

```sql
-- In Supabase SQL editor or migration
CREATE TABLE guard_brasil_events (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMP DEFAULT NOW(),

  -- Event
  event_type TEXT NOT NULL,
  api_key_hash TEXT NOT NULL,

  -- Performance
  duration_ms INTEGER,
  tokens_in INTEGER,
  tokens_out INTEGER,
  cost_usd NUMERIC(10, 8),

  -- Model
  model_id TEXT,
  provider TEXT,

  -- Guard-specific
  policy_pack TEXT,
  pii_types_detected TEXT[],
  atrian_score NUMERIC(3, 1),
  text_length INTEGER,
  status_code INTEGER,
  error_message TEXT,

  -- Metadata
  metadata JSONB,

  -- Indexes
  INDEX idx_api_key ON guard_brasil_events(api_key_hash),
  INDEX idx_created_at ON guard_brasil_events(created_at DESC),
  INDEX idx_event_type ON guard_brasil_events(event_type)
);

-- RLS: Customers see only their data
ALTER TABLE guard_brasil_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY customer_select
  ON guard_brasil_events FOR SELECT
  USING (api_key_hash = auth.uid());
```

### Create guard_brasil_customers table

```sql
CREATE TABLE guard_brasil_customers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at TIMESTAMP DEFAULT NOW(),

  api_key_hash TEXT UNIQUE NOT NULL,
  api_key_prefix TEXT,  -- For UI display (first 10 chars)

  email TEXT,
  tier TEXT CHECK (tier IN ('free', 'starter', 'pro', 'enterprise')),
  status TEXT CHECK (status IN ('active', 'suspended', 'inactive')),

  quota_limit BIGINT DEFAULT 3000,  -- Free: 3k/month
  quota_reset_at TIMESTAMP,

  -- Metadata
  company TEXT,
  created_by_source TEXT,  -- 'x.com', 'email', 'landing_page'
  metadata JSONB
);
```

---

## TRACK 5: Integração + Testing (Dias 4-5)

### Test Checklist

- [ ] Landing page loads, examples work
- [ ] Rate limiting works (10 req/min per IP)
- [ ] X.com bot posts daily
- [ ] Telemetry records each event
- [ ] Dashboard loads with public data
- [ ] Dashboard auth works (API key login)
- [ ] Realtime WebSocket updates
- [ ] Cost calculation accurate

### Deploy

```bash
# Landing page
cd /home/enio/egos/apps/guard-brasil-web
vercel deploy

# Dashboard
cd /home/enio/egos/apps/guard-brasil-dashboard
vercel deploy

# API gateway (if separate)
# Already running on Hetzner
```

---

## Timeline Summary

```
Week 1 (Mar 31 - Apr 5):
  Mon: Landing page + form (6h)
  Tue: X.com bot setup + test (4h)
  Wed: Dashboard MVP structure (6h)
  Thu: Supabase + telemetry integration (4h)
  Fri: Testing + tweaks (4h)
  Total: 24h

Week 2 (Apr 6 - 12):
  Mon-Fri: M-007 outreach (5h actual work, spread across)
  Par: Dashboard features (AI insights, charts)
  Par: Handle X.com responses, schedule demos
  Total: 15-20h

Week 3 (Apr 13 - 20):
  Execute demos
  Implement customer dashboards for pilots
  Production hardening
  Total: 15h
```

---

## Success Metrics (Go-Live Checklist)

- [ ] Landing page: >100 visits/day from X.com traffic
- [ ] X.com: Bot posting daily, engagement >5 likes/post
- [ ] Dashboard: >10 customers signed up
- [ ] API: <300ms latency, 99.9% uptime
- [ ] Telemetry: 100% of requests logged, zero data loss
- [ ] Cost: <$0.10/day total infrastructure (LLMs)
- [ ] M-007: 5+ emails sent, 3-5 responses within 48h
