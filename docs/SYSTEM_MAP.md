# SYSTEM_MAP.md — EGOS Framework Core

> **VERSION:** 3.0.0 | **UPDATED:** 2026-03-29
> **ROLE:** Repo-local activation map for `/start` in the canonical kernel

<!-- llmrefs:start -->

## LLM Reference Signature

- **Role:** Activation map for the `egos` kernel
- **Summary:** Points to local SSOTs that define governance, runtime, shared modules, and standards
- **Read next:**
  - `AGENTS.md` — repo identity, architecture, command surface
  - `TASKS.md` — current sprint and roadmap
  - `.windsurfrules` — active governance and frozen zones
  - `docs/SSOT_REGISTRY.md` — canonical cross-repo SSOT registry (v2.0.0)
  - `docs/CAPABILITY_REGISTRY.md` — reusable capability SSOT
  - `docs/modules/CHATBOT_SSOT.md` — canonical chatbot standard
  - `docs/strategy/GUARD_BRASIL_PRODUCT_BOUNDARY.md` — flagship product definition

<!-- llmrefs:end -->

## Canonical Local Truth

- `AGENTS.md` — what this repo is
- `TASKS.md` — what is next
- `.windsurfrules` — what is allowed (23 rules, max 150L)
- `docs/SSOT_REGISTRY.md` — what is globally canonical vs locally owned
- `.guarani/` — how reasoning and governance work
- `agents/runtime/` — frozen execution kernel
- `packages/shared/src/` — reusable core modules (14 modules, 162 tests)

## Activation Chain

1. Read `AGENTS.md`
2. Read `TASKS.md`
3. Read `.windsurfrules`
4. Read `.guarani/PREFERENCES.md` and `.guarani/IDENTITY.md`
5. Read `docs/SSOT_REGISTRY.md`
6. Read `docs/CAPABILITY_REGISTRY.md`
7. Read `docs/modules/CHATBOT_SSOT.md` when chatbot/compliance work is in scope
8. Read latest file in `docs/_current_handoffs/`

## Cross-Repo Context

- Global topology: `~/.egos/SYSTEM_MAP.md`
- `egos` = canonical kernel (governance, shared modules, agent runtime)
- `egos-lab` = incubator (apps, lab agents, worker infra)
- Leaf repos (852, forja, carteira-livre, br-acc) consume governance + shared modules

## Current Kernel Surfaces

### Scripts & Validation
- `scripts/governance-sync.sh` — kernel → ~/.egos → leaf propagation
- `scripts/doctor.ts` — 23-check environment validator
- `scripts/worktree-validator.ts` — branch naming + ownership enforcer
- `scripts/check-doc-proliferation.sh` — anti-proliferation gate
- `bun run typecheck` / `bun run agent:lint` / `bun run governance:check`

### Agents (10 registered in `agents/registry/agents.json`)
- `dep_auditor`, `archaeology_digger`, `chatbot_compliance_checker`, `dead_code_detector`
- `capability_drift_checker`, `context_tracker`, `gtm_harvester`
- `aiox_gem_hunter`, `framework_benchmarker`, `mastra_gem_hunter`

### Pre-Commit (5 gates, FROZEN)
- gitleaks (secret scan), tsc (type check), frozen zones, doc proliferation, SSOT drift

## Shared Modules (@egos/shared) — 14 modules, 162 tests

| Module | File | Tests | Purpose |
|--------|------|-------|---------|
| **Guard Brasil** | `guard-brasil.ts` | 9 | Unified safety (ATRiAN+PII+Guard+Evidence) |
| ATRiAN | `atrian.ts` | 16 | Ethical validation (7 axioms) |
| PII Scanner | `pii-scanner.ts` | 14 | Brazilian PII detection |
| Public Guard | `public-guard.ts` | 16 | LGPD-compliant masking |
| Evidence Chain | `evidence-chain.ts` | 17 | Traceable provenance |
| Conversation Memory | `conversation-memory.ts` | 13 | Session memory |
| Cross-Session Memory | `cross-session-memory.ts` | 17 | Supabase persistence |
| LLM Provider | `llm-provider.ts` | 6 | Multi-provider + cost estimation |
| Model Router | `model-router.ts` | 13 | Task-aware model selection |
| Rate Limiter | `rate-limiter.ts` | 8 | Token bucket throttling |
| Telemetry | `telemetry.ts` | 11 | Dual output (Supabase+JSON) |
| Metrics Tracker | `metrics-tracker.ts` | 13 | Session-level tracking |
| Mycelium Graph | `mycelium/reference-graph.ts` | — | Reference graph (27 nodes) |
| Repo Role | `repo-role.ts` | 6 | Repository classification |

## Workflows

| Workflow | Canonical | Compat | Purpose |
|----------|-----------|--------|---------|
| /start | `.agents/workflows/start-workflow.md` | `.windsurf/workflows/start.md` | Session init |
| /end | — | `.windsurf/workflows/end.md` | Session finalization |
| /pr | `.agents/workflows/pr-prep.md` | — | PR preparation |
| /sync | `.agents/workflows/sync.md` | — | Governance sync |
| /disseminate | `.agents/workflows/disseminate.md` | `.windsurf/workflows/disseminate.md` | Knowledge propagation |
| /mycelium | `.agents/workflows/mycelium.md` | `.windsurf/workflows/mycelium.md` | Mesh audit |
