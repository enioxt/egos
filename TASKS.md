# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.5.0 | **Updated:** 2026-03-23 | **Last Session:** Claude Code (Guard Brasil + Commons + migration gaps)

---

## Current Sprint: Foundation

## Strategic Reset — Product Focus (2026-03-18)

- [x] EGOS-061: Publish consolidated ecosystem verdict and repo roles — `docs/strategy/ECOSYSTEM_PRODUCT_VERDICT_2026-03.md`
- [x] EGOS-062: Package the canonical product boundary for `EGOS Guard Brasil` — ATRiAN + PII Scanner BR + public guard + evidence discipline — `docs/products/GUARD_BRASIL.md` + `packages/shared/src/public-guard.ts` + `packages/shared/src/evidence-chain.ts`
- [x] EGOS-063: Define free vs paid surface for the flagship (open SDK/specs vs hosted API/MCP/audit console) — `docs/products/GUARD_BRASIL_FREE_PAID.md`
- [x] EGOS-064: Deliver the first monetizable surface as a reusable package or MCP before expanding any new product line — `scripts/guard.ts` CLI + npm scripts (`guard:validate`, `guard:mask`, `guard:check`, `guard:demo`) + `docs/products/GUARD_BRASIL.md`
- [x] EGOS-073: Run the full `egos-lab` consolidation diagnostic — classify every active surface as `migrate_to_egos`, `keep_in_lab`, `standalone_candidate`, `internal_infra`, `archive`, or `discard`, with source→destination pointers — `docs/strategy/EGOS_LAB_CONSOLIDATION_DIAGNOSTIC.md`
- [ ] EGOS-074: Execute the kernel-first consolidation of SSOT/governance surfaces from `egos-lab` into `egos` and eliminate duplicated docs, maps, workflows, and stale claims with explicit archive references
- [ ] EGOS-075: Canonicalize the System Map control plane — one orchestrator contract, one machine map, one human map, freshness rules, and one cross-repo update flow
- [x] EGOS-076: Create the ecosystem classification registry for products/modules/ideas (`standalone`, `candidate`, `lab`, `internal_infra`, `archive`) and wire it into `TASKS.md`, `SYSTEM_MAP.md`, and `CAPABILITY_REGISTRY.md` — `docs/ECOSYSTEM_CLASSIFICATION_REGISTRY.md`

### Session Sync — 2026-03-23 (/start mesh truth audit)

- [x] EGOS-093: Canonicalized kernel `.windsurf/workflows/start.md` to require mesh truth audit, Codex readiness, Alibaba readiness, and explicit local/docs/github/runtime separation.
- [x] EGOS-094: Propagate the new kernel `/start` into `~/.egos/workflows` and downstream leaves via governance sync, then verify the shared `/start` matches kernel truth.
- [x] EGOS-095: Generalize startup audit beyond egos-lab so the kernel can own a first-class mesh-wide activation command without repo-local fallback.

### P0 (Blockers) — MIGRATION GAPS (egos-lab → egos)

**Found during Guard Brasil + Commons implementation. CRITICAL for consolidation.**

- [x] EGOS-090_MIGR: Sincronizar `@egos/shared` — egos-lab mantém cópia local desatualizada. Migrar todos os imports para consumir do kernel.
  > Arquivos: `egos-lab/packages/shared/src/`, referências em `package.json`
  > Bloqueador: Guard Brasil SDK só está em kernel, egos-lab não tem acesso

- [x] EGOS-091_MIGR: Clonar egos-lab no ambiente de trabalho — Claude Code só tem kernel local. Para continuidade de desenvolvimento, egos-lab precisa estar sincronizado.
  > Bloqueador: Agent-028 template, report_generator, gem-hunter estão lá, precisam estar acessíveis

- [x] EGOS-092_MIGR: Movimentar ou integrar `agent-028-template` — Atualmente em egos-lab, metadados no kernel. Ou move para kernel `/apps/` ou garante que egos-lab consome como submódulo.
  > Recomendação: Mover para kernel, deploy via Vercel como sub-app
  > Bloqueador: Vercel deploy requer acesso ao código-fonte

- [ ] EGOS-077: Add the new-project gate for PRD, ICP, go-to-market, objective, success metric, and multi-model review mode with a recorded blocking-vs-advisory decision
- [ ] EGOS-078: Define the `Agent Claim Contract` — formal taxonomy for `component`, `skill`, `agent_candidate`, `verified_agent`, and `online_agent`, with mandatory proof fields for runtime, triggers, evals, observability, and ownership
- [ ] EGOS-079: Enforce the `Agent Claim Gate` in kernel governance — registry lint + pre-commit/pre-push + docs/tasks checks must block any surface claimed as agent without executable entrypoint, existing eval, valid run modes, and runtime evidence
- [ ] EGOS-080: Define the `LLM Orchestration Matrix` for EGOS — explicit lane ownership for Cascade, terminal orchestration, Codex, Claude Code, Alibaba, and OpenRouter, with approval mode, authority level, and allowed task classes
- [x] EGOS-083: Create the canonical cross-repo SSOT registry in the kernel and define the ownership contract for `kernel_canonical`, `leaf_local`, and `shared_home` surfaces
- [x] EGOS-084: Extend kernel governance sync + pre-commit to cover canonical SSOT docs (`SSOT_REGISTRY`, `CAPABILITY_REGISTRY`, `CHATBOT_SSOT`) and sync them to `~/.egos/docs`
- [ ] EGOS-085: Roll out the SSOT registry adoption plan across mapped repos — each leaf must declare local SSOT pointers, freshness rules, and task-level migration status

> **Directive:** Until EGOS-062..064 are resolved, new work should strengthen the flagship guardrails product or its proof cases only.

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

### P1 (Critical) — MIGRATION & COMMONS INTEGRATION

- [ ] EGOS-093_MIGR: Remover/arquivar docs duplicadas em egos-lab — SYSTEM_MAP.md, CAPABILITY_REGISTRY.md, etc. Kernel é SSOT.
- [ ] EGOS-094_COMMONS: Criar Supabase schema para Commons — tables: `courses`, `enrollments`, `lesson_progress`, `lesson_feedback`, `quiz_attempts`, `certificates`
- [ ] EGOS-095_COMMONS: Integrar database no Commons frontend — Supabase client, auth GoTrue, realtime subscriptions

### P2 (Important) — INFRASTRUCTURE & DEPLOYMENT

- [ ] EGOS-096_INFRA: Setup VPS Contabo — DNS para commons.egos.ia.br, SSL Let's Encrypt, nginx/reverse proxy
- [ ] EGOS-097_API: Implementar Guard Brasil API hosted — rate limiting, telemetry, audit logs, SLA 99.5%
- [ ] EGOS-098_COMMONS: Integrar pagamento Asaas em Commons — enrollment flow, webhook verification, email confirmação

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
