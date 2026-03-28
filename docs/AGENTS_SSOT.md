# Agents SSOT — Single Source of Truth

**Purpose:** Master registry ensuring all dashboards, frontends, and monitoring systems reference the same agent definitions.

**Last updated:** 2026-03-28

---

## Canonical Source
- **File:** `/home/enio/egos/agents/registry/agents.json`
- **Format:** JSON array of agent definitions
- **Authority:** Kernel EGOS — all leaf repos derive from this

---

## SSOT Mirrors (Must Stay In Sync)

### 1. **egos-lab AgentsDashboard**
- **File:** `/home/enio/egos-lab/apps/egos-web/src/data/agents-registry.ts`
- **Type:** TypeScript export (mirrors agents.json)
- **Update trigger:** When agents.json changes
- **Status:** ✅ Synced (comment says "mirrors agents/registry/agents.json")
- **Sync method:** Manual (TODO: automate via CI)

### 2. **852 Admin Dashboard**
- **File:** `/home/enio/852/src/pages/admin/agents.tsx` (if exists)
- **Type:** React component with inline agent list
- **Update trigger:** Inherited from bracc API
- **Status:** ⚠️ Unknown (needs verification)
- **Sync method:** Via API `/api/agents` endpoint

### 3. **bracc API**
- **File:** `/home/enio/bracc/api/routes/agents.ts` (if exists)
- **Type:** REST endpoint returning agent list
- **Source:** Should query Neo4j graph or agent registry
- **Status:** ⚠️ Unknown (needs verification)
- **Sync method:** Real-time from Neo4j or cached from agents.json

### 4. **Telegram Bot**
- **File:** `@egos_bot` command handlers
- **Type:** Commands referencing agents
- **Source:** Should consume `/api/agents` or agents.json
- **Status:** ⚠️ Unknown (needs verification)
- **Sync method:** Runtime configuration or startup load

---

## Agent Definition Schema

### Required Fields
```typescript
interface Agent {
  id: string              // kebab-case: "dep-auditor"
  name: string           // human: "Dependency Auditor"
  area: string           // category: "security", "knowledge", "qa", "design", "observability"
  description: string    // brief purpose
  owner: string          // "enioxt" or GitHub handle
  risk_level: string     // "T0" (kernel), "T1" (supported), "T2" (experimental)
  entrypoint: string     // file path to agent code
  tools_allowed: string[] // ["filesystem:read", "git:read", ...]
  triggers: string[]     // ["pre-commit", "manual", "weekly"]
  run_modes: string[]    // ["dry_run", "execute"]
  status: string         // "active" | "pending" | "dormant"
  category: string       // "core" | "support" | "experimental" | "dormant"
  tags: string[]         // ["security", "git", "pre-commit", ...]
}
```

### Example
```json
{
  "id": "dep-auditor",
  "name": "Dependency Auditor",
  "area": "security",
  "description": "Audits dependencies for CVEs, version conflicts, and outdated packages",
  "owner": "enioxt",
  "risk_level": "T0",
  "entrypoint": "agents/agents/dep-auditor.ts",
  "tools_allowed": ["filesystem:read", "git:read"],
  "triggers": ["manual", "weekly"],
  "run_modes": ["dry_run", "execute"],
  "status": "active",
  "category": "core",
  "tags": ["security", "dependencies", "audit", "cve"]
}
```

---

## Sync Validation

### Check for Drift
```bash
# Compare egos-lab mirror against kernel
diff \
  <(jq '.[] | {id, name, status}' /home/enio/egos/agents/registry/agents.json) \
  <(grep -o 'id: [^ ]*' /home/enio/egos-lab/apps/egos-web/src/data/agents-registry.ts | cut -d' ' -f2 | sort)
```

### SSOT Audit Rules
1. ✅ `agents.json` is source of truth
2. ✅ `agents-registry.ts` must be manually synced when agents added/removed
3. ⚠️ `bracc API` must expose agents.json or Neo4j equivalent
4. ⚠️ `852 dashboard` must consume bracc API, not inline list
5. ⚠️ `Telegram bot` must use API endpoint, not hardcoded list

### Drift Detection
If you find an agent in one place but not another, **mark this file as drift signal** and update all locations.

---

## Current Gaps (Action Items)

| Component | Status | Gap | Fix |
|-----------|--------|-----|-----|
| agents.json | ✅ SSOT | — | Master source |
| egos-lab mirror | ✅ Synced | Manual sync | Automate via CI |
| bracc API | ⚠️ Unknown | May be hardcoded | Query agents.json or Neo4j |
| 852 dashboard | ⚠️ Unknown | May be hardcoded | Consume bracc API |
| Telegram bot | ⚠️ Unknown | May be hardcoded | Consume API endpoint |

---

## Implementation Checklist

### Phase 1: Establish SSOT Authority
- [ ] Verify agents.json contains all agents (6 kernel + others)
- [ ] Create TypeScript types matching schema above
- [ ] Document agent lifecycle (add → test → register → deploy)

### Phase 2: Sync Mirrors
- [ ] Auto-generate agents-registry.ts from agents.json during build
- [ ] Verify bracc API endpoint `/api/agents`
- [ ] Verify 852 dashboard consumes bracc API

### Phase 3: Monitor Drift
- [ ] Create SSOT auditor task in CI/CD
- [ ] Flag any new agents added outside agents.json
- [ ] Monthly drift audit report

---

## File Dependencies
```
agents.json (SOURCE)
  ├→ agents-registry.ts (mirror via CI)
  ├→ bracc/api/agents (endpoint)
  ├→ 852/dashboard (consumes endpoint)
  └→ @egos_bot/commands (uses endpoint)
```

---

## Notes
- **Why SSOT matters:** One source means one place to add/remove agents, reducing risk of inconsistency
- **Automation:** CI should generate `agents-registry.ts` from `agents.json` on every push
- **Verification:** SSOT Auditor agent should run weekly and flag drift
