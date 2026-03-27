# AGENT_GOVERNANCE_RULES.md — EGOS Agent Qualification Standard

> **VERSION:** 1.0.0 | **CREATED:** 2026-03-27 | **TYPE:** Mandatory governance document
> **PURPOSE:** Define objective criteria for what qualifies as an "EGOS Agent" vs scaffolding/ghost/placeholder

---

## Core Principle

> **An EGOS Agent is a real, executable, governable entity — not documentation, not pseudocode, not ghost registry entries.**

---

## Rule 1: Agent MUST Have Implementation

**Requirement:**
- Entrypoint MUST point to an existing, readable `.ts` file
- File MUST be valid TypeScript (passes `tsc --noEmit`)
- File MUST export a default `AgentConfig` object or function
- File size MUST be ≥ 50 lines (not a stub)

**Validation:**
```bash
# Pre-commit hook
bun agent:lint --strict
# Must pass with 0 errors
```

**Exception:** None. If no file, it's not an agent.

---

## Rule 2: Standardized Entrypoint Location

**Requirement:**
- ALL agents MUST live in `agents/agents/*.ts` (kernel) or equivalent in leaf repos
- NO entrypoints in `scripts/`, `docs/`, `bin/`, or external subrepos
- NO entrypoints that are markdown, docs, or non-executable files

**Valid:**
```
agents/agents/orchestrator.ts          ✅
agents/agents/security-scanner.ts      ✅
```

**Invalid:**
```
scripts/security_scan.ts               ❌ (not in agents/)
docs/protocols/rho-calibration.md      ❌ (markdown)
egos-autoresearch/autoresearch.ts      ❌ (external subrepo)
```

**Validation:**
```bash
# In pre-commit
find agents/registry/agents.json -exec jq '.agents[] | .entrypoint' {} \; | \
  grep -v '^"agents/agents/' && echo "FAIL: Invalid entrypoint location" && exit 1
```

---

## Rule 3: Agent MUST Support --dry Mode

**Requirement:**
- `--dry` flag MUST be supported by runner
- In `--dry` mode:
  - No files modified
  - No API calls made
  - No state changed
  - Output MUST be "report" only (JSON or markdown)
- `--exec` MUST be idempotent (safe to retry)

**Validation:**
```bash
bun agent:run <id> --dry
# Must complete without errors or side effects
```

---

## Rule 4: Agent MUST Have Registry Entry

**Requirement:**
- Entry in `agents/registry/agents.json` (kernel) or equivalent in leaf repo
- Schema MUST be valid per `agents/registry/schema.json`
- Required fields: `id`, `name`, `description`, `status`, `entrypoint`, `risk_level`, `run_modes`

**Example:**
```json
{
  "id": "orchestrator",
  "name": "Agent Orchestrator",
  "description": "Runs ALL registered agents sequentially, collects findings",
  "area": "orchestration",
  "entrypoint": "agents/agents/orchestrator.ts",
  "run_modes": ["dry_run", "execute"],
  "triggers": ["manual"],
  "risk_level": "T3",
  "status": "active"
}
```

---

## Rule 5: Status Field is Legal and Meaningful

**Requirement:**
- Only 3 valid status values:

| Status | Meaning | File Required? | TODO Required? | Can Be Scheduled? |
|--------|---------|----------------|---|---|
| `active` | Fully functional, ready for automation | ✅ YES | ❌ NO | ✅ YES |
| `dormant` | Intentional placeholder, blocked on dependency | ✅ YES | ✅ YES | ❌ NO |
| `broken` | Was active, now has broken dependencies | ✅ YES | ✅ YES | ❌ NO |

**Validation:**
```bash
# Pre-commit must reject invalid status values
jq '.agents[].status' agents/registry/agents.json | \
  grep -v '^"active"\|^"dormant"\|^"broken"' && \
  echo "FAIL: Invalid status" && exit 1
```

---

## Rule 6: Dormant MUST Have Minimal Implementation

**Requirement:**
- Even dormant agents MUST have a `.ts` file (≥ 50 lines)
- File MUST contain explicit TODO comment explaining blocker
- Example blocker comment:
  ```typescript
  // TODO: Blocked on Playwright MCP implementation (see TASKS.md#EGOS-104)
  // Expected completion: 2026-Q2
  // Contact: enioxt
  ```

**Invalid Dormant:**
```typescript
// Missing file entirely
// OR
export const e2e_smoke = {
  id: "e2e_smoke"
  // No TODO — why is this dormant?
};
```

---

## Rule 7: No Scripts in Registry

**Requirement:**
- If entrypoint is in `scripts/` directory, it's a **utility**, not an agent
- Utilities MUST be registered in a separate `utilities.json`, not `agents.json`
- Agents are governed, orchestrated, and auditable. Utilities are not.

**Example Violation:**
```json
{
  "id": "code_reviewer",
  "entrypoint": "scripts/review.ts"  // ❌ MOVE TO UTILITIES
}
```

**Corrected:**
```json
{
  "id": "code_reviewer",
  "entrypoint": "agents/agents/code-reviewer.ts"  // ✅ PROPER AGENT
}
```

---

## Rule 8: Ghost Agent Detection (Pre-commit Hook)

**Requirement:**
Pre-commit hook MUST fail if ANY of these conditions are true:

1. Agent in registry but entrypoint file doesn't exist
   ```bash
   jq '.agents[] | select(.entrypoint) | .entrypoint' agents/registry/agents.json | \
     while read f; do
       [ -f "${f%\"}" ] || echo "FAIL: Missing $f" && exit 1
     done
   ```

2. Agent status="active" but no implementation
   ```bash
   jq '.agents[] | select(.status == "active") | .id' agents/registry/agents.json | \
     while read id; do
       [ -s "agents/agents/$id.ts" ] || echo "FAIL: Active agent $id has no implementation" && exit 1
     done
   ```

3. Agent status="dormant" but file missing OR no TODO comment
   ```bash
   jq '.agents[] | select(.status == "dormant") | .id' agents/registry/agents.json | \
     while read id; do
       [ -f "agents/agents/$id.ts" ] || echo "FAIL: Dormant agent $id missing file" && exit 1
       grep -q "TODO" "agents/agents/$id.ts" || echo "FAIL: Dormant $id has no TODO" && exit 1
     done
   ```

---

## Rule 9: Agent MUST Be Orches**Trable

**Requirement:**
- Agent MUST support being called by `AgentRunner` (see `agents/runtime/runner.ts`)
- Agent config MUST match schema in `agents/registry/schema.json`
- Agent MUST accept standard CLI args: `--dry`, `--exec`, `--config`

**Validation:**
```bash
bun agent:run <id> --dry
# MUST succeed without errors
```

---

## Enforcement: Pre-Commit Hook

**Location:** `.husky/pre-commit`

**Checks (in order):**
1. No ghost agents (file exists + status valid)
2. No invalid entrypoint locations (only `agents/agents/`)
3. No invalid status values (active|dormant|broken only)
4. TypeScript compilation: `tsc --noEmit`
5. Registry lint: `bun agent:lint`

**Behavior:**
- If ANY check fails, commit is BLOCKED
- User MUST fix issues before retry
- No `--no-verify` allowed (enforced via hook config)

---

## Audit Trail: docs/AGENT_DEPRECATION_LOG.md

All removed agents MUST be logged in `docs/AGENT_DEPRECATION_LOG.md`:

```markdown
# Removed Agents

| Agent ID | Reason | Date | Notes |
|----------|--------|------|-------|
| orchestrator | Never implemented (ghost agent) | 2026-03-27 | See commit abc123 |
```

---

## Migration Path (Egos-Lab)

**Current state:** Some agents in egos-lab have `scripts/` entrypoints or invalid locations.

**Action plan:**
1. Convert `scripts/` utilities to `agents/agents/` proper agents
2. Move external subrepos into `agents/agents/` with wrapper
3. Replace markdown entrypoints with minimal `.ts` placeholder
4. Add TODO comment to all dormant agents

**Timeline:** Phase 2 (2026-Q2)

---

## Summary: Agent Qualification Matrix

```
Agent MUST satisfy ALL:

1. ✅ Implementation exists (.ts file, ≥ 50 lines)
2. ✅ Valid TypeScript (tsc --noEmit passes)
3. ✅ Correct location (agents/agents/*.ts)
4. ✅ Registry entry (valid schema)
5. ✅ Legal status (active|dormant|broken)
6. ✅ If dormant: has explicit TODO comment
7. ✅ Supports --dry flag
8. ✅ Passes pre-commit validation

If ANY fail → NOT a qualified EGOS Agent → REMOVE from registry
```

---

## Document History

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0.0 | 2026-03-27 | activation.egos | Initial creation — CRITICAL governance |
