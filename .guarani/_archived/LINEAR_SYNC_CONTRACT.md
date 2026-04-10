# LINEAR_SYNC_CONTRACT.md — EGOS-100

> **Version:** 1.0.0
> **Created:** 2026-03-30
> **Owner:** EGOS kernel governance
> **Status:** Contract defined — Linear not yet adopted (see Section 1)

This contract defines WHEN and HOW the EGOS ecosystem would adopt Linear for external issue tracking, and what the sync behavior would look like. TASKS.md remains the SSOT at all times.

---

## 1. Trigger for Adoption

Linear is adopted **only when ALL of the following conditions are true:**

1. TASKS.md exceeds **500 lines** after a monthly clarity review that has already pruned stale items
2. **More than 50 open tasks** require cross-person assignment or external visibility (e.g. contractors, partners)
3. At least **2 active contributors** are working in parallel and need collision-free assignment
4. The cost of manual coordination (missed tasks, duplicate work) is measurable

Until all four conditions are met, TASKS.md alone is sufficient. Adopting Linear prematurely creates sync overhead without benefit.

**Current state (2026-03-30):** Conditions NOT met. Single primary contributor. Do not adopt yet.

---

## 2. Task Decomposition Schema

When adoption is triggered, each TASKS.md entry maps to a Linear issue as follows:

### 2.1 TASKS.md Entry Format

```
- [ ] EGOS-NNN: <title> — <description> — **<status>**
  - <sub-item>
  - Contract/evidence: <path>
```

### 2.2 Linear Issue Mapping

| TASKS.md Field | Linear Field | Transformation Rule |
|---------------|-------------|---------------------|
| `EGOS-NNN` | Issue identifier (label) | Keep as-is; use as external ref tag |
| `<title>` | Issue title | Max 70 chars; strip markdown |
| `<description>` | Issue description | Full text + link to TASKS.md line |
| Priority class (see §3) | Priority | P0→Urgent, P1→High, P2→Medium, P3→Low |
| Sub-items | Checklist items | Each bullet becomes a sub-task |
| Contract path | Attachment / description link | Relative path from repo root |
| `[x]` done | Issue state: Done | Auto-close on sync |
| `[/]` in-progress | Issue state: In Progress | |
| `[ ]` open | Issue state: Todo | |

### 2.3 Required Labels

Every synced issue must carry at minimum:

- `egos` — marks it as an EGOS ecosystem task
- One of: `kernel` | `egos-lab` | `guard-brasil` | `cross-repo` — scope label
- One of: `P0` | `P1` | `P2` | `P3` — priority label
- One of: `governance` | `product` | `infra` | `docs` | `security` — domain label

---

## 3. Priority Classes

| Class | Label | Definition | Examples |
|-------|-------|------------|---------|
| **P0** | Urgent | Blocking revenue or a live production incident. Must be resolved within 24h. | API down, payment blocked, security breach, M-007 emails unsent |
| **P1** | High | Current sprint work. Blocking next milestone. Resolve within the sprint (7 days). | Guard Brasil demo blockers, integration release gate failures |
| **P2** | Medium | Backlog — planned for next 30 days. No hard deadline. | New capability modules, governance contracts, cross-repo rollouts |
| **P3** | Low | Someday / nice-to-have. Reviewed monthly. Auto-archive after 90 days with no progress. | Research ideas, aspirational agents, exploratory integrations |

**Classification rule:** When in doubt, ask "does this block a human from doing their job today?" If yes → P1. "Does it block revenue this week?" → P0.

---

## 4. Required Evidence at PR Gate

Every pull request must satisfy ONE of the following:

**Option A — Linear linked:**
```
## Fixes
Linear: EGOS-NNN (https://linear.app/egos/issue/EGOS-NNN)
```

**Option B — TASKS.md entry checked:**
```
## Fixes
TASKS.md: EGOS-NNN marked [x] in this PR (line NNN)
```

**Option C — Housekeeping (no task):**
```
## Type
chore: no associated task (dependency update / typo fix / formatting)
```

Option C is only valid for changes with zero behavioral impact. Any new capability, fix, or governance change requires Option A or B.

The pre-commit hook at `.guarani/orchestration/GATES.md` enforces this check before merge to `main`.

---

## 5. Sync Direction

**TASKS.md is SSOT. Linear is a view.**

```
TASKS.md  →  /linear-sync skill  →  Linear issues
   ↑                                      ↓
   |________________ NEVER _______________|
```

Rules:
- Changes made directly in Linear are **not authoritative** — they will be overwritten on next sync
- If a task is closed in Linear, the `/linear-sync` skill will re-open it unless TASKS.md also shows `[x]`
- If a task is added in Linear without a TASKS.md entry, it is flagged as `shadow-task` and must be migrated to TASKS.md within 48h or auto-closed
- No Linear issue may set priority without a corresponding TASKS.md priority annotation

---

## 6. `/linear-sync` Skill Spec

When implemented, the `/linear-sync` skill would execute the following:

### 6.1 Trigger

```
/linear-sync [--dry] [--filter=P0,P1] [--since=YYYY-MM-DD]
```

- `--dry`: Print the diff without writing to Linear
- `--filter`: Only sync tasks matching given priority classes
- `--since`: Only process tasks modified after this date

### 6.2 Steps

1. **Parse TASKS.md** — Extract all `EGOS-NNN` entries, their status markers (`[ ]`, `[/]`, `[x]`), titles, and priority hints
2. **Fetch Linear state** — Query Linear API for all issues tagged `egos`
3. **Diff** — Compare TASKS.md state vs Linear state for each EGOS-NNN
4. **Create** — For each TASKS.md entry with no matching Linear issue: create issue with mapped fields (§2.2)
5. **Update** — For each TASKS.md entry with a matching Linear issue where fields diverge: update title, description, priority, status
6. **Flag shadows** — For each Linear issue with no matching TASKS.md entry: add `shadow-task` label + comment
7. **Report** — Output sync summary: N created, N updated, N shadows flagged, N skipped

### 6.3 Required Config

```json
// ~/.egos/config/linear.json (never committed)
{
  "apiKey": "lin_api_...",
  "teamId": "...",
  "projectId": "...",
  "labelMap": {
    "P0": "label_id_urgent",
    "P1": "label_id_high",
    "P2": "label_id_medium",
    "P3": "label_id_low"
  }
}
```

### 6.4 Evidence Contract

The skill must write a sync log to `docs/_current_handoffs/linear-sync-YYYY-MM-DD.md` with:
- Timestamp of sync
- Number of issues created/updated/flagged
- Any errors (Linear API failures, parse failures)
- `--dry` output if run in dry mode

---

- [x] **EGOS-100** — Linear/Issue Sync Contract defined (2026-03-30)
