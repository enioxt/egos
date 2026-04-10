# Dead Code Detector
> **ID:** `dead-code-detector` | **Status:** active | **Area:** qa | **Risk:** T0  
> **Entrypoint:** `agents/agents/dead-code-detector.ts`  
> **Task:** ENC-L1-003 | **Created:** -

## Purpose
Finds dead exports, orphan files, and empty stubs across any TypeScript codebase using regex-based analysis (no external deps)

## Proof of Life
```bash
bun agents/agents/dead-code-detector.ts --dry-run --target .
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
