# MONETIZATION SSOT — EGOS Ecosystem
**Version:** 1.0.0 | **Owner:** enioxt | **Updated:** 2026-04-02

> Single source of truth for all pricing, revenue, and payment infrastructure decisions.
> **Update this file.** Do NOT create new pricing docs elsewhere.

---

## 1. Products & Pricing Matrix

| Product | Free Tier | Starter | Growth | Enterprise | Model |
|---------|-----------|---------|--------|------------|-------|
| **Guard Brasil** | 150 calls/mo | R$49/mo (5K calls) | R$199/mo (50K calls) | R$499/mo (unlimited) | Fixed tiers |
| **Eagle Eye** | 50 analyses/mo | 500 analyses/mo (R$49) | 5K analyses/mo (R$149) | Unlimited API + MCP (R$499) | Usage-based |
| **Gem Hunter** | 10 findings/day | R$19.90/mo base | R$49/mo + LLM% | API: % of LLM cost | Percentage |

### Pricing Philosophy per Product

**Guard Brasil** — Fixed tiers (predictable cost for compliance-sensitive customers)
- Target: DPO, CTO, CFO buying monthly budget
- Cost floor: R$0.000175/call → 2000% margin at starter tier
- Validated model: SaaS compliance tooling (TOTVS, Sankhya benchmarks)

**Eagle Eye** — Usage-based decision intelligence (chatbot / API / MCP)
- Model: pay-per-analysis (licitação scoring, opportunity alerts, document parsing)
- Channels: REST API (B2B integrations), MCP tool (Claude Code / AI assistants), Chatbot UI
- Free: 50 analyses/mo — enough for a team to discover 1 real opportunity
- Starter R$49: 500 analyses (~10 opportunities/day fully scored)
- Growth R$149: 5K analyses; Enterprise R$499: unlimited + SLA + white-label
- Pricing anchor: Licitações consultancies charge R$800-1200/mo → Eagle Eye API = 10x cheaper
- ⚠️ Eagle Eye pricing is PROPOSED (v2 — GenHunter spec). Validate BIZ-D1 with 3 pilots.

**Gem Hunter** — Percentage-based (aligns incentives with LLM usage)
- User decision 2026-04-02: Option D + % pricing (x402/Pix/Stripe)
- Formula: `customer_charge = llm_cost_usd × 1.5 + base_fee_usd`
- 50% margin on LLM pass-through + fixed base ($0.30/hunt API call)
- Free: 10 findings/day (no LLM deep analysis)

---

## 2. Free Tier Philosophy

**Rule:** Free tier must demonstrate value, not give away the product.

| Product | Free Limit | Why This Number |
|---------|-----------|-----------------|
| Guard Brasil | 150 calls/mo | ~1 dev integration test cycle |
| Eagle Eye | 3 territories | Enough to see the map, not enough to run a business |
| Gem Hunter | 10 findings/day | 1 discovery session; no LLM analysis |

**Standard:** All free tiers expire after 90 days inactivity → convert to freemium prompt.

---

## 3. Payment Infrastructure

| Method | Products | Status | Provider |
|--------|----------|--------|----------|
| Stripe (card/link) | All products | ✅ Live (pk_live configured) | Stripe |
| Pix (via Stripe) | All products | 🔲 BIZ-D2 — enable Stripe Pix (Brazil) | Stripe (native Pix support) |
| x402 (M2M) | Gem Hunter API | 🔲 GH-063 roadmap | x402 protocol |
| Bitcoin Lightning | Gem Hunter | 🔲 future experiment | LNBits or Alby |

**Stripe-unified strategy:** Stripe supports Pix natively in Brazil (PM type `pix`). No second provider needed.
Implement once in `packages/shared/src/billing/` — covers card + Pix + Apple/Google Pay.

**Single payment SSOT:** Use `packages/shared/src/billing/` for all payment logic.
Never implement payment code outside this package.

---

## 4. Cost Model (LLM + Infrastructure)

### Guard Brasil
| Component | Cost/call | Volume for breakeven |
|-----------|-----------|---------------------|
| LLM (PII scan) | $0.000050 | — |
| PostgreSQL/Supabase | $0.000025 | — |
| **Total** | **$0.000175** | 285 paid calls = $0.05 → covers Supabase free tier |

### Gem Hunter (per hunt run)
| Component | Cost/run | Notes |
|-----------|---------|-------|
| arXiv + GitHub + HN | $0.00 | Free APIs |
| Exa (10 queries) | $0.05 | $5/100 queries |
| LLM triage (5 papers × 1K tokens) | $0.0004 | Gemini Flash |
| LLM scaffold (3 papers × 3K tokens) | $0.0009 | Gemini Flash |
| **Total** | **~$0.06/run** | At 50% margin: charge $0.09/run |

### Eagle Eye
| Component | Cost/mo | Notes |
|-----------|---------|-------|
| Supabase storage (80+ territories) | ~$0 | Free tier |
| AI scanning (Gemini Flash) | ~$4.23/mo | Current demo estimate |
| VPS share | ~$3/mo | Proportional Hetzner |
| **Total** | **~$7/mo** | R$99 starter = 1300% margin |

---

## 5. ICP (Ideal Customer Profile)

| Product | Primary ICP | Secondary ICP | ACV Target |
|---------|-------------|--------------|------------|
| Guard Brasil | DPO at mid-corp (50-500 employees) | Fintechs, healthtechs with LGPD compliance obligations | R$2.400/yr |
| Eagle Eye | Head of procurement / compliance at SME bidding regularly | AI builders who want licitações as MCP tool in Claude | R$1.800/yr |
| Gem Hunter | Staff engineer at AI startup | Independent researcher / crypto investor | R$600/yr |

**Combined ICP Overlap:** CTO at Brazilian tech startup (buys Guard Brasil + Gem Hunter together).

---

## 6. Revenue Targets

| Product | Month 1 | Month 3 | Month 6 | Year 1 |
|---------|---------|---------|---------|--------|
| Guard Brasil | R$500 | R$2.000 | R$5.000 | R$24.000 |
| Eagle Eye | R$0 | R$300 | R$1.500 | R$9.000 |
| Gem Hunter | R$100 | R$500 | R$2.000 | R$12.000 |
| **Total** | **R$600** | **R$2.800** | **R$8.500** | **R$45.000** |

---

## 7. Open Decisions (need resolution)

| # | Decision | Owner | Deadline |
|---|----------|-------|----------|
| BIZ-D1 | Eagle Eye pricing — validate usage-based R$49/149/499 with 3 pilot customers | enioxt | 2026-05-01 |
| BIZ-D2 | Enable Stripe Pix (native Brazil PM) — test checkout flow end-to-end | enioxt | 2026-04-20 |
| BIZ-D3 | Gem Hunter free-tier LLM analysis — include or gate behind paid? | enioxt | 2026-04-15 |
| BIZ-D4 | x402 rollout — Gem Hunter only or all products in Phase 1? | enioxt | 2026-05-15 |

---

## 8. Files Superseded by This SSOT

These files remain as historical reference but THIS file is authoritative:
- `docs/business/FREE_VS_PAID_SURFACE.md` — tier definitions (archived)
- `docs/gem-hunter/GEM_HUNTER_v6_MASTER_PLAN.md` — pricing section
- Memory: `stripe_credentials.md` — credentials location only, not pricing
- Memory: `guardbrasil_transparencia_radical_pattern.md` — GTM pivot reference
