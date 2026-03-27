#!/bin/bash
# Pre-session hook - Verifica status do kernel antes da sessão

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔍 EGOS Pre-Session Check${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Git status
echo -e "\n${YELLOW}📊 Git Status:${NC}"
git status --short | head -20

# 2. Last commit
echo -e "\n${YELLOW}📝 Last Commit:${NC}"
git log -1 --oneline --decorate

# 3. Current branch
echo -e "\n${YELLOW}🌿 Branch:${NC}"
git branch --show-current

# 4. Check for uncommitted changes
UNCOMMITTED=$(git status --short | wc -l)
if [ "$UNCOMMITTED" -gt 0 ]; then
  echo -e "\n${YELLOW}⚠️  You have $UNCOMMITTED uncommitted changes${NC}"
fi

# 5. Check governance drift (optional - pode ser lento)
# Uncomment if you want to run governance check every session
# echo -e "\n${YELLOW}🔐 Governance Check:${NC}"
# bun run governance:check || echo -e "${RED}⚠️  Governance drift detected${NC}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Pre-session check complete${NC}\n"
