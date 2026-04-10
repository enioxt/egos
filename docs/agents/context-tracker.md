# Context Tracker
> **ID:** `context-tracker` | **Status:** active | **Area:** observability | **Risk:** T0  
> **Entrypoint:** `agents/agents/context-tracker.ts`  
> **Task:** ENC-L1-003 | **Created:** -

## Purpose
Estimates remaining usable context window (CTX 0-280) from uncommitted files, session commits, handoff size, and agent runs. Emits zone emoji + /end recommendation when CTX > 180.

## Proof of Life
```bash
bun agents/agents/context-tracker.ts
```

## Triggers
manual, pre_end

## Side Effects
none

## Cost
none

## Notes
*Add observations here after first dry-run.*

---
*SSOT: agents/registry/agents.json — do not duplicate metadata here*
