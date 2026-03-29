#!/bin/sh
# agent-claim-lint.sh — Enforce Agent Claim Contract on agents/registry/agents.json
# EGOS-079 | docs/governance/AGENT_CLAIM_CONTRACT.md
#
# Exit codes:
#   0 — all agents pass the contract
#   1 — one or more violations found

set -eu

REGISTRY="agents/registry/agents.json"
CONTRACT="docs/governance/AGENT_CLAIM_CONTRACT.md"
VIOLATIONS=0

if [ ! -f "$REGISTRY" ]; then
  echo "agent-claim-lint: $REGISTRY not found — skipping"
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "agent-claim-lint: python3 not found — skipping"
  exit 0
fi

python3 - <<'PYEOF'
import json, sys, os

REGISTRY = "agents/registry/agents.json"

with open(REGISTRY) as f:
    data = json.load(f)

agents = data.get("agents", [])
violations = []

REQUIRED_BASE = ["id", "name", "description", "area", "entrypoint", "run_modes", "triggers", "status"]
REQUIRED_VERIFIED = REQUIRED_BASE + ["evals", "observability", "ownership", "risk_level"]
REQUIRED_ONLINE = REQUIRED_VERIFIED + ["sla"]

VALID_STATUSES = {"candidate", "active", "deprecated", "archived"}
VALID_RISK = {"T0", "T1", "T2", "T3"}
VALID_AREAS = {"architecture", "knowledge", "compliance", "governance", "product", "infra", "research"}

for agent in agents:
    aid = agent.get("id", "UNKNOWN")
    status = agent.get("status", "")
    errors = []

    # 1. Required base fields
    for field in REQUIRED_BASE:
        if field not in agent or not agent[field]:
            errors.append(f"missing required field: '{field}'")

    # 2. Status must be valid
    if status not in VALID_STATUSES:
        errors.append(f"invalid status '{status}' — must be one of: {', '.join(VALID_STATUSES)}")

    # 3. Entrypoint file must exist (when not candidate)
    entrypoint = agent.get("entrypoint", "")
    if entrypoint and status != "candidate" and not os.path.isfile(entrypoint):
        errors.append(f"entrypoint '{entrypoint}' does not exist on disk")

    # 4. Active agents need verified fields
    if status == "active":
        for field in REQUIRED_VERIFIED:
            if field not in agent or not agent[field]:
                errors.append(f"active agent missing verified field: '{field}'")

        risk = agent.get("risk_level", "")
        if risk and risk not in VALID_RISK:
            errors.append(f"invalid risk_level '{risk}' — must be T0, T1, T2, or T3")

    # 5. Online agents (scheduled/event triggers) need SLA
    triggers = agent.get("triggers", [])
    is_online = any(t in triggers for t in ["scheduled", "event", "webhook"])
    if is_online and "sla" not in agent:
        errors.append("online agent (scheduled/event trigger) missing 'sla' field")

    if errors:
        violations.append((aid, errors))

if violations:
    print(f"\nagent-claim-lint: {len(violations)} agent(s) violate the Agent Claim Contract")
    print(f"  Contract: {REGISTRY}\n")
    for aid, errs in violations:
        print(f"  [{aid}]")
        for e in errs:
            print(f"    - {e}")
    print(f"\nFix violations in {REGISTRY} or see docs/governance/AGENT_CLAIM_CONTRACT.md")
    sys.exit(1)
else:
    print(f"agent-claim-lint: {len(agents)} agent(s) pass contract ✓")
    sys.exit(0)
PYEOF
