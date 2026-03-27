#!/bin/bash
# setup-leaf-repo.sh — Bootstrap .claude/ configuration for leaf repositories
#
# Purpose: Create complete Claude Code configuration in any EGOS leaf repository
# Usage: bash ~/.egos/.claude/setup-leaf-repo.sh /path/to/repo
#
# What it does:
#   1. Create .claude/config/ with copies from kernel
#   2. Create .claude/hooks/ with symlinks to ~/.egos/.claude/hooks/
#   3. Create .claude/commands/ with symlinks to ~/.egos/.claude/commands/
#   4. Create repo-specific manifest.json
#   5. Verify everything is in place

set -e

# ============================================================================
# Configuration
# ============================================================================

REPO_PATH="${1:-.}"
KERNEL_CLAUDE="${HOME}/.egos/.claude"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ============================================================================
# Helper Functions
# ============================================================================

log_info() {
  echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
  echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
  echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
  echo -e "${RED}❌ $1${NC}"
}

# ============================================================================
# Validation
# ============================================================================

log_info "Validating setup..."

# Check if repo path exists
if [ ! -d "$REPO_PATH" ]; then
  log_error "Repository path does not exist: $REPO_PATH"
  exit 1
fi

# Check if kernel .claude/ exists
if [ ! -d "$KERNEL_CLAUDE" ]; then
  log_error "Kernel .claude/ not found at: $KERNEL_CLAUDE"
  log_info "Please run: bun run governance:sync:exec in egos kernel first"
  exit 1
fi

# Check if kernel has required subdirectories
for subdir in config hooks commands; do
  if [ ! -d "$KERNEL_CLAUDE/$subdir" ]; then
    log_error "Kernel .claude/$subdir not found"
    exit 1
  fi
done

log_success "Validation passed"

# ============================================================================
# Step 1: Create .claude/config/ with copies
# ============================================================================

log_info "Step 1/4: Creating .claude/config/ with configuration files..."

mkdir -p "$REPO_PATH/.claude/config"

# Copy configuration files (these should NOT be symlinks — they're repo-specific)
for config_file in mcp-servers.json memory.json permissions.json output-styles.json; do
  if [ -f "$KERNEL_CLAUDE/config/$config_file" ]; then
    cp "$KERNEL_CLAUDE/config/$config_file" "$REPO_PATH/.claude/config/$config_file"
    log_success "Copied config/$config_file"
  else
    log_warning "Config file not found: $config_file (skipping)"
  fi
done

# ============================================================================
# Step 2: Create .claude/hooks/ with symlinks
# ============================================================================

log_info "Step 2/4: Creating .claude/hooks/ with symlinks..."

mkdir -p "$REPO_PATH/.claude/hooks"

for hook_file in "$KERNEL_CLAUDE/hooks"/*.sh; do
  hook_name=$(basename "$hook_file")
  target_path="$REPO_PATH/.claude/hooks/$hook_name"

  # Remove existing symlink if it exists
  if [ -L "$target_path" ]; then
    rm "$target_path"
  fi

  # Create symlink
  ln -sf "$hook_file" "$target_path"
  log_success "Symlinked hooks/$hook_name"
done

# ============================================================================
# Step 3: Create .claude/commands/ with symlinks
# ============================================================================

log_info "Step 3/4: Creating .claude/commands/ with symlinks..."

mkdir -p "$REPO_PATH/.claude/commands"

for cmd_file in "$KERNEL_CLAUDE/commands"/*.md; do
  cmd_name=$(basename "$cmd_file")
  target_path="$REPO_PATH/.claude/commands/$cmd_name"

  # Remove existing symlink if it exists
  if [ -L "$target_path" ]; then
    rm "$target_path"
  fi

  # Create symlink
  ln -sf "$cmd_file" "$target_path"
  log_success "Symlinked commands/$cmd_name"
done

# ============================================================================
# Step 4: Create repo-specific manifest.json
# ============================================================================

log_info "Step 4/4: Creating repository-specific manifest.json..."

REPO_NAME=$(basename "$REPO_PATH")

cat > "$REPO_PATH/.claude/manifest.json" << EOF
{
  "version": "1.0.0",
  "description": "Claude Code Configuration for $REPO_NAME",
  "repo": "$REPO_NAME",
  "kernel": "/home/enio/egos",
  "agent_registry": "agents/registry/agents.json",
  "tasks_ssot": "TASKS.md",
  "setup_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "setup_host": "$(hostname)",
  "config_strategy": "hybrid (symlinks + copies)"
}
EOF

log_success "Created manifest.json"

# ============================================================================
# Verification
# ============================================================================

log_info "Verifying setup..."

verify_success=true

# Check config directory
if [ -d "$REPO_PATH/.claude/config" ] && [ -f "$REPO_PATH/.claude/config/mcp-servers.json" ]; then
  log_success "✓ .claude/config/ exists with files"
else
  log_error "✗ .claude/config/ missing or incomplete"
  verify_success=false
fi

# Check hooks directory
if [ -d "$REPO_PATH/.claude/hooks" ] && [ -L "$REPO_PATH/.claude/hooks/pre-session.sh" ]; then
  log_success "✓ .claude/hooks/ exists with symlinks"
else
  log_error "✗ .claude/hooks/ missing or incomplete"
  verify_success=false
fi

# Check commands directory
if [ -d "$REPO_PATH/.claude/commands" ] && [ -L "$REPO_PATH/.claude/commands/start.md" ]; then
  log_success "✓ .claude/commands/ exists with symlinks"
else
  log_error "✗ .claude/commands/ missing or incomplete"
  verify_success=false
fi

# Check manifest
if [ -f "$REPO_PATH/.claude/manifest.json" ]; then
  log_success "✓ manifest.json created"
else
  log_error "✗ manifest.json not found"
  verify_success=false
fi

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "================================"

if [ "$verify_success" = true ]; then
  log_success "Setup complete for $REPO_NAME"

  echo ""
  log_info "Next steps:"
  echo "  1. cd $REPO_PATH"
  echo "  2. git add .claude/"
  echo "  3. git commit -m 'chore(.claude): initialize Claude Code configuration'"
  echo "  4. git push origin main"
  echo "  5. claude /agents list   # Should show agents from agents/registry/agents.json"
  echo ""
else
  log_error "Setup completed with errors — please review above"
  exit 1
fi

echo "================================"
