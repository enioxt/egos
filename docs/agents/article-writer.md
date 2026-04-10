# Article Writer
> **ID:** `article-writer` | **Status:** active | **Area:** publishing | **Risk:** T1  
> **Entrypoint:** `agents/agents/article-writer.ts`  
> **Task:** ENC-L1-003 | **Created:** 2026-04-08

## Purpose
Timeline AI Publishing Pipeline: reads git commits, calls qwen-plus to generate article draft, runs Guard Brasil PII check, inserts to timeline_drafts Supabase table. Part of PUBLISH: trigger in auto-disseminate.

## Proof of Life
```bash
bun agents/agents/article-writer.ts --dry
```

## Triggers
commit_hook, manual

## Side Effects
supabase_write, llm_call

## Cost
llm

## Notes
*Add observations here after first dry-run.*

---
*SSOT: agents/registry/agents.json — do not duplicate metadata here*
