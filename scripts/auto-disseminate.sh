#!/usr/bin/env bash
# ============================================================================
# scripts/auto-disseminate.sh — Post-Commit SSOT Auto-Propagation
# ============================================================================
# Triggered by .husky/post-commit after every commit.
# Also callable standalone: bash scripts/auto-disseminate.sh [--dry]
#
# Actions:
#   1. Parse commit message for task IDs → mark done in TASKS.md
#   2. Extract LEARNING: lines from commit body → append to HARVEST.md
#   3. Detect new capabilities (feat: commits) → warn if CAPABILITY_REGISTRY missing entry
#
# Non-blocking: never fails the commit. All errors are warnings.
# ============================================================================

set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel 2>/dev/null || pwd)"
TASKS_FILE="$REPO_ROOT/TASKS.md"
HARVEST_FILE="$REPO_ROOT/docs/knowledge/HARVEST.md"
CAP_REG="$REPO_ROOT/docs/CAPABILITY_REGISTRY.md"
DRY="${1:-}"
DATE=$(date +%Y-%m-%d)

# Get last commit info
COMMIT_MSG=$(git -C "$REPO_ROOT" log -1 --format="%B" 2>/dev/null || echo "")
COMMIT_HASH=$(git -C "$REPO_ROOT" log -1 --format="%h" 2>/dev/null || echo "unknown")
COMMIT_SUBJECT=$(git -C "$REPO_ROOT" log -1 --format="%s" 2>/dev/null || echo "")

echo "[auto-disseminate] commit=$COMMIT_HASH date=$DATE"

# ── 1. Task ID extraction ────────────────────────────────────────────────────
# Only scan the SUBJECT LINE (first line) for task IDs — not the body.
# Body may reference tasks as context ("Next P0: TASK-001") without completing them.
# To mark a task done: include its ID in the commit SUBJECT.
# Examples:
#   feat(hermes): X-COM-018 LLM analysis layer    ← marks X-COM-018 done
#   fix(guard): GUARD-BUG-003 nome pattern fix     ← marks GUARD-BUG-003 done
#
# DISS-BUG-001 fix: strip range notation (e.g. "KBS-001..026") before extraction.
# Without this, "KBS-001..026" would match KBS-001 as a standalone task ID.
CLEAN_SUBJECT=$(echo "$COMMIT_SUBJECT" | sed 's/[A-Z][A-Z0-9_]*-[0-9][0-9]*\.\.[0-9][0-9]*/RANGE_REMOVED/g')

TASK_IDS=$(echo "$CLEAN_SUBJECT" | grep -oE '\b[A-Z][A-Z0-9_]+-[0-9]+(-[A-Z][A-Z0-9]*)?\b' \
  | grep -vE '^(BRT|UTC|VPS|API|TLS|SQL|DNS|CDN|RAM|CPU|LLM|SSO|JWT|PII|URL|SSH|GTM|MCP|CCR|SSOT|LGPD|MVP|PRs?|RFC|EOF|HTTP|YAML|JSON|HTML|CORS|REPO|TODO|DONE|WARN|INFO|CRIT|NULL|TRUE|FALSE|RANGE_REMOVED)$' \
  | sort -u || true)

if [ -n "$TASK_IDS" ] && [ -f "$TASKS_FILE" ]; then
  MARKED=0
  for task_id in $TASK_IDS; do
    # Match checkbox pattern: - [ ] ... TASK-ID ...
    if grep -qE "^\- \[ \].*\b${task_id}\b" "$TASKS_FILE" 2>/dev/null; then
      if [ "$DRY" = "--dry" ]; then
        echo "  [DRY] would mark $task_id done in TASKS.md"
      else
        sed -i "s/^- \[ \] \(.*\b${task_id}\b.*\)/- [x] \1 ✅ ${DATE}/" "$TASKS_FILE"
        echo "  ✅ marked $task_id done"
        MARKED=$((MARKED + 1))
      fi
    fi
  done
  [ "$MARKED" -gt 0 ] && echo "[auto-disseminate] $MARKED task(s) marked done in TASKS.md"
fi

# ── 2. LEARNING: lines → HARVEST.md ─────────────────────────────────────────
LEARNINGS=$(echo "$COMMIT_MSG" | grep -E '^LEARNING:' | sed 's/^LEARNING:[[:space:]]*//' || true)

if [ -n "$LEARNINGS" ] && [ -f "$HARVEST_FILE" ]; then
  if [ "$DRY" = "--dry" ]; then
    echo "  [DRY] would append learnings to HARVEST.md:"
    echo "$LEARNINGS" | sed 's/^/    - /'
  else
    {
      echo ""
      echo "### Auto-harvested — $COMMIT_HASH ($DATE)"
      echo ""
      while IFS= read -r learning; do
        echo "- $learning"
      done <<< "$LEARNINGS"
    } >> "$HARVEST_FILE"
    echo "[auto-disseminate] learnings appended to HARVEST.md"
  fi
fi

# ── 3. New capability warning ────────────────────────────────────────────────
# If commit subject starts with "feat(" and CAPABILITY_REGISTRY.md exists,
# check that the capability name appears somewhere in the registry.
if echo "$COMMIT_SUBJECT" | grep -qE '^feat\('; then
  CAP_NAME=$(echo "$COMMIT_SUBJECT" | grep -oP '(?<=feat\()([^)]+)' || true)
  if [ -n "$CAP_NAME" ] && [ -f "$CAP_REG" ]; then
    if ! grep -qi "$CAP_NAME" "$CAP_REG" 2>/dev/null; then
      echo "  ⚠️  WARNING: feat($CAP_NAME) not found in CAPABILITY_REGISTRY.md"
      echo "       Consider adding a §N entry: docs/CAPABILITY_REGISTRY.md"
    fi
  fi
fi

# ── 4. PUBLISH: trigger → call article-writer ────────────────────────────────
# If commit body has "PUBLISH: <topic>" line, generate a timeline draft
PUBLISH_TOPIC=$(echo "$COMMIT_MSG" | grep -E '^PUBLISH:' | sed 's/^PUBLISH:[[:space:]]*//' | head -1 || true)

if [ -n "$PUBLISH_TOPIC" ]; then
  ARTICLE_WRITER="$REPO_ROOT/agents/agents/article-writer.ts"
  if [ "$DRY" = "--dry" ]; then
    echo "  [DRY] PUBLISH detected: '$PUBLISH_TOPIC' — would call article-writer.ts --hash $COMMIT_HASH"
  elif [ -f "$ARTICLE_WRITER" ]; then
    echo "[auto-disseminate] PUBLISH: '$PUBLISH_TOPIC' — triggering article-writer (background)..."
    bun "$ARTICLE_WRITER" --hash "$COMMIT_HASH" --topic "$PUBLISH_TOPIC" >>/tmp/egos-article-writer.log 2>&1 &
  else
    echo "  ⚠️  PUBLISH: detected but article-writer.ts not found at $ARTICLE_WRITER"
  fi
fi


# ── 5. PORTFOLIO SYNC: update living portfolio doc ─────────────────────────
# Triggers when a commit touches product-defining files
PORTFOLIO_SYNC="$REPO_ROOT/scripts/portfolio-sync.ts"
CHANGED_FILES=$(git -C "$REPO_ROOT" diff HEAD~1 --name-only 2>/dev/null || true)
SHOULD_SYNC=false

if echo "$CHANGED_FILES" | grep -qE "^(docs/CAPABILITY_REGISTRY\.md|agents/agents/|packages/|apps/|scripts/gem-hunter|scripts/x-reply-bot)"; then
  SHOULD_SYNC=true
fi

if [ "$SHOULD_SYNC" = "true" ] && [ -f "$PORTFOLIO_SYNC" ]; then
  if [ "$DRY" = "--dry" ]; then
    echo "  [DRY] portfolio-sync would run (product files changed)"
  else
    echo "[auto-disseminate] Portfolio sync triggered..."
    bun "$PORTFOLIO_SYNC" >>/tmp/egos-portfolio-sync.log 2>&1 &
  fi
fi

echo "[auto-disseminate] done."
exit 0
