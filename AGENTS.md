# AGENTS.md — EGOS Framework Core

> **VERSION:** 1.3.0 | **UPDATED:** 2026-03-27
> **TYPE:** Framework Core + Orchestration Kernel + Agent Runtime
> **NOTE:** Governance audit completed 2026-03-27 → Registry normalized (agents/tools separation), all agent files verified, 6 utility scripts reclassified. See `docs/AGENT_AUDIT_2026-03-27.md`

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

## Agent Status Summary (2026-03-27 Registry Audit)

**VERIFIED AGENT COUNT:**
- **Kernel agents:** 6 active (all implemented ✅)
  - dep_auditor, archaeology_digger, chatbot_compliance_checker, dead_code_detector, capability_drift_checker, context_tracker
- **Lab agents:** 18 real agents (all implemented ✅)
- **Utilities/Scripts:** 6 reclassified from "agents" → "tools" array
  - security_scanner, idea_scanner, rho_calculator, code_reviewer, disseminator, ambient_disseminator
- **Total working agents:** 24 (kernel 6 + lab 18)
- **Total tools/scripts:** 6

**Dormant/Non-Agents Handled:**
- ✅ `e2e_smoke` — Now has stub implementation (agents/agents/e2e-smoke.ts) in agents registry
- ✅ `social_media_agent` — Implemented stub in lab registry
- ❌ `ghost_hunter` — **REMOVED** (was markdown: docs/protocols/rho-calibration.md, not an agent)

**MCP Remediation Blocking:** 6 agents in egos-lab require Supabase/Morph MCPs
- Affected: contract_tester, integration_tester, etl_orchestrator (+ 3 in extended list)
- **Status:** Phase 1 complete (identified), Phase 2 pending (MCP implementation)
- Tracked in `docs/MCP_REMEDIATION_PLAN.md`

## Commands

```bash
bun agent:list              # List all registered agents (6 kernel + 18 lab = 24 agents; 6 tools)
bun agent:run <id> --dry    # Run agent in dry-run mode
bun agent:run <id> --exec   # Run agent in execute mode
bun agent:lint              # Validate agent registry (must have corresponding .ts files)
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
