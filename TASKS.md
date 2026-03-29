# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.9.0 | **Updated:** 2026-03-29

---

### Summary: Session 2026-03-29 (Test Coverage Sprint + Guard Brasil + Fixes)

**Completed:**
- [x] Test coverage: 43 → 162 tests (12 of 14 shared modules), 372 assertions, 0 failures
- [x] Spec-pipeline E2E: Fixed 13/16 failing tests (label format + SLA stagedAt) → 16/16 passing
- [x] llm-provider: Fixed cost_usd always returning 0 → added MODEL_COSTS map + estimateCost()
- [x] EGOS-062 (partial): Created `guard-brasil.ts` — unified Guard Brasil entry point (ATRiAN + PII + PublicGuard + EvidenceChain)
- [x] CI: Added `bun test` step to GitHub Actions workflow
- [x] package.json: Updated test command to include E2E tests
- [x] Gap analysis: `docs/GAPS_AND_ADVANCEMENT_PLAN.md` — full gap map with advancement plan
- [x] New test files: public-guard, evidence-chain, model-router, rate-limiter, repo-role, llm-provider, metrics-tracker, telemetry, cross-session-memory, guard-brasil

---

### Summary: Session 2026-03-26 (Autonomous Merge + Governance Sync - COMPLETE)

**Completed:**
- [x] PR #4 Merge: Create and organize master plan for EGOS — autonomous merge with conflict resolution
  - **Status:** MERGED & VALIDATED
  - **Commit:** 3932067 (Merge PR #4)
  - **Conflicts Resolved:** 5 files (.guarani/prompts/triggers.json, .windsurf/workflows/start.md, AGENTS.md, docs/SYSTEM_MAP.md, package.json)
  - **Resolution Strategy:** Accepted incoming version (--theirs) for all conflicts — latest PR branch state aligned with governance standards
  - **Validations Passed:**
    - TypeScript type check: ✅ PASSED
    - Test suite: 43 pass, 0 fail ✅ PASSED
    - Governance sync: 2 files synced, 0 drift ✅ PASSED
    - Pre-commit hooks: All 5 checks ✅ PASSED
  - **Governance Status:** Zero drift detected post-merge; synchronized to ~/.egos/ with 45 base files verified
  - **Features Merged:**
    - Cross-repository PR audit script (pr:audit)
    - Canonical mycelium workflow for autonomous governance
    - Global workspace configuration infrastructure
    - Session handoff + environment registry
    - Leaf Governance Audit Pattern from carteira-livre deep audit
  - **Report:** MERGE_REPORT_PR4.md

---

### Summary: Session 2026-03-26 (CI Troubleshooting - COMPLETE)

**Completed:**
- [x] EGOS-122: Fix CI error "frozen zones check exits 128" in `.github/workflows/ci.yml` — root cause: bash syntax error in GitHub Actions variable expansion; applied quickfix to line 50 (added error handling for git diff) + improved messaging
  - **Status:** VALIDATED & LIVE
  - **Commit:** cab3083 (fix(ci): frozen zones check bash syntax error in GitHub Actions)
  - **Changes:** Added error handling to `git diff` command (2>/dev/null || echo "") + improved success messages
  - **Publication:** Pushed to origin/main; PR #5 auto-closed via "Fixes #5" reference
  - **Validation:** CI workflow now handles both PR and push contexts without bash syntax errors

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
- [/] EGOS-062: Package the canonical product boundary for `EGOS Guard Brasil` — ATRiAN + PII Scanner BR + public guard + evidence discipline — `guard-brasil.ts` created with unified `createGuardBrasil()` API; npm publish pending
- [x] EGOS-063: Define free vs paid surface for the flagship — `docs/strategy/GUARD_BRASIL_PRODUCT_BOUNDARY.md` (SDK free/MIT, API/MCP/SLA paid)
- [/] EGOS-064: Deliver the first monetizable surface as a reusable package — `@egos/shared` package.json updated (private:false, metadata, exports); npm publish pending build step + README
- [x] EGOS-073: Run the full `egos-lab` consolidation diagnostic — `docs/strategy/EGOS_LAB_CONSOLIDATION_DIAGNOSTIC.md` (v1.0.0); all surfaces classified; P0 migration actions pending execution in egos-lab repo
- [/] EGOS-074: Execute the kernel-first consolidation — P0 actions documented (remove lab @egos/shared duplicate, merge SYSTEM_MAP, remove stale governance-sync copy); execution requires egos-lab repo access
- [x] EGOS-075: Canonicalize the System Map control plane — `docs/SYSTEM_MAP.md` v3.0.0 rewritten (removed duplicates, stale agents, added Guard Brasil, unified workflow table, 96L clean)
- [x] EGOS-076: Create ecosystem classification registry — `docs/ECOSYSTEM_CLASSIFICATION_REGISTRY.md` (v1.1.0); wired into TASKS.md, SYSTEM_MAP v3.0.0, CAPABILITY_REGISTRY v1.4.0
- [ ] EGOS-077: Add the new-project gate for PRD, ICP, go-to-market, objective, success metric, and multi-model review mode with a recorded blocking-vs-advisory decision
- [x] EGOS-078: Define Agent Claim Contract — `docs/contracts/AGENT_CLAIM_CONTRACT.md` (v1.0.0); L0-L4 taxonomy with proof fields, all 10 agents classified as L2, promotion protocol defined
- [x] EGOS-079: Enforce Agent Claim Gate — enhanced `agent:lint` with L2/L3 validation, entrypoint existence check, eval_suite file verification; 10 agents pass L2, all warned for L3 promotion
- [x] EGOS-080: LLM Orchestration Matrix — `docs/contracts/LLM_ORCHESTRATION_MATRIX.md` (6 lanes, task routing, cost ceilings, cheap-first policy); deprecated `llm-orchestrator.ts` → `model-router.ts` SSOT merge
- [ ] EGOS-093: Define canonical flagship brief in SSOT — objective, problem statement, personas, and GTM with acceptance metrics
- [ ] EGOS-094: Create "Market Intelligence Compiler" spec — ingestion contract for books/papers/code/platforms with source-link + evidence tiers
- [ ] EGOS-095: Build governance rule registry for market practices — normalize global best practices into executable controls and tests
- [ ] EGOS-096: Add cross-environment signature adoption for Google AI Studio lane (commit/push provenance fields mandatory)
- [ ] EGOS-097: Define dissemination protocol (`/disseminate`) for propagating new strategic rules to all mapped repos with drift-proof verification
- [/] EGOS-098: Ingest and operationalize pragmatic multi-agent benchmark patterns (worktree isolation, parallel ticket lanes, QA loop, file-first context) into kernel governance with explicit keep/drop decisions — keep/drop contract drafted + GTM harvester agent added; pending contract enforcement and workflow wiring
- [x] EGOS-099: Worktree Orchestration Contract — superseded by EGOS-110 (`.guarani/orchestration/WORKTREE_CONTRACT.md`)
- [ ] EGOS-100: Define `Linear/Issue Sync Contract` (`/linear-sync`) with task decomposition schema, priority classes, and required evidence at PR gate
- [ ] EGOS-101: Define `QA Loop Contract` (`/qa-loop`) using browser/devtools verification + test rerun policy + stop conditions
- [ ] EGOS-102: Build executable 10-second operator map (replace text-heavy integration map with founder-grade control plane view)
- [x] EGOS-107: Define and activate Stitch-first UI contract (`/stitch`) — prompt generation in EGOS lane, external creation in Google Stitch, and `.zip` intake mapping before implementation
- [ ] EGOS-108: Build `stitch_intake_mapper` agent to parse returned `.zip`, generate mapping table, and create integration tasks automatically
- [x] EGOS-109: Run full AIOX (`SynkraAI/aiox-core`) gem diagnosis against EGOS + NotebookLM export and codify keep/drop recommendations
- [x] EGOS-110: Implement `Worktree Orchestration Contract` from AIOX/workflow benchmark — **COMPLETE**
  - **Contract Document:** `.guarani/orchestration/WORKTREE_CONTRACT.md` (v1.0.0) — formal spec with naming rules (regex), ownership model, lifecycle state machine, merge gates, concurrency limits (max 5), and JSON report schema
  - **Validation Script:** `scripts/worktree-validator.ts` — enforces branch naming, ownership locks, frozen zone checks, lifecycle validation, and concurrency limits; supports --pre-commit, --ci, --status, --cleanup modes
  - **Metadata Registry:** `.guarani/worktrees.json` — ownership tracking with created_at, last_commit, status, files_touched, issue_link per worktree
  - **Functional Examples:** 4 active worktrees recorded (feature/worktree-validator, fix/ci-error-frozen-zones, docs/orchestration-guide, test/worktree-validation-examples)
  - **Integration:** Added to `/start` GATE phase as pre-flight check (Worktree Orchestration Check — EGOS-110)
  - **Validation:** Tested --status and --count-active modes; concurrency count working (2/5 active)
  - **Blockers:** EGOS-111 now unblocked (depends on worktree contract)
- [x] EGOS-111: Implement Spec-Pipeline Workflow Contract (analyst → pm → architect → sm) — **COMPLETE**
  - **Contract Document:** `.guarani/orchestration/SPEC_PIPELINE_CONTRACT.md` (v1.0.0) — formal spec with 4-stage workflow, RBAC by role, mandatory field validation, approval gates (min 2 reviewers per stage, 1 for SM), SLA tracking (24h per stage), handoff format with evidence requirements, and blocking criteria
  - **Router Agent:** `agents/agents/spec-router.ts` — validates mandatory fields, detects current stage, routes to next reviewer, tracks SLA violations, generates merge-block reasons, supports validate/route/sla-check/advance modes
  - **GitHub Actions Workflow:** `.github/workflows/spec-pipeline.yml` — trigger on label, validate fields, route to reviewers, track SLA hourly, auto-transition stages, post handoff comments, enforce merge gate
  - **E2E Test Suite:** `tests/spec-pipeline.e2e.test.ts` — 5 complete scenarios covering analyst→pm→architect→sm workflow, validation blocking, SLA tracking (OK/WARNING/EXCEEDED), stage routing, and edge cases
  - **Documented Example:** `docs/examples/spec-pipeline-example.md` — full walkthrough of 2FA feature through all 4 stages with real evidence links, handoff comments, and timing (11h total)
  - **Validation:** Merge gate blocks incomplete specs; SLA violations flagged but non-blocking; evidence-first design ensures quality
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
- [x] EGOS-116: Presentation System SSOT — 5 docs exist (PRESENTATION_IDENTITY, VALUES, VISUAL_IDENTITY, COMPETITIVE_ANALYSIS, INDEX) totaling 1,898 lines; needs SSOT Registry entry
- [x] EGOS-117: Operator narrative kit — `docs/strategy/OPERATOR_NARRATIVE_KIT.md` (1-page pitch with problem/solution/numbers/personas, derived from PRESENTATION_IDENTITY SSOT)
- [x] EGOS-118: Reproducible demo lane — `bun demo` (Guard Brasil + agent runtime + LLM routing), offline-capable, deterministic, with `--guard`/`--agents`/`--routing` flags
- [x] EGOS-119: Benchmark scorecard — `bun benchmark` compares EGOS vs LangChain/CrewAI/AutoGen/Cursor across 6 categories (governance, multi-repo, compliance, cost, tests, runtime); EGOS scores 50/60
- [ ] EGOS-120: Define visual identity/application rules for docs and generated artifacts (consistency pack)
- [ ] EGOS-121: Add monthly "clarity review" gate to prune complexity and keep kernel message/simple architecture coherent
- [x] EGOS-083: Create the canonical cross-repo SSOT registry in the kernel and define the ownership contract for `kernel_canonical`, `leaf_local`, and `shared_home` surfaces
- [x] EGOS-084: Extend kernel governance sync + pre-commit to cover canonical SSOT docs (`SSOT_REGISTRY`, `CAPABILITY_REGISTRY`, `CHATBOT_SSOT`) and sync them to `~/.egos/docs`
- [ ] EGOS-085: Roll out the SSOT registry adoption plan across mapped repos — each leaf must declare local SSOT pointers, freshness rules, and task-level migration status
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

> **Directive:** Until EGOS-062..064 are resolved, new work should strengthen the flagship guardrails product or its proof cases only.

## Benchmark Alignment Plan (2026-03-26)

**Goal:** absorb only what is useful from external multi-agent workflows and discard ornamental complexity.

### Keep (Implement)
- Worktree-isolated parallel execution.
- File-first context persistence (not opaque memory dependence).
- QA loop as a first-class gate (browser + tests + evidence).
- Clear operator control plane with low cognitive load.

### Drop (Do Not Implement)
- Platform lock-in orchestration dependencies as core runtime requirement.
- Non-executable philosophical layers mixed into production policy gates.
- Expensive infrastructure dependencies before first flagship monetization proof.

### Execution Order
1. EGOS-098 (keep/drop codification)
2. EGOS-099 (worktree contract)
3. EGOS-100 (ticket sync contract)
4. EGOS-101 (qa loop contract)
5. EGOS-102 (10-second operator map)

## Grok Intake Queue (Temporary Kernel Inbox)

> Use this queue to capture tasks extracted from external Grok conversations immediately, even before target-repo routing is finalized.

- [ ] EGOS-103: Define `GROK_TASK_INTAKE` template (source link, quote/snippet, intended repo, impact, effort, confidence, owner) for deterministic ingestion.
- [ ] EGOS-104: Build cross-repo task router policy (`target_repo` tag + migration rule) so kernel can hold temporary tasks and later move them to the correct repository.
- [ ] EGOS-105: Ingest latest Grok conversation backlog into temporary kernel queue with deduplication against existing EGOS/FORJA/egos-lab tasks.
- [ ] EGOS-106: Execute migration pass from temporary kernel queue to destination repos (`egos`, `egos-lab`, `FORJA`, `EGOS-Inteligencia`) with status sync proof.

### P0 (Blockers)

- [x] EGOS-001: Create clean repo structure with governance from commit 0
- [x] EGOS-002: Initialize git + first commit with all SSOT files
- [x] EGOS-003: Connect to GitHub (github.com/enioxt/egos) and push
- [x] EGOS-041: Align `/start` with core repo reality — remove or gate stale checks for `docs/SYSTEM_MAP.md`, `session:guard`, `docs/gem-hunter`, and `docs/reports`
- [x] EGOS-042: Create canonical core system-map surface and wire `/start` to it (`docs/SYSTEM_MAP.md` or an explicit repo-local equivalent)
- [x] EGOS-043: Restore/add `.windsurf/workflows/mycelium.md` or remove stale Mycelium workflow references across `/start`, `/end`, and Mycelium docs
- [x] EGOS-044: Create `docs/knowledge/HARVEST.md` or relax `/end` and `/disseminate` assumptions to match the current core repo
- [x] EGOS-056: Propagate updated kernel workflows into `~/.egos/workflows` and downstream synced repos, then rerun `bun run governance:check`

### P1 (Critical)

- [x] EGOS-004: Run `bun install` and validate `tsc --noEmit` passes
- [x] EGOS-005: Validate pre-commit hooks work (gitleaks + tsc + frozen)
- [x] EGOS-006: Update `~/.egos/SYSTEM_MAP.md` to include `egos` root
- [x] EGOS-007: Create `.egos` symlink to shared governance home
- [x] EGOS-081: Create cross-session memory module in @egos/shared — ported from 852, generalized for ecosystem reuse
- [x] EGOS-082: Create comprehensive metrics tracking system — tracks Codex, Alibaba, Claude Code, OpenRouter, Cascade usage with costs and performance
- [x] EGOS-045: Refresh `.guarani/orchestration/DOMAIN_RULES.md` from `egos-lab` assumptions to kernel reality (`egos`, leaf repos, `llm-provider.ts`)
- [x] EGOS-046: Validate Codex cloud + Alibaba live readiness for `egos` core and record evidence in workflows/handoff
- [x] EGOS-047: Fix missing `docs/META_PROMPT_ECOSYSTEM_AUDIT.md` reference — created `meta/ecosystem-audit.md` + fixed stale refs in `PROMPT_SYSTEM.md`
- [x] EGOS-048: Align Mycelium docs with actual core artifacts — created `packages/shared/src/mycelium/reference-graph.ts` (27 nodes, 32 edges)
- [x] EGOS-058: Consolidate `.env` credentials from ecosystem repos (egos-lab, 852, br-acc, policia) into kernel `.env` — 14 vars, all providers live
- [x] EGOS-059: Create `packages/shared/src/mycelium/reference-graph.ts` — Phase 1 canonical schema + kernel seed graph + utilities
- [x] EGOS-055: Add `.env.example` for kernel-level provider and sync expectations (`ALIBABA_DASHSCOPE_API_KEY`, `OPENROUTER_API_KEY`, optional GitHub/Codex hints)
- [x] EGOS-057: Create task-aware model router (`packages/shared/src/model-router.ts`) with 8 models, 3 cost tiers, 10 task types

### P2 (Important)

- [x] EGOS-008: Write comprehensive README.md with install instructions
- [x] EGOS-009: Set up GitHub Actions CI (lint + typecheck + registry lint)
- [x] EGOS-010: Create CONTRIBUTING.md with governance rules
- [x] EGOS-011: Migrate first agent from egos-lab as proof-of-concept
- [x] EGOS-049: Create repo-role-aware activation logic — `egos.config.json` + `repo-role.ts` + heuristic fallback
- [x] EGOS-050: Create `activation:check` command for the core repo — 42 checks, 100% pass rate
- [/] EGOS-051: Migrate core-safe agents from egos-lab — `dead_code_detector` migrated (5 kernel agents now); SSOT Auditor + Contract Tester need generalization (medium-term)
- [x] EGOS-052: Document the kernel-to-leaf migration matrix — `docs/strategy/MIGRATION_MATRIX.md`

### P2 (Important) — Archaeology Sprint

- [x] EGOS-017: Build interactive evolution tree (Tree of Life) — `docs/evolution-tree.html`
- [x] EGOS-018: Create archaeology_digger agent — `agents/agents/archaeology-digger.ts`
- [x] EGOS-019: Migrate Mycelium docs to egos kernel — `docs/concepts/mycelium/`
- [x] EGOS-020: Feature evolution categorization — `docs/archaeology/FEATURE_EVOLUTION_CATEGORIZATION.md`
- [x] EGOS-021: Run archaeology agent (execute) — 220 events, 31 agents, 42 handoffs, 7 breakpoints
- [x] EGOS-022: Validation sweep — tsc OK, registry lint OK, SSOT limits OK, frozen zones intact

### P1 (Critical) — SSOT Distillation Sprint

- [x] EGOS-025: Analyze 852 chatbot — extract quality patterns (memory, ATRiAN, prompt, PII, routing)
- [x] EGOS-026: Analyze Forja documentation — mobile CRM chatbot-first plan, architecture, stack
- [x] EGOS-027: Create `docs/modules/CHATBOT_SSOT.md` — canonical chatbot standard from 852
- [x] EGOS-028: Create `docs/CAPABILITY_REGISTRY.md` — full ecosystem capability map with tags/refs
- [x] EGOS-029: Update `/start`, `/end`, `/disseminate` workflows with capability map references
- [x] EGOS-030: Port ATRiAN validation layer to `packages/shared/` as reusable module
- [x] EGOS-031: Port PII scanner to `packages/shared/` as reusable module
- [x] EGOS-032: Port conversation memory pattern to `packages/shared/` as reusable module
- [x] EGOS-033: Create chatbot-compliance-checker agent (validates projects against CHATBOT_SSOT)

### P2 (Important) — Observability & Context

- [x] EGOS-060: Context Tracker agent — CTX score 0-280, zone emojis, auto /end trigger at 250+, wired into .windsurfrules + AGENTS.md + HARVEST.md

### P2 (Important) — Replication & Adoption

- [x] EGOS-034: Forja — production parity hardened with rate limiter, `.env.example`, `.husky/pre-commit`; capability drift 100% and chatbot SSOT 100/100
- [x] EGOS-035: carteira-livre — backfill ATRiAN + PII scanner + memory modules
- [x] EGOS-036: intelink — backfill ATRiAN + memory modules
- [x] EGOS-037: Research go-to-market theories for code/framework validation — `docs/strategy/GO_TO_MARKET_RESEARCH.md`
- [x] EGOS-038: Create capability-drift-checker agent (15 checks, kernel 100%, carteira-livre 93%)
- [x] EGOS-039: egos-web — aligned public chat with shared ATRiAN/PII/memory modules; build OK and chatbot SSOT 100/100
- [x] EGOS-040: br-acc — Python adapter/bridge added for CHATBOT_SSOT; py_compile OK and chatbot SSOT 100/100
- [x] EGOS-065: Stop legacy `.windsurfrules` symlink mutation in `~/.egos/governance-symlink.sh` and classify the script as legacy cleanup only
  > **Arquivos:** `~/.egos/governance-symlink.sh`, `docs/CAPABILITY_REGISTRY.md`
- [x] EGOS-066: Remove remaining stale claims/docs that still present `governance-symlink.sh` as the primary sync path instead of the kernel sync plane
  > **Arquivos:** `docs/diagnostics/SITE_AND_GOVERNANCE_DIAGNOSTIC_2026-03-13.md`, `.guarani/orchestration/DOMAIN_RULES.md`
- [x] EGOS-067: Define the hybrid multi-tool control plane for `Claude Code` + `Codex` + Alibaba + Antigravity with user-scope secrets and repo-local onboarding
  > **Arquivos:** `egos-lab/docs/plans/MULTI_TOOL_HUB.md`, `~/.claude.json`

### Backlog

- [ ] EGOS-012: Publish `@egos/shared` to npm (when stable)
- [x] EGOS-081: Create Oracle Cloud instance launcher utility (Python SDK) under `scripts/oracle-instance-launcher/` with API-key/instance-principal auth, AD retry, capacity-aware handling, and systemd-ready runner
  > **Arquivos:** `scripts/oracle-instance-launcher/README.md`, `scripts/oracle-instance-launcher/.env.example`, `scripts/oracle-instance-launcher/src/*.py`, `scripts/oracle-instance-launcher/scripts/*.sh`, `scripts/oracle-instance-launcher/oracle-instance-launcher.service`
- [x] EGOS-013: Create `egos-init` one-command installer
- [ ] EGOS-014: Add VRCP Coherence Model integration
- [ ] EGOS-015: Context Doctor agent (from conversaGROK ideas)
- [x] EGOS-016: Review remaining workflow overrides in leaf repos after SSOT rollout — `docs/reports/workflow-override-audit.md`
- [ ] EGOS-023: Publish egos-init via hosted installer URL
- [ ] EGOS-024: Full per-agent lineage matrix (ARCH-003) — continue with commit-level tracing
- [ ] EGOS-053: Build cross-repo capability compliance dashboard for kernel and leaf adoption state
- [x] EGOS-054: Make `/end` and `/disseminate` repo-role-aware — `egos.config.json` detection in Phase 1, conditional surface gating
- [ ] EGOS-068: Enforce shared workflow inheritance across mapped repos — re-link exact-match copies, replace stale overrides with thin wrappers or shared workflows, and preserve only justified repo-local exceptions
- [ ] EGOS-069: Bootstrap `santiago` into the EGOS governance mesh with `.egos`, repo-local SSOT files, and inherited core workflows
- [ ] EGOS-070: Complete Mycelium truth repair — align kernel docs and reference graph with actual local surfaces and classify consumer dashboards/bridges as external or planned
- [x] EGOS-071: Cheap-first orchestration — default CostPreference changed from 'balanced' to 'economy' in model-router.ts; 4 new tests verify policy; LLM_ORCHESTRATION_MATRIX.md (EGOS-080) defines full lane routing
- [ ] EGOS-072: Design anti-injection and least-privilege hardening for external-input workflows (issues, PRs, web, imported docs) before any high-trust automation
- [ ] EGOS-086: Extract circuit breaker pattern from carteira-livre guardrails into `@egos/shared` as reusable module
- [ ] EGOS-087: Build `@egos/mcp-governance` — custom MCP server for SSOT drift check, task listing, and deploy gates across all repos
- [ ] EGOS-088: Build `@egos/mcp-memory` — custom MCP server for persistent conversation memory (Supabase/Redis backend, recall/store/search tools)
- [ ] EGOS-089: Bridge Mycelium event bus to Redis Pub/Sub for cross-process agent communication (Phase 2 of MYCELIUM_NETWORK.md)
- [ ] EGOS-090: Build first domain-specific MCP server (forja `@egos/mcp-erp` or carteira-livre `@egos/mcp-marketplace`) as proof-of-concept
- [ ] EGOS-091: Add MCP server auto-discovery and health heartbeats to agent registry for plug-and-play tool management
- [ ] EGOS-092: Ensure all leaf repos consume `@egos/shared` for ATRiAN/PII/memory instead of maintaining local copies

### SSOT Core Infra (v2)
- [ ] SSOT-v2-01: Monitor usage and stability of the PM2 daemon (`egos-ssot`) locally and propagate to Contabo VPS.
- [ ] SSOT-v2-02: Activate `ssot_auditor` AST drift scanner in CI/CD pipeline (`egos-lab` GitHub Actions or VPS Webhook) to block structurally drifting PRs.
- [ ] SSOT-v2-03: Develop `ssot-package-auditor.ts` (or expand `sync.sh` jq rules) to enforce structural compliance across `package.json` vs `.egos/standards` map.

## Roadmap — Progress Dashboard

### Overall Progress

| Horizon | Total | Done | Open | Progress |
|---------|-------|------|------|----------|
| **Foundation (P0/P1)** | 21 | 21 | 0 | **100%** |
| **Replication (P2)** | 15 | 15 | 0 | **100%** |
| **Backlog** | 20 | 3 | 17 | **15%** |
| **Test Sprint** | 5 | 5 | 0 | **100%** |
| **TOTAL** | **61** | **47** | **14** | **77%** |

---

### Active Roadmap (see tasks above for full status — no duplicates)

**Short Term:** EGOS-064 (npm publish), EGOS-068 (workflow inheritance), EGOS-072 (anti-injection)
**Medium Term:** EGOS-087/088 (MCP servers), EGOS-053 (compliance dashboard), EGOS-092 (leaf @egos/shared adoption)
**Long Term:** EGOS-012 (npm @egos/shared), EGOS-089 (Mycelium Redis), EGOS-014 (VRCP), community adoption
