#!/bin/bash
# /start v6.0 — Optimized Session Initialization
# Usage: bun scripts/start-v6.ts OR bash scripts/start-v6.sh

set -e

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo $PWD)
REPO_NAME=$(basename $ROOT)
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
TIMESTAMP=$(date -u +'%Y-%m-%dT%H:%M:%SZ')

echo "🎯 EGOS /START v6.0 — $REPO_NAME@$BRANCH | $TIMESTAMP"
echo ""

# ============================================================
# PHASE 1: PARALLEL DATA COLLECTION (all reads at once)
# ============================================================
echo "📊 Phase 1: Parallel diagnostics..."

# Collect all data in background
(git log --oneline -5 2>/dev/null) > /tmp/start_git_log &
(git status --short 2>/dev/null | wc -l) > /tmp/start_uncommitted &
(cat TASKS.md 2>/dev/null | wc -l) > /tmp/start_tasks_lines &
(cat agents/registry/agents.json 2>/dev/null | jq '.agents | length' 2>/dev/null || echo "0") > /tmp/start_agents_count &
(ls -lh /home/enio/egos/docs/jobs/*.md 2>/dev/null | wc -l) > /tmp/start_job_reports &
(grep -c "Status: CRITICAL" /home/enio/egos/docs/jobs/*.md 2>/dev/null || echo "0") > /tmp/start_critical_count &
(df -h / 2>/dev/null | tail -1) > /tmp/start_disk &
(free -h 2>/dev/null | awk 'NR==2 {print $3 "/" $2}') > /tmp/start_mem &
(ssh -i ~/.ssh/hetzner_ed25519 -o ConnectTimeout=3 root@204.168.217.125 'docker ps --quiet | wc -l' 2>/dev/null || echo "VPS unreachable") > /tmp/start_vps_containers &
(curl -s https://guard.egos.ia.br/health 2>&1 | jq -r '.status' 2>/dev/null || echo "API unreachable") > /tmp/start_api_status &

# Wait for all background jobs
wait

# Read results
UNCOMMITTED=$(cat /tmp/start_uncommitted)
TASKS_LINES=$(cat /tmp/start_tasks_lines)
AGENTS_COUNT=$(cat /tmp/start_agents_count)
JOB_REPORTS=$(cat /tmp/start_job_reports)
CRITICAL_COUNT=$(cat /tmp/start_critical_count)
DISK=$(cat /tmp/start_disk)
MEMORY=$(cat /tmp/start_mem)
VPS_CONTAINERS=$(cat /tmp/start_vps_containers)
API_STATUS=$(cat /tmp/start_api_status)

# ============================================================
# PHASE 2: MEMORY CONTEXT (load previous sessions)
# ============================================================
echo "📚 Loading session memory..."
MEMORY_INDEX="/home/enio/.claude/projects/-home-enio-egos/memory/MEMORY.md"
if [ -f "$MEMORY_INDEX" ]; then
  LAST_SESSION=$(head -1 "$MEMORY_INDEX" | grep -o "P[0-9]*" | tail -1 || echo "unknown")
  MEMORY_LINES=$(wc -l < "$MEMORY_INDEX")
else
  LAST_SESSION="unknown"
  MEMORY_LINES="0"
fi

# ============================================================
# PHASE 3: CRITICAL VALIDATION GATES
# ============================================================
echo "🔐 Phase 3: Validation gates..."

GATE_PASS=true

# Check required files
for file in TASKS.md AGENTS.md .windsurfrules .guarani/PREFERENCES.md agents/registry/agents.json; do
  if [ ! -f "$file" ]; then
    echo "  ❌ MISSING: $file"
    GATE_PASS=false
  else
    echo "  ✅ $file"
  fi
done

# Check env vars (critical)
if [ -z "$ALIBABA_DASHSCOPE_API_KEY" ]; then
  echo "  ⚠️  MISSING: ALIBABA_DASHSCOPE_API_KEY"
else
  echo "  ✅ ALIBABA_DASHSCOPE_API_KEY set"
fi

if [ -z "$SUPABASE_URL" ]; then
  echo "  ⚠️  MISSING: SUPABASE_URL"
else
  echo "  ✅ SUPABASE_URL set"
fi

# ============================================================
# PHASE 4: INTEGRITY CHECKS
# ============================================================
echo "🔍 Phase 4: Integrity checks..."

# Version alignment
GUARD_VERSION=$(grep '"version"' packages/guard-brasil/package.json 2>/dev/null | head -1 | grep -o '"[0-9.]*"' | tr -d '"' || echo "unknown")
echo "  Guard Brasil version: $GUARD_VERSION"

# Test count
TEST_COUNT=$(find packages/shared/src/__tests__ -name "*.test.ts" -o -name "*.spec.ts" 2>/dev/null | wc -l || echo "0")
echo "  Tests: $TEST_COUNT files"

# Type check
if npx tsc --noEmit 2>&1 | grep -q "error"; then
  echo "  ❌ Type errors detected"
  GATE_PASS=false
else
  echo "  ✅ TypeScript: 0 errors"
fi

# ============================================================
# PHASE 5: EXECUTIVE SUMMARY
# ============================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 EXECUTIVE SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Repository:     $REPO_NAME @ $BRANCH"
echo "Last Session:   P$LAST_SESSION"
echo "Uncommitted:    $UNCOMMITTED files"
echo ""
echo "📊 System State:"
echo "  • Tasks:      $(cat TASKS.md 2>/dev/null | grep -c '^- \[' || echo '?') done / $(cat TASKS.md 2>/dev/null | grep -c '^- ' || echo '?') total"
echo "  • Agents:     $AGENTS_COUNT registered"
echo "  • Job Reports: $JOB_REPORTS files ($CRITICAL_COUNT critical)"
echo "  • Memory:     $MEMORY_LINES lines in MEMORY.md"
echo ""
echo "🖥️  Infrastructure:"
echo "  • Disk:       $DISK"
echo "  • Memory:     $MEMORY"
echo "  • VPS:        $VPS_CONTAINERS containers running"
echo "  • API Status: $API_STATUS"
echo ""
echo "✅ Validation:  $([ "$GATE_PASS" = true ] && echo 'PASS' || echo 'FAIL')"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ============================================================
# PHASE 6: RECOMMENDATIONS
# ============================================================
if [ "$JOB_REPORTS" -gt 0 ] && [ "$CRITICAL_COUNT" -gt 0 ]; then
  echo "⚠️  $CRITICAL_COUNT critical issues from job reports:"
  grep -l "CRITICAL" /home/enio/egos/docs/jobs/*.md 2>/dev/null | head -3 | while read f; do
    echo "   • $(basename $f)"
  done
  echo ""
fi

if [ "$UNCOMMITTED" -gt 0 ]; then
  echo "📝 Uncommitted changes:"
  git status --short | head -3
  echo ""
fi

if [ "$GATE_PASS" = false ]; then
  echo "🚨 BLOCKER: Fix validation gates before proceeding"
  echo ""
fi

echo "💡 Next actions:"
echo "   1. Review blocked tasks in TASKS.md (P0 section)"
echo "   2. Check /home/enio/egos/docs/_current_handoffs/ for context"
echo "   3. Run: bun run typecheck && npm test"
echo ""

# Cleanup
rm -f /tmp/start_*

echo "✅ /start v6.0 complete"
