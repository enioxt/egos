#!/bin/bash
# EGOS Legacy Code Detector — Pre-Commit Check
# Detects common legacy/dead code patterns being staged
# Non-blocking (warns only) — use --strict to block

set -e

STRICT="${1:-}"
STAGED_CODE=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(ts|tsx|js|py)$' || true)
WARNINGS=0

[ -z "$STAGED_CODE" ] && echo "✅ No code files staged" && exit 0

echo "🔍 Legacy Code Detector"

while IFS= read -r file; do
  [ ! -f "$file" ] && continue
  CONTENT=$(git diff --cached -- "$file" 2>/dev/null | grep '^+' | grep -v '^+++' || true)

  # 1. TODO/FIXME accumulation (>3 in one file diff = tech debt)
  TODO_COUNT=$(echo "$CONTENT" | grep -ciE '^\+.*\b(TODO|FIXME|HACK|XXX)\b' || true)
  if [ "$TODO_COUNT" -gt 3 ]; then
    echo "  ⚠️  $file: $TODO_COUNT TODO/FIXME added (tech debt threshold: 3)"
    WARNINGS=$((WARNINGS + 1))
  fi

  # 2. Console.log debug leaks in TS/JS
  if [[ "$file" =~ \.(ts|tsx|js)$ ]]; then
    DEBUG_LOGS=$(echo "$CONTENT" | grep -cE '^\+\s*console\.(log|debug|dir)\(' || true)
    if [ "$DEBUG_LOGS" -gt 2 ]; then
      echo "  ⚠️  $file: $DEBUG_LOGS console.log/debug added (remove debug logs before commit)"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi

  # 3. Commented-out code blocks (>5 lines = probably dead code)
  COMMENTED=$(echo "$CONTENT" | grep -cE '^\+\s*(//|#)\s*(const|function|def |class |import |export )' || true)
  if [ "$COMMENTED" -gt 5 ]; then
    echo "  ⚠️  $file: $COMMENTED commented-out code lines (consider deleting dead code)"
    WARNINGS=$((WARNINGS + 1))
  fi

  # 4. Unused imports pattern in TS (import X but X never used in diff)
  if [[ "$file" =~ \.(ts|tsx)$ ]]; then
    NEW_IMPORTS=$(echo "$CONTENT" | grep -E '^\+import ' | grep -oP "(?<=import \{ ).*?(?= \})" | tr ',' '\n' | sed 's/\s//g' | head -20)
    while IFS= read -r imp; do
      [ -z "$imp" ] && continue
      # Check if imported name appears more than once (import line + usage)
      USAGE=$(echo "$CONTENT" | grep -c "\b${imp}\b" || true)
      if [ "$USAGE" -lt 2 ]; then
        echo "  ⚠️  $file: possible unused import '$imp'"
        WARNINGS=$((WARNINGS + 1))
      fi
    done <<< "$NEW_IMPORTS"
  fi

  # 5. Hardcoded localhost/127.0.0.1 in non-test code
  if [[ ! "$file" =~ (test|spec|\.test\.|\.spec\.) ]]; then
    HARDCODED=$(echo "$CONTENT" | grep -cE '^\+.*(localhost|127\.0\.0\.1):' || true)
    if [ "$HARDCODED" -gt 0 ]; then
      echo "  ⚠️  $file: hardcoded localhost URL (use env var)"
      WARNINGS=$((WARNINGS + 1))
    fi
  fi

done <<< "$STAGED_CODE"

if [ "$WARNINGS" -gt 0 ]; then
  echo ""
  echo "  ⚠️  $WARNINGS legacy code warning(s). These are non-blocking but reduce quality."
  echo "  💡 Run: git diff --cached to review before committing."
  if [ "$STRICT" = "--strict" ]; then
    echo "  ❌ STRICT mode: blocking commit with legacy code."
    exit 1
  fi
fi

echo "✅ Legacy code check: $WARNINGS warning(s)"
