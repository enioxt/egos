# EGOS Flagship Brief — EGOS-093

> **VERSION:** 1.0.0 | **DATE:** 2026-03-29
> **PURPOSE:** Canonical flagship definition in SSOT. One place, one truth.

## Objective

Establish **Guard Brasil** as the flagship product of the EGOS ecosystem —
a composable AI safety layer for Brazilian systems that validates outputs,
masks PII, and traces provenance.

## Problem Statement

Brazilian AI teams deploying chatbots, copilots, and agent systems face:

1. **LGPD compliance gap** — No native tooling for CPF/CNPJ/RG detection in AI outputs
2. **Hallucination leakage** — LLMs make absolute claims, fabricate data, promise actions they can't fulfill
3. **No audit trail** — Can't trace which AI said what, based on what evidence
4. **Manual governance** — Compliance is paperwork, not code; drifts immediately

## Solution: Guard Brasil

A single `validate()` call that runs 4 safety checks:

| Check | What it catches | Evidence |
|-------|----------------|----------|
| **ATRiAN** | Absolute claims, fabricated data, false promises, blocked entities | 16 tests |
| **PII Scanner** | CPF, CNPJ, RG, email, phone, vehicle plates | 14 tests |
| **Public Guard** | Unmasked sensitive data in public output | 16 tests |
| **Evidence Chain** | Claims without traceable source | 17 tests |

**Combined:** 72 tests, 0 failures.

## Target Personas

| Persona | Size | Pain | Willingness to Pay |
|---------|------|------|-------------------|
| **BR AI Startups** (chatbots, copilots) | 500+ companies | LGPD compliance manual | R$500-2.000/mês |
| **GovTech** (public sector AI) | 50+ agencies | Audit trail mandatory | R$5.000-20.000 setup |
| **Fintechs** (AI in financial) | 200+ companies | PII leak = fine | R$2.000-5.000/mês |
| **Law firms** (AI assistants) | Growing | Hallucination liability | R$1.000-3.000/mês |

## GTM Strategy

**Phase 1 — Prove (current):**
- Open-source SDK on npm (MIT)
- 166 tests as proof of quality
- `bun demo` for live demonstrations
- `bun benchmark` showing 50/60 vs competitors

**Phase 2 — Adopt:**
- 10 developer interviews (validation)
- 3 case studies (852, carteira-livre, br-acc)
- egos.ia.br with live Guard Brasil playground

**Phase 3 — Monetize:**
- Hosted API (R$500/mês)
- MCP server for IDE integration (R$1.000/mês)
- Enterprise SLA + audit console (R$5.000+ setup)

## Success Metrics

| Metric | 30 days | 90 days | 180 days |
|--------|---------|---------|----------|
| npm downloads | 50+ | 500+ | 2.000+ |
| GitHub stars | 50+ | 200+ | 500+ |
| External adopters | 1 | 5+ | 20+ |
| Paying customers | 0 | 1-3 | 10+ |
| Monthly revenue | R$0 | R$2.500+ | R$15.000+ |

## Differentiators (Only Guard Brasil)

1. Only Brazilian LGPD-native AI safety SDK
2. Only post-response ethical validator (ATRiAN catches lies AFTER generation)
3. Only evidence chain with confidence scoring for AI claims
4. Only framework with pre-commit enforcement (governance-as-code)
5. 166 tests with real Brazilian data (CPF, CNPJ formats)

## Anti-Claims (What We Do NOT Promise)

- ❌ We don't block all hallucinations (we flag common patterns)
- ❌ We don't replace legal LGPD compliance review
- ❌ We don't have blockchain/on-chain analysis
- ❌ We don't have fine-tuned models
- ❌ We don't have external paying customers yet
