# SYSTEM_MAP.md — EGOS Framework Core

> **VERSION:** 1.0.0 | **UPDATED:** 2026-03-13
> **ROLE:** repo-local map for `/start` in the canonical kernel

<!-- llmrefs:start -->

## LLM Reference Signature

- **Role:** activation map for the `egos` kernel
- **Summary:** points to the local SSOTs that define governance, runtime, shared modules, migration status, and chatbot/mycelium standards
- **Read next:**
  - `AGENTS.md` — repo identity, architecture, command surface
  - `TASKS.md` — current sprint and roadmap horizons
  - `.windsurfrules` — active governance and frozen zones
  - `docs/MIGRATION_PLAN.md` — kernel vs lab separation and sync direction
  - `docs/CAPABILITY_REGISTRY.md` — reusable capability SSOT
  - `docs/modules/CHATBOT_SSOT.md` — canonical chatbot standard

<!-- llmrefs:end -->

## Canonical Local Truth

- `AGENTS.md` — what this repo is
- `TASKS.md` — what is next
- `.windsurfrules` — what is allowed
- `.guarani/` — how reasoning and governance work
- `agents/runtime/` — frozen execution kernel
- `packages/shared/src/` — reusable core modules

## Activation Chain

1. Read `AGENTS.md`
2. Read `TASKS.md`
3. Read `.windsurfrules`
4. Read `.guarani/PREFERENCES.md` and `.guarani/IDENTITY.md`
5. Read `docs/CAPABILITY_REGISTRY.md`
6. Read `docs/modules/CHATBOT_SSOT.md` when chatbot/compliance work is in scope
7. Read `docs/MIGRATION_PLAN.md` when scope touches kernel vs lab boundaries
8. Read latest file in `docs/_current_handoffs/`

## Cross-Repo Context

- Global topology lives in `~/.egos/SYSTEM_MAP.md`
- `egos` is the canonical kernel
- `egos-lab` is the incubator and operations surface
- Leaf repos consume governance and shared modules but keep domain truth local

## Current Kernel-Specific Surfaces

- Sync: `scripts/governance-sync.sh`, `scripts/link-ssot-files.sh`
- Validation: `bun run typecheck`, `bun run agent:lint`, `bun run governance:check`
- Agents: `dep_auditor`, `archaeology_digger`, `chatbot_compliance_checker`
- Docs: `docs/concepts/mycelium/`, `docs/archaeology/`, `docs/modules/`
