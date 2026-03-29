# EGOS Guard Brasil — Canonical Flagship Brief

> **SSOT Owner:** `egos/docs/strategy/FLAGSHIP_BRIEF.md`
> **Version:** 1.0.0 | **Last Updated:** 2026-03-29
> **Status:** ACTIVE — primary product focus

---

## One-Sentence Value Proposition

> "We make Brazilian AI assistants safer to ship by adding LGPD-aware guardrails, masking, evidence discipline, and policy enforcement."

---

## Problem Statement

Brazilian organizations — public agencies, hospitals, law enforcement, legal services, banks — are deploying AI assistants (chatbots, copilots, investigation tools) but face critical compliance and trust risks that generic AI safety tools do not address:

1. **LGPD exposure** — LLMs leak CPF, MASP, RG, REDS, process numbers, and names into responses. Generic PII scanners miss Brazilian identifiers entirely.
2. **Hallucination in high-stakes contexts** — AI assistants in police, legal, and health settings make absolute claims, invent data sources ("segundo dados do Ministério..."), and issue false promises of action — with real legal and operational consequences.
3. **No audit trail** — regulatory frameworks (LGPD, ANPD, sector-specific norms) require demonstrable accountability for AI decisions. Most AI products have no structured evidence or traceability layer.
4. **Language and cultural gap** — English-first safety tools miss Portuguese-language patterns, idioms, and the specific bureaucratic vocabulary of Brazilian public administration.

---

## Product: EGOS Guard Brasil

A Brazil-first guardrails SDK/API for AI assistants and public-facing AI systems.

### Core Modules

| Module | What it does | Key capability |
|---|---|---|
| **ATRiAN** | Ethical validation | Scores 0–100, flags absolute claims, fabricated data citations, false promises, blocked entities in PT-BR |
| **PII Scanner BR** | Personal identifier detection | CPF, RG, MASP, REDS, processo, placa, phone, email, nome — Brazilian government identifier vocabulary |
| **Public Guard** | LGPD-compliant masking | Mask or block critical PII, sensitivity classification (low/medium/high/critical), LGPD disclosure footer |
| **Evidence Chain** | Traceable response discipline | Structured claims with sources, confidence levels, audit hashes — every claim provenance-stamped |
| **GuardBrasil facade** | One-call API | `guard.inspect(text)` → `{ safe, output, atrian, masking, evidenceChain, lgpdDisclosure }` |

### Package

- **npm:** `@egos/guard-brasil` (OSS, MIT)
- **Source:** `egos/packages/guard-brasil/`
- **Runtime:** TypeScript/ESM, zero mandatory dependencies beyond `@egos/shared`
- **Tests:** 15 unit tests, 100% pass rate

---

## Target Personas

### Primary: AI Engineer at a Brazilian govtech or enterprise
- Building or integrating AI chatbots for public or regulated services
- Has deadline pressure to ship, limited budget for compliance infrastructure
- Needs a drop-in library that handles the compliance layer so they can focus on the AI feature
- **Job to be done:** "Add LGPD compliance and safety to my LLM app in less than one afternoon"

### Secondary: Data Protection Officer (DPO) or compliance team
- Needs to approve AI deployments in regulated environments
- Wants evidence that PII is not exposed and claims are traceable
- **Job to be done:** "Show me that the AI outputs are auditable and LGPD-compliant before I sign off"

### Tertiary: EGOS-Inteligência / br-acc application team
- Internal users of the stack, proving product-market fit by deploying in production
- **Job to be done:** "Make our investigation assistant safe to run on public-sector data"

---

## Differentiation

| Competitor | What they do | What we do differently |
|---|---|---|
| AWS Comprehend (PII) | Generic PII detection, English-first | Brazilian-specific entities (MASP, REDS, CASP, placa), PT-BR language patterns |
| Azure Content Safety | Harmful content moderation | Governance + ethical validation (ATRiAN) + evidence discipline — not just content harm |
| LangChain output parsers | Structured output | Compliance-oriented, not just structure — LGPD disclosure, audit trails, ATRiAN scoring |
| Open-source regex PII | Static pattern matching | Combined stack: PII + ethics + evidence + masking, maintained for BR identifiers |

**Core moat:** Brazilian government identifier vocabulary + ATRiAN ethical scoring + evidence chain for regulatory accountability — combined in a single composable SDK.

---

## Monetization

### Open Source (free)
- Core SDK: `@egos/guard-brasil` on npm
- Reference implementation and documentation
- ATRiAN rules and PII patterns

### Paid (future)
- **Hosted API / MCP** — no local setup, SLA, high throughput
- **Audit Dashboard** — track all masked events, PII categories, ATRiAN scores over time
- **Enterprise Policy Packs** — sector-specific rules (health, police, judiciary, banking)
- **Deployment hardening + integration support** — guided onboarding and SLA

### Reference Customer Path
- `EGOS-Inteligência` (br-acc) is the first production deployment
- Proves the stack works on real Brazilian public data under LGPD pressure
- Becomes the flagship case study for B2G and B2B sales

---

## Success Metrics

| Metric | Target | Timeframe |
|---|---|---|
| npm installs | 500 / month | 3 months post-publish |
| GitHub stars | 200 | 3 months post-publish |
| Integration PR from external org | 1 | 6 months |
| First paid API customer | 1 | 6 months |
| br-acc production validation | ✅ shipped | This quarter |

---

## What We Are NOT Building

- A generic agent framework (overcrowded category, low WTP without compliance angle)
- A "consciousness" or philosophical AI platform (not a business)
- A civic data pipeline product alone (br-acc moat, but not the sellable layer)
- A monorepo of experiments marketed as a single product

---

## Immediate Next Steps

1. **Publish `@egos/guard-brasil` to npm** — extract from monorepo or publish from workspace
2. **Wire into br-acc** — validate in production on EGOS-Inteligência data
3. **Write integration guide** — "Add LGPD guardrails to your FastAPI + LLM app in 30 minutes"
4. **Ship audit dashboard prototype** — even a basic Supabase-backed log view
5. **Define EGOS-063** — free vs paid surface, pricing model

---

## Related Documents

- [Product Verdict 2026-03](./ECOSYSTEM_PRODUCT_VERDICT_2026-03.md) — strategic context and repo roles
- [Capability Registry](../CAPABILITY_REGISTRY.md) — Guard Brasil capabilities registered
- [TASKS.md](../../TASKS.md) — EGOS-062, 063, 064, 093
- [packages/guard-brasil/README.md](../../packages/guard-brasil/README.md) — technical documentation
