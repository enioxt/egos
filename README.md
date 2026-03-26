# EGOS — Orchestration Kernel for Governed AI Agents

> Rules govern agents. Agents enforce rules. Community evolves rules.

EGOS is an open-source framework that provides governance, orchestration, and
runtime infrastructure for AI-powered code agents. It is the invisible layer
that makes agents think like governed systems.

## What EGOS Provides

- **Governance DNA** (`.guarani/`) — Identity, preferences, orchestration
  protocol, quality gates, and meta-prompt system
- **Agent Runtime** — Registry-based discovery, dry-run/execute modes,
  correlation IDs, JSONL structured logging, event bus
- **Multi-LLM Routing** — Alibaba Qwen (primary), OpenRouter/Gemini (fallback),
  with cost tracking and provider abstraction
- **Frozen Zones** — Protected core files with pre-commit enforcement
- **SSOT Enforcement** — File size limits, drift checks, and gitleaks
- **Stitch-First UI Flow** — Screen ideation through Google Stitch with prompt-pack + `.zip` intake contract before coding

## Quick Start

```bash
git clone https://github.com/enioxt/egos.git
cd egos
bash setup.sh
bun typecheck
bun governance:check
bun agent:list
```

## Operational Workflows & PR Discipline

Canonical operational workflows live in `.agents/workflows/`:

- `/start` → `.agents/workflows/start-workflow.md`
- `/pr` → `.agents/workflows/pr-prep.md`
- `/sync` → `.agents/workflows/sync.md`

PR preparation and merge gate commands:

```bash
bun pr:pack --title "[AREA] summary" --out /tmp/pr-pack.md
bun pr:gate --file /tmp/pr-pack.md
```

`pr:gate` enforces:
- `Signed-off-by` footer
- Windsurf validation evidence
- Antigravity validation evidence
- test rerun evidence after IDE-assisted changes

## Configuring Instructions in Codex

Use this baseline in Codex project instructions:

1. Always load these files first: `AGENTS.md`, `TASKS.md`, `.windsurfrules`, `docs/SYSTEM_MAP.md`.
2. Treat `.agents/workflows/` as canonical slash-command source (`/start`, `/pr`, `/disseminate`, `/sync`).
3. For governance propagation in container environments, use:
   - `EGOS_KERNEL=/workspace/egos bun run governance:sync:exec`
   - `EGOS_KERNEL=/workspace/egos bun run governance:check`
4. Require signed PR packs:
   - `bun run pr:pack --title "[AREA] summary" --out /tmp/pr-pack.md`
   - `bun run pr:gate --file /tmp/pr-pack.md`

## Architecture

```
egos/
├── .guarani/           # Governance DNA
├── agents/
│   ├── runtime/        # Runner + Event Bus (FROZEN)
│   ├── registry/       # Agent definitions (SSOT)
│   └── cli.ts          # Agent CLI
├── packages/shared/    # Core utilities (LLM, rate limiter)
├── .windsurfrules      # Active governance
├── frozen-zones.md     # Protected files
├── AGENTS.md           # System map
└── TASKS.md            # Live roadmap
```

## Ecosystem

EGOS is the kernel. Leaf repos consume it:

| Repo | Purpose |
|------|---------|
| [egos-lab](https://github.com/enioxt/egos-lab) | Lab + incubator (29 agents, apps, experiments) |
| [852](https://github.com/enioxt/852) | Institutional intelligence chatbot |
| [EGOS-Inteligencia](https://github.com/enioxt/EGOS-Inteligencia) | Public-data intelligence graph |
| [carteira-livre](https://github.com/enioxt/carteira-livre) | Production SaaS marketplace |

## Business Foundation (Operator-First)

This is the canonical business baseline before scaling implementation.

### 1) Objective

Build one flagship governed AI product that solves a high-value, high-frequency
compliance/decision problem in Brazil with auditable outputs and low operating cost.

### 2) Problem to Solve

Teams using multiple AI tools struggle with:
- non-auditable decisions,
- prompt inconsistency across environments,
- weak provenance of who changed what and where,
- fragmented governance and duplicated standards.

### 3) Personas

- **Operator/Founder:** needs speed + control + proof-of-work.
- **Compliance/SecOps lead:** needs traceability, policy enforcement, and risk gates.
- **Engineering lead:** needs reusable modules, low drift, and predictable delivery.

### 4) Go-To-Market (GTM) — Initial

- **Wedge:** governance-as-code + provenance signatures + Brazilian compliance defaults.
- **Entry offer:** implementation + audit-ready setup in pilot repositories.
- **Expansion:** reusable packages/MCP servers (`@egos/shared`, governance/memory MCP).
- **Proof:** measurable reduction in drift, incident risk, and manual review time.

### 5) Documentation & Rules Order (Mandatory)

1. Define objective/problem/personas/GTM in SSOT.
2. Define policy contracts (governance + signatures + claim gates).
3. Run adoption via `/start` + `governance:sync:exec` + `governance:check`.
4. Only then expand to new agents/products.

### 6) Next System to Build (Knowledge Compiler)

Create a governed "market intelligence compiler" that ingests books, papers,
codebases, benchmark reports, and platform docs, then normalizes them into:
- decision rules,
- implementation patterns,
- risk controls,
- testable playbooks.

All outputs must be source-linked, versioned, and attached to explicit target
problem statements (no generic knowledge dumps).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for governance rules.
All contributions must pass pre-commit hooks (gitleaks + tsc + frozen zones + SSOT drift).

## License

MIT
