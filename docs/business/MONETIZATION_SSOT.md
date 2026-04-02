# MONETIZATION SSOT — EGOS Ecosystem
**Version:** 1.0.0 | **Owner:** enioxt | **Updated:** 2026-04-02

> Single source of truth for all pricing, revenue, and payment infrastructure decisions.
> **Update this file.** Do NOT create new pricing docs elsewhere.

---

## 1. Products & Pricing Matrix

| Product | Free Tier | Starter | Growth | Enterprise | Model |
|---------|-----------|---------|--------|------------|-------|
| **Guard Brasil** | 150 calls/mo | R$49/mo (5K calls) | R$199/mo (50K calls) | R$499/mo (unlimited) | Fixed tiers |
| **Eagle Eye** | 3 territories | R$99/mo (10 territories) | R$249/mo (50 territories) | R$499/mo (unlimited) | B2B SaaS |
| **Gem Hunter** | 10 findings/day | R$19.90/mo base | R$49/mo + LLM% | API: % of LLM cost | Percentage |

### Pricing Philosophy per Product

**Guard Brasil** — Fixed tiers (predictable cost for compliance-sensitive customers)
- Target: DPO, CTO, CFO buying monthly budget
- Cost floor: R$0.000175/call → 2000% margin at starter tier
- Validated model: SaaS compliance tooling (TOTVS, Sankhya benchmarks)

**Eagle Eye** — B2B SaaS seats per territory coverage
- Target: Procurement officers, city governments, small municipalities
- Pain: Manual bidding discovery takes 2h/day → Eagle Eye = 5 min
- Pricing anchor: Licitações consultancies charge R$800-1200/mo → we're 4-8x cheaper
- ⚠️ Eagle Eye pricing is PROPOSED (not yet launched). Validate before going live.

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
| Stripe (card/link) | Guard Brasil, Gem Hunter | ✅ Live (pk_live configured) | Stripe |
| Pix | Guard Brasil, Eagle Eye | 🔲 Roadmap | MercadoPago or Juno |
| x402 (M2M) | Gem Hunter API | 🔲 GH-063 roadmap | x402 protocol |
| Bitcoin Lightning | Gem Hunter | 🔲 future experiment | LNBits or Alby |

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
| Eagle Eye | Procurement manager at small municipality (10K-100K pop) | Construction companies bidding regularly | R$3.000/yr |
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
| BIZ-D1 | Eagle Eye pricing — validate R$99-499 range with 3 pilot customers | enioxt | 2026-05-01 |
| BIZ-D2 | Pix provider — MercadoPago vs Juno vs PagSeguro | enioxt | 2026-04-30 |
| BIZ-D3 | Gem Hunter free-tier LLM analysis — include or gate behind paid? | enioxt | 2026-04-15 |
| BIZ-D4 | x402 rollout — Gem Hunter only or all products in Phase 1? | enioxt | 2026-05-15 |

---

## 8. Files Superseded by This SSOT

These files remain as historical reference but THIS file is authoritative:
- `docs/business/FREE_VS_PAID_SURFACE.md` — tier definitions (archived)
- `docs/gem-hunter/GEM_HUNTER_v6_MASTER_PLAN.md` — pricing section
- Memory: `stripe_credentials.md` — credentials location only, not pricing
- Memory: `guardbrasil_transparencia_radical_pattern.md` — GTM pivot reference
