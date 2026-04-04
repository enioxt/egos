# EGOS Master API — PRD (Product Requirements Document)

> **Version:** 1.0.0 | **Created:** 2026-04-04 | **Author:** Claude Opus 4.6  
> **Status:** INVESTIGATION PHASE | **Priority:** P0 (Enables all integrations)  
> **Focus Alignment:** Guard Brasil + Gem Hunter (controls both APIs)

---

## Problem Statement

The EGOS ecosystem has **multiple disconnected APIs** running independently:
- Guard Brasil API (guard.egos.ia.br:3001)
- Gem Hunter API (port 3097)
- Eagle Eye API (eagleeye.egos.ia.br:3090)
- Evolution API / WhatsApp (port 8080)
- VPS Crons (8 agents running independently)

There is **no unified control plane**. When Enio sends a WhatsApp message, nothing happens. There is no way to:
1. Query system state from any channel (WhatsApp, Telegram, Discord, CLI)
2. Trigger actions across services from a single command
3. Get aggregated health/cost/metrics from one endpoint
4. Route a natural language request to the correct service

---

## Solution: EGOS Master API (Control Plane)

A single API that:
1. **Receives** commands from any channel (WhatsApp, Telegram, CLI, HTTP)
2. **Routes** them to the correct service or agent
3. **Orchestrates** multi-step workflows across services
4. **Reports** results back to the originating channel
5. **Monitors** all sub-services health + costs + metrics

---

## 3 Architecture Options

### Option A: API Gateway Pattern (Industry SOTA — Kong/Traefik style)

```
WhatsApp/Telegram/Discord/CLI
         ↓
   [Caddy Reverse Proxy]
         ↓
   [EGOS Gateway API]         ← Single Bun/Hono server (port 3000)
    ├── /v1/guard/*           → proxy to Guard Brasil (3001)
    ├── /v1/gems/*            → proxy to Gem Hunter (3097)
    ├── /v1/eagle/*           → proxy to Eagle Eye (3090)
    ├── /v1/whatsapp/*        → proxy to Evolution API (8080)
    ├── /v1/agents/*          → trigger agent runner
    ├── /v1/health            → aggregate all service health
    ├── /v1/costs             → aggregate from Supabase telemetry
    ├── /v1/command            → NLP router (parse natural language)
    └── /webhooks/*           → receive callbacks from all services
```

**Mechanism:** Thin proxy layer. Each request is authenticated, routed to the correct backend, and the response is returned. The `/v1/command` endpoint uses an LLM to parse natural language ("check guard health" → GET /v1/guard/health).

**What it captures:** Request/response for ALL services, unified auth, cost aggregation.

**Effort:** ~8h (Hono server + proxy routes + Caddy config + Supabase logging)

**Pros:**
- Industry standard (Kong, Traefik, AWS API Gateway pattern)
- Each backend stays independent — gateway only routes
- Easy to add new services (1 route config)
- Unified auth (one API key for everything)

**Cons:**
- Another service to maintain
- Single point of failure (mitigated by Caddy health checks)
- NLP routing adds latency (~200ms for LLM call)

---

### Option B: Event-Driven Orchestrator (SOTA — Temporal/Inngest style)

```
WhatsApp/Telegram/Discord/CLI
         ↓
   [Message Ingestion]
         ↓
   [Supabase Realtime]        ← Events table (agent_events)
         ↓
   [Orchestrator Workers]     ← Bun processes watching events
    ├── guard-worker          → processes Guard requests
    ├── gem-worker            → processes Gem Hunter requests
    ├── eagle-worker          → processes Eagle Eye requests
    ├── notification-worker   → sends results back to channels
    └── health-worker         → periodic health aggregation
```

**Mechanism:** All incoming messages (WhatsApp, Telegram, CLI) are written as events to Supabase `agent_events` table. Workers subscribe via Supabase Realtime and process asynchronously. Results are written back and the notification-worker sends responses to the originating channel.

**What it captures:** Complete event history, retry/dead-letter support, async workflows.

**Effort:** ~12h (workers + Supabase functions + notification routing)

**Pros:**
- Fully async — no timeout issues
- Built on existing infra (Supabase agent_events has 72K+ events already)
- Natural audit trail (every event persisted)
- Workers can scale independently
- Supports complex multi-step workflows (chain events)

**Cons:**
- Higher latency (event → process → respond: 2-5s)
- More complex to debug (distributed system)
- Supabase Realtime has limits on free tier

---

### Option C: "Consciousness Loop" (Creative — Claude Opus 4.6 Unlimited)

```
WhatsApp/Telegram/Discord/CLI
         ↓
   [Sensory Cortex]           ← Multi-channel message parser
         ↓
   [Working Memory]           ← Supabase vector store + recent context
         ↓
   [Reasoning Engine]         ← LLM with full system state as context
    │
    ├── [Intent Classification]   → What does the user want?
    ├── [Context Retrieval]       → What do we know? (memory + telemetry)
    ├── [Action Planning]         → What steps are needed?
    ├── [Execution]               → Call APIs, run agents, modify state
    └── [Reflection]              → Did it work? Learn from result.
         ↓
   [Response Synthesis]       ← Format for target channel
         ↓
   [Motor Cortex]             ← Send via WhatsApp/Telegram/Discord
         ↓
   [Dream Cycle] (async)      ← Overnight: consolidate memory,
                                 prune stale data, suggest improvements,
                                 auto-run maintenance tasks
```

**Mechanism:** Inspired by cognitive architecture (Global Workspace Theory). Every message enters a "consciousness loop" that maintains a persistent world model. The system doesn't just route — it UNDERSTANDS context, remembers previous conversations, plans multi-step actions, and learns from outcomes.

**The "Dream Cycle"** runs at 3 AM BRT:
1. Consolidate day's interactions into memory patterns
2. Identify recurring requests → create automation rules
3. Run predictive maintenance (disk cleanup, credential rotation reminders)
4. Generate "morning briefing" for the next day
5. Update the world model with new knowledge

**Mathematical Foundation:**
- Intent classification: Bayesian inference over command taxonomy
- Context retrieval: cosine similarity in embedding space (Supabase pgvector)
- Action planning: MCTS (Monte Carlo Tree Search) over action space — estimate expected value of each possible action chain
- Reflection: Thompson sampling to balance explore/exploit when choosing response strategies
- Dream consolidation: experience replay (like DQN) — replay high-value interactions to strengthen patterns

**What it captures:** Everything. Full cognitive state, intent history, learning patterns, predictive models.

**Effort:** ~40h for MVP (sensory + reasoning + execution + basic dream cycle)

**Pros:**
- The system LEARNS and improves over time
- Natural language interface that truly understands context
- Dream cycle automates maintenance and insight generation
- Can handle ambiguous requests ("fix the thing that broke yesterday")
- Closest to the Tutor Melkin vision

**Cons:**
- Highest complexity and cost (LLM calls for every message)
- Needs careful prompt engineering for reliable intent classification
- Dream cycle needs monitoring to prevent hallucinated maintenance
- Token costs: ~$2-5/day for active usage

---

## Recommendation

**Start with A, evolve to C.**

1. **Week 1:** Build Option A (Gateway API) — 8h. Get unified routing working.
2. **Week 2:** Add WhatsApp webhook to Gateway — messages from Enio trigger API calls.
3. **Week 3:** Layer in Option C's "Reasoning Engine" on top of A's routing. Start with simple intent classification.
4. **Month 2:** Add Dream Cycle. Add vector memory. Add learning loop.

This gives immediate value (unified API access from WhatsApp) while building toward the full cognitive architecture.

---

## WhatsApp Command Interface (Immediate — Week 1)

When Enio sends a message to his own WhatsApp:

| Command | Action | Response |
|---------|--------|----------|
| `status` | Aggregate health of all services | Health report |
| `guard check <text>` | Run Guard Brasil inspection | PII findings |
| `gems` | Latest gem-hunter findings | Top 5 gems |
| `costs` | Today's API costs | Cost breakdown |
| `deploy guard` | Rebuild + restart Guard Brasil container | Deploy status |
| `agents` | List running agents + status | Agent report |
| `task <text>` | Add task to TASKS.md | Confirmation |
| Any other text | NLP → route to best service | Context-dependent |

---

## Technical Implementation (Option A — Gateway)

### Stack
- **Runtime:** Bun + Hono (lightweight, fast)
- **Auth:** API key (shared with Guard Brasil tenants)
- **Proxy:** fetch() to backend services
- **NLP Router:** Claude Haiku (cheapest, fastest for classification)
- **Persistence:** Supabase (agent_events for audit trail)
- **Deployment:** Docker on Hetzner VPS (alongside existing services)
- **Channel Integration:** Evolution API webhook (WhatsApp) + Telegram Bot API

### File Structure
```
apps/egos-gateway/
├── src/
│   ├── server.ts             # Hono server
│   ├── routes/
│   │   ├── guard.ts          # Proxy to Guard Brasil
│   │   ├── gems.ts           # Proxy to Gem Hunter
│   │   ├── eagle.ts          # Proxy to Eagle Eye
│   │   ├── agents.ts         # Trigger agent runner
│   │   ├── health.ts         # Aggregate health
│   │   ├── costs.ts          # Aggregate costs
│   │   └── command.ts        # NLP router
│   ├── channels/
│   │   ├── whatsapp.ts       # Evolution API webhook handler
│   │   ├── telegram.ts       # Telegram Bot API handler
│   │   └── discord.ts        # Discord webhook handler
│   ├── nlp/
│   │   └── intent-classifier.ts  # LLM-based intent routing
│   └── lib/
│       ├── auth.ts           # Unified authentication
│       └── telemetry.ts      # Event logging to Supabase
├── Dockerfile
├── docker-compose.yml
└── package.json
```

### Caddy Config Addition
```caddyfile
api.egos.ia.br {
    reverse_proxy localhost:3000
}
```

---

## Investigation Rules (New Governance Pattern)

Every request that requires investigation MUST follow this protocol:

### Investigation Report Template
```markdown
# Investigation: [TITLE]
## Question
What are we trying to learn?

## Sources Consulted
- [ ] Codebase (grep/graph)
- [ ] Supabase (SQL queries)
- [ ] VPS (SSH verification)
- [ ] External (web search, Exa, GitHub)
- [ ] Memory (previous sessions)

## Findings
### Fact (verified)
### Inference (derived from facts)
### Proposal (recommended action)

## Decision
### Chosen path + rationale
### Alternatives considered + why rejected
### Risks + mitigations

## Dissemination
- [ ] TASKS.md updated
- [ ] HARVEST.md updated (if new pattern)
- [ ] Memory saved (if cross-session relevance)
- [ ] Supabase logged (decisions_log)
- [ ] WhatsApp/Telegram notification (if milestone)
```

### When to use:
- ANY new feature request → Investigation first
- ANY architecture decision → 3 options minimum
- ANY integration → verify state before assuming
- ANY claim from another session → verify files exist

---

## Metrics for Success

| Metric | Target (Week 1) | Target (Month 1) |
|--------|-----------------|-------------------|
| WhatsApp response time | <10s | <3s |
| Services monitored | 4 (Guard, Gem, Eagle, Evolution) | 8+ |
| Daily report delivery | 100% | 100% |
| Command vocabulary | 10 commands | 50+ commands |
| NLP accuracy | 80% | 95% |
| Uptime | 95% | 99.5% |

---

## Open Questions

1. **Domain:** Use `api.egos.ia.br` or `master.egos.ia.br`?
2. **Auth:** Same API keys as Guard Brasil or separate system?
3. **Cost cap:** Max daily LLM spend for NLP routing? (Suggest: $1/day with Haiku)
4. **Dream cycle:** Start with or defer to month 2?

---

*PRD v1.0.0 — Claude Opus 4.6 — 2026-04-04*
*Investigation status: COMPLETE | Ready for implementation*
