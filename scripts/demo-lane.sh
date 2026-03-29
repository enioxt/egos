#!/bin/sh
# demo-lane.sh — Reproducible demo lane for meetings
# EGOS-118 | docs/NARRATIVE_KIT.md
#
# Usage:
#   sh scripts/demo-lane.sh           # full demo
#   sh scripts/demo-lane.sh --check   # pre-meeting checklist only
#   sh scripts/demo-lane.sh --offline # skip network-dependent checks

set -eu

MODE="${1:-full}"
PASS=0
FAIL=0

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  EGOS Guard Brasil — Demo Lane                              ║"
echo "║  Brazilian AI Safety Layer | @egos/guard-brasil v0.1.0      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

check() {
  label="$1"; cmd="$2"
  printf "  %-50s" "$label"
  if eval "$cmd" >/dev/null 2>&1; then
    echo "✅"
    PASS=$((PASS + 1))
  else
    echo "❌  FAIL"
    FAIL=$((FAIL + 1))
  fi
}

echo "── Pre-flight checks ────────────────────────────────────────────"
check "TypeScript — 0 errors"                "bun run typecheck"
check "Guard Brasil tests — 15/15 pass"      "bun test packages/guard-brasil/src/guard.test.ts --bail"
check "Agent lint — all contracts pass"      "bun run agent:lint"
check "Package version exists"               "grep '\"version\"' packages/guard-brasil/package.json"
check "Demo file exists"                     "test -f packages/guard-brasil/src/demo.ts"
echo ""

if [ "$MODE" = "--check" ]; then
  echo "── Checklist summary ────────────────────────────────────────────"
  echo "  Pass: $PASS | Fail: $FAIL"
  if [ "$FAIL" -gt 0 ]; then
    echo ""
    echo "  ⚠️  Fix failures before the meeting."
    exit 1
  else
    echo ""
    echo "  ✅ Ready for demo."
  fi
  exit 0
fi

echo "── Live demo ────────────────────────────────────────────────────"
echo ""
echo "  Running: bun run packages/guard-brasil/src/demo.ts"
echo ""
bun run packages/guard-brasil/src/demo.ts || {
  echo ""
  echo "  ❌ Demo script failed. Run manually to debug:"
  echo "     bun run packages/guard-brasil/src/demo.ts"
  exit 1
}
echo ""

echo "── Key talking points ───────────────────────────────────────────"
echo ""
echo "  1. PROBLEM: Generic AI tools miss CPF/MASP/REDS — Brazilian gov IDs"
echo "  2. SOLUTION: guard.inspect(llmOutput) → safe output in one call"
echo "  3. LAYERS: ATRiAN (ethics) + PII Scanner + Public Guard + Evidence Chain"
echo "  4. PROOF: 15 tests passing, br-acc in production (police/judicial AI)"
echo "  5. INSTALL: npm install @egos/guard-brasil  (free, MIT)"
echo "  6. PAID: REST API + dashboard + audit logs → R\$199/mo"
echo ""

echo "── Fallback (offline) ───────────────────────────────────────────"
echo ""
echo "  If live demo fails, show:"
echo "  - packages/guard-brasil/README.md (code examples)"
echo "  - packages/guard-brasil/src/guard.test.ts (15 test scenarios)"
echo "  - docs/NARRATIVE_KIT.md (pitch + proof checklist)"
echo ""
echo "── Summary ──────────────────────────────────────────────────────"
echo "  Pass: $PASS | Fail: $FAIL"
if [ "$FAIL" -eq 0 ]; then
  echo "  ✅ Demo lane complete — you're ready."
else
  echo "  ⚠️  $FAIL check(s) failed — review before presenting."
fi
echo ""
