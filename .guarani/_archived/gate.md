# /gate — Manual Quality Gate Scoring

> **Skill:** `~/.claude/commands/gate.md`  
> **Purpose:** Apply G1-G5 quality gates from `.guarani/orchestration/GATES.md` manually  
> **Usage:** Type `/gate` in Claude Code chat

---

## 🎯 When to Use

Use `/gate` when:
- [ ] Before submitting a PR (self-check)
- [ ] After completing a complex task (validation)
- [ ] When uncertain about code quality (assessment)
- [ ] Before running automated tests (pre-check)

---

## 📋 G1-G5 Quality Gates

### G1 — Syntax/Build Gate
**Question:** Does it compile/build without errors?

**Checklist:**
- [ ] `bun typecheck` passes (TypeScript)
- [ ] `bun lint` passes (ESLint)
- [ ] No console errors on startup
- [ ] Build completes successfully

**Pass Criteria:** All checks marked ✅
**Fail Action:** Fix errors before proceeding

---

### G2 — Logic/Correctness Gate
**Question:** Does it do what it claims to do?

**Checklist:**
- [ ] Core functionality tested manually
- [ ] Edge cases considered (null, empty, extreme values)
- [ ] Error handling paths verified
- [ ] No obvious logical flaws

**Pass Criteria:** Manual test successful + no red flags
**Fail Action:** Write test cases, fix issues

---

### G3 — SSOT/Drift Gate
**Question:** Does it respect Single Source of Truth?

**Checklist:**
- [ ] No hardcoded values that should be in config
- [ ] No duplicated logic from existing modules
- [ ] Documentation updated if interfaces changed
- [ ] No drift from `.guarani/` governance

**Pass Criteria:** `bun run governance:check` passes
**Fail Action:** Refactor to use shared utilities, update docs

---

### G4 — Integration/Side Effects Gate
**Question:** Does it break anything else?

**Checklist:**
- [ ] Related modules still work (tested)
- [ ] No breaking changes to public APIs
- [ ] Database migrations reversible
- [ ] Environment variables documented

**Pass Criteria:** Smoke tests pass in related areas
**Fail Action:** Fix regressions, add integration tests

---

### G5 — Review/Documentation Gate
**Question:** Can someone else understand and maintain this?

**Checklist:**
- [ ] Code comments explain "why" not "what"
- [ ] Complex logic has inline documentation
- [ ] README/API docs updated if needed
- [ ] Commit message explains intent

**Pass Criteria:** Peer could review without questions
**Fail Action:** Add comments, update docs

---

## 🏆 Scoring

**Perfect Score:** G1 ✅ G2 ✅ G3 ✅ G4 ✅ G5 ✅  
**Minimum for PR:** G1 ✅ G2 ✅ G3 ✅  
**Minimum for Deploy:** G1 ✅ G2 ✅ G3 ✅ G4 ✅

---

## 🚀 Quick Start

When you type `/gate`, Claude will:

1. **Identify current task** from context
2. **Run automated checks** (typecheck, lint, governance)
3. **Present G1-G5 checklist** for manual verification
4. **Calculate score** and suggest next actions
5. **Log result** to `egos_agent_events` for tracking

---

## 📝 Example Session

```
User: /gate

Claude: 🔍 Running quality gate assessment...

G1 (Syntax)     ✅ TypeScript passes
                ✅ Lint passes
                
G2 (Logic)      ⏳ Manual verification needed
                → Test: API returns expected PII patterns
                
G3 (SSOT)       ✅ No governance drift
                ⚠️  Warning: Consider moving hardcoded 4ms to config
                
G4 (Integration) ⏳ Pending manual test
                → Verify: Guard Brasil API still responds
                
G5 (Docs)       ⏳ Check needed
                → Update: API endpoint documentation

Score: 2/5 automated, 3/5 pending manual
Recommendation: Complete G2, G4, G5 before PR
```

---

## 🎯 Integration with EGOS

**Automatic triggers:**
- Pre-commit hook: Runs G1-G3 automatically
- PR creation: Requires G1-G4 pass
- Deploy: Requires G1-G5 pass

**Manual override:**
- Use `--force` to bypass (requires justification)
- Logs to `egos_agent_events` for audit

---

## 📊 Metrics

Track over time:
- Average gate score per agent
- Most common failure (G1? G3?)
- Time from code to G5 pass
- Manual vs automated detection ratio

---

**Source:** `.guarani/orchestration/GATES.md`  
**Created:** 2026-04-06  
**Version:** 1.0.0

