# Gem Hunter Session Close: EGOS ↔ Aider

**Date:** 2026-04-01
**Score:** 73.7/100
**Classification:** STUDY — above transplant threshold

---

## Final Verdict

Aider is the most mature CLI pair-programming tool in the open-source ecosystem. Its edit loop (extract → dry-run → apply → commit), repomap architecture, and benchmark infrastructure are all production-proven at 42K+ stars. EGOS has a fundamentally different scope (multi-agent platform vs single pair-programming session) but can adopt 3 concrete patterns with low risk.

---

## Top Patterns to Transplant

### 1. Dry-run + dirty-commit edit safety (P0 — adopt immediately)

**What:** Before any Write/Edit, check that:
1. All unstaged changes are committed first (`dirty_commit` pattern)
2. The proposed edit is validated for conflicts before applying (`dry_run` pattern)

**How in EGOS:** Enhance the `post-write-typecheck` PostToolUse hook to also:
- Warn if there are uncommitted changes before Claude Code edits
- Add a pre-edit validation pass (check that old_string exists before Edit is called)

**Files to create:**
- `.claude/hooks/pre-edit-safety` — PreToolUse hook for Edit: warns if dirty working tree

---

### 2. Weak/editor model separation for CCR cost reduction (P1)

**What:** Use a weaker/cheaper model for mechanical tasks (lint, format, grep summaries) and the main model for planning. In Aider: `--weak-model haiku` + `--editor-model sonnet`.

**How in EGOS:** CCR jobs already use Haiku by default. For local sessions:
- Create `/fast-mode` skill that sets `model: haiku` for pure automation tasks
- Document in CLAUDE.md when to use Haiku vs Sonnet vs Opus

---

### 3. SWE-Bench-inspired edit benchmark (P1)

**What:** Aider measures its own edit accuracy on real GitHub issues (SWE-Bench). EGOS has no equivalent.

**How in EGOS:** Create `packages/guard-brasil/src/benchmark.ts` (already done for PII — this pattern now) as the model. Extend to an "edit benchmark" for Claude Code skill quality:
- Collect 20 real edit tasks from EGOS history (file path, old content, expected new content)
- Run through each /edit skill, measure success rate
- Track over time in docs/jobs/

---

## Blind Spots Revealed

1. **No edit validation layer** — Claude Code writes files without dry-run; a single bad old_string can corrupt a file silently
2. **No local benchmark** — EGOS has no way to measure whether Claude Code skills are getting better or worse over time
3. **Single-model assumption** — EGOS architecture assumes one model per session; Aider's multi-model coordination (cheap/fast vs capable/slow) is more cost-efficient

---

## Recommended Next Repos (queue order)

1. **Cline** (`cline/cline`) — IDE agent autonomy, human-in-the-loop UX — directly comparable to Claude Code extension patterns
2. **OpenHands** (`OpenHands/OpenHands`) — full software agent SDK, durable execution, SWE-Bench leader
3. **LangGraph** (`langchain-ai/langgraph`) — stateful long-running agents — for future EGOS durable workflow needs

---

## EGOS Patches Generated

- `GH-031`: Create `.claude/hooks/pre-edit-safety` — warn on dirty working tree before Edit
- `GH-032`: SWE-Bench-inspired EGOS edit benchmark — 20 real edit tasks tracked over time
- `GH-033`: EGOS edit loop hardening — add dry-run conceptually in Edit skill wrapper

---

*Session closed 2026-04-01. Study validated — score 73.7/100 above transplant threshold.*
