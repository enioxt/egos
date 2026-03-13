# Mycelium Reference Graph Design — 2026-03-07

> **Inputs:** `apps/egos-web/src/lib/mycelium.ts`, `agents/runtime/event-bus.ts`, `docs/plans/tech/MYCELIUM_NETWORK.md`, `docs/knowledge/MYCELIUM_OVERVIEW.md`, `docs/agentic/HANDOFF_MYCELIUM.md`
> **Goal:** define a canonical reference system in graph/mycelium format without breaking the current event bus model

---

<!-- llmrefs:start -->

## LLM Reference Signature

- **Role:** reference-graph design rationale
- **Summary:** Specifies entity types, relation types, evidence semantics, and the roadmap.
- **Read next:**
  - `docs/knowledge/MYCELIUM_OVERVIEW.md` — **topology** — anchors the design to the current layered Mycelium meaning
  - `packages/shared/src/mycelium/reference-graph.ts` — **implementation** — is the canonical code seed produced from this design
  - `apps/egos-web/api/mycelium-stats.ts` — **implementation** — projects the graph into the public snapshot payload

<!-- llmrefs:end -->

## Why This Is Needed

The current Mycelium stack already has:

- a local event bus
- a worker + queue
- a dashboard snapshot model
- declared surfaces
- conceptual docs for distributed evolution

What it still lacks is a **reference graph** that answers:

- what entities exist in the mesh
- how they relate
- which relations are real vs planned
- which evidence proves each relation

Today, this knowledge is fragmented across:

- code
- route registries
- event logs
- docs
- issues
- dashboards

The missing piece is a canonical graph of references.

---

## Workspace-Wide Scope

This graph must represent **the real EGOS mesh**, not only `egos-lab`.
Today that includes at least these active roots and adjacent nodes:

- `/home/enio/.egos` — shared governance home
- `/home/enio/egos-lab` — canonical orchestration kernel
- `/home/enio/egos-lab/apps/intelink` — specialized intelligence node
- `/home/enio/carteira-livre` — regulated marketplace
- `/home/enio/br-acc` — public-data intelligence graph
- `/home/enio/forja` — industrial ERP in planning
- `/home/enio/policia` — private investigative silo
- `/home/enio/egos-self` — personal CLI/device channel
- `/home/enio/personal` — personal/public identity artifacts

If the reference graph ignores these roots, it becomes a **partial map** and will push agents toward hallucinated architecture.

---

## Design Principle

The reference graph is **not** the event stream.
The reference graph is **the map of the system**.

### Separation of Concerns

- **Event bus** = what happened
- **Reference graph** = what exists and how it connects
- **Docs** = human explanation of the graph
- **Dashboard** = projection of graph + telemetry

This keeps Mycelium from collapsing runtime data and architecture metadata into one layer.

---

## The Artistic Model — Mycelium As Reference Civilization

The mesh should be readable as a living organism:

- **roots** = first references, sources of trust, canonical documents
- **hyphae** = relations, citations, imports, links, event routes, issue chains
- **nodes** = repos, apps, agents, people, artifacts, databases
- **fruiting bodies** = what becomes visible to humans: dashboards, bots, reports, apps
- **spores** = contributions that leave one node and start another: PRs, issues, prompts, handoffs, investigations

This matters because the system is not only technical.
It is social and epistemic:

- nobody in the mesh is "standalone"
- every subsystem is legible through its references
- references can reference other references
- collaboration should be modeled as graph structure, not only prose

A healthy Mycelium map should let us answer:

- what exists
- what depends on what
- what is canonical
- what is derivative
- what is proven
- who contributed a reference
- which references became public surfaces

---

## Canonical Entity Types

### Workspace / Identity Entities

- `workspace_root`
- `repository`
- `human`
- `artifact`
- `reference`
- `citation`

### Core Runtime Entities

- `surface`
- `runtime`
- `agent`
- `worker`
- `endpoint`
- `event_topic`
- `queue`
- `database`
- `trigger`
- `bot`

### Governance / Knowledge Entities

- `document`
- `workflow`
- `issue`
- `task`
- `metric`
- `schema`
- `projection`
- `integration`

### Future / Verification Entities

- `shadow_node`
- `zkp_proof`
- `policy`
- `reference_snapshot`

---

## Canonical Relation Types

### Structural

- `belongs_to`
- `depends_on`
- `contains`
- `exposes`
- `subscribes_to`
- `emits`
- `persists_to`
- `reads_from`
- `writes_to`
- `routes_to`
- `references`
- `cites`
- `contributes_to`

### Governance

- `documents`
- `governs`
- `tracks`
- `plans`
- `validates`
- `derives_from`
- `mirrors`
- `flags`

### Evidence

- `observed_in_code`
- `observed_in_runtime`
- `observed_in_log`
- `observed_in_plan`

---

## Minimal Canonical Schema

```ts
export type ReferenceEntityType =
  | 'workspace_root'
  | 'repository'
  | 'human'
  | 'artifact'
  | 'reference'
  | 'citation'
  | 'surface'
  | 'runtime'
  | 'agent'
  | 'worker'
  | 'endpoint'
  | 'event_topic'
  | 'queue'
  | 'database'
  | 'trigger'
  | 'bot'
  | 'document'
  | 'workflow'
  | 'issue'
  | 'task'
  | 'metric'
  | 'schema'
  | 'projection'
  | 'integration'
  | 'shadow_node'
  | 'zkp_proof'
  | 'policy'
  | 'reference_snapshot';

export type ReferenceEvidence = 'code' | 'runtime' | 'log' | 'plan' | 'issue';

export interface ReferenceNode {
  id: string;
  type: ReferenceEntityType;
  label: string;
  status: 'active' | 'degraded' | 'offline' | 'planned';
  evidence: ReferenceEvidence[];
  sourcePath?: string;
  note?: string;
  tags?: string[];
}

export interface ReferenceEdge {
  from: string;
  relation:
    | 'belongs_to'
    | 'depends_on'
    | 'contains'
    | 'exposes'
    | 'subscribes_to'
    | 'emits'
    | 'persists_to'
    | 'reads_from'
    | 'writes_to'
    | 'routes_to'
    | 'references'
    | 'cites'
    | 'contributes_to'
    | 'documents'
    | 'governs'
    | 'tracks'
    | 'plans'
    | 'validates'
    | 'derives_from'
    | 'mirrors'
    | 'flags'
    | 'observed_in_code'
    | 'observed_in_runtime'
    | 'observed_in_log'
    | 'observed_in_plan';
  to: string;
  evidence: ReferenceEvidence[];
  note?: string;
}
```

---

## Initial Graph Seed for Current EGOS Reality

### Nodes

- `surface:egos-web-dashboard`
- `surface:egos-web-api`
- `runtime:agents-runtime`
- `worker:railway-worker`
- `queue:redis-task-queue`
- `database:supabase`
- `endpoint:api-mycelium-stats`
- `endpoint:api-status`
- `endpoint:worker-health`
- `endpoint:worker-metrics`
- `bot:egos-telegram`
- `document:mycelium-network-plan`
- `document:mycelium-overview`
- `document:mycelium-handoff`
- `event_topic:egos.audit.completed`
- `event_topic:egos.network.heartbeat`
- `event_topic:egos.knowledge.harvested`
- `projection:mycelium-snapshot`
- `schema:mycelium-event`

### Edges

- `surface:egos-web-dashboard` `reads_from` `endpoint:api-mycelium-stats`
- `endpoint:api-mycelium-stats` `derives_from` `projection:mycelium-snapshot`
- `projection:mycelium-snapshot` `tracks` `surface:egos-web-api`
- `projection:mycelium-snapshot` `tracks` `runtime:agents-runtime`
- `projection:mycelium-snapshot` `tracks` `worker:railway-worker`
- `runtime:agents-runtime` `emits` `event_topic:egos.audit.completed`
- `runtime:agents-runtime` `emits` `event_topic:egos.knowledge.harvested`
- `worker:railway-worker` `exposes` `endpoint:worker-health`
- `worker:railway-worker` `exposes` `endpoint:worker-metrics`
- `worker:railway-worker` `reads_from` `queue:redis-task-queue`
- `worker:railway-worker` `writes_to` `database:supabase`
- `bot:egos-telegram` `routes_to` `surface:egos-web-api`
- `document:mycelium-network-plan` `documents` `runtime:agents-runtime`
- `document:mycelium-overview` `documents` `projection:mycelium-snapshot`
- `document:mycelium-handoff` `plans` `worker:railway-worker`

---

## Global Workspace Seed

### Nodes

- `workspace_root:shared-governance-home`
- `repository:egos-lab`
- `repository:carteira-livre`
- `repository:br-acc`
- `repository:forja`
- `repository:policia`
- `repository:egos-self`
- `surface:intelink`
- `artifact:personal-identity-surface`
- `reference:workspace-map`
- `reference:ecosystem-map`
- `reference:mycelium-reference-graph`

### Edges

- `workspace_root:shared-governance-home` `governs` `repository:egos-lab`
- `workspace_root:shared-governance-home` `governs` `repository:carteira-livre`
- `workspace_root:shared-governance-home` `governs` `repository:br-acc`
- `workspace_root:shared-governance-home` `governs` `repository:forja`
- `workspace_root:shared-governance-home` `governs` `repository:egos-self`
- `repository:egos-lab` `contains` `surface:intelink`
- `reference:workspace-map` `documents` `repository:egos-lab`
- `reference:workspace-map` `references` `repository:carteira-livre`
- `reference:workspace-map` `references` `repository:br-acc`
- `reference:workspace-map` `references` `repository:forja`
- `reference:workspace-map` `references` `repository:policia`
- `reference:workspace-map` `references` `repository:egos-self`
- `reference:workspace-map` `references` `artifact:personal-identity-surface`
- `reference:ecosystem-map` `cites` `reference:workspace-map`
- `reference:mycelium-reference-graph` `cites` `reference:workspace-map`

This is the first step toward a graph where **references themselves become first-class nodes**.

---

## Status Semantics

The reference graph must preserve the honest distinctions already used by Mycelium:

- `active` = observed in code and confirmed in runtime or recent logs
- `degraded` = exists but evidence is partial or connectivity is incomplete
- `offline` = expected runtime surface not currently reachable
- `planned` = exists only in docs/issues/roadmap

This matches the current philosophy in `mycelium.ts` and avoids fictional “live mesh” claims.

---

## Evidence Rules

Every node and edge should carry evidence.

### Evidence Priority

1. `runtime`
2. `log`
3. `code`
4. `issue`
5. `plan`

### Truth Rule

A relation is only considered **operational** if at least one of these is true:

- observed in runtime
- observed in logs
- observed in code plus validated by a checker

Otherwise it is architectural intention, not live fact.

---

## File-Level SSOT Proposal

### Recommended Canonical Location

Future canonical graph definition should live in:

- `packages/shared/src/mycelium/reference-graph.ts`

Supporting layers:

- `scripts/mycelium-reference-snapshot.ts` -> generate current graph snapshot
- `apps/egos-web/api/mycelium-reference.ts` -> expose graph as JSON
- `apps/egos-web/src/components/MyceliumDashboard.tsx` -> render graph projection
- `docs/research/MYCELIUM_REFERENCE_GRAPH_DESIGN_2026-03-07.md` -> human rationale

### Why `packages/shared`

Because the graph is cross-surface and should not belong only to:

- web
- worker
- bot
- docs

It is ecosystem metadata.

---

## Incremental Roadmap

### Phase 1 — Canonical Schema

- define `ReferenceNode` and `ReferenceEdge`
- seed the first graph from current declared surfaces
- keep it static and explicit

### Phase 2 — Snapshot Generator

- generate derived graph from:
  - `mycelium.ts`
  - API registry
  - worker endpoints
  - event topic declarations
  - PM2/bot config

### Phase 3 — Dashboard Projection

- render node/edge graph in Mycelium UI
- support entity drill-down and evidence pane
- show planned vs live edges clearly

### Phase 4 — Governance and Verification

- attach issues/tasks/policies to graph nodes
- add drift checks for graph vs code
- later attach ZKP / shadow node verification entities

---

## Anti-Patterns to Avoid

- using the event stream as the reference graph
- inventing node types without source evidence
- mixing planned edges with runtime edges without status markers
- putting the graph only inside a dashboard component
- treating docs as the sole source of truth

---

## Immediate Next Implementation

The next practical step should be:

1. create `packages/shared/src/mycelium/reference-graph.ts`
2. seed 15-25 nodes and 20-30 edges from current known surfaces
3. expose a read-only snapshot endpoint
4. only then connect UI rendering

This keeps the graph:

- backwards-compatible
- auditable
- incremental
- honest

---

## Decision

The Mycelium reference system should be a **canonical graph of entities + relations + evidence**, not a vague metaphor and not a runtime event dump.

**Mycelium = topology + evidence + telemetry.**

The event bus tells us what moved.
The reference graph tells us what is connected.
