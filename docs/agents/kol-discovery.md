# KOL Discovery
> **ID:** `kol-discovery` | **Status:** active | **Area:** intelligence | **Risk:** T0  
> **Entrypoint:** `scripts/kol-discovery.ts`  
> **Task:** ENC-L1-003 | **Created:** -

## Purpose
Fetches @anoineim X following list, classifies accounts by bio (crypto/ai-ml/dev-tooling/governance/markets), scores signal quality (HIGH/MED/LOW), outputs kol-list.json

## Proof of Life
```bash
bun scripts/kol-discovery.ts --dry
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
