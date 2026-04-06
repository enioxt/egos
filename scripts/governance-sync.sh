#!/bin/sh
# ═══════════════════════════════════════════════════════════
# EGOS Governance Sync — Upstream Push
#
# Pushes governance files from egos/ (canonical kernel)
# to ~/.egos/guarani/ (shared home), then optionally
# triggers ~/.egos/sync.sh to propagate to all leaf repos.
#
# Usage:
#   ./scripts/governance-sync.sh          # dry-run (default)
#   ./scripts/governance-sync.sh --exec   # actually sync
#   ./scripts/governance-sync.sh --check  # CI mode (exit 1 if drift)
#   ./scripts/governance-sync.sh --exec --propagate  # sync + auto-propagate to leaf repos
# ═══════════════════════════════════════════════════════════

if [ -d "${PWD}/.guarani" ]; then
  DEFAULT_KERNEL="$PWD"
else
  DEFAULT_KERNEL="$HOME/egos"
fi

EGOS_KERNEL="${EGOS_KERNEL:-$DEFAULT_KERNEL}"
EGOS_HOME="${EGOS_HOME:-$HOME/.egos}"
MODE="--dry"
PROPAGATE_MODE="prompt"
for arg in "$@"; do
  case "$arg" in
    --dry|--exec|--check)
      MODE="$arg"
      ;;
    --propagate|--yes|--auto-propagate)
      PROPAGATE_MODE="yes"
      ;;
    --no-propagate)
      PROPAGATE_MODE="no"
      ;;
  esac
done
if [ "${EGOS_AUTO_PROPAGATE:-0}" = "1" ]; then
  PROPAGATE_MODE="yes"
fi
WORKFLOWS_SRC="$EGOS_KERNEL/.windsurf/workflows"
WORKFLOWS_DST="$EGOS_HOME/workflows"
DOCS_SRC="$EGOS_KERNEL/docs"
DOCS_DST="$EGOS_HOME/docs"
HOOKS_SRC="$EGOS_KERNEL/.egos/hooks"
HOOKS_DST="$EGOS_HOME/hooks"
HOME_SYNC_SRC="$EGOS_KERNEL/.egos/sync.sh"
HOME_SYNC_DST="$EGOS_HOME/sync.sh"
HOME_META_SRC="$EGOS_KERNEL/.egos"
HOME_META_FILES="README.md manifest.json"
CANONICAL_DOCS="CAPABILITY_REGISTRY.md SSOT_REGISTRY.md ECOSYSTEM_CLASSIFICATION_REGISTRY.md modules/CHATBOT_SSOT.md"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

DRIFT_COUNT=0
SYNC_COUNT=0
OK_COUNT=0

echo "EGOS Governance Sync"
echo "Kernel: $EGOS_KERNEL"
echo "Home:   $EGOS_HOME"
echo "Mode:   $MODE"
echo "---"

if [ ! -d "$EGOS_KERNEL/.guarani" ]; then
  printf "${RED}ERROR:${NC} %s/.guarani not found\n" "$EGOS_KERNEL"
  exit 1
fi

if [ ! -d "$EGOS_HOME/guarani" ]; then
  printf "${YELLOW}WARN:${NC} %s/guarani not found, creating...\n" "$EGOS_HOME"
  mkdir -p "$EGOS_HOME/guarani"
fi

if [ -d "$WORKFLOWS_SRC" ] && [ ! -d "$WORKFLOWS_DST" ]; then
  printf "${YELLOW}WARN:${NC} %s/workflows not found, creating...\n" "$EGOS_HOME"
  mkdir -p "$WORKFLOWS_DST"
fi

if [ -d "$HOOKS_SRC" ] && [ ! -d "$HOOKS_DST" ]; then
  printf "${YELLOW}WARN:${NC} %s/hooks not found, creating...\n" "$EGOS_HOME"
  mkdir -p "$HOOKS_DST"
fi

if [ -d "$DOCS_SRC" ] && [ ! -d "$DOCS_DST" ]; then
  printf "${YELLOW}WARN:${NC} %s/docs not found, creating...\n" "$EGOS_HOME"
  mkdir -p "$DOCS_DST/modules"
fi

# ── Compare each file in kernel .guarani/ with ~/.egos/guarani/ ──
compare_file() {
  rel_path="$1"
  src_root="$2"
  dst_root="$3"
  label="$4"
  src="$src_root/$rel_path"
  dst="$dst_root/$rel_path"

  if [ ! -f "$dst" ]; then
    printf "  ${YELLOW}NEW${NC}   %s: %s\n" "$label" "$rel_path"
    DRIFT_COUNT=$((DRIFT_COUNT + 1))
    if [ "$MODE" = "--exec" ]; then
      dst_dir=$(dirname "$dst")
      mkdir -p "$dst_dir"
      cp "$src" "$dst"
      SYNC_COUNT=$((SYNC_COUNT + 1))
      printf "        ${GREEN}-> copied${NC}\n"
    fi
  elif ! diff -q "$src" "$dst" > /dev/null 2>&1; then
    printf "  ${YELLOW}DRIFT${NC} %s: %s\n" "$label" "$rel_path"
    DRIFT_COUNT=$((DRIFT_COUNT + 1))
    if [ "$MODE" = "--exec" ]; then
      cp "$src" "$dst"
      SYNC_COUNT=$((SYNC_COUNT + 1))
      printf "        ${GREEN}-> updated${NC}\n"
    fi
  else
    OK_COUNT=$((OK_COUNT + 1))
  fi
}

# Walk all files in kernel .guarani/ using temp file to avoid subshell
TMPLIST=$(mktemp)
find "$EGOS_KERNEL/.guarani" -type f | sort > "$TMPLIST"

while read -r filepath; do
  rel=$(echo "$filepath" | sed "s|$EGOS_KERNEL/.guarani/||")
  compare_file "$rel" "$EGOS_KERNEL/.guarani" "$EGOS_HOME/guarani" "guarani"
done < "$TMPLIST"
rm -f "$TMPLIST"

if [ -d "$WORKFLOWS_SRC" ]; then
  TMPLIST=$(mktemp)
  find "$WORKFLOWS_SRC" -type f | sort > "$TMPLIST"

  while read -r filepath; do
    rel=$(echo "$filepath" | sed "s|$WORKFLOWS_SRC/||")
    compare_file "$rel" "$WORKFLOWS_SRC" "$WORKFLOWS_DST" "workflow"
  done < "$TMPLIST"
  rm -f "$TMPLIST"
fi

if [ -d "$HOOKS_SRC" ]; then
  TMPLIST=$(mktemp)
  find "$HOOKS_SRC" -type f | sort > "$TMPLIST"

  while read -r filepath; do
    rel=$(echo "$filepath" | sed "s|$HOOKS_SRC/||")
    compare_file "$rel" "$HOOKS_SRC" "$HOOKS_DST" "hook"
  done < "$TMPLIST"
  rm -f "$TMPLIST"
fi

if [ -f "$HOME_SYNC_SRC" ]; then
  compare_file "sync.sh" "$EGOS_KERNEL/.egos" "$EGOS_HOME" "home"
fi

for rel in $HOME_META_FILES; do
  if [ -f "$HOME_META_SRC/$rel" ]; then
    compare_file "$rel" "$HOME_META_SRC" "$EGOS_HOME" "home"
  fi
done

for rel in $CANONICAL_DOCS; do
  if [ -f "$DOCS_SRC/$rel" ]; then
    compare_file "$rel" "$DOCS_SRC" "$DOCS_DST" "doc"
  fi
done

echo ""
echo "---"
printf "OK: %d | Drift: %d | Synced: %d\n" "$OK_COUNT" "$DRIFT_COUNT" "$SYNC_COUNT"

if [ "$MODE" = "--check" ] && [ "$DRIFT_COUNT" -gt 0 ]; then
  printf "${RED}CI FAIL:${NC} %d files drifted from kernel\n" "$DRIFT_COUNT"
  exit 1
fi

# KB-008: Auto-compile Knowledge Base wiki after governance check
if [ "$MODE" = "--exec" ] || [ "$MODE" = "--check" ]; then
  echo ""
  printf "${BLUE}[KB-008] Wiki Knowledge Base — compiling...${NC}\n"
  if bun wiki:compile --quiet 2>/dev/null; then
    printf "${GREEN}✅ wiki:compile complete${NC}\n"
  else
    printf "${YELLOW}⚠️  wiki:compile skipped (not configured or no sources)${NC}\n"
  fi
fi

if [ "$MODE" = "--exec" ] && [ "$SYNC_COUNT" -gt 0 ]; then
  echo ""
  printf "${GREEN}Synced %d files to ~/.egos/guarani/, ~/.egos/workflows/, and ~/.egos/docs/${NC}\n" "$SYNC_COUNT"
  chmod +x "$HOME_SYNC_DST" 2>/dev/null || true
  if [ -d "$HOOKS_DST" ]; then
    find "$HOOKS_DST" -type f -exec chmod +x {} \; 2>/dev/null || true
  fi
  echo ""
  if [ -x "$EGOS_HOME/sync.sh" ]; then
    case "$PROPAGATE_MODE" in
      yes)
        "$EGOS_HOME/sync.sh"
        ;;
      no)
        printf "Skipping leaf propagation (${BLUE}--no-propagate${NC}).\n"
        ;;
      *)
        if [ -t 0 ]; then
          printf "Run ${BLUE}~/.egos/sync.sh${NC} to propagate to leaf repos? [y/N] "
          read -r answer
          if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
            "$EGOS_HOME/sync.sh"
          fi
        else
          printf "Non-interactive shell detected. Skipping leaf propagation; use ${BLUE}--propagate${NC} or ${BLUE}EGOS_AUTO_PROPAGATE=1${NC}.\n"
        fi
        ;;
    esac
  fi
fi

if [ "$MODE" = "--dry" ]; then
  echo ""
  echo "Dry-run complete. Use --exec to apply, --check for CI."
fi
