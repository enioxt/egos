#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# governance-propagate.sh — EGOS Kernel Rules Propagation v1.0
#
# Ensures ALL repos carry EGOS kernel rules as adapters.
# Safe to run multiple times (idempotent).
#
# Behavior:
#   - Repos WITH CLAUDE.md: prepend kernel reference block if missing
#   - Repos WITHOUT CLAUDE.md: create minimal adapter
#   - Repos WITHOUT .windsurfrules: create minimal adapter
#   - Updates ~/.egos/sync.sh REPOS array if repo is missing
#
# Usage:
#   bash scripts/governance-propagate.sh          # dry-run
#   bash scripts/governance-propagate.sh --exec   # apply changes
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

DRY_RUN=true
[[ "${1:-}" == "--exec" ]] && DRY_RUN=false

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

KERNEL_CLAUDE="$HOME/.claude/CLAUDE.md"
KERNEL_MARKER="# EGOS-KERNEL-PROPAGATED"
CHANGES=0

log()  { echo -e "${BLUE}[propagate]${NC} $*"; }
ok()   { echo -e "${GREEN}[✓]${NC} $*"; }
warn() { echo -e "${YELLOW}[~]${NC} $*"; }
err()  { echo -e "${RED}[✗]${NC} $*"; }
dry()  { echo -e "${YELLOW}[DRY-RUN]${NC} $*"; }

# ── All local repos that should carry EGOS rules ──
LOCAL_REPOS=(
  "$HOME/852"
  "$HOME/br-acc"
  "$HOME/carteira-livre"
  "$HOME/egos-inteligencia"
  "$HOME/egos-lab"
  "$HOME/forja"
  "$HOME/smartbuscas"
  "$HOME/santiago"
  "$HOME/commons"
  "$HOME/arch"
  "$HOME/egos-self"
  "$HOME/INPI"
)

# ── Kernel reference block injected at top of existing CLAUDE.md ──
kernel_header() {
  local repo_name="$1"
  cat <<EOF
${KERNEL_MARKER}: $(date +%Y-%m-%d)
<!-- AUTO-INJECTED by governance-propagate.sh — DO NOT EDIT THIS BLOCK MANUALLY -->
<!-- Kernel rules: ~/.claude/CLAUDE.md (always authoritative) -->
<!-- Domain rules: ~/.claude/egos-rules/*.md -->
<!-- Re-run: bash ~/egos/scripts/governance-propagate.sh --exec to update -->

> **EGOS Kernel rules apply to this repo.** See \`~/.claude/CLAUDE.md\` for full rules.
> Critical non-negotiables: no force-push main, no secret logging, no git add -A in agents.
> SSOT map: \`~/.claude/egos-rules/ssot-map.md\` | LLM routing: \`~/.claude/egos-rules/llm-routing.md\`

---

EOF
}

# ── Minimal CLAUDE.md adapter for repos without one ──
minimal_claude() {
  local repo_name="$1"
  local repo_path="$2"
  cat <<EOF
${KERNEL_MARKER}: $(date +%Y-%m-%d)
# CLAUDE.md — ${repo_name}

<!-- AUTO-GENERATED KERNEL ADAPTER by governance-propagate.sh -->
<!-- Kernel rules: ~/.claude/CLAUDE.md | Update: bash ~/egos/scripts/governance-propagate.sh --exec -->

> **EGOS Kernel rules apply.** Global rules at \`~/.claude/CLAUDE.md\` are always authoritative.
> Critical: no force-push main · no secret logging · no git add -A in agents
> SSOT: \`~/.claude/egos-rules/ssot-map.md\` | LLM: \`~/.claude/egos-rules/llm-routing.md\`

---

## Project: ${repo_name}

<!-- Add repo-specific context below this line -->
<!-- Runtime, architecture, key files, commands, conventions -->

EOF
}

# ── Minimal .windsurfrules adapter ──
minimal_windsurfrules() {
  local repo_name="$1"
  cat <<EOF
# .windsurfrules — ${repo_name}
${KERNEL_MARKER}: $(date +%Y-%m-%d)
# VERSION: 1.0.0 | MAX_LINES: 120 (HARD LIMIT)
# Extends: EGOS Kernel (~/.claude/CLAUDE.md) — kernel wins on conflict.
# Update: bash ~/egos/scripts/governance-propagate.sh --exec

## ⚡ PRIME DIRECTIVE
> EGOS kernel rules apply. Kernel is authoritative on all non-repo-specific matters.

## Kernel Rule Shortcuts (most critical)
- NEVER force-push main/master/production
- NEVER log/echo env var values or commit .env files
- NEVER git add -A in background agents (use specific files)
- COMMIT TASKS.md immediately after any edit
- SSOT-First: content goes to existing SSOT file, never create duplicate

## Repo: ${repo_name}
<!-- Add repo-specific Windsurf/Cascade rules below -->

EOF
}

echo ""
echo -e "${BOLD}═══ EGOS Governance Propagation ═══${NC}"
echo -e "Mode: $([ "$DRY_RUN" = "true" ] && echo "${YELLOW}DRY-RUN${NC} (pass --exec to apply)" || echo "${GREEN}EXEC${NC}")"
echo ""

# ── Process each repo ──
for REPO in "${LOCAL_REPOS[@]}"; do
  REPO_NAME=$(basename "$REPO")

  # Skip if directory doesn't exist
  if [[ ! -d "$REPO" ]]; then
    warn "Skipping $REPO_NAME (directory not found)"
    continue
  fi

  log "Processing: $REPO_NAME"

  # ── CLAUDE.md ──
  CLAUDE_FILE="$REPO/CLAUDE.md"
  if [[ -f "$CLAUDE_FILE" ]]; then
    if grep -q "$KERNEL_MARKER" "$CLAUDE_FILE" 2>/dev/null; then
      ok "  CLAUDE.md already has kernel marker"
    else
      warn "  CLAUDE.md exists but missing kernel marker — will prepend"
      if [[ "$DRY_RUN" = "false" ]]; then
        TMP=$(mktemp)
        kernel_header "$REPO_NAME" > "$TMP"
        cat "$CLAUDE_FILE" >> "$TMP"
        mv "$TMP" "$CLAUDE_FILE"
        ok "  CLAUDE.md updated (kernel header prepended)"
        CHANGES=$((CHANGES + 1))
      else
        dry "  Would prepend kernel header to $REPO_NAME/CLAUDE.md"
        CHANGES=$((CHANGES + 1))
      fi
    fi
  else
    warn "  CLAUDE.md missing — will create adapter"
    if [[ "$DRY_RUN" = "false" ]]; then
      minimal_claude "$REPO_NAME" "$REPO" > "$CLAUDE_FILE"
      ok "  CLAUDE.md created (minimal adapter)"
      CHANGES=$((CHANGES + 1))
    else
      dry "  Would create $REPO_NAME/CLAUDE.md (minimal adapter)"
      CHANGES=$((CHANGES + 1))
    fi
  fi

  # ── .windsurfrules ──
  WS_FILE="$REPO/.windsurfrules"
  if [[ -f "$WS_FILE" ]]; then
    if grep -q "$KERNEL_MARKER" "$WS_FILE" 2>/dev/null; then
      ok "  .windsurfrules already has kernel marker"
    else
      warn "  .windsurfrules exists but missing kernel marker — will prepend"
      if [[ "$DRY_RUN" = "false" ]]; then
        TMP=$(mktemp)
        # Prepend just the marker line + kernel pointer comment
        echo "${KERNEL_MARKER}: $(date +%Y-%m-%d)" > "$TMP"
        echo "# Extends: EGOS Kernel (~/.claude/CLAUDE.md) — kernel wins on conflict." >> "$TMP"
        echo "" >> "$TMP"
        cat "$WS_FILE" >> "$TMP"
        mv "$TMP" "$WS_FILE"
        ok "  .windsurfrules updated (kernel marker prepended)"
        CHANGES=$((CHANGES + 1))
      else
        dry "  Would prepend kernel marker to $REPO_NAME/.windsurfrules"
        CHANGES=$((CHANGES + 1))
      fi
    fi
  else
    warn "  .windsurfrules missing — will create adapter"
    if [[ "$DRY_RUN" = "false" ]]; then
      minimal_windsurfrules "$REPO_NAME" > "$WS_FILE"
      ok "  .windsurfrules created (minimal adapter)"
      CHANGES=$((CHANGES + 1))
    else
      dry "  Would create $REPO_NAME/.windsurfrules (minimal adapter)"
      CHANGES=$((CHANGES + 1))
    fi
  fi

  echo ""
done

# ── Update ~/.egos/sync.sh REPOS if egos-inteligencia is missing ──
SYNC_FILE="$HOME/.egos/sync.sh"
if [[ -f "$SYNC_FILE" ]]; then
  if ! grep -q "egos-inteligencia" "$SYNC_FILE"; then
    warn "~/.egos/sync.sh REPOS array missing egos-inteligencia"
    if [[ "$DRY_RUN" = "false" ]]; then
      sed -i 's|"$HOME/arch".*# EGOS governance bootstrap|"$HOME/arch"       # EGOS governance bootstrap\n  "$HOME/egos-inteligencia"  # EGOS-Inteligência (Intelink)|' "$SYNC_FILE"
      ok "~/.egos/sync.sh updated: egos-inteligencia added"
      CHANGES=$((CHANGES + 1))
    else
      dry "Would add egos-inteligencia to ~/.egos/sync.sh REPOS"
    fi
  else
    ok "~/.egos/sync.sh already includes egos-inteligencia"
  fi
fi

# ── Summary ──
echo ""
echo -e "${BOLD}═══ Summary ═══${NC}"
if [[ "$DRY_RUN" = "true" ]]; then
  echo -e "  $CHANGES change(s) would be applied. Run with ${GREEN}--exec${NC} to apply."
else
  echo -e "  ${GREEN}$CHANGES change(s) applied.${NC}"
fi
echo ""
