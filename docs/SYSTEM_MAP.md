# SYSTEM_MAP.md — EGOS Framework Core

> **VERSION:** 2.3.0 | **UPDATED:** 2026-03-30
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
- Integration release gate: `.guarani/orchestration/INTEGRATION_RELEASE_CONTRACT.md`, `integrations/manifests/`, `integrations/distribution/`, `bun run integration:check`
- Agents:
  - `dep_auditor`, `archaeology_digger`, `chatbot_compliance_checker`, `context_tracker`
  - `ethik_agent`: x402 Tokenomics, GCP Dynamic Key Gateway, and Donation Engine
  - `atrian_agent`: Ethical Compliance Gate
  - `mycelium_agent`: Event Bus and Mesh Logging
- Docs: `docs/concepts/mycelium/`, `docs/archaeology/`, `docs/modules/`
- **Guard Brasil GTM (2026-03-30):**
  - `docs/SESSION_GUARDBRASIL_DIAGNOSTIC.md` — session diagnostic summary
  - `docs/_current_handoffs/handoff_guardbrasil_gtm.md` — complete GTM handoff (architecture, revenue math, critical blocker M-007)
  - `docs/strategy/GUARD_BRASIL_TRANSPARENCIA_RADICAL.md` — pricing model spec (pay-per-use + IA reports)
  - `docs/_current_handoffs/GUARD_BRASIL_ARCHITECTURE_STACK.md` — 4-layer technical blueprint
  - `docs/_current_handoffs/ROADMAP_3WEEKS_GUARD_BRASIL_GTM.md` — week-by-week execution plan

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
| /start (canonical ops) | `.agents/workflows/start-workflow.md` | v1.0 |
| /sync (canonical ops) | `.agents/workflows/sync.md` | v1.0 |
| /pr (canonical ops) | `.agents/workflows/pr-prep.md` | v1.0 |
| /disseminate (canonical ops) | `.agents/workflows/disseminate.md` | v1.0 |
| /mycelium (canonical ops) | `.agents/workflows/mycelium.md` | v1.0 |
| /start | `.windsurf/workflows/start.md` | v5.4 |
| /end | `.windsurf/workflows/end.md` | v5.5 |
| /pre | `.windsurf/workflows/pre.md` | v1.0 |
| /prompt | `.windsurf/workflows/prompt.md` | v1.0 |
| /research | `.windsurf/workflows/research.md` | v1.0 |
| /disseminate | `.windsurf/workflows/disseminate.md` | v1.0 |
| /mycelium | `.windsurf/workflows/mycelium.md` | v1.0 |
| /regras | `.windsurf/workflows/regras.md` | v1.0 |

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
