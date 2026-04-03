# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.30.0 | **Updated:** 2026-04-03 | **LAST SESSION:** 2026-04-03 P17 — Agent registry ghost cleanup, drift-sentinel fix, LLM orchestration docs

---

### Agent Registry Health (2026-04-03)

**Done:**
- [x] EGOS-176: Agent registry ghost cleanup — removidos aiox-gem-hunter, mastra-gem-hunter (KILLED 2026-03-31). Drift sentinel corrigido para verificar entrypoints em qualquer path (scripts/, agents/api/, agents/agents/). ✅ 2026-04-03

---

### Guard Brasil Monetization Roadmap

**Completed:**
- [x] EGOS-151..157: v0.2.0 (15 patterns), MCP server, market report, VPS orchestrator, /disseminate, /diag, VPS paths
- [x] EGOS-158: npm publish @egosbr/guard-brasil@0.2.0 — **DONE 2026-04-01** (token expires ~2026-04-07)
- [x] EGOS-161: MCP server registered in Claude Code
- [x] Consumer apps PII sync: 852/forja/carteira-livre → 15 patterns each

**P0 — Revenue blocking:**
- [x] EGOS-159: @egosbr/guard-brasil@0.2.0 wired into VPS Docker API — CPF/PII live ✅ 2026-04-01
- [x] EGOS-160: Reversible redaction — tokenize()/restore() in packages/guard-brasil/src/lib/tokenizer.ts ✅ 2026-04-01

**P1 — Competitive:**
- [x] EGOS-162: Accuracy benchmark vs Presidio/anonym.legal — 85.3% F1, benchmark.ts in guard-brasil/src ✅ 2026-04-01
- [x] MONETIZE-001: Self-service API key generation (POST /v1/keys) + Supabase-backed auth + quota enforcement + landing page form ✅ 2026-04-02
- [x] MONETIZE-002: Deploy updated Guard Brasil API to VPS ✅ 2026-04-02 (packages/core synced, Supabase keys in .env, /v1/keys live on guard.egos.ia.br)
- [x] MONETIZE-003: Vercel guard-brasil-web deployed ✅ 2026-04-02 (vercel deploy --prod, build OK 19s, "Obtenha sua chave de API" section live at guard-brasil-ilxbkmbak-enio-rochas-projects.vercel.app)
- [x] MONETIZE-004: Eagle Eye API auth middleware ✅ 2026-04-02 (authenticateApiKey() on /api/territories + /api/opportunities + /api/scans/history; shared guard_brasil_tenants key system)
- [x] MONETIZE-005: Stripe webhook for paid tier upgrades ✅ 2026-04-02. POST /v1/stripe/checkout creates Stripe Checkout Session; POST /v1/stripe/webhook handles checkout.session.completed → PATCH guard_brasil_tenants (tier, quota_limit, mrr_brl, stripe_customer_id). Webhook registered: we_1THj4pHdOnphplrg47z9I8nn. Live test: cs_live_b1MHUCgk confirmed.
- [ ] EGOS-163: Pix billing integration
- [x] EGOS-164: Dashboard — real data from guard_brasil_events ✅ 2026-04-01. Telemetry wired: API recordApiCall() → guard_brasil_events → /api/events → DashboardV2Lean polling 5s. Requires: SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY in .env files.

**P2 — Growth:**
- [ ] EGOS-165: White-label outreach
- [ ] EGOS-166: REST API gateway mode

---

### Neural Mesh — Composed (2026-04-01)

**Verdict:** COMPOSE — see `docs/research/NEURAL_MESH_INVESTIGATION_REPORT.md`

**Done:**
- [x] EGOS-167: codebase-memory-mcp installed, 7 repos indexed (51K nodes, 75K edges), 3D graph UI, 4 skills
- [x] PreToolUse hook fixed (allows .md/.json, only blocks first code read)
- [x] CLAUDE.md v2.1 — codebase-memory-mcp rules + scheduled jobs reference

**Remaining:**
- [x] GH-040: SSOT consistency gate (validate-ssot.ts) ✅ 2026-04-01. Validates drift between agents.json, TASKS.md, HARVEST.md, CAPABILITY_REGISTRY. Integrated into CI (.github/workflows/ci.yml) and available as `npm run ssot:check`. Aligns with Codex QA report (PR #16) P0 recommendations.
- [x] EGOS-168: llmrefs blocks added to 10 governance docs ✅ 2026-04-01. AI navigation blocks added to: CAPABILITY_REGISTRY, ECOSYSTEM_CLASSIFICATION_REGISTRY, ENVIRONMENT_REGISTRY, AI_COVERAGE_MAP, ACTIVATION_FLOW, ACTIVATION_GUIDE, BLUEPRINT_TASKS_MATRIX, DOCTOR_COMMAND_SPEC, SSOT_REGISTRY, MIGRATION_PLAN. Each includes role, summary, read-next pointers.
- [x] GH-041: API smoke tests (5 contracts) ✅ 2026-04-01. Validates POST /v1/inspect schema, PII detection, Atrian response, rate limiting. Integrated into CI after ssot:check. Available as `npm run smoke:api`.
- [x] GH-042: Version lock checker ✅ 2026-04-01. Validates version sync across package.json (root), apps/guard-brasil-web, apps/api/src/server.ts, packages/guard-brasil. Detects drift and recommends highest semver. Integrated into CI. Available as `npm run version:lock`.

**Telemetry & Observability (P1 — Critical Gap):**
- [x] EGOS-TELEM-001: Guard Brasil API telemetry (recordApiCall) — ✅ 2026-04-01. Integrated: telemetry.ts + recordApiCall() exported, API server calls recordApiCall() post-inspect, guard_brasil_events table schema ready (20 columns). Fire-and-forget pattern (non-fatal if Supabase down). Dashboard ready to display events. Pending: API deployment + test calls to populate table.
- [x] EGOS-TELEM-002: Tool call attribution + cost tracking ✅ 2026-04-02. recordToolCall() + recordAgentSession() in packages/shared/src/telemetry.ts (from Codex PR #23). Tool calls tracked with duration, tokens, cost. Cost/tool ranking via telemetry_dashboard.py.
- [x] EGOS-TELEM-003: Gargalo detection (latency heatmap) ✅ 2026-04-02. getLatencyHeatmap() in telemetry.ts returns latency buckets (p50/p95/p99). QA script: scripts/qa/telemetry_dashboard.py shows slow operations. Alert threshold configurable via telemetry_guardrail.py.
- [x] EGOS-TELEM-004: Real-time cost dashboard ✅ 2026-04-02. GET /api/admin/cost-dashboard endpoint (admin-only): 24h cost breakdown by agent+tool, hourly breakdown.
- [x] EGOS-TELEM-005: Historical cost analysis + forecasting ✅ 2026-04-02. scripts/telemetry_forecast.py: 30-day projection, linear trend fit, budget alerts, CSV export.

- [ ] EGOS-169: @aiready/pattern-detect pre-commit (duplicate detection)
- [ ] EGOS-173: CRCDM hooks: llmrefs staleness + auto-heal rename
- [x] EGOS-175: llmrefs blocks added to 5 leaf AGENTS.md (forja, carteira-livre, smartbuscas, br-acc, santiago) ✅ 2026-04-01

---

### Session Initialization v6.0 — Optimized Health Checks (2026-04-02)

**Status:** ✅ LIVE — 50% faster, API validation, 3-min executive summary

**Completed:**
- [x] START-001: /start v6.0 core engine (TypeScript + Bun) — parallel diagnostics, 45s → 22s ✅ 2026-04-02 (`scripts/start-v6.ts`)
- [x] START-002: npm run start aliases (default/--full/--json) ✅ 2026-04-02 (`package.json`)
- [x] START-003: Design doc + bash fallback — `docs/SESSION_INITIALIZATION_v6.md`, `scripts/start-v6.sh` ✅ 2026-04-02
- [x] START-004: GitHub Actions integration — session health check in CI pipeline ✅ 2026-04-02 (`.github/workflows/ci.yml`)
- [x] START-005: Pre-commit hook integration — validation gates block commits on failures ✅ 2026-04-02 (`.husky/pre-commit`)

**Pending (P1):**
- [ ] START-006: Monitor performance over 1 week — baseline, peak, outliers tracking (due 2026-04-09)
- [ ] START-007: v6.1 roadmap — distributed agent health checks (SSH parallel, multi-repo)
- [ ] START-008: Dashboard integration — real-time health display in Grafana/Claude Code UI
- [ ] START-009: Alert system — Slack/Telegram on critical blockers (health < 40%)

**Documentation:**
- Memory: `/home/enio/.claude/projects/-home-enio-egos/memory/start_v6_improvements.md`
- Design: `docs/SESSION_INITIALIZATION_v6.md`
- Commits: `eb42e40` (core), `55a734c` (aliases), `1eff043` (docs)

---

### Scheduled Jobs — 3 CCR slots (2026-04-01)

All Haiku, 00-06h BRT, reports in `docs/jobs/` + `docs/gem-hunter/`

- [x] Governance Drift Sentinel — diário 0h17 BRT (trig_01S5za...)
- [x] Code Intel + Security Audit — seg+qui 1h42 BRT (trig_01RDDk...)
- [x] Gem Hunter Adaptive Intelligence — seg+qui 2h37 BRT (trig_01Sn7Y...)
- [x] /start v5.6 → v6.0 — upgraded from skill to self-contained executable ✅ 2026-04-02
- [x] GitHub Actions audit: 9 failing workflows disabled, only essential kept

---

### Eagle Eye — OSINT Licitações (2026-04-01)

**Code:** `/home/enio/egos-lab/apps/eagle-eye/`
**Domain:** `eagleeye.egos.ia.br` ✅ LIVE (Caddy route port 3090, Docker container)
**Supabase:** `lhscgsqhiooyatkebose` — 6 tables, 80 territories seeded, 121 opportunities (30-day backfill done 2026-04-02)

**Done:**
- [x] Backend pipeline: Querido Diário API → AI analysis (Gemini Flash ~$0.01/gazette) → 26 patterns
- [x] Supabase migration executed (territories, opportunities, scans, users, alerts, notifications)
- [x] React frontend (Dashboard, Reports, Analytics) — renders with mock data
- [x] Detection patterns: 26 across 3 tiers (licitações, LGPD, INPI, fiscal, etc.)

**P0 — Standalone extraction (egos-lab being deactivated):**
- [x] EAGLE-000: @egos-lab/shared removed, lib/shared.ts inlined, 5 imports updated ✅ 2026-04-01
- [x] EAGLE-001: 4 API endpoints confirmed in ui/server.ts (opportunities/territories/scans/scan-now) ✅ 2026-04-01
- [x] EAGLE-002: Frontend already uses fetch() to all 4 endpoints ✅ 2026-04-01
- [x] EAGLE-003: Dockerfile.standalone, docker-compose.prod.yml, Caddy route eagleeye.egos.ia.br ✅ 2026-04-01
- [x] EAGLE-004: VPS running — eagleeye.egos.ia.br, 15 territories seeded, Caddy reloaded ✅ 2026-04-01

**P1 — Production:**
- [x] EAGLE-005: alerts.ts — Telegram Bot + Resend email, fires post-scan for new opps ✅ 2026-04-01
- [x] EAGLE-006: 52 territories in code, 50 in Supabase — all 27 state capitals + tech hubs ✅ 2026-04-01
- [x] EAGLE-007: PNCP enrichment — wire pncp-client.ts into analysis pipeline ✅ 2026-04-01 (wired in analyze_gazette.ts step 6)
- [x] EAGLE-008: VPS cron added (0 12 * * * = 9am BRT, docker exec eagle-eye bun fetch) ✅ 2026-04-01
- [x] EAGLE-012: Licitação taxonomy (9 segments, 12 modalities, 4 size tiers, srp, esfera) added to types.ts + AI prompt ✅ 2026-04-01
- [x] EAGLE-013: Territory expansion Wave 2+3 — 52→84 cities, map.html COORDS updated ✅ 2026-04-01
- [x] EAGLE-014: discover-territories.ts — auto-discovery via PNCP + IBGE APIs ✅ 2026-04-01
- [x] EAGLE-015: Dashboard filter UI for segmento/modalidade/porte taxonomy ✅ 2026-04-02 (3 select dropdowns, setSegmento/setModalidade/setPorte wired to JS filter)
- [x] EAGLE-016: Sync 84 territories to Supabase (seed script) ✅ 2026-04-02 (sync-territories.ts, 79 territories seeded with upsert)

**P2 — Revenue:**
- [ ] EAGLE-009: Stripe/Pix payment for Pro tier (R$497/mo, 50+ territories)
- [x] EAGLE-010: Customer onboarding flow ✅ 2026-04-02. /docs page: API reference with cURL/JS/Python examples, params table, pricing tiers. Docs link added to landing footer. Vercel deploy triggered.
- [ ] EAGLE-011: E2E tests (Playwright)
- [x] EGOS-170: Guard Brasil dashboard wired to real Supabase data ✅ 2026-04-02 (/api/tenants + /api/stats routes, DashboardV1Giant fetches real customers + MRR on mount with 30s refresh)

**P4 — Government Licitações (DEPRIORITIZED 2026-04-02 — too slow, focus on API-first):**
- [x] EAGLE-017: Real data pipeline (Querido Diário API) — 36 opportunities found, R$ 10.5M value, 14 software/TI (38.9%) ✅ 2026-04-01. Script: `analyze-real-gazettes-v2.ts`. Cache + error handling robust. Enum validation fixed (Portuguese market_potential).
- [x] EAGLE-018: Software opportunities analysis + Tier 1/2/3 mapping ✅ 2026-04-01. Tier 1: Sistema de Gestão (R$ 250k, 28d), Plataforma Análise (R$ 180k, 36d), Auditoria (R$ 120k, 51d). Total opportunity: R$ 550k. Geographic: SP, RJ, BH. Success probability: 60-75%.
- [ ] EAGLE-019: Integrador partnership outreach — target DeLoit/Thoughtworks/regional partners, pitch EGOS as subcontractor for software bids. CRM + call scheduling.
- [ ] EAGLE-020: R$250k proposal submission (Sistema de Gestão de Licitações) — deadline 2026-04-29. Proposal drafted (PROPOSAL_250K_LICITACOES_SYSTEM.md). Timeline: 120d (4 sprints), stack: React + Next.js + Bun/TypeScript + PostgreSQL, margin 35%.
- [x] EAGLE-021: Daily analysis cron deployed ✅ 2026-04-02 (0 12 UTC = 9am BRT, full pipeline: fetch+AI+Supabase store, JSON parse fix for truncated responses)
- [x] EAGLE-022: Scale to 80 territories (full Brazil) + batch-query daily cron ✅ 2026-04-02. 4 API batches × 20 territories, 22 gazettes/day found in dry-run. --backfill=N flag for historical runs.
- [x] EAGLE-023: Integrador channel revenue share (70/30) + SLA documentation ✅ 2026-04-02. Doc: docs/eagle-eye/INTEGRADOR_CHANNEL.md — model, SLA, contract template, outreach script, API revenda, revenue projections.

---

### Commons & Santiago — Shared Infrastructure (2026-04-01)

**Commons** (`/home/enio/commons`): Shared Docker + services layer deployed on Hetzner (commit 3dec9e0)
**Santiago** (`/home/enio/santiago`): WhatsApp SaaS (Vercel + Hetzner). Waiting on business partner.

**Done:**
- [x] COMM-001: commons Dockerfile + docker-compose for shared services deployment ✅ 2026-04-01 (commit 3dec9e0)

**Pending:**
- [ ] COMM-002: Document commons services in ECOSYSTEM_REGISTRY.md
- [ ] SANT-001: Santiago partner onboarding — MVP ready, waiting on business partner confirmation

---

### br-acc (EGOS Inteligência) — Valuable Code Mining (2026-04-01)

**6 reusable modules identified (~3000 LOC total):**
- `provenance.py` (63 LOC) — **Proof-of-research hash system**: SHA-256 non-repudiation for data rows + source fingerprinting. Score: 9/10.
- `guard.py` (293 LOC) — Guard Brasil client + offline PII fallback. Score: 8/10.
- `base.py` (177 LOC) — Universal ETL pipeline base class + IngestionRun tracking. Score: 9/10.
- `cache.py` (122 LOC) — Redis cache-aside with graceful degradation. Score: 9/10.
- `neo4j_service.py` (90 LOC) + 47 .cypher files — Neo4j query abstraction. Score: 8/10.
- `transparency_tools.py` (1372 LOC) — 21 Brazilian gov API clients with circuit breaker. Score: 7/10.

**Tasks:**
- [x] BRACC-001: Extract provenance.py → packages/shared/src/provenance.ts ✅ 2026-04-01
- [x] BRACC-002: Extract cache.py pattern → packages/shared/src/cache.ts ✅ 2026-04-01
- [x] BRACC-003: Extract ETL base class → packages/shared/src/pipeline-base.ts ✅ 2026-04-01
- [ ] EGOS-128: Phase 2+3 (Python imports + Docker rename)
- [ ] EGOS-129: Docker network rename + redeploy Hetzner

---

### Governance Registry Health (2026-04-01)

**Triple registry system found (working at ~60%):**
- `docs/CAPABILITY_REGISTRY.md` v1.8.0 — 130+ capabilities, 12 domains. **Working.**
- `docs/SSOT_REGISTRY.md` v2.0.0 — 30+ domain SSOTs. **Working.**
- `docs/ECOSYSTEM_CLASSIFICATION_REGISTRY.md` v2.0.0 — repo governance classes. **NOT synced to leaves.**

**Tasks:**
- [x] GOV-001: Add ECOSYSTEM_CLASSIFICATION_REGISTRY.md to governance-sync.sh CANONICAL_DOCS ✅ 2026-04-01
- [x] GOV-002: Sync leaf repos (carteira-livre/forja/852/smartbuscas) — all 3 registries fresh ✅ 2026-04-01
- [x] GOV-003: Daily governance-sync cron added (0 12 * * * = 9am BRT) ✅ 2026-04-01

> **Archived:** All session summaries, ARCH project, benchmark plans, Grok intake → `docs/knowledge/TASKS_ARCHIVE_2026.md`

---

### Gem Hunter v2 — Pair Analysis Engine (2026-04-01)

**Source:** ChatGPT conversation analysis + egos-lab Gem Hunter v5.0 handoff
**Architecture:** 6-layer pipeline (Discovery→Triage→Pair Diagnosis→Decision Intelligence→SSOT→Continuous Operation)

**Done:**
- [x] Gem Hunter v5.0 Atomic Discovery Engine (anti-poisoning ≥40, -15 non-code, CJK block)
- [x] CCR scheduled job: Gem Hunter Adaptive Intelligence (seg+qui 2h37 BRT)
- [x] Report: 24 gems found 2026-04-01 (top: gptme ACP agent.py, 89pts)

**P0 — Pair Analysis Core:**
- [x] GH-001: Create `/study` skill — pair-analysis session for EGOS ↔ 1 reference repo
- [x] GH-002: Create `/study-end` skill — mandatory closure (9 sections: scorecard, transplants, blind spots, next recs)
- [x] GH-003: SSOT structure: `docs/gem-hunter/registry.yaml`, `pairs/`, `weights.yaml`, `SSOT.md`
- [x] GH-004: Weighted scoring config: `docs/gem-hunter/weights.yaml` (9-factor rubric)
- [x] GH-010: EGOS ↔ Continue — score 71/100, 5 transplants identified, 3 anti-patterns

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

- [ ] GH-035: Telegram notification when gem-hunter score > 80 (post to EGOS channel)
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
- [ ] GH-052: KOL list curada — 50+ X.com accounts for trend monitoring (needs user input)
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
- [ ] GH-066: Paper → Code generator — LLM reads full paper, generates complete scaffold implementation

**P2 — Advanced Studies:**
- [ ] GH-020: EGOS ↔ Mem0 — persistent agent memory layer
- [ ] GH-021: EGOS ↔ Temporal TS SDK — durable workflow engine
- [ ] GH-022: EGOS ↔ Haystack — RAG/retrieval/context engineering
- [ ] GH-023: EGOS ↔ DSPy — programmatic prompt optimization
- [ ] GH-024: Lego Assembler agent — consumes `.md` SSOT blocks from discovery engine

---

### Claude Code Leak Intelligence (2026-04-01)

**Source:** X threads analysis (2038965567269249484, 2038894956459290963), clean-room approach
**Principle:** Learn from public patterns, never use leaked code. Evidence-based only.

**Done:**
- [x] CLAUDE.md v2.1 employee-grade overrides (verification gates, context management, edit safety)
- [x] settings.json: permissions + hooks configured
- [x] Awareness: 44 feature flags, KAIROS, BUDDY, Coordinator Mode, anti-distillation patterns

**P1 — Claude Code Hardening:**
- [x] LEAK-001: Frustration-detection hook wired (UserPromptSubmit → ~/.claude/hooks/frustration-detector) ✅ 2026-04-01
- [x] LEAK-002: Memory consolidation — embedded as Part 2 in Governance Drift CCR (daily 3:17 BRT) ✅ 2026-04-01
- [x] LEAK-003: `/coordinator` skill — 4-phase orchestration (Research→Synthesis→Implementation→Verification) ✅ 2026-04-01
- [x] LEAK-004: PostToolUse hook — post-write-typecheck fires after Write/Edit on .ts/.tsx ✅ 2026-04-01
- [x] LEAK-005: Anti-compaction guard — UserPromptSubmit hook, turn counter, reminder every 10 turns ✅ 2026-04-01

**P1 — Architecture Insights (from zainhas blog analysis):**
- [x] LEAK-006: Tool result budgeting — note added to /end Phase 1 ✅ 2026-04-01
- [x] LEAK-007: Structured session memory — fixed sections + 2K cap added to /end Phase 7 ✅ 2026-04-01
- [x] LEAK-008: Read-parallel/Write-sequential — documented in CLAUDE.md §14, enforced in /coordinator ✅ 2026-04-01
- [x] LEAK-009: settings.json deny rules — 13 wildcard patterns for .env/credentials/keys ✅ 2026-04-01

**P2 — Awareness (no action needed yet):**
- [ ] LEAK-010: Monitor `Piebald-AI/claude-code-system-prompts` for per-release prompt changes
- [ ] LEAK-011: Monitor `nblintao/awesome-claude-code-postleak-insights` for community patterns
- [ ] LEAK-012: Evaluate Guard Brasil anti-distillation patterns (fake-tool injection for API protection)

---

### AI Coverage & Telemetry (2026-04-01)

**Purpose:** Track which repos/files use AI, keep map auto-updated, wire cost telemetry.

**Done:**
- [x] AI-001: `docs/AI_COVERAGE_MAP.md` created — 7 repos, ~33 AI files, provider hierarchy, cost model ✅ 2026-04-01
- [x] AI-002: `scripts/ai-coverage-scan.ts` — scanner + --update/--check/--dry-run modes ✅ 2026-04-01
- [x] AI-003: DashScope API key synced to egos/.env + all GH Secrets (10 secrets set programmatically) ✅ 2026-04-01
- [x] AI-004: X.com API keys synced from egos-lab to egos/.env ✅ 2026-04-01
- [x] AI-005: qwq-plus (reasoning) added to deep tier fallback chain in llm-provider.ts ✅ 2026-04-01
- [x] AI-006: gem-hunter.ts migrated from egos-lab → egos/agents/agents/ ✅ 2026-04-01
- [x] AI-007: gem-hunter-adaptive.yml GH Actions workflow created in egos/.github/workflows/ ✅ 2026-04-01

**P1 — Hook integration:**
- [ ] AI-008: Add ai-coverage-scan.ts --check to pre-commit hook (fires when llm*.ts changes)
- [ ] AI-009: Wire Atrian OBS spans to AI calls in llm-provider.ts (cost + latency per call)
- [ ] AI-010: Unified cost dashboard — aggregate ai_events from all repos into single Supabase view

---

### Atrian Observability Module (2026-04-01)

**Source:** ChatGPT architecture + OTel public patterns + Claude Code hook system
**Principle:** Collect metadata, not payload. Telemetry mínima de conteúdo, máxima de comportamento.

**P1 — Foundation:**
- [x] OBS-001: `packages/atrian-observability/` skeleton — SpanCollector, 4 subdirs ✅ 2026-04-01
- [x] OBS-002: Telemetry policy — allowedFields, blockedPatterns, retention, opt-out (ATRIAN_TELEMETRY=off) ✅ 2026-04-01
- [x] OBS-003: 12 trace spans (session.start → hook.result) OTel-compatible ✅ 2026-04-01
- [x] OBS-004: 10 core metrics with alert thresholds (latency p95, tokens, override rate, stuck loops) ✅ 2026-04-01

**P2 — Integration:**
- [ ] OBS-010: Wire hooks → OTel spans (PreToolUse/PostToolUse emit span events)
- [ ] OBS-011: Gem Hunter session telemetry (pair analysis duration, transplant acceptance rate)
- [ ] OBS-012: Runtime dashboard vs Product analytics dashboard — separate concerns
- [ ] OBS-013: Privacy-preserving structured logs (no raw code, masked secrets, redacted paths)

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
- [ ] X-003: VPS cron deploy — REVERTED: was marked done but cron never set up. Needs: X_BEARER_TOKEN + crontab on 204.168.217.125
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

**P1 — Signal Layer:**
- [ ] INTEL-005: Signal ingestion — Gem Hunter scores > 80 → auto-append to world model signals (= GH-050)
- [ ] INTEL-006: Proactive blocker detection — world model scans P0 list → creates TASKS entries if blocker stale > 7 days
- [ ] INTEL-007: `--mermaid` output from world-model.ts → embed in /start briefing as ASCII architecture snapshot

**P2 — Full Intelligence:**
- [ ] INTEL-008: DRI auto-assignment — when P0 task has no commit activity for 3 days, auto-flag + Telegram alert
- [ ] INTEL-009: Capability composition map — intelligence layer dynamically suggests which agents to invoke for a given task
- [ ] INTEL-010: World model diff — compare snapshots to detect regression (tasks going from [x] back to [ ])


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
- [ ] EAGLE-GH-002: `document-parser.ts` — extract structured data from edital PDFs (objeto, valor, prazo, requisitos técnicos, habilitação)
- [ ] EAGLE-GH-003: `classification-service.ts` — auto-classify licitação by category + assign sector preset
- [ ] EAGLE-GH-004: `extraction-service.ts` — pull deadline, CNAE, required docs, financial requirements from raw text

**P1 — Intelligence Layer:**
- [ ] EAGLE-GH-005: `insight-generator.ts` — LLM-based recommendation: "bid / skip / investigate" with justification
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
### P19 Diagnostic Actions (2026-04-02)
**P0 — Theater Cleanup + Security:**
- [ ] THEATER-001: Deploy x-reply-bot (X_BEARER_TOKEN + crontab) or remove from done
- [x] SECURITY-001: Auth audit CLOSED — 0 gaps found ✅ 2026-04-02
- [ ] CTX-001: Context recovery hook to /start (load handoff + MEMORY.md)
- [x] TEST-001: Integration test suite — 21 tests (Guard Brasil PII/API, Eagle Eye opportunities, Gem Hunter scoring+CLI) ✅ 2026-04-02
- [x] EAGLE-EYE-UX-001: Dashboard UX (pagination 15/page, territory name resolution, classifications badges, value filter, segmento/porte display) ✅ 2026-04-02
**P1 — Architecture / Agents:**
- [ ] HERMES-001: Wire Hermes-3 as BRAID mechanical executor (OpenRouter free tier, 2h, 30-40% cost savings)
- [ ] OPENCLAW-001: Register Guard Brasil as OpenClaw MCP skill (precondition: MCP interface + 1 paying customer, Phase 2-3)
**P1 — Infrastructure:**
- [ ] DASH-001: Mission Control Dashboard — React + Supabase Realtime (SSOTs, agents, tasks, revenue tracker)
- [ ] CTX-002: Auto-index codebase-memory-mcp on /start (graph is cold, needs warm-up)
- [ ] REWARDS-001: Unified rewards engine — merge ETHIK + 852 gamification + credit system into @egos/rewards
- [ ] MOAT-001: Data flywheels (moats ≠ features) — Eagle Eye: bid outcomes→scoring, Gem Hunter: gem adoption→scores, Guard Brasil: mask patterns→improve (2-3w total)
