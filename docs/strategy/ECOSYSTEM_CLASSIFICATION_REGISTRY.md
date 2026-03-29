# EGOS Ecosystem Classification Registry

> **SSOT Owner:** `egos/docs/strategy/ECOSYSTEM_CLASSIFICATION_REGISTRY.md`
> **Version:** 1.0.0 | **Created:** 2026-03-29 | **Status:** ACTIVE
> **Task:** EGOS-076

---

## Purpose

Single source of truth for classifying every product, module, idea, and repo surface in the EGOS ecosystem.

Used by:
- `TASKS.md` — task target routing (which repo, which tier)
- `SYSTEM_MAP.md` — repo role declarations
- `CAPABILITY_REGISTRY.md` — per-capability owner and status
- New-project gate (`docs/governance/NEW_PROJECT_GATE.md`) — block premature product creation

---

## Classification Taxonomy

| Class | Meaning | Action |
|-------|---------|--------|
| `flagship_product` | Primary monetizable product — the thing we sell | Protect scope, prioritize, measure revenue |
| `kernel_core` | Foundational infrastructure inside `egos` — not sold directly | Maintain quality, adopt across leaf repos |
| `standalone_candidate` | Could become its own npm package, service, or repo | Evaluate at product maturity (not before users) |
| `proof_case` | Reference implementation that validates the flagship works | Keep alive, document wins, avoid scope creep |
| `leaf_consumer` | Downstream repo consuming kernel packages | Must import from kernel, not duplicate |
| `incubator` | Experimental surface — not yet classified | No monetization, no broad marketing |
| `internal_infra` | CI/CD, scripts, dev tooling — stays internal | Never publicize, never sell |
| `archive` | Deprecated / superseded — keep for reference | No active development, mark clearly |
| `discard` | Dead code confirmed — delete | Remove in next cleanup cycle |

---

## Registry

### Repos

| Surface | Repo | Class | Rationale |
|---------|------|-------|-----------|
| EGOS kernel | `enioxt/egos` | `kernel_core` | Canonical SSOT, governance, shared packages, agent runtime |
| EGOS Lab | `enioxt/egos-lab` | `leaf_consumer` + incubator | Apps, demos, distribution surface — must not duplicate kernel |
| EGOS-Inteligência (br-acc) | `enioxt/EGOS-Inteligencia` | `proof_case` | Strongest concrete proof of Guard Brasil in production |
| carteira-livre | `enioxt/carteira-livre` | `leaf_consumer` | WhatsApp/marketplace bot — consumes ATRiAN + PII Scanner |
| forja | `enioxt/forja` | `leaf_consumer` | ERP/chat API — consumes ATRiAN + PII + shared |
| santiago | `enioxt/santiago` | `incubator` | Pending onboarding into governance mesh (EGOS-069) |

---

### Packages (`egos/packages/`)

| Package | npm name | Class | Rationale |
|---------|----------|-------|-----------|
| `guard-brasil/` | `@egos/guard-brasil` | `flagship_product` | ATRiAN + PII + Public Guard + Evidence Chain — the product we sell |
| `shared/` | `@egos/shared` | `kernel_core` | Foundational reusable modules consumed by all leaf repos |
| `types/` | `@egos/types` | `kernel_core` | Core type definitions (Atom, etc.) — shared contract layer |
| `core/` | `@egos/core` | `kernel_core` | Module system, contracts, auth primitives |
| `audit/` | `@egos/audit` | `kernel_core` | Audit logger — activation trail for governance |
| `registry/` | `@egos/registry` | `kernel_core` | Module registry — runtime module management |
| `atomizer/` | `@egos/atomizer` | `standalone_candidate` | Data atomization — composable, could be standalone npm package |
| `search-engine/` | `@egos/search-engine` | `standalone_candidate` | In-memory atomic search — composable, could be standalone npm package |

**Note on `standalone_candidate`:** `atomizer` and `search-engine` are clean, dependency-light packages that could be published independently. Evaluate after Guard Brasil has paying users — not before.

---

### Products / Ideas

| Idea | Current State | Class | Decision |
|------|--------------|-------|----------|
| EGOS Guard Brasil | `packages/guard-brasil/` — 15 tests pass, npm-ready | `flagship_product` | **Publish to npm now** (`npm publish --access public`) |
| MCP Guard Brasil | Phase 2 roadmap (GUARD_BRASIL.md) | `incubator` | Build after API Starter tier has ≥1 paying customer |
| Guard Brasil Hosted API | Phase 3 roadmap | `incubator` | Build after npm has ≥10 active users |
| Guard Brasil Dashboard | Phase 3 roadmap | `incubator` | Build after API has ≥1 paying customer |
| `@egos/mcp-governance` | EGOS-087 spec | `incubator` | No green light until Guard Brasil MVP is live |
| `@egos/mcp-memory` | EGOS-088 spec | `incubator` | No green light until Guard Brasil MVP is live |
| Atomic Search Engine | `packages/search-engine/` — functional | `standalone_candidate` | Evaluate as standalone npm package post-Guard-Brasil |
| Data Atomizer | `packages/atomizer/` — functional | `standalone_candidate` | Evaluate as standalone npm package post-Guard-Brasil |
| EGOS Commons / Split | EGOS-096 | `incubator` | Blocked — requires legal/compliance gates before payment automation |
| Network-state philosophy layer | Mentioned in older docs | `archive` | Not a product, not a feature — archive |

---

### Documentation / Governance

| Surface | Class | SSOT | Notes |
|---------|-------|------|-------|
| TASKS.md | `kernel_core` | `egos/TASKS.md` | Single backlog for kernel — do not duplicate in leaf repos |
| CAPABILITY_REGISTRY.md | `kernel_core` | `egos/docs/CAPABILITY_REGISTRY.md` | Synced to `~/.egos/docs/` via governance scripts |
| SYSTEM_MAP.md | `kernel_core` | `egos/docs/SYSTEM_MAP.md` + `~/.egos/SYSTEM_MAP.md` | Cross-repo map lives in `~/.egos/` |
| SSOT_REGISTRY.md | `kernel_core` | `egos/docs/SSOT_REGISTRY.md` | Cross-repo canonical ownership registry |
| FLAGSHIP_BRIEF.md | `flagship_product` | `egos/docs/strategy/FLAGSHIP_BRIEF.md` | Primary commercial narrative — do not fragment |
| This registry | `kernel_core` | `egos/docs/strategy/ECOSYSTEM_CLASSIFICATION_REGISTRY.md` | You are here |

---

## Classification Rules

### How to classify a new surface

Ask these questions in order:

1. **Does it generate revenue or is it the thing we demo to prospects?** → `flagship_product`
2. **Is it foundational infrastructure that powers the flagship but is not sold alone?** → `kernel_core`
3. **Is it a real, deployable proof that the flagship works?** → `proof_case`
4. **Is it a downstream app or service that consumes kernel packages?** → `leaf_consumer`
5. **Is it a clean, composable module that could stand alone with minimal effort?** → `standalone_candidate` — evaluate at product maturity
6. **Is it experimental, not yet validated?** → `incubator` — no promotion until criteria are met
7. **Is it internal tooling only?** → `internal_infra`
8. **Is it superseded or unused?** → `archive` or `discard`

### Promotion criteria (incubator → standalone_candidate)

A surface may be promoted from `incubator` to `standalone_candidate` when:
- [ ] Has a clear, single-sentence value proposition
- [ ] Has a defined ICP (who pays, who uses)
- [ ] Has at least one real user or proof case
- [ ] Passes the new-project gate (`docs/governance/NEW_PROJECT_GATE.md`)

### Promotion criteria (standalone_candidate → flagship_product)

- [ ] Has a paying customer or confirmed LOI
- [ ] Has a go-to-market plan with success metrics
- [ ] Has a named owner responsible for it
- [ ] Guard Brasil is already generating revenue (kernel health prerequisite)

---

## Guard Rails for This Registry

- **Do not add new `flagship_product` entries** without Guard Brasil achieving revenue first.
- **Do not promote `incubator` surfaces** without passing the new-project gate.
- **Do not create new repos** for `standalone_candidate` surfaces until they have external users.
- This registry must be updated whenever TASKS.md gains a new EGOS task targeting a new surface.

---

*Maintained by: EGOS Kernel*
*Related: EGOS-076, EGOS-073, docs/governance/NEW_PROJECT_GATE.md*
