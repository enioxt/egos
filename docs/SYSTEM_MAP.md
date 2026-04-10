# SYSTEM_MAP.md — EGOS Framework Core

> **VERSION:** 3.0.0 | **UPDATED:** 2026-04-10
> **ROLE:** repo-local activation map for `/start` — single source of read-order truth

<!-- llmrefs:start -->

## LLM Reference Signature — FAST PATH (/start lite)

Load these 5 files at session start for full context:

```
1. ~/.claude/CLAUDE.md          — rules v4.0 (T0>T1>T2>T3>T4, 263 lines)
2. TASKS.md                     — current work (grep top P0s)
3. docs/REPO_MAP.md             — 7 groups, which repos to touch
4. memory/MEMORY.md             — latest session context
5. docs/jobs/ (last 3 days)    — CCR output + sentinel alerts
```

Full activation: read sections below in order only when scope requires it.

- **Read next (governance scope):** `.guarani/RULES_INDEX.md` → `AGENTS.md`
- **Read next (architecture scope):** `docs/SSOT_REGISTRY.md` → `docs/CAPABILITY_REGISTRY.md`
- **Read next (agent scope):** `agents/registry/agents.json` → `docs/agents/INDEX.md`
- **Read next (audit/evidence scope):** `docs/audit/KERNEL_AUDIT.md` → `docs/governance/QUORUM_PROTOCOL.md`
- **Read next (site/timeline scope):** `apps/egos-site/src/server.ts` → `docs/strategy/EGOS_PATH_B_C_PLAN.md`

<!-- llmrefs:end -->

## Canonical Local Truth

| File | Role | Updated |
|------|------|---------|
| `~/.claude/CLAUDE.md` | Global rules v4.0 (T0→T4 tiers, 263 lines) | 2026-04-10 |
| `TASKS.md` | Current sprint (1300 lines, P0..P2) | live |
| `AGENTS.md` | Repo identity + command surface | 2026-04-06 |
| `.guarani/RULES_INDEX.md` | Governance entry point | 2026-04-09 |
| `docs/REPO_MAP.md` | 7-group repo classification (canonical) | 2026-04-09 |
| `agents/registry/agents.json` | 24 agents registry v2.4.0 | 2026-04-10 |
| `docs/agents/INDEX.md` | Per-agent docs index | 2026-04-10 |
| `docs/audit/KERNEL_AUDIT.md` | CLAUDE.md v4 section audit (4/6/6) | 2026-04-10 |
| `docs/strategy/EGOS_PATH_B_C_PLAN.md` | Path B (showcase) + C (EGOS Lab R$20/mês) | 2026-04-10 |
| `docs/governance/QUORUM_PROTOCOL.md` | Multi-LLM review for critical decisions | 2026-04-10 |
| `docs/SSOT_REGISTRY.md` | Cross-repo SSOT ownership | 2026-04-06 |
| `docs/CAPABILITY_REGISTRY.md` | Reusable capability SSOT (33 unbacked claims) | 2026-04-10 |
| `.guarani/` | Governance rules (23 active files post-cleanup) | 2026-04-09 |
| `agents/runtime/` | FROZEN execution kernel | — |
| `packages/shared/src/` | Reusable core modules | — |

## Activation Chain (full)

1. `~/.claude/CLAUDE.md` — global rules (auto-loaded by Claude Code)
2. `CLAUDE.md` (project) — repo adapter
3. `TASKS.md` — what's next (grep: `- \[ \] .*P0`)
4. `docs/REPO_MAP.md` — which repos are in scope today
5. `memory/MEMORY.md` — last session context (auto-loaded)
6. `.guarani/RULES_INDEX.md` — governance canon
7. `agents/registry/agents.json` — agent registry (when agent scope)
8. `docs/CAPABILITY_REGISTRY.md` — capability SSOT (when building features)
9. `docs/strategy/EGOS_PATH_B_C_PLAN.md` — 90-day plan (weekly review)

## Cross-Repo Context

- `egos` is the canonical kernel (PLATFORM group)
- `egos-lab` is ARCHIVING — no new features
- **Canonical repo classification:** `docs/REPO_MAP.md` (use this, ignore older inventory files)
- Leaf repos consume governance from kernel via `governance:sync`

### Current strategic tracks (2026-04-10)

| Track | SSOT | Status |
|-------|------|--------|
| Encapsulation (7 layers) | `docs/strategy/EGOS_PATH_B_C_PLAN.md` §6 | L0 ✅ L1 ✅ L2+ pending |
| EGOS Lab community R$20/mês | `docs/strategy/EGOS_PATH_B_C_PLAN.md` §3 | planning |
| egos-site + Timeline blog | `apps/egos-site/src/server.ts` | DNS propagating |
| Showcase article | `docs/strategy/EGOS_PATH_B_C_PLAN.md` §2 | week 10+ |
| Guard Brasil monetization | `docs/GTM_SSOT.md` | active |

### Key URLs (live)

| Service | URL | Status |
|---------|-----|--------|
| Guard Brasil | https://guard.egos.ia.br/health | ✅ live |
| EGOS HQ | https://hq.egos.ia.br | ✅ live |
| 852 chatbot | https://852.egos.ia.br | ✅ live |
| egos.ia.br (Hono site) | https://egos.ia.br/timeline | DNS propagating |
| Gem Hunter | https://gemhunter.egos.ia.br | ✅ live |

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
