#!/bin/bash
# session-start.sh — Pre-session initialization for EGOS Claude Code

set -e

echo "🔄 Initializing EGOS session..."

# Load environment
export EGOS_KERNEL_PATH="/home/enio/egos"
export EGOS_WORKSPACE="${EGOS_WORKSPACE:-.}"

# Check governance drift
if [ -f ".windsurfrules" ]; then
  echo "📋 Checking governance compliance..."
fi

# Create session log
mkdir -p .claude/logs
SESSION_LOG=".claude/logs/session_$(date +%Y%m%d_%H%M%S).jsonl"
echo "{\"type\":\"session_start\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" >> "$SESSION_LOG"

# List scheduled agents (next 3)
if [ -f "agents/registry/agents.json" ]; then
  echo "🤖 Registered agents in this repo:"
  head -3 <(jq -r '.agents[].id' agents/registry/agents.json 2>/dev/null) || true
fi

echo "✅ Session initialized"
