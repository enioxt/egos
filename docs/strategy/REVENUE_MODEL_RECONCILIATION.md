# Revenue Model Reconciliation — SSOT

> **VERSION:** 1.0.0 | **DATE:** 2026-03-29
> **PURPOSE:** Unify the two revenue models into one coherent strategy.
> **SSOT MERGE:** Resolves tension between business/inventory.md (95/5 model) and Guard Brasil docs (SaaS model).

## The Two Models (Both Valid, Different Contexts)

### Model A: Implementation Services (95/5 Split)
**Source:** `business/inventory.md`
**What:** Deploy EGOS products for clients. Client pays one-time setup fee.
95% goes to implementor, 5% to EGOS ecosystem fund.

| Product | Setup Fee | Monthly Support |
|---------|-----------|----------------|
| EGOS Kernel | R$2.500 | R$500 |
| Carteira Livre | R$4.900 | R$1.000 |
| 852 Inteligência | R$3.500 | R$800 |
| EGOS-Inteligência | R$7.900 | R$1.500 |
| Assistentes Guiados | R$3.000 | R$600 |

**Target:** Small businesses needing custom AI deployments.
**Validated:** Products exist and run in production.

### Model B: Guard Brasil SaaS
**Source:** `GUARD_BRASIL_PRODUCT_BOUNDARY.md`, `FLAGSHIP_BRIEF.md`
**What:** Self-service SDK (free) + hosted API/MCP/audit (paid monthly).

| Surface | Price | Recurring |
|---------|-------|-----------|
| SDK (npm) | Free | — |
| Hosted API | R$500/mês | Yes |
| MCP Server | R$1.000/mês | Yes |
| Enterprise SLA | R$2.000/mês | Yes |
| Audit Console | R$3.000/mês | Yes |

**Target:** Dev teams integrating AI safety into their products.
**Validated:** SDK exists (166 tests). API/MCP not yet built.

## Reconciliation: They're Complementary, Not Competing

```
Model A (Services) ←── For clients who need FULL deployment
                        "Deploy carteira-livre for my business"
                        One-time + monthly support
                        Revenue: R$3K-8K per client

Model B (SaaS)     ←── For dev teams who build their OWN products
                        "Add LGPD safety to my chatbot"
                        Self-service + monthly subscription
                        Revenue: R$500-6K/mês per team
```

### The Unified Revenue Funnel

```
1. AWARENESS
   └─ Open-source SDK on npm (Guard Brasil) → Model B entry
   └─ egos.ia.br content + demos → Both models

2. ADOPTION
   └─ Developer installs @egos/shared → Model B path
   └─ Business inquires about 852/carteira-livre → Model A path

3. CONVERSION
   └─ Dev team needs hosted API → Model B (R$500+/mês)
   └─ Business needs full deployment → Model A (R$3K-8K setup)

4. EXPANSION
   └─ Dev team needs enterprise SLA → Model B (R$2K-6K/mês)
   └─ Business needs additional products → Model A (R$2.5K-8K each)
```

## Product-to-Model Mapping

| Product | Primary Model | Secondary |
|---------|--------------|-----------|
| **Guard Brasil SDK** | B (SaaS) | — |
| **Guard Brasil API** | B (SaaS) | — |
| **Carteira Livre** | A (Services) | — |
| **852 Inteligência** | A (Services) | — |
| **EGOS-Inteligência** | A (Services) | B (API access to graph) |
| **Forja** | A (Services) | — |
| **EGOS Kernel** | A (Services) | B (governance consulting) |

## EGOS-Inteligência Role Clarification

EGOS-Inteligência (br-acc) has three roles that must be explicitly separated:

1. **Proof case** for Guard Brasil — shows ATRiAN/PII/PublicGuard working on real data
2. **Deployable product** — R$7.900 implementation for clients needing Brazilian public data graph
3. **Data moat** — Neo4j with millions of entities from 10+ public sources

These roles are compatible but **each should be pitched differently** depending on audience.

## Forja Gap

Forja appears in deployment lists but has NO entry in business/inventory.md.
**Action needed:** Add Forja to inventory with pricing and ICP.

## Test Count Reconciliation

Documents reference "162 tests" and "166 tests" — the correct current count is **166 tests** (after cheap-first policy tests were added). All docs should reference 166.
