# QA Loop Contract — EGOS Framework

> **Version:** 1.0.0 | **Created:** 2026-03-30 | **EGOS-101**
> **Owner:** kernel | **Enforcement:** pre-merge gate + PR evidence field

---

## 1. When to Run QA

Run QA after **any code change that could break existing behavior**, including:

- Any modification to a `src/` or `packages/` file
- Any change to API routes, middleware, or auth logic
- Any dependency bump (`package.json`, `bun.lockb`)
- Any environment variable addition or rename
- Any Docker/Caddy/infra config change
- Schema migrations (Supabase, Prisma, Neo4j)

Skip QA only for: pure documentation changes (`docs/**/*.md`), comment-only edits, or cosmetic whitespace — **and only if you are certain no behavior is affected.**

---

## 2. QA Levels

Pick the **minimum level** appropriate to the change scope. Higher is always acceptable.

### L0 — Compile Check
**Trigger:** Any change to TypeScript/JS source files.
```bash
bun run build
# or type-check only (faster):
bun run typecheck   # tsc --noEmit
```
**Pass condition:** Zero errors. Warnings allowed but must be documented.

---

### L1 — Unit Tests
**Trigger:** Any change to a module that has `*.test.ts` files.
```bash
bun test
# Scoped:
bun test packages/core/src/guards/
```
**Pass condition:** 0 failures for the affected module. New tests must accompany new logic.

---

### L2 — Integration Smoke
**Trigger:** Any change to API routes, middleware, or deployed services.
```bash
# Guard Brasil API
curl -s -o /dev/null -w "%{http_code}" https://guard.egos.ia.br/health
curl -s -X POST https://guard.egos.ia.br/v1/inspect \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $GUARD_API_KEY" \
  -d '{"input":"CPF 123.456.789-00"}' | jq .decision

# Local dev
curl -s http://localhost:3099/health
```
**Pass condition:** HTTP 2xx response. Decision field populated. Latency <500ms.

---

### L3 — Full E2E
**Trigger:** Changes to frontend flows, auth, payment, or major cross-service workflows.
```bash
# Playwright (if configured)
bunx playwright test

# Manual walkthrough checklist:
# 1. Login → dashboard loads
# 2. API call from dashboard → result displayed
# 3. Error state handled (bad input, 401, 500)
# 4. Mobile viewport: no layout breakage
```
**Pass condition:** All checklist items pass. Screenshot evidence attached to PR.

---

## 3. Stop Conditions

The following failures are **hard blocks** — do not merge, do not bypass.

| Condition | Level | Action |
|-----------|-------|--------|
| Any compilation error | L0 | Hard block. Fix before anything else. |
| Any test failure in affected module | L1 | Hard block. Fix or explicitly exclude with justification. |
| L2 returns non-2xx (unless expected) | L2 | Hard block. Verify service health, rollback if needed. |
| L3 manual walkthrough fails core flow | L3 | Hard block. Revert or hotfix. |

**Exception:** A non-2xx L2 result is allowed only if the PR explicitly documents the expected status code and the reason (e.g., a 404 for a route being intentionally removed).

---

## 4. Evidence Format

Every PR or commit touching runtime code **must include** a QA evidence line in the description or commit body:

```
QA: L[level] — [command run] → [result] [timestamp]
```

### Examples

```
QA: L0 — bun run typecheck → 0 errors 2026-03-30T14:22Z
QA: L1 — bun test packages/core/src/guards/ → 12/12 pass 2026-03-30T14:25Z
QA: L2 — curl guard.egos.ia.br/health → 200 OK 4ms 2026-03-30T14:30Z
QA: L3 — Playwright 23/23 pass + manual walkthrough ✓ 2026-03-30T15:00Z
```

Multiple levels can be stacked:
```
QA: L0 — bun run typecheck → 0 errors 2026-03-30T14:22Z
QA: L1 — bun test → 47/47 pass 2026-03-30T14:25Z
QA: L2 — curl /health → 200 OK 2026-03-30T14:27Z
```

---

## 5. Rerun Policy

**Flaky tests** (tests that fail intermittently without code change):

1. Rerun up to **3 times** before escalating.
2. If a test fails on retry 3, it is a **real failure** — treat as L1 block.
3. Document flakiness in the PR with the rerun count:
   ```
   QA: L1 — bun test → FLAKY: 2/3 retries pass. Escalating. 2026-03-30T14:30Z
   ```
4. Escalation path: open a `fix/flaky-test-<name>` worktree (per WORKTREE_CONTRACT.md), fix root cause, then merge.

**Never** mark a test as skipped to unblock a PR without creating a tracking task (EGOS-NNN) with P1 priority or higher.

---

## Related Contracts

- [`WORKTREE_CONTRACT.md`](./WORKTREE_CONTRACT.md) — isolation model for parallel work
- [`INTEGRATION_RELEASE_CONTRACT.md`](./INTEGRATION_RELEASE_CONTRACT.md) — release gate evidence
- [`AGENT_CLAIM_CONTRACT.md`](./AGENT_CLAIM_CONTRACT.md) — proof requirements for agent claims
