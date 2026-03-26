#!/bin/bash
# ═══════════════════════════════════════════════════════════
# EGOS Sync All Leaf Repos — Phase 2 Integration
#
# Synchronizes all leaf repositories with kernel governance.
# Runs governance sync + checks drift on each repo.
#
# Usage:
#   ./scripts/sync-all-leaf-repos.sh          # dry-run (default)
#   ./scripts/sync-all-leaf-repos.sh --exec   # apply all syncs
#   ./scripts/sync-all-leaf-repos.sh --check  # CI mode (fail if drift)
# ═══════════════════════════════════════════════════════════

set -e

MODE="${1:---dry}"

LEAF_REPOS=(
  "852"
  "INPI"
  "br-acc"
  "carteira-livre"
  "egos-lab"
  "egos-self"
  "forja"
  "policia"
  "santiago"
  "smartbuscas"
  "commons"
)

KERNEL="/home/enio/egos"
HOME_EGOS="$HOME/.egos"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "═══════════════════════════════════════════════════════════"
echo "🔄 EGOS Sync All Leaf Repos — Phase 2"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Mode: $MODE"
echo "Kernel: $KERNEL"
echo "Home: $HOME_EGOS"
echo "Repos: ${#LEAF_REPOS[@]}"
echo ""

# ── Step 1: Verify Kernel ──
echo -e "${BLUE}📋 Step 1: Verifying kernel governance...${NC}"
if [ -d "$KERNEL/.guarani" ]; then
  echo -e "   ${GREEN}✅${NC} Kernel .guarani exists"
else
  echo -e "   ${RED}❌${NC} MISSING: $KERNEL/.guarani"
  exit 1
fi

# ── Step 2: Sync Each Leaf ──
echo ""
echo -e "${BLUE}📋 Step 2: Syncing leaf repositories...${NC}"
echo ""

TOTAL_REPOS=${#LEAF_REPOS[@]}
SYNCED=0
DRIFTED=0
FAILED=0

for repo in "${LEAF_REPOS[@]}"; do
  REPO_PATH="/home/enio/$repo"

  if [ ! -d "$REPO_PATH" ]; then
    echo -e "   ${YELLOW}⏭️${NC}  $repo — NOT FOUND (skipped)"
    continue
  fi

  echo -e "   ${BLUE}📂 $repo${NC}"

  # Check if repo has package.json
  if [ ! -f "$REPO_PATH/package.json" ]; then
    echo -e "      ${YELLOW}⚠️${NC}  No package.json (not a JS project, skipped)"
    continue
  fi

  # Check if governance commands exist
  if ! grep -q "governance:check" "$REPO_PATH/package.json"; then
    echo -e "      ${YELLOW}⚠️${NC}  No governance commands in package.json"
    echo -e "         ${YELLOW}→${NC}  Adding commands..."

    # Add governance commands (simple sed-based patch)
    if [ "$MODE" = "--exec" ]; then
      cd "$REPO_PATH"
      npm set-script governance:sync "sh \$HOME/egos/scripts/governance-sync.sh --dry" || true
      npm set-script governance:sync:exec "sh \$HOME/egos/scripts/governance-sync.sh --exec --propagate" || true
      npm set-script governance:sync:local "sh \$HOME/egos/scripts/governance-sync.sh --exec --no-propagate" || true
      npm set-script governance:check "sh \$HOME/egos/scripts/governance-sync.sh --check" || true
    else
      echo -e "         ${YELLOW}→${NC}  (dry-run: not applied)"
    fi
  fi

  # Run governance sync
  cd "$REPO_PATH"

  if [ "$MODE" = "--check" ]; then
    if npm run governance:check 2>/dev/null; then
      echo -e "      ${GREEN}✅${NC}  0 drift"
      ((SYNCED++))
    else
      echo -e "      ${RED}❌${NC}  Drift detected"
      ((DRIFTED++))
    fi
  else
    # --dry or --exec
    if npm run governance:sync:local 2>/dev/null; then
      echo -e "      ${GREEN}✅${NC}  Synced"
      ((SYNCED++))
    else
      echo -e "      ${RED}❌${NC}  Sync failed"
      ((FAILED++))
    fi
  fi
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo -e "${GREEN}Summary:${NC}"
echo "   ✅ Synced: $SYNCED"
echo "   ⚠️  Drifted: $DRIFTED"
echo "   ❌ Failed: $FAILED"
echo ""

# ── Step 3: Final Kernel Check ──
echo -e "${BLUE}📋 Step 3: Final kernel governance check...${NC}"
cd "$KERNEL"

if npm run governance:check 2>/dev/null; then
  echo -e "   ${GREEN}✅${NC} Kernel is clean"
else
  echo -e "   ${YELLOW}⚠️${NC}  Kernel has drift (this is expected, run kernel sync separately)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"

if [ "$MODE" = "--check" ] && [ $DRIFTED -gt 0 ]; then
  echo -e "${RED}❌ CI FAIL: $DRIFTED repos have drift${NC}"
  exit 1
elif [ "$FAILED" -gt 0 ]; then
  echo -e "${RED}❌ ERROR: $FAILED repos failed${NC}"
  exit 1
else
  echo -e "${GREEN}✅ Phase 2 Sync Complete!${NC}"
  echo ""
  echo "Next steps:"
  echo "  1. Commit changes: git add -A && git commit -m 'chore: sync governance from kernel'"
  echo "  2. Test one repo: cd /home/enio/852 && npm run governance:check"
  echo "  3. Run kernel propagation: cd /home/enio/egos && bun run governance:sync:exec"
  exit 0
fi
