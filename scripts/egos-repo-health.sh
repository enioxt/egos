#!/bin/bash
# ═══════════════════════════════════════════════════════════
# EGOS Repo Health — Cross-Repo Git Status Dashboard
#
# Detects uncommitted changes, unpushed commits, and secrets
# across all EGOS repos to prevent stale file propagation.
#
# Usage:
#   bash scripts/egos-repo-health.sh           # status check
#   bash scripts/egos-repo-health.sh --push    # auto-push clean repos
#   bash scripts/egos-repo-health.sh --secrets # run gitleaks on all repos
# ═══════════════════════════════════════════════════════════

set -e

MODE="${1:-}"

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

KERNEL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

REPOS=(
  "$KERNEL_DIR"
  "/home/enio/852"
  "/home/enio/carteira-livre"
  "/home/enio/br-acc"
  "/home/enio/egos-lab"
  "/home/enio/smartbuscas"
  "/home/enio/INPI"
  "/home/enio/policia"
  "/home/enio/santiago"
  "/home/enio/forja"
  "/home/enio/commons"
)

# Counters
TOTAL=0
CLEAN=0
DIRTY=0
BEHIND=0

echo ""
printf "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════╗${NC}\n"
printf "${BOLD}${CYAN}║         EGOS Cross-Repo Health Dashboard                 ║${NC}\n"
printf "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════╝${NC}\n"
echo ""

for repo in "${REPOS[@]}"; do
  [ ! -d "$repo/.git" ] && continue

  name=$(basename "$repo")
  TOTAL=$((TOTAL + 1))

  # Get statuses
  uncommitted=$(git -C "$repo" status --short 2>/dev/null | grep -v "^?" | wc -l | tr -d ' ')
  untracked=$(git -C "$repo" status --short 2>/dev/null | grep "^?" | wc -l | tr -d ' ')
  unpushed=$(git -C "$repo" log --oneline @{u}..HEAD 2>/dev/null | wc -l | tr -d ' ')
  branch=$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "?")
  last_commit=$(git -C "$repo" log -1 --format="%cr" 2>/dev/null || echo "?")

  if [ "$uncommitted" -eq 0 ] && [ "$unpushed" -eq 0 ]; then
    CLEAN=$((CLEAN + 1))
    status_icon="${GREEN}✅${NC}"
    status_text="${GREEN}clean${NC}"
  else
    DIRTY=$((DIRTY + 1))
    status_icon="${YELLOW}⚠️ ${NC}"
    status_text="${YELLOW}needs attention${NC}"
  fi

  printf "  ${status_icon} ${BOLD}%-18s${NC} [%s] last: %s\n" "$name" "$branch" "$last_commit"

  if [ "$uncommitted" -gt 0 ]; then
    printf "     ${YELLOW}↳ %d modified/staged file(s)${NC}\n" "$uncommitted"
    git -C "$repo" status --short 2>/dev/null | grep -v "^?" | head -5 | while IFS= read -r line; do
      printf "       %s\n" "$line"
    done
    [ "$uncommitted" -gt 5 ] && printf "       ... and %d more\n" "$((uncommitted - 5))"
  fi

  if [ "$untracked" -gt 0 ]; then
    printf "     ${CYAN}↳ %d untracked file(s)${NC}\n" "$untracked"
    git -C "$repo" status --short 2>/dev/null | grep "^?" | head -3 | while IFS= read -r line; do
      printf "       %s\n" "$line"
    done
    [ "$untracked" -gt 3 ] && printf "       ... and %d more\n" "$((untracked - 3))"
  fi

  if [ "$unpushed" -gt 0 ]; then
    BEHIND=$((BEHIND + 1))
    printf "     ${RED}↳ %d unpushed commit(s)${NC}\n" "$unpushed"
    git -C "$repo" log --oneline @{u}..HEAD 2>/dev/null | head -3 | while IFS= read -r line; do
      printf "       %s\n" "$line"
    done
  fi

  # Secrets scan on dirty repos
  if [ "$MODE" = "--secrets" ] && [ "$uncommitted" -gt 0 ]; then
    if command -v gitleaks >/dev/null 2>&1; then
      printf "     🔐 Scanning for secrets...\n"
      if ! git -C "$repo" diff --cached | gitleaks detect --pipe --no-banner 2>/dev/null; then
        printf "     ${RED}❌ SECRETS FOUND — do not push!${NC}\n"
      else
        printf "     ${GREEN}✓ No secrets in staged changes${NC}\n"
      fi
    fi
  fi
done

echo ""
printf "${BOLD}═══════════════════════════════════════════════════${NC}\n"
printf "  Total repos: ${BOLD}%d${NC} | " "$TOTAL"
printf "${GREEN}Clean: %d${NC} | " "$CLEAN"
printf "${YELLOW}Needs attention: %d${NC} | " "$DIRTY"
printf "${RED}Unpushed: %d${NC}\n" "$BEHIND"
printf "${BOLD}═══════════════════════════════════════════════════${NC}\n"

if [ "$DIRTY" -gt 0 ]; then
  echo ""
  printf "${YELLOW}⚠️  Action required: %d repo(s) have uncommitted changes.${NC}\n" "$DIRTY"
  printf "   Risk: Stale files could be propagated via install scripts.\n"
  printf "   Run: ${BOLD}bash scripts/egos-repo-health.sh --secrets${NC} to scan for leaked secrets.\n"
fi

echo ""

# Exit non-zero if any repos are dirty (useful for CI)
[ "$DIRTY" -gt 0 ] && exit 1 || exit 0
