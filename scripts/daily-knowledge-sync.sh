#!/bin/bash
# ============================================================================
# EGOS Daily Knowledge Sync
# Runs after Governance Drift Sentinel — compiles raw sources into wiki
# Can be added to VPS cron or CCR scheduled job
#
# Usage:
#   bash scripts/daily-knowledge-sync.sh
#   bash scripts/daily-knowledge-sync.sh --dry
# ============================================================================

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DRY="${1:---compile}"
echo "[knowledge-sync] Starting at $(date -Iseconds)"

# Step 1: Compile raw sources → wiki pages
echo "[knowledge-sync] Step 1: Compiling raw sources..."
bun agents/agents/wiki-compiler.ts --compile $DRY 2>&1 || echo "[knowledge-sync] WARN: compile failed (non-fatal)"

# Step 2: Compile world-model snapshot
echo "[knowledge-sync] Step 2: Compiling world-model snapshot..."
bun agents/agents/wiki-compiler.ts --world $DRY 2>&1 || echo "[knowledge-sync] WARN: world-model compile failed (non-fatal)"

# Step 3: Run lint
echo "[knowledge-sync] Step 3: Running wiki lint..."
bun agents/agents/wiki-compiler.ts --lint 2>&1 || echo "[knowledge-sync] WARN: lint failed (non-fatal)"

echo "[knowledge-sync] Done at $(date -Iseconds)"
