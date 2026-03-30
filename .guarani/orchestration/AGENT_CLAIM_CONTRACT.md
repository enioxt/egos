# AGENT CLAIM CONTRACT — EGOS Kernel

> **Version:** 1.0.0 | **Ticket:** EGOS-078 | **Updated:** 2026-03-30
> **Enforced by:** `bun scripts/agent-claim-lint.ts` (EGOS-079)
> **Schema binding:** `agents/registry/schema.json` — `kind` field

---

## Purpose

Prevent "agent theater": the practice of calling any script, wrapper, or
concept an "agent" without evidence that it runs autonomously, handles
failures, and produces observable output. Every entry in `agents.json`
must declare an honest `kind` and carry proof proportional to that claim.

---

## Formal Taxonomy

### 1. `component`

A reusable building block with no autonomous behavior.
Examples: a TypeScript utility, a shared library function, a type definition.

**Not registered in agents.json.** Lives in `packages/`.

| Proof Required | None |
|---|---|
| Entrypoint | Not applicable |
| Triggers | Not applicable |

---

### 2. `tool`

A single-purpose CLI script invoked manually or by a human-driven
pipeline. Runs to completion and exits. No loop, no autonomy.

**Registered in agents.json with `kind: "tool"`.**

| Field | Requirement |
|---|---|
| `entrypoint` | Path to executable file — must exist on disk |
| `runtime_proof` | Command that validates the tool runs (e.g. `bun x.ts --dry-run`) |
| `run_modes` | Must include `dry_run` |
| `triggers` | Must include `manual` |
| `owner` | GitHub handle — required |
| `risk_level` | T0–T3 — required |

**Cannot be called an agent.** It is a tool.

---

### 3. `workflow`

A multi-step orchestration script that coordinates other tools or agents.
May call external APIs. Still human-triggered. No persistent loop.

**Registered in agents.json with `kind: "workflow"`.**

| Field | Requirement |
|---|---|
| `entrypoint` | Path to executable file — must exist on disk |
| `runtime_proof` | Command that validates the workflow runs |
| `run_modes` | Must include `dry_run` |
| `triggers` | At minimum `manual` |
| `owner` | Required |
| `side_effects` | Must declare all external state mutations |

**Cannot be called an agent.** It is a workflow.

---

### 4. `agent_candidate`

A script that exhibits some agent-like qualities (loop, LLM calls,
reactions to events) but has NOT been verified in production. Proof of
real execution is absent or incomplete.

**Registered in agents.json with `kind: "agent_candidate"`.**

| Field | Requirement |
|---|---|
| `entrypoint` | Path to executable file — must exist on disk |
| `runtime_proof` | WARN if missing (not blocking) |
| `loop_mechanism` | Must be non-`none` (otherwise demote to `tool`) |
| `triggers` | Must include at least one non-`manual` trigger |
| `owner` | Required |
| `telemetry_source` | Required — even if just `stdout` |

**May be referred to as "agent candidate" or "candidate agent".**
Must NOT be marketed or documented as a production agent.

---

### 5. `verified_agent`

An agent that has been confirmed to run autonomously in a real
environment, emits structured telemetry, and has at least one evaluation
proving its output quality.

**Registered in agents.json with `kind: "verified_agent"`.**

| Field | Requirement | Blocking? |
|---|---|---|
| `entrypoint` | File must exist on disk | YES |
| `runtime_proof` | Non-empty command string | YES |
| `loop_mechanism` | Non-`none` | YES |
| `triggers` | At least one non-`manual` | YES |
| `eval_suite` | At least one eval reference | YES |
| `telemetry_source` | Non-`stdout` preferred (file/db) | WARN |
| `last_duration_ms` | Must be ≥ 0 (real measurement) | YES |
| `owner` | GitHub handle | YES |
| `side_effects` | Declared (empty array is valid if read-only) | YES |

**Upgrade path from `agent_candidate`:**
1. Agent has run in production (or staging equivalent) at least once.
2. `last_duration_ms` is updated from a real execution (not -1).
3. `runtime_proof` command is executable and exits 0.
4. `eval_suite` references at least one passing test or eval script.
5. `loop_mechanism` is set to a real value (`cron`, `event_driven`, etc.).
6. PR is opened with evidence attached (log output or CI artifact).
7. Registry entry is updated to `kind: "verified_agent"`.

---

### 6. `online_agent`

A `verified_agent` that is actively running in a persistent process
(daemon, serverless function, or scheduled job) in a live environment.

**Registered in agents.json with `kind: "online_agent"`.**

Inherits ALL requirements from `verified_agent`, plus:

| Additional Field | Requirement | Blocking? |
|---|---|---|
| `runtime_proof` | Must be a health endpoint or live log path | YES |
| `telemetry_source` | Must be a persistent sink (db, file, external service) | YES |
| `loop_mechanism` | Must be `cron`, `event_driven`, or `while_loop` | YES |

**Upgrade path from `verified_agent`:**
1. Agent is deployed to production environment.
2. Health check or log confirms it is running continuously.
3. `runtime_proof` is updated to the live endpoint or log path.
4. `telemetry_source` points to a persistent sink.
5. Registry entry is updated to `kind: "online_agent"`.

---

## What CANNOT Be Called an "Agent" Without Proof

| Claim | Without Proof | Correct Label |
|---|---|---|
| "This script is an AI agent" | No loop, no autonomy | `tool` |
| "Our agent monitors X" | No runtime evidence, no telemetry | `agent_candidate` |
| "Verified production agent" | `last_duration_ms: -1`, no evals | `agent_candidate` |
| "Online agent handling requests" | No health endpoint, no persistent log | `verified_agent` at best |
| "Agent with 99% accuracy" | No `eval_suite` reference | marketing copy, not a claim |

The word **"agent"** in documentation, dashboards, or external
communications MUST correspond to a registry entry with
`kind: "verified_agent"` or `kind: "online_agent"`.

---

## Integration with Schema

The `kind` field in `agents/registry/schema.json` currently supports:

```
"verified_agent" | "agent_candidate" | "workflow" | "tool" | "dormant"
```

**EGOS-078 adds `online_agent` as a valid kind.**
The schema must be updated to add `"online_agent"` to the enum before any
entry uses it.

Fields required per kind (enforcement matrix for agent-claim-lint.ts):

| Field | tool | workflow | agent_candidate | verified_agent | online_agent |
|---|---|---|---|---|---|
| `entrypoint` exists on disk | ERROR | ERROR | ERROR | ERROR | ERROR |
| `runtime_proof` non-empty | WARN | WARN | WARN | ERROR | ERROR |
| `loop_mechanism` ≠ none | — | — | ERROR | ERROR | ERROR |
| `eval_suite` non-empty | — | — | — | ERROR | ERROR |
| `last_duration_ms` ≥ 0 | — | — | — | ERROR | ERROR |
| `telemetry_source` non-null | — | — | WARN | WARN | ERROR |
| `owner` non-empty | ERROR | ERROR | ERROR | ERROR | ERROR |

Legend: ERROR = lint fails (exit 1), WARN = logged but does not fail, — = not checked.

---

## Governance Notes

- This contract is enforced at commit time via `bun scripts/agent-claim-lint.ts`.
- Adding or promoting a registry entry requires the proof fields above.
- Demoting an entry (e.g., `verified_agent` → `agent_candidate`) is always allowed and encouraged if evidence is missing.
- The kernel currently has **0 verified_agents** (all entries are `tool` or `workflow`). This is intentional and honest. Verified agents live in leaf repos after they accumulate production evidence.
- `dormant` entries are allowed but must have a TASKS.md entry to either revive or delete them within 30 days.

---

*See also:* `agents/registry/schema.json`, `agents/registry/agents.json`,
`.guarani/orchestration/DOMAIN_RULES.md` §1 (Agentic Platform).
