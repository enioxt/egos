---
name: P19 Continued — Guard Brasil Monetization Complete + Eagle Eye Pipeline
description: VPS deploy fixed, Stripe metered billing live (4 tiers), OpenAPI+llms.txt endpoints, npm@0.2.2, Eagle Eye document-parser + insight-generator
type: project
---

## Session P19 Continued (2026-04-03)

### Guard Brasil v0.2.2 — Full Monetization Stack Live

**VPS Deploy Fix:**
- Container crashed on `packages/shared/src/billing/pricing.ts` missing. Fixed: added `COPY packages/shared/src/ packages/shared/src/` to Dockerfile
- docker-compose updated: `env_file: ../../.env.docker` (clean KEY=VALUE, no `export`)
- Caddy routing: `handle /openapi.json` and `handle /llms.txt` added before catch-all Vercel handler

**New Endpoints (production):**
- `GET /v1/meta` — pricing tiers + capabilities
- `GET /openapi.json` — OpenAPI 3.0 spec (4 endpoints)
- `GET /llms.txt` — AI agent discovery (text/plain)
- `POST /v1/stripe/checkout` — 4 tiers: developer/startup/business/enterprise

**Stripe (LIVE):**
- Product: `prod_UGevJnAti8JxS5` (Guard Brasil API)
- Billing Meter: `mtr_61URVa0BkHwshB0td41HdOnphplrgHQG` (event: `guard_brasil_api_call`)
- Prices: developer=`price_1TI7co...` (R$0.01), startup=`price_1TI7cp...` (R$0.007), business=`price_1TI7cq...` (R$0.004), enterprise=`price_1TI7cr...` (R$0.002)
- Webhook: `we_1TI7drHdOnphplrgzqers7Zz` → `guard.egos.ia.br/v1/stripe/webhook` (5 events)
- Old products archived: `prod_UGFX7E7L6uM6Ck` (Enterprise), `prod_UGFXnHYMMOrIg5` (Pro)

**npm:** `@egosbr/guard-brasil@0.2.2` published

### Eagle Eye Pipeline (egos-lab)

**EAGLE-GH-002: document-parser.ts**
- Regex-based: extracts objeto, valor, modalidade, segmento, porte, esfera, prazo, habilitação
- 78% confidence (regex), 88% (LLM), hybrid mode
- Key fix: Unicode `/iu` flags for Portuguese accents

**EAGLE-GH-005: insight-generator.ts**
- LLM-based + rule-based fallback
- Generates: BID/INVESTIGATE/SKIP decision, action items, risks, competitive angle, estimated revenue
- Input: LicitacaoScore + ParsedEdital → InsightReport

### TASKS.md Compressed
- LEAK-001..009 → 1 summary line
- AI-001..007 → 1 summary line
- OBS-001..004 → 1 summary line
- P19 completed tasks removed (SECURITY-001, TEST-001, EAGLE-EYE-UX-001)
- Current: 462 lines (was 525)

### Next Steps (for next agent)
1. **Stripe Meter Events**: Wire `POST /v1/billing/meter_events` into `/v1/inspect` handler — each API call should emit `guard_brasil_api_call` event
2. **EAGLE-GH-003/004**: classification-service + extraction-service (thin wrappers over document-parser)
3. **HERMES-001**: Wire Hermes-3 as BRAID mechanical executor
4. **Frontend**: Deploy guard-brasil-web with pricing page + Stripe checkout button
5. **VPS Caddy**: Caddyfile in container is stale — sync from host `/opt/bracc/infra/Caddyfile` when restarting
