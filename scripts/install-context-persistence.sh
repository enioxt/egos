#!/bin/bash
# install-context-persistence.sh — Disseminate Context Persistence to EGOS leaf repos
# Usage: bash scripts/install-context-persistence.sh [repo_path]
# If no repo_path given, installs to all registered leaf repos

set -e

KERNEL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONTEXT_MANAGER="$KERNEL_DIR/scripts/context-manager.ts"
RESTORE_SCRIPT="$KERNEL_DIR/scripts/restore-context-on-start.sh"
SNAPSHOT_CMD="$KERNEL_DIR/.claude/commands/snapshot.md"
RESTORE_CMD="$KERNEL_DIR/.claude/commands/restore-context.md"

REPOS=(
  "/home/enio/852"
  "/home/enio/carteira-livre"
  "/home/enio/br-acc"
  "/home/enio/egos-lab"
  "/home/enio/smartbuscas"
  "/home/enio/INPI"
  "/home/enio/policia"
  "/home/enio/santiago"
  "/home/enio/forja"
)

install_to_repo() {
  local repo="$1"
  local name=$(basename "$repo")

  if [ ! -d "$repo/.git" ]; then
    echo "⚠️  $name: not a git repo, skipping"
    return
  fi

  echo "📦 Installing context-persistence in $name..."

  # Create directories
  mkdir -p "$repo/scripts"
  mkdir -p "$repo/docs/_context_snapshots"
  mkdir -p "$repo/.claude/commands"

  # Copy core files (skip if already present and newer)
  cp "$CONTEXT_MANAGER" "$repo/scripts/context-manager.ts"
  cp "$RESTORE_SCRIPT" "$repo/scripts/restore-context-on-start.sh"
  chmod +x "$repo/scripts/restore-context-on-start.sh"

  # Copy slash commands
  cp "$SNAPSHOT_CMD" "$repo/.claude/commands/snapshot.md"
  cp "$RESTORE_CMD" "$repo/.claude/commands/restore-context.md"

  # Add to .gitignore if not present
  if [ -f "$repo/.gitignore" ]; then
    if ! grep -q "_context_snapshots/.state.json" "$repo/.gitignore" 2>/dev/null; then
      echo "" >> "$repo/.gitignore"
      echo "# Context persistence state (local only)" >> "$repo/.gitignore"
      echo "docs/_context_snapshots/.state.json" >> "$repo/.gitignore"
    fi
  fi

  # Integrate post-commit hook (merge if exists)
  if [ -d "$repo/.husky" ]; then
    local hook="$repo/.husky/post-commit"
    if [ -f "$hook" ]; then
      if ! grep -q "context-manager" "$hook"; then
        echo "" >> "$hook"
        echo "# Context Persistence — auto-snapshot on important commits" >> "$hook"
        echo 'commit_msg=$(git log --format=%s -1)' >> "$hook"
        echo 'if [[ $commit_msg =~ ^(feat|fix|refactor|perf|BREAKING)(\(.*\))?:  ]]; then' >> "$hook"
        echo '  bun scripts/context-manager.ts snapshot commit 2>/dev/null || true' >> "$hook"
        echo 'fi' >> "$hook"
        echo 'bun scripts/context-manager.ts increment 2>/dev/null || true' >> "$hook"
      fi
    else
      cat > "$hook" << 'HOOKEOF'
#!/bin/sh
# Context Persistence — auto-snapshot on important commits
commit_msg=$(git log --format=%s -1)
if [[ $commit_msg =~ ^(feat|fix|refactor|perf|BREAKING)(\(.*\))?:  ]]; then
  bun scripts/context-manager.ts snapshot commit 2>/dev/null || true
fi
bun scripts/context-manager.ts increment 2>/dev/null || true
HOOKEOF
      chmod +x "$hook"
    fi
  fi

  echo "✅ $name: context-persistence installed"
}

if [ -n "$1" ]; then
  install_to_repo "$1"
else
  echo "🌿 EGOS Context Persistence — Dissemination"
  echo "============================================="
  echo ""
  for repo in "${REPOS[@]}"; do
    install_to_repo "$repo"
  done
  echo ""
  echo "🎉 Context persistence disseminated to ${#REPOS[@]} repos"
  echo ""
  echo "Test: cd <repo> && bun scripts/context-manager.ts snapshot manual"
fi
