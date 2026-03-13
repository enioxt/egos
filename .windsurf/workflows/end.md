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
```

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

## Phase 4: Disseminate Knowledge

Before ending, the agent MUST persist knowledge:

| Condition | Required action |
|------|----------------|
| Any session | `create_memory()` with patterns, decisions, gotchas |
| Meta-prompt trigger suspected | Check `.guarani/prompts/triggers.json` |
| Architecture changed | Document in `.guarani/` or repo docs |
| New reusable pattern | Append to `docs/knowledge/HARVEST.md` |
| Capability created / improved / adopted | Update `docs/CAPABILITY_REGISTRY.md` |
| Chatbot surface changed | Re-check `docs/modules/CHATBOT_SSOT.md` adoption table + rollout protocol |
| Agents / dashboards / mesh claims changed | Apply `.windsurf/workflows/mycelium.md` logic and add maturity snapshot to handoff |
| Codex used | Record availability, mode, and accept/reject outcome in handoff |
| Research / discovery session | Run `bun agent:run gem-hunter --exec --quick` |
| Research data generated | Run `bun agent:run report-generator --exec --topic="<session topic>" --data=<latest gem-hunter report>` |

## Phase 5: Codex Cleanup

```bash
if command -v codex &> /dev/null; then
  codex --version 2>/dev/null && codex cloud list 2>/dev/null | head -5 || true
  [ "$(git -C "$ROOT" status --short 2>/dev/null | wc -l)" -gt 0 ] && codex review --uncommitted 2>/dev/null || true
else
  printf "Codex not installed\n"
fi
```

## Phase 6: Commit If Needed // turbo

```bash
UNCOMMITTED=$(git -C "$ROOT" status --short 2>/dev/null | wc -l)
if [ "$UNCOMMITTED" -gt 0 ]; then
  printf "⚠️  %s uncommitted files — commit now or state explicitly in handoff why not.\n" "$UNCOMMITTED"
  git -C "$ROOT" status --short
fi
```

## Phase 7: Session Summary

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

_v5.4 — Added capability-registry and chatbot-SSOT dissemination requirements to finalization flow._
