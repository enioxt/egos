# README Syncer
> **ID:** `readme-syncer` | **Status:** active | **Area:** governance | **Risk:** T1  
> **Entrypoint:** `agents/agents/readme-syncer.ts`  
> **Task:** ENC-L1-003 | **Created:** 2026-04-07

## Purpose
Syncs README claims against .egos-manifest.yaml. Part of Doc-Drift Shield — keeps README numbers in sync with manifest-verified values.

## Proof of Life
```bash
bun agents/agents/readme-syncer.ts --dry
```

## Triggers
manual, pre_commit

## Side Effects
fs_write

## Cost
none

## Notes
*Add observations here after first dry-run.*

---
*SSOT: agents/registry/agents.json — do not duplicate metadata here*
