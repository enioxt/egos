# New Project Gate — EGOS-077

> **VERSION:** 1.0.0 | **DATE:** 2026-03-29
> **PURPOSE:** Mandatory gate before any new product, module, or agent enters the ecosystem.
> **ENFORCEMENT:** Manual review + ECOSYSTEM_CLASSIFICATION_REGISTRY.md entry required.

## Gate Requirements

Before creating ANY new product, service, or significant module, the following
MUST be documented. No exceptions.

### Mandatory Fields

| Field | Description | Example |
|-------|------------|---------|
| **Name** | Clear, concise name | Guard Brasil |
| **Classification** | From ECOSYSTEM_CLASSIFICATION_REGISTRY schema | `product`, `candidate`, `lab`, `internal_infra` |
| **Problem Statement** | What specific pain does this solve? (max 3 sentences) | "Brazilian AI teams have no native LGPD tooling" |
| **ICP (Ideal Customer Profile)** | Who pays? Be specific. | "BR AI startups with chatbots, 5-50 employees" |
| **Success Metric** | How do we know it works? Measurable. | "5 external adopters in 90 days" |
| **Existing Alternatives** | What already exists? Why isn't it enough? | "No Brazilian-native solution exists" |
| **EGOS Advantage** | What does EGOS uniquely bring? | "ATRiAN + PII + governance-as-code" |
| **Effort Estimate** | T-shirt size: S/M/L/XL | M (2-4 weeks) |
| **Revenue Model** | How does this make money? | "Free SDK, paid API hosting" |
| **Dependencies** | What must exist first? | "@egos/shared published on npm" |

### Gate Decision

| Decision | Criteria |
|----------|---------|
| **PROCEED** | All fields filled, ICP validated, effort ≤ XL, no blocking deps |
| **DEFER** | Good idea but deps unresolved or higher priority exists |
| **REJECT** | No clear ICP, duplicates existing surface, or violates focus directive |

### Focus Directive (Active)

> Until EGOS-062..064 are resolved (Guard Brasil packaging + npm publish),
> new work MUST strengthen the flagship or its proof cases only.
> New products require explicit user approval to override this.

## Process

1. Proposer fills all mandatory fields in a PR description
2. Review against Ecosystem Classification Registry
3. Check SSOT Merge Rule (#23): does this duplicate an existing surface?
4. Gate decision recorded in PR comment
5. If PROCEED: add to ECOSYSTEM_CLASSIFICATION_REGISTRY.md with status
6. If DEFER: add to TASKS.md backlog with deps noted
7. If REJECT: document reason, do not create surface

## Integration Points

- **ECOSYSTEM_CLASSIFICATION_REGISTRY.md** — New entries go here
- **TASKS.md** — Deferred items go to backlog
- **SSOT_REGISTRY.md** — Approved products get SSOT entry
- **CAPABILITY_REGISTRY.md** — New capabilities registered
