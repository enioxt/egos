# AGENTS.md — EGOS Framework Core

> **VERSION:** 1.2.1 | **UPDATED:** 2026-03-27
> **TYPE:** Framework Core + Orchestration Kernel + Agent Runtime
> **NOTE:** Governance audit completed 2026-03-27 → 2 duplicates removed, 6 broken MCPs disabled, 3 non-critical agents dormant. See `docs/AGENT_DEPRECATION_LOG.md`

---

<!-- llmrefs:start -->

## LLM Reference Signature

- **Role:** system map + command surface for the EGOS framework core
- **Summary:** Pure orchestration kernel providing governance (.guarani/),
  agent runtime (runner + event bus), multi-LLM provider, and shared
  utilities. No apps — leaf repos (egos-lab, 852, br-acc, etc.) consume this.
- **Read next:**
  - `.windsurfrules` — active governance rules
  - `TASKS.md` — current priorities
  - `docs/SSOT_REGISTRY.md` — canonical cross-repo SSOT registry
  - `.guarani/PREFERENCES.md` — coding standards

<!-- llmrefs:end -->

## Project Overview

| Item | Value |
|------|-------|
| **Project** | EGOS |
| **Description** | Orchestration kernel for governed AI agents |
| **Path** | `/home/enio/egos` |
| **Repo** | github.com/enioxt/egos |
| **License** | MIT |
| **Runtime** | Bun / Node 20+ / TypeScript |
| **LLM (Primary)** | Alibaba Qwen-plus via DashScope |
| **LLM (Fallback)** | Gemini via OpenRouter |

## Architecture

```text
egos/
├── .guarani/                    # Governance DNA
│   ├── IDENTITY.md              # Agent identity
│   ├── PREFERENCES.md           # Coding standards
│   ├── DESIGN_IDENTITY.md       # Visual identity
│   ├── orchestration/           # 7-phase protocol
│   │   ├── PIPELINE.md
│   │   ├── GATES.md
│   │   ├── QUESTION_BANK.md
│   │   └── DOMAIN_RULES.md
│   ├── prompts/                 # Meta-prompt system
│   │   ├── PROMPT_SYSTEM.md
│   │   ├── triggers.json
│   │   └── meta/
│   └── philosophy/
├── agents/
│   ├── runtime/
│   │   ├── runner.ts            # Core agent execution (FROZEN)
│   │   └── event-bus.ts         # Inter-agent communication (FROZEN)
│   ├── registry/
│   │   ├── agents.json          # Agent definitions (SSOT)
│   │   └── schema.json
│   └── cli.ts                   # Agent CLI
├── packages/
│   └── shared/
│       └── src/
│           ├── llm-provider.ts  # Multi-LLM routing
│           ├── rate-limiter.ts  # API rate limiting
│           ├── types.ts         # Core types
│           └── index.ts
├── scripts/                     # Kernel utilities + infra launchers
│   └── oracle-instance-launcher/
├── .windsurfrules               # Active governance
├── frozen-zones.md              # Protected files list
├── AGENTS.md                    # THIS FILE
├── TASKS.md                     # Live roadmap
├── docs/
│   ├── SYSTEM_MAP.md            # Kernel activation map
│   ├── CAPABILITY_REGISTRY.md   # Reusable capability SSOT
│   └── SSOT_REGISTRY.md         # Cross-repo SSOT registry
└── README.md
```

## Frozen Zones

> **DO NOT EDIT** without explicit user request + proof-of-work:
> - `agents/runtime/runner.ts`
> - `agents/runtime/event-bus.ts`
> - `.husky/pre-commit`
> - `.guarani/orchestration/PIPELINE.md`

## Agent Status Summary (2026-03-27 Audit & Consolidation)

**Active Agents:** 34 (across kernel + lab)
- **Kernel:** 9 core + critical agents (T0-T3)
  - 6 base governance agents (T0)
  - 3 consolidated critical agents: orchestrator, security_scanner_v2, report_generator
- **Lab:** 25 operational agents (T0-T3)

**Dormant Agents:** 3 (awaiting implementation or scheduling)
- `e2e_smoke` — E2E test suite (blocked on Playwright, pending)
- `social_media_agent` — Multi-channel automation (blocked on content strategy, pending)
- `ghost_hunter` — Discovery protocol agent (intentional placeholder, awaiting first 3 discoverers)

**Broken Dependencies:** 6 MCPs disabled (files never created)
- See `docs/AGENT_DEPRECATION_LOG.md` for detailed audit trail
- See `docs/MCP_REMEDIATION_PLAN.md` for implementation plan
- Affected agents: contract_tester, integration_tester, code_reviewer, ssot_fixer, etl_orchestrator
- **Status:** Phase 1 complete (disabled), Phase 2 pending (remediation)

## Commands

```bash
bun agent:list              # List all registered agents (9 kernel + 25 lab = 34 total; 3 dormant)
bun agent:run <id> --dry    # Run agent in dry-run mode
bun agent:run <id> --exec   # Run agent in execute mode
bun agent:lint              # Validate agent registry
bun typecheck               # TypeScript strict check
bun lint                    # ESLint
bun governance:sync         # Dry-run kernel -> ~/.egos governance propagation
bun governance:sync:exec    # Sync kernel -> ~/.egos -> leaf repos
bun governance:sync:local   # Sync kernel -> ~/.egos only (skip leaf repos)
bun governance:check        # Verify kernel and ~/.egos have 0 drift
bun pr:pack --title "<title>" --out /tmp/pr.md  # Generate signed PR message pack with env context
bun pr:gate --file /tmp/pr.md  # Enforce sign-off + IDE validation checklist evidence
bash ./scripts/oracle-instance-launcher/scripts/run.sh --dry-run  # Oracle OCI launcher check

# Context Tracker (run anytime — mandatory before long multi-step tasks)
bun agent:run context_tracker --dry   # CTX score 0-280 with zone emoji + /end advice
```

## Slash Workflows (Operational)

- Canonical command workflows live in `.agents/workflows/`
- `/start` activation workflow: `.agents/workflows/start-workflow.md`
- Governance dissemination workflow: `.agents/workflows/sync.md`
- PR preparation workflow: `.agents/workflows/pr-prep.md`
- `/disseminate` propagation workflow: `.agents/workflows/disseminate.md`

## Meta-Prompts (Operational)

- `activation.egos-governance` → `.guarani/prompts/meta/egos-activation-governance.md` (used for `/start` and activation diagnostics)
