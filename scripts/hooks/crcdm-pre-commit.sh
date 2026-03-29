#!/bin/sh
# EGOS CRCDM Pre-Commit Hook
# Detects changes BEFORE they are committed, creates DAG node
# Part of Cross-Repo Change Detection Mesh (CRCDM)

set -eu

CRCDM_ROOT="${HOME}/.egos/crcdm"
HOOK_NAME="pre-commit"
REPO_PATH="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
REPO_NAME="$(basename "$REPO_PATH")"

echo "🔍 CRCDM [$HOOK_NAME] — Analyzing changes in $REPO_NAME..."

# Ensure CRCDM is initialized
mkdir -p "${CRCDM_ROOT}/logs"
mkdir -p "${CRCDM_ROOT}/dag"
mkdir -p "${CRCDM_ROOT}/state"
mkdir -p "${CRCDM_ROOT}/notifications"

# Get current branch and state
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
STAGED_FILES="$(git diff --cached --name-only 2>/dev/null || true)"
STAGED_COUNT="$(echo "$STAGED_FILES" | grep -c . 2>/dev/null || echo '0')"

if [ "$STAGED_COUNT" -eq 0 ]; then
  echo "  ℹ️ No staged files to analyze"
  exit 0
fi

# Security gate — gitleaks + staged diff fallback
GITLEAKS_CONFIG=""
if [ -f "$REPO_PATH/.gitleaks.toml" ]; then
  GITLEAKS_CONFIG="$REPO_PATH/.gitleaks.toml"
elif [ -f "$HOME/egos/.gitleaks.toml" ]; then
  GITLEAKS_CONFIG="$HOME/egos/.gitleaks.toml"
fi

if command -v gitleaks >/dev/null 2>&1; then
  echo "  🔐 Secret scan: gitleaks"
  if [ -n "$GITLEAKS_CONFIG" ]; then
    gitleaks protect --staged --no-banner --config "$GITLEAKS_CONFIG" || {
      echo "❌ BLOCKED: Secrets detected in staged changes. Remove or redact them before committing."
      exit 1
    }
  else
    gitleaks protect --staged --no-banner || {
      echo "❌ BLOCKED: Secrets detected in staged changes. Remove or redact them before committing."
      exit 1
    }
  fi
else
  echo "  ⚠️ gitleaks not installed — running fallback token scan"
fi

STAGED_PATCH="$(git diff --cached --no-color 2>/dev/null || true)"
if echo "$STAGED_PATCH" | grep -E '^[+].*(sbp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]+|gh[pousr]_[A-Za-z0-9]{20,}|sk_(live|test)_[A-Za-z0-9]{16,}|AIza[0-9A-Za-z_-]{20,}|-----BEGIN (RSA|EC|OPENSSH|DSA|PGP) PRIVATE KEY-----)' >/dev/null 2>&1; then
  echo "❌ BLOCKED: Potential secret detected in staged diff. Remove or redact it before committing."
  exit 1
fi

# Calculate staged files hash (Merkle-style)
STAGED_HASH=""
for file in $STAGED_FILES; do
  if [ -f "$file" ]; then
    file_hash="$(sha256sum "$file" 2>/dev/null | cut -d' ' -f1 || echo 'null')"
    STAGED_HASH="${STAGED_HASH}${file_hash}"
  fi
done
CHANGE_HASH="$(echo "${REPO_PATH}:${BRANCH}:${STAGED_HASH}:$(date +%s)" | sha256sum | cut -d' ' -f1)"
NODE_ID="$(echo "$CHANGE_HASH" | cut -c1-16)"

# Classify impact
IMPACT="low"
for file in $STAGED_FILES; do
  case "$file" in
    *runtime*|*auth*|*security*|*middleware*|*.env*)
      IMPACT="critical"
      break
      ;;
    *api/*|*db/*|*config/*|*migrations/*)
      if [ "$IMPACT" != "critical" ]; then
        IMPACT="high"
      fi
      ;;
    *components/*|*features/*|*hooks/*)
      if [ "$IMPACT" = "low" ]; then
        IMPACT="medium"
      fi
      ;;
  esac
done

# Create impact emoji
IMPACT_EMOJI="⚪"
case "$IMPACT" in
  critical) IMPACT_EMOJI="🔴" ;;
  high) IMPACT_EMOJI="🟠" ;;
  medium) IMPACT_EMOJI="🟡" ;;
esac

# Check for cross-repo dependencies
echo "  📊 Impact analysis: ${IMPACT_EMOJI} ${IMPACT} (${STAGED_COUNT} files)"

# Check if this change affects other repos
AFFECTS_OTHERS=""
for file in $STAGED_FILES; do
  case "$file" in
    *packages/shared*|*.guarani/*|.windsurf/workflows/*)
      AFFECTS_OTHERS="true"
      echo "  ⚠️  WARNING: Changes to $file may affect OTHER repositories!"
      ;;
  esac
done

# ════════════════════════════════════════════════════════
# GOVERNANCE GATE — Doc proliferation + SSOT limits
# ════════════════════════════════════════════════════════

# CHECK: Doc proliferation (BLOCKING)
NEW_DOCS=$(git diff --cached --name-only --diff-filter=A | grep '^docs/' || true)
if [ -n "$NEW_DOCS" ]; then
  FILTERED=$(echo "$NEW_DOCS" | grep -vE '^docs/(_context_snapshots|_generated|_archived_handoffs)/' || true)
  TIMESTAMPED=$(echo "$FILTERED" | grep -E '_20[0-9]{2}-[0-9]{2}' || true)
  if [ -n "$TIMESTAMPED" ]; then
    echo "❌ BLOCKED: Timestamped docs not allowed outside allowed folders."
    echo "   Move to docs/_archived_handoffs/ or use TASKS.md/SYSTEM_MAP.md instead:"
    echo "$TIMESTAMPED" | while IFS= read -r f; do echo "   - $f"; done
    exit 1
  fi
fi

# CHECK: SSOT file size limits (warning only)
_chk() {
  if [ -f "$1" ]; then
    _l=$(wc -l < "$1")
    [ "$_l" -gt "$2" ] && echo "  ⚠️  $1: ${_l} lines (soft limit: $2)" || true
  fi
}
_chk "AGENTS.md" 200; _chk "TASKS.md" 500; _chk "docs/SYSTEM_MAP.md" 300

# CHECK: Handoff freshness (warning only)
if [ -d "docs/_current_handoffs" ]; then
  _hc=$(find docs/_current_handoffs -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
  [ "${_hc:-0}" -gt 5 ] && echo "  ⚠️  ${_hc} active handoffs — consider archiving >30-day-old files" || true
fi

# Log to CRCDM
TIMESTAMP="$(date -u +%s)"
{
  echo "${TIMESTAMP} ${NODE_ID} ${REPO_NAME} ${BRANCH} ${IMPACT} PRE_COMMIT:${STAGED_COUNT}_files"
  echo "$STAGED_FILES" | while read -r file; do
    if [ -n "$file" ]; then
      echo "${TIMESTAMP} ${NODE_ID} FILE: $file"
    fi
  done
} >> "${CRCDM_ROOT}/logs/${HOOK_NAME}.log"

# Create pre-commit node in DAG
if command -v jq >/dev/null 2>&1; then
  DAG_FILE="${CRCDM_ROOT}/dag/dag.json"
  if [ ! -f "$DAG_FILE" ]; then
    echo '{"nodes": [], "edges": [], "version": "1.0.0"}' > "$DAG_FILE"
  fi
  
  # Create node
  NODE=$(jq -n \
    --arg id "$NODE_ID" \
    --arg repo "$REPO_NAME" \
    --arg branch "$BRANCH" \
    --arg impact "$IMPACT" \
    --argjson files "$(echo "$STAGED_FILES" | jq -R . | jq -s .)" \
    --arg timestamp "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
    --arg type "pre-commit" \
    '{id: $id, repo: $repo, branch: $branch, impact: $impact, files: $files, timestamp: $timestamp, type: $type, status: "pending"}')
  
  jq --argjson node "$NODE" '.nodes += [$node]' "$DAG_FILE" > "${DAG_FILE}.tmp" && mv "${DAG_FILE}.tmp" "$DAG_FILE"
fi

# Check for Claude Code context (if running inside Claude)
if [ -n "${CLaude_SESSION:-}" ] || [ -f ".claude/session.json" ] 2>/dev/null; then
  echo "  🤖 Claude Code session detected — syncing context..."
fi

# Final report
echo "  📝 CRCDM Node: ${NODE_ID}"
echo "  🌿 Branch: ${BRANCH}"
if [ -n "$AFFECTS_OTHERS" ]; then
  echo "  🔗 Cross-repo impact: YES — Run 'crcdm-sync' after commit"
fi

# Export for potential downstream hooks
export CRCDM_NODE_ID="$NODE_ID"
export CRCDM_IMPACT="$IMPACT"
export CRCDM_FILES_COUNT="$STAGED_COUNT"

echo "✅ CRCDM [$HOOK_NAME] — Ready to commit"
