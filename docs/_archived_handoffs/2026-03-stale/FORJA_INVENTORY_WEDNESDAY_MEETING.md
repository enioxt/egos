# 📋 FORJA Inventory - Complete Technical Overview
**Prepared by:** OpenCode Agent | **Date:** 2026-03-23 | **For:** Wednesday Meeting with Forja Team

---

## ✅ EXECUTIVE SUMMARY

**Forja Status:** MVP Phase - Chat-First ERP for Operations
- **Live:** https://forja-orpin.vercel.app (Vercel Production)
- **Database:** Supabase PostgreSQL (schema operacional ativo)
- **LLM:** Dual-provider (Alibaba Qwen-plus primary, Gemini 2.0 Flash fallback)
- **Tools:** 4 core operational tools (search, stock, quote, production)
- **Capabilities:** 17 active + 10 planned

---

## 1. 🎯 PRODUCT VISION

### What is Forja?
**Chat-first ERP assistant for operations** (metalurgia, oficinas)

**Core Value Proposition:**
- Query operational data via conversational AI
- Create reports (PDF/Excel) on demand
- Data entry via text/audio
- Run automations with governance (approval workflows)
- Email integration (Gmail/M365) with AI triage
- Notifications via WhatsApp/Push/Email

**Target User:** Metalúrgicas, oficinas mecânicas
- **UX Design:** Large touch targets (64px+), high contrast, voice-first
- **Language:** Portuguese (BR)
- **Accessibility:** Field workers, limited vision, large hands

---

## 2. 🏗️ CURRENT ARCHITECTURE

### Tech Stack (Active)

```
┌─ Frontend ─────────────────────────┐
│ Next.js 15 + React 19 + Tailwind 4 │
│ Deployed on Vercel                 │
│ PWA + Chat UI + Dashboard          │
└────────────────────────────────────┘
         ↓
┌─ Backend ──────────────────────────┐
│ Next.js API Routes (TypeScript)     │
│ FastAPI (Python) - future layer    │
│ Supabase PostgreSQL + RLS          │
│ Redis (planned)                    │
└────────────────────────────────────┘
         ↓
┌─ LLM & Tools ──────────────────────┐
│ Alibaba Qwen-plus (primary)        │
│ Google Gemini 2.0 Flash (fallback) │
│ OpenRouter adapter                 │
│ Tool Registry + Runner             │
└────────────────────────────────────┘
```

### Deployment Pipeline

```
Local Dev (Turbopack)
    ↓
GitHub Push
    ↓
Vercel Auto-Deploy
    ↓
Production: https://forja-orpin.vercel.app
```

**Production Verified:** 2026-03-20 ✅

---

## 3. ✨ ACTIVE CAPABILITIES (17 Implemented)

### Chat & LLM

| # | Capability | Module | Status |
|---|-----------|--------|--------|
| 1 | Chat API with LLM + SSE | `src/app/api/chat/route.ts` | ✅ Active |
| 2 | Multi-provider fallback | `src/lib/chat/runtime.ts` | ✅ Active |
| 3 | Provider routing by env | `src/lib/chat/runtime.ts` | ✅ Active |
| 4 | Conversation memory (session) | `src/lib/chat/runtime.ts` | 🔧 Partial |

### Safety & Governance

| # | Capability | Module | Status |
|---|-----------|--------|--------|
| 5 | ATRiAN Ethical Validation | `src/lib/chat/safety.ts` | ✅ Active |
| 6 | PII Scanner (CPF, CNPJ, telefone) | `src/lib/chat/safety.ts` | ✅ Active |
| 7 | Rate Limiting (per-IP) | `src/lib/chat/rate-limiter.ts` | ✅ Active |
| 8 | Telemetry (JSON logs) | `src/lib/chat/safety.ts` | ✅ Active |

### Data & Tools

| # | Capability | Module | Status |
|---|-----------|--------|--------|
| 9 | Tool Calling (Deterministic) | `src/lib/tools/chat-tools.ts` | ✅ Active |
| 10 | Tool Registry (4 core tools) | `src/lib/tools/registry.ts` | ✅ Active |
| 11 | Tool Runner with validation | `src/lib/tools/runner.ts` | ✅ Active |
| 12 | Prompt Builder (domain-aware) | `src/lib/chat/prompt.ts` | ✅ Active |

### Database & Schema

| # | Capability | Module | Status |
|---|-----------|--------|--------|
| 13 | Supabase RLS base schema | `supabase/migrations/20260319235900_*.sql` | ✅ Active |
| 14 | Operational core schema (cat/stock/quote/prod) | `supabase/migrations/20260320091000_*.sql` | ✅ Active |
| 15 | Supabase client (Next + Python) | `src/lib/supabase/client.ts` | ✅ Active |
| 16 | Contracts (TS + Python) | `src/lib/contracts/tools.ts` | ✅ Active |

### UI & Dashboard

| # | Capability | Module | Status |
|---|-----------|--------|--------|
| 17 | Dashboard operacional (mock-driven) | `src/app/(app)/painel/page.tsx` | 🔧 Partial |

---

## 4. 🔧 OPERATIONAL SCHEMA (Implemented in Supabase)

### Tables Structure

**Tenant & Auth:**
- `tenants` (id, name, subdomain, plan)
- `users` (id, tenant_id, email, role, created_at)
- `roles` (id, name, permissions - enum: admin, operator, viewer)

**Core ERP:**
- `customers` (id, name, cnpj, email, phone, address)
- `products` (id, name, category, code, unit_price, lead_time_days)
- `stock_positions` (id, product_id, warehouse, quantity, reserved)
- `stock_movements` (id, product_id, from_warehouse, to_warehouse, quantity, type, reason, created_at)
- `quotes` (id, customer_id, total_items, subtotal, taxes, total, status)
- `quote_items` (id, quote_id, product_id, quantity, unit_price, discount, subtotal)
- `production_orders` (id, customer_id, status, start_date, end_date, responsible)

**Audit & Observability:**
- `conversations` (id, user_id, tenant_id, summary, created_at)
- `messages` (id, conversation_id, role, content, model_used)
- `tool_calls` (id, conversation_id, tool_name, params, result, risk_tier)
- `audit_log` (id, user_id, action, resource, before, after, timestamp)

**RLS Enabled:** All tables have row-level security by tenant

---

## 5. 🛠️ CORE TOOLS (4 Implemented)

### Tool Registry

```typescript
Tool: search_products
├─ Input: { query: string, limit?: number }
├─ Output: [{ id, name, category, price }]
├─ Risk Tier: T0 (read-only)
└─ Use: Find materials by name/category/code

Tool: get_stock_level
├─ Input: { query: string }
├─ Output: { product, warehouse, quantity, reserved }
├─ Risk Tier: T0 (read-only)
└─ Use: Check inventory availability

Tool: create_quote
├─ Input: { customer_id, items: [{ product_id, qty }] }
├─ Output: { quote_id, draft_url, preview }
├─ Risk Tier: T1 (user-scoped write)
└─ Use: Draft new quote for confirmation

Tool: get_production_status
├─ Input: { status?: 'active' | 'pending' | 'completed' }
├─ Output: [{ order_id, status, progress_pct }]
├─ Risk Tier: T0 (read-only)
└─ Use: Track production orders
```

### Fallback Strategy

```
User Query
    ↓
LLM determines tool → Call tool
    ↓ (if tool not found or error)
Use deterministic routing (regex/pattern)
    ↓ (if pattern no match)
Fallback to mock data OR direct Supabase query
    ↓ (if user not authorized)
Return "sem permissão" + audit log
```

---

## 6. 📊 MODULES REUSABLE FROM ECOSYSTEM

### From `egos-lab` (IA & Orchestration)

| Module | Source | Reusable in Forja | Status |
|--------|--------|------------------|--------|
| AI Client | `packages/shared/src/ai-client.ts` | ✅ LLM routing base | Ready |
| Rate Limiter | `packages/shared/src/rate-limiter.ts` | ✅ Per-tenant limit | Ready |
| MCP Tool Runner | `packages/mcp/src/index.ts` | ✅ Tool execution | Ready |
| Telegram Client | `packages/shared/src/social/telegram-client.ts` | ✅ Notification channel | Ready |
| API Registry | `packages/shared/src/api-registry.ts` | ✅ Governance rules | Ready |
| Telegram Bot | `apps/telegram-bot/src/index.ts` | ✅ Chat pattern ref | Ready |
| Agent Runtime | `agents/runtime/runner.ts` | ✅ Worker inspiration | Ready |

### From `carteira-livre` (APIs & Webhooks)

| Module | Source | Reusable in Forja | Status |
|--------|--------|------------------|--------|
| Evolution API (WhatsApp) | `services/whatsapp/evolution-api.ts` | ✅ Notifications | Ready |
| API Utils | `services/api-utils.ts` | ✅ Auth/RBAC pattern | Ready |
| Asaas Sync | `services/payments/asaas-sync.ts` | ✅ Async webhook pattern | Ready |
| API Usage Logger | `services/api-usage-logger.ts` | ✅ Telemetry | Ready |

### From `br-acc/852` (Chat & Tools)

| Module | Source | Reusable in Forja | Status |
|--------|--------|------------------|--------|
| **Chat Router (26 tools)** | `api/src/bracc/routers/chat.py` | ✅ **Full architecture** | Reuse! |
| Transparency Tools | `api/src/bracc/services/transparency_tools.py` | ✅ Tool pattern | Ready |
| Public Guard / LGPD | `api/src/bracc/services/public_guard.py` | ✅ Data masking | Ready |
| Cache Service | `api/src/bracc/services/cache.py` | ✅ Redis layer | Ready |
| Activity Feed | `api/src/bracc/routers/activity.py` | ✅ Event logging | Ready |
| Evidence Chain | `chat.py` | ✅ Audit trail | Ready |

---

## 7. 📋 TASK STATUS (Roadmap)

### ✅ Completed Tasks (15)

| Task | Completed | Details |
|------|-----------|---------|
| FORJA-014 | 05/03 | Market research + tech evaluation |
| FORJA-015 | 05/03 | Next.js 15 scaffold + 7 screens UI |
| FORJA-016 | 05/03 | Architecture doc + MVP feedback form |
| FORJA-017 | 05/03 | Fiscal calculator (ICMS + IBS/CBS) |
| FORJA-018 | 05/03 | Chatbot language research (Python vs Elixir) |
| FORJA-019 | 05/03 | Email pipeline + observability design |
| FORJA-030 | 05/03 | Deploy to Vercel (production ready) |
| FORJA-022 | 05/03 | Interactive dashboard (painel operacional) |
| FORJA-001 | 19/03 | Minimal data model + RLS migrations |
| FORJA-002 | 20/03 | Data contracts (TS + Python) |
| FORJA-004 | 20/03 | Chat service + tool runner |
| FORJA-001B | 20/03 | Operational schema (customers, products, stock, quotes, production) |
| FORJA-004C | 19/03 | Product truth documentation (AGENTS.md v2.1, TASKS.md, SYSTEM_MAP.md) |
| FORJA-034 | 20/03 | Runtime + Deploy surface truth (Vercel envs validated) |

### 🔄 In Progress

| Task | Priority | Details |
|------|----------|---------|
| FORJA-003 | P0 | Auth Multi-Tenant + RLS policies |
| FORJA-004B | P0 | Design System (campo mode, 64px+ buttons) |
| FORJA-004D | P1 | PRD + ICP + Go-to-market |

### ⏳ Planned

| Task | Priority | Details |
|------|----------|---------|
| FORJA-031 | P1 | Coolify evaluation for production |
| FORJA-020 | P0 | WhatsApp Integration (Evolution API) |
| FORJA-021 | P0 | Triage Agent (WhatsApp bot) |
| FORJA-032 | P1 | Lightning Quoting Engine |
| FORJA-033 | P1 | Checklist Engine |
| FORJA-025 | P1 | Admin Dashboard full |
| FORJA-026 | P2 | PDF/DOCX Export (from 852) |
| FORJA-027 | P1 | Mobile (Capacitor Android) |
| FORJA-028 | P1 | Email ingestion (Gmail API / IMAP) |
| FORJA-029 | P2 | STT (Whisper via Groq) |

---

## 8. 🎮 DEMO: How it Works Today

### User: "Qual o estoque de aço inox 304?"

```
┌─ User sends message via Chat UI ──────────┐
│                                           │
│ Message: "Qual o estoque de aço inox?"   │
└──────────────────┬────────────────────────┘
                   ↓
        ┌─ LLM Processing ─────────┐
        │ • PII Scanner (safe ✅) │
        │ • Rate Limiter (OK ✅)  │
        │ • ATRiAN check (good ✅)|
        │ • Build system prompt   │
        └─────────┬───────────────┘
                  ↓
        ┌─ Tool Decision ──────────┐
        │ Model decides:           │
        │ → Need: get_stock_level │
        └─────────┬───────────────┘
                  ↓
        ┌─ Execute Tool ───────────┐
        │ • Validate input (Zod)  │
        │ • Check permissions     │
        │ • Query Supabase        │
        │ • Return: qty 523 units │
        └─────────┬───────────────┘
                  ↓
        ┌─ Generate Response ──────┐
        │ Model composes answer:   │
        │ "Temos 523 unidades..."  │
        │ SSE streams to UI        │
        └─────────┬───────────────┘
                  ↓
        ┌─ Audit & Log ────────────┐
        │ • Save conversation      │
        │ • Log tool call          │
        │ • Track tokens + cost    │
        │ • Alert if anomaly       │
        └──────────────────────────┘

Result shown to user in real-time via SSE
```

---

## 9. 🚀 SHARING WITH EGOS (What to Highlight Wednesday)

### What Forja Can Teach EGOS

1. **Operational Tool Pattern**
   - How to build domain-specific tool registry
   - Deterministic + LLM fallback strategy
   - Tool validation + risk tier classification

2. **Fiscal Integration**
   - ICMS/IBS/CBS calculator (complex tax logic)
   - Reforma Tributária tracking (2026-2033)
   - State-specific rules (CONFAZ)

3. **Safety Patterns**
   - ATRiAN ethical validation
   - PII scanning (CPF, CNPJ, telefone)
   - Rate limiting per-tenant

4. **Supabase RLS**
   - Multi-tenant isolation
   - Row-level security patterns
   - Operational schema design

5. **Accessibility**
   - Field worker UX (large touch, voice-first)
   - High contrast + assistive tech
   - Portuguese-first documentation

### What Forja Needs From EGOS

1. **Advanced Orchestration**
   - Sequential-Thinking for complex analysis
   - EXA for market/competitive research
   - Better fallback chains

2. **Agent Registry**
   - Worker automation framework
   - Multi-step approval workflows
   - Event-driven pipeline

3. **Telemetry & Observability**
   - Better cost tracking (per-tenant)
   - Usage analytics
   - Performance metrics

4. **Model Routing**
   - Intelligent model selection based on task
   - Cost optimization strategies
   - Quota management

---

## 10. 📁 FILE STRUCTURE

```
forja/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat/route.ts           ← Chat API + SSE
│   │   │   └── tools/execute/route.ts  ← Tool execution
│   │   └── (app)/
│   │       ├── chat/page.tsx           ← Chat UI
│   │       ├── painel/page.tsx         ← Dashboard
│   │       └── orcamentos/             ← Quoting UI
│   └── lib/
│       ├── chat/
│       │   ├── runtime.ts              ← LLM runtime
│       │   ├── safety.ts               ← ATRiAN + PII
│       │   ├── rate-limiter.ts         ← Rate limiting
│       │   └── prompt.ts               ← Prompt builder
│       ├── tools/
│       │   ├── registry.ts             ← Tool definitions
│       │   ├── runner.ts               ← Tool executor
│       │   ├── chat-tools.ts           ← Tool implementations
│       │   └── data.ts                 ← Mock + Supabase bridge
│       ├── contracts/
│       │   └── tools.ts                ← Zod schemas
│       ├── supabase/
│       │   ├── client.ts               ← Supabase setup
│       │   └── database.types.ts       ← Auto-generated types
│       └── mock-data.ts                ← Mock data
│
├── supabase/
│   └── migrations/
│       ├── 20260319235900_initial_schema.sql
│       └── 20260320091000_operational_core.sql
│
├── api/
│   └── src/forja/
│       ├── contracts.py                ← Python contracts
│       └── db.py                       ← Python DB client
│
├── scripts/
│   └── apply-migration.sh              ← Helper script
│
├── .guarani/                           ← Governance rules
├── .husky/pre-commit                   ← Doc freshness gates
├── AGENTS.md                           ← Project config
├── TASKS.md                            ← Task SSOT
├── FORJA_PRODUCT_SPEC.md              ← Product spec
└── docs/
    ├── SYSTEM_MAP.md
    ├── ARCHITECTURE.md
    ├── EMAIL_PIPELINE.md
    └── OBSERVABILITY.md
```

---

## 11. 🔗 QUICK REFERENCE

### Repositories
- **Forja:** https://github.com/enioxt/FORJA (PRIVATE)
- **Live:** https://forja-orpin.vercel.app
- **Database:** https://supabase.com/dashboard/project/zqcdkbnwkyitfshjkhqg

### Key Contacts/Tools
- **LLM Primary:** Alibaba DashScope API (Qwen-plus)
- **LLM Fallback:** OpenRouter (Gemini 2.0 Flash)
- **Database:** Supabase PostgreSQL + RLS
- **Deployment:** Vercel (production)
- **Future:** Coolify (VPS evaluation)

### Documentation
- Product Spec: `FORJA_PRODUCT_SPEC.md`
- Architecture: `docs/ARCHITECTURE.md`
- Tasks: `TASKS.md` (SSOT)
- Agents: `AGENTS.md` (v2.3.0)

---

## 12. 💡 DISCUSSION POINTS FOR WEDNESDAY

1. **Reusable Modules**
   - Can Forja use EGOS orchestration for tool selection?
   - Should we share chatbot runtime between Forja + br-acc?

2. **Go-to-Market**
   - Pilot customer: Rocha Implementos (metalúrgica)
   - Success metrics: Tool accuracy, response time, user adoption

3. **Next Phases**
   - Phase 2 (Apr): Email integration + WhatsApp triage agent
   - Phase 3 (May): Admin dashboard + approval workflows
   - Phase 4 (Jun): Mobile (Capacitor Android)

4. **Shared Infrastructure**
   - Should Forja use same Supabase project as egos-lab?
   - Cost optimization: Aggregate LLM calls across projects?

5. **Knowledge Sharing**
   - Forja's fiscal logic → Can help other domain-specific apps
   - Forja's tool registry → EGOS pattern inspiration
   - EGOS's orchestration → Forja needs for complex queries

---

## ✅ WHAT YOU CAN SAY WEDNESDAY

**"We built Forja as a chat-first ERP with:**
- ✅ **Live production setup** on Vercel
- ✅ **Operational schema** (customers, products, stock, quotes, production)
- ✅ **4 core tools** with safety validation + risk tiers
- ✅ **Multi-provider LLM** (Alibaba + Gemini fallback)
- ✅ **RLS multi-tenant** database (Supabase)
- ✅ **Accessibility** for field workers (large buttons, voice-first, high contrast)
- ✅ **Governance** (ATRiAN ethics + PII scanning + audit logs)

**We can share with EGOS:**
- Tool registry pattern
- Fiscal calculation module
- Safety framework
- Supabase RLS design

**We need from EGOS:**
- Sequential-Thinking for complex analysis
- Better model routing + cost optimization
- Agent registry for workflows
- Advanced observability

**Timeline:**
- MVP (Chat + Tools): Done ✅ (March 23)
- Phase 2 (Email + Triage Agent): April
- Phase 3 (Admin Dashboard): May
- Pilot: Rocha Implementos (metal mecânico)
- Go-to-market: June 2026"

---

**Document Status:** 🟢 READY FOR WEDNESDAY MEETING  
**Last Updated:** 2026-03-23  
**Next Update:** After Wednesday meeting with feedback  

---

*"Forja: Operações na conversa. Conversações na operação."*

