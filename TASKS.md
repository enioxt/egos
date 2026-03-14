# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.0.0 | **Updated:** 2026-03-13

---

## Current Sprint: Foundation

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
- [/] EGOS-051: Migrate core-safe agents from egos-lab — `dead_code_detector` migrated (4 kernel agents now); SSOT Auditor + Contract Tester need generalization (medium-term)
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

### P2 (Important) — Replication & Adoption

- [/] EGOS-034: Forja — foundation chatbot integrated with shared modules + `/api/chat`; production parity and hybrid architecture still pending
- [x] EGOS-035: carteira-livre — backfill ATRiAN + PII scanner + memory modules
- [x] EGOS-036: intelink — backfill ATRiAN + memory modules
- [ ] EGOS-037: Research go-to-market theories for code/framework validation
- [ ] EGOS-038: Create capability-drift-checker (compares repo chatbots against CHATBOT_SSOT checklist)
- [ ] EGOS-039: egos-web — align public chat with shared ATRiAN/PII/memory modules and nuanced CHATBOT_SSOT maturity tags
- [ ] EGOS-040: br-acc — define Python adapter/bridge to CHATBOT_SSOT and capability registry alignment

### Backlog

- [ ] EGOS-012: Publish `@egos/shared` to npm (when stable)
- [x] EGOS-013: Create `egos-init` one-command installer
- [ ] EGOS-014: Add VRCP Coherence Model integration
- [ ] EGOS-015: Context Doctor agent (from conversaGROK ideas)
- [ ] EGOS-016: Review remaining workflow overrides in leaf repos after SSOT rollout
- [ ] EGOS-023: Publish egos-init via hosted installer URL
- [ ] EGOS-024: Full per-agent lineage matrix (ARCH-003) — continue with commit-level tracing
- [ ] EGOS-053: Build cross-repo capability compliance dashboard for kernel and leaf adoption state
- [x] EGOS-054: Make `/end` and `/disseminate` repo-role-aware — `egos.config.json` detection in Phase 1, conditional surface gating

## Roadmap — Progress Dashboard

### Overall Progress

| Horizon | Total | Done | Open | Progress |
|---------|-------|------|------|----------|
| **Foundation (P0/P1)** | 21 | 21 | 0 | **100%** |
| **Replication (P2)** | 14 | 13 | 1 | **93%** |
| **Backlog** | 8 | 3 | 5 | **38%** |
| **TOTAL** | **43** | **38** | **5** | **88%** |

---

### Short Term (0-7 days) — Target: 75%

**Objective:** Complete all P2 core hardening. CONTRIBUTING.md, activation:check, and cross-repo adoption alignment.

- [x] EGOS-010 — CONTRIBUTING.md with governance rules
- [/] EGOS-034 — Forja chatbot production parity
- [ ] EGOS-039 — egos-web chat alignment with shared modules
- [ ] EGOS-040 — br-acc Python adapter for CHATBOT_SSOT
- [x] EGOS-050 — `activation:check` command for core repo (42 checks, 100%)

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
