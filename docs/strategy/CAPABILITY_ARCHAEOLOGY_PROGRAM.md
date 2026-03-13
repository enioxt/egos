# Capability Archaeology Program

> **Version:** 1.0.0 | **Created:** 2026-03-13
> **Purpose:** make reusable EGOS knowledge discoverable, classified, observable, and archivable.

## Verified Foundations

- `Gem Hunter` exists and is useful, but today is mainly **external discovery**.
- `Mycelium Reference Graph` already provides the right base: **entities + relations + evidence + status**.
- `Cronos` and `Nexus` are **capabilities**, not umbrella doctrines.
- `egos-archive/` already exists, but lacks a strict lifecycle and tombstone policy.

## Canonical Truth Chain

1. `~/.egos/SYSTEM_MAP.md`
2. `egos-lab/docs/EGOS_WORKSPACE_MAP.md`
3. `egos-lab/docs/EGOS_ECOSYSTEM_MAP.md`
4. `egos-lab/docs/research/MYCELIUM_REFERENCE_GRAPH_DESIGN_2026-03-07.md`
5. repo-local `AGENTS.md` + `TASKS.md` + `.windsurfrules`

## Lifecycle States

- `ssot`
- `active_derivative`
- `candidate`
- `needs_investigation`
- `obsolete_confirmed`
- `archived`

## Evidence Model

- `runtime`
- `log`
- `code`
- `issue`
- `plan`
- `doc`

Priority: `runtime > log > code > issue > plan > doc`

## Confidence Rules

- **>= 0.90** + at least **2 evidence classes** → may become `obsolete_confirmed`
- **0.60 - 0.89** → `needs_investigation`
- **< 0.60** → no lifecycle change

## Archive Policy

Nothing moves to `/home/enio/egos-archive` without:

- replacement or superseding target identified
- confidence >= 0.90
- rationale recorded
- tombstone left in live registry/docs

## System Architecture

- **Discovery:** `Gem Hunter` gains internal mode, or sibling `capability-archaeologist`
- **Reference:** extend Mycelium graph with `capability`, `module`, `component`, `integration`, `workflow`
- **Registry:** human SSOT + machine-readable registry projection
- **Observability:** every scan emits structured telemetry and archive decisions

## Mandatory Namespacing

- `intelink:cronos_timeline`
- `intelink:nexus_cross_case`
- `market:nexus_market`
- `mycelium:runtime_bus`
- `mycelium:reference_graph`

## Immediate Execution Order

1. Strengthen internal archaeology/search
2. Add lifecycle states to capability registry
3. Create archive ledger + tombstones
4. Port reusable chatbot primitives to `packages/shared/`
5. Create compliance-checker agent
6. Replicate SSOT modules to leaf repos
