# Caldex QA/Governance Action Plan (2026-04-02)

## Wave 1 — Stabilize (done)
- telemetry minimum gate enforced
- ssot diagnostic classification + CI summary

## Wave 2 — Operationalize (in progress)
- actionable playbook by classification
- confidence score + mixed_drift fallback
- JSON outputs for machine integrations

## Wave 3 — Prevent regressions
- adopt `ssot:diagnostic` in local pre-commit global hook (`~/.egos/hooks/pre-commit`)
- add monthly false-positive review for diagnostic heuristics
- introduce trend report of drift classifications over time

## Wave 4 — Interconnection / refactor
- unify QA artifact schemas (`qa-evidence`, `qa-ssot-check`, guardrail)
- add lightweight composer script to aggregate all QA outputs in one JSON envelope
