#!/bin/bash
# batch-setup-all-repos.sh — Setup .claude/ in all 10 EGOS leaf repos

set -e

REPOS=(
  "forja"
  "carteira-livre"
  "852"
  "br-acc"
  "smartbuscas"
  "INPI"
  "santiago"
  "policia"
  "egos-self"
  "commons"
)

SETUP_SCRIPT="/home/enio/egos/.claude/setup-leaf-repo.sh"
HOME_DIR="/home/enio"
COMMITTED=0
FAILED=0

echo "🚀 Batch setup for all EGOS leaf repos"
echo "======================================"
echo ""

for repo in "${REPOS[@]}"; do
  REPO_PATH="$HOME_DIR/$repo"

  echo "📦 Setting up: $repo"

  if [ ! -d "$REPO_PATH" ]; then
    echo "⚠️  Skipping $repo (directory not found)"
    continue
  fi

  # Run setup script
  if bash "$SETUP_SCRIPT" "$REPO_PATH" > /tmp/setup-$repo.log 2>&1; then
    echo "  ✅ Setup successful"

    # Stage and commit
    (
      cd "$REPO_PATH"
      if git status --porcelain .claude/ | grep -q .; then
        git add .claude/
        git commit -m "chore(.claude): initialize Claude Code configuration"
        echo "  ✅ Committed to git"
        ((COMMITTED++))
      fi
    ) || echo "  ⚠️  Git commit failed"
  else
    echo "  ❌ Setup failed (see /tmp/setup-$repo.log)"
    ((FAILED++))
  fi

  echo ""
done

echo "======================================"
echo "📊 Summary:"
echo "  ✅ Committed: $COMMITTED"
echo "  ❌ Failed: $FAILED"
echo "  📦 Total: ${#REPOS[@]}"
echo ""
echo "Next step: git push origin main (or review diffs first)"
