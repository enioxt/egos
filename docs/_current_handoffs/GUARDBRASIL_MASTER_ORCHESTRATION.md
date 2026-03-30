# Guard Brasil Master Orchestration — Visão Completa

> **Criado:** 2026-03-30 | **Status:** READY FOR EXECUTION | **Total Effort:** ~40h spread over 3 weeks

---

## 🎯 O PROBLEMA QUE ESTAMOS RESOLVENDO

**Situação:**
- Temos Guard Brasil API LIVE em guard.egos.ia.br (4ms latência, 100 req/min)
- Temos R$650+/mo em custos de infraestrutura (VPS Hetzner)
- Temos ZERO clientes pagantes
- Temos M-007 como bloqueador único (emails não foram enviados)

**Solução:** Criar um GTM that works WITHOUT upfront sales engineering
- Produto pode ser testado GRÁTIS com 100 testes/dia
- Custos reais de LLM: <R$1/mês mesmo com 10x traffic
- Distribuição via X.com (rede gratuita, já temos credenciais)
- Dashboard ao vivo mostra "social proof" para próximos clientes
- Depois de provar conceito, enviamos M-007 emails com case studies reais

---

## 📊 Stack Completo — O que vamos ter em 18 dias

### Layer 1: User-Facing (Customer touchpoints)

| Component | URL | Tech | Propósito |
|-----------|-----|------|-----------|
| **Landing Page** | guard.esos.ia.br | Next.js + TailwindCSS | Teach + let users test |
| **Public Dashboard** | guard.egos.ia.br/dashboard | Next.js + Supabase Realtime | Social proof (see live activity) |
| **Customer Dashboard** | guard.egos.ia.br/dashboard?key=... | Next.js + Auth | Customer-specific metrics |
| **X.com Bot** | @anoineim | Twitter API v2 | 1 post/day showing use cases |

### Layer 2: Core API (Existing, no changes)

| Component | URL | Tech | Propósito |
|-----------|-----|------|-----------|
| **Guard Brasil REST API** | guard.egos.ia.br/v1/inspect | Bun HTTP + TypeScript | Process inspections |
| **LLM Router** | internal | Qwen (primary) + Gemini (fallback) | Auto-select best model |
| **Rate Limiter** | internal | Token bucket | 10 req/min per IP, 100/day quota |

### Layer 3: Observability (NEW — SSOT)

| Component | Table | Tech | Propósito |
|-----------|-------|------|-----------|
| **Telemetry Recorder** | guard_brasil_events | @egos/shared + Supabase | Log every request |
| **Metrics Aggregation** | (SQL views) | Supabase SQL | Cost rollups, provider stats |
| **AI Insights** | (generated daily) | Qwen-plus | Daily summary: "You had 500 calls, avg 200ms, saved $0.50" |

### Layer 4: Infrastructure (Existing + enhanced)

| Component | Provider | Purpose |
|-----------|----------|---------|
| **VPS Bun Server** | Hetzner 204.168.217.125 | Guard API + rate limiter |
| **Database** | Supabase PostgreSQL | Telemetry + customer data |
| **DNS** | Registro.br | guard.egos.ia.br A record |
| **TLS** | Caddy (auto Let's Encrypt) | HTTPS on Hetzner |

---

## 💰 Cost Analysis — Complete Picture

### Infrastructure Monthly Costs

```
Hetzner VPS (current):           R$ 650
Supabase (telemetry storage):    FREE (< 1GB/month)
DNS (Registro.br):               R$ 20/year
Vercel (landing + dashboard):    FREE (1.2k/month in free tier)
                                 ─────────
TOTAL:                          R$ 650/month
```

### Variable Costs Per Customer (Revenue Model)

```
Customer in STARTER tier (R$0.02/call):
- Typical usage: 5,000 calls/mo = R$ 100/mo

LLM Costs (60% regex, 30% Qwen, 10% Gemini):
- Qwen-plus: 1,500 calls × $0.00007 = $0.105
- Gemini: 500 calls × $0.00003 = $0.015
- Regex: 3,000 calls = $0
- Total LLM cost: ~$0.12 ≈ R$ 0.60/month
  (Company takes: R$ 100 - R$ 0.60 ≈ R$ 99.40 profit/customer)

Customer in PRO tier (R$ 299/mo):
- Unlimited calls, advanced features
- LLM costs: same $0.12-5 depending on usage
- Company takes: R$ 299 - (LLM + support) = ~R$ 290 profit
```

### Break-Even Analysis

```
Month 1: R$ 0 revenue, R$ 650 burn
Month 2: 5 customers × R$ 100 = R$ 500 revenue, loss: R$ 150
Month 3: 15 customers × R$ 100 = R$ 1,500, +R$ 850 profit
Month 4: 30 customers × R$ 100 = R$ 3,000, +R$ 2,350 profit

✅ BREAK-EVEN: Month 2 (June 2026)
✅ PROFIT: Month 3 onwards

Note: These are CONSERVATIVE. Our transparency + X.com could viral faster.
```

---

## 🚀 Execution Roadmap — What To Do TODAY

### IMMEDIATELY (Next 2 hours)

1. **Commit the documentation** (3 files created)
   ```bash
   git add docs/TELEMETRY_SSOT.md \
           docs/_current_handoffs/GUARDBRASIL_GTM_EXECUTIONPLAN.md \
           docs/_current_handoffs/GUARDBRASIL_MASTER_ORCHESTRATION.md
   git commit -m "docs: Guard Brasil GTM master plan — full stack, 18-day timeline, cost analysis"
   ```

2. **Create directory structure** (10 min)
   ```bash
   cd /home/enio/egos/apps
   npx create-next-app guard-brasil-web --typescript --tailwind --eslint
   npx create-next-app guard-brasil-dashboard --typescript --tailwind --eslint
   ```

3. **Create Supabase table** (5 min)
   ```sql
   -- Run in Supabase SQL editor
   -- Copy the CREATE TABLE from GUARDBRASIL_GTM_EXECUTIONPLAN.md
   ```

### DAY 1-2 (Tomorrow & Thursday)

**Priority:** Landing Page + Form (6h of focused work)

```bash
# Copy components from execution plan into:
# apps/guard-brasil-web/components/
# apps/guard-brasil-web/app/page.tsx
# apps/guard-brasil-web/app/api/test/route.ts

# Test locally
cd /home/enio/egos/apps/guard-brasil-web
bun run dev  # http://localhost:3000

# Fill in examples, test rate limiting
# Test calls to guard.egos.ia.br/v1/inspect
```

**Success:** Can paste "CPF 123.456.789-00" and get back masked version + cost

### DAY 3 (Friday)

**Priority:** Telemetry Integration (4h)

```bash
# 1. Create migration in Supabase
# 2. Update Guard Brasil API (/v1/inspect) to call:
#    await guardBrasilTelemetry.recordEvent({...})
# 3. Verify events appear in guard_brasil_events table

# Test: Make 10 API calls, see 10 rows in DB with cost_usd filled
```

### DAY 4-5 (Next week Mon-Tue)

**Priority:** X.com Bot + First Post (4h)

```bash
# 1. Create agents/agents/x-guardbrasil-bot.ts
# 2. Test locally: bun agents/agents/x-guardbrasil-bot.ts
# 3. Post manually: npx ts-node x-guardbrasil-bot.ts
# 4. Set up GitHub Actions workflow (copy from execution plan)

# Success: Post appears on @anoineim at scheduled time
```

### WEEK 2 (Apr 6-12)

**Parallel tracks:**

1. **Dashboard MVP** (8h)
   - Public page showing live activity
   - Basic chart showing cost/provider breakdown
   - Auth page (API key login)

2. **M-007 Execution** (5h actual email work)
   - Use landing page stats as proof: "X people tested, X from X.com"
   - Send 5 emails with case studies
   - Track responses

3. **Handle Responses** (2h)
   - Demo calls with GUARD_BRASIL_DEMO_SCRIPT.md
   - Collect feedback

### WEEK 3 (Apr 13-20)

1. **Customer Dashboard Hardening** (3h)
   - Performance optimization
   - Better error handling
   - Mobile responsiveness

2. **Pilot Customer Onboarding** (4h)
   - Setup Starter customers in DB
   - Configure quotas
   - Provide API keys

3. **Production Validation** (2h)
   - Stress test: 1,000 req/day
   - Monitor latency, error rates
   - Check Supabase costs at scale

---

## 🤔 Critical Decisions (Make These NOW)

### Decision 1: Free Tier Limits

**Option A:** 100 tests/day per IP (current plan)
- Pro: Easy to explain, fair
- Con: Power users frustrated quickly
- Recommendation: ✅ GO WITH THIS

**Option B:** 1,000 tests/day per IP
- Pro: More generous
- Con: Still negligible cost, but requires more DDoS protection
- Recommendation: Consider for viral moment (Week 2+)

**Decision 2: Customer Tiers**

**Proposed:**
- FREE: npm SDK, no telemetry, local only
- STARTER: R$0.02/call, API, basic dashboard (our revenue driver)
- PRO: R$299/mo unlimited, advanced insights, team seats
- ENTERPRISE: Custom SLA

**Question for you:** OK with this 3-tier? Or want different pricing?

### Decision 3: Data Retention

**Proposed:** 1-year retention in Supabase (enough for compliance)

**Question:** After 1 year, archive to S3 or delete?

---

## 📋 Dependencies & Blockers

### No blockers! ✅

- API is already live
- X.com credentials are ready
- Supabase is configured
- Telemetry pattern exists (@egos/shared)
- Hetzner is stable

**Only requirement:** Execute the 3-week plan

---

## 🎬 Next Action

**RIGHT NOW (next 30 min):**

1. Commit the 3 docs I created
2. Create the app directories
3. Create the Supabase table
4. Tomorrow: Start on landing page

**Don't overthink it.** The plan is solid. The money works. The tech is proven.

The ONLY variable is: **Do you execute M-007 (emails) after social proof is built?**

---

## 📈 Success Indicators (By Week)

| Week | Metric | Target | Track |
|------|--------|--------|-------|
| 1 | Landing page traffic | 50+ visits/day | GA |
| 1 | X.com posts | 1 post/day | Twitter Analytics |
| 1 | API requests | 50+/day from landing | Supabase |
| 2 | M-007 emails sent | 5+ emails | Gmail sent folder |
| 2 | Demo calls booked | 2-3 calls | Calendar |
| 3 | Pilot customers | 1-2 signed | DB query |
| 3 | Revenue | R$ 100-200/mo | Stripe/invoice |

---

## 🔮 Questions for Refinement

**Before you ask me to implement:**

1. **Pricing:** Is R$0.02/call + R$299/mo Pro OK? Or adjust?
2. **Policy Packs:** The 4 tiers (security, health, judicial, financial) — right scope?
3. **Dashboard features:** Priority: Live activity, Cost charts, or AI insights first?
4. **M-007 timing:** Send emails immediately or wait for dashboard launch?
5. **X.com strategy:** Daily posts or 3x/week? Different content each time or rotate 6 examples?

---

**Status:** Ready for execution. No architecture blockers. Budget is positive. Timeline is realistic.

**Last check:** All 3 documents (TELEMETRY_SSOT, EXECUTION_PLAN, MASTER_ORCHESTRATION) make sense?

Next step: YOU execute Landing Page (Tomorrow). I'll wait.
