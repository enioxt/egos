# AGENTS.md — EGOS Framework Core

> **VERSION:** 1.2.0 | **UPDATED:** 2026-03-20
> **TYPE:** Framework Core + Orchestration Kernel + Agent Runtime

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

## Commands

```bash
bun agent:list              # List all registered agents (8 total)
bun agent:run <id> --dry    # Run agent in dry-run mode
bun agent:run <id> --exec   # Run agent in execute mode
bun agent:lint              # Validate agent registry
bun typecheck               # TypeScript strict check
bun lint                    # ESLint
bun governance:sync         # Dry-run kernel -> ~/.egos governance propagation
bun governance:sync:exec    # Sync kernel -> ~/.egos -> leaf repos
bun governance:sync:local   # Sync kernel -> ~/.egos only (skip leaf repos)
bun governance:check        # Verify kernel and ~/.egos have 0 drift
bun doctor:codex           # Codex lane environment + limitations disclosure + baseline checks
bash ./scripts/oracle-instance-launcher/scripts/run.sh --dry-run  # Oracle OCI launcher check

# Context Tracker (run anytime — mandatory before long multi-step tasks)
bun agent:run context_tracker --dry   # CTX score 0-280 with zone emoji + /end advice
```


## Codex Lane Constraints

- EGOS may run inside Codex terminal lane with non-interactive execution defaults.
- Browser/visual validation depends on explicit browser tool availability in session.
- `~/.egos` state can be ephemeral in cloud/sandbox contexts; rerun sync/check when needed.
- Always disclose these constraints in operational handoffs so expectations are explicit.
