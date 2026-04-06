# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.44.0 | **Updated:** 2026-04-06 | **LAST SESSION:** P32 — documentation alignment sweep; INFRA audit restored; BRACC boundary documented; governance drift 0; wiki compile side effect recorded

---

### Documentation Alignment Sweep (2026-04-06)
**SSOT:** `docs/DOCUMENTATION_ARCHITECTURE_MAP.md` | **Context:** principal docs aligned, missing audit restored, governance verification closed

**Done:**

**Follow-up:**
- [ ] DOC-005: Continue terminology sanitization on remaining legacy governance/docs surfaces still using `Sacred Code` or `Frozen Zones`

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

**P1 — Integration:**

**P1 — Quality:**

**P2 — Advanced:**
- [ ] KB-017: Auto-learning from git commits (extract patterns from commit messages + diffs)

---

- [ ] EGOS-169: @aiready/pattern-detect pre-commit (duplicate detection)
- [ ] EGOS-173: CRCDM hooks: llmrefs staleness + auto-heal rename

---

### Session Initialization v6.0 ✅ LIVE (2026-04-02)
START-001..005 DONE (parallel diagnostics 22s, CI, pre-commit). Design: `docs/SESSION_INITIALIZATION_v6.md`

**Pending (P1):**
- [ ] START-006: Monitor performance 1 week (due 2026-04-09)
- [ ] START-007: v6.1 distributed agent health (SSH parallel)
- [ ] START-008: Dashboard integration (Grafana/Claude Code UI)

---

### Scheduled Jobs — 3 CCR slots (2026-04-01)

All Haiku, 00-06h BRT, reports in `docs/jobs/` + `docs/gem-hunter/`


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
- [ ] GH-073: Weekly email digest

**New tasks from Continue study:**
- [ ] GH-025: `/pr` workflow + GitHub App — pre-merge gate invoking ssot-auditor + code-intel on branch diffs
- [ ] GH-026: Upgrade codebase-memory-mcp to HTTP/SSE transport (enables SaaS deployments)
- [ ] GH-027: `.guarani/checks/` layer — markdown-as-config for non-technical rule authoring

**Gem Hunter CCR:**

**P1 — Reference Repo Study Queue (priority order):**
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
- [ ] GH-063: x402 pay-per-call — M2M agent payments via x402 protocol
- [ ] GH-067: Deploy gem-hunter-server to VPS (gemhunter.egos.ia.br) + Caddy routing → P0 revenue
- [ ] GH-070: Chatbot orchestrator — WhatsApp channel NLP intent → tool calls → gem-hunter → curated reply
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

**P1 — Expand:**
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
**SSOT:** `docs/GTM_SSOT.md` (consolidated 2026-04-06 — replaces PARTNERSHIP_STRATEGY, OUTREACH_EMAIL_TEMPLATES, PART002_SOCIAL_POSTS, PART003_LAUNCH_THREAD, M007_OUTREACH_STRATEGY_EMAILS, DISTRIBUTION_PARTNERS_BR)

**P0 — Immediate (this week):**
- [ ] PART-001: Publish Guard Brasil on npm + ProductHunt (M-007 emails first)
- [ ] PART-003: Reach out to 3 DPO/compliance SaaS BR (templates ready: docs/GTM_SSOT.md §5)
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
**SSOT:** `docs/GTM_SSOT.md` | Market research: `docs/business/MARKET_RESEARCH_GUARD_BRASIL_2026.md`
**ICP (confirmed):** CTOs/backend devs at fintechs+healthtechs 50-500 employees. Handle CPF/RG daily, ANPD pressure, buy in days.
**Positioning:** "The Presidio for Brazil — free API key, zero setup, 15 BR PII patterns." Presidio has 0 BR patterns.
**Key insight:** Privacy Tools BR = PARTNER not competitor (process tool, no API). OneTrust/BigID = enterprise (R$50k+), not our market.

**P0 — INCIDENT 2026-04-06 (force-push by scheduled agent):**
- [ ] INC-001: A scheduled CCR job (likely Code Intel + Security Audit, author "Claude <noreply@anthropic.com>") force-pushed to origin/main and dropped 9 commits of P26/P27 work. Recovered via merge `1d1ef23`. Mitigations applied: (1) `.husky/pre-push` blocks non-FF push to protected branches locally, (2) GitHub branch protection enabled (allow_force_pushes=false, allow_deletions=false). **Action:** identify which scheduled job did this — check claude.ai/code/scheduled history for runs that touched git, fix the agent to do `git fetch && git rebase origin/main` before any push, prefer `git pull --rebase` or worktree isolation. No more direct commits on detached/stale main.

**P0 — SOCIAL FIRST (reprio 2026-04-06 per Enio): X.com → LinkedIn → email**
- [ ] GTM-002: Publish 4-tweet showcase thread on X.com @anoineim — demo Guard Brasil (CPF/RG/MASP, 4ms, free tier). Drafts ready: docs/GTM_SSOT.md §4.1. **Blocker:** no scripts/x-post.ts yet (x-reply-bot has OAuth1.0a but only postReply). Action: build scripts/x-post.ts (thread mode), post today.
- [ ] GTM-009: Publish LinkedIn post targeting compliance managers + DPOs BR. Draft ready: docs/GTM_SSOT.md §4.3. **Blocker:** no LINKEDIN_* credentials in .env + LinkedIn API requires OAuth2 app approval. Action: post MANUALLY (copy/paste) — fastest path, autonomous posting defer to GTM-014.
- [ ] GTM-011: X.com solo tweet "ANPD está acelerando fiscalização em 2026..." + link free tier (from market research). Post after GTM-002 thread lands.
- [ ] GTM-014: **NEW** — scripts/x-post.ts: standalone thread poster (reuse OAuth1.0a from x-reply-bot lines 169-225). Features: reads markdown → posts thread → returns thread URL. Required for GTM-002/011 autonomous.
- [ ] GTM-015: og-image.jpg for Guard Brasil (1200x630, HTML template ready). Playwright screenshot automation. Plan: `/home/enio/.claude/plans/precious-doodling-clover.md` (ready next session).
- [ ] M-007: Send 5 outreach emails to DPOs/compliance teams (templates: docs/GTM_SSOT.md §5). Now P0#2 (was oldest blocker, reprio'd behind social per Enio 2026-04-06). Days stale: 7+.

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

**Current state:** Gateway UP, billing proxy running (subscription=max), Codex proxy port 18802 (gpt-5.4). No channels configured — skeleton install.

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

**P2 — Médio prazo (1 mês): Funcionalidades avançadas**

- [ ] OC-012: Wire OpenClaw + Hermes-3 (8B local) — configurar provider `hermes-local` apontando para Hermes rodando via Ollama/llama.cpp. Usar para tasks autônomas overnight sem custo de API.
- [ ] OC-013: Configurar `sessions_spawn` para multi-agent: OpenClaw spawna sub-agentes para Gem Hunter hunts, Guard Brasil scans, kb wiki compilation. Cada sub-agente roda em sessão isolada.
- [ ] OC-014: Integrar OpenClaw Canvas — habilitar canvas-host para visualizações de dados (Gem Hunter dashboard, Guard Brasil stats) acessíveis via chat.
- [ ] OC-016: Instalar `@openclaw/discord` channel — criar servidor Discord EGOS para demo público do Guard Brasil. Bot responde a perguntas LGPD/PII.
- [ ] OC-017: Configurar cron jobs no OpenClaw (`~/.openclaw/cron/jobs.json`) — daily: compilar wiki, weekly: Gem Hunter hunt, monthly: PII pattern review.

**P3 — Longo prazo (3 meses): GTM + Produto**

- [ ] OC-018: guard-brasil-mcp no ClawHub marketplace (GTM play: 13K+ skills distribution)
- [ ] OC-019: egos-knowledge-mcp no ClawHub (KB EGOS via OpenClaw showcase)
- [ ] OC-020: OpenClaw A2A Gateway — conectar EGOS agents ao protocolo A2A
- [ ] OC-021: Multi-device QR — parear Android + tablet com OpenClaw gateway [BLOCKER: phone required]
- [ ] OC-022: Tutor Melkin v2 — OpenClaw como runtime, SOUL.md persona, Telegram+WhatsApp+Web
- [ ] OC-023: Guard Brasil self-serve onboarding via OpenClaw stack (R$99/mo)

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
- [ ] **SD-015 (P2)**: Prioritize additional pattern packs after alpha validation [DEP: SD-012, SD-014]
- [ ] **SD-016 (P2)**: Define auth/history strategy for when persistence becomes necessary [DEP: SD-003, SD-014]
- [ ] **SD-017 (P2)**: Define API documentation surface and consumer contract [DEP: SD-004, SD-014]
- [ ] **SD-018 (P2)**: Evaluate TypeScript migration boundaries vs leaving Python core isolated [DEP: SD-002, SD-017]
- [ ] **SD-019 (P2)**: Freeze post-alpha backlog after evidence from deploy/security/ux/launch gates [DEP: SD-015, SD-016, SD-017, SD-018]

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
- [ ] **GRF-002 (P2)**: Embutir graph.html (vis.js) no HQ como painel "Knowledge Graph" — feed de codebase-memory-mcp export. Parte de HQ-009.
- [ ] **GRF-003 (P2)**: Adicionar ingestão multimodal ao wiki-compiler: PDFs + papers → Supabase `egos_wiki_pages`. Usa Graphify padrão (PDF→AST→nodes).

**A-Evolve patterns (bookmark pós PMF):**
- [ ] **AEV-001 (P3)**: Formalizar Agent Workspace manifest: cada skill em `~/.egos/.claude/commands/` ganha `manifest.yaml` (name, version, capabilities, evolution_score). Padrão A-Evolve sem o engine.
- [ ] **AEV-002 (P3)**: Implementar evolution loop simples: constitutional reviewer (já existe, P30) → detecta violações → sugere mutação de skill → git tag `skill-v{N}`. Gate: hold-out test antes de aceitar.

 ### Governance Mesh Cleanup (2026-04-06 audit)
 - [ ] **GOV-001**: Collapse `~/.claude/CLAUDE.md` into a thin adapter to kernel `.guarani` [SOURCE: local Claude audit | IMPACT: parallel constitution / rule drift]
 - [ ] **GOV-002**: Unify workflow catalog across `egos/.windsurf/workflows`, `~/.egos/workflows`, and `scripts/workflow-sync-check.sh` [SOURCE: workflow audit | IMPACT: missing/stale workflow inheritance]
 - [ ] **GOV-003**: Define canonical skill distribution between `~/.egos/skills` and `~/.claude/skills` [SOURCE: local skill audit | IMPACT: duplicated discovery rules]
 - [ ] **GOV-004**: Update `~/.claude/config/manifest.json` SSOT hierarchy to kernel-first `.guarani` and remove adapter surfaces from constitutional status [SOURCE: local Claude audit | IMPACT: wrong authority model]
 - [ ] **GOV-005**: Review `~/.claude/settings.local.json` allowlist for hardcoded tokens and unsafe legacy permissions [SOURCE: local Claude audit | IMPACT: security and governance exposure]
 - [ ] **GOV-006**: Sanitize or archive stale shared-home artifacts (`.egos/.windsurfrules`, `SSOT_STATUS_20260328.txt`, repo-specific mirror leftovers) [SOURCE: ~/.egos audit | IMPACT: legacy noise and false authority]
 - [ ] **GOV-007**: Unify repo mesh registry across `.egos/sync.sh`, `scripts/sync-all-leaf-repos.sh`, `scripts/workflow-sync-check.sh`, and `.egos/manifest.json` [SOURCE: sync audit | IMPACT: drifted propagation targets]

 ---
