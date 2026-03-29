# EGOS-Lab → Clean Kernel Consumer Plan

> **VERSION:** 2.1.0 | **DATE:** 2026-03-29
> **PURPOSE:** Transform egos-lab from duplicate-carrying monorepo into clean kernel consumer
> **DEPENDS ON:** EGOS-073 (diagnostic), EGOS-074 (consolidation), EGOS-092 (leaf adoption)
> **LAST SYNC:** 2026-03-29 — Cleanup branch `fix/kernel-consumer-cleanup` delivered (2 commits)

## Context

egos-lab was the original development monorepo. The kernel (`egos`) was extracted from it.
Now that the kernel is mature (14 modules, 166 tests, governance enforced), egos-lab
must become a **clean consumer** — importing from `@egos/shared`, not maintaining local copies.

**IMPORTANT:** egos-lab is NOT being archived. It has 7+ production apps, 29 agents,
and active infrastructure (Railway, Redis, Vercel). The goal is to eliminate SSOT
violations (duplicate packages) while keeping production surfaces healthy.

## Phase 1: Already Migrated to Kernel ✅

These surfaces have ALREADY been moved from egos-lab to egos:

| Surface | Kernel Location | Status |
|---------|----------------|--------|
| ATRiAN | `packages/shared/src/atrian.ts` | ✅ Canonical in kernel (16 tests) |
| PII Scanner | `packages/shared/src/pii-scanner.ts` | ✅ Canonical (14 tests) |
| Conversation Memory | `packages/shared/src/conversation-memory.ts` | ✅ Canonical (13 tests) |
| Cross-Session Memory | `packages/shared/src/cross-session-memory.ts` | ✅ Canonical (17 tests) |
| LLM Provider | `packages/shared/src/llm-provider.ts` | ✅ Canonical (6 tests) |
| Model Router | `packages/shared/src/model-router.ts` | ✅ Canonical (17 tests) |
| Rate Limiter | `packages/shared/src/rate-limiter.ts` | ✅ Canonical (8 tests) |
| Telemetry | `packages/shared/src/telemetry.ts` | ✅ Canonical (11 tests) |
| Agent Runtime | `agents/runtime/runner.ts` + `event-bus.ts` | ✅ FROZEN in kernel |
| Dead Code Detector | `agents/agents/dead-code-detector.ts` | ✅ Migrated |
| Dep Auditor | `agents/agents/dep-auditor.ts` | ✅ Migrated |
| Governance DNA | `.guarani/` | ✅ Kernel is SSOT |
| SSOT docs | `AGENTS.md`, `TASKS.md`, registries | ✅ Kernel is SSOT |

## Phase 2: MUST Migrate Before Archiving

| Surface in egos-lab | Action | Target in Kernel | Priority |
|-------------------|--------|-----------------|----------|
| `packages/shared/` (duplicate) | **DELETE** — lab should import from kernel | N/A (already in kernel) | P0 |
| `governance-sync.sh` (copy) | **DELETE** — kernel owns this | N/A (already in kernel) | P0 |
| `SYSTEM_MAP.md` (lab version) | **MERGE** lab-specific parts into kernel v3.0.0, then delete | `docs/SYSTEM_MAP.md` | P0 |
| `CAPABILITY_REGISTRY.md` (lab copy) | **DELETE** — kernel v1.4.0 is canonical | N/A | P0 |
| SSOT Auditor agent | **EVALUATE** — generalize for kernel or archive | `agents/agents/` if useful | P1 |
| Contract Tester agent | **EVALUATE** — remove hardcoded endpoints, generalize | `agents/agents/` if useful | P1 |
| API Registry Check | **EVALUATE** — shared contract layer value | `agents/agents/` if useful | P2 |

## Phase 3: Keep in egos-lab (Archive as-is)

These surfaces are app-specific and should stay in the egos-lab archive:

| Surface | Reason to Archive (not migrate) |
|---------|-------------------------------|
| `apps/egos-web` | Production web app — lives at egos.ia.br, has its own deploy |
| `apps/agent-028-template` | AIXBT dashboard — app-specific |
| `apps/commons` | Marketplace — app-specific |
| `apps/telegram-bot` | Telegram bot — app-specific |
| `agents/worker/` | Railway worker infrastructure — lab-specific |
| Lab-specific agents (gem-hunter, report_generator) | App-specific, not kernel-worthy |
| Vercel configs | Deploy-specific |
| Redis/queue configs | Infrastructure-specific |
| Docker configs | Lab-specific infrastructure |

## Phase 4: Verify Clean Consumer State

Before declaring egos-lab a clean consumer, confirm ALL of:
- [ ] egos-lab package.json imports `@egos/shared` from kernel (not local copy)
- [ ] No local copies of atrian, llm-provider, rate-limiter in lab packages/
- [ ] governance-sync.sh removed from lab (or pointing to kernel)
- [ ] Lab SYSTEM_MAP and CAPABILITY_REGISTRY marked deprecated
- [ ] Boundary contract documented in lab AGENTS.md
- [ ] All production apps still building and deploying (smoke test)

## Phase 5: Future Decisions (not blocking)

- **SSOT Auditor / Contract Tester:** Generalize and migrate to kernel if reuse proven
- **ai-client.ts:** Merge into kernel llm-provider.ts or keep as lab-specific
- **egos-web extraction:** Consider standalone repo if it outgrows lab context
- **Agent registry:** Lab keeps its 29-agent registry; kernel keeps 10-agent registry

## Execution Checklist

- [ ] Phase 2: Remove `@egos/shared` duplicate from egos-lab
- [ ] Phase 2: Remove governance-sync.sh copy from egos-lab
- [ ] Phase 2: Merge lab SYSTEM_MAP into kernel
- [ ] Phase 2: Remove CAPABILITY_REGISTRY copy from lab
- [ ] Phase 2: Evaluate SSOT Auditor for kernel migration
- [ ] Phase 2: Evaluate Contract Tester for kernel migration
- [ ] Phase 4: Update egos-lab README with archive notice
- [ ] Phase 4: Update GitHub repo description
- [ ] Phase 4: Disable egos-lab CI
- [ ] Phase 4: Update mycelium graph (egos-lab → archived)
- [ ] Phase 5: Decision on egos-web extraction

## Execution Log

### 2026-03-29 — Branch `fix/kernel-consumer-cleanup` (egos-lab)

**Commits:** `8f1c68e`, `f7a73f5`

**Corrected assumptions:**
- egos-lab has **24 agents** (not 29) — 22 active, 2 dormant
- `social-media` → dormant | `domain-explorer` entrypoint fixed (snake→kebab)
- `dep_auditor`, `dead_code_detector` dormant in web consumer (migrated to kernel)
- `agent:lint` passes: 0 errors, 24 agents

**PR ready for merge to main in egos-lab.**

**Remaining P0 (next session with lab access):**
- [ ] Mark shared module copies as deprecated
- [ ] Mark governance-sync.sh copy as deprecated
- [ ] Mark CAPABILITY_REGISTRY/SYSTEM_MAP copies as deprecated
- [ ] Update egos-lab AGENTS.md with kernel dependency header

## Notes

- Phase 2 partially started (registry cleanup done, module deprecation pending)
- SSOT Merge Rule (#23) applies: no parallel truths between kernel and lab
