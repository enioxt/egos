#!/usr/bin/env bash
# EGOS Task Archiver — moves completed [x] tasks to TASKS_ARCHIVE.md
# Called by pre-commit hook when TASKS.md approaches limit
# NEVER deletes tasks — only moves completed ones to archive
#
# Usage: bash scripts/archive-tasks.sh [--dry-run]
# Exit 0: archived successfully | Exit 1: error

set -euo pipefail

DRY_RUN=false
[ "${1:-}" = "--dry-run" ] && DRY_RUN=true

TASKS="TASKS.md"
ARCHIVE="TASKS_ARCHIVE.md"
DATE=$(date -u '+%Y-%m-%d')

if [ ! -f "$TASKS" ]; then
  echo "ERROR: $TASKS not found" >&2
  exit 1
fi

BEFORE=$(wc -l < "$TASKS")

# Count how many completed tasks exist
COMPLETED=$(grep -c "^- \[x\]" "$TASKS" 2>/dev/null || true)

if [ "$COMPLETED" -eq 0 ]; then
  echo "No completed tasks to archive (TASKS.md: $BEFORE lines)"
  exit 0
fi

if [ "$DRY_RUN" = "true" ]; then
  echo "[DRY-RUN] Would archive $COMPLETED completed tasks from $TASKS → $ARCHIVE"
  grep "^- \[x\]" "$TASKS" | head -5
  echo "..."
  exit 0
fi

# Extract completed tasks
COMPLETED_BLOCK=$(grep "^- \[x\]" "$TASKS")

# Ensure archive exists with header
if [ ! -f "$ARCHIVE" ]; then
  cat > "$ARCHIVE" << HEADER
# TASKS_ARCHIVE.md — Completed Tasks
> Auto-archived from TASKS.md when approaching 500-line limit.
> Append-only. Never edit manually. Use scripts/archive-tasks.sh

HEADER
fi

# Append to archive with section header
echo "" >> "$ARCHIVE"
echo "## Archived ${DATE} (${COMPLETED} tasks)" >> "$ARCHIVE"
echo "" >> "$ARCHIVE"
echo "$COMPLETED_BLOCK" >> "$ARCHIVE"

# Remove completed tasks from TASKS.md (preserve blank lines context)
# Strategy: remove lines matching ^- [x] exactly (not section headers with [x])
python3 - << PYEOF
import re

with open('$TASKS', 'r') as f:
    content = f.read()

# Remove lines that are completed tasks (^- [x] pattern)
lines = content.split('\n')
filtered = []
for line in lines:
    if re.match(r'^- \[x\]', line):
        continue  # archived
    filtered.append(line)

# Remove consecutive blank lines (more than 2 in a row)
result = []
blank_count = 0
for line in filtered:
    if line.strip() == '':
        blank_count += 1
        if blank_count <= 2:
            result.append(line)
    else:
        blank_count = 0
        result.append(line)

with open('$TASKS', 'w') as f:
    f.write('\n'.join(result))
PYEOF

AFTER=$(wc -l < "$TASKS")
DELTA=$((BEFORE - AFTER))

echo "✅ Archived $COMPLETED completed tasks: $BEFORE → $AFTER lines (freed $DELTA lines)"
echo "   Archive: $ARCHIVE ($(wc -l < "$ARCHIVE") total lines)"
