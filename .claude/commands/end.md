# /end — Session Finalization (EGOS v5.5)

> Sacred Code: 000.111.369.963.1618

Finalize session. Create handoff, update docs, commit if needed.

## Phase 1: Collect Data
```bash
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo $PWD)
echo "Repo: $(basename $ROOT)"
echo "Last commit: $(git log --oneline -1 2>/dev/null)"
echo "Uncommitted: $(git status --short 2>/dev/null | wc -l) files"
echo "Session commits: $(git log --oneline --since='6 hours ago' 2>/dev/null | wc -l)"
```

## Phase 2: Generate Handoff
Create `docs/_current_handoffs/handoff_YYYY-MM-DD.md` with:
- **Accomplished** — bullet list with file links
- **In Progress** — % completion
- **Blocked** — reason + action needed
- **Next Steps** — ordered by priority
- **Environment State** — builds/tests status

## Phase 3: Update TASKS.md
- Mark completed tasks `[x]`
- Mark in-progress `[/]`
- Add newly discovered tasks

## Phase 4: Documentation Check (BLOCKING)
Cannot finalize if:
- Code changed in `src/` AND `SYSTEM_MAP.md` not updated
- New capability AND `AGENTS.md` not updated
- `TASKS.md` not current

## Phase 5: Disseminate Knowledge
- Save key patterns to memory
- Update HARVEST.md with learnings
- Update CAPABILITY_REGISTRY.md if new capabilities

## Phase 6: Commit If Needed
```bash
git status --short | wc -l
# If > 0: prompt to commit
```

## Phase 7: Session Summary Output
```
SESSION SUMMARY
===============
Repo: [name]
Commits: [N] this session
Security: [Clean]
Files changed: [list]
What was done: [2-4 lines]
Next steps: [P0/P1]
Context Tracker: [value/280]
Signed by: claude-code — [ISO8601]
```
