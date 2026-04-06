# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.41.0 | **Updated:** 2026-04-06 | **LAST SESSION:** 2026-04-06 P28 — MASTER_INDEX.md created, HQ-001..HQ-013 tasks added

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

### HQ Dashboard + Master Index (2026-04-06)
**SSOT:** `docs/MASTER_INDEX.md` | **Context:** Universal registry of all EGOS resources

**P0 — Critical Gaps:**
- [ ] **HQ-001**: Register `agent-validator.ts` in `agents.json` — agent exists but not in registry (4-point validation gap)
- [ ] **HQ-002**: Create `AGENTS.md` + `TASKS.md` for `commons/` repo — currently Grade D (only .claude/ folder)
- [ ] **HQ-003**: Add SSOT_REGISTRY pointers to repos 852, br-acc, carteira-livre — upgrade Grade C→A
- [ ] **HQ-004**: Create integration manifests for 6 adapters (slack, discord, telegram, whatsapp, webhook, github)
- [ ] **HQ-005**: Build `intelligence-engine.ts` for Dream Cycle Phase 2 (DC-004 dependency)

**P1 — Integration:**
- [ ] **HQ-006**: Configure OpenClaw Telegram/WhatsApp channels (OC-006..OC-008)
- [ ] **HQ-007**: Complete MCP global setup (obsidian, stripe, telegram pending)
- [ ] **HQ-008**: Build `@egosbr/guard-brasil-mcp` for OpenClaw marketplace
- [ ] **HQ-009**: Complete HQ Dashboard v2 (volume mounts + 5 API routes)
- [ ] **HQ-010**: Fix HARVEST.md deduplication (KB-019)

**P2 — Archive:**
- [ ] **HQ-011**: Archive 11 dormant repos per COMPLETE_REPO_INVENTORY_2026-04-03.md
- [ ] **HQ-012**: Complete Santiago fix-or-kill decision
- [ ] **HQ-013**: Consolidate egos-lab → kernel migration (LAB-ARCHIVE-001..006)

---

### Neural Mesh + Telemetry — DONE (2026-04-01)
EGOS-167/168/175, GH-040..042, EGOS-TELEM-001..005 — all DONE ✅. codebase-memory-mcp (51K nodes), llmrefs (15 docs), SSOT gate, smoke tests, version lock, full telemetry (5 layers). See git log.

---

### EGOS Knowledge System — Karpathy LLM Wiki (2026-04-05)

**Pattern:** 3-layer (raw sources → compiled wiki → schema). Supabase-backed, API-served, agent-compiled.
**Agent:** `agents/agents/wiki-compiler.ts` | **API:** `apps/egos-gateway/src/channels/knowledge.ts`
**Supabase tables:** `egos_wiki_pages` (50 pages), `egos_learnings`, `egos_wiki_changelog`

**Done:**
- [x] KB-001: Supabase schema (3 tables + RLS + indexes) ✅ 2026-04-05
- [x] KB-002: wiki-compiler agent (--compile, --world, --lint, --index, --dry) ✅ 2026-04-05
- [x] KB-003: Gateway API endpoints (7 routes: pages, search, index, learnings, stats) ✅ 2026-04-05
- [x] KB-004: World-model integration (--world generates system overview, P0 blockers, signals) ✅ 2026-04-05
- [x] KB-005: Initial compile — 50 pages from 5 raw source dirs, avg quality 80/100 ✅ 2026-04-05
- [x] KB-006: Agent registered in agents.json + AGENTS.md ✅ 2026-04-05
- [x] KB-007: NPM scripts (wiki:compile, wiki:lint, wiki:index) ✅ 2026-04-05

**P1 — Integration:**
- [x] KB-008: Add wiki:compile to Governance Drift CCR job (auto-compile after drift check) ✅ 2026-04-05
- [x] KB-009: /start Phase 0 — include KB stats (page count, avg quality, stale pages) ✅ 2026-04-05
- [x] KB-010: Record learnings from each Claude Code session (POST /knowledge/learnings on /end) ✅ 2026-04-05
- [x] KB-011: HQ Knowledge Base page (/knowledge) + Mission Control KB card ✅ 2026-04-05

**P1 — Quality:**
- [x] KB-012: Cross-reference enrichment — 3-strategy enrichment (entity/slug/tag), 0 orphans ✅ 2026-04-04
- [x] KB-013: Deduplication — detect similar pages and merge (wiki:dedup) ✅ 2026-04-05
- [x] KB-014: LLM enrichment pass for low-quality pages (<60) via qwen-plus (wiki:enrich) ✅ 2026-04-05

**P2 — Advanced:**
- [x] KB-015: Full-text search with pg_trgm or pgvector embeddings ✅ 2026-04-06 — pg_trgm GIN indexes + ?mode=fts param using phfts(portuguese)
- [x] KB-016: Knowledge graph visualization — /ui dashboard (egos-gateway) with category cards, search, quality scores, learnings panel ✅ 2026-04-04
- [ ] KB-017: Auto-learning from git commits (extract patterns from commit messages + diffs)
- [x] KB-018: MCP server @egos/knowledge-mcp — 5 tools: search_wiki, get_page, get_stats, record_learning, list_learnings ✅ 2026-04-05

---

- [ ] EGOS-169: @aiready/pattern-detect pre-commit (duplicate detection)
- [ ] EGOS-173: CRCDM hooks: llmrefs staleness + auto-heal rename
- [x] EGOS-175: llmrefs blocks added to 5 leaf AGENTS.md (forja, carteira-livre, smartbuscas, br-acc, santiago) ✅ 2026-04-01

---

### Session Initialization v6.0 ✅ LIVE (2026-04-02)
START-001..005 DONE (parallel diagnostics 22s, CI, pre-commit). Design: `docs/SESSION_INITIALIZATION_v6.md`

**Pending (P1):**
- [ ] START-006: Monitor performance 1 week (due 2026-04-09)
- [ ] START-007: v6.1 distributed agent health (SSH parallel)
- [ ] START-008: Dashboard integration (Grafana/Claude Code UI)
- [x] START-009: Alert system (Telegram on health < 40%) ✅ 2026-04-05 — health-monitor.ts polls 5min, score=100, alerts to TELEGRAM_AUTHORIZED_USER_ID

---

### Scheduled Jobs — 3 CCR slots (2026-04-01)

All Haiku, 00-06h BRT, reports in `docs/jobs/` + `docs/gem-hunter/`

- [x] Governance Drift Sentinel — diário 0h17 BRT (trig_01S5za...)
- [x] Code Intel + Security Audit — seg+qui 1h42 BRT (trig_01RDDk...)
- [x] Gem Hunter Adaptive Intelligence — seg+qui 2h37 BRT (trig_01Sn7Y...)
- [x] /start v5.6 → v6.0 — upgraded from skill to self-contained executable ✅ 2026-04-02
- [x] GitHub Actions audit: 9 failing workflows disabled, only essential kept

---

### Eagle Eye — OSINT Licitações ✅ LIVE
**eagleeye.egos.ia.br** | 84 territories | 121 opportunities | daily cron 9am BRT
**Done (EAGLE-000..023):** standalone Docker, Supabase 6 tables, 26 detection patterns, Telegram alerts, PNCP enrichment, 80 territories seeded, integrador 70/30 channel doc, daily cron, real pipeline (36 opps R$10.5M).
- [ ] EAGLE-009: Stripe/Pix for Pro tier (R$497/mo)
- [ ] EAGLE-019: Integrador partnership outreach
- [ ] EAGLE-020: R$250k proposal — deadline 2026-04-29
- [ ] EAGLE-GH-003..010: Classification + extraction + profile + API v2 + MCP + Pix
- [ ] SANT-001: Santiago partner onboarding (MVP ready, waiting partner)

---

### Gem Hunter v6 — Research Discovery Engine ✅ LIVE
**CCR:** seg+qui 2h37 BRT | **Standalone API:** port 3097 | **npm:** @egosbr/gem-hunter v6.0.0
**Done (GH-001..066):** /study+/study-end skills, pair studies (Continue 71/100, Aider 74/100, Cline 72.8/100), PWC pipeline, Papers Without Code, KOL discovery, Telegram+Discord alerts, BRAID GRD, X-reply-bot (VPS hourly cron), ArchitectureSelector, cost-tracker, world-model signals, gem-hunter-server API, pricing.ts, Gateway /gem-hunter channel.

**Active — Pair Studies Queue:**
- [ ] GH-013: EGOS ↔ OpenHands | GH-014: ↔ LangGraph | GH-015: ↔ OpenAI Agents SDK | GH-016: ↔ LiteLLM | GH-017: ↔ Langfuse
- [ ] GH-020: ↔ Mem0 | GH-021: ↔ Temporal | GH-022: ↔ Haystack | GH-023: ↔ DSPy | GH-036: OpenHarness adapter

**Active — Product:**
- [ ] GH-025: `/pr` workflow + GitHub App (pre-merge gate)
- [ ] GH-026: Upgrade codebase-memory-mcp to HTTP/SSE transport
- [ ] GH-027: `.guarani/checks/` layer
**Gem Hunter product (revenue):**
- [x] GH-061: Dashboard gemhunter.egos.ia.br ✅ 2026-04-06 — 288 gems, dark SPA servida em / (sem Next.js)
- [x] GH-067: gem-hunter-server deployed to VPS port 3095, systemd, Caddy ready ✅ 2026-04-05 — [BLOCKER] DNS A record gemhunter.egos.ia.br → 204.168.217.125 needed
- [x] GH-068: API keys Supabase auth | GH-069: Rate limiting ✅ 2026-04-05
- [x] GH-070: WhatsApp v2 — AI orchestrator (Qwen+tools: gem_search/wiki_search/status/costs/agents) + all media types ✅ 2026-04-05
- [x] GH-071: Telegram @EGOSin_bot (egosin_bot) — long-polling + AI orchestrator ✅ 2026-04-05 — send /start to @EGOSin_bot to get your chat_id, then set TELEGRAM_AUTHORIZED_USER_ID
- [ ] GH-073: Weekly email digest

**New tasks from Continue study:**
- [ ] GH-025: `/pr` workflow + GitHub App — pre-merge gate invoking ssot-auditor + code-intel on branch diffs
- [ ] GH-026: Upgrade codebase-memory-mcp to HTTP/SSE transport (enables SaaS deployments)
- [ ] GH-027: `.guarani/checks/` layer — markdown-as-config for non-technical rule authoring

**Gem Hunter CCR:**
- [x] GH-028: Gem Hunter Adaptive CCR extended with Mission 2 (pair analysis Phase 6) ✅ 2026-04-01

**P1 — Reference Repo Study Queue (priority order):**
- [x] GH-010: EGOS ↔ Continue — score 71/100 (done — see P0 section above)
- [x] GH-011: EGOS ↔ Aider — score 74/100, 4 transplants (dry-run, dirty-commit, SWE-Bench eval, weak model) ✅ 2026-04-01
- [x] GH-012: EGOS ↔ Cline (`cline/cline`) — score 72.8/100, 4 transplants (permission-flow-ux, model-gateway-abstraction, ast-aware-context, checkpoint-rollback) ✅ 2026-04-02
- [ ] GH-013: EGOS ↔ OpenHands (`OpenHands/OpenHands`) — full software agent SDK/CLI/GUI
- [ ] GH-014: EGOS ↔ LangGraph (`langchain-ai/langgraph`) — stateful long-running agents, durable execution
- [ ] GH-015: EGOS ↔ OpenAI Agents SDK (`openai/openai-agents-python`) — handoffs, guardrails, tracing
- [ ] GH-016: EGOS ↔ LiteLLM (`BerriAI/litellm`) — multi-model proxy, cost tracking, routing
- [ ] GH-017: EGOS ↔ Langfuse (`langfuse/langfuse`) — observability, prompt versioning, evals

**Aider study done (GH-031..039):** pre-edit-safety hook, CLAUDE.md §13 model guide, OpenHarness early-warning, Telegram gem alerts, BRAID Mode GRD, x-reply-bot VPS cron. Details: git log.
- [ ] GH-032: EGOS edit benchmark (SWE-Bench inspired, 20 tasks)
- [ ] GH-036: OpenHarness adapter in packages/shared/harness/

**Gem Hunter v5.1+v6.0 DONE (GH-043..065):** PWC pipeline, low-star scoring, ArchitectureSelector adapter, structural validation, auto-queue, signals ingestion, Papers Without Code, KOL discovery, evolution engine, multi-LLM fallback, Telegram alerts, multi-stage paper pipeline, cost budgeting, standalone API, MONETIZATION_SSOT, pricing.ts, gem-hunter npm v6.0.0. Details: git log.

*Month 2-3 — Product Scale:*
- [x] GH-061: Dashboard web — gemhunter.egos.ia.br ✅ 2026-04-06
- [x] GH-062: packages/gem-hunter/ — @egosbr/gem-hunter v6.0.0 ✅ 2026-04-02
- [ ] GH-063: x402 pay-per-call — M2M agent payments via x402 protocol
- [x] GH-064: Discord webhook alerts — sendGemDiscordAlert() rich embeds (score≥80, color-coded); DISCORD_WEBHOOK_URL env ✅ 2026-04-02
- [x] GH-066*: Gateway /gem-hunter channel — sector filter, topics, product pricing, trending ✅ 2026-04-04 (NOTE: renamed from Paper→Code)
- [ ] GH-067: Deploy gem-hunter-server to VPS (gemhunter.egos.ia.br) + Caddy routing → P0 revenue
- [x] GH-068: Auth — API keys via Supabase `gem_hunter_api_keys` table + Bearer token validation ✅ 2026-04-05
- [x] GH-069: Rate limiting middleware (tier-aware: free/starter/pro/pay-per-use) ✅ 2026-04-05
- [ ] GH-070: Chatbot orchestrator — WhatsApp channel NLP intent → tool calls → gem-hunter → curated reply
- [x] GH-071: Telegram bot (/hunt, /trending, /sector slash commands) ✅ 2026-04-06 — all 3 commands live in telegram.ts, /sector validates 6 sectors
- [ ] GH-072: Chatbot tier enforcement (200 queries/mo for R$149/mo chatbot plan)
- [ ] GH-073: Email digest — weekly top 10 gems to subscribers
- SSOT: docs/gem-hunter/GEM_HUNTER_PRODUCT.md

**P2 — Advanced Studies:**
- [ ] GH-020: EGOS ↔ Mem0 — persistent agent memory layer
- [ ] GH-021: EGOS ↔ Temporal TS SDK — durable workflow engine
- [ ] GH-022: EGOS ↔ Haystack — RAG/retrieval/context engineering
- [ ] GH-023: EGOS ↔ DSPy — programmatic prompt optimization
- [ ] GH-024: Lego Assembler agent — consumes `.md` SSOT blocks from discovery engine

---

### Claude Code Hardening + Observability (archived)
LEAK/AI/OBS 001..013 done. Pending: LEAK-010..012 (monitor repos), AI-008..010 (OTel wiring), OBS-010..013 (privacy logs) — P2.
**Ref repos done:** Continue 71/100, Aider 74/100, Cline 72.8/100, agent-scaling-laws 87% ArchSelector.
**P1 queue:** OpenHands, LangGraph, OpenAI Agents SDK, LiteLLM, Langfuse, Mem0, Temporal TS.

---

### X.com Presence & Rapid Response (2026-04-01)

**Context:** Speed-to-thread matters. When a trending topic matches our capabilities, we must respond in hours, not days.

**Code Written (not deployed):**
- [x] X-001: `scripts/x-reply-bot.ts` CODE ONLY (348 LOC) — NOT deployed on VPS, no cron, needs X_BEARER_TOKEN ⚠️
- [x] X-002: `scripts/rapid-response.ts` CODE ONLY (217 LOC) — manual utility, not automated ⚠️
- [x] X-003: VPS cron deploy ✅ Verified 2026-04-04 — x-reply-bot running hourly on VPS cron (0 * * * *).
- [x] X-004: Hermes-3 added to llm-provider (model config only, no active usage) ✅ 2026-04-01
- [x] X-005: `scripts/check-legacy-code.sh` in pre-commit ✅ 2026-04-01

**P1 — Expand:**
- [x] X-006: Grow capability profiles in rapid-response.ts (add br-acc, 852, BRAID executor) ✅ 2026-04-06 — br_acc, sistema_852, gem_hunter profiles added
- [x] X-007: `--post-thread` flag in rapid-response.ts — auto-post first tweet of thread ✅ 2026-04-06 — OAuth 1.0a posting, falls back to manual instructions
- [x] X-008: Daily X report to Telegram (how many replies sent, top threads engaged) ✅ 2026-04-06 — RunStats + sendDailyReport() in x-reply-bot.ts
- [ ] X-009: Trending topic scanner — check X API hourly for rising keywords vs our capabilities
- [ ] X-010: "Clean showcase" branch auto-creator — when topic detected, create `showcase/<topic>` with only clean files

**P2 — Upgrade:**
- [ ] X-011: Upgrade to Basic tier ($100/mo) when bot proves value — 3,000 writes/month vs 1,500
- [ ] X-012: Build thread scheduler — post multi-tweet threads with 2-min gaps
- [ ] X-013: Analytics dashboard — track which replies got most engagement

**X API Rate Limits (Free tier):**
- Write: 50/day hard limit → bot uses 40 (10 buffer)
- Search: 10 req/15min → 1 search per topic per run
- Run schedule: hourly, max 3 replies per run

---

### Block Intelligence Model — EGOS as Mini-AGI (2026-04-01)

**Done (4/4 P0):** INTEL-001..004 ✅ (world-model.ts, /start Phase 0, AGENTS.md IC/DRI/Coach, BRAID GRD)

**P0 — World Model Foundation (NEW 2026-04-03):**
- [ ] WM-001: Setup hardware local LLM (Ollama/LM Studio) — instalar Qwen2.5-7B ou Hermes-3-8B na máquina 24GB VRAM
- [ ] WM-002: Integrate local LLM to world-model.ts — extender interface para reasoning queries
- [ ] WM-003: Capability composition suggestions — dada task, sugerir agents/capabilities (embedding similarity)
- [ ] WM-004: Dataset preparation — coletar tasks + decisions para fine-tuning futuro

**P1 — Signal Layer:**
- [x] INTEL-005: Signal ingestion — Gem Hunter scores > 80 → auto-append to world model signals (= GH-050) ✅ 2026-04-06 — gem-hunter.ts appends type:gem_discovery, capped at 50
- [ ] INTEL-006: Proactive blocker detection — world model scans P0 list → creates TASKS entries if blocker stale > 7 days
- [ ] INTEL-007: `--mermaid` output from world-model.ts → embed in /start briefing as ASCII architecture snapshot

**P1 — World Model Enhanced (NEW 2026-04-03):**
- [ ] WM-005: Implement dynamics model (simulação básica — prediz estado futuro dado ação)
- [ ] WM-006: Causal discovery — aprender relações causa-efeito do histórico EGOS
- [ ] WM-007: Counterfactual reasoning — "o que teria acontecido se..."
- [ ] WM-008: Model-predictive control para planning ótimo

**P2 — Full Intelligence:**
- [ ] INTEL-008: DRI auto-assignment — when P0 task has no commit activity for 3 days, auto-flag + Telegram alert
- [ ] INTEL-009: Capability composition map — intelligence layer dynamically suggests which agents to invoke for a given task
- [ ] INTEL-010: World model diff — compare snapshots to detect regression (tasks going from [x] back to [ ])

**P2 — Ethics & Safety (NEW 2026-04-03):**
- [ ] WM-009..016: Safety+ethics+AGI capabilities (Qwen3Guard, constitutional rules, ATRiAN, auto-observation, self-modification, long-horizon planning) — P2/P3

**SSOT:** `docs/strategy/WORLD_MODEL_SSOT.md` — conceito completo, roadmap, hardware 16-24GB VRAM

---

### Eagle Eye v2 — Decision Intelligence Engine (GenHunter Spec 2026-04-02)
**Done:** EAGLE-020 spec analyzed, BIZ-001 pricing, EAGLE-GH-001 scoring-service, EAGLE-GH-002 document-parser (78%), EAGLE-GH-005 insight-generator ✅
**P0:** EAGLE-GH-003 classification-service, EAGLE-GH-004 extraction-service
**P1:** EAGLE-GH-006 profile-service, EAGLE-GH-007 feedback-learning, EAGLE-GH-008 REST API v2, EAGLE-GH-009 MCP server, EAGLE-GH-010 Stripe Pix
**P2:** EAGLE-GH-011..013 dashboard v2, Telegram routing, chatbot NL query
**DEADLINE:** EAGLE-023 — R$250k proposal by 2026-04-29
### P19-P20 Tasks — Active (archived done, see git log for P20 full list)

**P0 — Revenue:**
- [ ] MONETIZE-011: Deploy v0.2.3 to VPS with STRIPE_METER_ID env var
- [ ] MONETIZE-012: NOWPayments webhook URL config — ENIO action required
- [ ] MASTER-005: NLP intent classifier (Haiku, ~$1/day) for WhatsApp NL commands

**P1 — Infrastructure:**
- [ ] HERMES-001: Wire Hermes-3 as BRAID mechanical executor
- [ ] CTX-001: Context recovery hook to /start
- [ ] CTX-002: Auto-index codebase-memory-mcp on /start

### Partnership & Distribution Strategy (2026-04-05)

**Goal:** Find technical + business partners to accelerate Guard Brasil to enterprise scale.
**SSOT:** `docs/strategy/PARTNERSHIP_STRATEGY.md`

**P0 — Immediate (this week):**
- [ ] PART-001: Publish Guard Brasil on npm + ProductHunt (M-007 emails first)
- [x] PART-002: Posts X.com + LinkedIn preparados ✅ 2026-04-06 — docs/business/PART002_SOCIAL_POSTS.md (aguarda og-image + postagem manual)
- [ ] PART-003: Reach out to 3 DPO/compliance SaaS BR (templates ready: docs/business/OUTREACH_EMAIL_TEMPLATES.md)
- [ ] PART-004: Submit to Stripe App Marketplace (already on Stripe — low friction)

**P1 — Distribution Partners:**
- [ ] PART-005: Nuvemshop / VTEX app store integration (e-commerce PII protection)
- [ ] PART-006: Totvs / SAP BR partner program (ERP + LGPD = natural fit)
- [ ] PART-007: AWS Marketplace listing (SaaS contract, pay-as-you-go)
- [ ] PART-008: Reach out to DPOnet / OneTrust BR for white-label or API partnership

**P1 — Enterprise Layer:**
- [ ] PART-009: SLA documentation v1.0 (99.9% uptime, <5ms P95, incident response)
- [ ] PART-010: SOC2 readiness assessment (with Vanta or Secureframe)
- [ ] PART-011: Enterprise pricing page (custom contracts, volume, dedicated support)
- [ ] PART-012: Security questionnaire template (ready for enterprise procurement)

**P2 — Technical Integrations:**
- [ ] PART-013: LangChain Guard Brasil tool (npm @egosbr/guard-brasil-langchain)
- [ ] PART-014: Zapier / Make.com connector
- [ ] PART-015: Bubble.io plugin (no-code market)

---

### Evaluated & Deferred (2026-04-05)

**HiClaw (agentscope-ai/HiClaw):** Analyzed. Matrix rooms + MinIO + Higress = overhead for zero users. Already have WhatsApp gateway + Caddy + Supabase. **SKIP.**
**PAL (agno-agi/pal):** Analyzed. Compiler + Linter pattern adopted via wiki-compiler agent. Syncer not needed (Supabase > Git sync). **ADOPTED partially.**
**Karpathy LLM Wiki gist:** Adopted. 3-layer pattern (raw → wiki → schema) is now KB-001..007. **ADOPTED fully.**
**Fine-tuning próprio (Gemma 2B/Qwen 7B):** VPS has 540MB free RAM, 0 GPU. Fine-tune on Colab is possible but not 90-day focus. WM-001..004 covers dataset prep. **DEFERRED to P2.**

### P23-P24 Sessions (2026-04-05..2026-04-06) — EGOS HQ + Skills Sync — COMPRESSED ✅

**DONE:** CTRL-001..012 (HQ live, JWT auth, X Monitor, pr-review GH Action, 11 skills), SYNC-001, DEPS-001 (git log shows all items). HQ at hq.egos.ia.br, TLS fixed, Caddy resolved container name issue.

**P25-onward pending:** DEPS-002 (schedule), HERMES-001 (Hermes-3 executor), GUARANI-001..003 (refinery/triggers/gates hooks)

---

### P25 — GTM-First Phase (2026-04-06)

**North Star:** R$30k MRR by 2026-06-30. Every task must answer "who uses this?"
**SSOT:** `docs/strategy/PARTNERSHIP_STRATEGY.md` | Market research: `docs/business/MARKET_RESEARCH_GUARD_BRASIL_2026.md` (moved from business/)
**ICP (confirmed):** CTOs/backend devs at fintechs+healthtechs 50-500 employees. Handle CPF/RG daily, ANPD pressure, buy in days.
**Positioning:** "The Presidio for Brazil — free API key, zero setup, 15 BR PII patterns." Presidio has 0 BR patterns.
**Key insight:** Privacy Tools BR = PARTNER not competitor (process tool, no API). OneTrust/BigID = enterprise (R$50k+), not our market.

**P0 — INCIDENT 2026-04-06 (force-push by scheduled agent):**
- [ ] INC-001: A scheduled CCR job (likely Code Intel + Security Audit, author "Claude <noreply@anthropic.com>") force-pushed to origin/main and dropped 9 commits of P26/P27 work. Recovered via merge `1d1ef23`. Mitigations applied: (1) `.husky/pre-push` blocks non-FF push to protected branches locally, (2) GitHub branch protection enabled (allow_force_pushes=false, allow_deletions=false). **Action:** identify which scheduled job did this — check claude.ai/code/scheduled history for runs that touched git, fix the agent to do `git fetch && git rebase origin/main` before any push, prefer `git pull --rebase` or worktree isolation. No more direct commits on detached/stale main.

**P0 — SOCIAL FIRST (reprio 2026-04-06 per Enio): X.com → LinkedIn → email**
- [ ] GTM-002: Publish 4-tweet showcase thread on X.com @anoineim — demo Guard Brasil (CPF/RG/MASP, 4ms, free tier). Drafts ready: docs/business/PART002_SOCIAL_POSTS.md. **Blocker:** no scripts/x-post.ts yet (x-reply-bot has OAuth1.0a but only postReply). Action: build scripts/x-post.ts (thread mode), post today.
- [ ] GTM-009: Publish LinkedIn post targeting compliance managers + DPOs BR. Draft ready: docs/business/PART002_SOCIAL_POSTS.md. **Blocker:** no LINKEDIN_* credentials in .env + LinkedIn API requires OAuth2 app approval. Action: post MANUALLY (copy/paste) — fastest path, autonomous posting defer to GTM-014.
- [ ] GTM-011: X.com solo tweet "ANPD está acelerando fiscalização em 2026..." + link free tier (from market research). Post after GTM-002 thread lands.
- [ ] GTM-014: **NEW** — scripts/x-post.ts: standalone thread poster (reuse OAuth1.0a from x-reply-bot lines 169-225). Features: reads markdown → posts thread → returns thread URL. Required for GTM-002/011 autonomous.
- [ ] GTM-015: og-image.jpg for Guard Brasil (1200x630, HTML template ready). Playwright screenshot automation. Plan: `/home/enio/.claude/plans/precious-doodling-clover.md` (ready next session).
- [ ] M-007: Send 5 outreach emails to DPOs/compliance teams (templates: docs/business/OUTREACH_EMAIL_TEMPLATES.md). Now P0#2 (was oldest blocker, reprio'd behind social per Enio 2026-04-06). Days stale: 7+.

**P0 — GTM support (unchanged):**
- [ ] GTM-001: Update x-reply-bot search queries to target LGPD/compliance/DPO/ANPD conversations on X.com (currently too broad — add keywords: lgpd, anpd, dpo, "proteção de dados", "vazamento de dados", "conformidade")
- [ ] GTM-003: Add GTM metrics card to HQ home page — shows: MRR (R$0), customers (0), M-007 status (STALE), outreach sent/responded, pending demos
- [ ] GTM-004: Add partner/community discovery track to Gem Hunter — queries: "lgpd api", "data privacy compliance brazil", "dpo tools brasil", "gdpr brazil saas", "pii detection api". Output feeds PART-001..015 pipeline.
- [ ] GTM-005: Guard Brasil demo video (90 seconds) — record screen: API call → PII detected → LGPD report. Upload to X.com thread.

**P1 — Visibility:**
- [ ] GTM-006: Deploy Guard Brasil docs at guard.egos.ia.br/docs with interactive API playground (Scalar or Swagger UI)
- [ ] GTM-007: Submit Guard Brasil to ANPD's public registry of DPO tools (builds legitimacy)
- [ ] GTM-008: ProductHunt launch — prepare assets, schedule for Tuesday/Wednesday (peak traffic days)

**P1 — Content GTM (from market research):**
- [ ] GTM-010: dev.to post "Como detectar CPF, RG e MASP em sua API Node.js em 5 minutos" — with live Guard Brasil example. Target: Brazilian backend devs.
- [ ] GTM-011: X.com thread "ANPD está acelerando fiscalização em 2026. Aqui está uma API gratuita para verificar se seu app vaza PII brasileiro." + link free tier
- [ ] GTM-012: Reach out to Privacy Tools BR for partnership/integration (they have DPO customers who need our API layer)
- [ ] GTM-013: Nuvemshop / VTEX app store — create integration guide + submit app listing

---

### HQ Dashboard v2 (2026-04-06)

**Goal:** Mission Control shows full system state (tasks, gems, world model, GTM metrics, system map)
**Prerequisite:** Volume mounts on VPS (data bound to /data/ inside container)

**P0 — Volume mounts (needed for all v2 routes):**
- [ ] HQ-000: Add Docker volume mounts to VPS docker-compose.yml: TASKS.md, world-model/, gem-hunter/latest-run.json, agents.json, CAPABILITY_REGISTRY.md → /data/*

**P1 — API Routes (apps/egos-hq/app/api/hq/):**
- [ ] HQ-001: `tasks/route.ts` — parse /data/TASKS.md → `{categories, priorities, total, done, pending, p0_stale}`
- [ ] HQ-002: `world-model/route.ts` — read /data/world-model/current.json → full snapshot (health%, blockers, agents, signals)
- [ ] HQ-003: `gems/route.ts` — read /data/gem-hunter/latest-run.json → top gems + filters (score, source, category)
- [ ] HQ-004: `system-map/route.ts` — read /data/agents.json + CAPABILITY_REGISTRY.md → `{nodes, edges}` for D3
- [ ] HQ-005: `gtm/route.ts` — aggregate: MRR from Supabase, M-007 status, outreach count, pending demos

**P2 — Dashboard Pages:**
- [ ] HQ-006: `/tasks` page — Kanban by priority (P0 red, P1 yellow, P2 blue), done/pending counts
- [ ] HQ-007: `/world-model` page — health% gauge, P0 blocker cards, agent inventory, signal feed
- [ ] HQ-008: `/gems` page — filterable card grid (score badge, source icon, category color, search)
- [ ] HQ-009: `/system-map` page — interactive D3 graph (capability domains as nodes, agent edges)
- [ ] HQ-010: Update nav in hq-layout.tsx with new links (tasks, world-model, gems, system-map, gtm)

---

### P26 — MCPs + Focus v2.0 (2026-04-06)

**Completed:**
- [x] MCP-001: Firecrawl MCP installed (`fc-45cf069ee7ef4c3aa4942a41127d8629`, tested against guard.egos.ia.br) ✅ 2026-04-06
- [x] MCP-002: GitHub MCP installed (PAT token, repo access) ✅ 2026-04-06
- [x] MCP-003: Brave Search MCP installed (`BSA0E6k_mAdnrOrieC_zRvLGhuu-4lp`) ✅ 2026-04-06
- [x] MCP-004: Playwright MCP installed (headless browser automation) ✅ 2026-04-06
- [x] FOCUS-001: focus-enforcement v2.0 — FORBIDDEN-list replaces allowlist (researcher-builder profile) ✅ 2026-04-06
- [x] INFRA-001: pre-commit hook TTY graceful fallback for non-interactive environments ✅ 2026-04-06
- [x] RES-001: Guard Brasil market research — ICP confirmed, 5 competitors mapped, Privacy Tools BR = partner ✅ 2026-04-06

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

**Phase 1 — Foundation (DONE ✅):**
- [x] DC-001: Supabase tables `egos_nightly_logs` + `egos_nightly_reports` (migration applied) ✅ 2026-04-06
- [x] DC-002: Log Harvester script v1.1 (bash, 9 containers, severity classification) ✅ 2026-04-06
- [x] DC-003: VPS cron `0 2 * * *` (23h00 BRT) + Telegram alerts on critical ✅ 2026-04-06
- [x] LLM-001: Google AI Studio provider (Gemma 4 31B + Gemini 2.5 Flash free quota) ✅ 2026-04-06
- [x] LLM-002: Qwen 3.6 Plus free via OpenRouter ($0/token) — new first OpenRouter model ✅ 2026-04-06

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

**Current state:** Gateway UP (v2026.4.5, Node 22), billing proxy running (subscription=max), config valid, WebUI at http://127.0.0.1:18789, WebSocket handshake OK. **No channels configured yet** — only skeleton install.

---

**P0 — Curto prazo (esta semana): Base funcional**

- [x] OC-001: Telegram local — decidido: @egosmarkets_bot no VPS, local sem Telegram (evitar conflito com EGOS Gateway @EGOSin_bot). VPS pronto.
- [x] OC-002: Pipeline testado — `openclaw agent --message "..."` → billing proxy → Claude Sonnet 4.6 (PIPELINE_FINAL_OK ✅)
- [x] OC-003: Modelo padrão: `anthropic-subscription/claude-haiku-4-5-20251001` (P28: Haiku default, Sonnet complex, fallback: Qwen3-free+DashScope). Fixes: `api:"anthropic-messages"` + `apiKey` + auth-profiles.json.
- [x] OC-004: `~/.openclaw/workspace/USER.md` populado com perfil Enio (projetos, infra, preferências, estilo).
- [x] OC-005: Token auto-refresh: `0 */4 * * *` rsync credentials local→VPS. Proxy relê por request — sem restart.

- [x] OC-024: VPS watchdog (/opt/egos-watchdog.sh) — */5min cron, 10 containers + 4 endpoints + OAuth freshness, Telegram alert ✅ 2026-04-06
- [x] OC-025: HQ health 4/4 services (Guard, Gateway, OpenClaw, BillingProxy via internal URLs) + /api/hq/health made public ✅ 2026-04-06
- [x] OC-026: UFW rule — Docker infra_bracc 172.19.0.0/16 → port 18801 (billing proxy) ✅ 2026-04-06
**P1 — Médio prazo (2 semanas): Canais + Integração EGOS**

- [ ] OC-006: Decidir estratégia Telegram: (a) migrar egosin_bot para OpenClaw (OpenClaw gerencia o loop), ou (b) manter EGOS Gateway como primário e conectar OpenClaw via sessions API. **Recomendado: opção (b)** — EGOS Gateway tem LGPD/PII, OpenClaw traz skills/multi-device.
- [ ] OC-007: Conectar EGOS Gateway → OpenClaw sessions API — `sessions_spawn` para criar sub-agentes OpenClaw a partir de intent do EGOS orchestrator. Exemplo: usuário pede "pesquise concorrentes" → EGOS spawna sessão OpenClaw com Gem Hunter skill.
- [ ] OC-008: Instalar `@openclaw/whatsapp` channel — conectar ao Evolution API existente (port 8080 no VPS). OpenClaw gerencia loop de mensagens, EGOS Gateway faz PII-check antes de responder.
- [x] OC-009: `HEARTBEAT.md` configurado (Guard Brasil health, billing proxy, EGOS Gateway, Gem Hunter, daily summary).
- [ ] OC-010: Registrar Guard Brasil MCP (`@egosbr/guard-brasil-mcp`) — blocked on KB-019 (MCP server não existe ainda).
- [ ] OC-011: Configurar skills relevantes do ClawHub marketplace — pesquisar: Brave Search, Knowledge Base, Code Execution. Instalar 2-3 skills úteis.

**P2 — Médio prazo (1 mês): Funcionalidades avançadas**

- [ ] OC-012: Wire OpenClaw + Hermes-3 (8B local) — configurar provider `hermes-local` apontando para Hermes rodando via Ollama/llama.cpp. Usar para tasks autônomas overnight sem custo de API.
- [ ] OC-013: Configurar `sessions_spawn` para multi-agent: OpenClaw spawna sub-agentes para Gem Hunter hunts, Guard Brasil scans, kb wiki compilation. Cada sub-agente roda em sessão isolada.
- [ ] OC-014: Integrar OpenClaw Canvas — habilitar canvas-host para visualizações de dados (Gem Hunter dashboard, Guard Brasil stats) acessíveis via chat.
- [x] OC-015: `TOOLS.md` configurado (SSH VPS, serviços EGOS, billing proxy, repos, bots).
- [ ] OC-016: Instalar `@openclaw/discord` channel — criar servidor Discord EGOS para demo público do Guard Brasil. Bot responde a perguntas LGPD/PII.
- [ ] OC-017: Configurar cron jobs no OpenClaw (`~/.openclaw/cron/jobs.json`) — daily: compilar wiki, weekly: Gem Hunter hunt, monthly: PII pattern review.

**P3 — Longo prazo (3 meses): GTM + Produto**

- [ ] OC-018: Construir `guard-brasil-mcp` como skill publicada no ClawHub — qualquer usuário OpenClaw pode instalar Guard Brasil PII detection. GTM play: **distribuição orgânica via marketplace de 13K+ skills**.
- [ ] OC-019: Criar skill pública `egos-knowledge-mcp` no ClawHub — acesso à KB EGOS via OpenClaw. Showcase de capacidade para potenciais clientes.
- [ ] OC-020: Integrar OpenClaw A2A Gateway — conectar EGOS agents ao protocolo A2A (Agent-to-Agent) do OpenClaw. Permite que agentes EGOS colaborem com agentes de outros usuários OpenClaw.
- [ ] OC-021: Configurar multi-device — parear telefone Android + tablet com OpenClaw gateway via QR code. Todas as respostas chegam em todos os dispositivos.
- [ ] OC-022: Tutor Melkin v2 via OpenClaw — substituir arquitetura atual do tutor por OpenClaw como runtime. Melkin = persona no SOUL.md. Canais: Telegram + WhatsApp + Web. Hermes para tasks autônomas.
- [ ] OC-023: Avaliar OpenClaw para Guard Brasil self-serve onboarding — usuário instala Guard Brasil + OpenClaw, configura PII-scan automático em seus próprios canais de mensagem. Pricing: R$99/mo para essa stack.
