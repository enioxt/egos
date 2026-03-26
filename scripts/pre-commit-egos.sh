#!/bin/bash
# EGOS Ecosystem Standard Pre-Commit Hook
# ----------------------------------------
# Standard: Root-level docs must be in docs/
# Security: Basic secret scan (no hardcoded passwords)

REPO_NAME=$(basename "$PWD")
echo "Starting EGOS Pre-commit check for [$REPO_NAME]..."

# 1. Allowed Root Files (Whitelisted)
ALLOWED_ROOT_FILES=("README.md" "TASK.md" "AGENTS.md" "TASKS.md" "implementation_plan.md" "walkthrough.md" "package.json" "tsconfig.json" "index.html" "vite.config.ts" ".gitignore" ".env" ".env.example")

# Check for staged markdown/text files in root
STAGED_ROOT_FILES=$(git diff --cached --name-only --diff-filter=A | grep -v "/" | grep -E "\.md$|\.txt$")

for file in $STAGED_ROOT_FILES; do
    is_allowed=false
    for allowed in "${ALLOWED_ROOT_FILES[@]}"; do
        if [[ "$file" == "$allowed" ]]; then
            is_allowed=true
            break
        fi
    done
    
    if [ "$is_allowed" = false ]; then
        echo "❌ ERROR: File [$file] is not allowed in the repository root."
        echo "Please move it to the docs/ directory or add it to the whitelist in egos/scripts/pre-commit-egos.sh."
        exit 1
    fi
done

# 2. Secret Scan (Basic)
SENSITIVE_PATTERNS=("sk-or-v1-" "postgresql://postgres:" "ghp_")
for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if git diff --cached --name-only | xargs grep -q "$pattern"; then
        echo "❌ ERROR: Sensitive pattern [$pattern] detected in staged changes."
        echo "Please remove credentials before committing."
        exit 1
    fi
done

echo "✅ EGOS Pre-commit check passed."
exit 0
