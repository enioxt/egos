---
description: "Validate Mycelium reality, references, and maturity across the EGOS kernel."
---

# /mycelium — Kernel Reality Check

## 1. Load Canonical Sources

Read in order:

- `docs/concepts/mycelium/MYCELIUM_OVERVIEW.md`
- `docs/concepts/mycelium/REFERENCE_GRAPH_DESIGN.md`
- `docs/concepts/mycelium/NETWORK_PLAN.md`
- `docs/SYSTEM_MAP.md`
- latest file in `docs/_current_handoffs/`

## 2. Classify Layers

For each layer, mark `Present`, `Partial`, `Planned`, or `Missing`:

- Runtime/event bus
- Snapshot/dashboard
- Reference graph
- Cross-repo sync surfaces

## 3. Reality Rules

- Never claim a live mesh without code, command output, log, or endpoint evidence
- If a doc points to a missing file, either patch the doc or create a task
- Separate kernel truth from `egos-lab` truth

## 4. Deliverables

Produce:

- a compact maturity table
- drift notes for broken references
- next actions for kernel vs lab

## 5. Dissemination

If Mycelium truth changed:

- update `docs/concepts/mycelium/MYCELIUM_OVERVIEW.md`
- update `docs/knowledge/HARVEST.md`
- update `TASKS.md`
