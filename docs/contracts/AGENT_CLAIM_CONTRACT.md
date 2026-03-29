# Agent Claim Contract — EGOS-078

> **VERSION:** 1.0.0 | **DATE:** 2026-03-29
> **PURPOSE:** Formal taxonomy for agent maturity levels with mandatory proof fields.
> **ENFORCEMENT:** `agents/registry/agents.json` schema + `agent:lint` CI check.

## Agent Maturity Taxonomy

| Level | Name | Definition | Proof Required |
|-------|------|-----------|----------------|
| L0 | `component` | Reusable function/module — NOT an agent | Export in `@egos/shared`, unit tests |
| L1 | `skill` | Single-purpose utility with CLI interface | Entrypoint, `--dry` mode, zero external deps |
| L2 | `agent_candidate` | Registered in `agents.json`, runs in dry-run | Registry entry, entrypoint, Finding[] output |
| L3 | `verified_agent` | Passes eval suite + has runtime evidence | L2 + eval results + JSONL audit log |
| L4 | `online_agent` | Runs in production with monitoring | L3 + telemetry integration + health endpoint |

## Mandatory Proof Fields per Level

### L0 — Component
```json
{ "type": "component", "module": "packages/shared/src/X.ts", "tests": 5, "exports": ["fn1", "fn2"] }
```

### L1 — Skill
```json
{ "type": "skill", "entrypoint": "scripts/X.ts", "dry_run": true, "deps": 0 }
```

### L2 — Agent Candidate
```json
{
  "id": "my_agent",
  "type": "agent_candidate",
  "entrypoint": "agents/agents/my-agent.ts",
  "run_modes": ["dry_run"],
  "triggers": ["manual"],
  "risk_level": "T0",
  "status": "active"
}
```

### L3 — Verified Agent
```json
{
  "...L2 fields",
  "run_modes": ["dry_run", "execute"],
  "eval_suite": ["tests/my-agent.eval.ts"],
  "runtime_evidence": "agents/.logs/my_agent.jsonl",
  "last_verified": "2026-03-29T00:00:00Z"
}
```

### L4 — Online Agent
```json
{
  "...L3 fields",
  "health_endpoint": "/api/agents/my_agent/health",
  "telemetry_table": "agent_runs",
  "monitoring": { "alerts": true, "dashboard": "https://..." }
}
```

## Current Agent Classification

| Agent | Current Level | Missing for Next |
|-------|-------------|-----------------|
| dep_auditor | L2 | Eval suite for L3 |
| archaeology_digger | L2 | Eval suite for L3 |
| chatbot_compliance_checker | L2 | Eval suite for L3 |
| dead_code_detector | L2 | Eval suite for L3 |
| capability_drift_checker | L2 | Eval suite for L3 |
| context_tracker | L2 | Eval suite for L3 |
| gtm_harvester | L2 | Eval suite for L3 |
| aiox_gem_hunter | L2 | Eval suite for L3 |
| framework_benchmarker | L2 | Eval suite for L3 |
| mastra_gem_hunter | L2 | Eval suite for L3 |
| spec_router | L1 (sketch) | Registry entry for L2 |
| mcp_router | L1 (sketch) | Registry entry for L2 |

## Gate Enforcement

1. `agent:lint` MUST validate that every agent in `agents.json` has required fields for its claimed level.
2. No agent can claim L3+ without `eval_suite` pointing to an existing test file.
3. No agent can claim L4 without `health_endpoint` and `telemetry_table`.
4. Pre-commit blocks registry changes that violate this contract.

## Promotion Protocol

1. Developer adds agent at L2 with mandatory fields.
2. Developer writes eval suite → agent:lint validates → promote to L3.
3. Developer adds telemetry + health → promote to L4.
4. Demotions happen when: eval suite fails, runtime evidence stale >30 days, health endpoint unreachable.
