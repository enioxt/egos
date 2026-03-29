# Worktree Orchestration Contract

> **SSOT Owner:** `egos/docs/governance/WORKTREE_CONTRACT.md`
> **Version:** 1.0.0 | **Created:** 2026-03-29 | **Status:** ACTIVE
> **Task:** EGOS-099

---

## Purpose

Rules for using git worktrees in the EGOS ecosystem. Prevents branch sprawl, ownership conflicts, and stale worktrees from accumulating.

---

## Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feat/<scope>-<short-description>` | `feat/guard-brasil-mcp-server` |
| Fix | `fix/<scope>-<issue-or-description>` | `fix/atrian-false-positive` |
| Governance / docs | `docs/<scope>` | `docs/agent-claim-contract` |
| Automated agent | `claude/<task-slug>-<id>` | `claude/investigate-guarda-brasil-JHVzU` |
| Experiment | `exp/<name>` | `exp/atomic-search-benchmark` |
| Release | `release/v<version>` | `release/v0.2.0` |

**Rules:**
- No spaces, no uppercase in branch names
- `<scope>` = package or doc area (`guard-brasil`, `shared`, `governance`, `agents`)
- Maximum branch name length: 60 characters

---

## Ownership Locks

Each active branch has exactly one owner:

| Owner | Creates | Merges | Abandons |
|-------|---------|--------|---------|
| Human | Any type | Any type | Any time |
| Claude Code | `claude/*` only | No — human merges | After push |
| Windsurf/Cascade | `feat/*`, `fix/*`, `docs/*` | No — human merges | After PR |

**No two owners may commit to the same branch concurrently.** If two sessions are open, only one may be writing to a given branch.

---

## Lifecycle

```
create branch → develop → push → PR (if needed) → merge to main → delete branch
```

| Stage | Max duration | Action if exceeded |
|-------|-------------|-------------------|
| Development | 7 days | Either merge or create TASKS.md entry explaining delay |
| Awaiting review | 3 days | Ping or re-open with updated scope |
| Merged but not deleted | 1 day | Auto-delete via GitHub branch cleanup |
| Abandoned (no commits) | 3 days | Delete without PR |

---

## Cleanup Rules

1. **After merge:** Delete the branch immediately (GitHub auto-delete on merge is ON)
2. **After 7 days with no commits:** Branch is stale — delete or close with explanation in TASKS.md
3. **Claude branches (`claude/*`):** Always delete after push. Claude Code does not maintain long-lived branches.
4. **Experiment branches (`exp/*`):** May be kept for 14 days, then must either be promoted to `feat/*` or deleted.

---

## Merge Gates

All branches must pass before merging to `main`:

| Gate | Check | Required |
|------|-------|---------|
| TypeScript | `tsc --noEmit` passes | YES |
| Secret scan | gitleaks clean | YES |
| Frozen zones | Not modified without proof-of-work | YES |
| Agent lint | `bun run agent:lint` passes if `agents.json` changed | YES |
| Governance check | `bun run governance:check` passes if SSOT files changed | YES |
| Doc proliferation | No timestamped docs added | YES |

---

## Max Concurrency

| Scope | Max active branches |
|-------|-------------------|
| Per developer | 3 (1 main feature, 1 fix, 1 experiment) |
| Claude Code automation | 1 per session |
| Total across ecosystem | 10 (audit and clean if exceeded) |

---

## Worktree vs Normal Branch

Use `git worktree add` when:
- You need to run two branches simultaneously (e.g., test fix while developing feature)
- You are doing a long-running experiment that must not block main development

Always:
```bash
# Create
git worktree add ../egos-exp exp/<name>

# List
git worktree list

# Remove when done
git worktree remove ../egos-exp
git branch -d exp/<name>
```

---

*Maintained by: EGOS Kernel*
*Related: EGOS-099, docs/governance/NEW_PROJECT_GATE.md*
