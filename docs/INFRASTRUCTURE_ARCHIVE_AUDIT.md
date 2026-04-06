# INFRASTRUCTURE_ARCHIVE_AUDIT.md — Runtime & Archive Ops Snapshot

> **Date:** 2026-04-06
> **Status:** FIXO — operator-facing infrastructure inventory
> **Purpose:** durable reference for current runtime surfaces, recurring jobs, and archive-era operational findings that still matter to the kernel.

<!-- llmrefs:start -->
## LLM Reference Signature

- **Role:** infrastructure and operations audit snapshot for the 2026-04-06 documentation sweep
- **Summary:** records the durable VPS/runtime inventory used by the current kernel documentation set
- **Type:** FIXO
- **Read next:**
  - `docs/MASTER_INDEX.md` — ecosystem inventory and current runtime snapshot
  - `docs/EXECUTIVE_SUMMARY_DECISION_MATRIX.md` — decisions and follow-up actions
  - `docs/DOCUMENTATION_ARCHITECTURE_MAP.md` — document permanence and read order
<!-- llmrefs:end -->

---

## Current Runtime Surfaces

| Surface | Status | Notes |
|---------|--------|-------|
| Guard Brasil API | ✅ Live | Reference REST + MCP runtime in `apps/api/` |
| EGOS HQ | ✅ Live | Dashboard surface |
| EGOS Gateway | ✅ Live | Gateway/runtime coordination surface |
| Evolution API | ✅ Live | WhatsApp runtime used by validated patterns |
| Gem Hunter Server | ✅ Live | Discovery/API runtime |
| forja-notifications | ✅ Live | Validated WhatsApp instance |
| BRACC Neo4j | ✅ Standalone | Separate OSINT product boundary, not kernel Mycelium |

## Recurring Operational Jobs

- `Gem Hunter Refresh` — archive/BRACC-adjacent refresh loop
- `Log Harvester` — runtime observability collection
- `Watchdog` — health and resilience supervision

## Archive Findings That Still Matter

- Archive-era patterns remain **reference material**, not active runtime authority.
- BRACC stays **standalone** and must not be merged into kernel reference-graph surfaces.
- Self-Discovery is documented as a **separate future runtime**.
- Booking Agent remains **archived** unless a future product decision reopens it.

## Update Rule

Update this document when any of the following changes:

- runtime topology or service inventory
- recurring jobs or watchdog responsibilities
- boundary between kernel runtime and standalone products
- archive-derived operational patterns promoted into active use
