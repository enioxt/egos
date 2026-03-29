# QA Loop Contract

> **SSOT Owner:** `egos/docs/governance/QA_LOOP_CONTRACT.md`
> **Version:** 1.0.0 | **Created:** 2026-03-29 | **Status:** ACTIVE
> **Task:** EGOS-101

---

## Purpose

Defines the `/qa-loop` protocol: how to verify a change is working end-to-end, when to re-run tests, and when to stop.

---

## When to Run a QA Loop

Run a QA loop when:
- A bug fix is applied and you want to confirm it doesn't regress
- A new feature is complete and needs smoke testing before PR
- CI fails on a PR and you need to reproduce locally
- Any change touches a `packages/` module that is consumed by leaf repos

---

## QA Loop Steps

### Step 1: Type Check
```bash
bun run typecheck
# Must pass: 0 errors
```

### Step 2: Unit Tests
```bash
bun test packages/guard-brasil/src/guard.test.ts
bun test packages/shared/src/__tests__/
# All tests must pass. Zero allowed failures.
```

### Step 3: Agent Lint
```bash
bun run agent:lint
# All agents must pass contract
```

### Step 4: Governance Check (if SSOT files changed)
```bash
bun run governance:check
# Must pass or output actionable drift report
```

### Step 5: Smoke Test (if applicable)
For `guard-brasil` changes:
```bash
bun run packages/guard-brasil/src/demo.ts
# Output must include clean pass for all test cases
```

For agent changes:
```bash
bun run agent:run <agent-id> dry_run
# Must complete without uncaught errors
```

---

## Test Rerun Policy

| Scenario | Action |
|----------|--------|
| Single test fails, change is unrelated | Fix the test or skip with documented reason |
| Multiple tests fail after a change | Revert the change and investigate root cause before retrying |
| Flaky test (passes on rerun) | Mark as known flaky in a comment, open TASKS.md entry |
| Pre-commit hook fails | Fix the underlying issue — **do not use `--no-verify`** unless explicitly authorized |

---

## Stop Conditions

The QA loop is **done** when:
- [ ] `bun run typecheck` passes
- [ ] All unit tests pass
- [ ] `bun run agent:lint` passes
- [ ] `bun run governance:check` passes (if SSOT changed)
- [ ] Smoke test completes without error (if applicable)

The QA loop **should stop** (do not retry blindly) when:
- Same test fails 3 times with the same error — stop and diagnose root cause
- `tsc` errors > 5 and all from the same file — stop and fix the file before re-running
- Governance check reports drift > 3 files — run `governance:sync:exec` then re-check

---

## Browser/DevTools Verification (for web surfaces)

When changes affect `egos-lab` or any web app:

1. Open the app in browser
2. Open DevTools Console — must be zero `[Error]` entries for the changed flow
3. Open Network tab — no 5xx responses during the test flow
4. Record the verification with a screenshot in the PR description

This is **required** for any PR touching a web app's core user flow.

---

*Maintained by: EGOS Kernel*
*Related: EGOS-101, package.json scripts, .husky/pre-commit*
