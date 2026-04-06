# AGENTS.md — EGOS Framework Core

> **VERSION:** 1.6.0 | **UPDATED:** 2026-04-05
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
│   ├── shared/                  # Core shared utilities
│   │   └── src/
│   │       ├── llm-provider.ts  # Multi-LLM routing
│   │       ├── rate-limiter.ts  # API rate limiting
│   │       ├── types.ts         # Core types
│   │       └── index.ts
│   ├── search-engine/           # Adaptive Atomic Retrieval (AAR) engine
│   │   └── src/
│   │       ├── in-memory-search.ts  # In-memory search with scoring
│   │       └── index.ts
│   ├── atomizer/                # Semantic content atomization
│   │   └── src/
│   │       ├── default-atomizer.ts  # Sentence-level atom generation
│   │       └── index.ts
│   ├── types/                   # Shared type definitions
│   │   └── src/
│   │       ├── atom.ts          # Atom structure + metadata
│   │       └── index.ts
│   ├── core/                    # Core framework contracts
│   │   └── src/
│   │       ├── contracts.ts     # Search, module, integration contracts
│   │       ├── module.ts        # Module manifest
│   │       └── integration.ts
│   ├── audit/                   # Versioned record audit trail
│   │   └── src/
│   │       ├── versioned-record.ts  # Change tracking + history
│   │       └── index.ts
│   └── registry/                # Module registry + discovery
│       └── src/
│           ├── module-registry.ts  # Runtime module lookup
│           └── index.ts
├── integrations/                # Integration adapters framework
│   ├── _contracts/              # Standardized adapter interfaces
│   │   ├── slack.ts             # Slack messaging adapter
│   │   ├── discord.ts           # Discord adapter
│   │   ├── telegram.ts          # Telegram Bot API adapter
│   │   ├── whatsapp.ts          # WhatsApp Business API adapter
│   │   ├── webhook.ts           # Generic HTTP webhook adapter
│   │   ├── github.ts            # GitHub API adapter
│   │   └── index.ts
│   ├── manifests/              # Release manifests for integration readiness
│   ├── distribution/           # Compact bundles for sharing/install
│   └── README.md                # Integration pattern guide
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

## Framework Capabilities (EGOS-001 — Merged from BLUEPRINT-EGOS)

**Adaptive Atomic Retrieval (AAR):** `@egos/search-engine` + `@egos/atomizer` packages provide semantic content atomization (sentence-level) + in-memory full-text search with scoring. See `packages/search-engine/README.md`.

**Integration Adapters:** `integrations/_contracts` defines standardized interfaces for Slack, Discord, Telegram, WhatsApp, Webhooks, GitHub. Each has `XyzAdapter` contract + `XyzAdapterImpl` stub. Security: env-var credentials, audit-logged. See `integrations/README.md`.

**Integration Release Gate:** integrations are only `validated/shareable` when backed by manifest + SSOT/setup/runbook refs + runtime proof + compact distribution bundle + `bun run integration:check`.

## Commands

```bash
bun agent:list              # List all registered tools + routers (15 total)
bun agent:run <id> --dry    # Run agent in dry-run mode
bun agent:run <id> --exec   # Run agent in execute mode
bun agent:lint              # Validate agent registry
bun typecheck               # TypeScript strict check
bun lint                    # ESLint
bun integration:check      # Validate integration manifests + bundles + smoke commands
bun governance:sync         # Dry-run kernel -> ~/.egos governance propagation
bun governance:sync:exec    # Sync kernel -> ~/.egos -> leaf repos
bun governance:sync:local   # Sync kernel -> ~/.egos only (skip leaf repos)
bun governance:check        # Verify kernel and ~/.egos have 0 drift
bun pr:pack --title "<title>" --out /tmp/pr.md  # Generate signed PR message pack with env context
bun pr:gate --file /tmp/pr.md  # Enforce sign-off + IDE validation checklist evidence
bun pr:audit --owner enioxt --days 15  # Cross-repo PR status audit (active/inactive/recent closed)
bash ./scripts/oracle-instance-launcher/scripts/run.sh --dry-run  # Oracle OCI launcher check

# Context Tracker (run anytime — mandatory before long multi-step tasks)
bun agent:run context_tracker --dry   # CTX score 0-280 with zone emoji + /end advice
```

## Slash Workflows
Canonical workflows in `.agents/workflows/`: start, sync, pr-prep, disseminate, mycelium.

## EGOS as Intelligence — Block Model

### Agent Role Taxonomy (IC / DRI / Player-Coach)

| Agent ID | Role | Rationale |
|---|---|---|
| `ssot-auditor` | **DRI** | Cross-cutting ownership of structural correctness |
| `drift-sentinel` | **DRI** | Temporary owner when drift detected |
| `capability-drift-checker` | **DRI** | Temporary owner when capability gap found |
| `dep-auditor` | **DRI** | Temporary owner on dependency violations |
| `ssot-fixer` | **IC** | Executes plan from ssot-auditor (node executor) |
| `dead-code-detector` | **IC** | Executes targeted cleanup tasks |
| `archaeology-digger` | **IC** | Executes historical analysis tasks |
| `chatbot-compliance-checker` | **IC** | Executes compliance checks per spec |
| `context-tracker` | **IC** | Executes single measurement task |
| `mcp-router` | **IC** | Routes and executes MCP discovery |
| `spec-router` | **IC** | Executes spec validation pipeline |
| `framework-benchmarker` | **Player-Coach** | Self-improves by studying peer frameworks |
| `gem-hunter` | **DRI** | Discovery engine: GitHub/arXiv/HF/PWC — 14 sources, 6-stage pipeline |
| `wiki-compiler` | **DRI** | Compiles raw sources → structured wiki pages (Supabase). Karpathy LLM Wiki pattern |
| `kol-discovery` | **IC** | Fetches X following list, classifies KOLs by domain |
| `gem-hunter-api` | **IC** | REST API for gem-hunter findings (port 3097) |

### Four Pillars (Block → EGOS)

1. **World Model** → `packages/shared/src/world-model.ts` (tasks + agents + caps + signals) — auto-snapshot on /start ✅
2. **Intelligence Layer** → `/coordinator` skill + GH-037 BRAID GRD ✅ (Phase 2 emits Mermaid graph TD with frozen-zone guard, parallel reads, sequential edits, verification gates — generates plan once, ICs/cheap models execute strictly)
3. **Atomic Capabilities** → `docs/CAPABILITY_REGISTRY.md` (160 capabilities, 13 domains)
4. **Signal Layer** → Gem Hunter CCR (seg+qui 2h37 BRT) → feeds world model signals

## Meta-Prompts (Operational)

- `activation.egos-governance` → `.guarani/prompts/meta/egos-activation-governance.md` (used for `/start` and activation diagnostics)

---

## Investigation Documentation (P30)

Complete ecosystem investigation: `docs/INVESTIGATION_FINAL_SUMMARY.md` | Decisions: HUM-001, 002, 003 | Architecture: `docs/SELF_DISCOVERY_ARCHITECTURE.md` | DNS: self.egos.ia.br → 204.168.217.125
