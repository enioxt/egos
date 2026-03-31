#!/bin/bash
# EGOS Doc Proliferation Check (Kernel)
# Blocks creation of timestamped docs and audit files

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "📋 EGOS Doc Proliferation Check (Kernel)"

STAGED_DOCS=$(git diff --cached --name-only --diff-filter=A | grep '^docs/' || true)

if [ -z "$STAGED_DOCS" ]; then
  echo "✅ No new docs staged"
  exit 0
fi

VIOLATIONS=0

while IFS= read -r file; do
  # Skip allowed folders
  if [[ "$file" =~ ^docs/_archived_handoffs/ ]] || [[ "$file" =~ ^docs/_current_handoffs/ ]] || [[ "$file" =~ ^docs/_context_snapshots/ ]] || [[ "$file" =~ ^docs/_generated/ ]]; then
    continue
  fi
  
  # Check for date stamps
  if [[ "$file" =~ _20[0-9]{2}-[0-9]{2} ]]; then
    echo -e "${RED}❌ BLOCKED:${NC} $file (timestamped filename)"
    VIOLATIONS=$((VIOLATIONS + 1))
  fi
  
  # Check for AUDIT files (except canonical)
  if [[ "$file" =~ AUDIT.*\.md$ ]] && [[ ! "$file" =~ ^docs/_archived/ ]]; then
    echo -e "${RED}❌ BLOCKED:${NC} $file (audit files must update AGENTS.md)"
    VIOLATIONS=$((VIOLATIONS + 1))
  fi
  
  # Check for DIAGNOSTIC files
  if [[ "$file" =~ DIAGNOSTIC.*\.md$ ]] && [[ ! "$file" =~ ^docs/_archived/ ]]; then
    echo -e "${RED}❌ BLOCKED:${NC} $file (diagnostic files must update SYSTEM_MAP.md)"
    VIOLATIONS=$((VIOLATIONS + 1))
  fi
  
  # Check for REPORT files with dates
  if [[ "$file" =~ REPORT.*20[0-9]{2}.*\.md$ ]] && [[ ! "$file" =~ ^docs/_archived/ ]]; then
    echo -e "${RED}❌ BLOCKED:${NC} $file (report files must update AGENTS.md)"
    VIOLATIONS=$((VIOLATIONS + 1))
  fi
  
done <<< "$STAGED_DOCS"

if [ $VIOLATIONS -gt 0 ]; then
  echo -e "${RED}❌ COMMIT BLOCKED: $VIOLATIONS violation(s)${NC}"
  echo "Update AGENTS.md, TASKS.md, or SYSTEM_MAP.md instead"
  exit 1
fi

echo "✅ No violations"
exit 0
