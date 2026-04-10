# Doc-Drift Sentinel
> **ID:** `doc-drift-sentinel` | **Status:** active | **Area:** governance | **Risk:** T1  
> **Entrypoint:** `agents/agents/doc-drift-sentinel.ts`  
> **Task:** ENC-L1-003 | **Created:** 2026-04-07

## Purpose
Layer 3 of the EGOS Doc-Drift Shield. Daily scanner that verifies all .egos-manifest.yaml claims against live state, auto-patches last_value on manifests, opens GitHub issues, sends Telegram alerts on drift.

## Proof of Life
```bash
bun agents/agents/doc-drift-sentinel.ts --dry
```

## Triggers
manual

## Side Effects
git_branch, github_issue, telegram_alert

## Cost
none

## Notes
*Add observations here after first dry-run.*

---
*SSOT: agents/registry/agents.json — do not duplicate metadata here*
