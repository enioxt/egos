#!/usr/bin/env bash
# spec-gate-check.sh — SDD-006
# Warning-only check: if the current branch is feat/*, verify that the
# corresponding SPEC doc exists under docs/specs/.
#
# Usage (in a pre-commit hook or standalone):
#   bash scripts/spec-gate-check.sh
#
# Always exits 0 — this is a WARNING, not a blocker.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
SPECS_DIR="$REPO_ROOT/docs/specs"

# 1. Get current branch
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"

# 2. Only act on feat/* branches
if [[ ! "$BRANCH" =~ ^feat/ ]]; then
  exit 0
fi

# 3. Derive spec slug: feat/guard-brasil-pii → GUARD-BRASIL-PII
BRANCH_SLUG="${BRANCH#feat/}"                          # strip "feat/"
SPEC_SLUG="${BRANCH_SLUG^^}"                           # uppercase
SPEC_SLUG="${SPEC_SLUG//[^A-Z0-9]/-}"                 # non-alphanumeric → dash
SPEC_SLUG="${SPEC_SLUG##-}"                            # strip leading dashes
SPEC_SLUG="${SPEC_SLUG%%-}"                            # strip trailing dashes

SPEC_FILE="$SPECS_DIR/SPEC-${SPEC_SLUG}.md"
SPEC_REL="docs/specs/SPEC-${SPEC_SLUG}.md"

# 4. Check existence and warn if missing
if [[ ! -f "$SPEC_FILE" ]]; then
  echo ""
  echo "⚠️  SPEC missing for branch '$BRANCH'"
  echo "   Expected: $SPEC_REL"
  echo "   Run: cp docs/specs/SPEC-TEMPLATE.md $SPEC_REL"
  echo "   Or use the /spec:init skill if available."
  echo ""
fi

# Always exit 0 — warning only, never blocks the commit
exit 0
