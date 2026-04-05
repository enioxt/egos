# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.34.0 | **Updated:** 2026-04-05 | **LAST SESSION:** 2026-04-05 P22 — Real data tests (9/10 PII patterns verified), free quota 150→500 fixed everywhere, landing page updated, partnership strategy created (docs/strategy/PARTNERSHIP_STRATEGY.md)

---

### Completed Archive (compressed — see git log for details)
**P1-P22 (2026-03-27..2026-04-05):** EGOS-151..176, MONETIZE-001..015, START-001..005, KB-001..012, KB-016, MASTER-002/004, EAGLE-000..023, EAGLE-GH-001/002/005, GOV-001..003, BRACC-001..003, GH-001..060, GH-062/064/066, X-001..005, THEATER-001, WA-001..003 — all DONE ✅.
**Products live:** Guard Brasil v0.2.2 API (VPS), npm@0.2.2, web landing (Vercel), about/faq/terms/privacy pages, EGOS Gateway v0.1.0 (port 3050), Eagle Eye (eagleeye.egos.ia.br), Knowledge System (50 wiki pages, 3 Supabase tables).
**Infra:** Stripe metered billing, NOWPayments crypto, 27 credentials vault, WhatsApp daily cron, 196 groups indexed, 9/10 PII patterns verified with real br-acc data, free quota 500 everywhere.

---

### Guard Brasil Monetization Roadmap

**Completed:** EGOS-151..161, MONETIZE-001..015, EGOS-162/164 — all DONE ✅ (see archive)

**P1 — Remaining:**
- [ ] EGOS-163: Pix billing integration

**P2 — Growth:**
- [ ] EGOS-165: White-label outreach
- [ ] EGOS-166: REST API gateway mode

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
- [ ] KB-015: Full-text search with pg_trgm or pgvector embeddings
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
- [ ] GH-061: Dashboard gemhunter.egos.ia.br (Next.js web UI)
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

**New tasks from Aider study:**
- [x] GH-031: `.claude/hooks/pre-edit-safety` — PreToolUse hook warns on dirty working tree ✅ 2026-04-01
- [ ] GH-032: EGOS edit benchmark — 20 real edit tasks tracked over time (SWE-Bench inspired)
- [x] GH-033: CLAUDE.md §13 — model selection guide (Haiku/Sonnet/Opus per task type) ✅ 2026-04-01
- [x] GH-034: **P0-URGENT** OpenHarness task added, gem-hunter early-warning track wired ✅ 2026-04-01 (`HKUDS/OpenHarness`) — pure-Python minimal harness (44× smaller than Claude Code, skills/hooks/coordinator compatível), lançado 2026-04-01 por Chao Huang (@huang_chao4969, autor LightRAG). Avaliar: adapter em `packages/shared/harness/`, migração de skills, coordinator como sub-agent layer.

- [x] GH-035: Telegram gem alerts ✅ Already implemented as GH-055 (sendGemTelegramAlert in gem-hunter.ts). Env vars now on VPS.
- [ ] GH-036: OpenHarness adapter in packages/shared/harness/ — evaluate skill/coordinator compat
- [x] GH-037: **BRAID Mode** — upgrade `/coordinator` skill to emit Mermaid GRD before Implementation phase ✅ 2026-04-01. GRD = Guided Reasoning Diagram (nodes+edges+terminal states). Phase 2 now emits Mermaid graph TD with frozen-zone guard, parallel reads, sequential edits, verification gates. Cheap models execute strictly per graph. arXiv 2512.15959 (OpenServ BRAID), 74–122× cheaper. Frozen zones pattern aligned.
- [x] GH-038: Gem Hunter keyword update — BRAID/SERV/bounded-reasoning/OpenServ search tracks added to x-reply-bot.ts ✅ 2026-04-01
- [x] GH-039: **X.com Reply Bot** — `scripts/x-reply-bot.ts` deployed to VPS cron `0 * * * *`, 8 topic monitors, OAuth 1.0a ✅ 2026-04-01

**Gem Hunter v5.1 — Research-Backed Discovery (2026-04-02):**
- [x] GH-043: Papers With Code search source — searchPapersWithCode() queries PWC API for research implementations ✅ 2026-04-02
- [x] GH-044: Low-star/high-value scoring — arXiv citation (+18), empirical benchmarks (+12), research structure (+10), low-star+research bonus (+15) in scoreGem() ✅ 2026-04-02
- [x] GH-045: "agent-scaling" + "research-gems" search categories — scaling laws, error amplification, coordination architectures, clean-room implementations ✅ 2026-04-02
- [x] GH-046: EGOS ↔ agent-scaling-laws (`jimmyjdejesus-cmyk/agent-scaling-laws`) — /study: ArchitectureSelector (87% accuracy), 5 coordination architectures, error amplification metrics (17.2× → 4.4×), arXiv 2512.08296 ✅ 2026-04-02
- [x] GH-047: ArchitectureSelector adapter — transplant to packages/shared/intelligence/architecture-selector.ts. Wire to BRAID GRD: decide centralized/decentralized/hybrid before spawning agents ✅ 2026-04-02
- [x] GH-048: Gem Hunter structural validation (Camada 1) — check tree for README+arXiv, benchmarks/, tests/, ArchitectureSelector-like patterns. Score boost for repos with empirical test suites ✅ 2026-04-02
- [x] GH-049: Auto-integration queue (Camada 3) — queueForAutoIntegration(): score≥85 + structureBonus≥5 → docs/gem-hunter/auto-queue.json (branchSuggestion, status: queued/reviewed/adopted/rejected) ✅ 2026-04-02
- [x] GH-050: Gem Hunter → world-model signal ingestion — gem-signals.ts (appendGemSignal/getGemSignals), signals.json (max 50, LIFO), world-model.ts parseSignals() reads signals.json, score > 90 = CRITICAL ✅ 2026-04-02

**Gem Hunter v6.0 — Papers Without Code + Standalone Product (2026-04-02):**
**Master Plan:** `docs/gem-hunter/GEM_HUNTER_v6_MASTER_PLAN.md`
**Budget:** ~$15/month (free tiers + Gemini Flash)
**Decisions:** B (scaffold output), B (full auto trends), D (API→Bot→Dashboard→NPM), % pricing

*Week 1 — Foundation:*
- [x] GH-051: Papers Without Code pipeline — searchPapersWithoutCode() queries arXiv CS papers, cross-refs PWC for 0 implementations, +20 scoring bonus, 5 new queries, wired into dispatch ✅ 2026-04-02
- [x] GH-052: KOL discovery ✅ 2026-04-02. scripts/kol-discovery.ts implemented. X API integration working.
- [x] GH-053: Evolution Engine auto-integrate — loads next-queries.json, injects suggestedQueries as category=evolution-auto each run ✅ 2026-04-02
- [x] GH-054: Multi-LLM fallback chain — MODEL_CHAIN already in llm-provider.ts; gem-hunter uses chatWithLLM() via callAI() ✅ 2026-04-02
- [x] GH-055: Telegram alerts — sendGemTelegramAlert() fired for top 5 gems ≥80; appendGemSignal() wired; uses TELEGRAM_ADMIN_CHAT_ID ✅ 2026-04-02
- [x] CLEAN-001: egos-lab/gem-hunter.ts deprecated (header added, v5.0 stale); docs/gem-hunter/ clean; no timestamped reports ✅ 2026-04-02

*Week 2 — Intelligence Layer:*
- [x] GH-056: Multi-stage paper pipeline — LLM abstract triage (0-100) + scaffold gen (.ts + .md) in docs/gem-hunter/scaffolds/ ✅ 2026-04-02
- [x] GH-057: Context awareness — loadContextSignals() from git log + TASKS.md → injects category=context-auto queries ✅ 2026-04-02
- [x] GH-059: Cost budgeting — packages/shared/src/cost-tracker.ts (COST_TABLE, estimateCost, checkBudget, createCostSession) ✅ 2026-04-02
- [x] GH-060: Structural validation — validateGemStructure() checks README/tests/benchmarks/docs via GitHub API; structureBonus (0-25) ✅ 2026-04-02
- [x] GH-052: KOL discovery — scripts/kol-discovery.ts; fetches @anoineim following via X API, classifies bio (crypto/ai-ml/gov/markets), outputs kol-list.json ✅ 2026-04-02

*Week 3-4 — Monetization:*
- [x] GH-058: Standalone API — agents/api/gem-hunter-server.ts (port 3097): /v1/hunt, /v1/findings, /v1/papers, /v1/signals, /v1/kols, /v1/jobs/:id ✅ 2026-04-02
- [x] BIZ-001: docs/business/MONETIZATION_SSOT.md — 3 products, ICP, revenue targets, payment infra, 4 open decisions ✅ 2026-04-02
- [x] GH-065: packages/shared/src/billing/pricing.ts — priceGemHuntRun, priceGuardBrasilCalls, checkCustomerBudget, buildStripeCheckoutUrl ✅ 2026-04-02

*Month 2-3 — Product Scale:*
- [ ] GH-061: Dashboard web — gemhunter.egos.ia.br (findings feed, paper browser, trends, alerts config)
- [x] GH-062: packages/gem-hunter/ — @egosbr/gem-hunter v6.0.0 (GemHunter client + CLI: hunt/findings/papers/signals/wait) ✅ 2026-04-02
- [ ] GH-063: x402 pay-per-call — M2M agent payments via x402 protocol
- [x] GH-064: Discord webhook alerts — sendGemDiscordAlert() rich embeds (score≥80, color-coded); DISCORD_WEBHOOK_URL env ✅ 2026-04-02
- [x] GH-066*: Gateway /gem-hunter channel — sector filter, topics, product pricing, trending ✅ 2026-04-04 (NOTE: renamed from Paper→Code)
- [ ] GH-067: Deploy gem-hunter-server to VPS (gemhunter.egos.ia.br) + Caddy routing → P0 revenue
- [x] GH-068: Auth — API keys via Supabase `gem_hunter_api_keys` table + Bearer token validation ✅ 2026-04-05
- [x] GH-069: Rate limiting middleware (tier-aware: free/starter/pro/pay-per-use) ✅ 2026-04-05
- [ ] GH-070: Chatbot orchestrator — WhatsApp channel NLP intent → tool calls → gem-hunter → curated reply
- [ ] GH-071: Telegram bot (/hunt, /trending, /sector slash commands)
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

### Claude Code Hardening ✅ (2026-04-01)
LEAK-001..009 done (hooks, settings.json, /coordinator, CLAUDE.md v2.1). Pending: LEAK-010/011/012 (monitor pattern repos).

### AI Coverage & Observability ✅ (2026-04-01)
AI-001..007 done (coverage map, scanner, keys synced, gem-hunter migrated). Pending: AI-008/009/010 (pre-commit hook, OTel wiring, cost dashboard).
OBS-001..004 done (atrian-observability skeleton, telemetry policy, 12 spans, 10 metrics). Pending: OBS-010..013 (wiring, privacy logs).

---

### Reference Repos — Awareness Registry (2026-04-01)

**Repos identified for study (from ChatGPT analysis + Gem Hunter + leak threads):**

| ID | Repo | Category | Priority |
|----|------|----------|----------|
| continuedev/continue | coding_surface, governance | P1 |
| Aider-AI/aider | coding_surface, agent_runtime | P1 |
| cline/cline | coding_surface, agent_runtime | P1 |
| OpenHands/OpenHands | agent_runtime, product_surface | P1 |
| langchain-ai/langgraph | agent_runtime, durable_workflow | P1 |
| openai/openai-agents-python | agent_runtime, governance_safety | P1 |
| BerriAI/litellm | model_gateway | P1 |
| langfuse/langfuse | observability_evals | P1 |
| pydantic/pydantic-ai | agent_runtime | P2 |
| mem0ai/mem0 | memory_context | P2 |
| Arize-ai/phoenix | observability_evals | P2 |
| vercel/ai | product_surface | P2 |
| temporalio/sdk-typescript | durable_workflow | P2 |
| deepset-ai/haystack | retrieval_context | P2 |
| stanfordnlp/dspy | agent_runtime | P2 |
| modelcontextprotocol/servers | protocol_tooling | P2 |
| hesreallyhim/awesome-claude-code | protocol_tooling | Ref |
| disler/claude-code-hooks-multi-agent-observability | observability_evals | Ref |
| rohitg00/awesome-claude-code-toolkit | protocol_tooling | Ref |
| nblintao/awesome-claude-code-postleak-insights | protocol_tooling | Ref |
| jimmyjdejesus-cmyk/agent-scaling-laws | agent_scaling, intelligence_layer | P1 |
| HKUDS/OpenHarness | agent_runtime, harness | P1 |

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
- [ ] X-006: Grow capability profiles in rapid-response.ts (add br-acc, 852, BRAID executor)
- [ ] X-007: `--post-thread` flag in rapid-response.ts — auto-post first tweet of thread
- [ ] X-008: Daily X report to Telegram (how many replies sent, top threads engaged)
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
- [ ] INTEL-005: Signal ingestion — Gem Hunter scores > 80 → auto-append to world model signals (= GH-050)
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
- [ ] WM-009: Integrar Qwen3Guard para safety classification (Safe/Controversial/Unsafe)
- [ ] WM-010: Constitutional rules embedding (frozen zones, PRIME DIRECTIVE)
- [ ] WM-011: Value alignment local (ATRiAN principles: Accuracy, Truth, Reversibility, Impact, Accountability, Neutrality)
- [ ] WM-012: Intervention system com human-in-the-loop

**P3 — AGI Capabilities (Long-term):**
- [ ] WM-013: Auto-observação (world model que monitora a si mesmo)
- [ ] WM-014: Auto-modificação (melhorar próprio código)
- [ ] WM-015: Planejamento longo horizonte (quarter/year goals)
- [ ] WM-016: Criação automática de agents quando necessário

**SSOT:** `docs/strategy/WORLD_MODEL_SSOT.md` — conceito completo, roadmap, hardware 16-24GB VRAM

---

### Eagle Eye v2 — Decision Intelligence Engine (GenHunter Spec 2026-04-02)

**Source:** ChatGPT GenHunter Sistema Decisório spec — 7-layer pipeline, 5-axis scoring, 26 API endpoints
**Insight:** Eagle Eye evolves from territory-scanner to full licitações DECISION INTELLIGENCE system.
Modern monetization: usage-based API + MCP tool + chatbot. Stripe-unified (card + Pix).

**Architecture (microservices):**
- `collector-service` → `document-parser` → `classification-service` → `extraction-service`
- `scoring-service` → `insight-generator` → `dashboard-api` → `notification-service` → `feedback-learning`

**5-Axis Scoring:** aderência técnica / viabilidade econômica / capacidade técnica / risco operacional / compliance jurídica

**Done:**
- [x] EAGLE-020: Read and analyzed GenHunter spec (7-layer pipeline, 5-axis scoring, 26 endpoints) ✅ 2026-04-02
- [x] BIZ-001: MONETIZATION_SSOT.md updated with Eagle Eye usage-based pricing (R$49/149/499) ✅ 2026-04-02

**P0 — Core Pipeline:**
- [x] EAGLE-GH-001: `scoring-service.ts` — 5-axis scorer live in egos-lab/apps/eagle-eye/src/modules/licitacoes/ (10 sector presets, BID/INVESTIGATE/SKIP thresholds, CLI demo) ✅ 2026-04-02
- [x] EAGLE-GH-002: `document-parser.ts` — regex+LLM hybrid, extracts objeto/valor/prazo/modalidade/segmento/porte/habilitação, 78% confidence (no LLM) ✅ 2026-04-03
- [ ] EAGLE-GH-003: `classification-service.ts` — auto-classify licitação by category + assign sector preset
- [ ] EAGLE-GH-004: `extraction-service.ts` — pull deadline, CNAE, required docs, financial requirements from raw text

**P1 — Intelligence Layer:**
- [x] EAGLE-GH-005: `insight-generator.ts` — LLM + rule-based fallback, BID/INVESTIGATE/SKIP + action items + risks + revenue estimate ✅ 2026-04-03
- [ ] EAGLE-GH-006: `profile-service.ts` — company capability profile (past wins, CNAE, financial capacity) → fed into scoring
- [ ] EAGLE-GH-007: `feedback-learning.ts` — track bid outcomes (won/lost/skipped) → adjust scoring weights per sector

**P1 — API & MCP:**
- [ ] EAGLE-GH-008: REST API v2 — POST /v2/analyze (score single licitação), GET /v2/opportunities (filtered feed), GET /v2/insights/:id
- [ ] EAGLE-GH-009: MCP server `eagle-eye-mcp` — tools: `analyze_licitacao`, `search_opportunities`, `get_profile` → usable from Claude Code
- [ ] EAGLE-GH-010: Stripe Pix integration — enable `pix` payment method in Stripe Checkout for all Eagle Eye plans
**P2 — Dashboard & Notifications:**
- [ ] EAGLE-GH-011: Dashboard v2 redesign — opportunity feed with 5-axis radar chart, bid pipeline Kanban
- [ ] EAGLE-GH-012: Telegram alert routing — score ≥75 → `egosmarkets_bot`; score ≥90 AND deadline ≤7d → admin bot
- [ ] EAGLE-GH-013: Chatbot interface — natural language query: "find software opportunities in SP above R$500k"
**P2 — Proposal Tools (R$250k opportunity):**
- [ ] EAGLE-021: Proposal generator — auto-draft proposta técnica from edital + company profile
- [ ] EAGLE-022: Compliance checklist — auto-check habilitação requirements against company docs
- [ ] EAGLE-023: Submit EAGLE-020 proposal by 2026-04-29 (R$250k opportunity deadline)
### P20 Session Tasks (2026-04-04)

**Done:**
- [x] MONETIZE-006: Stripe meter events wired into /v1/inspect ✅ 2026-04-04
- [x] MONETIZE-007: Credentials vault SSOT (vault.ts + Supabase credentials_vault, 14 indexed) ✅ 2026-04-04
- [x] MONETIZE-008: Supabase tables: decisions_log, credentials_vault, claude_sessions ✅ 2026-04-04
- [x] GOV-P20-001: CLAUDE.md v2.4.0 (autonomy, challenge, investigation, vocabulary, chatbot everywhere) ✅ 2026-04-04
- [x] GOV-P20-002: Focus enforcement whitelist expanded (packages/shared, CLAUDE.md, .claude/, gem-hunter, docs/) ✅ 2026-04-04
- [x] GOV-P20-003: Git tag v2.3.0-snapshot-2026-04-04 ✅ 2026-04-04
- [x] WA-001: WhatsApp report sent via Evolution API (pipeline verified working) ✅ 2026-04-04
- [x] WA-002: Daily report cron installed on VPS (8am BRT → WhatsApp) ✅ 2026-04-04
- [x] WA-003: 196 WhatsApp groups indexed via Evolution API ✅ 2026-04-04
- [x] MASTER-001: Master API PRD created (3 architecture options: Gateway, Event-Driven, Consciousness Loop) ✅ 2026-04-04

**P0 — Revenue (Guard Brasil focus):**
- [x] MONETIZE-009: Fix Stripe tiered pricing ✅ 2026-04-04. Archived 3 broken prices, created 3 new with unit_amount_decimal (0.7/0.4/0.2 centavos). IDs: startup=price_1TISgBHdOnphplrgLp2RngAm, business=price_1TISgBHdOnphplrgXCCJPWx5, enterprise=price_1TISgBHdOnphplrghe81rAql. VPS .env updated, API restarted healthy v0.2.2.
- [x] MONETIZE-010: Frontend checkout button on guard-brasil-web ✅ 2026-04-05 (Stripe + NOWPayments buttons wired via /api/test proxy)
- [ ] MONETIZE-011: Deploy v0.2.3 to VPS with STRIPE_METER_ID env var
- [ ] MONETIZE-012: NOWPayments webhook URL config in dashboard (guard.egos.ia.br/v1/crypto/webhook + 3×5min recurring notifications) — ENIO
- [ ] MONETIZE-013: Pix billing integration (EGOS-163)

**P0 — Master API (Enables everything):**
- [x] MASTER-002: Build EGOS Gateway API (Hono server, port 3000, WhatsApp + Knowledge channels) ✅ 2026-04-05
- [x] MASTER-004: Deploy gateway to VPS Docker ✅ 2026-04-05 (port 3050, docker network infra_bracc, healthy)
- [x] MASTER-003: Evolution API webhook → gateway routing — WhatsApp v2 full orchestrator + Telegram bot live ✅ 2026-04-05
- [ ] MASTER-005: NLP intent classifier (Haiku, ~$1/day) for natural language commands

**P1 — Dashboard & Monitoring:**
- [ ] DASH-001: Evaluate ClawBridge / mission-control for EGOS mobile dashboard
- [ ] DASH-002: Build mobile-first dashboard (agent status, costs, WhatsApp groups, alerts)

**P1 — Gem Hunter Enhancement:**
- [ ] GH-070: Add crypto/X.com KOL monitoring sources (xscan-app pattern, crypto-twitter-alpha-stream)
- [ ] GH-071: Daily X.com scan via Gem Hunter (auto-trigger, not manual)

### Previous P19 Tasks (Still Active)
**P0 — Theater:**
- [x] THEATER-001: x-reply-bot verified running on VPS cron ✅ 2026-04-04
- [ ] CTX-001: Context recovery hook to /start
**P1 — Architecture:**
- [ ] HERMES-001: Wire Hermes-3 as BRAID mechanical executor
- [ ] OPENCLAW-001: Register Guard Brasil as OpenClaw MCP skill
**P1 — Infrastructure:**
- [ ] CTX-002: Auto-index codebase-memory-mcp on /start
- [ ] REWARDS-001: Unified rewards engine
- [ ] MOAT-001: Data flywheels — partially addressed by KB (egos_learnings table)

### Partnership & Distribution Strategy (2026-04-05)

**Goal:** Find technical + business partners to accelerate Guard Brasil to enterprise scale.
**SSOT:** `docs/strategy/PARTNERSHIP_STRATEGY.md`

**P0 — Immediate (this week):**
- [ ] PART-001: Publish Guard Brasil on npm + ProductHunt (M-007 emails first)
- [ ] PART-002: Post X.com + LinkedIn with og-image.jpg announcing Guard Brasil
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
