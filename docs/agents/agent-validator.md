# Agent Registry Validator
> **ID:** `agent-validator` | **Status:** active | **Area:** governance | **Risk:** T0  
> **Entrypoint:** `agents/agents/agent-validator.ts`  
> **Task:** ENC-L1-003 | **Created:** -

## Purpose
Lightweight validation agent — updates agents/registry/validation.json cache. 4-point check: entrypoint read, file exists, status verified, context validated. Ground truth hierarchy: agents.json (definitions) > validation.json (verification) > drift-sentinel (detector).

## Proof of Life
```bash
bun agents/agents/agent-validator.ts --exec
```

## Triggers
manual, on_agents_json_change

## Side Effects
fs_write

## Cost
none

## Notes
*Add observations here after first dry-run.*

---
*SSOT: agents/registry/agents.json — do not duplicate metadata here*
