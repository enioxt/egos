# Mycelium — Single Source of Truth

> **Version:** 1.0.0 | **Updated:** 2026-04-01
> **Owner:** EGOS Kernel | **Domain:** Event Bus + Reference Graph + File Signatures

---

## What is Mycelium?

Mycelium is EGOS's distributed event bus and reference graph layer. It:
1. **Routes events** between agents and apps (MyceliumBus → Supabase/Redis)
2. **Tracks cross-repo references** (file signatures, symlinks, governance pointers)
3. **Exposes system state** via snapshot API (maturity, telemetry, surfaces)

**Analogy:** fungal mycelium network — invisible connective tissue that lets independent nodes communicate without coupling.

---

## Real Code Map (~1600 LOC total)

### Kernel — packages/shared (canonical library)

| File | LOC | Role |
|------|-----|------|
| `egos/packages/shared/src/mycelium/redis-bridge.ts` | 337 | MyceliumNode — Redis pub/sub abstraction |
| `egos/packages/shared/src/mycelium/reference-graph.ts` | 300 | Reference graph — cross-repo edge tracking |

### Runtime — agents/runtime

| File | LOC | Role |
|------|-----|------|
| `egos/agents/runtime/event-bus.ts` | 327 | **CANONICAL** — MyceliumBus in-memory + JSONL audit trail |
| `egos-lab/agents/runtime/event-bus.ts` | 327 | Duplicate — **migrate to egos/ when egos-lab deactivates** |

### Scripts (tools)

| File | LOC | Role |
|------|-----|------|
| `egos-lab/scripts/mycelium/file-signature-sync.ts` | 96 | File signature propagation across repos |
| `egos-lab/scripts/mycelium/readme-linker.ts` | 172 | Symlink/reference linker for docs |
| `egos-lab/scripts/mycelium/test-poc.ts` | 63 | POC test harness |

### Frontend surfaces

| File | LOC | Role |
|------|-----|------|
| `egos/apps/commons/src/lib/mycelium.ts` | 38 | Frontend event emitter shim (fires events to VITE_MYCELIUM_URL) |
| `egos-lab/apps/egos-web/src/lib/mycelium.ts` | 92 | Rich types (MyceliumSnapshot, Surfaces, Events) |
| `egos-lab/apps/egos-web/api/mycelium-stats.ts` | 281 | Snapshot API endpoint |

### Skills / Orchestration

| File | Role |
|------|------|
| `~/.egos/.claude/commands/mycelium.md` | `/mycelium` skill |
| `~/.egos/.claude/commands/mycelium-check.md` | `/mycelium-check` skill |
| `egos/.guarani/prompts/meta/mycelium-orchestrator.md` | Meta-prompt for orchestration |

---

## Architecture

```
MyceliumBus (in-memory, agents/runtime/event-bus.ts)
  ↓ publish()
Supabase agent_events table   ←→   Redis pub/sub (packages/shared/mycelium/redis-bridge.ts)
  ↓
Reference Graph (packages/shared/mycelium/reference-graph.ts)
  ↓
Snapshot API (egos-lab/apps/egos-web/api/mycelium-stats.ts)
  ↓
Web Dashboard (egos-lab/apps/egos-web)
```

---

## What IS implemented (code-backed)

- In-memory event bus with JSONL audit trail ✅
- Redis pub/sub wrapper ✅
- Cross-repo reference graph (edge tracking) ✅
- File signature sync scripts ✅
- Snapshot API (maturity, surfaces, telemetry) ✅
- Frontend event emitter ✅

## What is NOT implemented (plan only — not code)

- **NATS transport** — only in docs/plans, NO code
- **ZKP shadow nodes** — `status: 'planned'` in types, NO implementation
- **Distributed broker** — Railway Worker health endpoint exists but is NOT a Mycelium event broker
- **Producer/consumer pair for Redis** — wrapper exists, wiring NOT confirmed active

---

## Rules

1. **Canonical runtime:** `egos/agents/runtime/event-bus.ts` — do not duplicate
2. **Library SSOT:** `egos/packages/shared/src/mycelium/` — shared types + bridges
3. **Vocab rule:** Never mention NATS, ZKP, shadow nodes as "implemented" — they are planned only
4. **egos-lab copies:** migrate to egos/ when egos-lab deactivates
5. **All docs:** must point here as the reference
