# SYSTEM_MAP.md — EGOS Framework Core

> **VERSION:** 2.5.0 | **UPDATED:** 2026-04-06
> **ROLE:** repo-local map for `/start` in the canonical kernel

<!-- llmrefs:start -->

## LLM Reference Signature

- **Role:** activation map for the `egos` kernel
- **Summary:** points to the local SSOTs that define governance, runtime, shared modules, migration status, and chatbot/mycelium standards
- **Read next:**
  - `.guarani/RULES_INDEX.md` — canonical governance entry point
  - `AGENTS.md` — repo identity, architecture, command surface
  - `TASKS.md` — current sprint and roadmap horizons
  - `docs/DOCUMENTATION_ARCHITECTURE_MAP.md` — documentation read order and permanence rules
  - `docs/CAPABILITY_REGISTRY.md` — reusable capability SSOT
  - `docs/SSOT_REGISTRY.md` — canonical cross-repo SSOT registry
  - `docs/modules/CHATBOT_SSOT.md` — canonical chatbot standard

<!-- llmrefs:end -->

## Canonical Local Truth

- `.guarani/RULES_INDEX.md` — where governance lookup starts
- `AGENTS.md` — what this repo is
- `TASKS.md` — what is next
- `CLAUDE.md` / `.windsurfrules` — environment adapters only
- `docs/SSOT_REGISTRY.md` — what is globally canonical vs locally owned
- `.guarani/` — how reasoning and governance work
- `agents/runtime/` — frozen execution kernel
- `packages/shared/src/` — reusable core modules

## Activation Chain

1. Read `.guarani/RULES_INDEX.md`
2. Read `AGENTS.md`
3. Read `TASKS.md`
4. Read `docs/DOCUMENTATION_ARCHITECTURE_MAP.md`
5. Read `.guarani/PREFERENCES.md` and `.guarani/IDENTITY.md`
6. Read `docs/SSOT_REGISTRY.md`
7. Read `docs/CAPABILITY_REGISTRY.md`
8. Read `docs/modules/CHATBOT_SSOT.md` when chatbot/compliance work is in scope
9. Read `docs/MIGRATION_PLAN.md` when scope touches kernel vs lab boundaries

## Cross-Repo Context

- Global topology lives in `~/.egos/SYSTEM_MAP.md`
- `egos` is the canonical kernel
- `egos-lab` is the incubator and operations surface
- Leaf repos consume governance and shared modules but keep domain truth local
- **Machine Map (classification):** `docs/ECOSYSTEM_CLASSIFICATION_REGISTRY.md` — canonical classification for every surface (kernel/standalone/candidate/lab/internal_infra/archive/discard)

## Freshness Rules

| Section | Owner | Max Staleness | Trigger to Update |
|---------|-------|--------------|-------------------|
| API Map (Guard Brasil REST/MCP) | EGOS kernel | 7 days | Any deploy to Hetzner, port change, or new route |
| Shared Modules table | EGOS kernel | 14 days | New package added to `packages/shared/src/` |
| WhatsApp Runtime Architecture | EGOS kernel | 14 days | New Evolution API instance, new product integration |
| Workflows table | EGOS kernel | 30 days | New `/slash` command or workflow version bump |
| Cross-Repo Context | EGOS kernel | 30 days | New leaf repo added or classification changes |
| Ecosystem Classification Registry | EGOS kernel | 30 days | Any new surface added or classification changed |
| Guard Brasil GTM section | EGOS kernel | 7 days | Any milestone completed or blocker resolved |

Staleness is measured from the `UPDATED` header date. If any section exceeds its max staleness, the `/doctor` command will emit a warning.

## Cross-Repo Update Flow

When a kernel change is made, the following leaf repos require notification (via `bun run governance:sync` or manual SSOT visit):

| Kernel Change | Notify These Repos | Method |
|--------------|-------------------|--------|
| New `packages/shared/` module | 852, carteira-livre, intelink, forja, egos-lab | `governance:sync` + PR in leaf |
| `.guarani/orchestration/` update | ALL leaf repos | `governance:sync:exec` |
| `SSOT_REGISTRY.md` change | ALL leaf repos | `governance:sync:exec` |
| `CAPABILITY_REGISTRY.md` change | egos-lab, 852, br-acc | Manual SSOT visit note |
| New Integration adapter (`integrations/_contracts/`) | forja, 852, carteira-livre | `integration:check` + distribution bundle |
| New Guard Brasil API route | Guard Brasil Web, egos-web | `docs/SYSTEM_MAP.md` update + API changelog |
| CRCDM hook update | ALL repos (via `~/.egos/hooks/`) | `governance:sync:exec` |
| Frozen zone added | ALL repos | `.windsurfrules` sync + AGENTS.md note |

## Current Kernel-Specific Surfaces

- Sync: `scripts/governance-sync.sh`, `scripts/link-ssot-files.sh`
- Utilities: `scripts/oracle-instance-launcher/` (Python OCI launcher with AD retry + capacity-aware handling)
- Validation: `bun run typecheck`, `bun run agent:lint`, `bun run governance:check`
- Integration release gate: `.guarani/orchestration/INTEGRATION_RELEASE_CONTRACT.md`, `integrations/manifests/`, `integrations/distribution/`, `bun run integration:check`
- Core agents: `ssot-auditor`, `drift-sentinel`, `dep-auditor`, `context-tracker`, `mcp-router`, `spec-router`, `gem-hunter`, `wiki-compiler`
- Docs: `docs/MASTER_INDEX.md`, `docs/SSOT_REGISTRY.md`, `docs/DOCUMENTATION_ARCHITECTURE_MAP.md`, `docs/modules/`
- Product architecture refs: `docs/SELF_DISCOVERY_ARCHITECTURE.md`, `docs/EXECUTIVE_SUMMARY_DECISION_MATRIX.md`, `docs/strategy/`

## Shared Modules (@egos/shared)

| Module | File | Status | Description |
|--------|------|--------|-------------|
| LLM Provider | `llm-provider.ts` | ✅ Active | Multi-provider chat (Alibaba/OpenRouter) |
| Model Router | `model-router.ts` | ✅ Active | Task-based model selection (8 models, 10 tasks) |
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

## Workflows

| Workflow | File | Version |
|----------|------|---------|
| /start | `.windsurf/workflows/start.md` | v5.4 |
| /end | `.windsurf/workflows/end.md` | v5.5 |
| /pre | `.windsurf/workflows/pre.md` | v1.0 |
| /prompt | `.windsurf/workflows/prompt.md` | v1.0 |
| /research | `.windsurf/workflows/research.md` | v1.0 |
| /disseminate | `.windsurf/workflows/disseminate.md` | v1.0 |
| /mycelium | `.windsurf/workflows/mycelium.md` | v1.0 |
| /regras | `.windsurf/workflows/regras.md` | v1.0 |
| /stitch | `.windsurf/workflows/stitch.md` | v1.0 |
| /diag | `.windsurf/workflows/diag.md` | v1.0 |

---

## WhatsApp Runtime Architecture (Multi-Channel Pattern)

> **SSOT:** `docs/knowledge/WHATSAPP_SSOT.md` (canonical integration guide)
> **Philosophy:** WhatsApp as workflow surface (alerts, confirmations, status), NOT open-chat platform
> **Validated:** forja-notifications (2026-03-30, state: open)

### Runtime SSOT

```
Hetzner VPS (public IP omitted)
  └─ Evolution API (Single Deployment, port 8080)
      ├─ forja-notifications (ACTIVE)
      ├─ 852-customer-service (future)
      └─ carteira-x-transactions (future)

Vercel Apps
  ├─ Webhook handlers (/api/notifications/whatsapp)
  ├─ Notification service layer
  └─ Admin dashboard (future Control Tower)

Supabase
  ├─ Audit logs (all webhook events)
  ├─ Instance registry (future)
  └─ Message history

Redis (Future P1)
  ├─ Message queue
  ├─ Retry/dead-letter
  └─ Rate limiting
```

### Key Patterns

| Pattern | Location | Status |
|---------|----------|--------|
| **WhatsApp Integration Architecture** | `docs/knowledge/WHATSAPP_SSOT.md` | ✅ Canonical |
| **Evolution API Deployment** | `docs/knowledge/WHATSAPP_SSOT.md` | ✅ Canonical |
| **QR Drift Recovery Protocol** | `docs/knowledge/WHATSAPP_SSOT.md` | ✅ Validated (forja) |
| **Integration Memory SSOT** | `forja/docs/INTEGRATIONS_MEMORY.md` | ✅ Pattern (disseminate) |
| **Multi-Channel Control Tower** | Planned | 📋 P1 |

### Instance Naming Convention

```
{product}-{purpose}

Examples:
- forja-notifications
- 852-customer-service
- carteira-x-transactions
```

### Dissemination Status

| Repo | Status | Instance Name | Notes |
|------|--------|---------------|-------|
| **forja** | ✅ LIVE | forja-notifications | State: open, validated 2026-03-30 |
| **852** | 📋 Planned | 852-customer-service | Future |
| **carteira-livre** | 📋 Planned | carteira-x-transactions | Future |

### Related Documents

- `docs/knowledge/WHATSAPP_SSOT.md` — Canonical integration guide
- `docs/knowledge/HARVEST.md` — Session patterns (Pattern #11, #12, #13, #14)
- `docs/CAPABILITY_REGISTRY.md` — Section 9 (WhatsApp & Messaging)
- `forja/docs/WHATSAPP_SETUP_GUIDE.md` — Step-by-step implementation
- `forja/docs/INTEGRATIONS_MEMORY.md` — Infrastructure SSOT pattern
