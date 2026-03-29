# Agent Claim Contract

> **SSOT Owner:** `egos/docs/governance/AGENT_CLAIM_CONTRACT.md`
> **Version:** 1.0.0 | **Created:** 2026-03-29 | **Status:** ACTIVE — ENFORCED
> **Task:** EGOS-078

---

## Purpose

Defines the formal taxonomy for anything claimed as an "agent" in the EGOS ecosystem, with mandatory proof fields per tier. Enforced by `scripts/agent-claim-lint.sh` at pre-commit.

---

## Taxonomy

### `component`
A library, module, or utility with no execution entrypoint of its own.

- **Example:** `@egos/shared`, `@egos/types`, `@egos/guard-brasil`
- **Registry:** Must NOT appear in `agents/registry/agents.json`
- **Proof required:** None — components live in `packages/`

---

### `skill`
A callable, stateless function exposed as a named capability. Single input → single output. No memory, no side effects beyond its return value.

- **Example:** `maskPublicOutput()`, `scanForPII()`, `validateResponse()`
- **Registry:** Declared in `docs/CAPABILITY_REGISTRY.md`, not in `agents.json`
- **Proof required:**
  - [ ] Exported function in a package file
  - [ ] Unit test covering the function

---

### `agent_candidate`
Designed and described as an agent, but runtime execution not yet validated.

- **Example:** A `.ts` file exists, the agent is registered, but has never been run end-to-end
- **Registry:** May appear in `agents.json` with `"status": "candidate"`
- **Mandatory fields in `agents.json`:**
  ```json
  {
    "id": "...",
    "name": "...",
    "description": "...",
    "area": "...",
    "entrypoint": "path/to/agent.ts",
    "run_modes": ["dry_run"],
    "triggers": ["manual"],
    "status": "candidate",
    "ownership": "..."
  }
  ```
- **Proof required:**
  - [ ] `entrypoint` file exists on disk
  - [ ] `status` is `"candidate"` (not `"active"`)

---

### `verified_agent`
Has an entrypoint, has been run at least once in `dry_run` mode, and has a recorded eval or test.

- **Registry:** Appears in `agents.json` with `"status": "active"`
- **Mandatory fields in `agents.json`:**
  ```json
  {
    "id": "...",
    "name": "...",
    "description": "...",
    "area": "...",
    "entrypoint": "path/to/agent.ts",
    "run_modes": ["dry_run", "execute"],
    "triggers": ["manual"],
    "evals": "path/to/test-or-eval-evidence",
    "observability": "console | telemetry.ts | supabase",
    "ownership": "...",
    "risk_level": "T0 | T1 | T2",
    "status": "active"
  }
  ```
- **Proof required:**
  - [ ] `entrypoint` file exists on disk
  - [ ] `evals` field points to a real file or documented evidence
  - [ ] At least one `run_modes` entry beyond `dry_run`
  - [ ] `risk_level` declared
  - [ ] `ownership` declared

---

### `online_agent`
Running in production — has daemon or scheduled trigger, connected to live systems.

- **Registry:** Appears in `agents.json` with `"status": "active"` and `"triggers"` includes `"scheduled"` or `"event"`
- **Mandatory fields:** All `verified_agent` fields, plus:
  ```json
  {
    "triggers": ["scheduled | event | webhook"],
    "observability": "supabase | redis | external logging URL",
    "sla": "best_effort | 99% | 99.5%"
  }
  ```
- **Proof required:** All `verified_agent` proof, plus:
  - [ ] `observability` points to a live system
  - [ ] `sla` declared
  - [ ] At least one documented run in production

---

## Current Registry Audit (2026-03-29)

| Agent ID | Current Status | Contract Tier | Missing Fields |
|----------|---------------|---------------|----------------|
| `dep_auditor` | `active` | `verified_agent` | `evals`, `observability`, `ownership` |
| `archaeology_digger` | `active` | `verified_agent` | `evals`, `observability`, `ownership` |
| `chatbot_compliance_checker` | `active` | `verified_agent` | `evals`, `observability`, `ownership` |
| `dead_code_detector` | `active` | `verified_agent` | `evals`, `observability`, `ownership` |
| `capability_drift_checker` | `active` | `verified_agent` | `evals`, `observability`, `ownership` |
| `context_tracker` | `active` | `verified_agent` | `evals`, `observability`, `ownership` |
| `gtm_harvester` | `active` | `agent_candidate` | `evals`, `observability`, `ownership` |
| `aiox_gem_hunter` | `active` | `agent_candidate` | `evals`, `observability`, `ownership` |
| `framework_benchmarker` | `active` | `agent_candidate` | `evals`, `observability`, `ownership` |
| `mastra_gem_hunter` | `active` | `agent_candidate` | `evals`, `observability`, `ownership` |
| `ssot_auditor` | `active` | `verified_agent` | `evals`, `observability`, `ownership` |
| `ssot_fixer` | `active` | `verified_agent` | `evals`, `observability`, `ownership` |
| `drift_sentinel` | `active` | `verified_agent` | `evals`, `observability`, `ownership` |

**Action:** No agent is blocked — `evals` and `ownership` will be added in EGOS-079 enforcement pass.
**Zero agents are `online_agent`** — all run manually or on-demand.

---

## Enforcement

Enforced by `scripts/agent-claim-lint.sh`. Run at:
- Pre-commit (if `agents/registry/agents.json` is staged)
- `bun run agent:lint`

See: `docs/governance/NEW_PROJECT_GATE.md` for new surface gate.

---

*Maintained by: EGOS Kernel*
*Related: EGOS-078, EGOS-079, agents/registry/agents.json, scripts/agent-claim-lint.sh*
