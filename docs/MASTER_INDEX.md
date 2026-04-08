# EGOS MASTER INDEX — Universal SSOT Registry

> **The canonical source of truth for everything EGOS.**  
> **Version:** 1.4.0 | **Created:** 2026-04-06 | **Updated:** 2026-04-08  
> **Purpose:** Single document to answer "What do we have? Where is it? What's its status?"

<!-- llmrefs:start -->

## LLM Reference Signature

- **Role:** Universal SSOT registry for entire EGOS ecosystem
- **Summary:** 17 repos, **19 agents**, 73 scripts, 90.6% coverage — Updated 2026-04-07 with verified evidence
- **Type:** FIXO — Master SSOT, always authoritative
- **Read next:**
  - `.guarani/RULES_INDEX.md` — canonical governance entry point
  - `docs/SSOT_REGISTRY.md` — ownership and freshness contracts
  - `docs/DOCUMENTATION_ARCHITECTURE_MAP.md` — documentation read order and permanence map
- **Update when:** Any structural change to repos, agents, capabilities, integrations

<!-- llmrefs:end -->

---

## 📋 Document Contract

**This document IS the master SSOT for:**
- All repositories and their classification
- All agents (active, dead, missing)
- All capabilities and where they're implemented
- All integrations and their health
- All tasks (consolidated from all TASKS.md files)
- All scripts, tools, and automation
- All duplication/drift issues requiring cleanup

**Update Rule:** This document MUST be updated whenever:
- New agent added (agents.json change)
- New repo created or classified
- New capability implemented
- Integration status changes
- Major commit changes ecosystem structure
- Duplicate/legacy code discovered

**Read Order for AIs:**
1. `.guarani/RULES_INDEX.md` — governance canon
2. This document (`MASTER_INDEX.md`) — scope everything
3. `AGENTS.md` — kernel identity
4. `SSOT_REGISTRY.md` — cross-repo ownership
5. `DOCUMENTATION_ARCHITECTURE_MAP.md` — document roles and permanence
6. `SYSTEM_MAP.md` — activation flow
7. `TASKS.md` — current execution priorities
8. `docs/EGOS_STATE_OF_THE_ECOSYSTEM.md` — state-of-the-ecosystem snapshot (2026-04-08+)
8. `docs/business/MONETIZATION_SSOT.md` — ecosystem monetization, partner model, founder-partner fit

---

## 🗺️ Repository Universe (Mapped Repo Surfaces)

### Classification Map

| Repo | Classification | Path | Grade | Health | Notes |
|------|---------------|------|-------|--------|-------|
| **egos** | kernel | `/home/enio/egos` | A | ✅ Active | Core governance + Guard Brasil + Self-Discovery (planned) |
| **egos-lab** | lab/incubator | `/home/enio/egos-lab` | B | ⚠️ Archiving | Being consolidated into kernel |
| **852** | standalone | `/home/enio/852` | C | ✅ Production | Police chatbot, 27 tools |
| **EGOS Inteligência (br-acc)** | standalone | `/home/enio/br-acc` | C | ✅ Production | OSINT platform, 77M Neo4j — boundary documented as standalone |
| **carteira-livre** | candidate | `/home/enio/carteira-livre` | C | ✅ Production | 191 profiles, 234 APIs |
| **forja** | candidate | `/home/enio/forja` | B | ✅ Active | CRM/ERP + WhatsApp live |
| **santiago** | candidate | `/home/enio/santiago` | C | ⚠️ Broken | Vercel deploy blocked |
| **intelink** | candidate | `/home/enio/INTELINK` | C | ❌ Dormant | 128 days stale |
| **commons** | candidate | `/home/enio/commons` | C | ⚠️ Empty | AGENTS.md + TASKS.md created 2026-04-06 |
| **policia** | lab | `/home/enio/policia` | C | ✅ Active | DHPP workspace |
| **INPI** | candidate | `/home/enio/INPI` | C | ? | Needs verification |
| **smartbuscas** | lab | `/home/enio/smartbuscas` | C | ⚠️ Rebrowser | Cloudflare bypass migration |

### Archive Candidates (11 Repos to Archive)

Per COMPLETE_REPO_INVENTORY_2026-04-03.md:
- egos-cortex (46 days stale)
- intelink (128 days stale) 
- DHPP (unknown state)
- EGOSv5, EGOSv3, EGOSv2 (superseded)
- BLUEPRINT-EGOS (unfinished)
- EGOSystem (260 days stale)
- Pochete2.0 (292 days stale)
- chacreamento (test repo)
- guia-INPI (reference only)

---

## 🤖 Agent Registry (18 Agents)

### Active Agents (16)

| # | Agent ID | Entrypoint | Status | Last Verified |
|---|----------|------------|--------|---------------|
| 1 | ssot-auditor | `agents/agents/ssot-auditor.ts` | ✅ | 2026-04-06 |
| 2 | ssot-fixer | `agents/agents/ssot-fixer.ts` | ✅ | 2026-04-06 |
| 3 | drift-sentinel | `agents/agents/drift-sentinel.ts` | ✅ | 2026-04-06 |
| 4 | dep-auditor | `agents/agents/dep-auditor.ts` | ✅ | 2026-04-06 |
| 5 | archaeology-digger | `agents/agents/archaeology-digger.ts` | ✅ | 2026-04-06 |
| 6 | dead-code-detector | `agents/agents/dead-code-detector.ts` | ✅ | 2026-04-06 |
| 7 | capability-drift-checker | `agents/agents/capability-drift-checker.ts` | ✅ | 2026-04-06 |
| 8 | context-tracker | `agents/agents/context-tracker.ts` | ✅ | 2026-04-06 |
| 9 | framework-benchmarker | `agents/agents/framework-benchmarker.ts` | ✅ | 2026-04-06 |
| 10 | mcp-router | `agents/agents/mcp-router.ts` | ✅ | 2026-04-06 |
| 11 | spec-router | `agents/agents/spec-router.ts` | ✅ | 2026-04-06 |
| 12 | gem-hunter | `agents/agents/gem-hunter.ts` | ✅ | 2026-04-06 |
| 13 | kol-discovery | `scripts/kol-discovery.ts` | ✅ | 2026-04-06 |
| 14 | gem-hunter-api | `agents/api/gem-hunter-server.ts` | ✅ | 2026-04-06 |
| 15 | wiki-compiler | `agents/agents/wiki-compiler.ts` | ✅ | 2026-04-06 |
| 16 | **agent-validator** | `agents/agents/agent-validator.ts` | ✅ **NEW** | 2026-04-06 |

### Dead Agents (2)

| # | Agent ID | Entrypoint | Death Reason |
|---|----------|------------|--------------|
| 1 | chatbot-compliance-checker | `agents/agents/chatbot-compliance-checker.ts` | prove-or-kill: no implementation |
| 2 | gtm-harvester | `agents/agents/gtm-harvester.ts` | hangs on --dry, no rate limiting |

---

## 📦 Kernel Packages (9 Packages)

| Package | Location | Capabilities | Status |
|---------|----------|--------------|--------|
| @egos/shared | `packages/shared/src/` | LLM provider, ATRiAN, PII scanner, rate limiter, telemetry, model-router | ✅ Active |
| @egos/guard-brasil | `packages/guard-brasil/src/` | LGPD PII detection (15 patterns), provenance, receipts | ✅ v0.2.0 Live |
| @egos/search-engine | `packages/search-engine/src/` | AAR in-memory search | ✅ Active |
| @egos/atomizer | `packages/atomizer/src/` | Semantic atomization | ✅ Active |
| @egos/core | `packages/core/src/` | Contracts, PRI safety gate | ✅ Active |
| @egos/audit | `packages/audit/src/` | Versioned record tracking | ✅ Active |
| @egos/registry | `packages/registry/src/` | Module lookup | ✅ Active |
| @egos/types | `packages/types/src/` | Shared types | ✅ Active |
| @egos/mcp-governance | `packages/mcp-governance/src/` | MCP tooling | ✅ Active |

---

## 🚀 Applications (6 Apps in egos/apps/)

| App | Path | Status | Domain | Port |
|-----|------|--------|--------|------|
| **Guard Brasil API** | `apps/api/` | ✅ LIVE | guard.egos.ia.br | 3099 |
| **Guard Brasil Web** | `apps/guard-brasil-web/` | ✅ Active | — | — |
| **EGOS HQ** | `apps/egos-hq/` | ✅ LIVE | hq.egos.ia.br | 3060 |
| **EGOS Gateway** | `apps/egos-gateway/` | ✅ LIVE | — | 3050 |
| **EGOS Commons** | `apps/commons/` | ⚠️ In Progress | — | — |
| **Agent-028 Template** | `apps/agent-028-template/` | 📋 Planned | — | — |

---

## 🧪 egos-lab Applications (Extended Catalog)

### Eagle Eye — Brazilian Gazette Monitor

| Property | Value |
|----------|-------|
| **Path** | `egos-lab/apps/eagle-eye/` |
| **Status** | ✅ Active (84 territórios, 36 oportunidades) |
| **Version** | 0.1.0 |
| **Domain** | eagle-eye.egos.ia.br (planned) |
| **Description** | Alerta antecipado de licitações de tecnologia para empresas que vendem pro governo |

**Components:**
- `fetch_gazettes.ts` — Querido Diário API client
- `analyze_gazette.ts` — AI analysis pipeline (Gemini 2.0 Flash)
- `idea_patterns.ts` — 26 detection patterns em 3 tiers
- `territories.ts` — 84 territórios configurados
- `batch_scan.ts` — Daily batch processing (08:00 UTC)
- `ui/server.ts` — Bun HTTP server + React frontend

**ICP:** Empresas de software em pregões, consultorias regulatórias, escritórios de direito público

**Revenue Model:** R$99-499/mês por integrador municipal

**Cross-References:**
- Querido Diário API: https://queridodiario.ok.org.br/
- PNCP API enrichment: `pncp-client.ts`
- SSOT: `egos-lab/apps/eagle-eye/README.md`
- Tasks: EAGLE-000..023 em `egos-lab/TASKS.md`

---

### Gem Hunter — Discovery Engine

| Property | Value |
|----------|-------|
| **Agent ID** | AGENT-027 |
| **Path** | `egos/agents/agents/gem-hunter.ts` |
| **Status** | ✅ Active (288 gems catalogados) |
| **Version** | 5.0 |
| **API** | gemhunter.egos.ia.br:3095/3097 |
| **Description** | Preference-driven discovery engine for open-source tools, models, papers, frameworks |

**Sources:**
- GitHub Search API (code + repos)
- HuggingFace Hub API
- arXiv API
- Exa API
- Reddit (no auth)
- StackOverflow (no auth)
- ProductHunt (via Exa)

**Features:**
- `--lang=typescript` — Filter by language
- `--license=mit` — Filter by license
- `--min-stars=100` — Star threshold
- `--deep` — SSOT Lego atomization
- `--track=x-signals` — Daily X signals
- `--history` — SQLite trending (multi-run)

**ICP:** Devs, VCs, aceleradoras, research teams

**Revenue Path:** R$50/mês (100 scans) → R$350 (1k) → Enterprise

**Cross-References:**
- Dashboard: `gemhunter.egos.ia.br`
- Telegram: `/hunt`, `/sector`, `/trending` commands
- API: `agents/api/gem-hunter-server.ts`
- Tasks: GH-001..071 em `egos/TASKS.md`

---

### Intelink — Knowledge Bridge (Legacy/Dormant)

| Property | Value |
|----------|-------|
| **Path** | `/home/enio/INTELINK` |
| **Status** | ❌ Dormant (128 days stale) |
| **Type** | Python experiment — knowledge aggregation |
| **Stack** | FastAPI backend + React frontend |

**Components:**
- `backend/` — FastAPI Python server
- `frontend/` — React SPA
- `docker/` — Docker compose setup

**Note:** Candidate for archive per HQC-014. Migration content to kernel if valuable.

**Cross-References:**
- Migration notes: `MIGRACAO_EGOS_INTELIGENCIA.md`
- Archive decision: HQC-014

---

### EGOS Inteligência — Intelligence Hub

| Property | Value |
|----------|-------|
| **Path** | `/home/enio/egos-inteligencia` |
| **Status** | ✅ Active (7,787 lines TASKS.md) |
| **Type** | Intelligence hub + ETL pipelines |
| **Stack** | Python ETL + API + Frontend |

**Components:**
- `etl/` — Data extraction pipelines
- `api/` — REST API surface
- `frontend/` — Web interface
- `scripts/` — Automation scripts

**Status:** Recently created (April 2026) — consolidating intelligence capabilities.

**Cross-References:**
- Tasks: 7,787 lines in `TASKS.md`
- AGENTS.md: `/home/enio/egos-inteligencia/AGENTS.md`

---

## 🔧 Scripts & Tools Catalog

### Core Scripts (24 in egos/scripts/)

| Script | Purpose | Status |
|--------|---------|--------|
| `check-doc-proliferation.sh` | Detect document bloat | ✅ Active |
| `check-legacy-code.sh` | Detect legacy patterns | ✅ Active |
| `claude-code-init.sh` | IDE setup | ✅ Active |
| `codex-doctor.sh` | Codex diagnostics | ✅ Active |
| `daily-knowledge-sync.sh` | Knowledge sync | ✅ Active |
| `dream-cycle/log-harvester.sh` | Overnight log harvest | ✅ DC-002 |
| `egos-init.sh` | EGOS bootstrap | ✅ Active |
| `egos-repo-health.sh` | Multi-repo health check | ✅ Active |
| `file-intelligence.sh` | Pre-commit intelligence | ✅ Active |
| `governance-sync.sh` | SSOT propagation | ✅ Active |
| `link-ssot-files.sh` | Symlink management | ✅ Active |
| `obsidian-llm-start.sh` | Obsidian bridge | ✅ Active |
| `safe-push.sh` | Protected push | ✅ Active |
| `setup-obsidian-mcp.sh` | MCP setup | ⏳ Pending |
| `start-v6.sh` | Session init v6 | ✅ Active |
| `sync-all-leaf-repos.sh` | Multi-repo sync | ✅ Active |
| `workflow-sync-check.sh` | Workflow validation | ✅ Active |

### Oracle Launcher Scripts (3)

- `install_service.sh`
- `run.sh`
- `setup-payg-protections.sh`

---

## 🔌 Integration Matrix

### MCP Servers (12 Total)

| # | MCP | Status | Install Date | Blocker |
|---|-----|--------|--------------|---------|
| 1 | filesystem | ✅ Built-in | — | — |
| 2 | memory | ✅ Built-in | — | — |
| 3 | sequential-thinking | ✅ Built-in | — | — |
| 4 | github | ✅ Active | — | — |
| 5 | supabase | ✅ Active | — | — |
| 6 | exa | ✅ Active | — | — |
| 7 | firecrawl | ✅ Installed | 2026-04-06 | — |
| 8 | brave-search | ✅ Installed | 2026-04-06 | — |
| 9 | playwright | ✅ Installed | 2026-04-06 | — |
| 10 | obsidian | ⏳ Pending | — | Needs vault path from Enio |
| 11 | stripe | ⏳ Pending | — | Needs Stripe secret key (VPS only) |
| 12 | telegram | ⏳ Pending | — | Needs bot token |

### Integration Contracts (6 Adapters)

| Adapter | Contract | Implementation | Manifest |
|---------|----------|----------------|----------|
| Slack | `slack.ts` | Stub | ⚠️ Stub manifest | HQC-007 stub created |
| Discord | `discord.ts` | Stub | ⚠️ Stub manifest | HQC-007 stub created |
| Telegram | `telegram.ts` | Stub | ⚠️ Stub manifest | HQC-007 stub created |
| WhatsApp | `whatsapp.ts` | ✅ Forja | ✅ whatsapp-runtime.json | Validated |
| Webhook | `webhook.ts` | Stub | ⚠️ Stub manifest | HQC-007 stub created |
| GitHub | `github.ts` | Stub | ⚠️ Stub manifest | HQC-007 stub created |

**Action Required:** Implement adapters to move from stub → validated (future sprint)

### VPS Services (Hetzner 204.168.217.125)

| Service | Port | Status | Health |
|---------|------|--------|--------|
| Guard Brasil API | 3099 | ✅ Live | Healthy |
| Evolution API | 8080 | ✅ Live | WhatsApp ready |
| EGOS HQ | 3060 | ✅ Live | Dashboard OK |
| EGOS Gateway | 3050 | ✅ Live | Gateway OK |
| Gem Hunter Server | 3095/3097 | ✅ Live | API ready |
| forja-notifications | — | ✅ Live | State: open |

---

## 📊 Task Consolidation (From All TASKS.md Files)

### egos/TASKS.md (v2.44.0) — current kernel snapshot

**Active P0 Tasks:**
- EGOS-163: Pix billing integration
- MONETIZE-011: Deploy v0.2.3 to VPS
- MONETIZE-012: NOWPayments webhook
- MASTER-005: NLP intent classifier
- INC-001: Scheduled agent force-push investigation
- GTM-002: X.com showcase thread
- GTM-009: LinkedIn post
- M-007: 5 outreach emails to DPOs
- HQC-001..HQC-006: HQ truth normalization + `/start` evidence

**Documentation + governance snapshot:**
- HQV2-000..HQV2-010: Dashboard v2 implementation track (mounted data + API routes + pages)
- SD-001..SD-019: Self-Discovery planning with explicit dependencies and named rollout gates
- GOV-001..GOV-007: governance mesh cleanup backlog (Claude adapter, workflows, skills, mirror, repo mesh)

**Active P1 Tasks:**
- EGOS-165: White-label outreach
- EGOS-166: REST API gateway mode
- EGOS-169: @aiready/pattern-detect
- EGOS-173: CRCDM llmrefs hooks
- KB-017: Auto-learning from git commits
- DC-004: Intelligence-engine.ts
- HQC-007..HQC-012: HQ wiring + contracts + anti-hardcode data flow
- OC-006..OC-023: OpenClaw roadmap

**Active P2 Tasks:**
- GH-013..GH-024: Pair studies (OpenHands, LangGraph, etc.)
- WM-001..WM-016: World Model enhancements
- X-009..X-013: X.com automation expansion
- HQC-013..HQC-015: ecosystem consolidation + archive cleanup

### egos-lab/TASKS.md (141 lines — Compressed)

- LAB-ARCHIVE-001..006: Migration to kernel
- EAGLE-000..023: Eagle Eye procurement
- GEM-HUNTER: Dashboard + API

### 852/TASKS.md (20,749 lines — Needs compression)

- S67: SSOT telemetry tests
- Multiple capability migrations pending

### br-acc/TASKS.md (82,633 lines — Needs audit)

- BRACC tasks for OSINT platform
- ETL pipeline tasks

### carteira-livre/TASKS.md (42,764 lines)

- WhatsApp AI flow E2E test
- QR code self-hosted

### forja/TASKS.md (32,560 lines)

- WhatsApp integration complete
- 7 migrations applied

---

## ⚠️ Duplications & Drift Detected

### Code Duplications

| Duplicate | Location A | Location B | Action |
|-----------|-----------|------------|--------|
| Shared packages | `egos/packages/shared/` | `egos-lab/packages/shared/` | Migrate to kernel |
| PII scanner | `egos/packages/shared/src/pii-scanner.ts` | `852/src/lib/pii-scanner.ts` | Consolidate to @egosbr/guard-brasil |
| Agent runtime | `egos/agents/runtime/` | `egos-lab/agents/runtime/` | Kernel is canonical |
| AI provider | `egos/packages/shared/src/llm-provider.ts` | `852/src/lib/ai-provider.ts` | Use kernel version |
| Rate limiter | `egos/packages/shared/src/rate-limiter.ts` | `egos-lab/packages/shared/src/rate-limiter.ts` | Use kernel version |

### Document Duplications

| Document | Count | Locations | Action |
|----------|-------|-----------|--------|
| HARVEST.md | 3x | egos-lab/docs/ duplicated | Run `bun wiki:dedup` (KB-019) |
| Shared package docs | 2x | kernel + lab | Deprecate lab version |
| Agent registry | 2x | kernel v2.2 + lab v1.0 | Lab is parallel, not canonical |

### Governance Drift

| Surface | Kernel Claim | Lab Claim | Status |
|---------|-------------|-----------|--------|
| Brand guide | `egos/docs/KERNEL_MISSION_CONTROL.md` | `egos-lab/branding/BRAND_GUIDE.md` | ⚠️ CONFLICTED (EGOS-132) |
| Shared packages | Kernel canonical | Lab deprecated | Migration in progress |
| SSOT pointers | Required in all repos | Missing in 6 repos | HQC-004 needed |

---

## 💎 Gems Catalog (Valuable Concepts & Patterns)

### Architecture Patterns

| Pattern | Location | Value | Status |
|---------|----------|-------|--------|
| **PRI Safety Gate** | `packages/core/src/guards/pri.ts` | Protocolo de Recuo por Ignorância | ✅ EGOS-070 |
| **ATRiAN Ethics** | `packages/shared/src/atrian.ts` | 7-axiom validation | ✅ Active |
| **Auditable Sandbox** | `docs/patterns/AUDITABLE_SANDBOX_PATTERN.md` | 4-zone UX pattern | ✅ Pattern |
| **Integration Memory** | `forja/docs/INTEGRATIONS_MEMORY.md` | Infrastructure SSOT | ✅ Pattern |
| **Mycelium Graph** | `packages/shared/src/mycelium/reference-graph.ts` | 27 nodes, 32 edges | ✅ Active |
| **BRAID GRD** | `.guarani/orchestration/BRAID_GRD.md` | Multi-agent reasoning | ✅ Active |

### Capabilities Extracted from br-acc

| Capability | Source | Ported To | Status |
|------------|--------|-----------|--------|
| Provenance hashing | `br-acc/etl/src/bracc_etl/guard.py` | `packages/guard-brasil/src/lib/provenance.ts` | ✅ EGOS-130 |
| Evidence chain | `br-acc/api/src/bracc/routers/chat.py` | `packages/shared/src/evidence-chain.ts` | ✅ Active |
| Public Guard Python | `br-acc/api/src/bracc/services/public_guard.py` | `packages/shared/src/public-guard.ts` | ✅ Active |

### Innovation Patterns

| Pattern | Location | Status |
|---------|----------|--------|
| **Dream Cycle** | `docs/strategy/DREAM_CYCLE_SSOT.md` | Phase 1 complete, Phase 2 pending |
| **Gem Hunter** | `agents/agents/gem-hunter.ts` | v6.0, dashboard live |
| **Stitch-First UI** | `.windsurf/workflows/stitch.md` | Active |
| **Auto-Commit ATRiAN** | `scripts/smart-commit.ts` | Disseminated to 6 repos |
| **X-Reply Bot** | `scripts/x-reply-bot.ts` | VPS cron hourly |
| **Rebrowser Playwright** | `smartbuscas/` | Cloudflare bypass migration |
| **Context Persistence** | `scripts/context-manager.ts` | Fibonacci backup pattern |

---

## 📈 Commit Pattern Analysis (Last 50 commits per repo)

### egos/ (Kernel)
| Pattern | Count | Purpose |
|---------|-------|---------|
| `Cascade snapshot` | 25 | Auto-backup every minute during sessions |
| `feat(governance)` | 5 | Governance improvements, SSOT updates |
| `docs(handoff)` | 4 | Session documentation |
| `fix(hq)` | 3 | HQ dashboard corrections |
| `chore(tasks)` | 3 | TASKS.md version updates |
| `feat(sandbox)` | 2 | Guard Brasil sandbox feature |
| `docs(openclaw)` | 2 | OpenClaw integration docs |

### egos-lab/ (Lab - Archiving)
| Pattern | Count | Status |
|---------|-------|--------|
| `feat(eagle-eye)` | 8 | Procurement analysis (Wave 2+3) |
| `feat(gem-hunter)` | 3 | Discovery engine upgrades |
| `Cascade snapshot` | 15 | Session backups |
| `docs` | 10 | Documentation updates |

### carteira-livre/ (Production)
| Pattern | Count | Critical |
|---------|-------|----------|
| `feat(telemetry)` | 5 | SSOT telemetry alignment |
| `feat(observability)` | 3 | Dashboard enhancements |
| `feat(security)` | 2 | Admin page protection (ADMIN-SECURITY-001) |
| `feat(admin)` | 2 | Admin hardening |
| `feat(whatsapp)` | 1 | Evolution API integration |

### forja/ (Candidate)
| Pattern | Count | Status |
|---------|-------|--------|
| `feat(whatsapp)` | 8 | Evolution API deployment |
| `docs` | 6 | Integration documentation |
| `feat(visao)` | 3 | Vision module sprint |
| `feat(claude)` | 2 | Claude Code configuration |

---

## 🖥️ VPS Services Health Matrix (Hetzner 204.168.217.125)

| Service | Port | Status | Last Health Check | Domain |
|---------|------|--------|-------------------|--------|
| **Guard Brasil API** | 3099 | ✅ Healthy | 2026-04-06 | guard.egos.ia.br |
| **Guard Brasil MCP** | 3099 | ✅ Active | 2026-04-06 | guard.egos.ia.br/mcp |
| **Evolution API** | 8080 | ✅ Live | 2026-04-06 | — |
| **EGOS HQ** | 3060 | ✅ Live | 2026-04-06 | hq.egos.ia.br |
| **EGOS Gateway** | 3050 | ✅ Live | 2026-04-06 | — |
| **Gem Hunter Server** | 3095/3097 | ✅ Live | 2026-04-06 | gemhunter.egos.ia.br |
| **forja-notifications** | — | ✅ State: open | 2026-03-30 | WhatsApp instance |
| **OpenClaw Gateway** | 18789 | ✅ UP | 2026-04-06 | localhost (VPS) |
| **OpenClaw Billing Proxy** | 18801 | ✅ Running | 2026-04-06 | subscription=max |

---

## 🔌 MCP Server Installation Log

| # | MCP Server | Status | Install Date | Config Location | Blocker |
|---|------------|--------|--------------|-----------------|---------|
| 1 | filesystem | ✅ Built-in | Native | — | — |
| 2 | memory | ✅ Built-in | Native | — | — |
| 3 | sequential-thinking | ✅ Built-in | Native | — | — |
| 4 | github | ✅ Active | Pre-installed | `~/.claude/settings.json` | — |
| 5 | supabase | ✅ Active | Pre-installed | `~/.claude/settings.json` | — |
| 6 | exa | ✅ Active | Pre-installed | `~/.claude/settings.json` | — |
| 7 | firecrawl | ✅ Installed | 2026-04-06 | Global | — |
| 8 | brave-search | ✅ Installed | 2026-04-06 | Global | — |
| 9 | playwright | ✅ Installed | 2026-04-06 | Global | — |
| 10 | obsidian | ⏳ Pending | — | — | Needs vault path from Enio |
| 11 | stripe | ⏳ Pending | — | — | Needs Stripe secret key (VPS only) |
| 12 | telegram | ⏳ Pending | — | — | Needs bot token |
| 13 | egos-knowledge | ⏳ Move | — | Local → Global | Move to `~/.claude/settings.json` |

---

## 🚨 Critical Tasks Consolidated (All Repos)

### P0 — Critical (This Week)

| Task ID | Repo | Description | Owner | Blocker |
|---------|------|-------------|-------|---------|
| **ADMIN-SECURITY-001** | carteira-livre | 14 admin pages without auth checks | carteira-livre | CRITICAL SECURITY |
| **HQC-003** | egos | Create AGENTS.md + TASKS.md for commons | kernel | Grade D repo |
| **INC-001** | egos | Investigate scheduled agent force-push | kernel | Git safety |
| **EGOS-158** | egos | Publish @egosbr/guard-brasil to npm | kernel | Auth/publish |
| **M-007** | egos | Send 5 outreach emails to DPOs | kernel | GTM blocker |
| **TASK-001** | br-acc | CNPJ ETL Phase 3 (53.6M companies) | br-acc | 77M entities loaded, Phase 4 blocked |
| **CL-WHATSAPP-001..005** | carteira-livre | Migrate WAHA → Evolution API | carteira-livre | SSOT alignment |
| **LAB-ARCHIVE-001..006** | egos-lab | Consolidation to kernel | egos-lab | Archive decision |

### P1 — Important (Next 2 Weeks)

| Task ID | Repo | Description | Dependencies |
|---------|------|-------------|--------------|
| **EGOS-165** | egos | White-label outreach | GTM strategy |
| **EGOS-166** | egos | REST API gateway mode | Architecture |
| **TASK-002** | br-acc | Neo4j memory upgrade + optimization | TASK-001 complete |
| **FORJA-003** | forja | Auth multi-tenant + RLS | Security |
| **LAB-SHARED-001** | egos-lab | Migrate 4 apps to @egos/shared | Deprecation |
| **HQC-008..HQC-012 + HQV2-000..010** | egos | MCP + OpenClaw + Dashboard v2 | Integration |

---

## 🗑️ Archive Decision Matrix

### Confirmed Archive Candidates (11 Repos)

| Repo | Last Commit | Days Stale | Reason | Action |
|------|-------------|------------|--------|--------|
| egos-cortex | 2026-02-16 | 46 | Experimental component | Archive |
| intelink | 2025-12-26 | 128 | Python experiment, dormant | Archive |
| DHPP | Unknown | ? | Unknown state | Verify then archive |
| EGOSv5 | 2026-03-28 | 6 | Superseded by kernel | Archive |
| EGOSv3 | 2026-03-26 | 8 | Old version | Archive |
| EGOSv2 | 2026-03-26 | 8 | Very old | Archive |
| BLUEPRINT-EGOS | 2026-03-30 | 4 | Unfinished | Archive |
| EGOSystem | 2025-07-17 | 260 | Infrastructure, abandoned | Archive |
| Pochete2.0 | 2025-06-15 | 292 | Test/Incomplete | Archive |
| chacreamento | 2025-11-02 | 152 | Test repo | Archive |
| guia-INPI | 2026-01-20 | 72 | Reference only | Archive |

### Migration Required Before Archive

| Source | Destination | Status |
|--------|-------------|--------|
| egos-lab/packages/shared | egos/packages/shared | In progress (LAB-SHARED-001) |
| egos-lab/agents/* | egos/agents/agents | Selective migration |
| egos-lab/apps/eagle-eye | Standalone candidate | Evaluation pending |
| egos-lab/apps/telegram-bot | Standalone candidate | Evaluation pending |

---

## 🔗 Cross-References

### Read Next

- **.guarani/RULES_INDEX.md** — Governance canon
- **AGENTS.md** — Kernel identity and command surface
- **CAPABILITY_REGISTRY.md** — 160 capabilities detailed
- **SSOT_REGISTRY.md** — Ownership and freshness contracts
- **DOCUMENTATION_ARCHITECTURE_MAP.md** — Documentation navigation and permanence
- **SYSTEM_MAP.md** — Activation and topology
- **TASKS.md** — Current execution priorities

### Related Documents

- `docs/ECOSYSTEM_CLASSIFICATION_REGISTRY.md` — Repo taxonomy
- `docs/KERNEL_CONSOLIDATION_PLAN.md` — Migration strategy
- `docs/strategy/PARTNERSHIP_STRATEGY.md` — GTM approach
- `docs/knowledge/HARVEST.md` — Session patterns
- `docs/WORKFLOW_INHERITANCE_REPORT.md` — Workflow lineage

### External References

- Guard Brasil: https://guard.egos.ia.br
- HQ Dashboard: https://hq.egos.ia.br
- Gem Hunter: https://gemhunter.egos.ia.br
- 852 Inteligência: https://852.egos.ia.br

---

## 📝 Update Log

| Date | Version | Changes |
|------|---------|---------|
| 2026-04-06 | 1.0.0 | Initial compilation from all SSOTs, commit history analysis, gap identification |
| 2026-04-06 | 1.1.0 | Added P27 Session handoff: Guard Brasil Sandbox, INC-001 hardening, CCR jobs, GTM status |
| 2026-04-06 | 1.2.0 | Aligned repo map, documentation read order, and kernel-first cross-references |

---

## 📋 P27 Session Handoff (2026-04-06) — Claude Code

### What Was Completed

| Item | Status | Location | Notes |
|------|--------|----------|-------|
| **Guard Brasil Sandbox** | ✅ LIVE | guard.egos.ia.br/sandbox | 4-zone interactive pattern |
| **AUDITABLE_SANDBOX_PATTERN.md** | ✅ SSOT | docs/patterns/ | Reusable pattern |
| **CAPABILITY_REGISTRY update** | ✅ | docs/CAPABILITY_REGISTRY.md §13 | Pattern registered |
| **Brand images** | ✅ | public/hero-shield.png, og-image.png | Playwright generated |
| **Favicons** | ✅ | app/icon.svg | guard + hq domains |
| **/image-prompt skill** | ✅ | ~/.claude/commands/image-prompt.md | — |
| **INC-001 hardening** | ✅ 5 layers | scripts/safe-push.sh, .husky/pre-push, branch protection, push-audit.yml | Force-push prevention |
| **agent-signature.ts** | ✅ | packages/shared/src/agent-signature.ts | Ed25519 + Merkle |
| **GUARD_BRASIL_DEFENSIBILITY.md** | ✅ | docs/strategy/ | — |
| **DISTRIBUTION_PARTNERS_BR.md** | ✅ | docs/strategy/ | — |
| **PART003_LAUNCH_THREAD.md** | ✅ | docs/business/ | Ready to post |
| **CCR Jobs (3)** | ✅ Scheduled | claude.ai/code/scheduled | INC-001 protocol applied |

### Next Solutions by Readiness (GTM Priority)

| Rank | Solution | Status | Missing | Revenue Path |
|------|----------|--------|---------|--------------|
| 🥇 **1. Gem Hunter API** | Dashboard: 288 gems, Telegram /hunt/sector/trending | Sandbox (1 day), pricing page, POST /v1/scan public | R$50/mês (100 scans) → R$350 (1k) → Enterprise |
| 🥈 **2. Eagle Eye** | 84 territórios, 36 oportunidades (R$10.5M), scraper diário | Frontend→backend connection, sandbox, pricing | R$99-499/mês por integrador municipal |
| 🥉 **3. Guard Brasil** | Sandbox live, strategy docs ready | SLA template (DEF-001), audit log dashboard (DEF-003), DPO endorsement (DEF-004) | 5 clientes pagantes em 30 dias |
| 4. **Knowledge Base API** | 50 wiki pages, 3 Supabase tables, wiki-compiler agent | Pricing page, landing, API pública | — |
| 5. **br-acc/BRACC** | 9.1M nodes Neo4j, 77M entidades, ferramentas policiais | Sandbox adaptado (dados sensíveis) | R$5k-50k/contrato |

### Scheduled CCR Jobs Status

| Job | Next Run | Status |
|-----|----------|--------|
| Governance Drift Sentinel | 2026-04-07 00h17 BRT | ✅ INC-001 updated |
| Code Intel + Security | 2026-04-09 01h42 BRT | ✅ INC-001 updated |
| Gem Hunter Adaptive | 2026-04-09 02h37 BRT | ✅ INC-001 updated |

### GTM Action Items (From P27)

1. **Post X.com thread** — PART003_LAUNCH_THREAD.md ready (5 tweets + reply)
2. **Eagle Eye meeting** — This week, demo preparation
3. **Deploy new images** — hero-shield.png, og-image.png to production
4. **Gem Hunter sandbox** — 1 day work with new pattern

---

**Maintained by:** EGOS Kernel  
**Update trigger:** Any structural change to agents, repos, capabilities, or integrations  
**Verification:** Run `bun agent:lint && bun run governance:check`

---

## 🗂️ Hidden Directories & System Folders

### OpenClaw Configuration (/.openclaw/)

| Component | Status | Purpose |
|-----------|--------|---------|
| **openclaw.json** | ✅ Active | v2026.4.5, local mode, Haiku 4.5 default |
| **agents/** | Empty | Sub-agent storage |
| **credentials/** | Empty | OAuth tokens |
| **memory/** | Empty | Conversation persistence |
| **telegram/** | Empty | Telegram channel config |
| **workspace/** | Empty | USER.md profile (Enio) |
| **canvas/** | Empty | Visual outputs |

### EGOS Shared Governance (/.egos/)

| Component | Status | Purpose |
|-----------|--------|---------|
| **sync.sh** | ✅ v2.0 | Governance propagation to 9 repos |
| **hooks/pre-commit** | ✅ Universal | CRCDM + gitleaks secret scan |
| **workflows/** | ✅ 12 files | Slash commands: /start, /end, /mycelium, etc. |
| **skills/** | ✅ 2 dirs | deep-research/, stitch-design/ |
| **guarani/** | ✅ | Shared governance DNA |
| **ssot/** | ✅ | SSOT pointers |
| **REPO_MESH_STATUS.md** | ✅ 2406 bytes | Cross-repo health tracking |
| **manifest.json** | ✅ 2062 bytes | System manifest |

### Registered Repos (in sync.sh)

```bash
REPOS=(
  "$HOME/852"
  "$HOME/egos-lab"
  "$HOME/carteira-livre"
  "$HOME/br-acc"
  "$HOME/forja"
  "$HOME/egos-self"
  "$HOME/smartbuscas"
  "$HOME/santiago"   # EGOS-069: added 2026-03-30
  "$HOME/arch"       # EGOS governance bootstrap 2026-03-30
)
```

### Codex State (/.codex/)

| Component | Status | Purpose |
|-----------|--------|---------|
| **auth.json** | ✅ | Authentication state |
| **models_cache.json** | ✅ 232KB | Model cache |
| **state_5.sqlite** | ✅ 204KB | Session persistence |
| **memories/** | Empty | Long-term memory |
| **skills/** | Empty | Codex skills |

### Other System Directories

| Directory | Status | Purpose |
|-----------|--------|---------|
| **/.agent/** + **/.agents/** | ⚠️ Minimal | compatibility workflow surfaces for older command layouts |
| **/arch/** | ✅ Active | SINAPI integration system (9175 lines TASKS.md) |
| **/egos-self/** | ✅ Active | Kotlin mobile app (1540 lines TASKS.md) |
| **/egos-archive/** | ⚠️ Archive | v2, v3, v4, v5 historical versions |
| **/blueprint-egos/** | ⚠️ Minimal | 553 lines TASKS.md, frozen-zones.md |
| **/INPI/** | ✅ Active | Patent platform, 2266 lines TASKS.md |
| **/policia/** | ✅ Active | DHPP workspace, Python, 2197 lines TASKS.md |
| **/chacreamento/** | 📁 Docs only | 3 PDF/DOCX files (land contracts) |
| **/BrandForge/** | ⚠️ Minimal | 5 files (metaprompts, route.ts) |
| **/video-editor/** | ⚠️ Minimal | 3 files (Python server) |
| **/EGOSv2/** | ❌ Empty | 3 empty folders |
| **/egos-inteligencia/** | ✅ Active | Intelligence hub (7787 lines TASKS.md) |

---

## 🔧 Most Referenced Scripts & Commands (by Importance Weight)

### Critical Infrastructure (Weight: 10/10)

| Script | Location | References | Purpose |
|--------|----------|------------|---------|
| **sync.sh** | `~/.egos/sync.sh` | 7+ repos | Governance propagation v2.0 |
| **pre-commit** | `~/.egos/hooks/pre-commit` | Universal | CRCDM + gitleaks security |
| **governance-sync.sh** | `scripts/governance-sync.sh` | package.json x3 | SSOT propagation |
| **start-v6.ts** | `scripts/start-v6.ts` | `bun start` | Session initialization |

### High Impact (Weight: 8/10)

| Script | Location | References | Purpose |
|--------|----------|------------|---------|
| **doctor.ts** | `scripts/doctor.ts` | `bun doctor` | System diagnostics |
| **pr-pack.ts** | `scripts/pr-pack.ts` | `bun pr:pack` | PR preparation |
| **pr-gate.ts** | `scripts/pr-gate.ts` | `bun pr:gate` | Quality gates |
| **activation-check.ts** | `scripts/activation-check.ts` | `bun activation:check` | /start Phase 0 |
| **wiki-compiler.ts** | `agents/agents/wiki-compiler.ts` | `bun wiki:*` | Knowledge system |
| **gem-hunter.ts** | `agents/agents/gem-hunter.ts` | GH-001..071 | Discovery engine |

### Medium Impact (Weight: 6/10)

| Script | Location | References | Purpose |
|--------|----------|------------|---------|
| **safe-push.sh** | `scripts/safe-push.sh` | INC-001 | Force-push prevention |
| **context-manager.ts** | `scripts/context-manager.ts` | Context persistence | Fibonacci backup |
| **rapid-response.ts** | `scripts/rapid-response.ts` | X.com | Emergency response |
| **x-reply-bot.ts** | `scripts/x-reply-bot.ts` | VPS cron | X automation |
| **smart-commit.ts** | `scripts/smart-commit.ts` | 6 repos | ATRiAN auto-commit |
| **validate-ssot.ts** | `scripts/validate-ssot.ts` | `bun ssot:check` | SSOT validation |
| **integration-release-check.ts** | `scripts/integration-release-check.ts` | `bun integration:check` | Release gates |

---

## 📊 Investigation Coverage Report

### Repositories Analyzed (6 main + 11 additional)

| Repo | Commits | Status | Coverage |
|------|---------|--------|----------|
| egos | 50 | ✅ Complete | 100% |
| egos-lab | 50 | ✅ Complete | 100% |
| 852 | 50 | ✅ Complete | 100% |
| br-acc | 50 | ✅ Complete | 100% |
| carteira-livre | 50 | ✅ Complete | 100% |
| forja | 50 | ✅ Complete | 100% |
| **Subtotal Main** | **300** | **✅** | **100%** |
| santiago | 30 | ✅ Complete | 100% |
| smartbuscas | 30 | ✅ Complete | 100% |
| intelink | 0 | ❌ Empty | N/A |
| commons | 0 | ❌ Empty | N/A |
| INPI | 0 | ⚠️ List only | 20% |
| policia | 0 | ⚠️ List only | 20% |
| egos-self | 0 | ⚠️ List only | 20% |
| arch | 0 | ⚠️ List only | 20% |
| egos-inteligencia | 0 | ⚠️ List only | 20% |
| **Subtotal Additional** | **60** | **⚠️** | **40%** |

### Hidden Directories Investigated

| Directory | Status | Files Found |
|-----------|--------|-------------|
| .openclaw/ | ✅ Complete | 12 items |
| .egos/ | ✅ Complete | 15 items |
| .codex/ | ✅ Complete | 10 items |
| .agent/ | ✅ Complete | 1 item |
| egos-archive/ | ✅ Complete | 10 items |
| blueprint-egos/ | ✅ Complete | 15 items |
| chacreamento/ | ✅ Complete | 3 items |
| BrandForge/ | ✅ Complete | 5 items |
| video-editor/ | ✅ Complete | 3 items |
| EGOSv2/ | ✅ Complete | 3 items |
| INPI/ | ✅ Complete | 20 items |
| policia/ | ✅ Complete | 15 items |
| egos-self/ | ✅ Complete | 12 items |
| arch/ | ✅ Complete | 20 items |
| egos-inteligencia/ | ✅ Complete | 10 items |
| commons/ | ✅ Complete | 1 item |
| intelink/ | ✅ Complete | 7 items |
| **Total Hidden/System** | **✅ 17 dirs** | **~160 items** |

### Scripts Cataloged

| Category | Count | Status |
|----------|-------|--------|
| Core scripts (egos/scripts/) | 24 | ✅ Cataloged |
| Agent files (agents/agents/) | 16 | ✅ Cataloged |
| API servers (agents/api/) | 1 | ✅ Cataloged |
| Package.json commands | 27 | ✅ Cataloged |
| Hidden dir scripts | 5 | ✅ Cataloged |
| **Total Scripts** | **73** | **✅** |

### Overall Coverage

| Metric | Count | Target | Percentage |
|--------|-------|--------|------------|
| Repos analyzed | 17 | 20 | **85%** |
| Commits read | 360+ | 400 | **90%** |
| Hidden dirs mapped | 17 | 17 | **100%** |
| Scripts cataloged | 73 | 80 | **91%** |
| Tasks consolidated | 13 repos | 15 | **87%** |
| **TOTAL COVERAGE** | — | — | **90.6%** |

---

**Maintained by:** EGOS Kernel  
**Update trigger:** Any structural change to agents, repos, capabilities, or integrations  
**Verification:** Run `bun agent:lint && bun run governance:check`

---

## 📱 Complete Apps Catalog (All Repositories)

### Production Apps (Live)

| App | Repo | Path | Domain | Status | Revenue |
|-----|------|------|--------|--------|---------|
| **Guard Brasil API** | egos | `apps/api/` | guard.egos.ia.br | ✅ LIVE | MRR ativo |
| **Guard Brasil Web** | egos | `apps/guard-brasil-web/` | — | ✅ Active | — |
| **EGOS HQ** | egos | `apps/egos-hq/` | hq.egos.ia.br | ✅ LIVE | — |
| **EGOS Gateway** | egos | `apps/egos-gateway/` | — | ✅ LIVE | — |
| **852 Inteligência** | 852 | `src/app/` | 852.egos.ia.br | ✅ LIVE | — |
| **Carteira Livre** | carteira-livre | `src/` | Vercel | ✅ LIVE | Marketplace |
| **Forja** | forja | `src/` | forja-orpin.vercel.app | ✅ LIVE | SaaS CRM |
| **BR-ACC** | br-acc | `api/` | — | ✅ LIVE | OSINT |

### Lab/Development Apps

| App | Repo | Path | Status | Notes |
|-----|------|------|--------|-------|
| **Eagle Eye** | egos-lab | `apps/eagle-eye/` | ✅ Active | 84 territórios, R$10.5M |
| **Gem Hunter API** | egos | `agents/api/` | ✅ Active | 288 gems, Telegram bot |
| **Inteligência egos** | egos-inteligencia | `frontend/` | ✅ Active | 7,787 lines TASKS.md |
| **Telegram Bot** | egos-lab | `apps/telegram-bot/` | ⚠️ In Progress | — |
| **EGOS Commons** | egos | `apps/commons/` | ⚠️ In Progress | — |
| **Agent-028 Template** | egos | `apps/agent-028-template/` | 📋 Planned | — |
| **Intelink** | INTELINK | `frontend/` | ❌ Dormant | Archive candidate |

---

## 📦 Packages Cross-Reference Matrix

### Kernel Packages → Apps

| Package | Used By | Purpose |
|---------|---------|---------|
| `@egos/shared` | All apps | LLM provider, PII scanner, rate limiter |
| `@egos/guard-brasil` | Guard Brasil, 852, carteira-livre, forja | LGPD PII detection |
| `@egos/search-engine` | Gem Hunter, wiki-compiler | AAR in-memory search |
| `@egos/atomizer` | wiki-compiler, gem-hunter | Semantic atomization |
| `@egos/core` | All apps | Contracts, PRI safety gate |
| `@egos/audit` | Guard Brasil | Versioned record tracking |
| `@egos/registry` | All apps | Module lookup |
| `@egos/types` | All apps | Shared types |
| `@egos/mcp-governance` | MCP servers | MCP tooling |

---

## 🔬 Verified Evidence (P33 Diagnostic — 2026-04-07)

> All claims below were verified via command execution on the live system on 2026-04-07.
> Commands are reproducible. See `.egos-manifest.yaml` in each repo for the full manifest.

### Neo4j Graph (br-acc / EGOS-Inteligencia)

```bash
# Verify node count (requires VPS SSH + Neo4j access)
ssh -i ~/.ssh/hetzner_ed25519 root@204.168.217.125 \
  'curl -s -u neo4j:BrAcc2026EgosNeo4j! \
  http://localhost:7474/db/neo4j/query/v2 \
  -H "Content-Type: application/json" \
  -d "{\"statement\":\"MATCH (n) RETURN count(n) as nodes\"}"' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['values'][0][0])"
# Result: 83773683

# Verify relationship count
# -d '{"statement":"MATCH ()-[r]->() RETURN count(r) as rels"}'
# Result: 26808540

# Verify label count
# -d '{"statement":"CALL db.labels() YIELD label RETURN count(label) as n"}'
# Result: 32
```

| Metric | Verified Value | Verified At |
|--------|---------------|-------------|
| Nodes | 83,773,683 | 2026-04-07 |
| Relationships | 26,808,540 | 2026-04-07 |
| Labels | 32 | 2026-04-07 |
| Container | bracc-neo4j | 2026-04-07 |

### 8/8 Public Domains (2026-04-07)

```bash
# Verify all domains at once
for url in \
  "https://guard.egos.ia.br/health" \
  "https://852.egos.ia.br/" \
  "https://eagleeye.egos.ia.br/" \
  "https://gemhunter.egos.ia.br/gem-hunter/topics" \
  "https://hq.egos.ia.br/" \
  "https://openclaw.egos.ia.br/" \
  "https://carteiralivre.com/" \
  "https://inteligencia.egos.ia.br/"; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url")
  echo "$STATUS $url"
done
```

| Domain | Status | Notes |
|--------|--------|-------|
| guard.egos.ia.br | 200 ✅ | Guard Brasil API |
| 852.egos.ia.br | 200 ✅ | Restored 2026-04-07 (was missing from Caddyfile) |
| eagleeye.egos.ia.br | 200 ✅ | Fixed 2026-04-07 (was :3090 → eagle-eye:3001) |
| gemhunter.egos.ia.br | 200 ✅ | Fixed 2026-04-07 (was :3095 → egos-gateway:3050) |
| hq.egos.ia.br | 307 ✅ | Redirect to /login (normal) |
| openclaw.egos.ia.br | 200 ✅ | |
| carteiralivre.com | 308→200 ✅ | Redirect from .com.br |
| inteligencia.egos.ia.br | 200 ✅ | Newly discovered (not in prev. MASTER_INDEX) |

### Carteira Livre Deep Metrics (2026-04-07)

```bash
# Run from /home/enio/carteira-livre:
bun /home/enio/egos/agents/agents/doc-drift-verifier.ts --repo /home/enio/carteira-livre --json
```

| Metric | Value | Reproduction Command |
|--------|-------|---------------------|
| Total commits | 1,690 | `git log --pretty=format:'%h' \| wc -l` |
| Next.js pages | 134 | `find app/ -name 'page.tsx' \| wc -l` |
| API routes | 254 | `find app/api/ -name 'route.ts' \| wc -l` |
| TypeScript LOC | 182,589 | `find . -name '*.ts' -o -name '*.tsx' \| ... \| wc -l` |
| Test files | 37 | `find . -name '*.test.ts' -o ... \| wc -l` |
| Test assertions | 2,847 | `grep -rhE 'it\(\|test\(\|describe\(' --include='*.test.*' .` |

### Doc-Drift Shield Status (2026-04-07)

| Layer | Component | Status |
|-------|-----------|--------|
| L1 — Contract Manifests | `.egos-manifest.yaml` in egos, br-acc, carteira-livre | ✅ Deployed |
| L2 — Pre-commit Hook | `doc-drift-verifier.ts` + `.husky/doc-drift-check.sh` | ✅ Deployed |
| L3 — Autonomous Sentinel | `doc-drift-sentinel.ts` (registered as agent #19) | ✅ Code ready |
| L4 — CLAUDE.md Rules | §27 in `~/.claude/CLAUDE.md` (v2.8.0) | ✅ Active |

```bash
# Verify all 3 repos clean (run from /home/enio/egos):
bun agents/agents/doc-drift-sentinel.ts --dry
```

---

> *"One document to find them, one document to bind them, one document to bring them all and in the light entwine them."* — EGOS SSOT Discipline
