#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# workflow-sync-check.sh — EGOS Workflow Inheritance Drift Detector
#
# TASK: EGOS-068
# PURPOSE: For each repo in the mesh, verify that ~/.egos/workflows/ files are
#          properly symlinked. Reports synced | stale | missing per workflow.
#
# EXIT CODES:
#   0 — all canonical workflows are present (synced or symlinked)
#   1 — one or more repos are MISSING all canonical workflows entirely
#
# Usage:
#   bash egos/scripts/workflow-sync-check.sh
#   bash egos/scripts/workflow-sync-check.sh --json   (machine-readable output)
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

EGOS_HOME="$HOME/.egos"
WORKFLOWS_DIR="$EGOS_HOME/workflows"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

JSON_MODE=false
if [[ "${1:-}" == "--json" ]]; then
  JSON_MODE=true
fi

# ── Registered repos in the mesh ──
REPOS=(
  "$HOME/852"
  "$HOME/egos-lab"
  "$HOME/carteira-livre"
  "$HOME/br-acc"
  "$HOME/forja"
  "$HOME/santiago"
  "$HOME/commons"
  "$HOME/INPI"
  "$HOME/smartbuscas"
)

# ── Canonical workflow list ──
CANONICAL_WORKFLOWS=()
while IFS= read -r -d '' f; do
  CANONICAL_WORKFLOWS+=("$(basename "$f")")
done < <(find "$WORKFLOWS_DIR" -maxdepth 1 -name "*.md" -print0 | sort -z)

CANONICAL_COUNT=${#CANONICAL_WORKFLOWS[@]}

# ── Counters ──
TOTAL_REPOS=0
REPOS_CLEAN=0
REPOS_STALE=0
REPOS_MISSING=0
HAS_CRITICAL_MISSING=false

declare -a JSON_LINES

print_header() {
  if ! $JSON_MODE; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║          EGOS Workflow Inheritance Drift Check — EGOS-068       ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Canonical source: $WORKFLOWS_DIR"
    echo "Canonical workflows ($CANONICAL_COUNT): ${CANONICAL_WORKFLOWS[*]}"
    echo ""
    echo "──────────────────────────────────────────────────────────────────"
  fi
}

check_repo() {
  local repo="$1"
  local repo_name
  repo_name=$(basename "$repo")
  local agent_dir="$repo/.agent/workflows"
  local windsurf_dir="$repo/.windsurf/workflows"

  TOTAL_REPOS=$((TOTAL_REPOS + 1))

  if [ ! -d "$repo" ]; then
    if ! $JSON_MODE; then
      echo -e "  ${YELLOW}⚠${NC}  $repo_name — repo directory not found, skipping"
    fi
    return
  fi

  # Determine which workflow dir to check (prefer .agent, fall back to .windsurf)
  local wf_dir=""
  if [ -d "$agent_dir" ]; then
    wf_dir="$agent_dir"
  elif [ -d "$windsurf_dir" ]; then
    wf_dir="$windsurf_dir"
  fi

  if ! $JSON_MODE; then
    echo -e "\n  ${BLUE}▶ $repo_name${NC}  ($repo)"
  fi

  local synced=0
  local stale=0
  local missing=0
  local stale_details=()
  local missing_details=()

  if [ -z "$wf_dir" ]; then
    # No workflow directory at all — all missing
    missing=$CANONICAL_COUNT
    missing_details=("${CANONICAL_WORKFLOWS[@]}")
    REPOS_MISSING=$((REPOS_MISSING + 1))
    HAS_CRITICAL_MISSING=true

    if ! $JSON_MODE; then
      echo -e "    ${RED}MISSING${NC}  — no .agent/workflows or .windsurf/workflows directory"
      echo -e "    ${RED}         Missing all $CANONICAL_COUNT canonical workflows${NC}"
      echo -e "    ${YELLOW}Fix:${NC} Add '$repo_name' to ~/.egos/sync.sh REPOS array and run sync"
    fi
  else
    for wf in "${CANONICAL_WORKFLOWS[@]}"; do
      local target="$wf_dir/$wf"
      local canonical="$WORKFLOWS_DIR/$wf"

      if [ ! -e "$target" ]; then
        missing=$((missing + 1))
        missing_details+=("$wf")
      elif [ -L "$target" ]; then
        # Symlink — check it points to canonical
        local link_target
        link_target=$(readlink -f "$target" 2>/dev/null || echo "BROKEN")
        if [ "$link_target" = "$canonical" ]; then
          synced=$((synced + 1))
        else
          # Symlink pointing somewhere else
          stale=$((stale + 1))
          stale_details+=("$wf → $(readlink "$target")")
        fi
      else
        # Real file (not a symlink) — compare content
        local diff_lines
        diff_lines=$(diff -u "$canonical" "$target" 2>/dev/null | wc -l | tr -d ' ' || echo "999")
        if [ "$diff_lines" -eq 0 ]; then
          # Identical content but real file — could be converted to symlink
          synced=$((synced + 1))
          stale=$((stale + 1))
          stale_details+=("$wf (real file, identical content — convert to symlink)")
        else
          stale=$((stale + 1))
          stale_details+=("$wf (real file, $diff_lines diff lines from canonical)")
        fi
      fi
    done

    if [ "$missing" -gt 0 ] && [ "$synced" -eq 0 ] && [ "$stale" -eq 0 ]; then
      REPOS_MISSING=$((REPOS_MISSING + 1))
      HAS_CRITICAL_MISSING=true
    elif [ "$stale" -gt 0 ] || [ "$missing" -gt 0 ]; then
      REPOS_STALE=$((REPOS_STALE + 1))
    else
      REPOS_CLEAN=$((REPOS_CLEAN + 1))
    fi

    if ! $JSON_MODE; then
      echo -e "    Workflow dir: $wf_dir"
      echo -e "    Synced:  ${GREEN}$synced${NC}/$CANONICAL_COUNT"

      if [ "${#stale_details[@]}" -gt 0 ]; then
        echo -e "    Stale:   ${YELLOW}$stale${NC}"
        for detail in "${stale_details[@]}"; do
          echo -e "      ${YELLOW}~${NC}  $detail"
        done
      else
        echo -e "    Stale:   ${GREEN}0${NC}"
      fi

      if [ "${#missing_details[@]}" -gt 0 ]; then
        echo -e "    Missing: ${RED}$missing${NC}"
        for detail in "${missing_details[@]}"; do
          echo -e "      ${RED}✗${NC}  $detail"
        done
        echo -e "    ${YELLOW}Fix:${NC} Run ~/.egos/sync.sh to install missing workflows"
      else
        echo -e "    Missing: ${GREEN}0${NC}"
      fi

      # Overall status
      if [ "$synced" -eq "$CANONICAL_COUNT" ] && [ "$stale" -eq 0 ]; then
        echo -e "    Status:  ${GREEN}CLEAN${NC}"
      elif [ "$missing" -gt 0 ] && [ "$synced" -eq 0 ] && [ "$stale" -eq 0 ]; then
        echo -e "    Status:  ${RED}MISSING (critical — run sync)${NC}"
      else
        echo -e "    Status:  ${YELLOW}STALE (run sync to fix)${NC}"
      fi
    fi
  fi

  # Build JSON entry
  if $JSON_MODE; then
    local status_tag="clean"
    if [ -z "$wf_dir" ]; then
      status_tag="missing_all"
    elif [ "$synced" -eq "$CANONICAL_COUNT" ] && [ "$stale" -eq 0 ]; then
      status_tag="clean"
    elif [ "$missing" -gt 0 ] && [ "$synced" -eq 0 ]; then
      status_tag="missing"
    else
      status_tag="stale"
    fi
    JSON_LINES+=("{\"repo\":\"$repo_name\",\"path\":\"$repo\",\"wf_dir\":\"${wf_dir:-null}\",\"synced\":$synced,\"stale\":$stale,\"missing\":$missing,\"status\":\"$status_tag\"}")
  fi
}

# ── Main ──
print_header

for repo in "${REPOS[@]}"; do
  check_repo "$repo"
done

if ! $JSON_MODE; then
  echo ""
  echo "──────────────────────────────────────────────────────────────────"
  echo -e "Summary:"
  echo -e "  Total repos checked: $TOTAL_REPOS"
  echo -e "  ${GREEN}Clean:${NC}   $REPOS_CLEAN"
  echo -e "  ${YELLOW}Stale:${NC}   $REPOS_STALE  (run ~/.egos/sync.sh to fix)"
  echo -e "  ${RED}Missing:${NC} $REPOS_MISSING  (add to ~/.egos/sync.sh REPOS + run sync)"
  echo ""
  if $HAS_CRITICAL_MISSING; then
    echo -e "${RED}RESULT: FAIL — one or more repos are missing all canonical workflows.${NC}"
    echo -e "Run: ~/.egos/sync.sh"
  else
    echo -e "${GREEN}RESULT: PASS — all repos have canonical workflows (some may be stale).${NC}"
    if [ "$REPOS_STALE" -gt 0 ]; then
      echo -e "       Run ~/.egos/sync.sh to convert real files to symlinks."
    fi
  fi
  echo ""
else
  # JSON output
  echo "["
  for i in "${!JSON_LINES[@]}"; do
    if [ $i -lt $((${#JSON_LINES[@]} - 1)) ]; then
      echo "  ${JSON_LINES[$i]},"
    else
      echo "  ${JSON_LINES[$i]}"
    fi
  done
  echo "]"
fi

# Exit code
if $HAS_CRITICAL_MISSING; then
  exit 1
else
  exit 0
fi
