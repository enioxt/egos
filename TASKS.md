# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.29.0 | **Updated:** 2026-04-01 | **LAST SESSION:** 2026-04-01 P9 — Block Intelligence Model, INTEL-001..010, world-model.ts, AGENTS.md IC/DRI/Coach taxonomy

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
- [ ] EGOS-169: @aiready/pattern-detect pre-commit (duplicate detection)
- [ ] EGOS-173: CRCDM hooks: llmrefs staleness + auto-heal rename
- [x] EGOS-175: llmrefs blocks added to 5 leaf AGENTS.md (forja, carteira-livre, smartbuscas, br-acc, santiago) ✅ 2026-04-01

---

### Scheduled Jobs — 3 CCR slots (2026-04-01)

All Haiku, 00-06h BRT, reports in `docs/jobs/` + `docs/gem-hunter/`

- [x] Governance Drift Sentinel — diário 0h17 BRT (trig_01S5za...)
- [x] Code Intel + Security Audit — seg+qui 1h42 BRT (trig_01RDDk...)
- [x] Gem Hunter Adaptive Intelligence — seg+qui 2h37 BRT (trig_01Sn7Y...)
- [x] /start v5.6 — Phase 6 reads job results, flags CRITICAL as P0
- [x] GitHub Actions audit: 9 failing workflows disabled, only essential kept

---

### Eagle Eye — OSINT Licitações (2026-04-01)

**Code:** `/home/enio/egos-lab/apps/eagle-eye/`
**Domain:** `eagleeye.egos.ia.br` (DNS configured, Caddy pending)
**Supabase:** `lhscgsqhiooyatkebose` — 6 tables created, 15 territories seeded

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
- [ ] EAGLE-015: Dashboard filter UI for segmento/modalidade/porte taxonomy
- [ ] EAGLE-016: Sync 84 territories to Supabase (seed script)

**P2 — Revenue:**
- [ ] EAGLE-009: Stripe/Pix payment for Pro tier (R$497/mo, 50+ territories)
- [ ] EAGLE-010: Customer onboarding flow + dashboard customization
- [ ] EAGLE-011: E2E tests (Playwright)
- [ ] EGOS-170: Guard Brasil Next.js web dashboard — Vercel deploy, real data from guard_brasil_events, usage charts

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
- [ ] GH-012: EGOS ↔ Cline (`cline/cline`) — IDE agent autonomy, human-in-the-loop UX
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

---

### X.com Presence & Rapid Response (2026-04-01)

**Context:** Speed-to-thread matters. When a trending topic matches our capabilities, we must respond in hours, not days.

**Done:**
- [x] X-001: `scripts/x-reply-bot.ts` — 40 replies/day budget, 8 topic monitors, OAuth 1.0a, hourly cron VPS ✅ 2026-04-01
- [x] X-002: `scripts/rapid-response.ts` — 4 capability profiles, X thread generator, showcase README ✅ 2026-04-01
- [x] X-003: VPS cron deployed `0 * * * *` using `/opt/egos-lab/.env` keys ✅ 2026-04-01
- [x] X-004: Hermes-3 (nousresearch/hermes-3-llama-3.1-70b) added to llm-provider default tier ✅ 2026-04-01
- [x] X-005: `scripts/check-legacy-code.sh` + wired in pre-commit (check 8, non-blocking) ✅ 2026-04-01

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

**Source:** Jack Dorsey / Block essay "From Hierarchy to Intelligence" (block.xyz/inside/from-hierarchy-to-intelligence)
**Insight:** Hierarchy = routing protocol for information. Block replacing it with world model + intelligence layer + atomic capabilities. EGOS already has 70% of this. Fill the gaps.

| Block Concept | EGOS Status | Gap |
|---|---|---|
| World Model | codebase-memory-mcp + TASKS.md | No unified snapshot generator |
| Intelligence Layer | Kernel + BRAID (GH-037) | GRD not yet in /coordinator |
| Atomic Capabilities | CAPABILITY_REGISTRY.md | Not dynamically composed |
| Signal Layer | Gem Hunter (CCR) | Doesn't feed world model |
| Edge Roles (IC/DRI/Coach) | agents.json | No role taxonomy |

**Done:**
- [x] INTEL-001: `packages/shared/src/world-model.ts` — unified snapshot: tasks/agents/caps/signals/health% ✅ 2026-04-01

**P0 — Foundation:**
- [x] INTEL-002: Wire world-model.ts into /start Phase 0 (runs before everything, saves snapshot) ✅ 2026-04-01 (already in .claude/commands/start.md Phase 0)
- [x] INTEL-003: AGENTS.md update — map each agent to IC/DRI/Player-Coach taxonomy ✅ 2026-04-01 (IC/DRI/Coach table in AGENTS.md § Agent Role Taxonomy)
- [x] INTEL-004: GH-037 BRAID Mode — /coordinator emits Mermaid GRD before Implementation ✅ 2026-04-01. Phase 2 synthesis now outputs template GRD (frozen-zone guard, phase groupings, terminal states). Execution contract for cheap models.

**P1 — Signal Layer:**
- [ ] INTEL-005: Signal ingestion — Gem Hunter scores > 80 → auto-append to world model signals
- [ ] INTEL-006: Proactive blocker detection — world model scans P0 list → creates TASKS entries if blocker stale > 7 days
- [ ] INTEL-007: `--mermaid` output from world-model.ts → embed in /start briefing as ASCII architecture snapshot

**P2 — Full Intelligence:**
- [ ] INTEL-008: DRI auto-assignment — when P0 task has no commit activity for 3 days, auto-flag + Telegram alert
- [ ] INTEL-009: Capability composition map — intelligence layer dynamically suggests which agents to invoke for a given task
- [ ] INTEL-010: World model diff — compare snapshots to detect regression (tasks going from [x] back to [ ])

