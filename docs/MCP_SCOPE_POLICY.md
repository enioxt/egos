# MCP Scope Policy — EGOS-004

**Date:** 2026-03-28
**Status:** Active / MANDATORY
**Purpose:** Define minimal, necessary scopes for each MCP server integration to prevent privilege escalation

---

## Overview

All MCP servers operating within EGOS must declare their required scopes explicitly. This policy enforces **principle of least privilege**: each server gets only the scopes it needs, nothing more.

### Scope Format

Scopes follow the pattern: `{category}:{operation}:{resource?}`

Examples:
- `database:read:tables` — Read access to table metadata
- `database:query:tasks` — Query the tasks table
- `github:read:public` — Read public repository information
- `github:write:own-repo` — Write to user's own repositories only
- `api:chat` — Call chat completion endpoints

---

## Scopes By MCP Server

### 1. Supabase Database MCP (`supabase-db`)

**Risk Level:** T1 (Medium)
**Transport:** HTTP with Bearer token

**Required Scopes:**
- `database:read:schema` — Introspect table structures
- `database:query:{table}` — Query specific tables (filtered by allowlist)
- `database:subscribe:realtime` — Subscribe to real-time change events
- `database:read:rls` — Read RLS policy definitions (for audit)

**Forbidden Scopes:**
- ~~`database:write:*`~~ — No arbitrary writes
- ~~`database:execute:migration`~~ — Migrations only via `supabase db push`
- ~~`database:delete:*`~~ — No delete operations
- ~~`database:drop:*`~~ — No schema drops

**Implementation:**
```typescript
{
  "id": "supabase-db",
  "scopes": [
    "database:read:schema",
    "database:query:vision_events",
    "database:query:vision_anomalies",
    "database:query:cameras",
    "database:query:tasks",
    "database:subscribe:realtime",
    "database:read:rls"
  ],
  "allowedTables": [
    "vision_events", "vision_anomalies", "baseline_sessions",
    "cameras", "tasks", "agents", "handoffs", "sso_links"
  ]
}
```

**Rationale:**
- Database is sensitive (contains all system data)
- Limit to read + query operations for safety
- RLS policies must be readable to understand data isolation
- Real-time subscriptions needed for reactive features
- Migration execution never delegated to MCP (controlled in CI)

---

### 2. LLM Router MCP (`llm-router`)

**Risk Level:** T0 (Low)
**Transport:** Stdio (local)

**Required Scopes:**
- `api:chat` — Call chat completion endpoints
- `api:embed` — Call embedding endpoints
- `billing:track` — Record usage for billing

**Forbidden Scopes:**
- ~~`api:fine-tune`~~ — No model fine-tuning
- ~~`api:admin`~~ — No API account changes
- ~~`billing:configure`~~ — No billing config changes

**Implementation:**
```typescript
{
  "id": "llm-router",
  "scopes": [
    "api:chat",
    "api:embed",
    "billing:track"
  ],
  "allowedModels": [
    "alibaba/qwen-plus",
    "anthropic/claude-opus",
    "meta-llama/llama-2-70b"
  ]
}
```

**Rationale:**
- LLM calls are the core capability
- Embedding support needed for search
- Tracking usage is essential for cost management
- Fine-tuning disabled (too risky, not needed)
- Model list is hardcoded (no dynamic calls)

---

### 3. Git Advanced MCP (`git-advanced`)

**Risk Level:** T0 (Low)
**Transport:** Stdio (local)

**Required Scopes:**
- `git:read:blame` — Read line attribution
- `git:read:history` — Read commit history
- `git:read:governance` — Read .guarani/* and frozen-zones
- `git:validate:messages` — Validate commit message compliance

**Forbidden Scopes:**
- ~~`git:write:*`~~ — No commits from MCP
- ~~`git:force:*`~~ — No force pushes
- ~~`git:admin:*`~~ — No repository admin changes

**Implementation:**
```typescript
{
  "id": "git-advanced",
  "scopes": [
    "git:read:blame",
    "git:read:history",
    "git:read:governance",
    "git:validate:messages"
  ],
  "auditFiles": [
    "frozen-zones.md",
    "AGENTS.md",
    ".guarani/orchestration/*"
  ]
}
```

**Rationale:**
- Git analysis is read-only (no mutations)
- Blame tracking for governance attribution
- Governance file audit is critical
- Commit message validation enforces discipline

---

### 4. Filesystem Watch MCP (`fs-watch`)

**Risk Level:** T0 (Low)
**Transport:** Stdio (local)

**Required Scopes:**
- `fs:watch:directory` — Monitor directory for changes
- `fs:read:governance` — Read governance files
- `fs:validate:frozen` — Validate frozen zones

**Forbidden Scopes:**
- ~~`fs:write:*`~~ — No file writes
- ~~`fs:delete:*`~~ — No file deletes
- ~~`fs:execute:*`~~ — No command execution

**Implementation:**
```typescript
{
  "id": "fs-watch",
  "scopes": [
    "fs:watch:directory",
    "fs:read:governance",
    "fs:validate:frozen"
  ],
  "watchedPaths": [
    ".guarani/*",
    "frozen-zones.md",
    "docs/"
  ]
}
```

**Rationale:**
- Filesystem watching is defensive (detect unauthorized changes)
- Read-only access to governance files
- No write or execute capabilities

---

### 5. Calendar & Schedule MCP (`calendar`)

**Risk Level:** T0 (Low)
**Transport:** HTTP

**Required Scopes:**
- `schedule:read:sla` — Read SLA definitions
- `schedule:read:sprint` — Read sprint information
- `schedule:write:milestone` — Create milestones (tracking only)
- `schedule:read:capacity` — Query team availability

**Forbidden Scopes:**
- ~~`schedule:admin:*`~~ — No sprint configuration
- ~~`schedule:delete:*`~~ — No deletion
- ~~`identity:manage`~~ — No user/team management

**Implementation:**
```typescript
{
  "id": "calendar",
  "scopes": [
    "schedule:read:sla",
    "schedule:read:sprint",
    "schedule:write:milestone",
    "schedule:read:capacity"
  ]
}
```

**Rationale:**
- Schedule operations are non-destructive
- SLA checks are important for planning
- Milestone tracking for audit trail
- No administrative changes allowed

---

### 6. Sequential Thinking MCP (`sequential-thinking`)

**Risk Level:** T0 (Low)
**Transport:** Stdio (local)

**Required Scopes:**
- `reasoning:execute` — Run extended thinking sessions

**Forbidden Scopes:**
- None (reasoning-only tool, no resource access)

**Implementation:**
```typescript
{
  "id": "sequential-thinking",
  "scopes": ["reasoning:execute"]
}
```

**Rationale:**
- Pure computation, no external access
- Safe to run unrestricted

---

### 7. EXA Research MCP (`exa-research`)

**Risk Level:** T0 (Low)
**Transport:** HTTP

**Required Scopes:**
- `search:web` — Search public web
- `search:research` — Search research papers
- `search:news` — Search news articles
- `search:similar` — Find similar documents

**Forbidden Scopes:**
- ~~`search:private`~~ — No access to user data
- ~~`search:admin`~~ — No search configuration

**Implementation:**
```typescript
{
  "id": "exa-research",
  "scopes": [
    "search:web",
    "search:research",
    "search:news",
    "search:similar"
  ]
}
```

**Rationale:**
- Public search operations only
- No private data exposure
- Limited to published information

---

### 8. Memory MCP (`memory`)

**Risk Level:** T0 (Low)
**Transport:** Stdio (local)

**Required Scopes:**
- `knowledge:create:entity` — Create knowledge graph entities
- `knowledge:add:observation` — Add observations to entities
- `knowledge:read:entities` — Query knowledge graph
- `knowledge:read:sessions` — List conversation sessions

**Forbidden Scopes:**
- ~~`knowledge:delete:*`~~ — No deletion (append-only)
- ~~`knowledge:admin:*`~~ — No configuration changes

**Implementation:**
```typescript
{
  "id": "memory",
  "scopes": [
    "knowledge:create:entity",
    "knowledge:add:observation",
    "knowledge:read:entities",
    "knowledge:read:sessions"
  ]
}
```

**Rationale:**
- Knowledge graph is append-only (immutable history)
- No deletions (audit trail preservation)
- Entities and observations tracked for compliance

---

## MCP Server Configuration Template

Each MCP server MUST declare scopes in `.guarani/mcp-config.json`:

```json
{
  "id": "example-mcp",
  "name": "Example MCP",
  "scopes": [
    "category:operation:resource"
  ],
  "auth": {
    "type": "env",
    "envVar": "EXAMPLE_API_KEY",
    "required": true
  },
  "governance": {
    "allowedResources": ["..."],
    "forbiddenResources": ["..."]
  }
}
```

---

## Scope Validation at Runtime

When an MCP server attempts to access a resource, the system MUST:

1. **Check declared scopes:** Does the server have the required scope?
2. **Validate resource:** Is the resource in the allowlist?
3. **Log access:** Emit audit event with identity + scope
4. **Enforce:** Deny if scope missing or resource forbidden

**Example Audit Log:**
```json
{
  "timestamp": "2026-03-28T15:30:00Z",
  "mcp_server": "supabase-db",
  "identity": {
    "userId": "mcp-supabase-db",
    "source": "mcp",
    "scopes": ["database:query:tasks"]
  },
  "action": "query",
  "resource": "tasks",
  "result": "allowed",
  "reasoning": "Scope database:query:tasks matches requested resource"
}
```

---

## Scope Review & Rotation

- **Quarterly Review:** Audit all MCP scopes for necessity (EGOS-004)
- **Incident Response:** On breach, revoke scopes immediately
- **Token Rotation:** API keys rotated every 90 days (stored in env vars via CI/CD)
- **Access Logs:** Retained for 1 year for compliance

---

## References

- **EGOS-004:** MCP Security Hardening
- **EGOS-002:** Universal Activation Layer (Identity & Permission)
- **Frozen Zones:** `/egos/frozen-zones.md`
- **MCP Config:** `/egos/.guarani/mcp-config.json`

---

**Last Updated:** 2026-03-28
**Owner:** Enio (EGOS Governance)
**Next Review:** 2026-06-28
