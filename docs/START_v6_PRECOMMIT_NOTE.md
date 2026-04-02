# /start v6.0 — Pre-Commit Hook Integration (FROZEN ZONE)

**Status:** ⚠️ BLOCKED — `.husky/pre-commit` is a FROZEN ZONE  
**Date:** 2026-04-02  
**Issue:** Need to integrate health check into pre-commit, but file cannot be modified without explicit approval

---

## Problem

The `.husky/pre-commit` file is marked as FROZEN in the pre-commit hook itself:

```bash
for frozen in \
  "agents/runtime/runner.ts" \
  "agents/runtime/event-bus.ts" \
  ".husky/pre-commit"  # ← FROZEN
  ...
```

This prevents adding the /start v6.0 health check as [2/5] validation step.

**Error message:**
```
❌ BLOCKED: Frozen zone files modified.
   To override: git commit --no-verify (requires proof-of-work in message)
```

---

## Solution Options

### Option A: User Manual Action (Recommended)
Requires explicit user approval + proof-of-work in commit message.

```bash
git add .husky/pre-commit
git commit --no-verify -m "chore(pre-commit): integrate /start v6.0 health checks

This is an authorized modification of a FROZEN ZONE file.

Proof-of-work: Adding health check as [2/5] validation step to catch system health issues early. Benefits:
- Early blocker detection (fails fast before tsc/ssot/tests)
- API availability check (Guard Brasil, Supabase)
- Type safety validation
- Non-blocking on jq (graceful fallback)

Intended change:
- Move TypeScript check to [2.5/5]
- Add health check [2/5]
- Keep all other checks intact

Verified: bun scripts/start-v6.ts --json works correctly, jq parsing valid

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

### Option B: Create New Hook File (Alternative)
Instead of modifying `.husky/pre-commit`, create a new standalone hook:

```bash
# .husky/pre-commit-health
#!/bin/bash
set -e
echo "🔍 Pre-commit health check..."
HEALTH=$(bun scripts/start-v6.ts --json 2>/dev/null)
if [ $(echo "$HEALTH" | jq -r '.validation.gates_pass') != "true" ]; then
  echo "$HEALTH" | jq '.blockers'
  exit 1
fi
```

Then enable in `.husky/pre-commit`:
```bash
# In pre-commit, after gitleaks check:
bash .husky/pre-commit-health || exit 1
```

⚠️ **Issue:** Still requires modifying the FROZEN `.husky/pre-commit`

### Option C: GitHub Actions Only (Current State)
✅ **Already implemented** — health check in CI pipeline  
✅ **Non-blocking** — doesn't prevent local commits  
✅ **Catches issues** — before PR is merged

```yaml
.github/workflows/ci.yml:
- name: Session health check (/start v6.0)
  run: |
    HEALTH=$(bun scripts/start-v6.ts --json)
    ...
```

**Trade-off:** Issues only caught after push to GitHub

---

## Current State

### ✅ Implemented
- GitHub Actions health check (`.github/workflows/ci.yml`)
- `/start v6.0` core engine (fully functional)
- Documentation and design specification
- TASKS tracking (START-001..009)

### ⏳ Pending
- Pre-commit hook integration (requires approval)
- Per-commit validation (blocks bad state locally)

---

## Recommendation

**Use Option A** (User Manual Approval):

1. When ready to enforce pre-commit validation:
   ```bash
   git add .husky/pre-commit
   git commit --no-verify -m "chore(pre-commit): integrate /start v6.0 health checks\n\nProof-of-work: ..."
   ```

2. This is a one-time change with explicit oversight
3. After that, health checks run on every commit

---

## Evidence & Validation

### /start v6.0 Ready
- ✅ `bun scripts/start-v6.ts --json` works
- ✅ JSON output valid (jq parseable)
- ✅ Exit codes correct (0 = pass, 1 = fail)
- ✅ Performance < 30s (suitable for pre-commit)

### Pre-Commit Impact
- No slowdown (gate #2 out of 8)
- Non-blocking fallback if jq missing
- Informative blockers + recommendations

---

## Implementation Checklist

When user approves:

- [ ] User adds `.husky/pre-commit` changes with --no-verify
- [ ] Pre-commit hook validates health on every commit
- [ ] Local failures shown immediately
- [ ] GitHub Actions as secondary check (redundant but safe)
- [ ] Document approved in TASKS.md (START-005.1)

---

**Next Action:** Await user approval or explicit request to apply Option A.

See also: `docs/START_v6_INTEGRATION.md` (full implementation guide)
