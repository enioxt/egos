#!/bin/bash
# Post-session hook - Rastreia contexto ao final da sessão

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "\n${GREEN}📊 EGOS Post-Session Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Context tracker
echo -e "\n${YELLOW}📈 Context Tracker:${NC}"
bun run agent:run context_tracker --dry 2>&1 | grep "CTX" || echo "Context tracker not available"

# 2. Session summary
echo -e "\n${YELLOW}📝 Session Summary:${NC}"
COMMITS_THIS_SESSION=$(git log --since="1 hour ago" --oneline | wc -l)
FILES_CHANGED=$(git diff --name-only HEAD~${COMMITS_THIS_SESSION}..HEAD 2>/dev/null | wc -l || echo "0")

echo "  • Commits in last hour: $COMMITS_THIS_SESSION"
echo "  • Files changed: $FILES_CHANGED"

# 3. Uncommitted changes
UNCOMMITTED=$(git status --short | wc -l)
if [ "$UNCOMMITTED" -gt 0 ]; then
  echo -e "\n${YELLOW}⚠️  Reminder: You have $UNCOMMITTED uncommitted changes${NC}"
  echo "  Run: git status"
fi

# 4. Suggestion to /end if CTX high
# TODO: Parse CTX score and suggest /end if > 180

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Session complete. Safe to /end${NC}\n"
