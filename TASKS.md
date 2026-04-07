# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.48.0 | **Updated:** 2026-04-07 | **LAST SESSION:** P35+CAREER — SSOT gate 26 domains, career-ops setup (CAREER-001..004 done), profile fixes

---

### Doc-Drift Shield Implementation (2026-04-07)
**SSOT:** `docs/DOC_DRIFT_SHIELD.md` | **Handoff:** `docs/_current_handoffs/handoff_2026-04-07_doc-drift-shield-plan.md`
**Context:** P33 discovered severe drift across READMEs (Carteira Livre: 54 pages → real 134 / +148%; 68 APIs → real 254 / +273%; BR-ACC 77M → real 83,773,683 Neo4j nodes). Solution: 4-layer structural shield. L1 (contract manifest) + L4 part B (CLAUDE.md §27 rules) DONE. L2 (pre-commit) + L3 (VPS sentinel) + L4 part A (CCR module) pending.

**Done P33 (2026-04-07):**

**Done P34 (2026-04-07):** doc-drift-verifier.ts, doc-drift-sentinel.ts, readme-syncer.ts, doc-drift-check.sh hook, agents.json registered (19 agents), br-acc/carteira-livre manifests + annotations, MASTER_INDEX v1.3.0

**Done P35 (2026-04-07):** DRIFT-008 (decision: local cron primary, CCR secondary), DRIFT-009 (governance-drift.yml CCR workflow), DRIFT-010 (manifests: 852/forja/egos-lab/egos-inteligencia), DRIFT-011 (manifest-generator.ts LLM extraction), SSOT gate (.ssot-map.yaml 21 domains + ssot-router.ts pre-commit step 5.7), X_POSTS_SSOT.md (5 files → 1), doc-drift-analyzer.ts (Layer 3.5), developer timeline, EN native thread

**P1 — Pending:**
- [ ] **DRIFT-012**: Drift dashboard in hq.egos.ia.br showing status across all repos
- [ ] **DRIFT-013**: Integrate with Gem Hunter for third-party claim verification
- [ ] **SSOT-MCP**: Create `docs/MCP_SSOT.md` — consolidate 7 MCP_*.md files (MCP_DEPLOYMENT_CHECKLIST, MCP_ENV_VARS_REFERENCE, MCP_INTEGRATION_GUIDE, MCP_INTEGRATION_MAP, MCP_ORCHESTRATION_STRATEGY, MCP_SCOPE_POLICY, MCP_IMPLEMENTATION_SUMMARY)
- [ ] **SSOT-OUTREACH**: Migrate docs/outreach/ (8 files) → GTM_SSOT.md §partnerships
- [ ] **ARR-001**: Wire AAR (`@egos/search-engine`) into Gem Hunter content indexing (first activation use case)
- [ ] **ARR-002**: Wire AAR into KB wiki search (replaces raw grep in wiki-compiler)
- [ ] **ARR-003**: Hybrid retrieval pattern — AAR (precision/exact) + pg_trgm FTS (recall) for Guard Brasil + EGOS Inteligência. Validated by 2025 research (Meilisearch/Redis/Glean): full-text superior to vectors for identifier-heavy domains (CPF/CNPJ/PEPs/contracts). NOT a vector DB replacement.

### HQ Integration Masterplan (2026-04-07)
**Goal:** HQ shows live data for ALL 19 VPS containers — no service invisible, no number hardcoded.
**Diagnostic:** 2026-04-07 — hq.egos.ia.br covers 5/19 services. 14 containers invisible. Placeholder cards shipped (page.tsx + health/route.ts extended). Integration in 4 phases.
**SSOT:** `apps/egos-hq/app/page.tsx` + `apps/egos-hq/app/api/hq/health/route.ts`

**Phase 1 — Wiring internal services (health/route.ts already extended):**
- [ ] **HQI-001**: Eagle Eye → add counts from Supabase (territories, opportunities) via `/api/hq/eagle-eye` route
- [ ] **HQI-002**: 852 Police Bot → expose messages_today from 852-app internal API (find correct health endpoint)
- [ ] **HQI-003**: SINAPI → verify internal Docker URL + expose entry_count from DB
- [ ] **HQI-004**: br-acc/Neo4j → live node count via bolt (find creds in VPS docker-compose)
- [ ] **HQI-005**: Gateway channels ✅ wired → verify WA/TG cards show real data in HQ
- [ ] **HQI-006**: Guard Brasil pattern_count ✅ from /v1/meta → verify card shows 15 patterns
- [ ] **HQI-007**: Billing proxy enriched ✅ (subscription_type, uptime, patterns) → verify card
- [ ] **HQI-008**: OpenClaw real config → read actual fallback_chain from openclaw-sandbox (not hardcoded)

**Phase 2 — Volume mounts + data routes:**
- [ ] **HQV2-000**: VPS docker-compose: volume mounts → TASKS.md, agents.json, CAPABILITY_REGISTRY.md, docs/jobs/ → /data/*
- [ ] **HQV2-001**: `/api/hq/tasks` — parse /data/TASKS.md → `{total, pending, p0, p1, stale_p0}`
- [ ] **HQV2-002**: `/api/hq/world-model` — read /data/world-model/current.json → health%, blockers
- [ ] **HQV2-003**: `/api/hq/gems` — gem-hunter API → top gems, last run, sector breakdown
- [ ] **HQV2-004**: `/api/hq/drift` — read /data/jobs/doc-drift-sentinel.md → structured drift per repo (DRIFT-012)

**Phase 3 — New dashboard pages:**
- [ ] **HQV2-006**: `/tasks` page — Kanban P0/P1/P2, done/pending counts (dep: HQV2-001)
- [ ] **HQV2-007**: `/world-model` page — health% gauge, P0 blockers, agent inventory
- [ ] **HQV2-008**: `/gems` page — filterable cards (score, source, category)
- [ ] **HQV2-009**: `/system-map` page — D3 graph from agents.json + CAPABILITY_REGISTRY
- [ ] **HQV2-010**: Nav update — add tasks, world-model, gems, system-map, drift links

**Phase 4 — Intelligence + Dream Cycle:**
- [ ] **DC-007**: HQ "Last Night" card — Dream Cycle results from egos_nightly_logs
- [ ] **HQC-012**: Intelligence engine — `intelligence-engine.ts` + Gemma 4 31B free → auto-task creation
- [ ] **GRF-002**: Knowledge Graph panel — vis.js embed from codebase-memory-mcp
- [ ] **ORB-004**: Orchestration Status widget — MCP server health (brave, github, filesystem, etc.)
- [ ] **HQC-011**: Remove all remaining hardcoded data — drive from canonical registries

---

### P2 — SSOT Limpeza (Content em lugares errados)
**Context:** Descoberto em P35. Arquivos dispersos que devem ser movidos para SSOTs existentes.

| Arquivo | Conteúdo | Ação |
|---------|----------|------|
| `docs/strategy/XCOM_SOCIAL_AUTOMATION_PLAN.md` | Estratégia automação X.com | Mover → GTM_SSOT.md §automação |
| `docs/social/X_POST_PROFILE_PARTNERSHIP.md` | Post já consolidado em X_POSTS_SSOT.md | Deletar (migrado P35) |
| `docs/outreach/*.md` (8 arquivos) | Partner briefs, prospects, kit | Mover → GTM_SSOT.md §partnerships |
| `docs/MCP_*.md` (7 arquivos) | Config MCP dispersa | → **SSOT-MCP** (task separada abaixo) |
| `docs/sales/*.md` | Vendas/pricing content | Mover → MONETIZATION_SSOT.md |

- [ ] **CLEAN-001 [P2]**: Mover XCOM_SOCIAL_AUTOMATION_PLAN.md → GTM_SSOT.md §X.com automation e deletar original
- [ ] **CLEAN-002 [P2]**: Deletar `docs/social/X_POST_PROFILE_PARTNERSHIP.md` (conteúdo já em X_POSTS_SSOT.md)
- [ ] **CLEAN-003 [P2]**: Migrar `docs/outreach/` (8 arquivos) → GTM_SSOT.md §partnerships (= SSOT-OUTREACH)
- [ ] **CLEAN-004 [P2]**: Migrar `docs/sales/*.md` → MONETIZATION_SSOT.md
- [ ] **EGOS-132 [P2]**: Resolver conflito brand: `docs/BRAND_CANONICAL.md` (kernel) vs `egos-lab/branding/BRAND_GUIDE.md` (lab). Decisão: usar egos-lab até resolução (conforme .ssot-map.yaml nota)

---

---

### Documentation — Misc Pending
- [ ] DOC-005: Terminology sanitization — remove `Sacred Code` / `Frozen Zones` from legacy governance docs

---

### Completed Archive (compressed — see git log for details)
**P1-P26 (2026-03-27..2026-04-06):** EGOS-151..176, MONETIZE-001..015, START-001..009, KB-001..018, GH-001..071, X-001..008, INTEL-005, THEATER-001, WA-001..003, EAGLE-*, GOV-*, BRACC-*, PART-001..015 — all DONE ✅. Products live: Guard Brasil v0.2.2 API+web+npm, EGOS Gateway v0.3.0 (port 3050), Gem Hunter dashboard (port 3095), HQ (hq.egos.ia.br), Eagle Eye, KB (52 wiki pages). OpenClaw billing proxy integrated (subscription:max).

---

### Guard Brasil Monetization Roadmap

**Completed:** EGOS-151..161, MONETIZE-001..015, EGOS-162/164 — all DONE ✅ (see archive)

**P1 — Remaining:**
- [ ] EGOS-163: Pix billing integration

**P2 — Growth:**
- [ ] EGOS-165: White-label outreach
- [ ] EGOS-166: REST API gateway mode

---

### HQ Completion Program (2026-04-06)
**SSOT:** `docs/MASTER_INDEX.md` + `docs/SSOT_REGISTRY.md` + `docs/SYSTEM_MAP.md`
**Goal:** HQ becomes the non-hardcoded control plane for verified ecosystem reality.

**P0 — Truth normalization + /start evidence:**
- [ ] **HQC-004**: Add kernel SSOT pointers to `852`, `br-acc`, `carteira-livre`, `forja`, `egos-lab`; audit `policia`, `INPI`, `commons`

**P1 — Wiring + contracts:**
- [ ] **HQC-008**: Complete MCP setup gaps (obsidian, stripe, telegram) and make HQ consume installation truth
- [ ] **HQC-009**: Build `@egosbr/guard-brasil-mcp` and register OpenClaw/ClawHub path
- [ ] **HQC-010**: Configure OpenClaw Gateway / WhatsApp / Telegram path without duplicated orchestration
- [ ] **HQC-011**: Remove hardcoded HQ data dependencies and drive HQ from canonical registries (`TASKS.md`, `agents.json`, `validation.json`, `CAPABILITY_REGISTRY.md`, `MASTER_INDEX.md`)
- [ ] **HQC-012**: Build `intelligence-engine.ts` and connect Dream Cycle outputs to HQ

**P2 — Ecosystem consolidation:**
- [ ] **HQC-013**: Fix HARVEST/KB dedup and freshness so HQ can trust knowledge surfaces
- [ ] **HQC-014**: Archive 11 dormant repos and close Santiago fix-or-kill
- [ ] **HQC-015**: Execute egos-lab kernel consolidation wave (`LAB-ARCHIVE-001..006`)

---

### Neural Mesh + Telemetry — DONE (2026-04-01)
EGOS-167/168/175, GH-040..042, EGOS-TELEM-001..005 — all DONE . codebase-memory-mcp (51K nodes), llmrefs (15 docs), SSOT gate, smoke tests, version lock, full telemetry (5 layers). See git log.

---

### EGOS Knowledge System — Karpathy LLM Wiki (2026-04-05)

**Pattern:** 3-layer (raw sources compiled wiki schema). Supabase-backed, API-served, agent-compiled.
**Agent:** `agents/agents/wiki-compiler.ts` | **API:** `apps/egos-gateway/src/channels/knowledge.ts`
**Supabase tables:** `egos_wiki_pages` (50 pages), `egos_learnings`, `egos_wiki_changelog`

**Done:**

**P1 — Integration:**

**P1 — Quality:**

**P2 — Advanced:**
- [ ] KB-017: Auto-learning from git commits (extract patterns from commit messages + diffs)

---

- [ ] EGOS-169: @aiready/pattern-detect pre-commit (duplicate detection)
- [ ] EGOS-173: CRCDM hooks: llmrefs staleness + auto-heal rename

---

### Session Initialization v6.0 LIVE (2026-04-02)
START-001..005 DONE (parallel diagnostics 22s, CI, pre-commit). Design: `docs/SESSION_INITIALIZATION_v6.md`

**Pending (P1):**
- [ ] START-006: Monitor performance 1 week (due 2026-04-09)
- [ ] START-007: v6.1 distributed agent health (SSH parallel)
- [ ] START-008: Dashboard integration (Grafana/Claude Code UI)

---

### Scheduled Jobs — 3 CCR slots (2026-04-01)

All Haiku, 00-06h BRT, reports in `docs/jobs/` + `docs/gem-hunter/`

---

### Eagle Eye — OSINT Licitações LIVE
**eagleeye.egos.ia.br** | 84 territories | 121 opportunities | daily cron 9am BRT
**Done (EAGLE-000..023):** standalone Docker, Supabase 6 tables, 26 detection patterns, Telegram alerts, PNCP enrichment, 80 territories seeded, integrador 70/30 channel doc, daily cron, real pipeline (36 opps R$10.5M).
- [ ] EAGLE-009: Stripe/Pix for Pro tier (R$497/mo)
- [ ] EAGLE-019: Integrador partnership outreach
- [ ] EAGLE-020: R$250k proposal — deadline 2026-04-29
- [ ] EAGLE-GH-003..010: Classification + extraction + profile + API v2 + MCP + Pix
- [ ] SANT-001: Santiago partner onboarding (MVP ready, waiting partner)

---

### Gem Hunter v6 — Research Discovery Engine LIVE
**CCR:** seg+qui 2h37 BRT | **Standalone API:** port 3097 | **npm:** @egosbr/gem-hunter v6.0.0
**Done (GH-001..066):** /study+/study-end skills, pair studies (Continue 71/100, Aider 74/100, Cline 72.8/100), PWC pipeline, Papers Without Code, KOL discovery, Telegram+Discord alerts, BRAID GRD, X-reply-bot (VPS hourly cron), ArchitectureSelector, cost-tracker, world-model signals, gem-hunter-server API, pricing.ts, Gateway /gem-hunter channel.

**Active — Pair Studies Queue:**
- [ ] GH-013: EGOS OpenHands | GH-014: EGOS LangGraph | GH-015: EGOS OpenAI Agents SDK | GH-016: EGOS LiteLLM | GH-017: EGOS Langfuse
- [ ] GH-020: EGOS Mem0 | GH-021: EGOS Temporal | GH-022: EGOS Haystack | GH-023: EGOS DSPy | GH-036: OpenHarness adapter

**Active — Product:**
- [ ] GH-025: `/pr` workflow + GitHub App (pre-merge gate)
- [ ] GH-026: Upgrade codebase-memory-mcp to HTTP/SSE transport
- [ ] GH-027: `.guarani/checks/` layer
**Gem Hunter product (revenue):**
- [ ] GH-073: Weekly email digest

**Gem Hunter CCR:**

**P1 — Reference Repo Study Queue (priority order):**
- [ ] GH-013: EGOS OpenHands (`OpenHands/OpenHands`) — full software agent SDK/CLI/GUI
- [ ] GH-014: EGOS LangGraph (`langchain-ai/langgraph`) — stateful long-running agents, durable execution
- [ ] GH-015: EGOS OpenAI Agents SDK (`openai/openai-agents-python`) — handoffs, guardrails, tracing
- [ ] GH-016: EGOS LiteLLM (`BerriAI/litellm`) — multi-model proxy, cost tracking, routing
- [ ] GH-017: EGOS Langfuse (`langfuse/langfuse`) — observability, prompt versioning, evals

**Aider study done (GH-031..039):** pre-edit-safety hook, CLAUDE.md §13 model guide, OpenHarness early-warning, Telegram gem alerts, BRAID Mode GRD, x-reply-bot VPS cron. Details: git log.
- [ ] GH-032: EGOS edit benchmark (SWE-Bench inspired, 20 tasks)
- [ ] GH-036: OpenHarness adapter in packages/shared/harness/

**Gem Hunter v5.1+v6.0 DONE (GH-043..065):** PWC pipeline, low-star scoring, ArchitectureSelector adapter, structural validation, auto-queue, signals ingestion, Papers Without Code, KOL discovery, evolution engine, multi-LLM fallback, Telegram alerts, multi-stage paper pipeline, cost budgeting, standalone API, MONETIZATION_SSOT, pricing.ts, gem-hunter npm v6.0.0. Details: git log.

*Month 2-3 — Product Scale:*
- [ ] GH-063: x402 pay-per-call — M2M agent payments via x402 protocol
- [ ] GH-067: Deploy gem-hunter-server to VPS (gemhunter.egos.ia.br) + Caddy routing → P0 revenue
- [ ] GH-070: Chatbot orchestrator — WhatsApp channel NLP intent → tool calls → gem-hunter → curated reply
- [ ] GH-072: Chatbot tier enforcement (200 queries/mo for R$149/mo chatbot plan)
- [ ] GH-073: Email digest — weekly top 10 gems to subscribers
- SSOT: docs/gem-hunter/GEM_HUNTER_PRODUCT.md

**P2:** GH-020..024 (Mem0, Temporal, Haystack, DSPy, Lego Assembler) — post PMF.

---

### Claude Code Hardening + Observability (archived)
LEAK/AI/OBS 001..013 done. Pending: LEAK-010..012 (monitor repos), AI-008..010 (OTel wiring), OBS-010..013 (privacy logs) — P2.
**Ref repos done:** Continue 71/100, Aider 74/100, Cline 72.8/100, agent-scaling-laws 87% ArchSelector.
**P1 queue:** OpenHands, LangGraph, OpenAI Agents SDK, LiteLLM, Langfuse, Mem0, Temporal TS.

---

### X.com Presence (2026-04-01)
**BLOCKER:** XMCP-001 (X credentials 401 — regenerate at developer.twitter.com first)
- [ ] X-009: Trending topic scanner (hourly, keywords vs capabilities)
- [ ] X-012: Thread scheduler (multi-tweet, 2-min gaps) — dep XMCP-001
- [ ] GTM-002-unblock: Post Guard Brasil thread after XMCP-001

---

### Block Intelligence + Eagle Eye (compressed)
**WM-001..008:** Local LLM + world model (P2, post-PMF). **INTEL-006..010:** Proactive detection, mermaid, DRI auto-assign (P1-P2). SSOT: `docs/strategy/WORLD_MODEL_SSOT.md`
**Eagle Eye v2:** EAGLE-GH-001..005 done. P0: GH-003/004 (classification/extraction). Deadline: EAGLE-023 R$250k proposal 2026-04-29.
- [ ] MONETIZE-011: Deploy v0.2.3 to VPS with STRIPE_METER_ID env var
- [ ] MONETIZE-012: NOWPayments webhook URL config — ENIO action required

### Partnership & Distribution Strategy (2026-04-05)
**Compressed:** See `docs/GTM_SSOT.md` + `docs/MONETIZATION_SSOT.md` for full roadmap.
- [ ] **PART-001**: Publish npm + ProductHunt (M-007 emails first)
- [ ] **M-007**: Send 5 outreach emails to DPOs (templates in GTM_SSOT §5) — **STALE 7+ days**
- [ ] **PART-016**: Decide PARTNER-D1 co-founder model

---

### Evaluated & Deferred (2026-04-05)

**HiClaw (agentscope-ai/HiClaw):** Analyzed. Matrix rooms + MinIO + Higress = overhead for zero users. Already have WhatsApp gateway + Caddy + Supabase. **SKIP.**
**PAL (agno-agi/pal):** Analyzed. Compiler + Linter pattern adopted via wiki-compiler agent. Syncer not needed (Supabase > Git sync). **ADOPTED partially.**
**Karpathy LLM Wiki gist:** Adopted. 3-layer pattern (raw → wiki → schema) is now KB-001..007. **ADOPTED fully.**
**Fine-tuning próprio (Gemma 2B/Qwen 7B):** VPS has 540MB free RAM, 0 GPU. Fine-tune on Colab is possible but not 90-day focus. WM-001..004 covers dataset prep. **DEFERRED to P2.**

### GTM & Incidents (P25-P35)

**SSOT:** `docs/GTM_SSOT.md` | **ICP:** CTOs/backend devs at fintechs+healthtechs (confirmed).  
**INC-001 (2026-04-06):** Force-push incident — recovered. Mitigations: `.husky/pre-push` blocks, GitHub branch protection enabled, CLAUDE.md §25 added.

**P0 — Social & Outreach (stale, see GTM_SSOT.md for details):**
- [ ] **M-007**: Send 5 outreach emails to DPOs (STALE 7+ days)
- [ ] **GTM-002**: X.com thread demo (4 tweets, drafts ready)
- [ ] **GTM-001**: x-reply-bot search tuning (lgpd/anpd/dpo keywords)

**P1 — Content & Integrations:** GTM-006..013 (docs playground, ProductHunt, dev.to, partnerships) — see git log for status.

---

### HQ Dashboard v2 (2026-04-06)
**Goal:** Mission Control shows full system state (tasks, gems, world model, GTM metrics, system map)
**Prerequisite:** Volume mounts on VPS (data bound to /data/ inside container)

**P0 — Volume mounts (needed for all v2 routes):**
- [ ] HQV2-000: Add Docker volume mounts to VPS docker-compose.yml: TASKS.md, world-model/, gem-hunter/latest-run.json, agents.json, CAPABILITY_REGISTRY.md → /data/*

**P1 — API Routes (apps/egos-hq/app/api/hq/):**
- [ ] HQV2-001: `tasks/route.ts` — parse /data/TASKS.md → `{categories, priorities, total, done, pending, p0_stale}`
- [ ] HQV2-002: `world-model/route.ts` — read /data/world-model/current.json → full snapshot (health%, blockers, agents, signals)
- [ ] HQV2-003: `gems/route.ts` — read /data/gem-hunter/latest-run.json → top gems + filters (score, source, category)
- [ ] HQV2-004: `system-map/route.ts` — read /data/agents.json + CAPABILITY_REGISTRY.md → `{nodes, edges}` for D3
- [ ] HQV2-005: `gtm/route.ts` — aggregate: MRR from Supabase, M-007 status, outreach count, pending demos

**P2 — Dashboard Pages:**
- [ ] HQV2-006: `/tasks` page — Kanban by priority (P0 red, P1 yellow, P2 blue), done/pending counts
- [ ] HQV2-007: `/world-model` page — health% gauge, P0 blocker cards, agent inventory, signal feed
- [ ] HQV2-008: `/gems` page — filterable card grid (score badge, source icon, category color, search)
- [ ] HQV2-009: `/system-map` page — interactive D3 graph (capability domains as nodes, agent edges)
- [ ] HQV2-010: Update nav in hq-layout.tsx with new links (tasks, world-model, gems, system-map, gtm)

---

### P26 — MCPs + Focus v2.0 (2026-04-06)

**Completed:**

**Pending:**
- [ ] MCP-005: Obsidian MCP — needs vault path from Enio (`setup-obsidian-mcp.sh` ready, smithery CLI)
- [ ] MCP-006: Stripe MCP (`@stripe/mcp`) — needs Stripe secret key (on VPS only)
- [ ] MCP-007: Telegram MCP (`mcp-telegram`) — needs bot token
- [ ] MCP-008: Move `egos-knowledge` MCP from `egos/.claude/settings.json` → `~/.claude/settings.json` (make global)
- [ ] GTM-016: Build `guard-brasil-mcp` — wraps guard.egos.ia.br as Claude tool, publish as `@egosbr/guard-brasil-mcp` (GTM play: devs install it in their Claude session)
- [ ] KB-019: `bun wiki:dedup` — fix HARVEST.md 1944-line triplication caused by wiki:compile running without dedup

---

### Dream Cycle — Overnight Intelligence (2026-04-06)
**SSOT:** `docs/strategy/DREAM_CYCLE_SSOT.md`
**Goal:** Wake up to briefed HQ showing all nightly work. LLM cost: $0 (Gemma 4 31B free).

**Phase 1 — Foundation (DONE ):**

**Phase 2 — Intelligence (this week):**
- [ ] DC-004: `agents/agents/intelligence-engine.ts` — reads nightly logs + TASKS.md, uses Gemma 4 31B, writes egos_nightly_reports + auto-creates TASKS entries
- [ ] DC-005: Extend CCR Governance Sentinel to run intelligence-engine after drift check
- [ ] DC-006: Auto-Healer script — restart containers on known patterns (rule-based, no LLM)
- [ ] DC-011: Tune log-harvester Caddy pattern (false-positive: 472 TLS entries flagged as critical)

**Phase 3 — HQ Integration:**
- [ ] DC-007: HQ "Last Night" card on home page — shows Dream Cycle results from egos_nightly_logs
- [ ] DC-008: HQ `/events` page (CTRL-014) — real-time stream from egos_agent_events + nightly reports
- [ ] DC-009: Morning Briefing (06h30 BRT) — Telegram + WhatsApp summary of overnight work

---

### Skills + Hooks Backlog (2026-04-06)

**Skills:**
- [ ] SKILL-001: `/gate` — manual quality gate scoring (G1-G5 template from .guarani/orchestration/GATES.md). Create `~/.claude/commands/gate.md`
- [ ] SKILL-002: `/mycelium-think` — thinking meta-prompt (different from /mycelium VPS check). Create `~/.claude/commands/mycelium-think.md`
- [ ] SKILL-003: `/brainet` — sync content from .guarani/prompts/meta/brainet.md (if outdated). Verify ~/.claude/commands/brainet.md exists.

**Hooks:**
- [ ] HOOK-001: `~/.claude/hooks/skill-auto-trigger` — UserPromptSubmit hook that detects keywords from .guarani/prompts/triggers.json (7 triggers: strategy, brainet, mycelium, audit, debate, extraction, activation) and injects meta-prompt content as context
- [ ] HOOK-002: `~/.claude/hooks/refinery-gate` — UserPromptSubmit hook for vague prompts (<50 chars) or risky keywords (deletar/remover/migrar/deploy/produção) → inject clarification guidance from .guarani/refinery/classifier.md

---

### OpenClaw Integration Roadmap (2026-04-06)

> **SSOT:** `docs/OPENCLAW_SSOT.md` | **Gateway:** localhost:18789 | **Billing proxy:** localhost:18801

**Current state:** Gateway UP, billing proxy running (subscription:max), Codex proxy port 18802 (gpt-5.4). No channels configured — skeleton install.

**P0 — Curto prazo (esta semana): Base funcional**


**P0 — GAPS CRÍTICOS identificados (2026-04-06):**
- [ ] OC-031: Codex auth.json refresh cron no VPS — token expira, precisa refresh igual ao billing proxy (last_refresh: 2026-04-01)
- [ ] OC-032: VPS watchdog — adicionar monitoramento porta 18802 (Codex proxy) ao /opt/egos-watchdog.sh
- [ ] OC-033: Constitutional review cron no VPS — atualmente só roda local; adicionar ao crontab do VPS
- [ ] OC-034: Codex quota Telegram alert — alertar via Telegram quando quota ≥ 80% usada (rate_limited_count > 0)

**P1 — Médio prazo (2 semanas): Canais + Integração EGOS**

- [ ] OC-006: Decidir estratégia Telegram: (a) migrar egosin_bot para OpenClaw (OpenClaw gerencia o loop), ou (b) manter EGOS Gateway como primário e conectar OpenClaw via sessions API. **Recomendado: opção (b)** — EGOS Gateway tem LGPD/PII, OpenClaw traz skills/multi-device.
- [ ] OC-007: Conectar EGOS Gateway → OpenClaw sessions API — `sessions_spawn` para criar sub-agentes OpenClaw a partir de intent do EGOS orchestrator. Exemplo: usuário pede "pesquise concorrentes" → EGOS spawna sessão OpenClaw com Gem Hunter skill.
- [ ] OC-008: Instalar `@openclaw/whatsapp` channel — conectar ao Evolution API existente (port 8080 no VPS). OpenClaw gerencia loop de mensagens, EGOS Gateway faz PII-check antes de responder.
- [ ] OC-010: Registrar Guard Brasil MCP (`@egosbr/guard-brasil-mcp`) — blocked on KB-019 (MCP server não existe ainda).
- [ ] OC-011: Configurar skills relevantes do ClawHub marketplace — pesquisar: Brave Search, Knowledge Base, Code Execution. Instalar 2-3 skills úteis.

**P2:** OC-012..017 (Hermes local, sessions_spawn multi-agent, Canvas, Discord, cron jobs) — post HERMES MVP go/no-go.

**P3:** OC-018..023 (ClawHub marketplace, A2A, multi-device, Tutor Melkin v2, self-serve onboarding) — post PMF.

 ---
 
 ### Self-Discovery Product (2026-04-06)
 **SSOT:** `docs/SELF_DISCOVERY_ARCHITECTURE.md` | self.egos.ia.br → VPS | B2C wellness (não medical device)
- **Execution order:** SD-001 → 002 → 003 → 004 → 005 → 006/007/008 → 009 → 010..019
- **Named gates:** `deploy` = SD-006 | `security` = SD-007 | `ux` = SD-008 | `launch` = SD-009
- [ ] **SD-001 (P0)**: Inventory v2 source files and define exact extraction scope [DEP: HUM-002, architecture doc]
- [ ] **SD-002 (P0)**: Map backend/frontend/shared boundaries for the future container tree [DEP: SD-001]
- [ ] **SD-003 (P0)**: Define env contract, secrets map, Supabase touchpoints, and `.env.example` contract [DEP: SD-001]
- [ ] **SD-004 (P0)**: Specify Dockerfiles + `docker-compose` shape for port 3098 without implementing yet [DEP: SD-002, SD-003]
- [ ] **SD-005 (P0)**: Specify reverse proxy, health endpoint, watchdog path, and rollback path [DEP: SD-004]
- [ ] **SD-006 (P0 / deploy gate)**: Approve deploy checklist — health check, smoke check, monitoring path, rollback path [DEP: SD-004, SD-005]
- [ ] **SD-007 (P0 / security gate)**: Approve security checklist — disclaimers, secrets handling, PII/log policy, access model [DEP: SD-003, SD-005]
- [ ] **SD-008 (P0 / ux gate)**: Approve UX checklist — onboarding, empty/error states, copy review, acceptance criteria [DEP: SD-002]
- [ ] **SD-009 (P0 / launch gate)**: Approve launch checklist — ICP, analytics path, feedback loop, GTM/dissemination handoff [DEP: SD-006, SD-007, SD-008]
- [ ] **SD-010 (P1)**: Define ICP and pricing hypothesis for the first niche (wellness / procrastination / journaling) [DEP: SD-009]
- [ ] **SD-011 (P1)**: Define landing scope and public positioning without medical claims [DEP: SD-008, SD-010]
- [ ] **SD-012 (P1)**: Define pattern taxonomy for the first production slice (reflection/procrastination/self-sabotage) [DEP: SD-001]
- [ ] **SD-013 (P1)**: Define onboarding flow and first-session success criteria [DEP: SD-008, SD-010]
- [ ] **SD-014 (P1)**: Define analytics, feedback, and session-review signals [DEP: SD-009]
- [ ] **SD-015..019 (P2)**: Post-alpha backlog — prioritize pattern packs, auth/history, API docs, TypeScript migration, freeze backlog. [DEP: SD-014 alpha evidence]

### VPS Infrastructure Optimization & Resource Management (P34-P35)

**Investigation Complete (2026-04-07):** Full VPS audit reveals healthy infrastructure (19 containers stable, 23 agents active, 9-day uptime) but critical RAM pressure (622MB free / 15GB total). Neo4j BR-ACC consuming 4.8GB (31.5% of total). `/opt/backups/` = 15GB of dated Neo4j dumps (2026-04-03/04/05). Decision: Keep BR-ACC online as production SSOT; clean backups; implement intelligent resource management before Hermes MVP.

**SSOT:** `/home/enio/.egos/memory/mcp-store/vps_hetzner_complete_infrastructure_map_2026-04-07.md` | **Handoff:** docs/_current_handoffs/handoff_2026-04-07_doc-drift-shield-plan.md §2

**P0 — Critical (This Week: Before Hermes MVP):**


**P1 — Infrastructure Baseline (P35):**

- [ ] **VPS-CAPACITY-001**: Create capacity planning model — given: current 19 containers, Neo4j 4.8GB, how much RAM remains for Hermes+Codex? Simulate: "if we add X, what breaks?" [OWNER: arch, 2h]
- [ ] **VPS-SWAP-001**: Add 4GB swap partition if cleanup + Neo4j tuning insufficient. Benchmark: does swapping kill performance? (defer if not needed) [OWNER: infra, P1]

---

### Hermes MVP Deployment (P35 — Proposed Start 2026-04-08)

**Investigation Complete (2026-04-07):** Hermes Agent (24/7 executor framework) ready for MVP. Design documented. Deployment path clear. ✅ **RAM cleanup DONE (VPS-BACKUP-001).** ROI: R$0-40/month marginal cost, unlocks always-on research + self-improving skills. Risk: Low (can remove in 1h if needed). Trial period: 1 week, go/no-go gate at 2026-04-19.

**SSOT:** `/home/enio/.egos/memory/mcp-store/hermes_agent_investigation_deep_dive_2026-04-07.md`

**P0 — MVP Deployment (Sequential Phases, Start 2026-04-08):**

**Phase 1: Prep (1 hour)**
- [ ] **HERMES-001-P1**: Confirm `/opt/backups/` cleanup done (VPS-BACKUP-001). Verify: `free -h` shows >2GB available. [DEP: VPS-BACKUP-001 | Owner: infra]
- [ ] **HERMES-001-P2**: Verify Docker/docker-compose versions on VPS. Confirm: `docker --version && docker-compose --version`. Minimum: Docker 20.x, compose 2.x. [Owner: infra, 10min]

**Phase 2: Build (1 hour)**
- [ ] **HERMES-002-P1**: Clone Hermes Agent repo to VPS: `ssh ... cd /opt && git clone https://github.com/NousResearch/hermes-agent.git`. [Owner: infra, 15min]
- [ ] **HERMES-002-P2**: Build Hermes Docker image on VPS: `cd /opt/hermes-agent && docker build -t hermes:latest .`. Confirm: `docker images | grep hermes` shows image. [Owner: infra, 30min]
- [ ] **HERMES-002-P3**: Prepare docker-compose skeleton — copy from investigation doc (lines 778-817) to `/opt/hermes/docker-compose.yml`. [Owner: infra, 10min]

**Phase 3: Configure (30 min)**
- [ ] **HERMES-003-P1**: Create first profile: `hermes profile create egos-kernel --model claude-3-7-sonnet-20250219 --system-prompt "$(cat .guarani/BLUEPRINT-EGOS)"`. [Owner: infra, 15min]
- [ ] **HERMES-003-P2**: Generate `.env` for Hermes: HERMES_MODEL, HERMES_TELEGRAM_TOKEN (from egos-watchdog), HERMES_SQLITE_PATH, HERMES_LOG_LEVEL=info. [Owner: infra, 15min]

**Phase 4: Test (2 hours)**
- [ ] **HERMES-004-P1**: Start Hermes container: `docker-compose up -d` from /opt/hermes/. Wait 30s. [Owner: infra, 5min]
- [ ] **HERMES-004-P2**: Run test task: `hermes task --profile egos-kernel "list /opt/egos/agents"`. Confirm: task completes, outputs agent list. [Owner: infra, 15min]
- [ ] **HERMES-004-P3**: Verify Telegram integration — Hermes should have sent startup message to configured chat_id. Check Telegram. [Owner: infra, 5min]
- [ ] **HERMES-004-P4**: Monitor logs: `docker logs hermes | tail -50`. Check for errors, memory warnings, startup messages. Confirm: clean boot. [Owner: infra, 10min]

**Phase 5: Trial (1 week: 2026-04-08 through 2026-04-15)**
- [ ] **HERMES-005-P1**: Run production trial — Hermes stays online 7 days. Measure: uptime, RAM usage, token consumption, error rate. [Owner: infra, monitoring]
- [ ] **HERMES-005-P2**: Validate: At least 1 auto-generated skill created and persisted to SQLite. Test invoking skill. [Owner: infra]
- [ ] **HERMES-005-P3**: Cost tracking — capture actual token spend vs estimate (R$0-10 for trial week expected). [Owner: infra]
- [ ] **HERMES-005-P4**: Decision gate (2026-04-15): Go/no-go for scaling to 6 profiles. If YES → P35 scope expands. If NO → remove, document learnings. [Owner: Enio]

**P1 — Scaling (P35+ Post-MVP):**

- [ ] **HERMES-006**: Scale to 6 profiles (egos-kernel, egos-strategy, egos-governance, egos-research, egos-ops, egos-learning) — one per domain. [DEP: HERMES-005-P4 go]
- [ ] **HERMES-007**: Integrate Hindsight SDK (persistent memory + world-model sync) — enables GEPA self-improvement. [DEP: HERMES-006]
- [ ] **HERMES-008**: Connect Gem Hunter v7 as Hermes job — automate cross-repo discovery runs. Cron: `0 2 * * * hermes task --profile egos-kernel "analyze-cross-repo-patterns"`. [DEP: HERMES-006 + GEM_HUNTER_V7]
- [ ] **HERMES-009**: Add watchdog for Hermes itself — if process dies, auto-restart. Alert via Telegram. [DEP: HERMES-006]

---

### VPS Orchestration — Codex + Claude Code + OpenClaw + Gemini CLI (P35)

**Context:** VPS runs 5 overlapping execution layers. Need explicit orchestration strategy to avoid conflicts, token quota exhaustion, and cost drift.

**SSOT:** `docs/OPENCLAW_SSOT.md` (OpenClaw routing) | `docs/INFRA_SSOT.md` (VPS services mapping)

**P1:**
- [ ] **ORB-002**: Fallback chain if Codex proxy fails → DashScope/MiniMax-M2.7 [dev, 2h]
- [ ] **ORB-003**: Cost attribution per task → Supabase [dev, 3h]
- [ ] **ORB-004**: HQ widget "Orchestration Status" [UI, 2h]

---

### Gem Research — P31 (2026-04-06): Graphify + A-Evolve + XMCP
**Source:** Grok analysis. Decisions: Graphify=adopt patterns only (codebase-memory-mcp overlap 80%); A-Evolve=bookmark pós PMF; XMCP=install now.

**XMCP — X MCP Server oficial (xdevplatform/xmcp):**
- [ ] **XMCP-001 [BLOCKER]**: Regenerar X credentials — developer.twitter.com → Apps → Keys and Tokens → Regenerate. Atualizar .env (X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET). Atual: 401 Unauthorized. [MANUAL ACTION]
- [ ] **XMCP-002** (dep: XMCP-001): Atualizar /opt/xmcp/.env no VPS com credentials reais + iniciar serviço: `bash /opt/xmcp/start.sh`. Verificar: `curl http://VPS:8000/health`
- [ ] **XMCP-003** (dep: XMCP-002): Adicionar UFW rule VPS: `ufw allow from 172.19.0.0/16 to any port 8000`. Ativar x-mcp no openclaw.json (remover nota INACTIVE).
- [ ] **XMCP-004** (dep: XMCP-002): Criar skill `egos-x-researcher` — usa XMCP searchPostsRecent para monitorar: lgpd, anpd, dpo, "proteção de dados". Saída → Supabase + HQ.
- [ ] **GTM-002-unblock**: Thread Guard Brasil (4 tweets prontos em GTM_SSOT.md §4.1) — BLOQUEADO por X credentials 401. Usar `bun /tmp/post-guard-thread.ts` após XMCP-001.

**Graphify patterns (adotar sem instalar a lib):**
- [ ] **GRF-001 (P2)**: Criar CCR job `graph-report` — usa codebase-memory-mcp query_graph para gerar GRAPH_REPORT.md semanal (god nodes, surprising connections, clusters). Output em `docs/jobs/`.
- [ ] **GRF-002 (P2)**: Embutir graph.html (vis.js) no HQ como painel "Knowledge Graph" — feed de codebase-memory-mcp export. Parte de HQV2-009.
- [ ] **GRF-003 (P2)**: Adicionar ingestão multimodal ao wiki-compiler: PDFs + papers → Supabase `egos_wiki_pages`. Usa Graphify padrão (PDF→AST→nodes).

**A-Evolve patterns (bookmark pós PMF):** AEV-001..002 (P3) — manifest.yaml per skill + evolution loop. See git log for design.

### Governance Mesh Cleanup (2026-04-06 audit)
- [ ] **GOV-001**: CLAUDE.md → thin adapter to `.guarani` kernel [constitution drift]
- [ ] **GOV-002**: Unify workflow catalog (.windsurf/workflows + ~/.egos/workflows + workflow-sync-check.sh)
- [ ] **GOV-003**: Canonical skill distribution ~/.egos/skills vs ~/.claude/skills
- [ ] **GOV-004**: manifest.json SSOT hierarchy → kernel-first `.guarani`
- [ ] **GOV-005**: settings.local.json allowlist audit — hardcoded tokens, unsafe legacy permissions
- [ ] **GOV-006**: Sanitize stale ~/.egos artifacts (.windsurfrules, SSOT_STATUS_20260328.txt)
- [ ] **GOV-007**: Unify repo mesh registry (sync.sh + sync-all-leaf-repos.sh + manifest.json)

### Ratio Collaboration (2026-04-07) — PR #1 open, Guard Brasil wired
**Context:** Fork `enioxt/ratio` — Carlos Victor Rodrigues, Brazilian legal RAG + LangGraph drafting. Goal: PRs that demonstrate EGOS assets and open organic partnership. Branch: `feat/escritorio-multi-provider-llm`, PR #12 (103 tests passing).

**Done:** llm_provider 4 providers ✅ | pii_guard Guard Brasil ✅ | planning id-coercion ✅ | bot review issues ✅ | live pipeline 4/4 ✅ | frontend local ✅

- [ ] **RATIO-001 [P1]**: Submit PR #2 (Guard Brasil) as separate branch after PR #1 merged. Branch: `feat/escritorio-pii-guard`. LGPD compliance, fail-open, 8 tests.
- [ ] **RATIO-002 [P1]**: Open Issue on Carlos's repo re: LGPD gap (fatos_brutos with CPF → Gemini unmasked). Offer Guard Brasil free tier. Frame constructively. Metric: Carlos responds.
- [ ] **RATIO-003 [P2]**: br-acc entity resolution adapter — `entity_resolver.py` + `resolve_parties()` in intake. Maps party names → CPF/CNPJ/OAB/process history via br-acc API. PR #3.
- [ ] **RATIO-004 [P2]**: `.ratio-manifest.yaml` Doc-Drift Shield adoption PR. Claims: `total_documents: 471366`, `lancedb_store_gb: 8.5`. Verified via LanceDB count.
- [ ] **RATIO-005 [P2]**: Full end-to-end test via API with Caso 1 (STJ PDF real) → intake → planning → redaction → adversarial → formatter → download DOCX.
- [ ] **RATIO-006 [P3]**: Draft br-acc API pricing model for Carlos (free 100 lookups/mês + paid). Monetization path proposal.

 ---
