# EGOS — Governance Kernel for Auditable AI Systems

> Governance framework, policy enforcement, and reusable safety modules for production AI systems.

EGOS is the open-source kernel that provides governance, orchestration, validation, and reusable surfaces for AI systems requiring traceability, compliance, and operational discipline.

---

## Main Product: Guard Brasil

**Guard Brasil** (`@egosbr/guard-brasil`) is the first public product built on the EGOS kernel.
It adds LGPD protection, ethical validation, evidence trails, and exit policies for AI assistants and flows operating in the Brazilian context.

```bash
# SDK (open source, MIT)
npm install @egosbr/guard-brasil

# Hosted REST API
curl -X POST https://guard.egos.ia.br/v1/inspect \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "CPF do cliente: 123.456.789-00"}'
```

**Detects and handles:** CPF, RG, MASP, REDS, case numbers, license plates, phone numbers, emails, names, and other identifiers relevant to Brazilian scenarios.

**Commercial docs:**
- [1-pager PT-BR](docs/strategy/GUARD_BRASIL_1PAGER.md)
- [Demo script 30min](docs/strategy/GUARD_BRASIL_DEMO_SCRIPT.md)
- [Tiers and pricing](docs/strategy/FREE_VS_PAID_SURFACE.md)

---

## What the Kernel Provides

| Module | Description | Status |
|--------|-------------|--------|
| **Governance DNA** (`.guarani/`) | Identity, orchestration protocol, quality gates, meta-prompts | Active |
| **Agent Runtime** | Registry-based discovery, dry-run/execute, correlation IDs, event bus | Active |
| **Guard Brasil Stack** | PII Scanner BR + LGPD masking + Evidence Chain | Active, v0.2.0 published |
| **Protected Surfaces** | File protection via pre-commit and governance enforcement | Active |
| **SSOT Enforcement** | File limits, drift checks, gitleaks | Active |

---

## Packages

| Package | Description | Status |
|---------|-------------|--------|
| `guard-brasil` | `@egosbr/guard-brasil` v0.2.0 — LGPD PII detection (15 patterns), npm published | Active |
| `shared` | Event bus (Mycelium), Redis bridge, reference graph, LLM provider routing | Active |
| `mcp-governance` | MCP server for governance validation tools | Active |
| `mcp-memory` | MCP server for memory/knowledge tools | Active |
| `atomizer` | Code atomization utilities | Experimental |
| `audit` | Audit trail utilities | Experimental |
| `core` | Core kernel abstractions | Experimental |
| `registry` | Agent registry types and tooling | Active |
| `search-engine` | Search engine abstractions | Experimental |
| `types` | Shared TypeScript types | Active |

---

## What is Deployed

| Service | URL | Status |
|---------|-----|--------|
| Guard Brasil API | `https://guard.egos.ia.br` | Live (Hetzner VPS) |
| Guard Brasil Web | `https://guard.egos.ia.br` | Live |
| Health check | `https://guard.egos.ia.br/health` | Live |

---

## Quick Start

```bash
git clone https://github.com/enioxt/egos.git
cd egos
bun install
bun run doctor              # validate environment
bun run governance:check    # check drift
bun run agent:list          # list registered agents
```

**Test Guard Brasil locally:**
```bash
bun run packages/guard-brasil/src/demo.ts
bun test packages/guard-brasil/src/guard.test.ts
```

---

## Architecture

```
egos/
├── .guarani/               # Governance DNA (identity, orchestration, prompts)
├── agents/
│   ├── runtime/            # Runner + Event Bus
│   ├── registry/           # Agent definitions SSOT
│   └── agents/             # Implementations
├── packages/
│   ├── guard-brasil/       # @egosbr/guard-brasil v0.2.0
│   ├── shared/             # Event bus, Redis bridge, LLM router
│   ├── mcp-governance/     # MCP governance server
│   ├── mcp-memory/         # MCP memory server
│   └── (6 more)            # atomizer, audit, core, registry, search-engine, types
├── apps/
│   ├── api/                # Guard Brasil REST + MCP reference server
│   └── guard-brasil-web/   # Public landing page
├── scripts/                # doctor.ts, governance-sync.sh, kernel utilities
├── TASKS.md                # Live roadmap
└── docs/concepts/          # Architecture references (see status in each file)
```

---

## Ecosystem (Leaf Repos)

| Repo | Purpose | Status |
|------|---------|--------|
| [egos-lab](https://github.com/enioxt/egos-lab) | Lab + incubator (agents, apps, Telegram bot) | Active |
| [852](https://github.com/enioxt/852) | Institutional chatbot for public safety | Production |
| [carteira-livre](https://github.com/enioxt/carteira-livre) | Marketplace SaaS | Production |
| [FORJA](https://github.com/enioxt/forja) | Chat-First ERP for small businesses | MVP |
| [br-acc](https://github.com/enioxt/br-acc) | Brazilian accountability data mining | Active |

---

## Roadmap

See [TASKS.md](TASKS.md) for the live roadmap and current sprint priorities.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). All commits pass through:
- `gitleaks` — secret detection
- `tsc --noEmit` — strict typecheck
- frozen zones check — canonical file protection
- governance drift check — `~/.egos/` sync

## License

MIT — [`@egosbr/guard-brasil`](packages/guard-brasil/) also MIT.
