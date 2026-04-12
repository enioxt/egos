# INC-004: Supabase Realtime Quota Exhaustion

**Date:** 2026-04-11  
**Severity:** HIGH — caused grace period warning on Pro plan  
**Status:** RESOLVED  

## Summary

The `master-orchestrator` agent emitted 156,858 `orchestrator.schedule` events (severity=info) in 5 days (Apr 1-5, 2026). Each `emit()` call generated **two** Supabase Realtime messages:

1. Explicit broadcast via `ch.send()` (Realtime channel)
2. INSERT into `agent_events` table, which was in the `supabase_realtime` publication (Postgres-level Realtime trigger)

This double-emission exhausted the Supabase Pro plan Realtime Message Count quota.

## Root Cause Analysis

| Factor | Detail |
|--------|--------|
| **Runaway source** | `master-orchestrator` writing one event per agent-schedule-definition per execution (20+ schedule entries × frequent runs = 62K events/day) |
| **Double Realtime** | `emit()` broadcasted explicitly AND `agent_events` table was in `supabase_realtime` publication |
| **No rate limiting** | Event bus had no per-source rate limiting |
| **No severity gate** | All events (including info) were broadcast via Realtime |
| **No retention** | Old events accumulated indefinitely |
| **No monitoring** | No alerting on event volume spikes |

## Fixes Applied

### Immediate (Supabase — via MCP migrations)

1. **Removed `agent_events` from `supabase_realtime` publication** — eliminated double-broadcast
2. **Removed `intelink_entities` and `intelink_relationships`** from publication — no active subscribers
3. **Deleted 157K stale rows** from `agent_events` (Apr 1-5 runaway data)
4. **Added `pg_cron` retention job** — DELETE > 7 days, runs daily 03:00 UTC
5. **Added `idx_agent_events_created_at` index** — fast retention DELETEs
6. **Added `agent_events_daily_volume` monitoring view**

### Code (packages/shared/src/event-bus.ts)

1. **Severity gate**: `emit()` only broadcasts via Realtime when `severity >= warn`
2. **Rate limiter**: max 100 events per source per 60-second window; excess dropped with warning
3. **`cleanup()` clears rate buckets**

### Pre-commit (scripts/check-supabase-safety.sh)

1. **Blocks** adding tables to `supabase_realtime` publication without review
2. **Warns** on Supabase INSERT/UPSERT inside loops
3. **Warns** on CREATE TABLE without RLS
4. **Warns** on event-bus.ts modifications without INC reference
5. **Override**: `SUPABASE-SAFETY-OVERRIDE: <reason>` in commit message

### CARTEIRA-LIVRE (second Supabase project)

1. **Added `pg_cron` retention** for `volante_system_logs` (7M cumulative inserts!) — DELETE > 7 days
2. **Added retention** for `volante_admin_events` — DELETE > 30 days
3. **Added index** on `volante_system_logs.created_at`

## Prevention Rules

1. **Never add tables to `supabase_realtime` publication** without reviewing event volume
2. **info-severity events** are audit-only — never Realtime-broadcast
3. **All Supabase-writing code** must go through the shared event-bus (which has rate limiting)
4. **Every Supabase project** must have `pg_cron` retention for log/event tables
5. **Pre-commit hook** blocks dangerous Supabase patterns

## Monitoring

Query to check for runaway agents:
```sql
SELECT * FROM agent_events_daily_volume
WHERE event_count > 1000
ORDER BY day DESC;
```

## Timeline

| When | What |
|------|------|
| Apr 1 | master-orchestrator starts writing schedule events (11K/day) |
| Apr 3 | Volume spikes to 51K/day |
| Apr 4 | Peak: 62K/day — Realtime quota exhaustion begins |
| Apr 6 | Orchestrator stops (12 events) — possibly killed manually |
| Apr 11 | Grace period warning detected in Supabase dashboard |
| Apr 11 | Full root cause analysis + all fixes applied |

## Related

- INC-001: Force-push incident (2026-04-06)
- INC-003: TASKS.md anti-hallucination (2026-04-08)
