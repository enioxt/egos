# AGENTS.md — EGOS Framework Core

> **VERSION:** 2.0.0 | **UPDATED:** 2026-03-29
> **TYPE:** Framework Core + Orchestration Kernel + Agent Runtime

---

<!-- llmrefs:start -->

## LLM Reference Signature

- **Role:** System map + command surface for the EGOS framework core
- **Summary:** Orchestration kernel: governance (.guarani/), agent runtime,
  Guard Brasil safety layer, multi-LLM provider, 14 shared modules (162 tests).
  No apps — leaf repos consume this.
- **Read next:**
  - `.windsurfrules` — 23 active governance rules
  - `TASKS.md` — current priorities
  - `docs/SSOT_REGISTRY.md` — cross-repo SSOT registry (v2.0.0)
  - `docs/SYSTEM_MAP.md` — activation map (v3.0.0)

<!-- llmrefs:end -->

## Project Overview

| Item | Value |
|------|-------|
| **Project** | EGOS |
| **Description** | Orchestration kernel for governed AI agents |
| **Repo** | github.com/enioxt/egos |
| **License** | MIT |
| **Runtime** | Bun / TypeScript |
| **LLM Primary** | Alibaba Qwen-plus via DashScope |
| **LLM Fallback** | Gemini/GPT-4o/Claude/DeepSeek via OpenRouter |
| **Tests** | 162 passing, 372 assertions, 14 files |
| **Modules** | 14 in `@egos/shared` (86% test coverage) |
| **Agents** | 10 registered, all active |

## Architecture

```text
egos/
├── .guarani/                    # Governance DNA (SSOT)
│   ├── orchestration/           # PIPELINE.md, GATES.md (FROZEN)
│   ├── prompts/                 # Meta-prompt system + triggers
│   └── standards/               # Signature contracts
├── agents/
│   ├── runtime/                 # runner.ts + event-bus.ts (FROZEN)
│   ├── registry/agents.json     # 10 agents (SSOT)
│   └── agents/                  # Agent implementations
├── packages/shared/src/         # 14 shared modules
│   ├── guard-brasil.ts          # Unified safety (flagship)
│   ├── atrian.ts                # Ethical validation (7 axioms)
│   ├── pii-scanner.ts           # Brazilian PII detection
│   ├── public-guard.ts          # LGPD masking
│   ├── evidence-chain.ts        # Traceable provenance
│   ├── llm-provider.ts          # Multi-provider + cost
│   ├── model-router.ts          # Task-aware routing
│   └── ...                      # memory, telemetry, metrics, etc.
├── docs/
│   ├── SSOT_REGISTRY.md         # Cross-repo SSOT map (v2.0.0)
│   ├── CAPABILITY_REGISTRY.md   # Capability index (v1.4.0)
│   └── SYSTEM_MAP.md            # Activation map (v3.0.0)
├── .husky/pre-commit            # 5 enforcement gates (FROZEN)
└── .windsurfrules               # 23 governance rules (max 150L)
```

## Frozen Zones

> **DO NOT EDIT** without explicit approval + proof-of-work:
> - `agents/runtime/runner.ts` — core execution
> - `agents/runtime/event-bus.ts` — inter-agent communication
> - `.husky/pre-commit` — enforcement gates
> - `.guarani/orchestration/PIPELINE.md` — 7-phase protocol

## Commands

```bash
# Agents
bun agent:list                    # List 10 registered agents
bun agent:run <id> --dry          # Dry-run mode
bun agent:run <id> --exec         # Execute mode
bun agent:lint                    # Validate registry

# Tests & Quality
bun test                          # 162 tests (shared + E2E)
bun typecheck                     # TypeScript strict (0 errors)

# Governance
bun governance:sync               # Preview kernel → ~/.egos sync
bun governance:sync:exec          # Execute sync + propagate to leaves
bun governance:check              # Verify 0 drift

# PR & Validation
bun pr:pack --title "..." --out /tmp/pr.md
bun pr:gate --file /tmp/pr.md
bun pr:audit --owner enioxt --days 15
bun doctor                        # 23-check environment validator
```

## Registered Agents (10)

| Agent | Area | Purpose |
|-------|------|---------|
| dep_auditor | architecture | Package.json version conflicts |
| archaeology_digger | knowledge | Git history reconstruction |
| chatbot_compliance_checker | knowledge | CHATBOT_SSOT validation |
| dead_code_detector | qa | Orphan files + dead exports |
| capability_drift_checker | architecture | 15-capability adoption check |
| context_tracker | observability | CTX score 0-280 + auto /end |
| gtm_harvester | knowledge | GTM/strategy pattern extraction |
| aiox_gem_hunter | knowledge | AIOX pattern analysis |
| framework_benchmarker | knowledge | MASA/LangGraph/AutoGen comparison |
| mastra_gem_hunter | knowledge | Mastra workflow/eval extraction |

## Slash Workflows

| Command | Canonical | Purpose |
|---------|-----------|---------|
| /start | `.agents/workflows/start-workflow.md` | Session init + diagnostics |
| /end | `.windsurf/workflows/end.md` | Session finalization |
| /pr | `.agents/workflows/pr-prep.md` | PR preparation |
| /sync | `.agents/workflows/sync.md` | Governance sync |
| /disseminate | `.agents/workflows/disseminate.md` | Knowledge propagation |
| /mycelium | `.agents/workflows/mycelium.md` | Mesh audit |
