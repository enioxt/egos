#!/usr/bin/env bash
# ============================================================================
# scripts/create-pr.sh — Automated PR creation (GIT-005)
# ============================================================================
# Usage:
#   bash scripts/create-pr.sh "My PR title"
#   bash scripts/create-pr.sh "feat: add X" --draft
#   bash scripts/create-pr.sh "fix: Y" --base develop
#
# What it does:
#   1. Ensure on a feature branch (not main/master)
#   2. Push current branch to origin (via safe-push.sh)
#   3. Generate PR body from commit log since diverging from base
#   4. Create PR via gh CLI
# ============================================================================

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
TITLE="${1:-}"
DRAFT_FLAG=""
BASE_BRANCH="main"

# Parse args
shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --draft) DRAFT_FLAG="--draft" ;;
    --base) BASE_BRANCH="${2:-main}"; shift ;;
  esac
  shift || true
done

if [ -z "$TITLE" ]; then
  echo "Usage: bash scripts/create-pr.sh \"PR title\" [--draft] [--base <branch>]"
  exit 1
fi

CURRENT_BRANCH=$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD)

if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" ]]; then
  echo "❌ Cannot create PR from main/master. Create a feature branch first:"
  echo "   git checkout -b feat/your-feature"
  exit 1
fi

echo "[create-pr] Branch: $CURRENT_BRANCH → $BASE_BRANCH"
echo "[create-pr] Title: $TITLE"

# Push branch
echo "[create-pr] Pushing branch..."
bash "$REPO_ROOT/scripts/safe-push.sh" "$CURRENT_BRANCH" 2>&1

# Build PR body from commits
COMMITS=$(git log "origin/$BASE_BRANCH..HEAD" --oneline --no-merges 2>/dev/null || git log "$BASE_BRANCH..HEAD" --oneline --no-merges 2>/dev/null)
COMMIT_COUNT=$(echo "$COMMITS" | grep -c . || echo "0")
CHANGED_FILES=$(git diff --name-only "origin/$BASE_BRANCH...HEAD" 2>/dev/null | wc -l | tr -d ' ')

PR_BODY="$(cat <<BODY
## Summary

$(echo "$COMMITS" | head -10 | sed 's/^/- /')

## Changes

- Files changed: $CHANGED_FILES
- Commits: $COMMIT_COUNT

## Test plan

- [ ] \`bun typecheck\` passes
- [ ] \`bun test\` passes (if tests exist)
- [ ] Reviewed diff before merge

🤖 Generated with [Claude Code](https://claude.ai/claude-code)
BODY
)"

# Create PR
echo "[create-pr] Creating PR..."
PR_URL=$(gh pr create \
  --title "$TITLE" \
  --body "$PR_BODY" \
  --base "$BASE_BRANCH" \
  --head "$CURRENT_BRANCH" \
  $DRAFT_FLAG \
  2>&1)

echo ""
echo "✅ PR created: $PR_URL"
