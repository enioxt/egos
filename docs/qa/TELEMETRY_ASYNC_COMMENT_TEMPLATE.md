# Telemetry QA — Async Comment Template

Use este template em comentários de PR/Issue para coordenação assíncrona entre agentes.

```md
### QA Telemetry Review (EGOS)

**Scope reviewed:**
- [ ] EGOS-TELEM-001 Agent execution tracking
- [ ] EGOS-TELEM-002 Tool attribution
- [ ] EGOS-TELEM-003 Gargalo heatmap
- [ ] EGOS-TELEM-004 Real-time dashboard
- [ ] EGOS-TELEM-005 Forecast

**Verified evidence:**
- Command(s): `...`
- File(s): `...`
- Runtime proof/log(s): `...`

**Findings:**
1. [risk level: low/med/high] ...
2. ...

**Recommended next commit (smallest safe step):**
- ...

**Blocking items (if any):**
- ...

**Owner suggestion:** @claude / @codex
```

## Current baseline (2026-04-01)

- Shared telemetry now has scaffolds for `recordAgentSession()` and `recordToolCall()`.
- `agents/cli.ts run` now emits `recordAgentSession()` on execution end (success/failure + duration).
- Next focus: wire tool-level events and build Supabase schema/query layer.
