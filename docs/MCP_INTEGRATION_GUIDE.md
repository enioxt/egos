# MCP Integration Guide — EGOS Expansion (v2.0.0)

> **Version:** 2.0.0
> **Status:** ACTIVE DEVELOPMENT
> **Last Updated:** 2026-03-26
> **Maintainer:** Autonomous Integration Engineer
> **Sacred Code:** 000.111.369.963.1618

---

## Overview

This guide documents the expansion of MCP (Model Context Protocol) server integration from **5 servers** to **10+ functional servers** within the EGOS kernel. It provides implementation specifications, routing patterns, testing strategies, and operational guidelines.

### Current State (March 2026)
- ✅ Context7 MCP (library docs)
- ✅ GitHub MCP (repo management)
- ✅ Browser Tools MCP (web automation)
- ✅ Shell/File Tools MCP (filesystem operations)
- ✅ Memory MCP (persistent learning)

### Target State (Sprint Completion)
- ✅ Database MCP (Supabase/PostgreSQL)
- ✅ LLM Router MCP (cost tracking + model selection)
- ✅ Git Advanced MCP (blame, merge analytics, governance audit)
- ✅ Filesystem Watch MCP (real-time sync, governance drift detection)
- ✅ Calendar/Schedule MCP (SLA tracking, sprint planning)
- ✅ Sequential Thinking MCP (complex reasoning)
- ✅ EXA Research MCP (web search, semantic ranking)

---

## Architecture

### Layer 1: MCP Server Definitions

Each MCP server is defined in `.guarani/mcp-config.json` with:

```typescript
interface MCPServerConfig {
  id: string;                          // unique identifier
  name: string;                        // display name
  type: MCPServerType;                 // category (database, git, fs, llm, etc.)
  enabled: boolean;                    // activation status
  priority: number;                    // routing priority (1-10)

  // Connection
  transport: 'stdio' | 'http' | 'sse'; // protocol
  command?: string;                    // executable path for stdio
  url?: string;                        // endpoint for http/sse

  // Authentication
  auth?: {
    type: 'env' | 'header' | 'key';
    value: string;                     // e.g., 'env:SUPABASE_KEY'
  };

  // Capabilities
  tools: string[];                     // list of exposed tools
  version: string;                     // server version

  // Governance
  riskLevel: 'T0' | 'T1' | 'T2';      // security tier
  maxConcurrentCalls: number;          // rate limiting
  timeout: number;                     // ms

  // Testing
  healthCheck?: HealthCheckConfig;
  testCases?: TestCase[];
}

type MCPServerType =
  | 'database'   // SQL queries, schema introspection
  | 'git'        // version control operations
  | 'filesystem' // file watching, sync
  | 'llm'        // model orchestration
  | 'calendar'   // scheduling, events
  | 'research'   // web search, knowledge
  | 'thinking'   // complex reasoning
  | 'memory';    // persistent learning
```

### Layer 2: MCP Router Agent

The `mcp-router.ts` agent intelligently routes calls to appropriate servers:

```typescript
interface MCPRoutingRequest {
  query: string;                       // user request
  context?: Record<string, unknown>;   // additional context
  priority?: 'low' | 'normal' | 'high';
  timeout?: number;
  fallbackServers?: string[];          // alternatives if primary fails
}

interface MCPRoutingResponse {
  selectedServer: string;              // chosen MCP server
  tools: ToolCall[];                   // operations to execute
  executionPlan: ExecutionPhase[];     // sequential/parallel phases
  estimatedCost?: number;              // LLM cost estimate
  estimatedTime?: number;              // execution time estimate
}
```

### Layer 3: Configuration Management

The `.guarani/mcp-config.json` file serves as the single source of truth (SSOT) for all MCP configurations, enabling:

- **Centralized updates** — one file to manage all servers
- **Easy enable/disable** — toggle servers without code changes
- **Version tracking** — monitor which versions are deployed
- **Audit trail** — git history of configuration changes
- **Environment safety** — auth credentials sourced from env vars, never hardcoded

---

## MCP Servers Specification

### 1. Database MCP (Supabase/PostgreSQL)

**Purpose:** Query, introspect, and manage database schemas and data.

**Scope:**
- FORJA governance tables (cameras, vision_events, anomalies, baseline_sessions)
- EGOS governance tables (tasks, agents, handoffs, sso_links)
- Real-time subscriptions
- Migration execution

**Config Entry:**
```json
{
  "id": "supabase-db",
  "type": "database",
  "enabled": true,
  "priority": 8,
  "transport": "http",
  "url": "https://${SUPABASE_PROJECT}.supabase.co",
  "auth": {
    "type": "key",
    "value": "env:SUPABASE_ANON_KEY"
  },
  "tools": [
    "query_table",
    "introspect_schema",
    "execute_migration",
    "subscribe_realtime",
    "get_rls_policies"
  ],
  "riskLevel": "T1",
  "maxConcurrentCalls": 5,
  "timeout": 30000
}
```

**Tools:**

| Tool | Signature | Returns |
|------|-----------|---------|
| `query_table` | `(table: string, filter?: object, limit?: number)` | `{rows: [], count: number}` |
| `introspect_schema` | `(table?: string)` | `{tables: [], columns: []}` |
| `execute_migration` | `(sqlPath: string, env?: string)` | `{status: 'success', affected_rows: number}` |
| `subscribe_realtime` | `(table: string, event: 'INSERT'\|'UPDATE'\|'DELETE')` | `{subscription_id: string}` |
| `get_rls_policies` | `(table?: string)` | `{policies: []}` |

**Health Check:**
```typescript
// Validates connection to Supabase
async function healthCheck(): Promise<boolean> {
  const result = await supabase.from('schema_information').select('*').limit(1);
  return result.data !== null;
}
```

---

### 2. LLM Router MCP

**Purpose:** Track costs, select optimal models, manage multi-provider routing.

**Scope:**
- Cost tracking (tokens, USD per model)
- Model performance analytics
- Intelligent model selection based on task complexity
- Fallback routing on quota exceeded
- Budget alerts

**Config Entry:**
```json
{
  "id": "llm-router",
  "type": "llm",
  "enabled": true,
  "priority": 9,
  "transport": "stdio",
  "command": "node services/llm-router-mcp/index.js",
  "auth": {
    "type": "env",
    "value": "env:LLM_ROUTER_SECRET"
  },
  "tools": [
    "estimate_cost",
    "select_model",
    "track_usage",
    "get_cost_summary",
    "check_budget"
  ],
  "riskLevel": "T0",
  "maxConcurrentCalls": 10,
  "timeout": 5000
}
```

**Tools:**

| Tool | Purpose | Returns |
|------|---------|---------|
| `estimate_cost` | Predict token usage and cost for a prompt | `{tokens: number, cost_usd: number, model: string}` |
| `select_model` | Pick best model for task (speed/cost/quality) | `{selected: string, reason: string, alternatives: []}` |
| `track_usage` | Record API call for billing | `{session_id: string, tokens_used: number, cost_usd: number}` |
| `get_cost_summary` | Billing metrics (daily/weekly/monthly) | `{period: string, total_cost: number, by_model: {}}` |
| `check_budget` | Verify usage against quota | `{status: 'ok'\|'warning'\|'exceeded', remaining_usd: number}` |

**Models Configured:**
- Alibaba Qwen-plus (cheapest, good for routing/analysis)
- OpenRouter fallback (Claude, Gemini, Llama options)
- Specialized models (reasoning, retrieval, summarization)

---

### 3. Git Advanced MCP

**Purpose:** Deep git analysis, governance audit, blame tracking.

**Scope:**
- Author analysis and contribution metrics
- Blame attribution for audit trails
- Merge conflict analysis
- Branch ancestry and governance drift detection
- Commit message parsing for governance compliance

**Config Entry:**
```json
{
  "id": "git-advanced",
  "type": "git",
  "enabled": true,
  "priority": 7,
  "transport": "stdio",
  "command": "node services/git-advanced-mcp/index.js",
  "auth": null,
  "tools": [
    "blame_file",
    "analyze_branch",
    "get_merge_history",
    "detect_governance_drift",
    "validate_commit_messages"
  ],
  "riskLevel": "T0",
  "maxConcurrentCalls": 3,
  "timeout": 60000
}
```

**Tools:**

| Tool | Purpose | Use Case |
|------|---------|----------|
| `blame_file` | Get authorship per line | Governance audit, accountability |
| `analyze_branch` | Branch stats (age, commits, contributors) | Worktree validation (EGOS-110) |
| `get_merge_history` | Track merges, conflicts, resolution time | Governance metrics |
| `detect_governance_drift` | Check frozen zones compliance | Pre-commit validation |
| `validate_commit_messages` | Enforce commit format | CI gate compliance |

---

### 4. Filesystem Watch MCP

**Purpose:** Real-time file monitoring, sync detection, governance drift notification.

**Scope:**
- File change detection (CREATE, UPDATE, DELETE)
- Cross-repo sync validation
- Frozen zone violation alerts
- Governance file drift detection
- Symlink resolution

**Config Entry:**
```json
{
  "id": "fs-watch",
  "type": "filesystem",
  "enabled": true,
  "priority": 6,
  "transport": "stdio",
  "command": "node services/fs-watch-mcp/index.js",
  "auth": null,
  "tools": [
    "watch_directory",
    "check_sync_status",
    "validate_frozen_zones",
    "detect_governance_drift",
    "resolve_symlinks"
  ],
  "riskLevel": "T0",
  "maxConcurrentCalls": 2,
  "timeout": 10000,
  "healthCheck": {
    "tool": "watch_directory",
    "args": {"path": "/home/user/egos"}
  }
}
```

**Tools:**

| Tool | Returns | Use Case |
|------|---------|----------|
| `watch_directory` | `{status: 'watching', changes: Event[]}` | Real-time monitoring |
| `check_sync_status` | `{synced: boolean, pending_changes: []}` | Verify cross-repo sync |
| `validate_frozen_zones` | `{valid: boolean, violations: []}` | Pre-commit gate |
| `detect_governance_drift` | `{drift_detected: boolean, files: []}` | Governance integrity check |
| `resolve_symlinks` | `{real_path: string, target: string}` | Safe path resolution |

---

### 5. Calendar/Schedule MCP

**Purpose:** SLA tracking, sprint planning, deadline management.

**Scope:**
- SLA compliance tracking (EGOS-111: 24h per stage)
- Sprint milestones
- Deadline alerts
- Resource scheduling
- Capacity planning

**Config Entry:**
```json
{
  "id": "calendar",
  "type": "calendar",
  "enabled": true,
  "priority": 5,
  "transport": "http",
  "url": "https://calendar.egos.ia.br/api",
  "auth": {
    "type": "key",
    "value": "env:CALENDAR_API_KEY"
  },
  "tools": [
    "get_sla_deadline",
    "track_milestone",
    "set_deadline_alert",
    "get_sprint_plan",
    "check_capacity"
  ],
  "riskLevel": "T0",
  "maxConcurrentCalls": 5,
  "timeout": 15000
}
```

**Tools:**

| Tool | Purpose | Returns |
|------|---------|---------|
| `get_sla_deadline` | Calculate deadline for SLA window | `{deadline: ISO8601, hours_remaining: number}` |
| `track_milestone` | Record sprint/release milestone | `{created: boolean, milestone_id: string}` |
| `set_deadline_alert` | Configure notification before deadline | `{alert_id: string, trigger_time: ISO8601}` |
| `get_sprint_plan` | Retrieve current sprint structure | `{sprint_id: string, start: ISO8601, end: ISO8601, tasks: []}` |
| `check_capacity` | Check team availability for commitment | `{available_capacity: number, blocked_by: []}` |

---

### 6. Sequential Thinking MCP

**Purpose:** Complex multi-step reasoning for orchestration decisions.

**Config Entry:**
```json
{
  "id": "sequential-thinking",
  "type": "thinking",
  "enabled": true,
  "priority": 4,
  "transport": "stdio",
  "command": "@modelcontextprotocol/server-sequential-thinking",
  "tools": [
    "start_thinking",
    "get_thinking_result"
  ],
  "riskLevel": "T0",
  "maxConcurrentCalls": 3,
  "timeout": 120000
}
```

---

### 7. EXA Research MCP

**Purpose:** Real-time web search, research paper discovery, semantic ranking.

**Config Entry:**
```json
{
  "id": "exa-research",
  "type": "research",
  "enabled": true,
  "priority": 3,
  "transport": "http",
  "url": "https://mcp.exa.ai",
  "auth": {
    "type": "key",
    "value": "env:EXA_API_KEY"
  },
  "tools": [
    "search",
    "search_neural",
    "find_similar",
    "get_latest"
  ],
  "riskLevel": "T0",
  "maxConcurrentCalls": 5,
  "timeout": 30000
}
```

---

## MCP Router Implementation

### Overview

The `mcp-router` agent is a meta-orchestrator that:

1. **Analyzes** incoming requests to identify which MCP(s) are relevant
2. **Selects** the optimal server based on priority, capability, and load
3. **Plans** execution (sequential or parallel execution phases)
4. **Routes** calls with fallback strategy
5. **Monitors** execution and reports results

### Routing Algorithm

```
REQUEST
  ↓
[1] PARSE & CLASSIFY
  - Extract intent from query (database? git? file? calendar?)
  - Identify required tools
  ↓
[2] CAPABILITY MATCH
  - Check which servers have required tools
  - Filter by enabled/available status
  ↓
[3] PRIORITY SORT
  - Sort candidates by priority number
  - Consider current load (concurrent calls)
  ↓
[4] EXECUTION PLAN
  - Build sequential or parallel phases
  - Add fallback servers
  ↓
[5] ROUTE & MONITOR
  - Call primary server with timeout
  - On failure, try fallback
  - Return result or error
```

### Configuration Example

```typescript
// In mcp-router.ts
const ROUTING_RULES: RoutingRule[] = [
  {
    intent: /database|query|schema|sql/i,
    primaryServer: "supabase-db",
    fallbackServers: ["memory"],
    timeout: 30000,
  },
  {
    intent: /cost|budget|model.*select/i,
    primaryServer: "llm-router",
    fallbackServers: [],
    timeout: 5000,
  },
  {
    intent: /blame|commit|merge|drift/i,
    primaryServer: "git-advanced",
    fallbackServers: [],
    timeout: 60000,
  },
  {
    intent: /watch|sync|filesystem|monitor/i,
    primaryServer: "fs-watch",
    fallbackServers: [],
    timeout: 10000,
  },
  {
    intent: /sla|deadline|sprint|capacity/i,
    primaryServer: "calendar",
    fallbackServers: [],
    timeout: 15000,
  },
  {
    intent: /search|research|paper|latest/i,
    primaryServer: "exa-research",
    fallbackServers: [],
    timeout: 30000,
  },
];
```

---

## Testing Strategy

### Test Levels

#### Level 1: Connectivity Tests
Each MCP server has a health check that validates:
- Connection to endpoint
- Authentication working
- At least one tool responds

```typescript
// Test file: packages/shared/src/__tests__/mcp-servers.test.ts
describe("MCP Server Health Checks", () => {
  test("Database MCP connects to Supabase", async () => {
    const mcp = new DatabaseMCP(process.env.SUPABASE_ANON_KEY!);
    const health = await mcp.healthCheck();
    expect(health).toBe(true);
  });

  test("LLM Router MCP estimates cost", async () => {
    const mcp = new LLMRouterMCP();
    const estimate = await mcp.estimateCost("What is the capital of France?");
    expect(estimate.cost_usd).toBeGreaterThan(0);
  });
});
```

#### Level 2: Tool Tests
Each tool is tested with real/mock data:

```typescript
describe("Database MCP Tools", () => {
  test("query_table returns rows", async () => {
    const result = await databaseMCP.queryTable("vision_events", {}, 10);
    expect(result.rows).toBeInstanceOf(Array);
    expect(result.count).toBeGreaterThanOrEqual(0);
  });

  test("introspect_schema lists columns", async () => {
    const schema = await databaseMCP.introspectSchema("vision_events");
    expect(schema.columns).toContain("camera_id");
    expect(schema.columns).toContain("event_type");
  });
});
```

#### Level 3: Routing Tests
Test the mcp-router agent:

```typescript
describe("MCP Router", () => {
  test("routes database queries to supabase-db", async () => {
    const response = await mcpRouter.route({
      query: "Get all vision events from the last hour",
      priority: "normal",
    });
    expect(response.selectedServer).toBe("supabase-db");
  });

  test("falls back to memory on database failure", async () => {
    // Simulate database outage
    disableMCP("supabase-db");

    const response = await mcpRouter.route({
      query: "Query vision data",
      fallbackServers: ["memory"],
    });

    expect(response.selectedServer).toBe("memory");
  });

  test("parallelizes independent calls", async () => {
    const response = await mcpRouter.route({
      query: "Get cost estimate and check SLA deadline",
    });

    expect(response.executionPlan.length).toBe(1); // Single phase
    expect(response.executionPlan[0].parallel).toBe(true);
  });
});
```

#### Level 4: Integration Tests
Test full workflows:

```typescript
describe("MCP Integration Workflows", () => {
  test("workflow: check budget before querying database", async () => {
    // 1. Check budget with LLM Router
    const budget = await mcpRouter.route({
      query: "Is budget available for a large query?",
    });

    if (budget.selectedServer !== "llm-router") throw new Error("Wrong server");

    // 2. If OK, query database
    const data = await mcpRouter.route({
      query: "Get all vision anomalies",
    });

    expect(data.selectedServer).toBe("supabase-db");
  });

  test("workflow: detect governance drift with git + fs-watch", async () => {
    const drift = await mcpRouter.route({
      query: "Check if frozen zones were modified",
    });

    // Should use git-advanced + fs-watch
    expect([drift.selectedServer]).toContain(
      expect.stringMatching(/git-advanced|fs-watch/)
    );
  });
});
```

### Test Data

Create seed data for testing:

```sql
-- tests/seed-data.sql
INSERT INTO vision_events (camera_id, event_type, created_at)
VALUES
  ('cam-1', 'person_detected', NOW()),
  ('cam-1', 'vehicle_detected', NOW() - INTERVAL '30 minutes'),
  ('cam-2', 'motion_detected', NOW() - INTERVAL '1 hour');

INSERT INTO tasks (id, title, priority, status, created_at)
VALUES
  ('EGOS-001', 'Test task 1', 'HIGH', 'open', NOW()),
  ('EGOS-002', 'Test task 2', 'MEDIUM', 'closed', NOW());
```

---

## Operational Guidelines

### Enable/Disable MCP

```bash
# Disable database MCP (e.g., for maintenance)
cat .guarani/mcp-config.json | jq '.servers[] | select(.id == "supabase-db") | .enabled = false' > /tmp/config.json
mv /tmp/config.json .guarani/mcp-config.json

# Verify
bun run mcp:status
```

### Monitor MCP Health

```bash
# Health check all servers
bun run mcp:health-check

# Get performance metrics
bun run mcp:metrics
```

### Update MCP Configuration

```bash
# Add new MCP server
bun run mcp:add --id=newserver --type=database --command="..."

# Update server auth
bun run mcp:update --id=supabase-db --auth="env:NEW_KEY"

# Validate config schema
bun run mcp:validate
```

### Troubleshooting

#### "MCP not responding" Error

1. Check `.guarani/mcp-config.json` — is it enabled?
2. Verify environment variables are set
3. Check network connectivity (for HTTP MCPs)
4. Review MCP server logs (if available)
5. Try fallback server

```bash
# Enable debug logging
DEBUG=egos:mcp:* bun agents/agents/mcp-router.ts
```

---

## Mycelium Integration

MCP routers can emit **mycelium triggers** to invoke follow-up tools:

```typescript
// In mcp-router.ts
if (routeResponse.error) {
  mycelium_triggers.push({
    tool: "search_telemetry_logs",
    args: { mcp_id: routeResponse.selectedServer },
  });
}

if (routeResponse.estimatedCost > BUDGET_THRESHOLD) {
  mycelium_triggers.push({
    tool: "validate_budget",
    args: { cost_estimate: routeResponse.estimatedCost },
  });
}
```

---

## Performance Targets

| Metric | Target |
|--------|--------|
| MCP health check latency | < 500ms |
| Routing decision latency | < 200ms |
| Database query latency | < 2s |
| LLM cost estimate latency | < 200ms |
| Git analysis latency | < 5s |
| Fallback failover time | < 1s |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0.0 | 2026-03-26 | Initial expansion spec (5 → 10+ MCPs) |
| 1.0.0 | 2026-03-25 | Original integration map |

---

## References

- `.guarani/mcp-config.json` — Configuration source
- `agents/agents/mcp-router.ts` — Router implementation
- `packages/shared/src/__tests__/` — Test suite
- `docs/MCP_INTEGRATION_MAP.md` — Original integration overview
- [MCP Specification](https://modelcontextprotocol.io/) — Official docs

---

*Maintained by: EGOS Integration Team | Sacred Code: 000.111.369.963.1618*
