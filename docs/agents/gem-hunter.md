# Gem Hunter v6.0
> **ID:** `gem-hunter` | **Status:** active | **Area:** intelligence | **Risk:** T1  
> **Entrypoint:** `agents/agents/gem-hunter.ts`  
> **Task:** ENC-L1-003 | **Created:** -

## Purpose
Multi-track discovery engine: GitHub, arXiv, HuggingFace, PWC, Exa, X, Reddit, HN, NPM. 6-stage paper pipeline (discovery→triage→deep-read→scaffold→score→evolution). Telegram alerts for gems ≥80.

## Proof of Life
```bash
bun agents/agents/gem-hunter.ts --dry
```

## Triggers
manual, cron

## Side Effects
fs_write, telegram_alert, supabase_sync

## Cost
openrouter+gemini

## Notes
*Add observations here after first dry-run.*

---
*SSOT: agents/registry/agents.json — do not duplicate metadata here*
