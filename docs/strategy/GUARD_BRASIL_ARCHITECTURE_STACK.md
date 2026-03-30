# Guard Brasil — Full Stack Architecture (TRANSPARÊNCIA RADICAL)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         GUARD BRASIL ECOSYSTEM                               │
└──────────────────────────────────────────────────────────────────────────────┘

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                          CLIENT LAYER (Free/Starter/Pro)                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│                                                                              │
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────┐ │
│  │  npm SDK (Free)     │    │  REST API (Starter) │    │  Dashboard (Pro)│ │
│  │ @egosbr/guard-brasil│    │ guard.egos.ia.br/   │    │ guard.egos.ia.br│
│  │                     │    │   v1/inspect        │    │    /dashboard   │
│  │ • CPF masking       │    │ • Bearer auth       │    │ • Activity feed │
│  │ • RG detection      │    │ • JSON request/resp │    │ • Cost breakdown│
│  │ • MASP validation   │    │ • 4ms latency       │    │ • IA reports    │
│  │ • No telemetry      │    │ • Auto telemetry    │    │ • Alerts config │
│  └─────────────────────┘    └─────────────────────┘    └─────────────────┘
│           │                           │                       │
│           └───────────────────────────┴───────────────────────┘
│                                 ↓
├──────────────────────── HTTPS / MCP Stdio ────────────────────────────────────
│
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                      CORE LAYER (API Server + Telemetry)                    ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ apps/api/src/server.ts (Bun HTTP Server - Hetzner:3099)            │   │
│  │                                                                     │   │
│  │  POST /v1/inspect                                                  │   │
│  │    ├─ Input: {text, options}                                      │   │
│  │    ├─ Execution:                                                  │   │
│  │    │  ├─ GuardBrasil.inspect() (packages/guard-brasil)            │   │
│  │    │  │  ├─ ATRiAN.validate()  → score 0-100                     │   │
│  │    │  │  ├─ PIIScannerBR.detect() → CPF/RG/MASP/REDS            │   │
│  │    │  │  ├─ EvidenceChain.hash() → audit trail                  │   │
│  │    │  │  └─ LGPDDisclosure → compliance text                    │   │
│  │    │  └─ TelemetryRecorder.recordEvent()                         │   │
│  │    │     ├─ event_type: 'cpf_masking'|'rg_detect'|etc          │   │
│  │    │     ├─ cost_usd: 0.002 (~R$0.01)                          │   │
│  │    │     ├─ tokens_in/out: measured                            │   │
│  │    │     ├─ model_id: 'qwen-plus'                              │   │
│  │    │     └─ persist to Supabase                                │   │
│  │    └─ Output: {safe, output, atrian, evidence, cost}            │   │
│  │                                                                     │   │
│  │  Health checks + rate limiting (100 req/min)                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                            ↓                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ packages/shared/src/telemetry.ts (Structured Telemetry)            │   │
│  │                                                                     │   │
│  │  • recordEvent(TelemetryEvent)                                      │   │
│  │  • recordChatCompletion(tokens, cost, duration)                     │   │
│  │  • recordRateLimitHit(clientIp, endpoint)                           │   │
│  │  • Dual output: Supabase + JSON console logs (docker-friendly)      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                            ↓                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ apps/api/src/mcp-server.ts (MCP Stdio Server)                       │   │
│  │                                                                     │   │
│  │  • guard_inspect(text) → same as REST /v1/inspect                  │   │
│  │  • guard_scan_pii(text) → detailed PII breakdown                  │   │
│  │  • guard_check_safe(text) → pass/fail only (fast)                 │   │
│  │  • JSON-RPC 2.0 stdio protocol                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                            ↓↓↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    DATA PERSISTENCE & OBSERVABILITY LAYER                   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Supabase PostgreSQL (guard_events table)                            │   │
│  │                                                                     │   │
│  │  Columns:                                                           │   │
│  │  • id: UUID                                                         │   │
│  │  • api_key_hash: SHA256 of client key                             │   │
│  │  • event_type: 'cpf_masking'|'rg_detect'|'masp_lookup'|etc        │   │
│  │  • model_id: 'qwen-plus'                                           │   │
│  │  • tokens_in, tokens_out: integer                                  │   │
│  │  • cost_usd: decimal(10,6)                                         │   │
│  │  • duration_ms: integer                                            │   │
│  │  • status_code: 200|429|500|etc                                    │   │
│  │  • error_message: (if error)                                       │   │
│  │  • client_ip_hash: privacy-safe                                    │   │
│  │  • metadata: JSONB {pii_types: [...], atrian_score: ...}          │   │
│  │  • created_at: timestamp with TZ                                   │   │
│  │                                                                     │   │
│  │  Indexes: (api_key_hash, created_at), (event_type)                │   │
│  │  Retention: 1 year (archival to cold storage beyond)              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Supabase Realtime (WebSocket updates for Dashboard)                │   │
│  │  • Activity feed updates (< 1 sec latency)                         │   │
│  │  • Cost accumulation (live ticker)                                 │   │
│  │  • Alert notifications                                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                            ↓↓↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    ANALYTICS & REPORTING LAYER                              ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ apps/dashboard/pages/dashboard.tsx (Next.js SPA)                    │   │
│  │  Powered by: React + TanStack Query + Recharts                      │   │
│  │                                                                     │   │
│  │  Sections:                                                          │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ Activity Feed (Real-time)                                  │   │   │
│  │  │  • Last 100 events with timestamps                        │   │   │
│  │  │  • Cost per event (R$0.02, etc)                           │   │   │
│  │  │  • Event type badge (CPF, RG, etc)                        │   │   │
│  │  │  • Status indicator (✅ success, ❌ error)                │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ Cost Breakdown (Charts)                                    │   │   │
│  │  │  • Pie chart: % by event type                             │   │   │
│  │  │  • Line chart: Daily cost trend                           │   │   │
│  │  │  • Table: Cumulative by type                              │   │   │
│  │  │  • Budget indicator: $X of $Y used                        │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ IA Insights (Qwen-powered)                                 │   │   │
│  │  │  Refreshed 2x daily, natural language:                     │   │   │
│  │  │  • Pattern detection (peaks/valleys)                       │   │   │
│  │  │  • Anomaly alerts                                          │   │   │
│  │  │  • Cost optimization suggestions                           │   │   │
│  │  │  • Safety recommendations (ATRiAN score trends)            │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ Configuration Panel                                        │   │   │
│  │  │  • Alert thresholds (CPF/hour, score < X, cost > Y)       │   │   │
│  │  │  • Integrations (Slack, Teams, Email webhooks)            │   │   │
│  │  │  • Report scheduling (daily/weekly/monthly)               │   │   │
│  │  │  • Rate limit viewing + override requests                 │   │   │
│  │  │  • API key rotation                                       │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Report Generator (Async, Qwen MCP)                                  │   │
│  │  • Trigger: Daily cron (8am PT), on-demand                          │   │
│  │  • Input: guard_events aggregated (24h/7d/30d window)              │   │
│  │  • Process:                                                         │   │
│  │    1. Query Supabase: SUM(cost), COUNT(*), GROUP BY(event_type)    │   │
│  │    2. Detect trends: Compare vs previous period                    │   │
│  │    3. Generate prompt: "Analyze these API usage stats..."          │   │
│  │    4. Call Qwen via MCP: get natural language analysis             │   │
│  │    5. Store report in Supabase (guard_reports table)               │   │
│  │    6. Send via Slack/Email webhook                                 │   │
│  │                                                                     │   │
│  │  Output format: Markdown with embeds:                              │   │
│  │  ```                                                                │   │
│  │  # Guard Brasil Daily Report — 2026-03-30                          │   │
│  │                                                                     │   │
│  │  **Summary:** 847 API calls, R$16.94 spent, 3 anomalies detected   │   │
│  │                                                                     │   │
│  │  **Usage breakdown:**                                              │   │
│  │  - CPF masking: 420 calls (50%) — typical                          │   │
│  │  - RG detection: 310 calls (37%) — +12% vs yesterday               │   │
│  │  - ATRiAN scoring: 117 calls (14%) — +25% (WATCH)                 │   │
│  │                                                                     │   │
│  │  **Anomalies:**                                                    │   │
│  │  ⚠️  RG detection spike at 14h UTC (310 → 800/h)                  │   │
│  │      → Possible: daily batch job or API test                       │   │
│  │      → Recommendation: confirm intentional                         │   │
│  │                                                                     │   │
│  │  **Cost optimization:**                                            │   │
│  │  💰 Using /batch endpoint could save ~R$8.47/mo (50% discount)    │   │
│  │  ```                                                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Webhook Dispatcher (Notifications)                                  │   │
│  │                                                                     │   │
│  │  Triggers:                                                          │   │
│  │  • Daily report (8am)                                              │   │
│  │  • Weekly summary (Mondays 9am)                                    │   │
│  │  • Alerts (on threshold breach, real-time)                        │   │
│  │                                                                     │   │
│  │  Channels:                                                          │   │
│  │  • Slack: #guard-brasil-alerts (customer workspace)                │   │
│  │  • Teams: Bot notification                                         │   │
│  │  • Email: Customer + cc:support@egos.ia.br                         │   │
│  │  • Custom: User-defined webhooks                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘


┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                           DATA FLOW EXAMPLE                                 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│                                                                              │
│  User calls Guard Brasil API:                                              │
│                                                                              │
│  POST guard.egos.ia.br/v1/inspect                                           │
│  Authorization: Bearer sk_live_abc123...                                    │
│  Content-Type: application/json                                             │
│                                                                              │
│  {                                                                           │
│    "text": "Paciente João Silva, CPF 123.456.789-00",                      │
│    "options": {"audit": true}                                               │
│  }                                                                           │
│                                                  ↓                           │
│                          [apps/api/src/server.ts processes]                │
│                          GuardBrasil.inspect(text) called                  │
│                          Returns in 4ms                                     │
│                                                  ↓                           │
│  Response 200 OK:                                                           │
│  {                                                                           │
│    "safe": true,                                                             │
│    "output": "Paciente João Silva, CPF [CPF REMOVIDO]",                    │
│    "blocked": ["123.456.789-00"],                                           │
│    "atrian": {"score": 92, "reasoning": "..."},                             │
│    "evidenceChain": "hash:sha256:abc123..."                                │
│  }                                                                           │
│                                                  ↓                           │
│                    [TelemetryRecorder.recordEvent called]                   │
│                    Event stored in Supabase guard_events:                  │
│                    {                                                         │
│                      event_type: 'cpf_masking',                             │
│                      model_id: 'qwen-plus',                                 │
│                      tokens_in: 42,                                         │
│                      tokens_out: 15,                                        │
│                      cost_usd: 0.0019,  ← Cost calculated                 │
│                      duration_ms: 4,                                        │
│                      status_code: 200,                                      │
│                      created_at: '2026-03-30T14:23:45Z'                    │
│                    }                                                         │
│                                                  ↓                           │
│              [Dashboard updates in real-time via Supabase Realtime]         │
│              Activity feed shows: [14:23] ✅ CPF masking  R$0.02            │
│              Cost ticker updates: R$16.94 → R$16.96                         │
│                                                  ↓                           │
│          [Daily cron @ 8am: Report Generator reads last 24h events]        │
│          Qwen analyzes: "847 calls, R$16.94 total, RG spike at 14h UTC"   │
│          Report sent to Slack: "Daily Guard Brasil Report — see link"     │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Key Characteristics

| Component | Tech | Why | Status |
|-----------|------|-----|--------|
| **REST API** | Bun + TypeScript | Speed (4ms), low overhead | ✅ Live |
| **SDK** | TS/Node.js, MIT open-source | Portability, vendor lock-out | ✅ npm published |
| **MCP Server** | JSON-RPC stdio | Claude integration, no HTTP needed | ✅ Built |
| **Telemetry** | Supabase + JSON logs | Traceability, Docker-friendly | ✅ Implemented |
| **Dashboard** | Next.js + React | Modern, real-time, SPA | 🔜 Week 1 |
| **Reports** | Qwen via MCP | Natural language, transparent | 🔜 Week 2 |
| **Webhooks** | Standard HTTP POST | Slack, Teams, Email, custom | 🔜 Week 2 |

## What Makes This "TRANSPARÊNCIA RADICAL"

1. **Every event is visible** — not aggregated, not hidden in dashboards
2. **Every cost is shown** — R$0.02 per call, itemized, explainable
3. **No surprises** — cost appears immediately, before any invoice
4. **IA explains why** — not just "detected CPF", but "why it matters in this context"
5. **Full control** — users set their own thresholds, not forced tiers
6. **Zero lock-in** — open SDK, standard API, data export anytime
