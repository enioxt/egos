# VPS Orchestration Brief (ORB-001)

**Version:** 1.0.0 | **Date:** 2026-04-07 | **Status:** Active  
**Scope:** Codex + Claude Code + OpenClaw + Gemini CLI + Hermes (future)  
**Purpose:** Define routing, contracts, fallback chains, and cost attribution for overlapping execution layers

---

## Overview

The VPS runs **5 overlapping execution layers**, each with different:
- **Cost models** (free tier, pay-per-use, subscription, session-based)
- **Latency profiles** (milliseconds to hours)
- **Reliability guarantees** (stateless to persistent)
- **Auth models** (API keys, JWT, OAuth)

**This brief** specifies who calls what, in what order, and what happens when failures occur.

---

## Layer Map

| Layer | Type | Cost | Latency | Reliability | Status | Owned By |
|-------|------|------|---------|-------------|--------|----------|
| **Codex** | Always-on proxy | Free → $50/mo | <1s | 99.9% (best-effort) | ✅ Live | Infrastructure |
| **Claude Code** | Session-based | $550/mo | Variable | 99% | ✅ Live | User (Enio) |
| **OpenClaw** | Sandbox LLM | $40/mo (model) | <5s | 99% | ✅ Live | Billing |
| **Gemini CLI** | Research/batch | Free tier | <10s | 90% (daily quota) | ✅ Live | GEM-TOKEN-001 |
| **Hermes** | 24/7 executor | R$0-40/mo | <30s | 95% | ⏳ P35 | Infrastructure |

---

## Routing Decision Tree

```
Task arrives → Classify by latency + cost sensitivity
  │
  ├─ RESEARCH (low urgency, high accuracy) → GEM-TOKEN-001 (free Gemini)
  │   └─ Timeout → FALLBACK: DashScope or MiniMax
  │
  ├─ REASONING (high accuracy, low latency) → Claude Code (pay)
  │   └─ Session unavailable → FALLBACK: OpenClaw sandbox
  │
  ├─ EXECUTION (batch, no user present) → Hermes (after MVP)
  │   └─ Failure → FALLBACK: Codex proxy (async)
  │
  ├─ ALWAYS-ON (monitoring, health checks) → Codex proxy (free)
  │   └─ Rate limit → FALLBACK: DashScope or log locally
  │
  └─ URGENT (user blocking) → Claude Code (immediate)
      └─ Unavailable → Escalate to Enio (manual)
```

---

## Contracts & Responsibilities

### Codex Proxy (Always-On)
- **Role:** Default research/synthesis layer, monitoring
- **Cost:** Free tier (<100 reqs/day), pay-as-you-go thereafter
- **Token Refresh:** `gemini-token-refresh.sh` (uses Codex patterns)
- **Fallback to:** DashScope free tier (lower quality, acceptable for internal research)
- **Monitoring:** VPS watchdog checks `/health` every 5min
- **Contract:** "I will respond to simple queries within 1s, or return 503 Service Unavailable"

### Claude Code (Session-Based)
- **Role:** High-reasoning, user-facing, code generation
- **Cost:** $550/month fixed (unlimited requests in session)
- **Availability:** Only when user is active (blocking)
- **Fallback to:** OpenClaw sandbox (lower quality, but reliable)
- **Contract:** "I am available for the full user session, or escalate to user"

### OpenClaw (Sandbox LLM)
- **Role:** Backup reasoning layer, cost-capped sandbox
- **Cost:** $40/month (subscription) for model access
- **Rate Limit:** Enforced by billing proxy (OC-031..034)
- **Fallback to:** Hermes (simple tasks) or Codex (research)
- **Contract:** "I will process tasks in <5s, or return 429 if quota exceeded"

### Gemini CLI (Daily Quota)
- **Role:** Research, discovery, batch analysis
- **Cost:** Free daily quota (varies by account, ~1M tokens or similar)
- **Token Refresh:** `gemini-token-refresh.sh` (every 2 hours)
- **Quota Tracking:** `gemini-quota-tracker.ts` (daily cron)
- **Fallback to:** DashScope (different free tier) or MiniMax (paid, R$40/mo)
- **Contract:** "I will respond to research queries while quota permits"

### Hermes (Future: P35+)
- **Role:** 24/7 autonomous executor, skill generation
- **Cost:** R$0-40/month (mostly free tier LLM costs)
- **Availability:** Always online, no user intervention needed
- **Fallback to:** Codex proxy for critical tasks
- **Contract:** "I execute routine tasks 24/7, self-improving, or delegate to other layers"

---

## Fallback Chains (ORB-002)

### Chain 1: Research Fallback
```
Gemini CLI (free) 
  → [on quota exhausted]
  → DashScope (free tier)
    → [on failure]
    → MiniMax-M2.7 ($40/mo)
      → [on failure]
      → Codex proxy (last resort)
```

### Chain 2: Reasoning Fallback
```
Claude Code (session)
  → [on unavailable]
  → OpenClaw sandbox
    → [on rate limit]
    → Hermes + Codex (cascade)
      → [on failure]
      → Log task for manual review
```

### Chain 3: Execution Fallback
```
Hermes (autonomous)
  → [on failure]
  → Codex proxy (async)
    → [on rate limit]
    → Supabase task queue (manual pickup)
```

---

## Cost Attribution (ORB-003)

Every task logs:
```typescript
{
  task_id: string;           // Unique identifier
  service: "codex" | "claude" | "openclaw" | "gemini" | "hermes";
  request_timestamp: ISO8601;
  request_tokens: number;
  response_tokens: number;
  total_tokens: number;
  estimated_cost_usd: number;
  actual_cost_usd: number;   // For metered services (Codex, OpenClaw)
  status: "success" | "fallback" | "error";
  fallback_chain_used: string; // Which chain was activated
  duration_ms: number;
}
```

Logs → Supabase table: `vps_service_cost_ledger`

**Monthly Review:**
- Codex: Sum(actual_cost) from service='codex'
- Claude Code: $550 (fixed) + overage
- OpenClaw: $40 (fixed) + usage
- Gemini: $0 (free tier) or overage
- Hermes: R$X based on uptime + skill generation
- **Total MRR:** Sum all services

---

## Health Checks (VPS Watchdog)

Every 5 minutes, VPS watchdog verifies:

```bash
# Codex proxy health
curl -s http://localhost:18802/health | jq .status

# Guard Brasil API health
curl -s https://guard.egos.ia.br/health | jq .status

# HQ dashboard
curl -s https://hq.egos.ia.br/api/health (expects 307 redirect)

# OpenClaw integration
curl -s http://localhost:8000/health | jq .status

# Hermes (when live)
curl -s http://localhost:3000/health | jq .status
```

If service fails: Log to `/var/log/egos/watchdog.log` + alert Telegram (VPS-MEMORY-001 pattern).

---

## Priority Ordering

**When multiple tasks queue simultaneously:**

1. **ALWAYS-ON first:** Monitoring, health checks (Codex proxy)
2. **USER-BLOCKING second:** Claude Code sessions (must not timeout)
3. **RESEARCH third:** Batch jobs (Gemini CLI or fallback)
4. **BACKGROUND last:** Hermes async tasks (lowest priority)

Token quota exhaustion order (defensive):
- Sacrifice research → Accept lower quality from fallback
- Sacrifice background → Defer to next day
- **Never sacrifice:** User sessions (Claude Code)

---

## Integration Points

### 1. Orchestrator Module
**File:** `packages/shared/orchestrator.ts`  
**Export:** `async function route(task, context): Promise<Response>`  
**Logic:** Implements routing decision tree + fallback chains

### 2. Cost Ledger
**Table:** `vps_service_cost_ledger` (Supabase)  
**Columns:** task_id, service, tokens, cost_usd, status, timestamp  
**Populated by:** Each service adapter logs after execution

### 3. HQ Dashboard Widget
**File:** `apps/egos-hq/app/orchestration.tsx`  
**Shows:** Real-time status of all 5 layers (health, tokens remaining, cost YTD)

### 4. Telegram Alerts
**Config:** TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID in VPS .env  
**Triggers:** Layer failure, quota exhausted, cost threshold exceeded

---

## Decisions & Rationale

### Decision 1: Codex as default (not Claude Code)
- Claude Code has $550/month cost → only for user-interactive sessions
- Codex is free → ideal for background research/monitoring
- Fallback chain provides reasonable quality degradation

### Decision 2: Gemini CLI over other APIs
- Free tier most generous (1M tokens or equivalent)
- Token refresh pattern already proven (Codex proxy)
- Fallback chains tested in production (GEM-TOKEN-001)

### Decision 3: OpenClaw as backup reasoning (not Codex)
- Codex ≈ search → good for research, weak at reasoning
- OpenClaw ≈ reasoning LLM → good for code/logic, better for fallback
- Cost: $40/mo subscription covers both reasoning + sandbox

### Decision 4: Hermes async (not real-time)
- 24/7 uptime valuable for skill generation + overnight research
- Autonomous execution risk → keep out of critical path initially
- 1-week trial (2026-04-08..2026-04-15) validates ROI before scaling

---

## Rollout Checklist (ORB-002, ORB-003, ORB-004)

- [ ] **ORB-002:** Wire fallback chains in `packages/shared/orchestrator.ts` (2h)
- [ ] **ORB-003:** Add cost attribution per task (3h)
- [ ] **ORB-004:** Create HQ dashboard widget (2h)
- [ ] **GEM-TOKEN-001:** Deploy Gemini token refresh cron (1h)
- [ ] **GEM-TOKEN-002:** Deploy quota tracker (30min)
- [ ] **Test:** Route 10 tasks, verify fallback triggers correctly
- [ ] **Monitor:** Check Telegram alerts + cost ledger for 24h
- [ ] **Document:** Update VPS_RESOURCE_SSOT.md with actual costs

---

## References

- **VPS Infrastructure:** `docs/VPS_RESOURCE_SSOT.md`
- **Codex Proxy:** `packages/shared/orchestrator/codex-proxy.ts`
- **Monitoring:** `scripts/vps-ram-monitor.sh` + `scripts/gemini-quota-tracker.ts`
- **HQ:** `apps/egos-hq/app/api/hq/orchestration.ts`

---

*Canonical brief for VPS orchestration. Update as new layers are added.*
