#!/bin/bash
# COST-004 — Weekly Claude Code cost alert
# Cron: every Friday 18h BRT (21h UTC)
# 0 21 * * 5 root /usr/local/bin/claude-cost-alert.sh

set -a
source /opt/apps/egos-agents/.env 2>/dev/null || true
set +a

TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-$TELEGRAM_BOT_TOKEN_AI_AGENTS}"
TELEGRAM_CHAT_ID="${TELEGRAM_ADMIN_CHAT_ID:-171767219}"
SCRIPT="/home/enio/egos/scripts/claude-cost.ts"

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
  echo "[cost-alert] No TELEGRAM_BOT_TOKEN — skipping"
  exit 0
fi

# Get JSON summary for last 7 days
JSON=$(bun "$SCRIPT" --days 7 --json 2>/dev/null)
if [ -z "$JSON" ]; then
  echo "[cost-alert] No data returned"
  exit 0
fi

TOTAL=$(echo "$JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(round(sum(p['cost_usd'] for p in d['by_project']), 2))" 2>/dev/null || echo "?")
TOP_PROJ=$(echo "$JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); p=d['by_project']; print(p[0]['project'].replace('-home-enio-','') + ' \$' + str(round(p[0]['cost_usd'],2))) if p else print('none')" 2>/dev/null || echo "?")
SESSIONS=$(echo "$JSON" | python3 -c "import json,sys; d=json.load(sys.stdin); print(sum(p['sessions'] for p in d['by_project']))" 2>/dev/null || echo "?")

MSG="📊 *Claude Code — Weekly Cost*

💰 Total: *\$$TOTAL* (7 dias)
🏆 Top project: $TOP_PROJ
🔄 Sessions: $SESSIONS

#egos #cost #claude"

curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\":\"${TELEGRAM_CHAT_ID}\",\"text\":$(echo "$MSG" | python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))"),\"parse_mode\":\"Markdown\"}" \
  > /dev/null

echo "[cost-alert] Sent: \$$TOTAL this week"
