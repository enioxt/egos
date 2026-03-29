# Linear / Issue Sync Contract

> **SSOT Owner:** `egos/docs/governance/LINEAR_SYNC_CONTRACT.md`
> **Version:** 1.0.0 | **Created:** 2026-03-29 | **Status:** ACTIVE
> **Task:** EGOS-100

---

## Purpose

Defines how TASKS.md (the kernel SSOT for work) stays in sync with any external issue tracker (GitHub Issues, Linear) and how tasks decompose into PRs.

---

## SSOT Hierarchy

```
TASKS.md (kernel) ← CANONICAL
    ↓ sync
GitHub Issues (enioxt/egos) ← mirror, not source
    ↓ reference
PR description ← must link to EGOS task ID
```

**Rule:** `TASKS.md` is always the source of truth. GitHub Issues may exist for visibility but must reference the EGOS task ID (`EGOS-NNN`). Never create an issue without a corresponding TASKS.md entry.

---

## Task Decomposition Schema

Every TASKS.md entry must have:

```markdown
- [ ] EGOS-NNN: <imperative verb> — <description>
  - **Priority:** P0 | P1 | P2 | P3
  - **Target:** <repo or package>
  - **Depends on:** EGOS-NNN (optional)
```

Completed tasks:
```markdown
- [x] EGOS-NNN: <description>
  - **Status:** COMPLETE (<date>)
  - **Deliverable:** <file or measurable output>
```

---

## Priority Classes

| Class | Meaning | Response time |
|-------|---------|--------------|
| P0 | Blocker — blocks shipping or breaks production | Same session |
| P1 | Critical — blocks the next milestone | Next session |
| P2 | Important — should ship this sprint | This week |
| P3 | Backlog — low urgency, high value | When capacity allows |

---

## PR Gate Requirements

Every PR must include in its description:

| Field | Required |
|-------|---------|
| EGOS task IDs resolved (`Closes EGOS-NNN`) | YES |
| Test plan (what was tested, how) | YES |
| Governance check result (if SSOT files changed) | YES |
| Screenshot or smoke test evidence (if UI or agent changed) | YES |
| Link to contract violated (if fixing a governance issue) | YES |

PRs without EGOS task IDs will not be merged.

---

## Sync Flow

### TASKS.md → GitHub Issues (optional, for visibility)

```bash
# Manual for now — no automated sync
# When a P0/P1 task is created, optionally open a GitHub Issue with:
# Title: "[EGOS-NNN] <description>"
# Body: full task description + dependencies
# Label: P0/P1/P2 + area tag
```

### GitHub Issue → TASKS.md (when issue comes from outside)

1. Read the issue
2. Classify it against ECOSYSTEM_CLASSIFICATION_REGISTRY.md — which repo/surface does it belong to?
3. Add to the correct TASKS.md with a new EGOS-NNN ID
4. Close or link the GitHub Issue to the TASKS.md entry
5. If the issue came from an AI session (Grok, AI Studio): follow EGOS-097 reconciliation pass first

---

## Task ID Allocation

- IDs are monotonically increasing: `EGOS-001`, `EGOS-002`, ...
- Current highest: check `grep -o 'EGOS-[0-9]*' TASKS.md | sort -t- -k2 -n | tail -1`
- IDs are never reused — deprecated tasks keep their ID with status `ARCHIVE`

---

## Stale Task Policy

A task is considered **stale** when:
- P1/P2 task with no commit referencing it in > 30 days
- Action: Move to `## Backlog (P3)` section with a note

A task is **closed** when:
- `[x]` marked with Status, Date, and Deliverable
- A PR referencing it has been merged to main

---

*Maintained by: EGOS Kernel*
*Related: EGOS-100, TASKS.md, docs/governance/NEW_PROJECT_GATE.md*
