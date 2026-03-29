# EGOS Presentation System

> **SSOT Owner:** `egos/docs/PRESENTATION_SYSTEM.md`
> **Version:** 1.0.0 | **Created:** 2026-03-29 | **Status:** ACTIVE
> **Task:** EGOS-116

---

## Core Positioning

### One-Sentence VP
> "We make Brazilian AI assistants safer to ship by adding LGPD-aware guardrails, masking, evidence discipline, and policy enforcement."

### Tagline (15 words max)
> "Brazilian AI safety layer. LGPD-compliant. Evidence-traced. Drop-in SDK."

### Anti-bloat thesis
EGOS is not an agent framework. It is not a philosophy layer. It is not a generic LLM toolkit.
It is a **compliance and safety layer for Brazilian AI deployments** — one product, one audience, one problem.

---

## The Promise

| Dimension | Promise |
|-----------|---------|
| **Privacy** | No CPF, MASP, RG, or REDS will leak from your AI responses |
| **Ethics** | No absolute claims, fabricated citations, or false promises from your assistant |
| **Accountability** | Every claim has a traceable source and an audit hash |
| **Speed** | `npm install @egos/guard-brasil` — integrated in one afternoon |

---

## Evidence (what we can prove)

| Claim | Evidence |
|-------|---------|
| "Detects Brazilian PII" | 15 unit tests covering CPF, RG, MASP, REDS, placa, processo, phone, email passing in `packages/guard-brasil/` |
| "ATRiAN ethical validation works" | Score 0–100 with violation categories tested in `guard.test.ts` |
| "LGPD compliance" | `buildLGPDDisclosure()` generates compliant footer per Lei 13.709/2018 |
| "Evidence chain with audit hash" | `createEvidenceChain().build()` produces immutable SHA-256 audit hash |
| "Production-proven" | br-acc (EGOS-Inteligência) runs guardrails in police/judicial AI context |

---

## Differentiators

| vs | Them | Us |
|----|------|----|
| AWS Comprehend PII | Generic, English-first | MASP, REDS, CASP — Brazilian gov vocab |
| Azure Content Safety | Harmful content only | Compliance + ethics + evidence — governed AI |
| LangChain output parsers | Structure only | LGPD disclosure + audit trails + ATRiAN scoring |
| Open-source regex PII | Static patterns | Combined stack maintained for BR identifiers |
| Generic agent frameworks | Broad / abstract | Narrow / specific / pays-for-itself via compliance |

---

## Anti-Patterns (never say these)

| Don't say | Say instead |
|-----------|------------|
| "We're building an AI ecosystem" | "We make AI safer to ship in Brazil" |
| "Multi-agent orchestration kernel" | "Brazilian AI safety SDK" |
| "Network-state philosophy" | — (don't say anything like this) |
| "Eventually we'll add X" | "Today we do Y. Phase 2 adds Z." |
| "It's like LangChain but..." | "It's LGPD compliance as an SDK" |

---

## Target Surfaces

This positioning should appear consistently in:

| Surface | Status |
|---------|--------|
| `packages/guard-brasil/README.md` | ✅ Updated |
| `docs/strategy/FLAGSHIP_BRIEF.md` | ✅ Canonical |
| npm package description | ⏳ On publish |
| GitHub repo description | Enio to update |
| Landing page `egos.ia.br/guard` | Phase 3 |
| Demo script `scripts/demo-lane.sh` | ✅ Created |

---

## Visual Identity Rules

Minimal, credible, Brazilian-anchored.

| Rule | Detail |
|------|--------|
| Colors | Only in actual UI — docs are black/white/code |
| Language | Portuguese-first for docs aimed at Brazilian devs; English for npm/GitHub |
| Logo | None yet — do not create one without `docs/governance/NEW_PROJECT_GATE.md` approval |
| Code samples | Always runnable — never pseudocode in README |
| Claims | Always backed by evidence — no "enterprise-grade" without proof |

---

*Maintained by: EGOS Kernel*
*Related: EGOS-116, docs/strategy/FLAGSHIP_BRIEF.md, packages/guard-brasil/README.md*
