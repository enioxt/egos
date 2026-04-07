# Governance Drift Report — 2026-04-07

**Timestamp:** 2026-04-07T09:00Z  
**Runner:** autoDream (Governance Sentinel)  
**Overall Status:** ⚠️ **WARNING** — 2 critical issues requiring action

---

## PART 1: Governance Drift

### 1. File Size Compliance

| File | Lines | Limit | Status |
|------|-------|-------|--------|
| `TASKS.md` | 528 | 500 | ❌ **OVER LIMIT** |
| `AGENTS.md` | 199 | 200 | ✅ OK |
| `.windsurfrules` | 150 | 200 | ✅ OK |

**Action Required:** Archive completed/archived tasks from TASKS.md to TASKS_ARCHIVE_2026.md to bring under 500-line limit.

### 2. Broken References

**Status:** ❌ **CRITICAL** — 20 broken llmref links detected

Broken references found in markdown files:
- `.guarani/` (directory reference)
- `/home/enio/egos/AGENTS.md` (absolute path, not relative)
- `/home/enio/egos/docs/SSOT_REGISTRY.md` (absolute path)
- `/start` (skill reference, not file)
- Missing doc files: `ACTIVATION_FLOW.md`, `ACTIVATION_GUIDE.md`, `CAPABILITY_REGISTRY.md`, `ECOSYSTEM_CLASSIFICATION_REGISTRY.md`, `ENVIRONMENT_REGISTRY.md`, `EXECUTIVE_SUMMARY_DECISION_MATRIX.md`, `INFRASTRUCTURE_ARCHIVE_AUDIT.md`, `MASTER_INDEX.md`, `SSOT_REGISTRY.md`, `SYSTEM_MAP.md`, `docs/knowledge/MYCELIUM_OVERVIEW.md`
- Example broken app references: `apps/egos-web/api/mycelium-stats.ts`, `another/file.ts`

**Action Required:** Audit and fix broken llmrefs. Most appear to be stale documentation references.

### 3. Version Alignment

| Component | Local | Published | Status |
|-----------|-------|-----------|--------|
| guard-brasil | 0.2.2 | 0.2.2 | ✅ **IN SYNC** |

### 4. Agent Registry

- **Agents Registered:** 19
- **Status:** ✅ OK

### 5. Uncommitted Changes

- **Status:** ✅ **CLEAN** — 0 uncommitted files

### 6. Recent Job Reports

- 2026-04-07: doc-drift-sentinel.md
- 2026-04-03: governance-drift.md (✅ In sync)
- 2026-04-01: governance-drift.md (⚠️ 2 issues)

---

## PART 2: Memory Consolidation

### 7. Job Report Cleanup

- governance-drift: 2 reports (within limit)
- doc-drift: 2 reports (within limit)
- code-security: 0 reports
- **Status:** ✅ No archival needed yet

### 8. Orphaned Handoffs

- **Status:** ✅ OK — No `_current_handoffs` directory or 0 handoffs >30 days old

### 9. TASKS.md Health

| Metric | Value |
|--------|-------|
| Total lines | 528 |
| Completed tasks | 0 |
| Pending tasks | 0 |
| **Status** | ⚠️ **BLOATED** |

**Note:** TASKS.md exceeds 450-line threshold. No completed tasks detected in traditional checkbox format — may use different tracking. Recommend reviewing and archiving if stale content exists.

---

## Summary

### Critical Issues (P0)

1. **TASKS.md bloat** — 528 lines vs. 500-line limit
   - Action: Archive old/completed items

2. **Broken llmrefs** — 20+ stale documentation links
   - Action: Audit and fix or remove references

### Warnings (P1)

- None additional

### Clean (P2+)

- ✅ Version alignment (guard-brasil 0.2.2)
- ✅ Agent registry (19 agents)
- ✅ Git working tree (0 uncommitted)
- ✅ Job report rotation
- ✅ Handoff cleanup

---

## Recommended Actions

1. **TODAY:** Audit and fix/remove 20 broken llmrefs
2. **TODAY:** Review TASKS.md and create TASKS_ARCHIVE_2026.md if needed
3. **Next cycle:** Consider SSOT-first rule enforcement for documentation

**Next Governance Check:** 2026-04-08 (daily)
