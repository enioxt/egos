# EGOS — Operator Narrative Kit (1-Page)

> **EGOS-117** | **VERSION:** 1.0.0 | **DATE:** 2026-03-29
> **USE:** Pitch deck, meetings, emails, GitHub README header

---

## One-Liner

**EGOS is a governance-first orchestration kernel for AI agents.**
Rules govern agents. Agents enforce rules. Community evolves rules.

## The Problem

AI agent teams (5+ repos, 10+ agents, 3+ LLM providers) drift fast:
- No consistent rules across repos
- Agents hallucinate, leak PII, make false promises
- No audit trail — "who told the agent to do that?"
- Compliance is manual paperwork, not code

## What EGOS Does

| Layer | What | Evidence |
|-------|------|---------|
| **Guard Brasil** | Brazilian AI safety (LGPD masking, ethical validation, traceability) | 72 tests, production in 8 repos |
| **Governance DNA** | `.guarani/` rules propagate to all repos via symlinks | Pre-commit 5 gates, frozen zones |
| **Agent Runtime** | Registry-based execution with audit trail | 10 agents, JSONL logging, dry-run first |
| **Multi-LLM Routing** | Cost-aware model selection (8 models, 10 task types) | qwen-flash FREE → premium escalation |
| **162 Tests** | Behavioral tests for real Brazilian data (CPF, CNPJ, etc.) | 86% module coverage, 0 failures |

## Unique Capabilities (Only EGOS)

1. **Pre-commit rule enforcement** — agents can't bypass governance
2. **Multi-repo symlink propagation** — one `.guarani/`, all repos in sync
3. **Frozen zone protection** — core runtime files can't be hallucinated away
4. **ATRiAN post-response validation** — catches lies AFTER the LLM generates them
5. **Evidence chain** — every AI claim traced to source with confidence scoring

## Guard Brasil — Flagship Product

```typescript
import { createGuardBrasil } from '@egos/shared/guard-brasil';
const guard = createGuardBrasil();
const result = guard.validate(aiOutput);
// result.safe, result.maskedText, result.atrianScore, result.lgpdDisclosure
```

**Free:** SDK (MIT) on npm | **Paid:** Hosted API, MCP server, SLA, audit console

## Numbers That Matter

| Metric | Value |
|--------|-------|
| Shared modules | 14 (TypeScript/Bun) |
| Tests | 162 passing, 372 assertions |
| Agents | 10 registered, all active |
| Repos using governance | 7+ |
| Pre-commit gates | 5 (gitleaks, tsc, frozen, drift, SSOT) |
| LLM models routed | 8 across 2 providers |
| Cost of qwen-flash | $0 (free tier) |

## Live Deployments

- **egos.ia.br** — Main site
- **inteligencia.egos.ia.br** — Public data intelligence (Neo4j graph)
- **852.egos.ia.br** — Institutional chatbot
- **commons.egos.ia.br** — Community platform
- **forja** — CRM chatbot (Vercel)

## Who It's For

| Persona | Pain Point | EGOS Answer |
|---------|-----------|-------------|
| **DevOps** | "Agents keep breaking things" | Pre-commit enforcement |
| **AI Ops** | "5 repos, rules drifting" | Symlink governance sync |
| **Compliance** | "Need audit trail" | Evidence chain + ATRiAN |
| **Founder** | "LLM costs unpredictable" | Cheap-first routing + metrics |

## Contact

- **GitHub:** github.com/enioxt/egos (MIT)
- **Web:** egos.ia.br
- **Author:** Enio Rocha — Patos de Minas, MG, Brazil
