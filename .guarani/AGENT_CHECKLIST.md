# AGENT CREATION CHECKLIST v1.0

> **STATUS:** Mandatory governance for all new agents
> **Version:** 1.0.0 | **Updated:** 2026-03-27
> **Audit Reference:** See `docs/AGENT_AUDIT_2026-03-27.md`

---

## What is a "Real Agent"? (DEFINITION)

An agent is ONLY valid if **ALL** of these are true:

1. **Has a TypeScript implementation:** `agents/agents/<name>.ts` or approved subrepo
2. **Registered in agents.json:** Exactly one entry with matching id + entrypoint
3. **Implements Agent interface:** Must export `run(options)` function
4. **Has metadata:** Must export const `metadata = { id, version, ... }`
5. **Supports --dry mode:** Must handle `--dry_run` before `--execute`
6. **NOT a script utility:** No `scripts/` location + spawn/fs/util imports
7. **NOT documentation:** No .md, .json, .yaml entrypoints
8. **Passes validation:** `bun agent:lint` returns 0

---

## Pre-Registration Checklist (BEFORE adding to agents.json)

- [ ] **File exists:** Agent implementation at declared entrypoint
- [ ] **Interface compliance:** Has `run(options)` and `metadata` exports
- [ ] **Dry-run support:** Logic branches on `options.dry` parameter
- [ ] **Documented:** `metadata.description` is clear + `@param` jsdoc
- [ ] **No external deps:** Only Node/Bun stdlib (shared packages OK)
- [ ] **TypeScript valid:** `bun typecheck` passes
- [ ] **Registry entry:** Has id, entrypoint, status, risk_level, area
- [ ] **Lint passes:** `bun agent:lint` returns 0

---

## Valid Agent Structure (EXAMPLE)

```typescript
// agents/agents/my-agent.ts

import { analyzeCode } from "../runtime/runner";

// 🔴 NEVER DO THIS:
// import { spawn } from "child_process"  ← scripts use this
// import fs from "fs/promises"           ← scripts use this

// ✅ DO THIS:
export async function run(options: { dry?: boolean } = {}) {
  if (options.dry) {
    console.log("[DRY] Would analyze repository");
    return { status: "dry", findings: 0 };
  }

  // Agent logic here
  const result = await analyzeCode(process.cwd());
  return result;
}

export const metadata = {
  id: "my_agent",
  version: "1.0.0",
  status: "active", // or "dormant"
  description: "Short, clear description of what this agent does"
};
```

---

## Valid agents.json Entry (EXAMPLE)

```json
{
  "id": "my_agent",
  "name": "My Agent",
  "description": "Clear description matching metadata.description",
  "area": "qa", // or: architecture, knowledge, observability, security
  "entrypoint": "agents/agents/my-agent.ts",
  "status": "active",
  "risk_level": "T0", // T0 (safe) to T3 (critical)
  "run_modes": ["dry_run", "execute"],
  "triggers": ["manual"],
  "tools_allowed": [],
  "migrated_from": "optional"
}
```

---

## INVALID Patterns (RED FLAGS)

| Pattern | Problem | Fix |
|---------|---------|-----|
| `"entrypoint": "scripts/something.ts"` | Script utility, not agent | Move to `tools[]` array |
| `"entrypoint": "docs/something.md"` | Documentation, not code | Remove from registry |
| No `agents/agents/<name>.ts` file | Missing implementation | Create file first |
| Only `spawn()` + `readFile()` calls | Pure utility script | Don't register as agent |
| No `run()` function | Wrong interface | Export `run(options)` |
| No `--dry` branch | Can't test safely | Add `if (options.dry)` check |
| `"status": "active"` but file missing | Ghost agent | Remove or implement |
| Multiple agents pointing to same file | Duplicate registration | One agent per file |

---

## Governance Rules Reinforced

### Rule #1: REGISTRY IS SSOT

If it's in agents.json, it MUST work or be marked "dormant"

### Rule #2: ONE THING PER FILE

Each agent id matches exactly one file basename

### Rule #3: NO SCRIPTS IN agents[]

Scripts go in `tools[]` array, not `agents[]`

### Rule #4: DORMANT ≠ MISSING

Dormant agents need stubs + clear unblock conditions

---

**Last Updated:** 2026-03-27