---
description: "Finaliza sessão com handoff completo, disseminação e meta-prompt check"
---

# /end — Session Finalization (v5.3)

> **Sacred Code:** 000.111.369.963.1618
> **Works in:** ANY EGOS repo
> **Auto-trigger:** Context Tracker reaches ⛔ CRITICAL (CTX 280+) → agent executes /end autonomously

## Phase 1: Collect Session Data // turbo

```bash
ROOT="$PWD"; CUR="$ROOT"
while [ "$CUR" != "/" ] && [ ! -e "$CUR/.git" ]; do CUR="$(dirname "$CUR")"; done
[ -e "$CUR/.git" ] && ROOT="$CUR"
export ROOT

printf "📂 Repo: %s | Last: %s | Uncommitted: %s | Session commits: %s\n" \
  "$(basename "$ROOT")" \
  "$(git -C "$ROOT" log --oneline -1 2>/dev/null)" \
  "$(git -C "$ROOT" status --short 2>/dev/null | wc -l)" \
  "$(git -C "$ROOT" log --oneline --since='6 hours ago' 2>/dev/null | wc -l)"
git -C "$ROOT" log --oneline --since="6 hours ago" 2>/dev/null || git -C "$ROOT" log --oneline -5
[ -f "$ROOT/TASKS.md" ] && printf "📝 TASKS.md: %s lines\n" "$(wc -l < "$ROOT/TASKS.md")"
[ -f "$ROOT/egos.config.json" ] && printf "🏷️  Role: %s\n" "$(cat "$ROOT/egos.config.json" | grep -o '"role": "[^"]*"')" || printf "🏷️  Role: (no egos.config.json — heuristic detection)\n"
```

**Repo-role detection:** If `egos.config.json` exists, read `role` and `surfaces` to gate conditional steps below. If absent, assume `leaf` role and skip surfaces like gem-hunter, report-generator, and session:guard.

## Phase 2: Agent Handoff Generation

The agent MUST create `docs/_current_handoffs/handoff_YYYY-MM-DD.md`.

Required sections:

- `Accomplished` — bullet list with file links
- `In Progress` — include % completion
- `Blocked` — reason + required action
- `Next Steps` — ordered by priority
- `Environment State` — builds/tests status with evidence
- `Decision Trail` — selected `ask_user_question` branches/options

Acceptance:

- Next agent becomes productive in `< 2 minutes`
- Claims are separated into `Verified`, `Inferred`, `Proposed`

## Phase 3: Update TASKS.md

The agent SHALL ensure `TASKS.md` reflects the current state:

- Mark completed tasks with `[x]`
- Mark in-progress with `[/]`
- Add newly discovered tasks
- Update version + `LAST SESSION` line

## Phase 4: Documentation Freshness Check (BLOCKING)

The agent MUST verify documentation is current before finalizing:

```bash
# Check if code changed but docs not updated
CODE_CHANGED=$(git -C "$ROOT" diff --name-only HEAD~5 2>/dev/null | grep -E '^src/(app/api|lib)/' || true)
SYSTEM_MAP=$(find "$ROOT" -name "SYSTEM_MAP.md" -type f 2>/dev/null | head -1)

if [ -n "$CODE_CHANGED" ] && [ -n "$SYSTEM_MAP" ]; then
  MAP_AGE=$(stat -c %Y "$SYSTEM_MAP" 2>/dev/null || stat -f %m "$SYSTEM_MAP" 2>/dev/null || echo 0)
  NOW=$(date +%s)
  HOURS_OLD=$(( (NOW - MAP_AGE) / 3600 ))
  if [ "$HOURS_OLD" -gt 24 ]; then
    printf "⚠️  SYSTEM_MAP.md is %s hours old. Update required before /end.\n" "$HOURS_OLD"
  fi
fi

# Check AGENTS.md freshness
if [ -f "$ROOT/AGENTS.md" ]; then
  AGENTS_AGE=$(stat -c %Y "$ROOT/AGENTS.md" 2>/dev/null || stat -f %m "$ROOT/AGENTS.md" 2>/dev/null || echo 0)
  NOW=$(date +%s)
  DAYS_OLD=$(( (NOW - AGENTS_AGE) / 86400 ))
  if [ "$DAYS_OLD" -gt 7 ]; then
    printf "⚠️  AGENTS.md is %s days old. Consider updating.\n" "$DAYS_OLD"
  fi
fi
```

**Mandatory doc updates when:**

| Code Change | Required Doc Update |
|-------------|---------------------|
| New API route | `SYSTEM_MAP.md` capability registry |
| New lib module | `SYSTEM_MAP.md` architecture section |
| New capability | `AGENTS.md` capabilities table |
| Schema change | `SYSTEM_MAP.md` + migration docs |
| New integration | `SYSTEM_MAP.md` integrations section |

**The agent SHALL NOT finalize `/end` if:**

1. Code changed in `src/app/api/` or `src/lib/` AND `SYSTEM_MAP.md` not updated in session
2. New capability added AND `AGENTS.md` capabilities table not updated
3. `TASKS.md` not reflecting current state

## Phase 5: Disseminate Knowledge

Before ending, the agent MUST persist knowledge:

| Condition | Required action |
|------|----------------|
| Any session | `create_memory()` with patterns, decisions, gotchas |
| Meta-prompt trigger suspected | Check `.guarani/prompts/triggers.json` |
| Architecture changed | Document in `.guarani/` or repo docs |
| Kernel governance / workflows changed | Run `bun run governance:sync:exec` then `bun run governance:check` |
| New reusable pattern | Append to `docs/knowledge/HARVEST.md` |
| Capability created / improved / adopted | Update `docs/CAPABILITY_REGISTRY.md` + `SYSTEM_MAP.md` |
| Chatbot surface changed | Re-check `docs/modules/CHATBOT_SSOT.md` adoption table + rollout protocol |
| Agents / dashboards / mesh claims changed | Apply `.windsurf/workflows/mycelium.md` logic and add maturity snapshot to handoff |
| Codex used | Record availability, mode, and accept/reject outcome in handoff |
| Research / discovery session in repos that ship Gem Hunter | Run `bun agent:run gem-hunter --exec --quick` |
| Research data generated in repos that ship report generation | Run `bun agent:run report-generator --exec --topic="<session topic>" --data=<latest gem-hunter report>` |

## Phase 6: Codex Cleanup

```bash
if command -v codex &> /dev/null; then
  codex --version 2>/dev/null && codex cloud list 2>/dev/null | head -5 || true
  [ "$(git -C "$ROOT" status --short 2>/dev/null | wc -l)" -gt 0 ] && codex review --uncommitted 2>/dev/null || true
else
  printf "Codex not installed\n"
fi
```

## Phase 7: Commit If Needed // turbo

```bash
UNCOMMITTED=$(git -C "$ROOT" status --short 2>/dev/null | wc -l)
if [ "$UNCOMMITTED" -gt 0 ]; then
  printf "⚠️  %s uncommitted files — commit now or state explicitly in handoff why not.\n" "$UNCOMMITTED"
  git -C "$ROOT" status --short
fi
```

## Phase 8: Session Summary

The agent MUST display this structure in chat:

```text
SESSION SUMMARY
===============
Repo: [name]
Commits: [N] this session
Files changed: [list key files]
What was done: [2-4 lines]
Next steps: [P0/P1 priorities]
Meta-prompts used: [any triggered?]
Context Tracker: [final CTX value/280] [zone emoji]
Signed by: cascade-agent — [ISO8601]
```

---

_v5.5 — Added Phase 4 (Documentation Freshness Check) as BLOCKING requirement. SYSTEM_MAP.md and AGENTS.md must be current before /end can finalize._
