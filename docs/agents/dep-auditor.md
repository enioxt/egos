# Dependency Auditor
> **ID:** `dep-auditor` | **Status:** active | **Area:** architecture | **Risk:** T0  
> **Entrypoint:** `agents/agents/dep-auditor.ts`  
> **Task:** ENC-L1-003 | **Created:** -

## Purpose
Scans package.json files for version conflicts, misplaced dev deps, and unused dependencies

## Proof of Life
```bash
bun agents/agents/dep-auditor.ts --dry-run --target .
```

## Triggers
manual

## Side Effects
none

## Cost
none

## Notes
*Add observations here after first dry-run.*

---
*SSOT: agents/registry/agents.json — do not duplicate metadata here*
