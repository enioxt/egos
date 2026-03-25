# SYSTEM_MAP.md — EGOS Framework Core

> **VERSION:** 2.2.0 | **UPDATED:** 2026-03-24
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
  - `docs/SSOT_REGISTRY.md` — canonical cross-repo SSOT registry
  - `docs/modules/CHATBOT_SSOT.md` — canonical chatbot standard

<!-- llmrefs:end -->

## Canonical Local Truth

- `AGENTS.md` — what this repo is
- `TASKS.md` — what is next
- `.windsurfrules` — what is allowed
- `docs/SSOT_REGISTRY.md` — what is globally canonical vs locally owned
- `.guarani/` — how reasoning and governance work
- `agents/runtime/` — frozen execution kernel
- `packages/shared/src/` — reusable core modules

## Activation Chain

1. Read `AGENTS.md`
2. Read `TASKS.md`
3. Read `.windsurfrules`
4. Read `.guarani/PREFERENCES.md` and `.guarani/IDENTITY.md`
5. Read `docs/SSOT_REGISTRY.md`
6. Read `docs/CAPABILITY_REGISTRY.md`
7. Read `docs/modules/CHATBOT_SSOT.md` when chatbot/compliance work is in scope
8. Read `docs/MIGRATION_PLAN.md` when scope touches kernel vs lab boundaries
9. Read latest file in `docs/_current_handoffs/`

## Cross-Repo Context

- Global topology lives in `~/.egos/SYSTEM_MAP.md`
- `egos` is the canonical kernel
- `egos-lab` is the incubator and operations surface
- Leaf repos consume governance and shared modules but keep domain truth local

## Current Kernel-Specific Surfaces

- Sync: `scripts/governance-sync.sh`, `scripts/link-ssot-files.sh`
- Utilities: `scripts/oracle-instance-launcher/` (Python OCI launcher with AD retry + capacity-aware handling)
- Validation: `bun run typecheck`, `bun run agent:lint`, `bun run governance:check`
- Agents: 
  - `dep_auditor`, `archaeology_digger`, `chatbot_compliance_checker`, `context_tracker`
  - `ethik_agent`: x402 Tokenomics, GCP Dynamic Key Gateway, and Donation Engine
  - `atrian_agent`: Ethical Compliance Gate
  - `mycelium_agent`: Event Bus and Mesh Logging
- Docs: `docs/concepts/mycelium/`, `docs/archaeology/`, `docs/modules/`

## Shared Modules (@egos/shared)

| Module | File | Status | Description |
|--------|------|--------|-------------|
| LLM Provider | `llm-provider.ts` | ✅ Active | Multi-provider chat (Alibaba/OpenRouter) |
| Model Router | `model-router.ts` | ✅ Active | Task-based model selection (8 models, 10 tasks) |
| MCP Wrapper | `mcp-wrapper.ts` | ✅ Active | Unified MCP interfaces (EXA, Sequential-Thinking, Memory) |
| ATRiAN | `atrian.ts` | ✅ Active | Ethical validation (7 axioms) |
| PII Scanner | `pii-scanner.ts` | ✅ Active | Brazilian PII detection (CPF, CNPJ, etc.) |
| Conversation Memory | `conversation-memory.ts` | ✅ Active | Session memory + summarization |
| Rate Limiter | `rate-limiter.ts` | ✅ Active | Token bucket rate limiting |
| Telemetry | `telemetry.ts` | ✅ Active | Dual output (Supabase + JSON logs) |
| Mycelium Graph | `mycelium/reference-graph.ts` | ✅ Active | Reference graph (27 nodes, 32 edges) |
| Repo Role | `repo-role.ts` | ✅ Active | Repo classification heuristics |

## Skills

| Skill | File | Purpose |
|-------|------|---------|
| System Map | `.windsurf/skills/system-map.md` | SYSTEM_MAP.md structure and triggers |
| Capability Import | `.windsurf/skills/capability-import.md` | Cross-repo feature import process |

## Diagnostic & Testing Tools

| Tool | File | Purpose | Status |
|------|------|---------|--------|
| Quota Diagnostic | `scripts/diagnose-quotas.js` | Test each model to discover real quotas/limits | ✅ New |
| Model Specializations | `docs/MODEL_SPECIALIZATIONS.md` | Routing matrix: what each model does BEST | ✅ New |
| Quota Guide | `docs/RUN_QUOTA_DIAGNOSTIC.md` | How to run diagnostic + interpret results | ✅ New |

## Orchestration & MCP Configuration

| Component | Location | Status | Notes |
|-----------|----------|--------|-------|
| MCP Strategy | `docs/MCP_ORCHESTRATION_STRATEGY.md` | ✅ Active | 7-tier routing, 12+ models, 5 MCPs |
| Activation Guide | `docs/ACTIVATION_GUIDE.md` | ✅ Active | MCP setup + cost optimization |
| Decision Tree | `docs/ROUTING_DECISION_TREE.txt` | ✅ Active | Visual ASCII guide for routing |
| OpenCode Setup | `docs/OPENCODE_FREE_MODELS_SETUP.md` | ✅ Active | Free models integration |
| Free Models Strategy | `~/.opencode/FREE_MODELS_STRATEGY.md` | ✅ Active | 80% free / 15% promo / 5% premium |

## Workflows

| Workflow | File | Version |
|----------|------|---------|
| /start (canonical ops) | `.agents/workflows/start-workflow.md` | v1.0 |
| /sync (canonical ops) | `.agents/workflows/sync.md` | v1.0 |
| /pr (canonical ops) | `.agents/workflows/pr-prep.md` | v1.0 |
| /disseminate (canonical ops) | `.agents/workflows/disseminate.md` | v1.0 |
| /start | `.windsurf/workflows/start.md` | v5.4 |
| /end | `.windsurf/workflows/end.md` | v5.5 |
| /pre | `.windsurf/workflows/pre.md` | v1.0 |
| /prompt | `.windsurf/workflows/prompt.md` | v1.0 |
| /research | `.windsurf/workflows/research.md` | v1.0 |
| /disseminate | `.windsurf/workflows/disseminate.md` | v1.0 |
| /mycelium | `.windsurf/workflows/mycelium.md` | v1.0 |
| /regras | `.windsurf/workflows/regras.md` | v1.0 |
