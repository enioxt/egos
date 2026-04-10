# SSOT Auditor
> **ID:** `ssot-auditor` | **Status:** active | **Area:** architecture | **Risk:** T0  
> **Entrypoint:** `agents/agents/ssot-auditor.ts`  
> **Task:** ENC-L1-003 | **Created:** -

## Purpose
Structural Triage Engine — scans TypeScript/Python codebases via AST, detects type drift (duplicate definitions with different shapes), produces prioritized reports with codemod plans

## Proof of Life
```bash
bun agents/agents/ssot-auditor.ts --dry-run --target .
```

## Triggers
manual, weekly

## Side Effects
fs_write

## Cost
none

## Notes
*Add observations here after first dry-run.*

---
*SSOT: agents/registry/agents.json — do not duplicate metadata here*
