# KERNEL_CONSOLIDATION_PLAN.md — EGOS-074

<!-- llmrefs:start -->
## LLM Reference Signature

- **Role:** migration plan for canonical surfaces from `egos-lab` into `egos` kernel
- **Summary:** Phased consolidation strategy grounded in EGOS-073 diagnostic evidence to reduce duplicate/stale surfaces.
- **Read next:**
  - `docs/SSOT_REGISTRY.md` — ownership of canonical surfaces
  - `docs/SYSTEM_MAP.md` — placement of migrated components
  - `TASKS.md` — active execution state for consolidation tasks
<!-- llmrefs:end -->

> **VERSION:** 1.0.0 | **CREATED:** 2026-03-30 | **TASK:** EGOS-074
> **SSOT-VISITED:** 2026-03-30, disposition: gem-found

## Context

This is the execution plan for moving canonical surfaces from `egos-lab` into `egos` (kernel).
It is grounded in the completed EGOS-073 diagnostic at `docs/strategy/EGOS_LAB_CONSOLIDATION_DIAGNOSTIC.md`.

**What already happened:**
- `egos/packages/shared/` is the kernel SSOT for all shared TypeScript modules (not a symlink — it is independent)
- `egos-lab/packages/shared/` is a separate copy with the same structure; it is **stale and should not be used**
- Three agents from egos-lab were already migrated to egos kernel: `ssot_auditor`, `ssot_fixer`, `drift_sentinel` (confirmed in `agents/registry/agents.json`)
- `egos-lab` does NOT have a symlink bridging `packages/shared` to egos — it has its own copy in `packages/nexus-shared/` (AI layer) and `packages/shared/` (duplicated)

---

## Phase 1 — Immediate (this week)

> Goal: Eliminate the most dangerous duplications — shared package drift and stale governance claims.

### P1-A: Remove or stub the duplicate `@egos/shared` in egos-lab

| Field | Value |
|-------|-------|
| What | Duplicated `packages/shared/src/` with llm-provider, atrian, pii-scanner, model-router, etc. |
| Source | `/home/enio/egos-lab/packages/shared/src/` |
| Destination | Delete; consumers should import from `@egos/shared` (kernel) |
| Why | Kernel owns `@egos/shared`. Lab copy drifts silently. EGOS-073 P0 action never executed. |
| Blocker | Lab apps (`egos-web`) reference `@egos-lab/shared` workspace. Rename required in `package.json`. |

**Execution steps:**
1. Update `egos-lab/apps/egos-web/package.json`: replace `"@egos-lab/shared": "workspace:*"` with `"@egos/shared": "workspace:../../egos/packages/shared"` (or publish kernel to npm)
2. Update `egos-lab/packages/nexus-shared/` imports accordingly
3. Archive `egos-lab/packages/shared/src/` → `egos-lab/packages/_archived/shared-deprecated-2026-03-30/`
4. Verify `bun run typecheck` passes in egos-lab after removal

### P1-B: Remove stale governance-sync.sh from egos-lab (if it exists)

| Field | Value |
|-------|-------|
| What | Any copy of `governance-sync.sh` or `.guarani/` overrides in egos-lab |
| Source | `egos-lab/.guarani/` (if overrides exist beyond identity/preferences) |
| Destination | Delete. Kernel `.guarani/` is SSOT. |
| Why | Leaf repo overrides shadow kernel governance and cause drift. |
| Blocker | None — check before deleting. |

**Execution steps:**
1. Run `diff /home/enio/egos/.guarani/ /home/enio/egos-lab/.guarani/` to identify overrides
2. Archive any lab-local overrides that are NOT identity/preferences
3. Confirm `~/.egos/sync.sh` propagation covers egos-lab

### P1-C: Archive stale docs in egos-lab

| Field | Value |
|-------|-------|
| What | Docs older than 60 days with no active TASKS.md reference in egos-lab |
| Source | `/home/enio/egos-lab/docs/` — SYSTEM_MAP.md, CAPABILITY_REGISTRY.md, stale maps |
| Destination | Add `<!-- DUPLICATE: canonical at egos/docs/SYSTEM_MAP.md -->` header to lab copies; archive if stale |
| Why | LAB-ARCHIVE-003 explicit task. Lab docs shadow kernel SSOT and mislead LLMs. |
| Blocker | None. |

**Execution steps:**
1. Add stale disclaimer headers to `egos-lab/docs/SYSTEM_MAP.md` and any `CAPABILITY_REGISTRY` copy
2. Move any lab-only docs older than 60d with no task ref to `egos-lab/docs/archive/`
3. Update `egos-lab/AGENTS.md` with pointer: "For global SSOT, see `egos/docs/SSOT_REGISTRY.md`"

---

## Phase 2 — Short-term (2 weeks)

> Goal: Tighten the kernel↔lab boundary. Formalize what lives where. Apply LAB-ARCHIVE tasks.

### P2-A: Adopt kernel SSOT_REGISTRY in egos-lab (LAB-ARCHIVE-006)

| Field | Value |
|-------|-------|
| What | Explicit SSOT pointers in egos-lab TASKS.md, AGENTS.md, and active maps |
| Source | `/home/enio/egos/docs/SSOT_REGISTRY.md` (kernel, this file) |
| Destination | egos-lab AGENTS.md and TASKS.md gain pointer sections |
| Why | LAB-ARCHIVE-006 task. Currently egos-lab makes implicit global SSOT claims. |
| Blocker | None. |

**Execution steps:**
1. Add to `egos-lab/AGENTS.md`: "## SSOT Registry\nGlobal canonical SSOT: `egos/docs/SSOT_REGISTRY.md`. Lab-local truth: this file."
2. Add to `egos-lab/TASKS.md`: pointer to kernel SSOT for governance, shared packages, agent registry
3. Mark LAB-ARCHIVE-006 [x] in egos-lab/TASKS.md

### P2-B: Classify remaining egos-lab apps (LAB-ARCHIVE-005)

| Surface | Source | Classification | Decision |
|---------|--------|----------------|----------|
| `eagle-eye` | `egos-lab/apps/eagle-eye/` | `keep_in_lab` | OSINT gazette monitor, lab-specific. |
| `telegram-bot` | `egos-lab/apps/telegram-bot/` | `keep_in_lab` | Community bot, lab production surface. |
| `egos-web` | `egos-lab/apps/egos-web/` | `keep_in_lab` | Public website egos.ia.br, production. |
| `agent-commander` | `egos-lab/apps/agent-commander/` | `keep_in_lab` | Lab CLI surface, production. |
| `nexus` | `egos-lab/apps/nexus/` | `standalone_candidate` | Has mobile+web+supabase — evaluate for own repo at stable phase. |
| `marketplace-core` | `egos-lab/apps/marketplace-core/` | `standalone_candidate` | Could be `egos-marketplace` repo if product materializes. |
| `intelink` | `egos-lab/apps/intelink/` | `keep_in_lab` | Internal intelligence aggregator. |
| `carteira-x` | `egos-lab/apps/carteira-x/` | `keep_in_lab` | Lab surface for wallet experiments. |
| `radio-philein` | `egos-lab/apps/radio-philein/` | `keep_in_lab` | Community radio surface. |
| `symphony-egos` | `egos-lab/apps/symphony-egos/` | `archive` | No active task reference — evaluate for archive. |
| `egos-self` | `egos-lab/apps/egos-self/` | `archive` | Python-based self-agent, pre-dates current architecture — archive candidate. |
| `_archived` | `egos-lab/apps/_archived/` | `archive` | Already archived. Confirm permanent. |

**Execution steps:**
1. For `standalone_candidate` apps: add `STANDALONE_CANDIDATE.md` stub in each app root
2. For `archive` apps: move to `egos-lab/apps/_archived/` if not already there
3. Record decisions in `egos-lab/TASKS.md` as LAB-ARCHIVE-005 [x]

### P2-C: Classify egos-lab agents against Agent Claim Contract (LAB-ARCHIVE-005)

| Agent | entrypoint | Classification | Decision |
|-------|-----------|----------------|----------|
| `gem-hunter` | `agents/agents/gem-hunter.ts` | `tool` / `keep_in_lab` | Lab code discovery, not generic enough for kernel |
| `contract-tester` | `agents/agents/contract-tester.ts` | `tool` / `keep_in_lab` | Lab-specific contract testing |
| `security-scanner` | `agents/agents/security-scanner.ts` | `tool` / evaluate | Generic scanner — evaluate if kernel already covers via `ssot_auditor` |
| `autoresearch` | (not in listed agents/) | `lab_experiment` | Keep in lab; no evaluator yet per LAB-ARCHIVE-005 sub-task |
| `ambient_disseminator` | (not in listed agents/) | `lab_experiment` | Keep in lab; needs eval before claim |
| `ui-designer` | `agents/agents/ui-designer.ts` | `tool` / `keep_in_lab` | Stitch UI designer, lab-specific |
| `social-media` | `agents/agents/social-media.ts` | `tool` / `keep_in_lab` | Social automation, lab surface |
| `quota-guardian` | `agents/agents/quota-guardian.ts` | `tool` / `keep_in_lab` | Lab infra monitoring |
| `orchestrator` | `agents/agents/orchestrator.ts` | `workflow` / evaluate | Review vs kernel runner before claim |

**Rule:** No agent can be reclassified from `tool` → `verified_agent` without proof (runtime_proof, telemetry_source, loop_mechanism) per EGOS-078 Agent Claim Contract.

### P2-D: Fix lab package.json boundary

| Field | Value |
|-------|-------|
| What | `egos-lab` package resolution for `@egos/shared` |
| Source | `egos-lab/package.json` and `egos-lab/apps/*/package.json` |
| Destination | All lab apps import from kernel `@egos/shared` |
| Why | Lab packages currently maintain their own copy, creating drift |
| Blocker | Requires either workspace path reference or npm publish of kernel package |

---

## Phase 3 — Deferred (when stable)

> Goal: Long-term boundary hardening. Only run when Phase 1+2 complete and Guard Brasil GTM is not in active sprint.

### P3-A: Publish `@egos/shared` to npm

| Field | Value |
|-------|-------|
| What | Publish `egos/packages/shared/` as `@egos/shared` npm package |
| Source | `/home/enio/egos/packages/shared/` |
| Destination | npm registry (scoped, private or public) |
| Why | Enables leaf repos (br-acc, carteira-livre, 852) to consume shared without workspace path hacks |
| Blocker | Requires npm org setup. Kernel package must be stable first. |

### P3-B: Evaluate `nexus` for standalone repo

| Field | Value |
|-------|-------|
| What | `egos-lab/apps/nexus/` — mobile + web + supabase |
| Source | `/home/enio/egos-lab/apps/nexus/` |
| Destination | Own repo `/home/enio/nexus` or `egos-nexus` |
| Why | Has its own supabase, mobile, and web surfaces — complex enough for standalone |
| Blocker | No active user base. Defer until product clarity. |

### P3-C: Canonicalize System Map control plane (EGOS-075)

| Field | Value |
|-------|-------|
| What | One orchestrator contract, one machine map, one human map |
| Source | `egos/docs/SYSTEM_MAP.md` (kernel), `egos-lab/docs/*.md` (stale) |
| Destination | All maps point to kernel SYSTEM_MAP.md |
| Why | Currently egos-lab has its own system map claiming global truth |
| Blocker | Depends on Phase 2 doc archiving being complete. |

---

## Archive Candidates (mark, do not delete yet)

These surfaces exist in egos-lab and are confirmed stale or superseded:

| Surface | Path | Reason | Action |
|---------|------|--------|--------|
| lab shared package | `egos-lab/packages/shared/src/` | Superseded by kernel `packages/shared/` | Archive after Phase 1-A |
| symphony-egos | `egos-lab/apps/symphony-egos/` | No active task reference found | Move to `_archived` |
| egos-self | `egos-lab/apps/egos-self/` | Python prototype, pre-dates current architecture | Move to `_archived` |
| Lab SYSTEM_MAP | `egos-lab/docs/SYSTEM_MAP.md` (if exists) | Superseded by kernel | Add stale header |
| Lab CAPABILITY_REGISTRY | `egos-lab/docs/CAPABILITY_REGISTRY.md` (if exists) | Superseded by kernel | Add stale header |
| Lab governance-sync.sh | `egos-lab/scripts/governance-sync.sh` (if exists) | Kernel SSOT for governance scripts | Delete or symlink to kernel |

---

## What Not to Move

| Surface | Why stays in egos-lab |
|---------|----------------------|
| `egos-web` (Mission Control) | Production web app for egos.ia.br |
| `eagle-eye` | OSINT product, lab-specific data pipeline |
| `telegram-bot` | Community bot, lab production |
| `agent-commander` | Lab CLI |
| `nexus-shared` (AI layer) | Lab-specific AI utilities for nexus — not generic enough for kernel |
| `.github/workflows/` (lab) | Deploy/CI workflows for lab apps — infra-local |
| Lab agent registry | Lab agents.json v1.0.0 stays in lab; kernel has its own v2.0.0 |

---

## Boundary Contract (Post-Consolidation)

```
egos (kernel)
├── agents/registry/agents.json     ← v2.0.0, SSOT for kernel agents
├── agents/runtime/                 ← FROZEN — runner + event-bus
├── agents/agents/                  ← Generic kernel tools (ssot_auditor, drift_sentinel, etc.)
├── packages/shared/src/            ← @egos/shared — ALL shared TS modules live here
├── .guarani/                       ← Governance DNA SSOT
├── docs/SSOT_REGISTRY.md           ← Cross-repo SSOT map
└── docs/CAPABILITY_REGISTRY.md     ← Capability SSOT

egos-lab (lab + production surface)
├── apps/                           ← Production web apps (CONSUME @egos/shared)
├── agents/agents/                  ← Lab-specific agents only
├── packages/nexus-shared/          ← Lab-local AI layer for nexus
└── AGENTS.md                       ← Points to kernel SSOT_REGISTRY
```

---

*Owner: EGOS Kernel*
*Related: EGOS-073, EGOS-074, EGOS-075, LAB-ARCHIVE-001..006*
*Prev: `docs/strategy/EGOS_LAB_CONSOLIDATION_DIAGNOSTIC.md`*
