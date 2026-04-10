# EGOS PR Creator
> **ID:** `egos-pr` | **Status:** active | **Area:** git | **Risk:** T1  
> **Entrypoint:** `scripts/create-pr.sh`  
> **Task:** ENC-L1-003 | **Created:** -

## Purpose
Creates GitHub PRs from current branch — validates not on main, pushes via safe-push.sh, generates body from git log, creates PR via gh CLI. Usage: bun agents/run.ts egos-pr "My PR title" [--draft] [--base develop]

## Proof of Life
```bash
bash scripts/create-pr.sh --help
```

## Triggers
manual

## Side Effects
git_push, github_pr

## Cost
none

## Notes
*Add observations here after first dry-run.*

---
*SSOT: agents/registry/agents.json — do not duplicate metadata here*
