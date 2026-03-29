# SSOT_REGISTRY.md — EGOS Cross-Repo Registry

> **VERSION:** 2.0.0 | **UPDATED:** 2026-03-29
> **PURPOSE:** Canonical registry for ALL SSOT surfaces that govern the EGOS ecosystem.
> **RULE:** When distinct systems cover the same concept, evaluate merge into SSOT. Never maintain parallel truths.

## SSOT Merge Rule (MANDATORY)

> **Whenever you encounter two or more systems, documents, configs, or code modules
> that govern the same concept, rules, or data — you MUST evaluate whether they should
> be merged into a single SSOT.** Parallel truths create drift, contradiction, and governance failure.

**Evaluation checklist:**
1. Do these surfaces describe the same concept? → If yes, one must be canonical.
2. Is one a copy/fork of the other? → If yes, delete the copy, point to canonical.
3. Do they have different scopes? → If yes, document the boundary explicitly.
4. Can they be unified without losing information? → If yes, merge now.
5. If merge is not possible, register BOTH in this file with explicit relationship.

## Registry Contract

- `kernel_canonical` — Source lives in `egos`, propagates outward via governance sync.
- `leaf_local` — Source lives in the leaf repo, must NOT be overwritten by kernel.
- `shared_home` — Synced copy in `~/.egos/` consumed by all mapped repos.
- `product_boundary` — Defines a product boundary (e.g., Guard Brasil).
- Every SSOT must declare: owner, enforcement point, freshness rule, and related surfaces.

## Canonical Global SSOTs

| Surface | Class | Canonical Source | Shared Copy | Enforcement | Related |
|---|---|---|---|---|---|
| Governance DNA | `kernel_canonical` | `egos/.guarani/` | `~/.egos/guarani/` | `governance:sync`, pre-commit | — |
| Shared Workflows | `kernel_canonical` | `egos/.windsurf/workflows/` | `~/.egos/workflows/` | `governance:sync`, pre-commit | — |
| Capability Registry | `kernel_canonical` | `egos/docs/CAPABILITY_REGISTRY.md` | `~/.egos/docs/CAPABILITY_REGISTRY.md` | `governance:check` | This file |
| Chatbot SSOT | `kernel_canonical` | `egos/docs/modules/CHATBOT_SSOT.md` | `~/.egos/docs/modules/CHATBOT_SSOT.md` | compliance checks | Capability Registry |
| SSOT Registry | `kernel_canonical` | `egos/docs/SSOT_REGISTRY.md` | `~/.egos/docs/SSOT_REGISTRY.md` | `governance:check` | — |
| Guard Brasil Boundary | `product_boundary` | `egos/docs/strategy/GUARD_BRASIL_PRODUCT_BOUNDARY.md` | — | Manual review | Capability Registry |
| Gap Analysis & Plan | `kernel_canonical` | `egos/docs/GAPS_AND_ADVANCEMENT_PLAN.md` | — | Session review | TASKS.md |
| Agent Rules | `kernel_canonical` | `egos/.windsurfrules` | `~/.egos/.windsurfrules` | pre-commit (150L max) | .guarani/ |
| Pre-Commit Hooks | `kernel_canonical` | `egos/.husky/pre-commit` | — | FROZEN ZONE | — |
| Orchestration Pipeline | `kernel_canonical` | `egos/.guarani/orchestration/PIPELINE.md` | `~/.egos/guarani/orchestration/` | FROZEN ZONE | GATES.md |
| Quality Gates | `kernel_canonical` | `egos/.guarani/orchestration/GATES.md` | `~/.egos/guarani/orchestration/` | FROZEN ZONE | PIPELINE.md |
| Agent Claim Contract | `kernel_canonical` | `egos/docs/contracts/AGENT_CLAIM_CONTRACT.md` | — | `agent:lint` | agents.json |
| Ecosystem Classification | `kernel_canonical` | `egos/docs/ECOSYSTEM_CLASSIFICATION_REGISTRY.md` | — | Manual review | CAPABILITY_REGISTRY |
| Migration Matrix | `kernel_canonical` | `egos/docs/strategy/MIGRATION_MATRIX.md` | — | Manual review | SSOT Registry |
| Presentation System | `kernel_canonical` | `egos/docs/PRESENTATION_*.md` (5 files) | — | Quarterly review | CAPABILITY_REGISTRY |
| LLM Orchestration Matrix | `kernel_canonical` | `egos/docs/contracts/LLM_ORCHESTRATION_MATRIX.md` | — | `model-router.ts` | llm-provider.ts |
| Operator Narrative Kit | `product_boundary` | `egos/docs/strategy/OPERATOR_NARRATIVE_KIT.md` | — | Manual review | Presentation System |

## Shared Module SSOTs (@egos/shared)

| Module | SSOT Source | Tests | Status | Replaces |
|---|---|---|---|---|
| Guard Brasil (unified) | `packages/shared/src/guard-brasil.ts` | 9 | ✅ Active | — (new unified entry) |
| ATRiAN | `packages/shared/src/atrian.ts` | 16 | ✅ Active | 852 origin → kernel canonical |
| PII Scanner | `packages/shared/src/pii-scanner.ts` | 14 | ✅ Active | 852 origin → kernel canonical |
| Public Guard | `packages/shared/src/public-guard.ts` | 16 | ✅ Active | — |
| Evidence Chain | `packages/shared/src/evidence-chain.ts` | 17 | ✅ Active | — |
| Conversation Memory | `packages/shared/src/conversation-memory.ts` | 13 | ✅ Active | 852 origin → kernel canonical |
| Cross-Session Memory | `packages/shared/src/cross-session-memory.ts` | 17 | ✅ Active | 852 origin → kernel canonical |
| LLM Provider | `packages/shared/src/llm-provider.ts` | 6 | ✅ Active | 852 origin → kernel canonical |
| Model Router | `packages/shared/src/model-router.ts` | 13 | ✅ Active | — |
| Rate Limiter | `packages/shared/src/rate-limiter.ts` | 8 | ✅ Active | — |
| Telemetry | `packages/shared/src/telemetry.ts` | 11 | ✅ Active | 852 origin → kernel canonical |
| Metrics Tracker | `packages/shared/src/metrics-tracker.ts` | 13 | ✅ Active | — |
| Mycelium Graph | `packages/shared/src/mycelium/reference-graph.ts` | — | ✅ Active | — |
| Repo Role | `packages/shared/src/repo-role.ts` | 6 | ✅ Active | — |

## Pre-Commit Hook SSOTs (Cross-Repo)

| Repo | Hook Source | Canonical? | Divergence from Kernel |
|---|---|---|---|
| egos (kernel) | `.husky/pre-commit` | ✅ Canonical | — |
| 852 | `.husky/pre-commit` | ❌ Leaf variant | Native secret scan, handoff freshness, SSOT as warnings |
| FORJA | `.husky/pre-commit` | ❌ Copy of 852 | Identical to 852 (SHA 03302b3) |
| egos-lab | `.husky/pre-commit` | ❌ Lab variant | 9 checks incl. security_scan, ui_sync, session:guard |
| br-acc | — | ❌ Missing | Python project, needs ruff/mypy hooks |

**NOTE:** 852/FORJA hooks were COPIED, not inherited via governance sync. This creates drift risk. Target: derive leaf hooks from kernel canonical + leaf-specific extensions.

## Required Local SSOTs per Repo

| Surface | Class | Required In | Notes |
|---|---|---|---|
| `AGENTS.md` | `leaf_local` | every repo | identity, runtime, commands (max 200L) |
| `TASKS.md` | `leaf_local` | every repo | execution SSOT (max 500L) |
| `.windsurfrules` | `leaf_local` | every repo | repo-local governance (max 150L) |
| `docs/SYSTEM_MAP.md` | `leaf_local` | every repo | human + machine map |
| `docs/knowledge/HARVEST.md` | `leaf_local` | when keeping knowledge | local learnings |

## Freshness Rules

1. New global SSOT: update this file + `CAPABILITY_REGISTRY.md` + `SYSTEM_MAP.md`.
2. New module SSOT: add to table above + update `index.ts` exports.
3. Staged canonical changes must pass `bun run governance:check`.
4. Pre-commit hook changes in leaves must be evaluated against kernel canonical.
5. **SSOT Merge Rule**: evaluate parallel systems EVERY session. Log in HARVEST.md.

## Update Flow

1. Edit kernel canonical SSOT in `egos`.
2. Run `bun run governance:sync:exec`.
3. Run `bun run governance:check`.
4. Update affected leaf `TASKS.md` and system maps.
5. Record learnings in `docs/knowledge/HARVEST.md`.
6. Run `/disseminate` to propagate knowledge.
