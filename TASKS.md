# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.11.0 | **Updated:** 2026-03-30 | **LAST SESSION:** 2026-03-30 — Guard Brasil GTM TRANSPARÊNCIA RADICAL Sprint

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
- [x] **EGOS-070** Implement PRI (Protocolo de Recuo por Ignorância) as safety gate
  - Artefatos: `protocols/pri.md`, `guards/pri.ts`, `policies/pri.rego`
  - Conexão: Safety gate para Guard Brasil API (BLOCK/DEFER/ESCALATE)
  - Entregue: `packages/core/src/guards/pri.ts`, `packages/core/src/guards/pri.test.ts`, `packages/core/src/auth/contracts.ts`, `packages/core/src/index.ts`, `apps/api/src/pri.ts`, `apps/api/src/server.ts`, `apps/api/src/mcp-server.ts`, `policies/pri.rego`
  - Evidência: `bun test packages/core/src/guards/pri.test.ts`, `bun test packages/guard-brasil/src/guard.test.ts`, smoke real em `POST /v1/inspect` (200 ALLOW + 202 DEFER)
  - Prioridade: P1 (alto impacto, baixo custo)
- [x] **EGOS-071** Resolver SSOT de agentes: reclassificar com schema 22 campos — **COMPLETE (2026-03-30)**
  - Schema v2: 22 campos com `kind` field (verified_agent/agent_candidate/workflow/tool/dormant)
  - Novos campos: runtime_proof, telemetry_source, cost_source, last_duration_ms, loop_mechanism, side_effects
  - Resultado: 0 verified_agents no kernel, 14 tools, 1 workflow (spec_router)
  - Arquivos: `agents/registry/schema.json` v2.0, `agents/registry/agents.json` v2.0
- [x] **EGOS-072** Implementar fórmula de roteamento multi-LLM U(m,t) — **COMPLETE (2026-03-30)**
  - Formula: `U = wc*Capability + wr*Reliability - ck*CostNorm - cq*QuotaRisk`
  - 5 modelos: qwen-plus, qwen-turbo, gemini-flash, claude-sonnet, gpt-5.4
  - 4 lanes: planner, executor, cheap, sovereign
  - Guard Brasil shortcuts: `routeGuardBrasil('pii_detection')` → cheap, `bias_analysis` → sovereign
  - Quota tracking: `reportUsage()` + `resetQuotas()` per-minute
  - Arquivos: `packages/shared/src/llm-router.ts`, `packages/shared/src/llm-router.test.ts`
  - Tests: 11/11 pass
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

### Summary: Session 2026-03-30 (Secret Scanning + Hardening - COMPLETE)
- [x] Secret leak sanitized (Supabase token in 852 handoff docs)
- [x] Hardened pre-commit: gitleaks + regex fallback across all repos
- [ ] Revoke/rotate exposed Supabase token (user action)

---

### Summary: Session 2026-03-26 (PR #4 Merge + Governance Sync - COMPLETE)
- [x] PR #4 merged (commit 3932067), 5 conflicts resolved, all validations passed

---

### Summary: Session 2026-03-26 (CI Troubleshooting - COMPLETE)
- [x] EGOS-122: Fix CI frozen zones bash syntax error — commit cab3083, PR #5 auto-closed

---

### Summary: Session 2026-03-25

**Completed:**
- ✅ FORJA signup without email confirmation (tested, live)
- ✅ BLUEPRINT-EGOS absorption + architecture documentation
- ✅ VPS hosting strategy analysis + cost savings calculation ($60-100/mo)
- ✅ EGOS agent orchestration blueprint (Router/Supervisor pattern)
- ✅ Memory + HARVEST.md updates
- ✅ System-wide dissemination (this TASKS.md update)

- [x] EGOS-061: Publish consolidated ecosystem verdict and repo roles — `docs/strategy/ECOSYSTEM_PRODUCT_VERDICT_2026-03.md`
- [x] EGOS-062: Package the canonical product boundary for `EGOS Guard Brasil` — ATRiAN + PII Scanner BR + public guard + evidence discipline
  - **Status:** COMPLETE (2026-03-29)
  - **Package:** `packages/guard-brasil/` — `@egosbr/guard-brasil` v0.1.0
  - **Files:** `src/index.ts`, `src/guard.ts` (GuardBrasil facade), `src/demo.ts`, `src/guard.test.ts`, `README.md`
  - **Tests:** 15/15 pass (bun test) — clean output, PII detection, ATRiAN validation, evidence chain, combined scenarios
  - **Capabilities:** CPF/RG/MASP/REDS/placa/processo masking, ATRiAN score 0–100, LGPD disclosure, evidence audit hash
- [x] EGOS-063: Define free vs paid surface for the flagship (open SDK/specs vs hosted API/MCP/audit console)
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/strategy/FREE_VS_PAID_SURFACE.md`
  - **Tiers:** Free (npm SDK) → Starter API R$49/mo → Pro R$199/mo → Business R$499/mo → Enterprise custom
  - **Policy Packs:** Segurança Pública, Saúde, Judiciário, Financeiro (R$2.990/ano each)
  - **Revenue path:** npm→API→Dashboard→Policy Packs over 12 months
- [x] EGOS-064: Deliver the first monetizable surface as a reusable package or MCP before expanding any new product line
  - **Status:** COMPLETE (2026-03-29) — npm-ready, pending `npm publish`
  - **Build:** `tsc -p tsconfig.build.json` → `dist/` (7 JS + 7 .d.ts + source maps)
  - **Standalone:** Inlined modules from @egos/shared → zero workspace dependencies
  - **Known acronyms:** 24 Brazilian govt acronyms pre-loaded (CPF, RG, MASP, REDS, etc.)
  - **Next:** `cd packages/guard-brasil && npm publish --access public` (requires npm login)
- [x] EGOS-073: Run the full `egos-lab` consolidation diagnostic — classify every active surface as `migrate_to_egos`, `keep_in_lab`, `standalone_candidate`, `internal_infra`, `archive`, or `discard`, with source→destination pointers
  - **Status:** COMPLETE (2026-03-29)
  - **Diagnostic:** `docs/strategy/EGOS_LAB_CONSOLIDATION_DIAGNOSTIC.md`
  - **Key findings:** 3 agents → kernel (ssot-auditor, ssot-fixer, drift-sentinel), nexus+nexus-market consolidation needed, shared symlink broken
- [x] EGOS-074: Execute the kernel-first consolidation of SSOT/governance surfaces from `egos-lab` into `egos` — **COMPLETE (2026-03-30)** — `docs/KERNEL_CONSOLIDATION_PLAN.md`: 3-phase plan, boundary contract, 11 apps + 9 agents classified
- [x] EGOS-075: Canonicalize System Map — **COMPLETE (2026-03-30)** — `SYSTEM_MAP.md` v2.4.0: Freshness Rules (7 sections), Cross-Repo Update Flow (8 rules), Machine Map pointer
- [x] EGOS-076: Ecosystem Classification Registry — **COMPLETE (2026-03-30)** — `ECOSYSTEM_CLASSIFICATION_REGISTRY.md` v2.0.0: 7 classes, 50+ surfaces (filesystem-verified), promotion gates
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

- [ ] EGOS-123: `npm publish --access public` for @egosbr/guard-brasil v0.1.0 (**MANUAL — M-001** em MANUAL_ACTIONS.md)
  - Pre-req: `cd packages/guard-brasil && npm login && npm publish --access public`
  - After first publish: create publish credentials in CI secret store (M-006)
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
  - Deployed to Hetzner VPS: port 3098, container `egos-arch`, health check passing
  - Caddy configured: `arch.egos.ia.br` → 127.0.0.1:3098

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

**Staffing Recommendation:**
- **Full-stack developer** (TypeScript + Python + DevOps): Owns end-to-end integration, database, auth, performance
- **Python specialist** (geometry + ML): Owns 3D generation, 2D extraction, video generation
- **Part-time AI expert** (1-2 sprints): Prompt engineering for vision + briefing robustness

**Risk Mitigation:**
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Vision API quota exhaustion | HIGH | Implement request deduplication + caching early (Week 1) |
| 3D model generation slow | MEDIUM | Profile Trimesh early (Week 2); consider simplification algorithm |
| Video generation cost explosion | MEDIUM | Implement short-form default (30s); add user-controlled length setting |
| Sketch quality highly variable | HIGH | Add feedback loop: user can refine sketch if geometry bad |

**Immediate Actions This Week (2026-03-30):**
- [x] Move OpenRouter API key to `.env` — **COMPLETE (2026-03-30)**
- [x] Deploy ARCH to Hetzner VPS (Docker + Caddy) — **COMPLETE (2026-03-30)**
- [ ] Add DNS A record for `arch.egos.ia.br` → 204.168.217.125 (**MANUAL**)
- [ ] Initialize Supabase project and create migrations (3h)
- [ ] Create GitHub project board + link ARCH-001 through ARCH-006 issues

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
- [ ] EGOS-130: Wire Guard Brasil middleware em egos-inteligencia (Python)
  - Dep: EGOS-128 + API DNS ativa (M-002)
  - Criar `etl/src/egos_inteligencia_etl/guard.py` — wrapper HTTP para `POST guard.egos.ia.br/v1/inspect`

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
