# Handoff — P19 Continued: Guard Brasil Monetization + Eagle Eye Pipeline
**Date:** 2026-04-03 ~10:30 BRT  
**Agent:** Claude Opus 4.6 (claude-code)  
**Session:** P19 continued (context recovery from compaction)  
**Repos:** egos (7 commits), egos-lab (2 commits)

---

## Accomplished

### Guard Brasil v0.2.2 — Full Monetization Stack Live
- **VPS Deploy Fixed** — Container was crashing on missing `packages/shared/src/billing/pricing.ts`. Added to [Dockerfile](apps/api/Dockerfile). Rebuilt and restarted via docker-compose with new [.env.docker](apps/api/docker-compose.prod.yml) pattern (env_file instead of environment substitution)
- **API v0.2.2 live** at `https://guard.egos.ia.br`:
  - `GET /v1/meta` — returns pricing tiers, capabilities, endpoints
  - `GET /openapi.json` — full OpenAPI 3.0 spec (4 endpoints)
  - `GET /llms.txt` — AI agent discovery file (text/plain)
  - `POST /v1/inspect` — returns inspection receipt with SHA256 hash chain + provenance
- **Caddy routing updated** — `/openapi.json`, `/llms.txt`, `/health`, `/v1/*` → API container; everything else → Vercel (guard-brasil-web). Config lives in container at `/tmp/Caddyfile` (reloaded via `caddy reload --config /tmp/Caddyfile`)
- **npm published**: `@egosbr/guard-brasil@0.2.2` ([server.ts](apps/api/src/server.ts), [guard.ts](packages/guard-brasil/src/guard.ts), [pricing.ts](packages/shared/src/billing/pricing.ts))

### Stripe Metered Billing — Live Production
- **Product**: `prod_UGevJnAti8JxS5` (Guard Brasil API)
- **Billing Meter**: `mtr_61URVa0BkHwshB0td41HdOnphplrgHQG` (event: `guard_brasil_api_call`)
- **4 Metered Prices** (BRL):
  - Developer: `price_1TI7coHdOnphplrgwv7eWNK2` (R$0.01/call)
  - Startup: `price_1TI7cpHdOnphplrg1QXf5Juw` (R$0.01/call — should be R$0.007, needs tiered)
  - Business: `price_1TI7cqHdOnphplrg2HguEqS4` (R$0.00/call — needs tiered pricing)
  - Enterprise: `price_1TI7crHdOnphplrgB9VUa733` (R$0.00/call — needs tiered pricing)
- **Webhook**: `we_1TI7drHdOnphplrgzqers7Zz` → `guard.egos.ia.br/v1/stripe/webhook` (subscription.created/updated/deleted, invoice.payment_succeeded/failed)
- **Checkout tested**: `POST /v1/stripe/checkout {"tier":"developer","email":"..."}` → returns Stripe Checkout URL ✅
- **Old products archived**: `prod_UGFX7E7L6uM6Ck`, `prod_UGFXnHYMMOrIg5`

### Eagle Eye — Core Pipeline Built (egos-lab)
- **EAGLE-GH-002**: [`document-parser.ts`](../../../egos-lab/apps/eagle-eye/src/modules/licitacoes/document-parser.ts) — regex+LLM hybrid. Extracts: objeto, valor, modalidade, segmento, porte, esfera, prazo, habilitação, ME/EPP, SRP. 78% confidence (regex), 88% (LLM)
- **EAGLE-GH-005**: [`insight-generator.ts`](../../../egos-lab/apps/eagle-eye/src/modules/licitacoes/insight-generator.ts) — BID/INVESTIGATE/SKIP decision + action items + risks + competitive angle + revenue estimate. LLM + rule-based fallback
- **Types updated**: Added `CHAMAMENTO_PUBLICO` and `CONCURSO` to `LicitacaoModalidade`

### Infrastructure
- **TASKS.md compressed**: 525 → 462 lines. LEAK-001..009, AI-001..007, OBS-001..004, P19 completed tasks all summarized to 1-line each
- **Pricing tiers finalized**: Free (500/mo) → Developer R$0.01 → Pro R$0.007 → Business R$0.004 → Enterprise R$0.002/call

---

## In Progress (0%)
- **Stripe Meter Event Emission**: The `/v1/inspect` handler doesn't yet emit `guard_brasil_api_call` events to the Stripe Billing Meter. This is required for actual usage billing to work. ~30min task.

## Blocked
- **Stripe tiered pricing**: The startup/business/enterprise prices were created with incorrect unit_amounts (0 centavos for business/enterprise). Need to either: (a) archive and recreate with correct amounts, or (b) use Stripe's graduated tiered pricing instead of per_unit. The developer tier (1 centavo = R$0.01) is correct.

---

## Next Steps (Ordered by Priority)

### P0 — Revenue Critical
1. **Wire Meter Events into /v1/inspect** — After each successful inspection, emit `guard_brasil_api_call` event via `POST https://api.stripe.com/v1/billing/meter_events` with customer identifier + timestamp. This makes billing actually work.
2. **Fix Stripe Prices** — Archive `price_1TI7cq...` (business) and `price_1TI7cr...` (enterprise) which have 0 centavo unit_amount. Recreate with correct amounts: business=0.4 centavos (need tiered), enterprise=0.2 centavos (need tiered). Consider graduated pricing.
3. **Frontend Checkout** — guard-brasil-web landing page needs a "Get Started" button that calls `/v1/stripe/checkout` with tier selection

### P1 — Product
4. **EAGLE-GH-003/004**: classification-service + extraction-service (thin wrappers over document-parser, may skip if scoring already works)
5. **HERMES-001**: Wire Hermes-3 as BRAID mechanical executor (OpenRouter free tier)
6. **Guard Brasil usage dashboard**: `GET /api/admin/cost-dashboard` exists but needs Supabase wiring to show real call counts per tenant

### P2 — Infrastructure
7. **VPS Caddy Sync**: The container's Caddyfile (`/tmp/Caddyfile` in infra-caddy-1) is different from host's `/opt/bracc/infra/Caddyfile`. Need to sync or establish SSOT
8. **THEATER-001**: Deploy x-reply-bot or remove from done status
9. **CTX-001/002**: Context recovery hook + codebase-memory-mcp warm-up

---

## Environment State

| System | Status |
|--------|--------|
| `guard.egos.ia.br/health` | ✅ v0.2.2 healthy |
| `guard.egos.ia.br/v1/meta` | ✅ 5 tiers, usage-based |
| `guard.egos.ia.br/openapi.json` | ✅ 4 paths |
| `guard.egos.ia.br/llms.txt` | ✅ text/plain |
| Stripe Checkout | ✅ all 4 tiers create sessions |
| Stripe Webhook | ✅ registered, untested (no real payments yet) |
| npm @egosbr/guard-brasil | ✅ v0.2.2 published |
| Eagle Eye scoring-service | ✅ 5-axis scorer (egos-lab) |
| Eagle Eye document-parser | ✅ regex+LLM hybrid (egos-lab) |
| Eagle Eye insight-generator | ✅ BID/INVESTIGATE/SKIP (egos-lab) |
| egos `bun test` | ✅ 188+ tests passing |
| egos-lab pre-commit | ✅ gitleaks + SSOT + security scan |

---

## Key Files Modified This Session

### egos (7 commits)
- `apps/api/src/server.ts` — OpenAPI, llms.txt, Stripe checkout multi-tier, API_VERSION=0.2.2
- `apps/api/Dockerfile` — Added `COPY packages/shared/src/`
- `apps/api/docker-compose.prod.yml` — env_file pattern, metered price IDs
- `packages/guard-brasil/package.json` — v0.2.2
- `packages/guard-brasil/src/guard.ts` — GUARD_VERSION 0.2.1
- `packages/shared/src/billing/pricing.ts` — 5 usage tiers (free→enterprise)
- `TASKS.md` — compressed to 462 lines, marked EAGLE-GH-002/005 done

### egos-lab (2 commits)
- `apps/eagle-eye/src/modules/licitacoes/document-parser.ts` — NEW (EAGLE-GH-002)
- `apps/eagle-eye/src/modules/licitacoes/insight-generator.ts` — NEW (EAGLE-GH-005)
- `apps/eagle-eye/src/modules/licitacoes/index.ts` — exports updated
- `apps/eagle-eye/src/types.ts` — CHAMAMENTO_PUBLICO, CONCURSO added

### VPS (204.168.217.125)
- `/opt/apps/guard-brasil/.env.docker` — all Stripe keys + meter + price IDs
- `/opt/apps/guard-brasil/apps/api/docker-compose.prod.yml` — env_file pattern
- Caddy: `/openapi.json` and `/llms.txt` routes added to guard.egos.ia.br block (in container's `/tmp/Caddyfile`)

---

## Credentials & IDs Reference (for next agent)

| Key | Value (truncated) | Location |
|-----|-------------------|----------|
| Stripe Secret Key | `sk_live_51Rm3wP...my7J` | VPS `.env.docker` |
| Stripe Publishable | `pk_live_51Rm3wP...VbZ` | VPS `.env.docker` |
| Stripe Product | `prod_UGevJnAti8JxS5` | Stripe Dashboard |
| Stripe Meter | `mtr_61URVa0BkHwshB...` | VPS `.env.docker` |
| Stripe Webhook Secret | `whsec_O4coKrpOE0N...` | VPS `.env.docker` |
| Guard API Key (env) | `9e573724-8f4f-...` | VPS `.env.docker` |
| npm token | expires ~2026-04-07 | `~/.npmrc` |

---

*Signed by: claude-code (Opus 4.6) — 2026-04-03T13:30:00Z*
