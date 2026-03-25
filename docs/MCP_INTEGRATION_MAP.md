# MCP Integration Map — EGOS Ecosystem

> **Version:** 1.0.0 | **Updated:** 2026-03-25
> **Purpose:** Canonical map of all MCP servers — active, planned, and proposed

---

## 1. Currently Active MCPs

| Server | Scope | Config | Purpose |
|--------|-------|--------|---------|
| `filesystem` | Global | `~/.claude.json` | Direct access to 9 repos (egos, egos-lab, 852, carteira-livre, br-acc, forja, policia, santiago, /tmp) |
| `memory` | Global | `~/.claude.json` | Persistent knowledge graph at `egos-lab/memory_db/memory.jsonl` |
| `sequential-thinking` | Global | `~/.claude.json` | Multi-step reasoning for complex tasks |
| `exa` | Global | `~/.claude.json` | Web search with semantic ranking |
| `context7` | egos + forja | `~/.claude.json` (project) | Up-to-date library docs (Next.js 15, Tailwind v4, React 19, Supabase) |

### Claude.ai Connected MCPs

| Server | Status | Accessible Projects |
|--------|--------|-------------------|
| `claude.ai Supabase` | ✅ Connected | egos-lab, CARTEIRA-LIVRE |
| `claude.ai Vercel` | ✅ Connected | All projects |
| `claude.ai Notion` | ✅ Connected | All |
| `claude.ai Gmail` | ✅ Connected | All |

> **Note:** FORJA Supabase project (`zqcdkbnwkyitfshjkhqg`) is under a separate org — not accessible via claude.ai MCP connector. Apply migrations via `psql` or Supabase CLI with updated `.env` credentials.

---

## 2. Context7 — How to Use

Context7 gives **real-time, version-accurate docs** for 1000+ libraries. Just add `use context7` to your prompt:

```
"How do I configure Tailwind v4 dark mode with CSS variables? use context7"
"Next.js 15 route handlers with streaming? use context7"
"Supabase realtime subscriptions React hook? use context7"
```

**Highest value for FORJA Visão:**
- Tailwind v4 (very new — training data may be stale)
- Next.js 15/16 app router patterns
- Supabase Realtime for live camera events
- React 19 hooks (useOptimistic, use())

---

## 3. egos-core MCP — What It Should Be

> **Current status:** DOES NOT EXIST YET — planned as EGOS-087/088 in TASKS.md backlog

`egos-core` would be a **custom MCP server** that exposes EGOS kernel capabilities as tools for any AI agent:

### Proposed Tool Surface

```typescript
// @egos/mcp-governance — EGOS-087
tools:
  - check_ssot_drift(repo?)          // detect TASKS.md/AGENTS.md drift
  - list_tasks(repo, priority?)      // query TASKS.md across all repos
  - sync_governance(repos[])         // run sync-all-leaf-repos.sh --exec
  - validate_capability(claim)       // ATRiAN/PII compliance check
  - get_repo_role(repo)              // return egos.config.json role

// @egos/mcp-memory — EGOS-088
tools:
  - store_pattern(title, content, tags[])
  - recall_patterns(query, limit?)
  - search_memory(query)             // semantic search in memory.jsonl
  - list_recent_sessions(days?)

// @egos/mcp-erp (FORJA-specific) — EGOS-090
tools:
  - get_production_status(order_id?)
  - get_camera_events(camera_id, since?)
  - get_anomalies(severity?, status?)
  - get_baseline_stats(family_id?)
  - get_stock_level(product_id?)
```

### Implementation Path

```
Phase 1 (1 day): @egos/mcp-governance
  → Node.js + stdio transport
  → Reads TASKS.md, AGENTS.md, egos.config.json
  → Runs governance scripts via child_process
  → Register in ~/.claude.json as global MCP

Phase 2 (2 days): @egos/mcp-memory
  → Wraps existing memory.jsonl with semantic search
  → Uses existing @egos/shared memory module
  → Enables cross-session pattern recall

Phase 3 (3 days): @egos/mcp-erp
  → Connects to FORJA Supabase (vision tables)
  → Real-time anomaly subscription
  → Chat-callable from FORJA AI chat interface
```

---

## 4. MCP Integration Plan for FORJA Visão

### Sprint 2 — Database (use Supabase MCP for egos-lab, psql for FORJA)

```sql
-- Apply 20260325_visao_module.sql
-- Tables: cameras, vision_presets, vision_zones, baseline_sessions,
--         vision_events, stage_transitions, vision_anomalies, generated_insights
```

Manually apply via updated DB credentials:
```bash
psql "$SUPABASE_DB_URL" -f supabase/migrations/20260325_visao_module.sql
```

### Sprint 3 — Frigate + MQTT Bridge

```yaml
# docker-compose.yml additions
frigate:
  image: ghcr.io/blakeblackshear/frigate:stable
  volumes:
    - ./config/frigate.yml:/config/config.yml
  ports: ["5000:5000", "1935:1935"]

mqtt-bridge:
  build: ./services/mqtt-bridge
  env:
    - MQTT_BROKER=mqtt://localhost:1883
    - SUPABASE_URL=$SUPABASE_URL
    - SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY
```

The MQTT bridge transforms Frigate events → `vision_events` Supabase rows:
```typescript
// services/mqtt-bridge/index.ts
mqtt.on('frigate/+/+', (topic, payload) => {
  const [, cameraId, eventType] = topic.split('/');
  supabase.from('vision_events').insert({
    camera_id: cameraId,
    event_type: mapFrigateEvent(eventType),
    ...parsePayload(payload)
  });
});
```

### Sprint 4 — Real-time Frontend

Replace mock data with Supabase Realtime subscriptions:

```typescript
// _hooks/useVisionEvents.ts
const channel = supabase
  .channel('vision-events')
  .on('postgres_changes', {
    event: 'INSERT',
    schema: 'public',
    table: 'vision_events',
    filter: `tenant_id=eq.${tenantId}`
  }, (payload) => setEvents(prev => [payload.new, ...prev.slice(0, 49)]))
  .subscribe();
```

---

## 5. Next MCP Candidates (Recommended)

| MCP | Package | Value for EGOS/FORJA | Effort |
|-----|---------|----------------------|--------|
| **Playwright** | `@playwright/mcp` | E2E testing FORJA UI | Low |
| **GitHub** | `@modelcontextprotocol/server-github` | PR management, issue tracking | Low |
| **Redis** | `mcp-redis` | Query Mycelium event bus on VPS | Medium |
| **MQTT** | `mcp-mqtt` | Direct query of Frigate events | Medium |
| **@egos/mcp-governance** | (build) | SSOT drift, task queries | High value |
| **Frigate** | (build) | Camera stream + event query | High value |

### Install GitHub MCP (immediate value):

```bash
claude mcp add github -- npx -y @modelcontextprotocol/server-github
# requires GITHUB_PERSONAL_ACCESS_TOKEN in env
```

---

## 6. Memory MCP — Using It Now

The `memory` MCP is already active. Use it to store FORJA patterns:

```
mcp__memory__create_entities — store FORJA Visão architecture
mcp__memory__add_observations — add learnings to existing entities
mcp__memory__search_nodes — recall patterns in future sessions
```

Key entities to create:
- `FORJA_VISAO_ARCH` — camera stack decisions
- `FORJA_SUPABASE` — project ID, table names, RLS patterns
- `EGOS_VPS` — agent map, Docker services, PM2 processes

---

*Maintained by: EGOS Kernel | Source: `docs/MCP_INTEGRATION_MAP.md`*
