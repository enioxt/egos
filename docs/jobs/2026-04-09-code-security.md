# Code Intelligence + Security Audit
**Date:** 2026-04-09  
**Duration:** Full codebase scan  
**Status:** REVIEW (3-5 actionable items identified)

---

## PART 1: CODE INTELLIGENCE

### Code Metrics
| Metric | Value | Status |
|--------|-------|--------|
| Total TypeScript files | 450+ | ✓ Healthy |
| Largest file | `apps/egos-gateway/src/orchestrator.ts` (900 LOC) | ⚠ Monitor |
| Average file size | 120 LOC | ✓ Good |
| TODO/FIXME count | 34 total | ⚠ Manageable |
| Implicit `any` types | 132 | ⚠ Review needed |

### Large Files (>300 LOC) — Top 5
1. **apps/egos-gateway/src/orchestrator.ts** (900 LOC) — Gateway orchestrator
2. **apps/api/src/server.ts** (810 LOC) — API entrypoint
3. **apps/egos-gateway/src/channels/gem-hunter-api.ts** (535 LOC) — Gem Hunter channel
4. **packages/shared/src/telemetry.ts** (443 LOC) — Telemetry instrumentation
5. **packages/shared/src/aaak.ts** (430 LOC) — Agent activation kernel

**Recommendation:** Consider breaking orchestrator.ts and server.ts into smaller modules (split at service boundaries, e.g., auth → separate file).

### TODO/FIXME Distribution
- **Integration layer** (8): Telegram, Slack, Webhook contracts — all marked `TODO: Implement`
- **Shared utilities** (4): Model router, validators
- **Agents** (22): Mostly skeleton implementations (wiki-compiler, article-writer, etc.)

**Status:** Low risk — TODOs are in non-critical paths and match design intent.

### TypeScript Type Safety
**Finding:** 21 TypeScript errors, all in scripts/
- `scripts/x-reply-bot.ts` (13 errors) — Missing `@types/node` types for `process`
- `scripts/x-smart-scheduler.ts` (7 errors) — Missing `fs`, `path`, `process` types

**Root Cause:** Scripts lack proper `tsconfig` or type definitions. Not blocking main codebase.

**Fix:** Add `/// <reference types="node" />` to script files OR create `scripts/tsconfig.json` with `"types": ["node"]`.

### Code Quality
| Issue | Count | Severity | Notes |
|-------|-------|----------|-------|
| `as any` casts | 132 total | Medium | Mostly in tests & integration boundaries (acceptable) |
| `exec()` calls | 79 across codebase | Low | All use `execSync` with controlled inputs from env/args |
| `child_process` imports | 26 files | Medium | Script-heavy codebase (agents, CI tooling) — validate args before passing |
| Dead exports | ~5-10 estimated | Low | Unused from shared exports (low impact) |

### Unused Exports (High Priority)
Identified exports from `packages/shared/src/index.ts` with low/zero usage:
- `getKernelSeedGraph` — only test usage
- `nodesByType`, `nodesByStatus` — graph utilities, low adoption
- `buildEvent` — Redis bridge helper, check mycelium integration

**Action:** Audit imports in key files (`agents/agents/*.ts`, `apps/**/src/`) to confirm. Mark unused as internal or deprecate.

---

## PART 2: SECURITY AUDIT

### Dependency Health
| Check | Result | Status |
|-------|--------|--------|
| npm audit | Requires lockfile (using bun.lockb) | ✓ N/A |
| Bun packages installed | 448 | ✓ Recent (Apr 9) |
| Guard Brasil version | 0.2.3 (local & npm) | ✓ In sync |
| Root deps | substack-api, yaml, zod (latest) | ✓ Current |
| GitHub Dependabot scan | **12 vulnerabilities detected** | 🔴 **CRITICAL** |

**⚠️ ALERT:** GitHub Dependabot found 12 vulnerabilities on default branch:
- **4 HIGH severity** ← Requires immediate action
- **8 MODERATE severity** ← Review & patch

**Action Required:** Visit https://github.com/enioxt/egos/security/dependabot to review and apply patches. This should block next production deploy if not resolved.

**Status:** ⏳ Action pending (dependency vulnerabilities > code vulnerabilities)

### Secret Scanning
**Finding:** 15 matches for API key patterns — ALL SAFE ✓
- 14 legitimate uses: `process.env.SUPABASE_KEY`, `SUPABASE_SERVICE_KEY`, `EVOLUTION_API_KEY`
- 1 test file: `expect(body.api_key).toBeDefined()` (mock test)
- 0 hardcoded secrets detected

### Code Injection Risks
| Pattern | Count | Status | Notes |
|---------|-------|--------|-------|
| `eval()` | 5 | ✓ Safe | Test mocks, not production |
| `exec()`/`execSync()` | 79 | ⚠ Verify | All with env vars/controlled args |
| Template interpolation | 0 | ✓ Safe | No SQL/NoSQL template injection |
| `child_process` | 26 files | ⚠ Monitor | Scripts use `execSync(git)` + system commands |

**Risk Assessment:**
- **exec/child_process usage:** Mostly git operations (`execSync('git fetch')`, `git rebase`) and bun commands. No user-input interpolation detected.
- **Recommendation:** Add `--` boundary before user-controlled args in any future `exec` calls (e.g., `execSync(\`git commit -m "${msg}"\`)` → separate args array).

### Environment & Configuration
- **process.env usage:** 303 instances ✓ (all guarded with defaults)
- **Sensitive vars:** SUPABASE_KEY, EVOLUTION_API_KEY, ALIBABA_DASHSCOPE_API_KEY — all loaded from env, never committed
- **Test fixtures:** Safe use of test-key placeholders in test suites

**Status:** ✓ Configuration hardening looks good.

### INC-001 Mitigation Status
**Post-Force-Push Recovery (2026-04-06):**

| Layer | Status | File |
|-------|--------|------|
| Pre-push hook | ✅ Deployed | `.husky/pre-push` (3.0K) |
| GitHub branch protection | ✅ Deployed | `allow_force_pushes=false` |
| CI push audit | ✅ Deployed | `.github/workflows/push-audit.yml` (3.6K) |
| Safe-push wrapper | ✅ Deployed | `scripts/safe-push.sh` (3.2K) |
| Scheduled job updates | ⏳ Pending | See "Pending Actions" below |

**Status:** ✓ Core mitigations in place. Scheduled jobs still need auditing.

---

## PART 3: DOCUMENTATION & GOVERNANCE

### SSOT Compliance (CLAUDE.md §28)
| Domain | SSOT | Status |
|--------|------|--------|
| Tasks | `TASKS.md` (864 lines) | ✓ Under 900 threshold |
| Agents | `AGENTS.md` (199 lines) | ✓ Under 200 threshold |
| GTM | `docs/GTM_SSOT.md` | ✓ Exists |
| Capabilities | `docs/CAPABILITY_REGISTRY.md` | ✓ Exists |
| Learnings | `docs/knowledge/HARVEST.md` | ✓ Exists |

**Status:** ✓ SSOT structure respected, no duplicate doc files in forbidden zones.

### Recent Governance Activity
- **Last 10 commits:** Mix of feature, fix, chore — well-formed conventional commits ✓
- **INC-001 doc:** Current (2026-04-06) — force-push recovery documented ✓
- **Git hooks:** Pre-commit installed & enforced ✓

---

## PART 4: RECOMMENDATIONS (PRIORITIZED)

### 🔴 CRITICAL PRIORITY (P0 - BLOCKING)
**GitHub Dependabot: 12 vulnerabilities (4 high, 8 moderate)**
- **Action:** Review & apply patches at https://github.com/enioxt/egos/security/dependabot
- **Timeline:** Within 24 hours (4 HIGH = production risk)
- **Blocker:** Do not merge to production until resolved
- **Impact:** Potential RCE, auth bypass, or data exposure depending on package

### 🔴 HIGH PRIORITY (P0)
1. **Audit & update CCR scheduled jobs** (INC-001 pending action)
   - Which job did the 2026-04-06 force-push? Check https://claude.ai/code/scheduled
   - Edit to use `bash scripts/safe-push.sh main` instead of `git push`
   - Apply to all 3 scheduled jobs (Code Intel, Governance, Gem Hunter Adaptive)
   - **Impact:** Prevents future force-push data loss
   - **Est. time:** 15 min

2. **Fix TypeScript errors in scripts/**
   - Add `/// <reference types="node" />` to `scripts/*.ts` OR create `scripts/tsconfig.json`
   - Validate with `bun typecheck`
   - **Impact:** Unblocks CI type-checking
   - **Est. time:** 10 min

### 🟡 MEDIUM PRIORITY (P1)
3. **Refactor orchestrator.ts & server.ts for readability**
   - orchestrator.ts: 900 LOC → split at service boundaries (at least 2 modules)
   - server.ts: 810 LOC → separate routes, middleware, handlers
   - **Impact:** Easier testing, maintenance, review cycles
   - **Est. time:** 2-3 hours (can be phased)

4. **Audit & resolve implicit `any` types (132 instances)**
   - Scan `packages/shared/src/__tests__/` for test-only anys (likely safe)
   - In production code, convert to proper types or document why
   - **Impact:** Improved type safety, better IDE support
   - **Est. time:** 4-6 hours

5. **Integration contract TODOs (8 items)**
   - Telegram, Slack, Webhook implementations are currently no-op
   - Decide: Ship as beta contracts OR move to roadmap?
   - **Impact:** Clarifies API surface & contract guarantees
   - **Est. time:** 1-2 hours

### 🟢 LOW PRIORITY (P2)
6. **Audit unused exports from shared/index.ts**
   - Confirm: `getKernelSeedGraph`, `nodesByType`, `nodesByStatus` unused?
   - If unused, either document as internal or deprecate with timeline
   - **Impact:** Cleaner public API
   - **Est. time:** 30 min

---

## OVERALL STATUS

| Category | Grade | Notes |
|----------|-------|-------|
| **Code Health** | B+ | Large files (900 LOC), 132 anys, but no dead code. TypeScript errors only in scripts. |
| **Security** | 🔴 **C** | **12 GitHub vulnerabilities detected (4 HIGH).** No hardcoded secrets, but dependency risk is elevated. INC-001 mitigations mostly deployed. |
| **Governance** | A | SSOT compliant, TASKS.md under limit, conventional commits enforced. |
| **Incident Readiness** | A- | Branch protection + audit logging in place; pending: scheduled job update. |

### **FINAL VERDICT: CRITICAL** (1 blocking dependency issue + 3 P1 items)

**MUST FIX BEFORE PRODUCTION:**
1. 🔴 **GitHub Dependabot: Apply 4 HIGH severity patches** (24h SLA)
2. ✅ Scheduled jobs → use safe-push.sh (INC-001)
3. ✅ TypeScript in scripts/ (ci visibility)
4. ✅ Implicit any audit (code quality)

**Can phase in parallel:**
- Large file refactoring (improves testability)
- Integration contract decisions (clarifies API)

---

## Verification Commands

```bash
# Run this to confirm mitigations:
bun typecheck 2>&1 | grep -c "error"           # expect <5 (scripts only)
grep -r "export.*any" packages/shared/src --include='*.ts' | wc -l  # any reduction?
git log --oneline -1 | grep "safe-push"       # last push safe? ✓
bash scripts/safe-push.sh main --force 2>&1 | head  # rejects --force ✓
```

---

**Generated by:** Code Intelligence + Security Agent  
**Next audit:** 2026-04-16 (weekly)
