# SSOT Fixer
> **ID:** `ssot-fixer` | **Status:** active | **Area:** architecture | **Risk:** T1  
> **Entrypoint:** `agents/agents/ssot-fixer.ts`  
> **Task:** ENC-L1-003 | **Created:** -

## Purpose
Consumes ssot-auditor output and applies safe, low-risk codemod plans automatically (EXACT or RELAXED drift only)

## Proof of Life
```bash
bun agents/agents/ssot-fixer.ts --dry-run
```

## Triggers
manual

## Side Effects
fs_write

## Cost
none

## Notes
*Add observations here after first dry-run.*

---
*SSOT: agents/registry/agents.json — do not duplicate metadata here*
