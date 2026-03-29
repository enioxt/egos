# EGOS-Lab → Kernel Migration & Archival Plan

> **VERSION:** 1.0.0 | **DATE:** 2026-03-29
> **PURPOSE:** Complete migration checklist before archiving egos-lab
> **DEPENDS ON:** EGOS-073 (diagnostic), EGOS-074 (consolidation), EGOS-092 (leaf adoption)

## Context

egos-lab was the original development monorepo. The kernel (`egos`) was extracted from it.
Now that the kernel is mature (14 modules, 166 tests, governance enforced), egos-lab
should become an archive. This plan ensures nothing is lost.

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

## Phase 4: Archival Steps

1. **Verify all P0 items migrated** (Phase 2 complete)
2. **Update egos-lab README** to say: "⚠️ ARCHIVED — Kernel is at github.com/enioxt/egos"
3. **Add `[ARCHIVED]` to repo description** on GitHub
4. **Set egos-lab topics**: `archived`, `egos-legacy`
5. **Keep repo PUBLIC** (reference for archaeology_digger agent)
6. **Do NOT delete** — preserve git history for provenance
7. **Disable GitHub Actions** in egos-lab (save CI minutes)
8. **Update mycelium reference-graph** to mark egos-lab as `status: 'archived'`

## Phase 5: Post-Archival

After archival, the egos-lab apps that are still in production (egos-web, commons)
need to be either:
- **Option A:** Extracted as standalone repos (e.g., `enioxt/egos-web`)
- **Option B:** Left in archived egos-lab with deploy hooks still active
- **Option C:** Moved to the kernel as `apps/` directory

**Recommendation:** Option A for egos-web (it's the main site), Option B for the rest.

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

## Notes

- All Phase 2 actions require access to the egos-lab repo
- Phase 4 requires GitHub admin access
- This plan aligns with EGOS-073 (diagnostic) and EGOS-074 (consolidation)
- SSOT Merge Rule (#23) applies: no parallel truths between kernel and lab
