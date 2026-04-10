# Doc-Drift Verifier
> **ID:** `doc-drift-verifier` | **Status:** active | **Area:** governance | **Risk:** T0  
> **Entrypoint:** `agents/agents/doc-drift-verifier.ts`  
> **Task:** ENC-L1-003 | **Created:** 2026-04-07

## Purpose
Layer 2 of EGOS Doc-Drift Shield. Verifies .egos-manifest.yaml claims against live state. Called by .husky/doc-drift-check.sh in pre-commit gate.

## Proof of Life
```bash
bun agents/agents/doc-drift-verifier.ts --dry
```

## Triggers
pre_commit

## Side Effects
stdout

## Cost
none

## Notes
*Add observations here after first dry-run.*

---
*SSOT: agents/registry/agents.json — do not duplicate metadata here*
