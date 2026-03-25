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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for governance rules.
All contributions must pass pre-commit hooks (gitleaks + tsc + frozen zones + SSOT drift).

## License

MIT
