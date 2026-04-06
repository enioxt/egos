# Dream Cycle — Overnight Autonomous Intelligence

> **Version:** 1.0.0 | **Created:** 2026-04-06
> **Concept:** While Enio sleeps, EGOS reads, thinks, creates, and fixes.
> **Goal:** Wake up to a fully briefed HQ dashboard with nightly work done.

---

## What Is the Dream Cycle?

A coordinated set of VPS cron jobs + CCR agents that run between 23h00–06h00 BRT.
Each job has a defined scope, uses free/cheap LLMs (Gemma 4 31B / Qwen 3.6 Plus),
writes outputs to Supabase, and surfaces results in HQ dashboard at morning login.

---

## Pipeline Architecture

```
23h00  Log Harvester       → reads all container logs → Supabase egos_nightly_logs
00h00  Gem Hunter CCR      → (already running 2h37 Mon+Thu)
00h17  Governance Sentinel → (already running daily)
01h00  Intelligence Engine → cross-references logs + tasks → creates egos_nightly_reports
02h00  Auto-Healer         → applies known fixes for known errors (restart-only scope)
06h00  Morning Briefing    → compiles final report → Telegram + WhatsApp → HQ /events
```

---

## Jobs Specification

### Job 1: Log Harvester (VPS cron — 23h00 BRT daily)
**Script:** `/opt/apps/egos-agents/scripts/log-harvester.sh`
**Runtime:** ~5 min | **LLM:** None (pure log parsing)

**Reads:**
- `docker logs <container> --since 24h` for all 19 containers
- `/opt/bracc/infra/logs/access.log` (Caddy)
- VPS system: `journalctl --since yesterday`

**Writes to Supabase `egos_nightly_logs`:**
```json
{
  "date": "YYYY-MM-DD",
  "container": "guard-brasil-api",
  "level": "error|warn|info",
  "count": 42,
  "samples": ["..."],
  "summary": "5 401 errors, 2 500s on /v1/inspect"
}
```

**Patterns detected:**
- Container restart count > 3 → `severity: critical`
- HTTP 5xx rate > 1% → `severity: high`
- Auth failures (401/403) spike → `severity: high`
- New API endpoints hitting 404 → `severity: medium`
- Guard Brasil calls count → feeds GTM metrics

---

### Job 2: Intelligence Engine (CCR slot — extend Governance Sentinel OR new VPS cron 01h00)
**Script:** `agents/agents/intelligence-engine.ts` (new agent)
**Runtime:** ~15 min | **LLM:** Gemma 4 31B (default tier, 1500 req/day)

**Reads:**
- Supabase `egos_nightly_logs` (from Job 1)
- `TASKS.md` (P0 tasks, stale tasks)
- Gem Hunter latest output
- Guard Brasil API call count (from logs)
- `egos_learnings` table (recent session learnings)

**Produces:**
1. **Intelligence Report** saved to `docs/jobs/YYYY-MM-DD-nightly-intelligence.md`
   - Error summary by severity
   - Guard Brasil usage stats
   - Top Gem Hunter finds (if ran tonight)
   - Stale P0 tasks (>3 days with no commit)
   - Recommended new tasks (scored by revenue impact)
2. **Auto-created TASKS.md entries** for critical blockers
3. **Telegram notification** with 3-bullet summary

---

### Job 3: Auto-Healer (VPS cron — 02h00 BRT, only if critical issues detected)
**Script:** `/opt/apps/egos-agents/scripts/auto-healer.sh`
**Runtime:** ~3 min | **LLM:** None (rule-based)

**Scope (limited by design):**
- Container down → `docker start <container>`
- Caddy 502 → `docker restart infra-caddy-1`
- High memory usage > 90% → `docker restart <container>` (except DB)
- SSL cert expiry < 7 days → Telegram alert (cannot auto-renew)

**CANNOT DO:**
- Deploy code changes
- Modify databases
- Change Caddyfile routing
- Spend money

**Writes:** all actions to Supabase `egos_agent_events` with `source: auto-healer`

---

### Job 4: Morning Briefing (VPS cron — 06h30 BRT daily)
**Script:** `/opt/apps/egos-agents/scripts/morning-briefing.sh`
**Runtime:** ~2 min | **LLM:** Gemini 2.5 Flash (condense text)

**Compiles:**
- Last night's intelligence report (top 5 items)
- Auto-healer actions taken
- Guard Brasil usage (calls since yesterday)
- M-007 status (if still unsent → highlight RED)
- Any new TASKS created overnight

**Sends to:**
- Telegram (TELEGRAM_AUTHORIZED_USER_ID)
- WhatsApp (Evolution API daily report — already wired)

---

## HQ Dashboard Integration

### New `/events` page (CTRL-014 — existing task)
Real-time stream from `egos_agent_events` table (Supabase Realtime).
Shows: all Dream Cycle activity, auto-healer actions, log summaries.

### New HQ card: "Last Night" on home page
- Dream Cycle ran: YES/NO
- Issues found: N (N critical)
- Tasks created: N
- Guard Brasil calls last 24h: N
- Link → full nightly report

---

## Free LLM Budget

| Job | LLM Used | Req/day | Cost |
|-----|----------|---------|------|
| Log Harvester | None | 0 | $0 |
| Intelligence Engine | Gemma 4 31B | ~10-15 | $0 (free quota) |
| Morning Briefing | Gemini 2.5 Flash | ~3 | $0 (free quota) |
| Auto-Healer | None | 0 | $0 |
| **Total** | | **~15-18 req/day** | **$0** |

Daily free quotas available: Gemma 4 31B = 1,500 req, Gemini 2.5 Flash = 500 req.
The Dream Cycle uses ~1% of available free quota.

---

## Implementation Phases

### Phase 1 — Foundation (this week)
- [ ] DC-001: Supabase tables: `egos_nightly_logs`, `egos_nightly_reports` + RLS
- [ ] DC-002: Log Harvester script (bash, no LLM, parses Docker logs)
- [ ] DC-003: VPS cron: `0 23 * * * /opt/apps/egos-agents/scripts/log-harvester.sh`
- [ ] DC-004: Auto-Healer script (bash, rule-based container restart)

### Phase 2 — Intelligence (next week)
- [ ] DC-005: `agents/agents/intelligence-engine.ts` (new agent using chatWithLLM Gemma 4)
- [ ] DC-006: Wire to CCR Governance Sentinel slot (extend existing job)
- [ ] DC-007: Auto-task creation from intelligence report → TASKS.md append

### Phase 3 — HQ Integration (2 weeks)
- [ ] DC-008: HQ `/events` page (CTRL-014 already planned)
- [ ] DC-009: HQ home "Last Night" card
- [ ] DC-010: Morning Briefing → Telegram + WhatsApp

---

## Why Gemma 4 31B (not Gemini Pro)?

From the thread (03/04/2026) + our own testing:
- **Strong:** code generation, structured output, reasoning over logs
- **Weak:** tool calling (don't use for agent execution — use Hermes-3 via OpenRouter)
- **Free:** 1,500 req/day via Google AI Studio (no monthly expiry, unlike Alibaba 90-day grant)
- **Qwen 3.6 Plus free:** $0 on OpenRouter, falls back to when Google daily limit hit

The Intelligence Engine does not need tool-calling — it reads data, synthesizes, writes.
Gemma 4 31B is the perfect fit.

---

*SSOT: docs/strategy/DREAM_CYCLE_SSOT.md*
*Related: apps/egos-hq/ (dashboard), agents/agents/ (intelligence-engine.ts)*
