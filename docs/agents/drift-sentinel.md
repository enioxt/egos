# Drift Sentinel
> **ID:** `drift-sentinel` | **Status:** active | **Area:** governance | **Risk:** T1  
> **Entrypoint:** `agents/agents/drift-sentinel.ts`  
> **Task:** ENC-L1-003 | **Created:** -

## Purpose
Configuration drift detection — compares narrative (docs) vs live system state, monitors TASKS.md priorities vs git activity, agents.json vs agents/ directory

## Proof of Life
```bash
bun agents/agents/drift-sentinel.ts --dry-run
```

## Triggers
every_6h, manual

## Side Effects
fs_write

## Cost
none

## Notes
*Add observations here after first dry-run.*

---
*SSOT: agents/registry/agents.json — do not duplicate metadata here*
