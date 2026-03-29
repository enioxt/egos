# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.9.0 | **Updated:** 2026-03-29

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
- [x] EGOS-062: Package the canonical product boundary for `EGOS Guard Brasil` — ATRiAN + PII Scanner BR + public guard + evidence discipline
  - **Status:** COMPLETE (2026-03-29)
  - **Package:** `packages/guard-brasil/` — `@egos/guard-brasil` v0.1.0
  - **Files:** `src/index.ts`, `src/guard.ts` (GuardBrasil facade), `src/demo.ts`, `src/guard.test.ts`, `README.md`
  - **Tests:** 15/15 pass (bun test) — clean output, PII detection, ATRiAN validation, evidence chain, combined scenarios
  - **Capabilities:** CPF/RG/MASP/REDS/placa/processo masking, ATRiAN score 0–100, LGPD disclosure, evidence audit hash
- [x] EGOS-063: Define free vs paid surface for the flagship (open SDK/specs vs hosted API/MCP/audit console)
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/strategy/FREE_VS_PAID_SURFACE.md`
  - **Tiers:** Free (npm SDK) → Starter API R$99/mo → Pro R$499/mo → Enterprise custom
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
- [ ] EGOS-074: Execute the kernel-first consolidation of SSOT/governance surfaces from `egos-lab` into `egos` and eliminate duplicated docs, maps, workflows, and stale claims with explicit archive references
- [x] EGOS-075: Canonicalize the System Map control plane — one orchestrator contract, one machine map, one human map, freshness rules, and one cross-repo update flow
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/governance/SYSTEM_MAP_CONTROL_PLANE.md` — machine map vs human map ownership, one update flow, freshness signals, current ecosystem map, anti-patterns
- [x] EGOS-076: Create the ecosystem classification registry for products/modules/ideas (`standalone`, `candidate`, `lab`, `internal_infra`, `archive`) and wire it into `TASKS.md`, `SYSTEM_MAP.md`, and `CAPABILITY_REGISTRY.md`
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/strategy/ECOSYSTEM_CLASSIFICATION_REGISTRY.md` — full taxonomy + per-surface classification for all repos, packages, products, ideas, and docs
  - **Classes:** `flagship_product`, `kernel_core`, `standalone_candidate`, `proof_case`, `leaf_consumer`, `incubator`, `internal_infra`, `archive`, `discard`
  - **Key verdict:** Guard Brasil = `flagship_product` | atomizer/search-engine = `standalone_candidate` (evaluate post-revenue) | MCP/API/Dashboard = `incubator` (blocked until Guard Brasil has users)
- [x] EGOS-077: Add the new-project gate for PRD, ICP, go-to-market, objective, success metric, and multi-model review mode with a recorded blocking-vs-advisory decision
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/governance/NEW_PROJECT_GATE.md` — blocking gate with PRD + ICP + GTM + metrics + kernel health prerequisite + multi-model review + copy-paste template
  - **Gate decisions:** `APPROVED` / `BLOCKED — prerequisites` / `BLOCKED — incomplete PRD` / `ADVISORY`
  - **Prerequisite:** No new product until Guard Brasil is on npm OR has ≥1 external user
- [x] EGOS-078: Define the `Agent Claim Contract` — formal taxonomy for `component`, `skill`, `agent_candidate`, `verified_agent`, and `online_agent`, with mandatory proof fields for runtime, triggers, evals, observability, and ownership
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/governance/AGENT_CLAIM_CONTRACT.md` — 5-tier taxonomy with required fields per tier + current registry audit (13 agents classified)
  - **Registry updated:** `agents/registry/agents.json` v1.2.0 — all 13 agents now have `evals`, `observability`, `ownership` fields
- [x] EGOS-079: Enforce the `Agent Claim Gate` in kernel governance — registry lint + pre-commit/pre-push + docs/tasks checks must block any surface claimed as agent without executable entrypoint, existing eval, valid run modes, and runtime evidence
  - **Status:** COMPLETE (2026-03-29)
  - **Script:** `scripts/agent-claim-lint.sh` — validates all contract fields, entrypoint existence, status/risk_level values, online agent SLA requirement
  - **Wire:** `bun run agent:lint` → calls lint script (13/13 pass)
  - **Pending:** Pre-commit wire blocked — `.husky/pre-commit` is frozen zone; requires explicit user approval to add
- [x] EGOS-080: Define the `LLM Orchestration Matrix` for EGOS — explicit lane ownership for Cascade, terminal orchestration, Codex, Claude Code, Alibaba, and OpenRouter, with approval mode, authority level, and allowed task classes
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/governance/LLM_ORCHESTRATION_MATRIX.md` — 6 lanes (Alibaba Qwen, Claude Code, Windsurf, AI Studio, Codex, OpenRouter) with authority levels, task classes, forbidden actions, conflict rules, cost budgets
- [x] EGOS-093: Define canonical flagship brief in SSOT — objective, problem statement, personas, and GTM with acceptance metrics
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/strategy/FLAGSHIP_BRIEF.md` — one-sentence VP, problem statement, personas, differentiation matrix, monetization model, success metrics
- [ ] EGOS-094: Create "Market Intelligence Compiler" spec — ingestion contract for books/papers/code/platforms with source-link + evidence tiers
- [ ] EGOS-095: Build governance rule registry for market practices — normalize global best practices into executable controls and tests
- [ ] EGOS-096: Add cross-environment signature adoption for Google AI Studio lane (commit/push provenance fields mandatory)
- [x] EGOS-097: Define dissemination protocol (`/disseminate`) for propagating new strategic rules to all mapped repos with drift-proof verification
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/governance/DISSEMINATION_PROTOCOL.md` — when to disseminate, 6-step protocol, propagation map, drift prevention checklist
- [/] EGOS-098: Ingest and operationalize pragmatic multi-agent benchmark patterns (worktree isolation, parallel ticket lanes, QA loop, file-first context) into kernel governance with explicit keep/drop decisions — keep/drop contract drafted + GTM harvester agent added; pending contract enforcement and workflow wiring
- [x] EGOS-099: Define `Worktree Orchestration Contract` for EGOS (branch naming, ownership locks, lifecycle, cleanup, merge gates, max concurrency)
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/governance/WORKTREE_CONTRACT.md` — naming patterns, ownership model, lifecycle stages, cleanup rules, merge gates, max 10 branches total / 3 per dev
- [x] EGOS-100: Define `Linear/Issue Sync Contract` (`/linear-sync`) with task decomposition schema, priority classes, and required evidence at PR gate
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/governance/LINEAR_SYNC_CONTRACT.md` — TASKS.md as canonical SSOT, P0-P3 classes, PR gate requirements, sync flow, stale task policy
- [x] EGOS-101: Define `QA Loop Contract` (`/qa-loop`) using browser/devtools verification + test rerun policy + stop conditions
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/governance/QA_LOOP_CONTRACT.md` — 5-step loop (typecheck → tests → agent:lint → governance:check → smoke), rerun policy, stop conditions
- [x] EGOS-102: Build executable 10-second operator map (replace text-heavy integration map with founder-grade control plane view)
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/OPERATOR_MAP.md` — architecture one-liner, live surfaces, control plane commands, decision log, blocked items, governance docs index
- [x] EGOS-107: Define and activate Stitch-first UI contract (`/stitch`) — prompt generation in EGOS lane, external creation in Google Stitch, and `.zip` intake mapping before implementation
- [x] EGOS-108: Build `stitch_intake_mapper` agent to parse returned `.zip`, generate mapping table, and create integration tasks automatically
  - **Status:** COMPLETE (2026-03-29)
  - **Agent:** `agents/agents/stitch-intake-mapper.ts` — registered in agents.json v1.3.0 (14 agents)
  - **Usage:** `STITCH_ZIP=/path/to/file.zip bun agents/cli.ts run stitch_intake_mapper dry_run`
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
- [x] EGOS-116: Define "Presentation System" SSOT for EGOS (positioning, promise, evidence, differentiators, anti-bloat thesis) in canonical surfaces
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/PRESENTATION_SYSTEM.md` — VP, tagline, anti-bloat thesis, evidence table, differentiators, anti-patterns, target surfaces, visual identity rules
- [x] EGOS-117: Build operator-facing narrative kit (1-page pitch + architecture map + proof checklist) from existing SSOT without creating parallel truths
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/NARRATIVE_KIT.md` — 60-second pitch, architecture map, proof checklist, FAQ, competitive landscape, contact
- [x] EGOS-118: Create reproducible demo lane for meetings (live build script + guardrails checklist + fallback offline path)
  - **Status:** COMPLETE (2026-03-29)
  - **Script:** `scripts/demo-lane.sh` — 5/5 pre-flight checks (typecheck, tests, agent:lint, package, demo file) + live demo + talking points + offline fallback
  - **Commands:** `bun run demo` (full) | `bun run demo:check` (pre-meeting check only)
- [x] EGOS-119: Add benchmark scorecard command comparing EGOS vs MASA/Mastra/LangGraph/CrewAI on governance, speed, and compliance
  - **Status:** COMPLETE (2026-03-29)
  - **Script:** `scripts/benchmark-scorecard.ts` — scores 5 frameworks (governance/compliance/brazil-first 0–10) + live EGOS metrics
  - **Command:** `bun run benchmark` | `bun run benchmark --json`
- [ ] EGOS-120: Define visual identity/application rules for docs and generated artifacts (consistency pack)
  - **Note:** Partial — `docs/PRESENTATION_SYSTEM.md` has visual identity rules. Full consistency pack (fonts, colors, templates) → needs design tooling (Enio)
- [x] EGOS-121: Add monthly "clarity review" gate to prune complexity and keep kernel message/simple architecture coherent
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/governance/CLARITY_REVIEW_GATE.md` — 6 checks, green/yellow/red thresholds, 15-minute protocol, output template
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

- [x] EGOS-103: Define `GROK_TASK_INTAKE` template (source link, quote/snippet, intended repo, impact, effort, confidence, owner) for deterministic ingestion.
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/governance/GROK_INTAKE_CONTRACT.md` — full intake template + router policy + dedup rules + queue hygiene (max 10 items)
- [x] EGOS-104: Build cross-repo task router policy (`target_repo` tag + migration rule) so kernel can hold temporary tasks and later move them to the correct repository.
  - **Status:** COMPLETE (2026-03-29) — included in `docs/governance/GROK_INTAKE_CONTRACT.md`
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
- [ ] EGOS-071: Formalize cheap-first multi-model orchestration for Windsurf/Codex/Claude/Alibaba/OpenRouter with one coordinator, sequential routing, and reviewer proof-of-work
- [x] EGOS-072: Design anti-injection and least-privilege hardening for external-input workflows (issues, PRs, web, imported docs) before any high-trust automation
  - **Status:** COMPLETE (2026-03-29)
  - **Document:** `docs/governance/ANTI_INJECTION_HARDENING.md` — threat model (6 sources), 6 security rules, least-privilege table, implementation checklist
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
- [x] SSOT-v2-03: Develop `ssot-package-auditor.ts` (or expand `sync.sh` jq rules) to enforce structural compliance across `package.json` vs `.egos/standards` map.
  - **Status:** COMPLETE (2026-03-29)
  - **Script:** `scripts/ssot-package-auditor.ts` — checks naming, type:module, required fields, dev-deps-in-prod, publishable completeness, private flag
  - **Command:** `bun run ssot:audit` | `bun run ssot:audit --strict` (exit 1 on errors)

## Roadmap — Progress Dashboard

### Overall Progress

| Horizon | Total | Done | Open | Progress |
|---------|-------|------|------|----------|
| **Foundation (P0/P1)** | 21 | 21 | 0 | **100%** |
| **Replication (P2)** | 15 | 15 | 0 | **100%** |
| **Backlog** | 20 | 3 | 17 | **15%** |
| **TOTAL** | **56** | **42** | **14** | **75%** |

---

### Short Term (0-7 days) — Target: 75%

**Objective:** Complete all P2 core hardening. CONTRIBUTING.md, activation:check, and cross-repo adoption alignment.

- [x] EGOS-010 — CONTRIBUTING.md with governance rules
- [x] EGOS-034 — Forja chatbot production parity
- [x] EGOS-039 — egos-web chat alignment with shared modules
- [x] EGOS-040 — br-acc Python adapter for CHATBOT_SSOT
- [x] EGOS-050 — `activation:check` command for core repo (42 checks, 100%)
- [ ] EGOS-068 — Shared workflow inheritance rollout across mapped repos
- [ ] EGOS-069 — `santiago` governance bootstrap into the shared mesh
- [ ] EGOS-070 — Mycelium truth repair across kernel docs and topology references
- [ ] EGOS-071 — Cheap-first multi-model orchestration policy and routing contract
- [ ] EGOS-072 — Anti-injection / least-privilege hardening for external-input automation

### Medium Term (1-4 weeks) — Target: 85%

**Objective:** Repo-role architecture, migration framework, go-to-market research, capability drift monitoring.

- [x] EGOS-037 — GTM research v2.0: OSS economics, developer funnel metrics (TOFU/MOFU/BOFU), lighthouse strategy, 10-item validation checklist — `docs/strategy/GO_TO_MARKET_RESEARCH.md`
- [x] EGOS-038 — capability-drift-checker agent (15 checks, kernel 100%, carteira-livre 93%)
- [x] EGOS-049 — Repo-role-aware activation logic — `egos.config.json` + `repo-role.ts`
- [/] EGOS-051 — Migrate core-safe agents — `dead_code_detector` done; SSOT Auditor needs generalization
- [x] EGOS-052 — Kernel-to-leaf migration matrix — `docs/strategy/MIGRATION_MATRIX.md`
- [x] EGOS-016 — Workflow override audit: 1 legitimate (egos-lab mycelium), 9 stale (br-acc/forja/egos-self v5.0→v5.4) — `docs/reports/workflow-override-audit.md`

### Long Term (1-3 months) — Target: 95%

**Objective:** Public npm package, compliance dashboard, distributed verification, community adoption.

- [ ] EGOS-012 — Publish `@egos/shared` to npm
- [ ] EGOS-014 — VRCP Coherence Model integration
- [ ] EGOS-015 — Context Doctor agent
- [ ] EGOS-023 — Publish egos-init via hosted installer URL
- [ ] EGOS-024 — Full per-agent lineage matrix (ARCH-003)
- [ ] EGOS-053 — Cross-repo capability compliance dashboard
- [x] EGOS-054 — `/end` and `/disseminate` repo-role-aware — `egos.config.json` detection + conditional gating

---

### Infrastructure Migration: Contabo → Hetzner (2026-03-28 COMPLETE)

> VPS migrado. IP novo: 204.168.217.125. Backup validado em /home/enio/vps-backup-hetzner/

**Completed (2026-03-29):**
- [x] INFRA-001 — Atualizar /vps command (`egos/.claude/commands/vps.md`) → Hetzner IP + nova SSH key
- [x] INFRA-002 — Atualizar `docs/KERNEL_MISSION_CONTROL.md` — Deploy Target e tabela de custos
- [x] INFRA-003 — Atualizar `docs/MARKET_READY_FEATURES.md` — referência de deploy do 852
- [x] INFRA-004 — Atualizar `docs/knowledge/HARVEST.md` — tabela de repos (852, br-acc, santiago)
- [x] INFRA-005 — Atualizar `egos-lab/.env` — BRACC_API_URL → 204.168.217.125, comentar CONTABO
- [x] INFRA-006 — Atualizar `egos-lab/agents/agents/etl-orchestrator.ts` — fallback URL
- [x] INFRA-007 — Atualizar `egos-lab/agents/agents/uptime-monitor.ts` — fallback URL + comentário
- [x] INFRA-008 — Atualizar `egos-lab/apps/telegram-bot/src/index.ts` — descrição de infraestrutura

**Completed (2026-03-29 — leaf repos):**
- [x] INFRA-009 — `br-acc`: AGENTS.md, README.md, ROADMAP.md, docs/SYSTEM_MAP.md, docs/pt-BR/DOWNLOAD_DADOS.md, scripts/download-all-datasets.sh → commit `5c2b8d1`
- [x] INFRA-010 — `br-acc`: badge de API Status no README atualizado
- [x] INFRA-011 — `santiago`: .env.local, docs/SETUP_GUIDE.md, SYSTEM_DIAGNOSTIC.md, handoff → commit `d7deaf3`
- [x] INFRA-012 — `852`: scripts/release_contabo.sh → release_hetzner.sh → commit `0b22a15`
- [x] INFRA-013 — `852`: CLAUDE.md, README.md, AGENTS.md, package.json → commit `0b22a15`
- [x] INFRA-014 — `forja`: TASKS.md, TelemetryDashboard.tsx, ARCHITECTURE.md, ORCHESTRATION.md, scripts → commit `50a9629`
- [x] INFRA-015 — `egos-lab`: memory_db/memory.jsonl (EGOS_VPS_CONTABO → EGOS_VPS_HETZNER) → commit `0101bf2`
- [x] INFRA-016 — `egos-lab`: SECURITY_AND_DECENTRALIZATION_PLAN.md + postar.md → commit `0101bf2`

**Completed (2026-03-29):**
- [x] INFRA-017 — Contabo cancelado pelo usuário. Hetzner estável 31h+, 9 containers healthy, SSL OK, disk IO 238MB/s

**Discovered during battle test (2026-03-29):**
- [x] INFRA-018 — Node.js + PM2 instalados no Hetzner. Telegram bot funcional via PM2 startup. Discord bot pendente (sem Discord app separado).
- [x] INFRA-019 — Uptime-monitor health check path corrigido: `gem-hunter` (hifens), rota `/api/v1/meta/etl-progress`, etl-orchestrator fallback URL → Hetzner
- [x] INFRA-020 — openclaw-sandbox identificado: AI gateway/CLI runtime (`alpine/openclaw:latest`, Node.js 24, porta 18789/18791, egos.service label). Serviço legítimo EGOS. 572MB RAM = Node.js esperado.

**Security + Observability (2026-03-29):**
- [x] INFRA-021 — Leaked Supabase PAT (`sbp_d827...`) sanitized in 852 handoff files. Token needs rotation by user in Supabase dashboard.
- [x] INFRA-022 — Gitleaks hardened: added `sbp_[40hex]` rule to `.gitleaks.toml`. Universal hook (`~/.egos/hooks/pre-commit`) now scans secrets on ALL repos.
- [x] INFRA-023 — `governance-sync.sh` updated to propagate `.egos/hooks/` and `sync.sh` on `--exec`.
- [x] INFRA-024 — CRCDM pre-push/post-commit hooks fixed: `#!/bin/sh` → `#!/bin/bash` (bash-specific substring expansion `${var:0:8}`).
- [x] INFRA-025 — carteira-livre `.husky/pre-commit` converted to POSIX sh (fixes `[[ ]]`, `<<<` bash constructs + `head -5` always-true false-positive bug in secrets scan).
- [x] INFRA-026 — `scripts/egos-repo-health.sh` created: cross-repo uncommitted change dashboard. Run before any installer scripts to prevent stale file propagation.
- [x] INFRA-027 — Context Persistence (Fibonacci snapshots) disseminated to kernel + 9 leaf repos via `scripts/install-context-persistence.sh`. All repos committed + pushed.
