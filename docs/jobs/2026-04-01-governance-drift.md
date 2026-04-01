# EGOS Governance Drift Report
**Date:** 2026-04-01  
**Overall Status:** ⚠️ **WARNING** (2 issues detected)

---

## 1. File Size Compliance

| File | Lines | Limit | Status |
|------|-------|-------|--------|
| TASKS.md | 487 | 500 | ✅ PASS |
| AGENTS.md | 170 | 200 | ✅ PASS |
| .windsurfrules | 150 | 200 | ✅ PASS |

**Summary:** All SSOT files within compliance limits.

---

## 2. Broken References

**Found:** 2 broken llmrefs

- ❌ `apps/egos-web/api/mycelium-stats.ts` — referenced in README/docs but file missing
- ❌ `docs/knowledge/MYCELIUM_OVERVIEW.md` — referenced in README/docs but file missing

**Action Required:** Review and fix broken references in documentation files.

---

## 3. Version Alignment

| Component | Version | Status |
|-----------|---------|--------|
| guard-brasil package.json | 0.2.0 | ✅ ALIGNED |
| guard-brasil npm published | 0.2.0 | ✅ ALIGNED |
| server.ts (v0.2.0 string) | 0.2.0 | ✅ ALIGNED |
| mcp-server.ts (v0.2.0 string) | 0.2.0 | ✅ ALIGNED |

**Summary:** All versions synchronized.

---

## 4. Agent Registry

- **Total Agents:** 15
- **Registry Version:** 2.1.0
- **Status:** ✅ INTACT

---

## 5. Git Repository

- **Uncommitted Changes:** 0
- **Status:** ✅ CLEAN

---

## 6. Job Reports History

- **Previous Reports:** None (first governance check)

---

## 7. Codebase Memory

- **codebase-memory-mcp:** Not available in environment

---

## Recommendations

1. **Priority:** HIGH - Create missing files or remove broken references:
   - Investigate if `apps/egos-web/api/mycelium-stats.ts` should be created or references removed
   - Investigate if `docs/knowledge/MYCELIUM_OVERVIEW.md` should be created or references removed

2. **Schedule:** Next check on 2026-04-02

---

**Report Generated:** 2026-04-01 (Daily Health Check)
