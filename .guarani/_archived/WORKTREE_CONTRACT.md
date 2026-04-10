# Worktree Orchestration Contract — EGOS-099 / EGOS-110

**Version:** 1.1.0 | **Updated:** 2026-03-30 | **EGOS-099 addendum added**
**Original:** EGOS-110 (2026-03-26) | **Status:** ACTIVE
**Source:** AIOX workflow benchmark analysis + EGOS governance integration

> This contract formalizes the orchestration rules for isolated worktree-based development in EGOS repositories. It ensures predictable team coordination, prevents merge conflicts, and maintains governance integrity across parallel development lanes.

---

## EGOS-099 Quick Reference (Practical Rules)

> Read this section first. The detailed spec follows in sections 1-14.

### Branch Naming (short form)

```
feat/EGOS-NNN-short-description     # new capability
fix/EGOS-NNN-short-description      # bug fix
refactor/EGOS-NNN-short-description # restructure, no behavior change
chore/EGOS-NNN-short-description    # tooling, deps, CI, docs
```

Always include task ID. No ID = no worktree. Max 60 chars.

### Ownership Lock

One worktree = one task = one agent at a time.
Check `.guarani/worktrees.json` before starting. If claimed: stop and wait.
First committed entry wins. Challenger logs conflict in TASKS.md.

### Lifecycle (max 72h)

```
create → work → test → merge → cleanup
```

- Max open: **3 active worktrees** (guideline; 4+ signals planning failure)
- Max age: **72 hours** per worktree before it must be merged or closed
- Abandonment: **no commit in 24h** → status = `abandoned` → delete branch + remove from worktrees.json + reset task to `[ ]`

### Merge Gates

```
[ ] bun run typecheck        — zero TS errors
[ ] bun test                 — zero failing tests
[ ] bun run lint             — zero lint errors
[ ] bun run governance:check — zero SSOT drift
[ ] TASKS.md task marked [x] with evidence
[ ] worktrees.json entry present and updated
[ ] No frozen zone edits without human confirm in PR body
```

### Using Claude Code EnterWorktree / ExitWorktree

```
# Start
EnterWorktree(branch=feat/EGOS-NNN-desc, baseBranch=main)

# Do work, commit

# End
ExitWorktree  ← do NOT exit without committing
```

If two Claude Code sessions attempt EnterWorktree on the same branch: second call fails. Resolve via worktrees.json inspection first.

Example workflow:
```
1. EnterWorktree(feat/EGOS-080-llm-matrix)
2. Write files
3. Update TASKS.md [x]
4. git commit -m "feat(egos-080): LLM orchestration matrix"
5. ExitWorktree
6. Open PR → run merge gates
7. After merge: remove worktree + clean worktrees.json
```

---

---

## 1. Executive Summary

The Worktree Orchestration Contract defines rules for:
- **Branch naming discipline** with semantic prefixes
- **Ownership locks** per worktree to prevent conflicts
- **Lifecycle management** with automatic cleanup
- **Merge gates** for safety and governance compliance
- **Concurrency limits** (max 5 active worktrees per repo)

**Scope:** EGOS kernel + all leaf repositories
**Enforcement:** Pre-commit hooks, pre-flight checks, CI/CD gates
**Keep/Drop Decision:** KEEP (essential for EGOS-111 spec-pipeline workflow)

---

## 2. Naming Rules

All worktrees **must** follow semantic branch naming conventions. The naming rule is **mandatory** and enforced by pre-commit hooks.

### 2.1 Valid Branch Prefixes

```regex
^(feature|fix|docs|chore|refactor|perf|test|ci|security)/[a-z0-9]+-[a-z0-9]+(-[a-z0-9]+)*$
```

**Pattern breakdown:**
- `feature/` — New capability, feature, or agent
- `fix/` — Bug fix or hotfix
- `docs/` — Documentation-only changes
- `chore/` — Dependency updates, cleanup, maintenance
- `refactor/` — Code restructuring without behavior change
- `perf/` — Performance optimization
- `test/` — Test additions or improvements
- `ci/` — GitHub Actions, pre-commit, build changes
- `security/` — Security patch or audit response

**Identifier rules:**
- Must start with lowercase letter
- Use hyphens to separate words (no underscores, no camelCase)
- No uppercase letters
- No special characters except hyphens
- Minimum length: 3 characters (e.g., `fix/x-y` is invalid; use `fix/add-xyz`)

### 2.2 Valid Examples

```
✅ feature/worktree-validator
✅ fix/concurrency-limit-check
✅ docs/orchestration-contract
✅ chore/update-typescript
✅ security/pii-scanner-hardening
✅ perf/memory-optimization
✅ test/validation-edge-cases
```

### 2.3 Invalid Examples

```
❌ feature/WorktreeValidator      (camelCase)
❌ fix_concurrency_limits          (underscores, missing prefix)
❌ newfeature                       (no prefix)
❌ feature/x                        (too short)
❌ Feature/worktree-validator      (uppercase)
❌ feature/worktree.validator      (special char period)
```

---

## 3. Ownership Model

Each active worktree is assigned to **one owner** for the duration of its lifetime. Ownership prevents concurrent edits to the same files and ensures accountability.

### 3.1 Ownership Rules

| Rule | Definition |
|------|-----------|
| **Primary Owner** | The developer who created the worktree; listed in `.guarani/worktrees.json` |
| **Ownership Lock** | Active from branch creation until merge to main |
| **Lock Scope** | Entire branch (prevent override via `git push --force`) |
| **Transfer** | Owner can explicitly transfer to another team member via `bun worktree:transfer <branch> <new-owner>` |
| **Concurrent Edit Conflict** | If two owners commit to same branch, validator rejects and demands coordination |

### 3.2 Ownership Metadata

Each worktree stores ownership in `.guarani/worktrees.json`:

```json
{
  "worktrees": [
    {
      "branch": "feature/worktree-validator",
      "owner": "architect",
      "created_at": "2026-03-26T14:30:00Z",
      "last_commit": "2026-03-26T16:45:00Z",
      "status": "active",
      "files_touched": [
        ".guarani/orchestration/WORKTREE_CONTRACT.md",
        "scripts/worktree-validator.ts"
      ],
      "issue_link": "EGOS-110"
    }
  ]
}
```

### 3.3 Enforcement

- Pre-commit hook verifies branch matches owner's recorded identity
- Validator rejects commits if `git config user.email` ≠ recorded owner email
- CI gates block PR merge if ownership metadata is stale (>30 days)

---

## 4. Lifecycle Management

Worktrees follow a predictable state machine:

```
┌─────────────────────────────────────────────────┐
│                  CREATED                        │
│   (branch exists, owner recorded, age = 0)      │
│                                                 │
│         ↓          ↓           ↓                │
│      ACTIVE    STALE       ABANDONED           │
│   (< 7 days)  (7-30 days)  (> 30 days)        │
│                                                 │
│      ↓           ↓             ↓                │
│   MERGING   PENDING-CLEANUP   AUTO-DELETE      │
│   (ready)   (flagged)         (purged)         │
│                                                 │
│         ↓          ↓                           │
│       MERGED     DELETED                       │
│     (success)   (cleaned up)                   │
└─────────────────────────────────────────────────┘
```

### 4.1 State Definitions

| State | Condition | TTL | Action |
|-------|-----------|-----|--------|
| **CREATED** | Branch exists, metadata recorded | — | Automatic on branch push |
| **ACTIVE** | Last commit < 7 days old | 7 days | Monitor for staleness |
| **STALE** | Last commit 7–30 days old | 30 days | Send Slack/email warning to owner |
| **ABANDONED** | Last commit > 30 days old | Auto-delete | Delete branch + cleanup |
| **MERGING** | PR created, awaiting merge | 14 days | CI/CD validation active |
| **MERGED** | PR merged to main | Archive | Move metadata to `_archived/` |
| **DELETED** | Branch purged | — | Cleanup complete |

### 4.2 Automatic Cleanup

Run `bun worktree:cleanup` daily (via GitHub Actions or CI scheduler):

```bash
# Find abandoned worktrees (> 30 days, no commits)
bun scripts/worktree-validator.ts --cleanup

# Output example:
# Deleted: feature/old-feature (last commit: 2025-12-01)
# Deleted: fix/forgotten-hotfix (last commit: 2025-11-15)
# Total deleted: 2
```

### 4.3 Manual Lifecycle Commands

```bash
# Check current worktree state
bun worktree:status feature/worktree-validator

# Manually extend TTL (owner only)
bun worktree:extend feature/worktree-validator --days 7

# Transfer ownership
bun worktree:transfer feature/worktree-validator alice@egos.local

# Mark for cleanup (owner/maintainer)
bun worktree:retire feature/worktree-validator

# Force delete (maintainer only, audited)
bun worktree:purge feature/worktree-validator --reason "duplicate" --issue EGOS-999
```

---

## 5. Merge Gates (Safety & Governance)

PRs from worktrees must pass mandatory gates before merge:

### 5.1 PR Gate Checklist

| Gate | Check | Enforced By | Failure Action |
|------|-------|-----------|-----------------|
| **Branch name** | Matches regex | Pre-commit + CI | Block PR creation |
| **Ownership** | PR author = branch owner | CI | Require override approval |
| **Single owner** | Only owner commits | CI | Block merge (flag for coordination) |
| **Governance check** | No frozen zone edits | Pre-commit | Block commit |
| **Tests pass** | CI suite green | GitHub Actions | Block merge (mark red) |
| **Sign-off** | PR description has `Signed-off-by:` footer | CI gate script | Block merge |
| **Evidence** | IDE validation checklist completed | PR gate | Require manual override |
| **SSOT alignment** | Docs updated if SSOT touched | Manual review | Require follow-up issue |

### 5.2 Gate Implementation

Gates are enforced by:

1. **Pre-commit hooks** (local machine)
   - File: `.husky/pre-commit`
   - Runs: `bun scripts/worktree-validator.ts --pre-commit`

2. **CI gates** (GitHub Actions)
   - File: `.github/workflows/ci.yml`
   - Runs: `bun scripts/worktree-validator.ts --ci --pr-number ${{ github.event.pull_request.number }}`

3. **Merge gate** (CLI pre-merge validation)
   - File: `scripts/pr-gate.ts`
   - Runs: `bun scripts/pr-gate.ts --file <pr-pack-markdown>`

---

## 6. Concurrency Limits

EGOS enforces a **maximum of 5 active worktrees** per repository to prevent coordination chaos.

### 6.1 Limit Definition

**Active worktree:** A branch that has commits in the last 7 days AND is not merged.

```bash
# Count active worktrees
bun scripts/worktree-validator.ts --count-active

# Output:
# Active worktrees: 3/5
#   1. feature/worktree-validator (2026-03-26, 1 day old)
#   2. fix/ci-error (2026-03-24, 3 days old)
#   3. docs/orchestration-guide (2026-03-22, 5 days old)
```

### 6.2 Enforcement

When limit is reached:

1. **New branch push is blocked** with message:
   ```
   ❌ Concurrency limit reached (5/5)

   Active worktrees:
   1. feature/worktree-validator (3 days old)
   2. fix/ci-error (3 days old)
   3. docs/orchestration-guide (5 days old)
   4. test/validation-suite (1 day old)
   5. chore/update-deps (2 days old)

   Action required:
   - Merge or delete one of the above branches
   - Or extend TTL of a nearly-stale branch (see bun worktree:extend)
   ```

2. **Manual override** (maintainer only):
   ```bash
   git push --force origin feature/new-branch \
     --opt-in-override=EGOS-110 \
     --reason="time-critical hotfix"
   ```

### 6.3 Justification

- **Why 5?** Based on AIOX workflow analysis: typical team (3-4 devs) + testing lane + continuous updates = ~5 parallel tracks before coordination breaks down
- **Not hard limit:** Can be overridden with explicit audit log entry for critical hotfixes
- **Auto-cleanup:** Abandoned branches deleted after 30 days, freeing slots

---

## 7. Validation Script Interface

The authoritative validator is `scripts/worktree-validator.ts`. It runs in multiple contexts:

### 7.1 Pre-Commit Hook Mode

```bash
bun scripts/worktree-validator.ts --pre-commit
```

**Output:** Exit code 0 (pass) or 1 (fail)
**Checks:** Branch name, ownership, file edits against frozen zones
**Speed:** < 2 seconds

### 7.2 CI Mode (GitHub Actions)

```bash
bun scripts/worktree-validator.ts --ci --pr-number 42
```

**Output:** JSON report to stdout + exit code
**Checks:** All 7 merge gates (see section 5.1)
**Speed:** < 10 seconds

### 7.3 Local Status Check

```bash
bun scripts/worktree-validator.ts --status
```

**Output:** Markdown table of all active worktrees
**Checks:** None (reporting only)
**Speed:** < 5 seconds

### 7.4 Cleanup Mode

```bash
bun scripts/worktree-validator.ts --cleanup
```

**Output:** List of deleted branches + count
**Checks:** Identifies abandoned branches (> 30 days)
**Speed:** < 10 seconds
**Dry-run:** Default; add `--exec` to actually delete

---

## 8. JSON Report Schema

Validator outputs machine-readable reports for CI/CD integration:

```json
{
  "schema_version": "1.0.0",
  "timestamp": "2026-03-26T16:45:00Z",
  "repository": "egos",
  "context": "ci",
  "summary": {
    "total_worktrees": 3,
    "active_worktrees": 3,
    "stale_worktrees": 0,
    "abandoned_worktrees": 0,
    "concurrency_limit": 5,
    "concurrency_used": 3,
    "concurrency_status": "healthy"
  },
  "checks": {
    "branch_naming": {
      "status": "pass",
      "message": "Branch matches semantic naming rule"
    },
    "ownership": {
      "status": "pass",
      "owner": "architect",
      "verified_at": "2026-03-26T16:45:00Z"
    },
    "single_ownership": {
      "status": "pass",
      "unique_authors": 1
    },
    "frozen_zone": {
      "status": "pass",
      "files_touched": ["scripts/worktree-validator.ts"],
      "frozen_files_touched": 0
    },
    "lifecycle": {
      "status": "pass",
      "age_days": 1,
      "ttl_remaining_days": 6,
      "lifecycle_state": "ACTIVE"
    }
  },
  "gates": [
    {
      "name": "branch_naming",
      "status": "pass",
      "weight": 1
    },
    {
      "name": "ownership_verified",
      "status": "pass",
      "weight": 1
    },
    {
      "name": "tests_passing",
      "status": "pending",
      "weight": 2
    }
  ],
  "warnings": [],
  "errors": [],
  "exit_code": 0
}
```

---

## 9. Integration Points

### 9.1 Pre-Commit Hook

**File:** `.husky/pre-commit`

```bash
#!/bin/sh
# Pre-commit hook: validate worktree ownership + naming
bun scripts/worktree-validator.ts --pre-commit || exit 1
```

### 9.2 GitHub Actions CI

**File:** `.github/workflows/ci.yml` (add to existing workflow)

```yaml
- name: Validate worktree contract
  run: |
    REPORT=$(bun scripts/worktree-validator.ts --ci --pr-number ${{ github.event.pull_request.number }})
    echo "$REPORT" > /tmp/worktree-report.json
    # Fail if critical gates don't pass
    EXIT_CODE=$(jq '.exit_code' /tmp/worktree-report.json)
    exit $EXIT_CODE
```

### 9.3 /start Pre-Flight Checks

**File:** `.agents/workflows/start-workflow.md` (or `.windsurf/workflows/start.md`)

Add to the pre-flight section:

```markdown
## Pre-flight: Worktree Orchestration Check

Running: `bun scripts/worktree-validator.ts --status`

- Concurrency: 3/5 active worktrees ✅
- Abandoned branches: 0 ✅
- Ownership locks: All verified ✅
```

---

## 10. Examples

### 10.1 Example: Create Valid Worktree

```bash
# Developer creates a feature worktree
git checkout -b feature/user-authentication-guard

# Edits files following governance rules
echo "export async function authenticateUser(...) {}" >> src/auth.ts

# Pre-commit validator runs automatically
bun scripts/worktree-validator.ts --pre-commit
# ✅ Branch name valid
# ✅ Ownership recorded: alice@egos.local
# ✅ No frozen zone edits
# Exit: 0 (PASS)

# Commit succeeds
git add src/auth.ts
git commit -m "feat: add user authentication guard"

# Push succeeds
git push origin feature/user-authentication-guard
```

Metadata recorded in `.guarani/worktrees.json`:

```json
{
  "branch": "feature/user-authentication-guard",
  "owner": "alice@egos.local",
  "created_at": "2026-03-26T14:30:00Z",
  "status": "active",
  "files_touched": ["src/auth.ts"],
  "issue_link": "EGOS-50"
}
```

### 10.2 Example: Concurrency Limit Reached

```bash
# Attempt 6th concurrent worktree
git checkout -b feature/new-experiment

bun scripts/worktree-validator.ts --pre-commit
# ❌ Concurrency limit reached (5/5)
#
# Active worktrees:
#   1. feature/user-auth (3 days old)
#   2. fix/pii-scanner (2 days old)
#   3. docs/governance-update (5 days old)
#   4. test/validation-suite (1 day old)
#   5. chore/upgrade-typescript (2 days old)
#
# Action: Merge or delete one, or override with --emergency

git push origin feature/new-experiment --emergency --reason="critical-bug"
# (Creates audit log entry: who, when, why, issue)
```

### 10.3 Example: Stale Worktree Cleanup

```bash
# Daily cleanup job (via CI scheduler)
bun scripts/worktree-validator.ts --cleanup --dry

# Output:
# Abandoned branches found (> 30 days, no commits):
#   - feature/old-idea (last commit: 2025-12-10)
#   - fix/forgotten-hotfix (last commit: 2025-11-28)
#
# Total to delete: 2
# Run with --exec to apply

bun scripts/worktree-validator.ts --cleanup --exec
# Deleted: feature/old-idea
# Deleted: fix/forgotten-hotfix
# Archived metadata: .guarani/worktrees/_archived/2026-03/
```

---

## 11. Troubleshooting

### Problem: "Branch name invalid"

**Cause:** Branch doesn't match semantic naming rule
**Fix:**

```bash
# Rename your branch
git branch -m feature/myfeature feature/my-feature

# Rename on remote
git push origin :feature/myfeature
git push origin feature/my-feature
```

### Problem: "Concurrency limit reached"

**Cause:** 5 or more active worktrees already exist
**Fix:**

```bash
# Option 1: Merge an old branch
git checkout main && git pull
git checkout feature/old-work && git merge main && git push

# Option 2: Extend TTL of stale branch to prevent deletion
bun worktree:extend feature/old-work --days 7

# Option 3: Force-push with emergency override (maintainer approval required)
git push --emergency --reason="EGOS-999: critical-security-patch"
```

### Problem: "Ownership mismatch"

**Cause:** Committer email ≠ recorded owner
**Fix:**

```bash
# Check recorded owner
git log --all --format="%an <%ae>" | head -1

# Update git config locally
git config user.email alice@egos.local

# Retry commit
git commit --amend --no-edit
```

---

## 12. Acceptance Criteria (EGOS-110)

- ✅ Contract document written with formal specification
- ✅ Naming rules defined with regex patterns and examples
- ✅ Ownership model with metadata schema documented
- ✅ Lifecycle state machine with TTL rules
- ✅ Merge gates defined and numbered
- ✅ Concurrency limit (max 5) enforced
- ✅ Validation script interface specified
- ✅ JSON report schema defined
- ✅ Integration points for pre-commit, CI, and `/start` identified
- ✅ Examples with 3+ valid worktrees created
- [ ] `scripts/worktree-validator.ts` implementation (NEXT)
- [ ] Integration into `/start` pre-flight checks (NEXT)
- [ ] Functional test proof with real worktrees (NEXT)

---

## 13. Blockers & Dependencies

- **Predecessor:** EGOS-099 (Define base contracts) ✅ Complete
- **Blocking:** EGOS-111 (Spec Pipeline Workflow Contract) — depends on worktree contract
- **Implementation:** All TypeScript/Bun tooling in place

---

## 14. Keep/Drop Analysis (AIOX)

**Decision:** KEEP ✅

**Rationale:**
- **High signal:** Worktree isolation + ownership locks are core to multi-developer coordination
- **EGOS alignment:** Fits cleanly into kernel governance + pre-commit/CI gate ecosystem
- **Minimal overhead:** Validator runs in <2s pre-commit, <10s CI
- **Reusable:** Applied identically to all leaf repos via symlinks
- **Blocker removal:** Unblocks EGOS-111 (spec-pipeline) and subsequent governance initiatives

---

## References

- **AIOX Source:** `SynkraAI/aiox-core` (worktree orchestration benchmark)
- **Related Contract:** `.guarani/orchestration/GATES.md`
- **Implementation:** `scripts/worktree-validator.ts` (EGOS-110 continuation)
- **Successor:** `.guarani/orchestration/SPEC_PIPELINE_CONTRACT.md` (EGOS-111)
- **Evidence:** `docs/_current_handoffs/` (session notes with functional examples)
