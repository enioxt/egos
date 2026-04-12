#!/bin/bash
# TL-009: Timeline Daily Cron
# Scans last 24h of commits and generates article drafts
# Cron: 03:00 UTC daily
# Usage: bash scripts/timeline-cron-daily.sh [--dry-run]

set -euo pipefail

DRY_RUN="${1:-}"
LOG_DIR="${EGOS_ROOT:-/opt/egos}/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/timeline-cron-$(date +%Y-%m-%d).log"

log() { echo "[$(date -u '+%Y-%m-%d %H:%M:%S UTC')] $*" | tee -a "$LOG_FILE"; }

log "🕐 Timeline Daily Cron starting..."

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EGOS_DIR="${EGOS_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"

# If EGOS_DIR is not a git repo, try /opt/egos-git (VPS clone)
if [ ! -d "$EGOS_DIR/.git" ]; then
  if [ -d "/opt/egos-git/.git" ]; then
    EGOS_DIR="/opt/egos-git"
    log "Using git clone at $EGOS_DIR"
  else
    log "❌ No git repo found at $EGOS_DIR — skipping"
    exit 1
  fi
fi

# Pull latest commits
log "Pulling latest from origin..."
git -C "$EGOS_DIR" pull --rebase origin main --quiet 2>/dev/null || log "⚠️  git pull failed (non-blocking)"

# Get commits from last 24h
COMMITS=$(git -C "$EGOS_DIR" log \
  --since="24 hours ago" \
  --format="%H %s" \
  --no-merges \
  2>/dev/null || true)

if [ -z "$COMMITS" ]; then
  log "No commits in last 24h — skipping"
  exit 0
fi

COMMIT_COUNT=$(echo "$COMMITS" | wc -l)
log "Found $COMMIT_COUNT commits in last 24h"

# Filter: only feat/fix/docs commits (skip chore/style/ci)
PUBLISHABLE=$(echo "$COMMITS" | grep -E '^[a-f0-9]+ (feat|fix|docs)\(' || true)
PUBLISHABLE_COUNT=$(echo "$PUBLISHABLE" | grep -c '.' || echo 0)

log "Publishable commits (feat/fix/docs): $PUBLISHABLE_COUNT"

if [ -z "$PUBLISHABLE" ]; then
  log "No publishable commits — skipping"
  exit 0
fi

DRAFTED=0
SKIPPED=0

while IFS= read -r line; do
  HASH=$(echo "$line" | cut -d' ' -f1)
  SUBJECT=$(echo "$line" | cut -d' ' -f2-)

  log "  Processing $HASH: $SUBJECT"

  if [ "$DRY_RUN" = "--dry-run" ]; then
    log "  [DRY-RUN] Would call: bun $EGOS_DIR/agents/agents/article-writer.ts --hash $HASH"
    DRAFTED=$((DRAFTED + 1))
    continue
  fi

  # Call article-writer (non-blocking, fire and forget into background)
  # article-writer handles its own dedup via timeline_drafts(slug unique)
  if bun "$EGOS_DIR/agents/agents/article-writer.ts" \
      --commit "$HASH" \
      --topic "$SUBJECT" \
      >> "$LOG_FILE" 2>&1; then
    log "  ✅ Draft created for $HASH"
    DRAFTED=$((DRAFTED + 1))
  else
    log "  ⚠️  Draft skipped for $HASH (may already exist)"
    SKIPPED=$((SKIPPED + 1))
  fi

  # Rate limit: 1 article per 5s to avoid LLM quota
  sleep 5

done <<< "$PUBLISHABLE"

log "✅ Timeline cron complete — drafted: $DRAFTED, skipped: $SKIPPED"
