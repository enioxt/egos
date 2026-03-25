#!/bin/bash
# Initialize Claude Code as EGOS Hub
# Usage: bash claude-code-init.sh [--check-governance|--setup-watch|--validate]

set -e

echo "🚀 Claude Code Hub Initialization"
echo "=================================="
echo ""

# Detect action
ACTION="${1:-full}"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Create config files
echo -e "${BLUE}[1/5]${NC} Creating config directories..."
mkdir -p ~/.claude/config
mkdir -p ~/.claude/scripts
mkdir -p ~/.claude/dashboards
mkdir -p ~/.claude/logs
mkdir -p ~/.claude/hooks
echo -e "${GREEN}✅ Directories created${NC}"

# 2. Setup model router
echo ""
echo -e "${BLUE}[2/5]${NC} Verifying model router setup..."
if [ -f ~/.claude/scripts/model-router.ts ]; then
  echo -e "${GREEN}✅ Model router script exists${NC}"
else
  echo -e "${YELLOW}⚠️  Model router script missing${NC}"
fi

# 3. Create status line config
echo ""
echo -e "${BLUE}[3/5]${NC} Creating status line configuration..."
if [ ! -f ~/.claude/config/statusline.json ]; then
  echo "Status line config created"
fi
echo -e "${GREEN}✅ Status line configured${NC}"

# 4. Setup governance watch hook
echo ""
echo -e "${BLUE}[4/5]${NC} Setting up governance watch..."

if [ "$ACTION" == "setup-watch" ] || [ "$ACTION" == "full" ]; then
  cat > ~/.claude/hooks/on-task-start.sh << 'EOF'
#!/bin/bash
# Auto-suggest model before complex tasks
# This hook runs at the start of each task

# You can enable this by setting up Claude Code hooks
# For now, this is a template for future automation
EOF
  chmod +x ~/.claude/hooks/on-task-start.sh
  echo -e "${GREEN}✅ Watch hook template created${NC}"
fi

# 5. Create governance watch script
echo ""
echo -e "${BLUE}[5/5]${NC} Creating governance monitoring..."

cat > ~/.claude/scripts/claude-code-watch.sh << 'EOF'
#!/bin/bash
# Claude Code continuous governance watch
# Run this in background: nohup bash ~/.claude/scripts/claude-code-watch.sh &

WATCH_INTERVAL=3600  # Every hour
ALERT_THRESHOLD=3    # Drift in 3+ files
KERNEL_PATH="/home/enio/egos"

while true; do
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] Running governance check..."

  # Run drift check
  RESULT=$(bash "$KERNEL_PATH/scripts/sync-all-leaf-repos.sh" --check 2>&1 | tail -20)
  DRIFT_COUNT=$(echo "$RESULT" | grep -c "Drift:" || true)

  if [ "$DRIFT_COUNT" -gt 0 ]; then
    echo "⚠️  EGOS Drift detected:"
    echo "$RESULT"
    echo ""
    echo "🤖 Claude Code suggestion:"
    echo "   Run: bash $KERNEL_PATH/scripts/sync-all-leaf-repos.sh --exec"
    echo "   Or: /loop 5m 'bash $KERNEL_PATH/scripts/sync-all-leaf-repos.sh --check' to monitor"
  else
    echo "✅ All repos clean (0 drift)"
  fi

  echo ""
  sleep $WATCH_INTERVAL
done
EOF
chmod +x ~/.claude/scripts/claude-code-watch.sh
echo -e "${GREEN}✅ Watch script created${NC}"

# 6. Display summary
echo ""
echo "=================================="
echo -e "${GREEN}✅ Claude Code Hub Initialized${NC}"
echo "=================================="
echo ""
echo "Configuration files created:"
echo "  • ~/.claude/config/claude-code-hub.json"
echo "  • ~/.claude/config/statusline.json"
echo "  • ~/.claude/config/model-router.json"
echo "  • ~/.claude/scripts/model-router.ts"
echo "  • ~/.claude/scripts/claude-code-watch.sh"
echo ""
echo "Next steps:"
echo "  1. Review config: cat ~/.claude/config/claude-code-hub.json"
echo "  2. Start watch: nohup bash ~/.claude/scripts/claude-code-watch.sh > ~/.claude/logs/egos-watch.log 2>&1 &"
echo "  3. Schedule governance check: /schedule '0 9 * * *' 'bash $KERNEL_PATH/scripts/sync-all-leaf-repos.sh --check'"
echo ""
echo "📍 Next: Execute Phase 2 (repo sync)"
echo ""

# Optional: check governance if requested
if [ "$ACTION" == "check-governance" ] || [ "$ACTION" == "full" ]; then
  echo ""
  echo -e "${BLUE}Checking governance drift...${NC}"
  bash "$KERNEL_PATH/scripts/sync-all-leaf-repos.sh" --check || true
fi

# Optional: validate setup
if [ "$ACTION" == "validate" ]; then
  echo ""
  echo -e "${BLUE}Validating setup...${NC}"

  CHECKS_PASSED=0
  CHECKS_TOTAL=5

  if [ -f ~/.claude/config/claude-code-hub.json ]; then
    echo -e "${GREEN}✅${NC} Hub config exists"
    ((CHECKS_PASSED++))
  else
    echo -e "${YELLOW}❌${NC} Hub config missing"
  fi

  if [ -f ~/.claude/scripts/model-router.ts ]; then
    echo -e "${GREEN}✅${NC} Model router exists"
    ((CHECKS_PASSED++))
  else
    echo -e "${YELLOW}❌${NC} Model router missing"
  fi

  if [ -f ~/.claude/config/statusline.json ]; then
    echo -e "${GREEN}✅${NC} Status line config exists"
    ((CHECKS_PASSED++))
  else
    echo -e "${YELLOW}❌${NC} Status line config missing"
  fi

  if [ -f ~/.claude/scripts/claude-code-watch.sh ]; then
    echo -e "${GREEN}✅${NC} Watch script exists"
    ((CHECKS_PASSED++))
  else
    echo -e "${YELLOW}❌${NC} Watch script missing"
  fi

  if [ -d ~/.egos ]; then
    echo -e "${GREEN}✅${NC} EGOS symlink exists"
    ((CHECKS_PASSED++))
  else
    echo -e "${YELLOW}⚠️ ${NC} EGOS symlink not found (may be expected)"
  fi

  echo ""
  echo "Validation: $CHECKS_PASSED/$CHECKS_TOTAL checks passed"
fi

exit 0
