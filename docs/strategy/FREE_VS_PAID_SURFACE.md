# EGOS Guard Brasil — Free vs Paid Surface Definition

> **SSOT Owner:** `egos/docs/strategy/FREE_VS_PAID_SURFACE.md`
> **Version:** 1.0.0 | **Updated:** 2026-03-29
> **Status:** ACTIVE — defines monetization boundary
> **Parent:** [FLAGSHIP_BRIEF.md](./FLAGSHIP_BRIEF.md)

---

## Principle

Open-source the engine. Charge for the infrastructure, policy, and accountability layers that enterprises need but individual developers don't.

---

## Free Tier: `@egos/guard-brasil` (npm, MIT)

Everything a solo developer or small team needs to add LGPD-compliant guardrails to their AI app.

### What's included

| Module | Capability | Limit |
|---|---|---|
| **ATRiAN** | Ethical validation (absolute claims, fabricated data, false promises, blocked entities) | Unlimited local usage |
| **PII Scanner BR** | Detect CPF, RG, MASP, REDS, processo, placa, phone, email, nome, data nasc. | All 10 categories |
| **Public Guard** | Mask/redact/block sensitive output + LGPD disclosure footer | Full feature set |
| **Evidence Chain** | Build traceable claims with audit hash | Full feature set |
| **GuardBrasil facade** | `guard.inspect(text)` — one-call API composing all layers | Full feature set |

### What's NOT included in free

- No hosted API (must run locally or self-host)
- No persistence (evidence chains are in-memory, caller must store)
- No dashboard (caller must build their own visualization)
- No custom policy packs (only default rules)
- No SLA or support

### Distribution

- **npm:** `@egos/guard-brasil`
- **License:** MIT
- **Runtime:** TypeScript/ESM, zero external dependencies
- **Install:** `npm install @egos/guard-brasil`

---

## Paid Tier 1: Guard Brasil API (SaaS)

> **Target:** Teams that want guardrails without running infrastructure.
> **Pricing model:** Usage-based (per-inspection) + monthly base

### What's included

| Feature | Description |
|---|---|
| **Hosted REST API** | `POST /v1/inspect` — same as local `guard.inspect()` but hosted, load-balanced, monitored |
| **MCP Server** | Claude/Windsurf/Cursor integration via Model Context Protocol |
| **Persistence** | Evidence chains stored in managed Supabase — query by session, date, category |
| **Webhook alerts** | Notify on critical PII detection, ATRiAN score < threshold, blocked outputs |
| **Rate limiting** | Managed rate limits with burst capacity |
| **99.5% SLA** | Uptime guarantee for production workloads |

### Pricing (proposed)

| Plan | Inspections/month | Price | Notes |
|---|---|---|---|
| Starter | 5,000 | R$ 99/mo | Solo devs, small apps |
| Pro | 50,000 | R$ 499/mo | Teams, multi-app |
| Enterprise | Unlimited | Custom | Dedicated instance, custom SLA |

### Tech stack

- **Runtime:** Hetzner VPS (204.168.217.125) + Docker
- **API:** Node.js/Bun + Express or Hono
- **Storage:** Supabase (evidence chains, audit logs, usage metrics)
- **Auth:** API key per customer
- **Monitoring:** Telemetry system (`telemetry.ts`) → Supabase dashboard

---

## Paid Tier 2: Audit Dashboard (SaaS add-on)

> **Target:** DPOs, compliance teams, managers who need visibility.
> **Pricing model:** Included in Pro+, standalone for Starter

### What's included

| Feature | Description |
|---|---|
| **Inspection timeline** | Visual timeline of all inspections, filterable by date/category/severity |
| **PII heatmap** | Which PII categories appear most, trending over time |
| **ATRiAN score trends** | Score distribution, violation breakdown, improvement tracking |
| **Evidence explorer** | Browse sealed evidence chains with audit hash verification |
| **Export** | PDF/CSV reports for compliance audits |
| **Team views** | Per-app, per-team, per-environment breakdown |

### Pricing

- Included in Pro and Enterprise plans
- Standalone for Starter: R$ 149/mo add-on

---

## Paid Tier 3: Enterprise Policy Packs

> **Target:** Regulated industries needing sector-specific rules.
> **Pricing model:** Per-pack annual license

### Planned packs

| Pack | Sector | Rules | Price |
|---|---|---|---|
| **Segurança Pública** | Police, investigations | REDS patterns, depoimento PII, investigação terms, chain-of-custody evidence | R$ 2.990/ano |
| **Saúde** | Hospitals, clinics | CRM, prontuário, CID patterns, medical privacy (Lei 13.787/2018) | R$ 2.990/ano |
| **Judiciário** | Courts, legal | OAB, número de processo CNJ, segredo de justiça, intimação patterns | R$ 2.990/ano |
| **Financeiro** | Banks, fintens | Conta, agência, PIX key, Bacen patterns, sigilo bancário | R$ 2.990/ano |

### What a policy pack includes

- Sector-specific PII patterns (added to scanner)
- Sector-specific ATRiAN rules (domain vocabulary, false promise patterns)
- Compliance mapping document (LGPD article references per check)
- Integration guide for the sector's typical stack

---

## Paid Tier 4: Integration Support

> **Target:** Enterprises that need hands-on help.

| Service | Description | Price |
|---|---|---|
| **Onboarding** | 4h guided integration into customer's stack | R$ 4.990 one-time |
| **Custom rules** | Build customer-specific ATRiAN rules + PII patterns | R$ 9.990 one-time |
| **SLA Premium** | 99.9% uptime + 1h response time + dedicated Slack | R$ 1.990/mo |

---

## Revenue Path

```
Month 1-3:  npm publish (free) → github stars → developer adoption
Month 3-6:  Launch API (Tier 1 Starter) → first paid customers
Month 6-9:  Audit Dashboard (Tier 2) → DPO/compliance buyers
Month 9-12: First Policy Pack (Segurança Pública) → sector expansion
```

### Year 1 target (conservative)

| Source | Customers | MRR |
|---|---|---|
| API Starter | 20 | R$ 1.980 |
| API Pro | 5 | R$ 2.495 |
| Dashboard add-on | 10 | R$ 1.490 |
| Policy Packs | 3 | R$ 747 (amortized) |
| **Total** | **38** | **R$ 6.712/mo** |

---

## Implementation Priority

1. **Now:** Publish `@egos/guard-brasil` to npm (free tier — EGOS-064)
2. **Next:** Build `apps/api/` — minimal REST API wrapping GuardBrasil (Tier 1 MVP)
3. **Then:** Wire Supabase persistence for evidence chains (Tier 1 + Tier 2 foundation)
4. **Later:** Audit Dashboard React app (Tier 2)
5. **Future:** First policy pack (Tier 3 — Segurança Pública, leveraging br-acc domain knowledge)

---

## Decision Record

- **Why usage-based, not seat-based?** AI safety checks scale with traffic, not team size. A 2-person team with high-traffic chatbot needs more inspections than a 20-person team building slowly.
- **Why R$ not USD?** Primary market is Brazil. USD pricing creates friction for govtech procurement.
- **Why MCP?** AI-native developers (Claude Code, Windsurf, Cursor) are the early adopters. MCP is the lowest-friction integration for them.
- **Why not freemium API?** Free API attracts abuse and costs infrastructure. The SDK is free. The API is the service boundary.
