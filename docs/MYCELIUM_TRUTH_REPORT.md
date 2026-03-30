# MYCELIUM_TRUTH_REPORT.md — EGOS-070

> **Auditor:** EGOS Systems Auditor
> **Date:** 2026-03-30
> **EGOS Task:** EGOS-070 — Mycelium truth repair
> **Scope:** All Mycelium capability claims in `/home/enio/egos` and `/home/enio/egos-lab`

---

## 1. What Is REAL

### 1.1 Reference Graph (in-memory, TypeScript)

**File:** `/home/enio/egos/packages/shared/src/mycelium/reference-graph.ts`
**Also at:** `/home/enio/egos-lab/packages/shared/src/mycelium/reference-graph.ts` (identical copy)

Evidence: `code` only.

This file is the **sole implemented Mycelium artifact** in both repos. It exports:
- Type definitions: `ReferenceEntityType`, `ReferenceRelation`, `ReferenceEvidence`, `NodeStatus`
- Core interfaces: `ReferenceNode`, `ReferenceEdge`, `ReferenceGraph`
- Utility functions: `createGraph`, `findNode`, `findEdgesFrom`, `findEdgesTo`, `nodesByType`, `nodesByStatus`, `graphHealth`
- Kernel seed graph: 27 nodes, 32 edges — pure in-memory, static TypeScript data

**What it does:** Defines the canonical topology schema and seeds a static snapshot of the EGOS mesh. No persistence. No network. No runtime event emission.

### 1.2 Local Event Bus

**File:** `agents/runtime/event-bus.ts` (in egos-lab)

A local, in-memory, synchronous event bus. Events dispatched within a single process. JSONL audit trail written to disk. This is the only runtime component with "Mycelium" in its conceptual lineage that actually executes.

### 1.3 Documentation Layer

The following docs exist and are accurate in their own sections:

| Doc | Path | Status | Notes |
|-----|------|--------|-------|
| Mycelium Overview (kernel) | `docs/concepts/mycelium/MYCELIUM_OVERVIEW.md` | Accurate | Correctly separates layers; marks planned items |
| Mycelium Overview (egos-lab) | `egos-lab/docs/knowledge/MYCELIUM_OVERVIEW.md` | Partially inaccurate | References `node.ts`, `schema.ts`, `test-poc.ts` — none exist |
| SYSTEM_MAP.md | `docs/SYSTEM_MAP.md` | Accurate | Lists Mycelium Graph as `reference-graph.ts`; marked Active |
| SSOT_REGISTRY.md | `docs/SSOT_REGISTRY.md` | Accurate | Correctly cites reference-graph.ts as canonical |

---

## 2. What Is PLANNED (not yet implemented)

### 2.1 Redis Pub/Sub Bridge (EGOS-089)

Referenced in: `egos-lab/docs/plans/tech/MYCELIUM_NETWORK.md` Phase 2

The plan is to use the existing Railway Redis instance to add Pub/Sub channels for cross-process event propagation between Vercel, Railway workers, and the dashboard. No implementation exists.

Files claimed but not found in either repo:
- `packages/shared/src/mycelium/node.ts` — MyceliumNode wrapper (not present)
- `packages/shared/src/mycelium/schema.ts` — Zod event schema (not present)
- `scripts/mycelium/test-poc.ts` — PoC test script (not present)
- `apps/egos-web/src/lib/mycelium.ts` — Dashboard lib (not present in egos kernel)
- `apps/egos-web/api/mycelium-stats.ts` — Stats API (not present in egos kernel)
- `apps/egos-web/src/components/MyceliumDashboard.tsx` — UI component (not present in egos kernel)

### 2.2 Neo4j Graph Database

**No Mycelium-related Neo4j implementation exists in either the `egos` or `egos-lab` repos.**

The `bracc-neo4j` Docker service running on Hetzner VPS (77M entities) belongs to `br-acc` — a standalone Python OSINT platform. It is **correctly classified** in `docs/ECOSYSTEM_CLASSIFICATION_REGISTRY.md` and is not part of Mycelium.

The `/mycelium` command in `.claude/commands/mycelium.md` queries `bracc-neo4j` as a "Graph/Memory" check — this is a **misleading conflation**: Neo4j belongs to br-acc, not to the EGOS Mycelium layer.

### 2.3 ZKP / Shadow Nodes

Referenced in `egos-lab/docs/plans/tech/MYCELIUM_NETWORK.md` Phase 3.

No `snarkjs`, `circom`, ZKP circuit files, or Shadow Node code exists anywhere in egos or egos-lab. Fully aspirational.

### 2.4 Persistent Event Storage (Supabase)

Referenced in `egos-lab/docs/plans/tech/MYCELIUM_NETWORK.md` Phase 2.

No `mycelium_events` table, no `mycelium_shadow_nodes` table, no migration files. SQL shown in the plan is a design artifact only.

### 2.5 SSE Real-Time Stream

Referenced as `GET /api/mycelium/events`. No endpoint exists in either repo.

---

## 3. What Is ASPIRATIONAL (future / marked planned)

| Claim | Location | Disposition |
|-------|----------|-------------|
| "15 agents → Mycelium Events" routing table | egos-lab MYCELIUM_NETWORK.md §4.1 | ASPIRATIONAL — agents don't emit Mycelium events; event-bus.ts is local only |
| "ZKP proofsVerified: 8492" in stats API sample | egos-lab MYCELIUM_NETWORK.md §6 | ASPIRATIONAL — no ZKP system exists |
| "nodesOnline: 4, totalEvents24h: 1247" in stats sample | egos-lab MYCELIUM_NETWORK.md §6 | ASPIRATIONAL — sample JSON, not live data |
| "Shadow Nodes earn ETHIK for verification" | egos-lab MYCELIUM_NETWORK.md §3.3 | ASPIRATIONAL — no ETHIK token system |
| MyceliumCity 3D + AgentRank visualization | docs/conversaGROK.md (research chat) | ASPIRATIONAL — design exploration, not a project plan |
| node.ts, schema.ts, test-poc.ts (bridge PoC) | egos-lab MYCELIUM_OVERVIEW.md §1.1 | ASPIRATIONAL — files do not exist |
| MyceliumDashboard.tsx, mycelium-stats API | egos-lab MYCELIUM_NETWORK.md §1 | ASPIRATIONAL (for egos-lab context) — may exist in egos-web app but not in kernel |

---

## 4. Disposition for Each Doc

| Document | Path | Disposition | Action |
|----------|------|-------------|--------|
| reference-graph.ts | `packages/shared/src/mycelium/reference-graph.ts` | **REAL** — kept-as-ref | No change |
| MYCELIUM_OVERVIEW.md (kernel) | `docs/concepts/mycelium/MYCELIUM_OVERVIEW.md` | **ACCURATE** — kept-as-ref | No change needed; already marks planned items correctly |
| MYCELIUM_NETWORK.md | `egos-lab/docs/plans/tech/MYCELIUM_NETWORK.md` | **PARTIALLY INFLATED** — update-in-place | Phase 2 table shows items as LIVE that are not; Neo4j/ZKP/SSE need PLANNED callouts |
| MYCELIUM_OVERVIEW.md (egos-lab) | `egos-lab/docs/knowledge/MYCELIUM_OVERVIEW.md` | **PARTIALLY FALSE** — update-in-place | References node.ts/schema.ts/test-poc.ts that don't exist |
| /mycelium command | `.claude/commands/mycelium.md` | **MISLEADING** — update-in-place | Neo4j step conflates bracc-neo4j (br-acc OSINT) with Mycelium layer |
| vps.md command | `.claude/commands/vps.md` | **MISLEADING** — update-in-place | Labels `bracc-neo4j` as "Neo4j/Mycelium" — should read "Neo4j/br-acc" |
| docs/conversaGROK.md | `docs/conversaGROK.md` | **RESEARCH CHAT** — kept-as-ref | Brainstorm export, not spec. No action; not SSOT. |
| SYSTEM_CHECKLIST_20260325.md | `docs/SYSTEM_CHECKLIST_20260325.md` | **HISTORICAL** — kept-as-ref | Point-in-time checklist; not SSOT |

---

## 5. Summary: Reality vs Claims

| Layer | Claimed Status | Actual Status |
|-------|---------------|---------------|
| In-memory event bus | LIVE | LIVE (event-bus.ts in egos-lab) |
| Reference graph (static) | LIVE | LIVE (reference-graph.ts, both repos) |
| Redis Pub/Sub bridge | LIVE (in MYCELIUM_NETWORK.md table) | NOT IMPLEMENTED — planned |
| Dashboard / Stats API | LIVE (in MYCELIUM_NETWORK.md table) | NOT in egos kernel — may be in egos-web app |
| Neo4j as Mycelium store | Implied by /mycelium command | FALSE — Neo4j is br-acc's database, unrelated to Mycelium |
| ZKP / Shadow Nodes | Phase 3 planned | NOT STARTED — aspirational |
| Supabase event persistence | Phase 2 planned | NOT IMPLEMENTED |
| SSE real-time stream | Designed | NOT IMPLEMENTED |

---

## 6. Docs Modified Under This Task

The following files received `> PLANNED` callout blocks at the top:

- `egos-lab/docs/plans/tech/MYCELIUM_NETWORK.md` — Phase 2 table items marked
- `egos-lab/docs/knowledge/MYCELIUM_OVERVIEW.md` — node.ts/schema.ts refs marked
- `.claude/commands/mycelium.md` — Neo4j step clarified
- `.claude/commands/vps.md` — bracc-neo4j label corrected

---

- [x] **EGOS-070** — Mycelium truth repair complete (2026-03-30)
