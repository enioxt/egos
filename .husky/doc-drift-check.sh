#!/bin/sh
# EGOS Doc-Drift Check — Layer 2 of the Doc-Drift Shield
# Blocks commits whose code changes drift from declared .egos-manifest.yaml claims
# without pairing them with a README/manifest update.
#
# Part of: docs/DOC_DRIFT_SHIELD.md
# Schema: .egos-manifest.yaml
# Verifier: agents/agents/doc-drift-verifier.ts

set -eu

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")
MANIFEST="$REPO_ROOT/.egos-manifest.yaml"

# Skip if no manifest (opt-in — repos without L1 are unprotected)
if [ ! -f "$MANIFEST" ]; then
  echo "  [doc-drift] no manifest in $REPO_ROOT — skipping (add .egos-manifest.yaml to opt in)"
  exit 0
fi

# Rule B: Override via commit message body
# Add "DOC-DRIFT-ACCEPTED: <reason>" to commit body to bypass this check.
COMMIT_MSG_FILE="$REPO_ROOT/.git/COMMIT_EDITMSG"
if [ -f "$COMMIT_MSG_FILE" ] && grep -q "DOC-DRIFT-ACCEPTED:" "$COMMIT_MSG_FILE" 2>/dev/null; then
  REASON=$(grep "DOC-DRIFT-ACCEPTED:" "$COMMIT_MSG_FILE" | head -1)
  echo "  [doc-drift] OVERRIDE accepted: $REASON"
  OVERRIDES_LOG="$REPO_ROOT/docs/jobs/doc-drift-overrides.log"
  mkdir -p "$(dirname "$OVERRIDES_LOG")" 2>/dev/null || true
  echo "$(date -Iseconds) $REASON" >> "$OVERRIDES_LOG" 2>/dev/null || true
  exit 0
fi

# Rule A: Pairing — only run verifier when code is staged
STAGED_CODE=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null | grep -E '\.(ts|tsx|py|js|jsx)$' || true)

if [ -z "$STAGED_CODE" ]; then
  echo "  [doc-drift] no code staged — skipping verifier"
  exit 0
fi

echo "  [doc-drift] code staged — running drift verifier..."
cd "$REPO_ROOT"

VERIFIER="/home/enio/egos/agents/agents/doc-drift-verifier.ts"
if [ ! -f "$VERIFIER" ]; then
  echo "  [doc-drift] WARNING: verifier not found at $VERIFIER — skipping"
  exit 0
fi

# Run verifier; capture output to temp file for human-readable error display
DRIFT_JSON=$(mktemp /tmp/doc-drift-XXXXXX.json)
trap 'rm -f "$DRIFT_JSON"' EXIT

if ! bun "$VERIFIER" --repo "$REPO_ROOT" --fail-on-drift --json > "$DRIFT_JSON" 2>/dev/null; then
  echo ""
  echo "❌ DOC-DRIFT BLOCKED: code changes drifted from declared claims."
  echo ""

  # Print drifted claims in human-readable form (non-interactive, no prompts)
  python3 - <<'PYEOF'
import json, sys
try:
    with open("$DRIFT_JSON") as f:
        d = json.load(f)
    drifted = [r for r in d.get("results", []) if r.get("status") == "drifted"]
    for r in drifted:
        pct = f"  ({r['drift_pct']}% drift)" if r.get('drift_pct') else ""
        delta = f"  (Δ{r['drift_abs']})" if r.get('drift_abs') else ""
        print(f"  - {r['id']}: last={r['last_value']} current={r['current_value']} tolerance={r['tolerance']}{pct}{delta}")
except Exception as e:
    print(f"  (could not parse drift report: {e})")
PYEOF
  # Fallback if python3 not available
  if command -v python3 > /dev/null 2>&1 && [ -s "$DRIFT_JSON" ]; then
    python3 -c "
import json, sys
try:
    d = json.load(open('$DRIFT_JSON'))
    for r in d.get('results', []):
        if r.get('status') == 'drifted':
            delta = f'  (delta={r.get(\"drift_abs\",\"\")}%)' if r.get('drift_abs') else ''
            print(f'  - {r[\"id\"]}: last={r[\"last_value\"]} current={r[\"current_value\"]} tolerance={r[\"tolerance\"]}{delta}')
except: pass
" 2>/dev/null || cat "$DRIFT_JSON"
  fi

  echo ""
  echo "Fix options:"
  echo "  1. Update README.md with new numbers + re-stage"
  echo "  2. Update .egos-manifest.yaml last_value + last_verified_at + re-stage"
  echo "  3. Override: add 'DOC-DRIFT-ACCEPTED: <reason>' to commit body"
  echo ""
  echo "  Verify: bun agents/agents/doc-drift-verifier.ts --repo $REPO_ROOT"
  exit 1
fi

echo "  [doc-drift] ✅ all claims verified"
exit 0
