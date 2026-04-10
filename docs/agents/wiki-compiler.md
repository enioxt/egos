# Wiki Compiler
> **ID:** `wiki-compiler` | **Status:** active | **Area:** knowledge | **Risk:** T0  
> **Entrypoint:** `agents/agents/wiki-compiler.ts`  
> **Task:** ENC-L1-003 | **Created:** -

## Purpose
Compiles raw sources (handoffs, job reports, gem-hunter, strategy docs) into structured wiki pages in Supabase. Karpathy LLM Wiki pattern: ingest → compile → lint. Also records learnings for data flywheel.

## Proof of Life
```bash
bun agents/agents/wiki-compiler.ts --compile --dry
```

## Triggers
manual, cron

## Side Effects
supabase_sync

## Cost
none

## Notes
*Add observations here after first dry-run.*

---
*SSOT: agents/registry/agents.json — do not duplicate metadata here*
