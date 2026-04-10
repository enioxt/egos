# Benchmark Enforcement Contract — EGOS-098

> **Version:** 1.0.0 | **Created:** 2026-03-30 | **Closes:** EGOS-098
> **Status:** ACTIVE
> **Source:** Multi-agent benchmark analysis (AIOX / SynkraAI) + EGOS governance integration
> **Parent:** WORKTREE_CONTRACT.md (EGOS-099/110), QA Loop Contract (EGOS-101)

This document defines the **enforcement mechanism** for the four benchmark patterns
ingested from pragmatic multi-agent workflow research. Documentation alone is not
governance. Each pattern must have a concrete check point, a violation signature,
a consequence, and a remediation path.

---

## Pattern 1 — Worktree Isolation

> Every task executes in an isolated git worktree. No shared working-directory state
> between concurrent tasks.

### Where It Is Checked

| Surface | Trigger | Tool |
|---------|---------|------|
| Pre-commit hook | Every `git commit` | `scripts/worktree-validator.ts --pre-commit` |
| /start Gate phase | Session initialization | Worktree Orchestration Check (EGOS-110) |
| CI (future) | PR opened/pushed | `bun run worktree:check` |

### Violation Signature

```
# Symptom: commits on main/trunk without worktree registration
$ git log --oneline main | head -5
# → Direct commits from main session, no feat/fix/chore branch

# Symptom: worktrees.json missing entry for active branch
$ cat .guarani/worktrees.json
# → active branch not listed

# Symptom: two tasks share the same branch
$ git worktree list
# → duplicate paths or unexpected working-dir mutations
```

Concrete example of a violation:
```
Agent A is working on EGOS-120 (ui changes) and EGOS-121 (api changes).
Both are edited in the same directory. A commit touches both:
  feat: update ui and fix api endpoint
→ VIOLATION: tasks not isolated, review contamination risk is high.
```

### Consequence

| Severity | Condition | Response |
|----------|-----------|----------|
| WARN | Commit on main without worktree entry | Warning logged; commit not blocked (yet) |
| BLOCK | Branch in worktrees.json with `status: abandoned` being re-used | Commit blocked; requires cleanup first |
| REQUIRE APPROVAL | Frozen zone files edited outside a registered worktree | Human confirm required in PR body |

### Fix

1. Run `bun run worktree:status` — identify unregistered branches.
2. Register the active branch: add entry to `.guarani/worktrees.json`.
3. If abandoned: delete the stale branch, reset the TASKS.md item to `[ ]`, create a fresh worktree.
4. If direct commit to main: open PR from a feature branch retroactively (git branch from the commit SHA).

### Reference

- Full spec: `.guarani/orchestration/WORKTREE_CONTRACT.md`
- Validator: `scripts/worktree-validator.ts`
- Registry: `.guarani/worktrees.json`

---

## Pattern 2 — Parallel Ticket Lanes

> Agents work on different tasks in parallel, each in their own lane. No agent
> holds more than one active `[/]` ticket per session without explicit documentation.

### Where It Is Checked

| Surface | Trigger | Tool |
|---------|---------|------|
| /start Gate phase | Session open | Manual scan: count `[/]` items in TASKS.md |
| /end Phase 4 | Session close | Verify every `[/]` item is either `[x]` or formally parked |
| Pre-commit hook | On TASKS.md change | `scripts/ssot_governance.ts` (warns on multiple `[/]` same session) |

Detection logic (pseudo-script):
```bash
# Count in-progress items
grep -c '^\- \[/\]' TASKS.md
# If result > 1 in a single-agent session: WARN
```

### Violation Signature

```
# TASKS.md shows:
- [/] EGOS-098: Ingest benchmark patterns...
- [/] EGOS-102: Build operator map...
- [/] EGOS-115: Refactor auth module...

# Three concurrent in-progress tasks in one session → parallel lane violation.
# Risk: context bleed, partial commits across tasks, drift.
```

Concrete example of a violation:
```
Session opens. Agent sees EGOS-103 [/] from yesterday.
Agent starts EGOS-115 without closing EGOS-103.
Commits contain changes from both. PR review fails: "What does this PR actually do?"
→ VIOLATION: two open lanes, no explicit parallel-track declaration.
```

### Consequence

| Severity | Condition | Response |
|----------|-----------|----------|
| WARN | >1 `[/]` item at /start | Warning printed: "Multiple in-progress tasks detected. Close one or declare parallel track." |
| WARN | >1 `[/]` item at /end | Warning printed: must document each open item with explicit status note |
| BLOCK (future) | >3 `[/]` items | Hard block on commit if TASKS.md shows more than 3 simultaneous in-progress |

### Fix

**Option A — Serial:** Close the previous task before starting new one.
```
Change: - [/] EGOS-103  →  - [x] EGOS-103 (with evidence)
Then: start EGOS-115
```

**Option B — Explicit Parallel:** Add a parallel-track declaration comment immediately below:
```
- [/] EGOS-098: ... (PARALLEL-TRACK: running alongside EGOS-115, different domains)
- [/] EGOS-115: ... (PARALLEL-TRACK: governance vs UI, no shared files)
```
Parallel tracks MUST touch different file domains (no shared file edits).

---

## Pattern 3 — QA Loop

> No task is marked `[x]` without verifiable evidence of correct behavior.
> Evidence = test output, screenshot, curl response, or governance check.

### Where It Is Checked

| Surface | Trigger | Tool |
|---------|---------|------|
| Pre-commit hook | TASKS.md item changed from `[/]` to `[x]` | `scripts/ssot_governance.ts` — checks for evidence keyword |
| /end Phase 4 | Session close | Manual: verify each `[x]` has evidence in its TASKS.md entry |
| Merge gate | PR opened | TASKS.md entry for the relevant EGOS-NNN must include evidence |

Evidence keywords (any one of these in the task entry satisfies the check):
```
COMPLETE | ✅ | bun run | passing | verified | screenshot | curl | response | log
```

### Violation Signature

```
# TASKS.md shows:
- [x] EGOS-120: Implement new auth flow

# No evidence. No test output. No curl. No screenshot.
# → VIOLATION: task marked done without QA loop.
```

Concrete example of a violation:
```
Agent implements new API endpoint. Marks [x]. Commits.
No `bun test` output, no curl response, no smoke command.
Next agent reads TASKS.md, trusts the [x], ships. Bug discovered in production.
→ VIOLATION: QA loop skipped, false confidence propagated.
```

### Consequence

| Severity | Condition | Response |
|----------|-----------|----------|
| WARN | `[x]` task entry has no evidence keyword | Warning at pre-commit; commit not blocked |
| BLOCK (EGOS-101 target) | QA Loop Contract active + no evidence | Commit blocked until evidence added |
| REQUIRE APPROVAL | Frozen zone task marked `[x]` without evidence | Human confirm required |

### Fix

1. Add evidence to the TASKS.md entry **before** marking `[x]`:
```markdown
- [x] EGOS-120: Implement new auth flow
  - **Evidence:** `bun test` → 12 tests passed, 0 failed
  - **Smoke:** `curl https://api.guard.egos.ia.br/health` → 200 OK
  - **Verified:** 2026-03-30
```
2. If already marked `[x]` without evidence: downgrade to `[/]`, add evidence, re-mark.
3. Full QA Loop spec pending: EGOS-101 (`/qa-loop` contract).

---

## Pattern 4 — File-First Context

> Before acting on any file, read its current state. Never write from memory
> of a previous session. Never assume a file is unchanged since last read.

### Where It Is Checked

| Surface | Trigger | Tool |
|---------|---------|------|
| SSOT Visit Protocol | Any cross-repo or deep-tree file access | DOMAIN_RULES.md §7 |
| Pre-commit hook | Staged files include cross-repo paths | `scripts/ssot_governance.ts` warns if visit not logged |
| Agent protocol | Any agent task that touches existing files | Agent checklist: "Read before Write" |

### Violation Signature

```
# Agent writes to packages/core/src/auth/contracts.ts
# without reading the current file first.
# Result: overwrites changes committed since last session.

# Agent assumes TASKS.md looks like it did 2 sessions ago.
# Writes a patch based on stale mental model.
# Result: duplicate task entries, wrong line offsets, missed items.
```

Concrete example of a violation:
```
New session. Agent recalls EGOS-131 was pending.
Writes "- [/] EGOS-131: ..." to TASKS.md without reading it.
But EGOS-131 was already marked [x] in the previous session.
→ VIOLATION: file-first context skipped, duplicate/regression introduced.
```

### Consequence

| Severity | Condition | Response |
|----------|-----------|----------|
| WARN | SSOT visit log missing for a deep-tree file edited this session | Warning at /end Phase 4 |
| WARN | Cross-repo file edited without visit log entry | Warning printed by ssot_governance.ts |
| BLOCK | Agent invoked in `--exec` mode without `--dry` first | Agent runner blocks (runner.ts enforced) |

### Fix

1. **Always Read before Edit.** Use the Read tool, not memory.
2. **Log the visit** per DOMAIN_RULES.md §7:
   ```
   - [x] SSOT-VISIT 2026-03-30: egos/packages/core/src/auth/contracts.ts → read current state → independent
   ```
3. **For agents:** enforce `--dry` before `--exec` (runner.ts zero-deps rule, DOMAIN_RULES.md §1).
4. **Cross-session continuity:** /start must re-read TASKS.md before making any edits.

---

## Enforcement Matrix Summary

| Pattern | Pre-commit | /start | /end | CI | Manual |
|---------|-----------|--------|------|----|--------|
| Worktree Isolation | BLOCK (frozen zones) / WARN | GATE check | verify | future | worktrees.json |
| Parallel Ticket Lanes | WARN (>1 `[/]`) | WARN (count `[/]`) | WARN (unresolved `[/]`) | — | explicit declaration |
| QA Loop | WARN (no evidence) | — | verify each `[x]` | future (EGOS-101) | evidence keywords |
| File-First Context | WARN (missing visit log) | re-read TASKS.md | verify visit log | — | Read tool discipline |

---

## Wiring Status

| Pattern | Contract Doc | Enforcement Script | Workflow Hook | Status |
|---------|-------------|-------------------|--------------|--------|
| Worktree Isolation | WORKTREE_CONTRACT.md | `scripts/worktree-validator.ts` | /start GATE, pre-commit | ACTIVE |
| Parallel Ticket Lanes | This file | `scripts/ssot_governance.ts` (partial) | /start GATE | PARTIAL |
| QA Loop | EGOS-101 (pending) | — | /end Phase 4 | PENDING |
| File-First Context | DOMAIN_RULES.md §7 | `scripts/ssot_governance.ts` | /start, /end | ACTIVE |

---

## Next Actions

- [ ] EGOS-101: Define QA Loop Contract with stop conditions and evidence schema
- [ ] Add `[/]` count check to `/start` GATE phase in `~/.egos/workflows/start.md`
- [ ] Add evidence-keyword check to `scripts/ssot_governance.ts` for `[x]` transitions
- [ ] Wire parallel-track detection into pre-commit TASKS.md scan

---

*Governance without enforcement is aspiration. This document makes it operational.*
