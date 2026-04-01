# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.18.0 | **Updated:** 2026-03-31 | **LAST SESSION:** 2026-03-31 — Guard Brasil v0.2 + Market Research + VPS Orchestrator

---

### Guard Brasil Monetization Roadmap (NEW — from market research)

**Market insight:** No Brazilian-native PII detection API exists. CPF detected at only 45% by English tools. ANPD enforcement shifting to AI systems 2026-27.

**Completed:**
- [x] EGOS-151: Guard Brasil v0.2.0 — add SUS, Titulo de Eleitor, NIS/PIS (15 patterns total)
- [x] EGOS-152: MCP Server exists and works (guard_inspect, guard_scan_pii, guard_check_safe)
- [x] EGOS-153: Market report with 5 competitors analyzed + 3 monetization paths
- [x] EGOS-154: MasterOrchestrator deployed on VPS (cron every 30min, events in Supabase)
- [x] EGOS-155: /disseminate upgraded (7 phases, leaf repo propagation)
- [x] EGOS-156: /diag workflow created (full ecosystem diagnostic)
- [x] EGOS-157: VPS cron paths fixed (/home/enio → /opt/egos-lab)

**P0 — Revenue blocking:**
- [x] Consumer apps PII sync (2026-03-31): 852/forja/carteira-livre updated to v0.2.0 parity (3→15 patterns)
  - 852 pii-scanner.ts: 9→15 patterns
  - forja safety.ts: 4→15 patterns (reordered by specificity)
  - carteira-livre tutor-runtime.ts: 3→15 patterns
  - All have TODO (EGOS-158) comments awaiting npm publish
- [ ] EGOS-158: npm publish v0.2.0 (requires `npm adduser` — MANUAL) — **BLOCKED on user auth choice**
- [ ] EGOS-159: Guard Brasil REST API — wire npm package into Hono server on VPS (currently hardcoded patterns)
- [ ] EGOS-160: Reversible redaction — tokenized mask+restore (Grepture's killer feature)

**P1 — Competitive features:**
- [x] EGOS-161: Register MCP server in Claude Code (registered in .claude.json, verified v0.2.0 handshake)
- [ ] EGOS-162: Accuracy benchmark — publish CPF/RG/CNPJ detection rates vs Presidio/anonym.legal
- [ ] EGOS-163: Pix billing integration (no competitor accepts R$ via Pix)
- [ ] EGOS-164: Guard Brasil dashboard — real data from guard_brasil_events Supabase table

**P2 — Growth:**
- [ ] EGOS-165: White-label licensing outreach to Privacy Tools / Confidata
- [ ] EGOS-166: REST API gateway mode (HTTP proxy between apps and LLM providers)

---

### Neural Mesh — REVISED after Investigation (2026-03-31)

**Research:** `docs/research/NEURAL_MESH_INVESTIGATION_REPORT.md` (20+ tools evaluated)
**Original spec:** `docs/concepts/NEURAL_MESH_ARCHITECTURE.md` (superseded by compose strategy)
**Verdict:** COMPOSE — adopt market tools + keep EGOS-unique systems. 5h vs 14h.

**Phase 1 — Adopt market tools (P0, ~1.5h):**
- [ ] EGOS-167: Install codebase-memory-mcp (MIT, 1100 stars, single binary)
  - `curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash -s -- --ui`
  - Index all 9 EGOS repos: egos, egos-lab, 852, forja, carteira-livre, br-acc, smartbuscas, policia, INPI
  - Verify 3D graph UI at localhost:9749
  - Verify Claude Code MCP integration (`/mcp` shows 14 tools)
  - Replaces: Mycelium reference-graph.ts, Obsidian export, extract-mesh-graph.ts
- [ ] EGOS-169: Install @aiready/pattern-detect + wire pre-commit
  - `npm install -g @aiready/cli`
  - Add to CRCDM pre-commit: `npx @aiready/pattern-detect ./src --threshold 70 --quiet`
  - Configure: ignore tests, threshold 75% for validators, 70% for formatters
  - Replaces: EGOS-174 (custom feature registry)

**Phase 2 — llmrefs for governance docs (P1, ~1.5h):**
- [ ] EGOS-168: Add llmrefs blocks to 10 more governance files (manual, 15 total)
  - Level 0 (add to 3): TASKS.md, .windsurfrules, .guarani/IDENTITY.md
  - Level 1 (add to 7): .guarani/PREFERENCES.md, PIPELINE.md, DOMAIN_RULES.md, RULES_INDEX.md, SSOT_REGISTRY.md, CAPABILITY_REGISTRY.md, SEPARATION_POLICY.md
  - Keep existing 5 (AGENTS.md, SYSTEM_MAP.md, MYCELIUM_OVERVIEW.md, REFERENCE_GRAPH_DESIGN.md, NEURAL_MESH_INVESTIGATION_REPORT.md)
  - Each block: Role + Summary + Read next (typed edges)

**Phase 3 — CRCDM enhancement (P2, ~2h):**
- [ ] EGOS-173: CRCDM hooks: llmrefs staleness warning + auto-heal on rename
  - When git detects file rename → grep all llmrefs for old path → update → stage
  - When file with llmrefs modified but block unchanged > 30 days → warn
- [ ] EGOS-175: Add kernel llmrefs pointers to leaf repo AGENTS.md (manual, 7 repos)
  - Each leaf gets: `Read next: /home/enio/egos/AGENTS.md` + `docs/SSOT_REGISTRY.md`

**KILLED (market solved better):**
- ~~EGOS-170~~: extract-mesh-graph.ts → codebase-memory-mcp has richer graph + 3D UI
- ~~EGOS-171~~: inject-llmrefs.ts → MCP graph makes code-level headers unnecessary
- ~~EGOS-172~~: JSDoc @llmref → tree-sitter AST indexing is superior
- ~~EGOS-174~~: custom feature registry → @aiready/pattern-detect does this
- ~~EGOS-176~~: Obsidian export → codebase-memory-mcp 3D graph UI at localhost:9749

**npm publish (unblocked):**
- [ ] EGOS-158: npm publish @egosbr/guard-brasil@0.2.0 — token set, expires 2026-04-07

---

### Summary: Session 2026-03-31 (Full Diagnostic + P0-P2 Execution)

**Status:** DIAGNOSTIC COMPLETE | TELEMETRY WIRED | 6 AGENTS KILLED | CLAUDE.MD v2.0

**P0 Completed:**
- [x] Telemetry: event-bus emit wired into 4 VPS agents (uptime-monitor, quota-guardian, drift-sentinel, etl-orchestrator)
- [x] DOMAIN_RULES v2.1: updated providers (DashScope/OpenRouter/Groq/HF), date corrected
- [x] Full ecosystem diagnostic: 38 agents audited, telemetry 5-10% integrated, 60% theater identified

**P1 Completed:**
- [x] social-media agent KILLED (missing x-client module, never operational)
- [x] chatbot-compliance-checker KILLED (no implementation file)
- [x] Gem Hunter: Supabase persistence (dual-write SQLite + gem_hunter_gems/runs tables)
- [x] Guard Brasil dashboard-v1 set as default page (Vercel deployed)

**P2 Completed:**
- [x] CLAUDE.md v2.0: employee-grade overrides from leak analysis (forced verification, pre-work rule, useful repos)
- [x] Claude Code leak repos researched: best hooks/skills/settings patterns extracted

**Previously completed (same session):**
- [x] EGOS-145..149: naming, Qwen, event bus, orchestrator, Supabase migration
- [x] Guard Brasil web: Caddy split routing (guard.egos.ia.br = Vercel + API)
- [x] Killed 3 duplicate agents (-3,660 lines) + /start v2.0

**Completed (earlier this session):**
- [x] Killed 3 duplicate agents from egos-lab (-3,660 lines): drift-sentinel, ssot-auditor, ssot-fixer
- [x] Registry v2.1.0: fixed domain-explorer naming, social-media dead_reason, prompt as tool
- [x] /start v2.0: mandatory integration validation (15+ checks before any work)
- [x] Verified critical analysis from other session (6 claims correct, 4 claims wrong)

**Prove-or-Kill Results (completed 2026-03-31):**
- [x] EGOS-137: gtm-harvester — **KILLED** (hangs on --dry, no rate limiting, downloads all raw files)
- [x] EGOS-138: aiox-gem-hunter — **KILLED** (too niche, single-repo scanner for SynkraAI)
- [x] EGOS-139: framework-benchmarker — **KEPT** (3.3s, 7 findings, 5 frameworks)
- [x] EGOS-140: mastra-gem-hunter — **KILLED** (too niche, single-repo scanner for mastra-ai)
- [x] EGOS-141: autoresearch — **KEPT** (dry exits cleanly, research loop architecture)
- [x] EGOS-142: ui-designer — **KEPT** (1ms, 7 mockups generated)
- [x] EGOS-143: living-laboratory — **KEPT** (619ms, git pattern analysis, self-improvement)
- [x] EGOS-144: etl-orchestrator — **KEPT** (dry works, exec needs VPS API fix)

---

### Summary: Session 2026-03-31 (Gem Hunter + Guard Brasil + Pre-Commit Intelligence)

**Status:** GEM HUNTER v3.2 (13 SOURCES) | GUARD BRASIL WIRED IN ETL | PRE-COMMIT INTELLIGENCE LAYER

**Completed This Session:**
- [x] Gem Hunter v3.2: +Reddit, +StackOverflow, +ProductHunt sources (13 total)
- [x] Gem Hunter: SQLite historical tracking (history.db, --history flag)
- [x] AgentShield deny list: 10 dangerous operations blocked in settings.json
- [x] EGOS-130: Guard Brasil Python middleware in egos-inteligencia/ETL
  - GuardBrasilClient: HTTP wrapper for guard.egos.ia.br/v1/inspect
  - Offline fallback: 7 regex patterns (CPF, CNPJ, RG, MASP, REDS, email, telefone)
  - Pipeline.run() → _guard_check() between transform() and load()
  - guard_dataframe() for bulk PII scan on pandas DataFrames
- [x] Pre-commit intelligence layer (scripts/file-intelligence.sh)
  - File classification by type (report, doc, config, code, data, test)
  - Report compliance: REPORT_SSOT mandatory sections, confidence markers, citations
  - PII scan: unmasked CPF detection in docs, points to Guard Brasil
  - Config hygiene: .env blocked, docker restart:always warned
- [x] Rules discovery index (.guarani/RULES_INDEX.md)
  - Single entry point for ALL rules with lookup table + enforcement matrix
- [x] agents.json updated for gem-hunter v3.2

**Governance (2026-03-31):**
- [x] egos-lab TASKS.md compressed: 1033→140 lines, added identity directive ("lab in archival mode"), surface inventory created

**Backlog:**
- [ ] EGOS-125: M-007 outreach emails (MANUAL)
- [ ] EGOS-128: br-acc rename Phase 2+3 (MANUAL)
- [x] Gem Hunter: Supabase persistence (DONE — dual-write SQLite + Supabase)
- [ ] ARCH paused (separate session) — ARCH-002/004/013-015 pending

---

> **Archived sessions (2026-03-30 and earlier) → `docs/knowledge/TASKS_ARCHIVE_2026.md`**
- [x] Hindsight repo analyzed: biomimetic memory, MIT, 91.4% LongMemEval, @vectorize-io/hindsight-client npm
- [x] Grok conversation insights extracted: Aider alignment, NLAH paper (Tsinghua), activation patterns

**Pending This Session:**
- [ ] DNS A record `arch.egos.ia.br → 204.168.217.125` (**registered in registro.br, awaiting propagation**)

**New Tasks from Grok Insights:**
- [ ] EGOS-134: Hindsight memory integration — `@vectorize-io/hindsight-client` as persistent agent memory
  - SDK: npm package available, MIT license, 91.4% LongMemEval accuracy
  - Architecture: Retain/Recall/Reflect ops, Supabase PostgreSQL compatible
  - Effort: 4h adapter + 2h Zustand integration
  - Priority: P1 (enables cross-session agent memory without custom build)
- [ ] EGOS-135: Aider execution backend — CLI code editing + Git native for non-IDE environments
  - Repo: github.com/Aider-AI/aider (42.6k stars, Apache-2.0)
  - Integration: subprocess wrapper in agents, auto-commit + auto-fix
  - Solves: EGOS activation outside IDEs (terminal, Grok, servers)
  - Effort: 3h wrapper + 2h governance integration
  - Priority: P2 (nice-to-have, Claude Code already covers most cases)
- [ ] EGOS-136: NLAH (Natural-Language Agent Harnesses) evaluation
  - Paper: arXiv 2603.25723 (Tsinghua) — +4.8% SWE-bench via dynamic SOPs
  - Concept: Let agents generate their own orchestration SOPs in natural language
  - EGOS alignment: Governance rules as human-locked invariants, agents generate dynamic SOPs within constraints
  - Effort: 8h research + prototype
  - Priority: P2 (innovative but not blocking revenue)

---

### Summary: Session 2026-03-30 (Guard Brasil GTM TRANSPARÊNCIA RADICAL - IN PROGRESS)

**Status:** ARCHITECTURE COMPLETE | CRITICAL: M-007 OUTREACH

**Completed:**
- [x] GTM Pivot: TRANSPARÊNCIA RADICAL pay-per-use model
- [x] Architecture Stack: 4-layer (Client → Core → Data → Analytics)
- [x] 3-Week Roadmap + Sales Kit + M-001/M-002/M-004
- [x] Pricing v2.0: Data-driven from 8 competitors (Grepture, Cloak, Protecto, etc.)
  - Corrected R$0.02 → R$0.0049/call (was 7x overpriced). Tiers: Free/49/199/499
  - Document: `docs/strategy/GUARD_BRASIL_PRICING_RESEARCH.md`
- [x] X.com automation plan: API research, 5 drafts, pipeline spec
  - Document: `docs/strategy/XCOM_SOCIAL_AUTOMATION_PLAN.md`
- [x] 3 dashboard versions (code, not docs): Giant/Lean/Radical
  - Code: `apps/guard-brasil-web/components/DashboardV{1,2,3}*.tsx`
- [x] Landing page with 6 interactive examples + pricing section
  - Code: `apps/guard-brasil-web/app/page.tsx`
- [x] Public docs hardening + branding alignment
  - Removed public IPs, demo API key, and secret-location hints from active public docs
  - Aligned package naming to `@egosbr/guard-brasil` and current public tiers (Free/49/199/499)
  - Added local demo route: `apps/guard-brasil-web/app/api/test/route.ts`
- [x] TELEMETRY_SSOT.md: Canonical schema + 5 repo extensions
- [x] 5 ChatGPT chats analyzed: PRI, Agent SSOT, House, Multi-LLM, BRACC
- [x] EGOS-098: Benchmark Enforcement Contract — `.guarani/orchestration/BENCHMARK_ENFORCEMENT.md` — 4 patterns, enforcement matrix, violation signatures, consequences
- [x] EGOS-132: Brand canonical resolution — `docs/BRAND_CANONICAL.md` — PRESENTATION_VISUAL_IDENTITY.md wins (Navy #0A0E27, Blue #2563EB, Inter), egos-lab guide superseded

**SSOT Visits (2026-03-30):**
- [x] SSOT-VISIT 2026-03-30: egos-lab/branding/BRAND_GUIDE.md → read full (Cyan/Purple v1.0.0, 2026-02-22) → superseded
- [x] SSOT-VISIT 2026-03-30: egos/docs/PRESENTATION_VISUAL_IDENTITY.md → read full (Navy/Blue v1.0.0, 2026-03-26) → kept-as-ref (canonical)
- [x] SSOT-VISIT 2026-03-30: egos/docs/_current_handoffs/handoff_2026-03-22.md → Cambraia dark-enterprise context → kept-as-ref
- [x] SSOT-VISIT 2026-03-30: egos/.guarani/orchestration/WORKTREE_CONTRACT.md → read 100 lines for EGOS-098 → kept-as-ref
- [x] SSOT-VISIT 2026-03-30: egos/.guarani/orchestration/DOMAIN_RULES.md → read full for EGOS-098 → kept-as-ref
- [x] SSOT-VISIT 2026-03-30: carteira-livre/supabase/migrations/20260330_create_carteira_livre_events.sql → reviewed telemetry schema alignment → kept-as-ref (TELEMETRY_SSOT.md canonical)

**Critical Blocker:**
- [ ] **M-007** Send 5+ outreach emails (only action blocking revenue)

**New Tasks (from ChatGPT analysis):**
- [x] **EGOS-070** PRI safety gate — `guards/pri.ts`, BLOCK/DEFER/ESCALATE, tests pass
- [x] **EGOS-071** Agent SSOT v2 — 22-field schema, `kind` field, 0 verified agents, 14 tools
- [x] **EGOS-072** Multi-LLM router U(m,t) — 5 models, 4 lanes, 11/11 tests pass
- [x] **EGOS-131** Eagle Eye surgery v3.0: strip to procurement core (2026-03-30)
  - DONE: Killed SEO_STRATEGY, COMMUNITY_STRATEGY, GAMIFICATION_REPORT, TOURISM_MODULE, STITCH_PROMPTS
  - DONE: Dashboard.tsx "28 territories" → "15" (real count), README rewritten
  - Owner: egos-lab — committed
- [x] **EGOS-132** Resolve EGOS brand conflict: two incompatible color palettes exist — **COMPLETE (2026-03-30)**
  - **Decision:** `egos/docs/PRESENTATION_VISUAL_IDENTITY.md` is canonical (Navy/Blue/Inter)
  - **Reasoning:** newer (+32 days), 5x more complete, explicitly aligned with dark-enterprise/operator aesthetic, matches Gabriel Cambraia GTM positioning
  - **Canonical guide:** `docs/BRAND_CANONICAL.md` — decision record + migration notes + Cambraia brief
  - **Superseded:** `egos-lab/branding/BRAND_GUIDE.md` — SUPERSEDED header added; archive on next cleanup
  - **SSOT visits logged:** both files read, handoff_2026-03-22.md read for Cambraia context
- [x] **EGOS-133** Eagle Eye: consolidate duplicate EagleEye.tsx in br-acc — **COMPLETE (2026-03-30)**
  - Decision: INDEPENDENT — br-acc/Querido Diário direct API vs egos-lab/pre-processed backend; both canonical
  - Action: SSOT-VISIT header added to br-acc/frontend/src/pages/EagleEye.tsx
- [ ] **EGOS-073** BRACC Operacional: blueprint para módulo policial PCMG
  - Spec completa em ChatGPT export (7 camadas, 20 módulos, break-glass access)
  - Guard Brasil como motor de validação MASP/PII
  - Prioridade: P2 (aguarda contexto institucional)

**Handoff:** `docs/_current_handoffs/handoff_guardbrasil_gtm.md`

---

> **Archived to `docs/knowledge/TASKS_ARCHIVE_2026.md` (2026-03-31):**
> - Session 2026-03-30 (Secret Scanning) — 3 items complete + 1 manual
> - Sessions 2026-03-26 (PR #4 + CI) — 2 items complete
> - Session 2026-03-25 — 14 items complete (EGOS-061..076, FORJA, BLUEPRINT)
> - Guard Brasil package (EGOS-062..064) — all complete, npm published
- [ ] EGOS-077: Add the new-project gate for PRD, ICP, go-to-market, objective, success metric, and multi-model review mode with a recorded blocking-vs-advisory decision
- [x] EGOS-078: Agent Claim Contract — `.guarani/orchestration/AGENT_CLAIM_CONTRACT.md` — 6-level taxonomy (component|tool|workflow|agent_candidate|verified_agent|online_agent) + proof matrix
- [x] EGOS-079: Agent Claim Gate — `scripts/agent-claim-lint.ts` — lint agents.json, exit 1 on verified/online without proof, passes on current registry
- [x] EGOS-080: LLM Orchestration Matrix — `.guarani/orchestration/LLM_ORCHESTRATION_MATRIX.md` — 5 orchestrators, 4 lanes, routing flow, fallback chain, conflict table
- [x] EGOS-093: Define canonical flagship brief in SSOT — objective, problem statement, personas, and GTM with acceptance metrics
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/strategy/FLAGSHIP_BRIEF.md` — one-sentence VP, problem statement, personas, differentiation matrix, monetization model, success metrics
- [ ] EGOS-094: Create "Market Intelligence Compiler" spec — ingestion contract for books/papers/code/platforms with source-link + evidence tiers
- [ ] EGOS-095: Build governance rule registry for market practices — normalize global best practices into executable controls and tests
- [ ] EGOS-096: Add cross-environment signature adoption for Google AI Studio lane (commit/push provenance fields mandatory)
- [x] EGOS-097: /disseminate protocol — SSOT Visit Audit Step 0, SSOT Gem Scan in /start, Phase 4.2 BLOCKING in /end. Files: ~/.egos/workflows/{disseminate,start,end}.md
- [x] EGOS-098: Ingest and operationalize pragmatic multi-agent benchmark patterns (worktree isolation, parallel ticket lanes, QA loop, file-first context) into kernel governance with explicit keep/drop decisions — **COMPLETE (2026-03-30)**
  - **Contract:** `.guarani/orchestration/BENCHMARK_ENFORCEMENT.md` — enforcement matrix for all 4 patterns
  - **Patterns covered:** Worktree Isolation (ACTIVE), Parallel Ticket Lanes (PARTIAL), QA Loop (delegates to EGOS-101), File-First Context (ACTIVE)
  - **Enforcement surfaces:** pre-commit hook, /start GATE, /end Phase 4 for each pattern
  - **Next:** EGOS-101 QA Loop Contract completes the remaining enforcement gap
- [x] EGOS-099: Worktree Orchestration Contract — `.guarani/orchestration/WORKTREE_CONTRACT.md` — branch naming, 72h max, 24h abandonment, merge gates, EnterWorktree/ExitWorktree
- [x] EGOS-100: Define `Linear/Issue Sync Contract` (`/linear-sync`) with task decomposition schema, priority classes, and required evidence at PR gate — **COMPLETE (2026-03-30)**
  - Contract: `.guarani/orchestration/LINEAR_SYNC_CONTRACT.md` — adoption trigger (>50 tasks + multi-contributor), decomposition schema, P0-P3 classes, PR gate evidence, sync direction (TASKS.md SSOT), `/linear-sync` skill spec
- [x] EGOS-101: Define `QA Loop Contract` (`/qa-loop`) using browser/devtools verification + test rerun policy + stop conditions — **COMPLETE (2026-03-30)**
  - Contract: `.guarani/orchestration/QA_LOOP_CONTRACT.md` — L0-L3 levels, stop conditions, evidence format, rerun policy
- [x] EGOS-102: Build executable 10-second operator map (replace text-heavy integration map with founder-grade control plane view) — **COMPLETE (2026-03-30)**
  - Document: `docs/OPERATOR_MAP.md` — ASCII tables, live services, revenue path, active agents, open blockers, quick commands
- [x] EGOS-131: Define `Integration Release Contract` for EGOS — **COMPLETE (2026-03-30)**
  - **Contract:** `.guarani/orchestration/INTEGRATION_RELEASE_CONTRACT.md`
  - **Executable Gate:** `scripts/integration-release-check.ts` + `bun run integration:check`
  - **Typed Manifest Contract:** `packages/core/src/integration.ts`
  - **First Canonical Bundle:** `integrations/manifests/whatsapp-runtime.json` + `integrations/distribution/whatsapp-runtime/`
  - **SSOT Updates:** `AGENTS.md`, `docs/SYSTEM_MAP.md`, `docs/CAPABILITY_REGISTRY.md`, `docs/knowledge/WHATSAPP_SSOT.md`, `integrations/README.md`, `.guarani/orchestration/DOMAIN_RULES.md`
  - **Validation:** `bun run integration:check` ✅, `bun run typecheck` ✅
  - **Pending:** `bun run governance:sync:exec` required before `bun run governance:check` returns 0 drift
- [x] EGOS-107: Define and activate Stitch-first UI contract (`/stitch`) — prompt generation in EGOS lane, external creation in Google Stitch, and `.zip` intake mapping before implementation
- [ ] EGOS-108: Build `stitch_intake_mapper` agent to parse returned `.zip`, generate mapping table, and create integration tasks automatically
- [x] EGOS-109: Run full AIOX (`SynkraAI/aiox-core`) gem diagnosis against EGOS + NotebookLM export and codify keep/drop recommendations
- [x] EGOS-110: Implement `Worktree Orchestration Contract` from AIOX/workflow benchmark — **COMPLETE**
  - **Contract Document:** `.guarani/orchestration/WORKTREE_CONTRACT.md` (v1.0.0) — formal spec with naming rules (regex), ownership model, lifecycle state machine, merge gates, concurrency limits (max 5), and JSON report schema
  - Script: `scripts/worktree-validator.ts`; Registry: `.guarani/worktrees.json`; /start GATE integrated; concurrency (2/5 active) verified
- [x] EGOS-111: Implement Spec-Pipeline Workflow Contract (analyst → pm → architect → sm) — **COMPLETE**
  - Contract: `.guarani/orchestration/SPEC_PIPELINE_CONTRACT.md` (v1.0.0); Agent: `agents/agents/spec-router.ts`; CI: `.github/workflows/spec-pipeline.yml`; E2E: `tests/spec-pipeline.e2e.test.ts`
- [x] EGOS-112: Build lightweight `doctor` command for environment + governance readiness inspired by AIOX installer/doctor
  - **Status:** COMPLETE (100% — from 60%)
  - **Implementation:** `bun scripts/doctor.ts` with full environment validation
  - **Checks Implemented (23 total):**
    - Environment: 10 checks (2 required API keys, 8 optional providers)
    - Files: 4 checks (freshness validation for AGENTS.md, TASKS.md, .windsurfrules, SYSTEM_MAP.md)
    - Providers: 3 checks (API reachability for Alibaba DashScope, OpenRouter, OpenAI)
    - Hooks: 2 checks (Husky directory and pre-commit hook status)
    - Workspace: 3 checks (git status, upstream sync, branch state)
    - Governance: 1 check (drift detection via governance:check)
  - **Features:**
    - Exit codes: 0 (all ok), 1 (warnings), 2 (failures)
    - Flags: `--json`, `--fix`, `--no-network`, `--doctor-skip`, `--verbose`
    - JSON report output in `docs/_generated/doctor-report.json` (timestamped)
    - Auto-fix capability for stale docs and missing hooks
    - Smart recommendations engine (4+ contextual fixes per scenario)
  - **Integration into /start:**
    - GATE phase executes `bun run doctor --json` as blocking validation
    - Exit code governs workflow: 0→proceed, 1→warn+continue, 2→block+recommendations
    - Report included in final /start output summary
  - **Validation tested:**
    - Missing env vars (failures detected)
    - Stale docs (warnings + fixable flags)
    - Provider offline (graceful degradation with --no-network)
    - Skip override (--doctor-skip flag works)
    - Exit codes (0, 1, 2 tested)
  - **Documentation:** Updated `.agents/workflows/start-workflow.md` GATE phase with doctor gate details and `.windsurf/workflows/start.md` compatibility wrapper
- [x] EGOS-113: Benchmark MASA framework + major competitors from official sources and create executable benchmark agent (`framework_benchmarker`)
- [ ] EGOS-114: Run MASA pilot in one leaf repo and measure impact on drift, architectural violations, and lead-time before broader adoption
- [x] EGOS-115: Create `mastra_gem_hunter` agent and run initial scan for workflow/evals/observability/MCP/human-loop extraction
- [ ] EGOS-116: Define "Presentation System" SSOT for EGOS (positioning, promise, evidence, differentiators, anti-bloat thesis) in canonical surfaces
- [ ] EGOS-117: Build operator-facing narrative kit (1-page pitch + architecture map + proof checklist) from existing SSOT without creating parallel truths
- [ ] EGOS-118: Create reproducible demo lane for meetings (live build script + guardrails checklist + fallback offline path)
- [ ] EGOS-119: Add benchmark scorecard command comparing EGOS vs MASA/Mastra/LangGraph/CrewAI on governance, speed, and compliance
- [ ] EGOS-120: Define visual identity/application rules for docs and generated artifacts (consistency pack)
- [x] EGOS-121: Add monthly "clarity review" gate to prune complexity and keep kernel message/simple architecture coherent — **COMPLETE (2026-03-30)**
  - Contract: `.guarani/orchestration/CLARITY_REVIEW.md` — 5 clarity questions, inputs, outputs, 500-line gate, archive protocol, `/clarity-review` trigger registered in `~/.egos/guarani/prompts/triggers.json`
- [x] EGOS-083: Create the canonical cross-repo SSOT registry in the kernel and define the ownership contract for `kernel_canonical`, `leaf_local`, and `shared_home` surfaces
- [x] EGOS-084: Extend kernel governance sync + pre-commit to cover canonical SSOT docs (`SSOT_REGISTRY`, `CAPABILITY_REGISTRY`, `CHATBOT_SSOT`) and sync them to `~/.egos/docs`
- [x] EGOS-085: Roll out the SSOT registry adoption plan across mapped repos — **COMPLETE (2026-03-30)** — `docs/SSOT_REGISTRY.md` v2.0.0: 30 domains, per-repo grades (A/B/C/D), rollout checklist, 14 SSOT-VISITs logged
- [x] EGOS-093: Canonicalize `/start` command surface for Claude Code/Codex — `.agents/workflows/start-workflow.md` as SSOT + `.windsurf/workflows/start.md` compatibility wrapper
- [ ] EGOS-094: Create BLUEPRINT integration placement contract — define exact destination for AAR/registry/audit interfaces in kernel (`packages/shared` adapters first, no big-bang move)
- [x] EGOS-095: Add \"evidence-first\" activation report contract — `/start` now enforces verified facts vs inference vs proposal with explicit evidence-first blocking checklist
- [ ] EGOS-096: Define phased execution plan for EGOS Commons/split initiative with explicit legal/compliance gates before payment automation
- [ ] EGOS-097: Add cross-repo research intake workflow — when external LLMs (e.g., Grok) are used without repo access, require reconciliation pass against kernel SSOT before planning decisions
- [x] EGOS-098: Standardize PR communication pack — canonical `/pr` workflow + PR template + `pr:pack` generator with environment context, validation status, rollback notes, and signed-off footer
- [x] EGOS-099: Add enforceable post-PR IDE validation gate (Windsurf + Antigravity) with evidence checklist + `pr:gate` proof before merge
- [x] EGOS-100: Add canonical `/disseminate` workflow + Codex instruction setup guide (load order, governance propagation, PR gate flow)
- [x] EGOS-101: Add reusable EGOS activation meta-prompt v1.1.0 with ATRiAN honesty filter + next-AI review mandate and trigger mapping
- [x] EGOS-102: Add ecosystem PR audit automation (`pr:audit`) + canonical `/mycelium` workflow for active/inactive PR mesh classification

> **Directive (2026-03-30):** Guard Brasil go-to-market is P0 chain: npm publish → API deploy on Hetzner → cold outreach 20 CTOs govtech → first customer. br-acc rename to egos-inteligencia is P1 (script ready, needs --execute). FORJA and Santiago = frozen (no work this session).

---

## Guard Brasil GTM — P0 Chain (2026-03-30)

- [x] EGOS-123: `npm publish --access public` for @egosbr/guard-brasil v0.1.0 — **COMPLETE (2026-03-30)**
  - Published as `@egosbr/guard-brasil` on npm (commit 0cb570c confirms)
- [x] EGOS-124: Deploy Guard Brasil REST API on Hetzner — **COMPLETE (2026-03-30)**
  - Container: `guard-brasil-api` healthy, port 3099, restart: unless-stopped
  - Caddy: `guard.egos.ia.br` entry added (TLS auto)
  - **⚠️ BLOCKED**: DNS A record `guard.egos.ia.br` requires final validation in DNS provider (MANUAL M-002)
  - Health cron: `*/5 * * * *` no Hetzner monitorando e auto-restart
  - API key: secret store on the server (path intentionally omitted)
  - Deploy script: `bash apps/api/deploy.sh`
- [ ] EGOS-125: Cold outreach — 20 CTOs govtech BR (**MANUAL — M-007**)
  - Templates prontos: `docs/strategy/OUTREACH_EMAILS.md` (3 templates + lista de 20 targets)
  - Dep: DNS guard.egos.ia.br ativo (M-002) para demos funcionarem
- [x] EGOS-126: Build EGOS-116/117 sales kit — **COMPLETE (2026-03-30)**
  - 1-pager: `docs/strategy/GUARD_BRASIL_1PAGER.md`
  - Demo script 30min: `docs/strategy/GUARD_BRASIL_DEMO_SCRIPT.md` (com FAQ)
- [x] EGOS-G002: Consolidate PII patterns to shared config — **COMPLETE (2026-03-30)**
  - Created `packages/guard-brasil/src/pii-patterns.ts`: 12 Brazilian PII patterns
  - Exported `detectPII(text)` → PIIMatch[] and `maskPII(text)` → masked string
  - Refactored pii-scanner.ts to import centralized patterns (backward compatible)
  - Re-exported all from index.ts

## ARCH Project Revival (2026-03-30)

**Status:** Deep dive complete — brutal honesty assessment + 12-week execution roadmap created.

**Current State (Honest Assessment):**
- ✅ UI 80% complete: Chat interface, 9-view navigation, export utilities working
- ❌ Backend 80% missing: No persistence, no vision pipeline, no parametric engine, no 3D generation, no video integration, no Python workers
- 🔴 **CRITICAL SECURITY ISSUE:** Hardcoded OpenRouter API key in `server.ts` line 13

**Completed (2026-03-30):**
- [x] Read ChatGPT conversation exports (2 files) that originated ARCH concept
- [x] Clone and analyze GitHub repo structure + all 9 React components
- [x] Review backend architecture, telemetry framework, state management
- [x] Identify honest truth: 20% complete, 80% backend missing
- [x] Create 12-week phased implementation plan with realistic effort estimates
- [x] Document staffing recommendations (1 full-stack + 1 frontend for Phase 1)
- [x] Establish success metrics and decision gates (weeks 4, 8, 12)

**Phase 1 (Weeks 1-4): Foundation — Persistence + Vision Pipeline + 3D Generation**

- [x] ARCH-001: Fix critical API key exposure (move to `.env`) — **COMPLETE (2026-03-30)**
  - Moved to `process.env.OPENROUTER_API_KEY` in server.ts
  - Deployed to Hetzner VPS: port 3098, container `egos-arch`
  - Caddy configured: `arch.egos.ia.br` → egos-arch:3000 (Docker network)
  - **LIVE:** https://arch.egos.ia.br — TLS auto-provisioned, chat + briefing APIs working

- [ ] ARCH-002: Setup Supabase database schema (persistence foundation)
  - Effort: 3h | Owner: full-stack
  - Schema: projects table (id, user_id, briefing_json, floor_plan_json, created_at, updated_at)
  - Auth: Row-level security for multi-tenant
  - Dependencies: Supabase CLI, migration runner

- [ ] ARCH-003: Implement authentication gate
  - Effort: 2h | Owner: full-stack
  - Require Supabase session before saving projects
  - Store user context in Zustand + session provider
  - Validation: Login flow blocks unsaved state loss

- [ ] ARCH-004: Wire Sketch → Geometry Vision Pipeline
  - Effort: 4h | Owner: full-stack + AI expert
  - Replace 2.5s fake delay in pipeline.ts with actual Gemini 3.1 Pro vision call
  - Input: uploaded sketch image
  - Output: JSON geometry spec (walls, openings, dimensions, roof pitch)
  - Prompt: architect-agent.ts already written; use it verbatim
  - Validation: produce valid JSON, not hardcoded "hexagon"

- [ ] ARCH-005: Implement 3D Model Generation (Trimesh)
  - Effort: 5h | Owner: Python specialist
  - Python worker endpoint: `POST /generate-3d` accepts geometry JSON
  - Output: glTF 2.0 model
  - Library: Trimesh + pyassimp
  - Integration: Send model to frontend for Three.js visualization

- [ ] ARCH-006: Test end-to-end: sketch → JSON → 3D → visual proof
  - Effort: 1h | Owner: full-stack
  - E2E test: upload hex sketch, verify 3D model renders
  - Store result in Supabase
  - Screenshot for handoff proof

**Phase 2 (Weeks 5-8): Usability — Briefing Robustness + Auto Planta + Images**

- [ ] ARCH-007: Robustify briefing interpreter (ATRiAN honesty gates)
  - Effort: 3h | Owner: AI expert
  - Add fact-checking for claims (e.g., "I have R$500k budget" → validate against material costs)
  - Add evidence linking (reference constraints from uploaded docs)
  - Prevent hallucinations in room suggestions

- [ ] ARCH-008: Implement 2D Floor Plan Auto-Generation
  - Effort: 4h | Owner: Python + geometry
  - Input: 3D model from ARCH-005
  - Output: 2D floor plan (SVG or PDF)
  - Algorithm: orthogonal projection + dimension extraction
  - Integration: Display in PlantaView component

- [ ] ARCH-009: Wire AI Image Generation (Gemini 3 Pro Image)
  - Effort: 3h | Owner: full-stack
  - Integration: `POST /generate-render` with camera params + model
  - Output: photorealistic render image (1024x1024)
  - Validation: store in Supabase, display in RendersView

- [ ] ARCH-010: Build render variation panel (multiple angles + lighting)
  - Effort: 2h | Owner: frontend
  - Generate 4 renders: front, back, left, right + one sunset lighting
  - Batch API calls with quota management
  - Cache results in Supabase

**Phase 3 (Weeks 9-12): Polish — Performance + Error Handling + Docs + Video**

- [ ] ARCH-011: Implement video walkthrough generation (Veo 3.1)
  - Effort: 6h | Owner: video + Python
  - Input: 3D model + camera path + audio (optional)
  - Output: 30-60 second MP4 walkthrough
  - Integration: VideoView component + Supabase storage

- [ ] ARCH-012: Performance optimization + caching
  - Effort: 3h | Owner: full-stack
  - Cache generated models, renders, videos in Supabase blob storage
  - Implement request deduplication (same sketch → same result)
  - Add loading states + progress bars to all views

- [ ] ARCH-013: Error handling + graceful degradation
  - Effort: 2h | Owner: full-stack
  - Try/catch all API calls with user-friendly error messages
  - Fallback: if vision fails, prompt user to redraw or describe
  - Fallback: if 3D fails, show 2D floor plan only
  - Telemetry: log all failures for monitoring

- [ ] ARCH-014: Complete integration tests + E2E validation
  - Effort: 3h | Owner: full-stack + QA
  - Test flow: upload sketch → briefing → 3D → 2D plan → renders → video
  - Test error cases: bad image, invalid geometry, API timeouts
  - Test persistence: reload project and verify state

- [ ] ARCH-015: Documentation + README updates
  - Effort: 2h | Owner: technical writer
  - API docs for each backend endpoint
  - User guide for each view (Briefing, Croqui, Planta, Massa3D, Renders, Video, Export)
  - Architecture diagram: data flow from sketch to video

**Success Metrics & Decision Gates:**

| Gate | Week | Decision | Evidence |
|------|------|----------|----------|
| **Week 4 Gate** | 4 | Can we persist projects + upload sketches + generate basic 3D? | ARCH-001 through ARCH-006 all passing |
| **Week 8 Gate** | 8 | Can we generate 2D plans + renders automatically? | ARCH-007 through ARCH-010 all passing |
| **Week 12 Gate** | 12 | Can we generate walkthrough videos + handle errors gracefully? | ARCH-011 through ARCH-015 all passing |

**Effort Summary:**
- Phase 1: 25 hours (1.5 weeks for 2-person team)
- Phase 2: 12 hours (1 week for 2-person team)
- Phase 3: 10 hours (1 week for 2-person team)
- **Total: 47 hours ≈ 6-7 weeks with 2 full-time contributors**

**ARCH PAUSED** — user decision. Pending: DNS A record, Supabase setup, real API keys on VPS.

---

## br-acc → egos-inteligencia Rename (2026-03-30)

- [x] EGOS-127: Execute rename Phase 1 (docs) — **COMPLETE (2026-03-30)**
  - 47 arquivos .md/.html atualizados, commitado e pushado para EGOS-Inteligencia
  - Confirmado: GitHub repo já se chama `enioxt/EGOS-Inteligencia`
- [ ] EGOS-128: Execute rename Phase 2+3 (Python imports + Docker configs) — **MANUAL M-003**
  - `bash /home/enio/br-acc/scripts/rename-to-egos-inteligencia.sh --execute` (fases 2-5)
  - Após: `git mv etl/src/bracc_etl etl/src/egos_inteligencia_etl`
  - Valida: `python -c "from egos_inteligencia_etl.runner import main"`
- [ ] EGOS-129: Docker network rename + redeploy Hetzner — **MANUAL M-005**
  - Dep: EGOS-128 completo
  - `ssh hetzner 'docker network rename infra_bracc infra_egos_inteligencia'`
- [x] EGOS-130: Wire Guard Brasil middleware em egos-inteligencia — **COMPLETE (2026-03-31)**
  - `etl/src/bracc_etl/guard.py`: GuardBrasilClient + offline fallback + guard_dataframe()
  - Pipeline.run() → _guard_check() entre transform() e load()
  - Commit: `03f1981` em br-acc

> **Archived sections moved to `docs/knowledge/TASKS_ARCHIVE_2026.md`:**
> - Benchmark Alignment Plan (2026-03-26)
> - Grok Intake Queue (2026-03-30)
> - P0 (Blockers) — 9/9 complete
> - P1 (Critical) — 13/13 complete
> - P2 (Important) — 37/37 complete

> **Backlog and historical items archived in `docs/knowledge/TASKS_ARCHIVE_2026.md`:**
> - Backlog (20 deferred items: EGOS-012, 014, 015, 023, 024, 053, 071, 072, 089, 090, 091, 092)
> - SSOT Core Infra v2 (3 items)
> - Roadmap Progress Dashboard (P0 100%, P1 100%, P2 100%)
> - Infrastructure Migration (INFRA-001..027 COMPLETE, Contabo→Hetzner 2026-03-28)
