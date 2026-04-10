# Spec Pipeline Router
> **ID:** `spec-router` | **Status:** active | **Area:** governance | **Risk:** T0  
> **Entrypoint:** `agents/agents/spec-router.ts`  
> **Task:** ENC-L1-003 | **Created:** -

## Purpose
Validates spec pipeline stage fields, detects current stage, routes to next reviewer, tracks SLA violations, and generates merge-block reasons

## Proof of Life
```bash
bun agents/agents/spec-router.ts --mode validate --spec docs/examples/spec-pipeline-example.md
```

## Triggers
manual, on_label

## Side Effects
none

## Cost
none

## Notes
*Add observations here after first dry-run.*

---
*SSOT: agents/registry/agents.json — do not duplicate metadata here*
