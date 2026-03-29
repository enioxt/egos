# Guard Brasil — Product Boundary Definition

> **EGOS-062 + EGOS-063** | **Version:** 1.0.0 | **Date:** 2026-03-29

## Product Identity

**Guard Brasil** is a composable AI safety layer for Brazilian systems.
It validates AI outputs against ethical axioms, detects and masks personal data (LGPD),
and provides traceable provenance for every claim.

## Components

| Module | What it does | Tests |
|--------|-------------|-------|
| **ATRiAN** | 7-axiom ethical validation (absolute claims, fabricated data, false promises, blocked entities, acronyms) | 16 |
| **PII Scanner** | Brazilian personal data detection (CPF, CNPJ, RG, email, phone, plates) | 14 |
| **Public Guard** | LGPD-compliant output masking with sensitivity levels and audit trail | 16 |
| **Evidence Chain** | Traceable provenance for AI-generated claims with confidence scoring | 17 |
| **Guard Brasil** | Unified API combining all above in a single `validate()` call | 9 |

**Total: 72 tests, 0 failures.**

## Usage

```typescript
import { createGuardBrasil } from '@egos/shared/guard-brasil';

const guard = createGuardBrasil({
  atrian: { knownAcronyms: ['CPF', 'CNPJ', 'LGPD'] },
  minAtrianScore: 60,
});

const result = guard.validate('O CPF 123.456.789-00 pertence ao suspeito.');
// result.safe → false
// result.piiCount → 1
// result.maskedText → 'O [CPF REMOVIDO] pertence ao suspeito.'
// result.atrianScore → 100 (no ethical violations)
// result.lgpdDisclosure → '[LGPD] Dados pessoais detectados...'
```

## Free vs Paid Surface (EGOS-063)

### Free (Open Source — MIT)

| Surface | Access | Channel |
|---------|--------|---------|
| Full source code | GitHub | `github.com/enioxt/egos` |
| `@egos/shared` npm package | npm install | `npm i @egos/shared` |
| Guard Brasil TypeScript SDK | import | `@egos/shared/guard-brasil` |
| ATRiAN, PII Scanner, Public Guard, Evidence Chain | import | Individual modules |
| Documentation + examples | Web | `egos.ia.br` |
| Community support | GitHub Issues | Open |

### Paid (Services)

| Surface | Price | What you get |
|---------|-------|-------------|
| **Hosted API** (REST) | R$500/mês | Rate-limited Guard Brasil API endpoint, no infrastructure to manage |
| **MCP Server** | R$1.000/mês | Guard Brasil as MCP tool for IDE integration (Cursor, Windsurf, Claude) |
| **Implementation** | R$5.000-20.000 | Setup + customization + training for your team |
| **Enterprise Policy Packs** | R$5.000 setup | Custom ATRiAN rules, domain-specific blocked entities, sector compliance |
| **SLA Support** | R$2.000/mês | 24h response, incident support, priority fixes |
| **Audit Console** | R$3.000/mês | Dashboard for PII detections, ATRiAN violations, evidence chains across your fleet |

### Monetization Thesis

> "The code is free. The knowledge, speed, and reliability are paid."

- Developers who self-host pay nothing
- Teams who want managed infrastructure pay for hosting
- Enterprises who need compliance guarantees pay for SLA + audit
- The open-source SDK drives adoption → paid services drive revenue

## Entry Points

```
@egos/shared                    → Full shared library
@egos/shared/guard-brasil       → Guard Brasil only (unified API)
packages/shared/src/atrian.ts   → ATRiAN standalone
packages/shared/src/pii-scanner.ts → PII Scanner standalone
packages/shared/src/public-guard.ts → Public Guard standalone
packages/shared/src/evidence-chain.ts → Evidence Chain standalone
```

## npm Publish Checklist (EGOS-064)

- [x] `guard-brasil.ts` created with unified API
- [x] 72 tests passing for safety modules
- [x] Subpath export in package.json
- [ ] Remove `"private": true` from package.json
- [ ] Add `"description"`, `"keywords"`, `"repository"` fields
- [ ] Build step (tsc → dist/)
- [ ] README.md for npm package page
- [ ] `npm publish --access public`
- [ ] Badge in main README

---

*Created during EGOS-062/063 sprint — 2026-03-29*
