#!/bin/bash
# EGOS Supabase Safety Check — Pre-commit guard (INC-004)
#
# Detects dangerous patterns in staged code that could cause:
# - Supabase Realtime quota exhaustion
# - Runaway DB writes (missing rate limits)
# - Realtime publication of high-volume tables
# - Missing RLS on new tables
#
# Exit 0 = pass, Exit 1 = blocked

set -eu

echo "📋 EGOS Supabase Safety Check v1.0"

STAGED_CODE=$(git diff --cached --name-only 2>/dev/null | grep -E '\.(ts|tsx|js|jsx)$' || true)

if [ -z "$STAGED_CODE" ]; then
  echo "✅ No code files staged — skipping Supabase safety check"
  exit 0
fi

VIOLATIONS=0
WARNINGS=0

# ── Check 1: Realtime publication additions ─────────────────────────────
# Adding tables to supabase_realtime without review is dangerous.
REALTIME_ADDS=$(git diff --cached -- $STAGED_CODE 2>/dev/null | grep '^+' | grep -v '^+++' | \
  grep -iE 'supabase_realtime|ALTER\s+PUBLICATION.*ADD\s+TABLE' || true)

if [ -n "$REALTIME_ADDS" ]; then
  echo "  ❌ CRITICAL: Code adds tables to Supabase Realtime publication!"
  echo "     Every INSERT to published tables generates Realtime messages (quota cost)."
  echo "     Review: Is this table low-volume? Does it NEED real-time subscribers?"
  echo "$REALTIME_ADDS" | head -5 | sed 's/^/     /'
  VIOLATIONS=$((VIOLATIONS + 1))
fi

# ── Check 2: Fire-and-forget Supabase writes in loops ──────────────────
# Pattern: .from('table').insert/upsert inside for/while/map loops
DIFF_CONTENT=$(git diff --cached -- $STAGED_CODE 2>/dev/null)

LOOP_WRITES=$(echo "$DIFF_CONTENT" | grep '^+' | grep -v '^+++' | \
  grep -iE '\.from\(.*\)\.(insert|upsert)' || true)

if [ -n "$LOOP_WRITES" ]; then
  # Check if any of these are in loop context (heuristic: look for for/while/map nearby)
  LOOP_CONTEXT=$(echo "$DIFF_CONTENT" | grep '^+' | grep -v '^+++' | \
    grep -B5 -iE '\.from\(.*\)\.(insert|upsert)' | \
    grep -iE '\b(for\s*\(|while\s*\(|\.forEach\(|\.map\()' || true)

  if [ -n "$LOOP_CONTEXT" ]; then
    echo "  ⚠️  WARNING: Supabase INSERT/UPSERT detected inside loop pattern."
    echo "     High-frequency DB writes can exhaust Supabase quota."
    echo "     Consider: batch upsert, rate limiting, or bulk operations."
    echo "$LOOP_CONTEXT" | head -3 | sed 's/^/     /'
    WARNINGS=$((WARNINGS + 1))
  fi
fi

# ── Check 3: event-bus emit() without severity parameter ───────────────
# Calls to emit() that default to severity='info' in high-frequency contexts
EMIT_NO_SEVERITY=$(echo "$DIFF_CONTENT" | grep '^+' | grep -v '^+++' | \
  grep -E "emit\([^)]*\)" | grep -v "severity" | grep -v "warn\|error\|critical" || true)

if [ -n "$EMIT_NO_SEVERITY" ]; then
  echo "  ℹ️  NOTE: emit() calls found without explicit severity."
  echo "     Default is 'info' (rate-limited, no Realtime broadcast)."
  echo "     Use severity='warn'+ only for actionable events."
fi

# ── Check 4: New migration without RLS ─────────────────────────────────
MIGRATION_FILES=$(echo "$STAGED_CODE" | grep -iE 'migration|\.sql' || true)
if [ -n "$MIGRATION_FILES" ]; then
  CREATE_TABLE=$(echo "$DIFF_CONTENT" | grep '^+' | grep -v '^+++' | \
    grep -iE 'CREATE\s+TABLE' || true)
  RLS_ENABLE=$(echo "$DIFF_CONTENT" | grep '^+' | grep -v '^+++' | \
    grep -iE 'ENABLE\s+ROW\s+LEVEL\s+SECURITY|ALTER\s+TABLE.*ENABLE\s+RLS' || true)

  if [ -n "$CREATE_TABLE" ] && [ -z "$RLS_ENABLE" ]; then
    echo "  ⚠️  WARNING: CREATE TABLE found without ENABLE ROW LEVEL SECURITY."
    echo "     All new tables should have RLS enabled."
    echo "$CREATE_TABLE" | head -3 | sed 's/^/     /'
    WARNINGS=$((WARNINGS + 1))
  fi
fi

# ── Check 5: Modifying frozen event-bus without INC reference ──────────
EVENTBUS_CHANGED=$(git diff --cached --name-only 2>/dev/null | grep 'event-bus\.ts$' || true)
if [ -n "$EVENTBUS_CHANGED" ]; then
  COMMIT_MSG=$(cat "$(git rev-parse --git-dir)/COMMIT_EDITMSG" 2>/dev/null || echo "")
  if ! echo "$COMMIT_MSG" | grep -qiE 'INC-|SECURITY|CRITICAL'; then
    echo "  ⚠️  WARNING: event-bus.ts is modified (frozen zone)."
    echo "     Changes to event emission affect Supabase quota. Include INC reference."
    WARNINGS=$((WARNINGS + 1))
  fi
fi

# ── Summary ─────────────────────────────────────────────────────────────
if [ "$VIOLATIONS" -gt 0 ]; then
  echo ""
  echo "❌ BLOCKED: $VIOLATIONS critical Supabase safety violation(s) found."
  echo "   Fix violations above, or add 'SUPABASE-SAFETY-OVERRIDE: <reason>' to commit message."
  # Allow override via commit message
  COMMIT_MSG=$(cat "$(git rev-parse --git-dir)/COMMIT_EDITMSG" 2>/dev/null || echo "")
  if echo "$COMMIT_MSG" | grep -q 'SUPABASE-SAFETY-OVERRIDE:'; then
    echo "   ⚠️  Override detected — proceeding with caution."
  else
    exit 1
  fi
fi

if [ "$WARNINGS" -gt 0 ]; then
  echo "  ⚠️  $WARNINGS warning(s) — review recommended but not blocking."
fi

echo "✅ Supabase safety check passed"
exit 0
