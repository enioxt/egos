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
# EGOS Guard Brasil — Free vs Paid Surface Definition

> **VERSION:** 1.0.0 | **CREATED:** 2026-03-23 | **STATUS:** Active
> **TASK:** EGOS-063

---

## Commercial Sentence

> "We make Brazilian AI assistants safer to ship by adding LGPD-aware guardrails, masking, evidence discipline, and policy enforcement."

---

## Tiering Strategy

### Free (Open Source — MIT)

Everything needed to self-host and evaluate:

| Surface | Description | License |
|---------|-------------|---------|
| `@egos/shared` SDK | ATRiAN, PII Scanner, Public Guard, Evidence Chain | MIT |
| CLI tool (`egos-guard`) | Validate files/text from terminal | MIT |
| Spec & docs | Protocol specs, integration guides | MIT |
| Reference implementation | br-acc as working example | MIT |

**Why free:** Drives adoption. Developers integrate, validate value, discover limits.

---

### Paid (Hosted / Enterprise)

| Tier | Target | Price (est.) | Surface |
|------|--------|-------------|---------|
| **API Starter** | Indie devs / startups | R$199/mo | Hosted REST API, 50K req/mo, basic dashboard |
| **API Pro** | SMBs | R$799/mo | 500K req/mo, audit logs, email alerts, SLA 99.5% |
| **Enterprise** | Gov / large corps | Custom | Custom SLA, on-prem deploy, RBAC, evidence archival |
| **MCP Addon** | AI agent builders | R$299/mo | Guard Brasil as MCP tools for Claude/OpenAI agents |

---

## Feature Breakdown

| Feature | Free SDK | API Starter | API Pro | Enterprise |
|---------|----------|-------------|---------|-----------|
| ATRiAN validation | ✅ | ✅ | ✅ | ✅ |
| PII Scanner BR | ✅ | ✅ | ✅ | ✅ |
| Public Guard masking | ✅ | ✅ | ✅ | ✅ |
| Evidence Chain | ✅ | ✅ | ✅ | ✅ |
| REST API endpoint | ❌ | ✅ | ✅ | ✅ |
| API key management | ❌ | ✅ | ✅ | ✅ |
| Compliance dashboard | ❌ | Basic | Full | Custom |
| Audit log (30 days) | ❌ | ❌ | ✅ | Unlimited |
| Violation alerts | ❌ | Email | Email + Slack | Custom webhooks |
| SLA | ❌ | Best-effort | 99.5% | 99.9% |
| Custom policies | ❌ | ❌ | ❌ | ✅ |
| On-premise deploy | ❌ | ❌ | ❌ | ✅ |
| MCP server | ❌ | Add-on | Add-on | ✅ |
| Priority support | ❌ | ❌ | ✅ | Dedicated |

---

## Monetization Logic

### Why this works

1. **Self-serve funnel:** `npm install @egos/shared` → `egos-guard validate` → hits rate limits or needs dashboard → upgrades
2. **B2B expansion:** Enterprise buys for compliance mandate (LGPD enforcement). One contract = 12+ months ARR.
3. **MCP add-on:** Unique positioning as AI agent guardrails-as-a-service. No competitor has a Brazil-first MCP guardrail.
4. **Evidence archival:** Legal teams need evidence trails. Charged by retention period.

### Revenue targets

| Milestone | Metric | Revenue/mo |
|-----------|--------|-----------|
| MVP | 10 API Starter | R$2K |
| Early | 30 API Starter + 5 Pro | R$10K |
| Scale | 5 Enterprise + 100 Starter | R$50K+ |

---

## What Stays Free Forever

To protect ecosystem trust and adoption:
- Core SDK (`@egos/shared` modules)
- ATRiAN spec and patterns
- PII scanner patterns and logic
- Evidence chain protocol
- br-acc reference implementation

**Commitment:** Open source core is never paywalled. Only hosted infrastructure is paid.

---

## Next Steps (EGOS-064)

1. **Publish `@egos/guard-brasil` to npm** — standalone package from shared modules
2. **Build CLI `egos-guard`** — `egos-guard validate <file>` + `egos-guard mask <text>`
3. **Create landing page** — `egos.ia.br/guard` with live demo
4. **First paid customer target** — carteira-livre or br-acc as internal reference + 1 external prospect

---

*Maintained by: EGOS Kernel*
*Related: EGOS-062, EGOS-063, EGOS-064*
