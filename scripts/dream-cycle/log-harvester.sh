#!/bin/bash
# ============================================================================
# EGOS Dream Cycle — Log Harvester v1.1
# VPS cron: 0 23 * * * /opt/apps/egos-agents/scripts/log-harvester.sh
# ============================================================================

DATE=$(date +%Y-%m-%d)
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
LOG_DIR="/opt/apps/egos-agents/logs"
REPORT_FILE="${LOG_DIR}/log-harvest-${DATE}.json"
mkdir -p "$LOG_DIR"

# Load env from gateway (has Supabase + Telegram credentials)
set -a
[ -f /opt/apps/egos-gateway/.env ] && source /opt/apps/egos-gateway/.env
set +a

echo "[dream-cycle] Log Harvester ${VERSION:-1.1} started: $TIMESTAMP"

CONTAINERS=(
  "guard-brasil-api"
  "egos-gateway"
  "egos-hq"
  "eagle-eye"
  "852-app"
  "egos-arch"
  "evolution-api"
  "infra-caddy-1"
  "infra-api-1"
)

# Collect per-container stats into temp file
STATS_FILE=$(mktemp)
echo "[]" > "$STATS_FILE"

for container in "${CONTAINERS[@]}"; do
  STATUS="running"
  SEVERITY="ok"
  ERROR_COUNT=0
  WARN_COUNT=0
  HTTP_5XX=0
  HTTP_4XX=0

  if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${container}$"; then
    STATUS="down"
    SEVERITY="critical"
    echo "[dream-cycle] CRITICAL: $container is DOWN"
  else
    LOGS=$(docker logs "$container" --since 24h 2>&1 | tail -500)
    ERROR_COUNT=$(echo "$LOGS" | grep -ciE "error|exception|fatal" 2>/dev/null) || ERROR_COUNT=0
    WARN_COUNT=$(echo "$LOGS" | grep -ciE "warn(ing)?" 2>/dev/null) || WARN_COUNT=0
    HTTP_5XX=$(echo "$LOGS" | grep -cE ' 5[0-9][0-9] ' 2>/dev/null) || HTTP_5XX=0
    HTTP_4XX=$(echo "$LOGS" | grep -cE ' 4[0-9][0-9] ' 2>/dev/null) || HTTP_4XX=0

    # Normalize to integers
    ERROR_COUNT=${ERROR_COUNT//[^0-9]/}; ERROR_COUNT=${ERROR_COUNT:-0}
    WARN_COUNT=${WARN_COUNT//[^0-9]/};   WARN_COUNT=${WARN_COUNT:-0}
    HTTP_5XX=${HTTP_5XX//[^0-9]/};       HTTP_5XX=${HTTP_5XX:-0}
    HTTP_4XX=${HTTP_4XX//[^0-9]/};       HTTP_4XX=${HTTP_4XX:-0}

    [ "$ERROR_COUNT" -gt 50 ] || [ "$HTTP_5XX" -gt 20 ] && SEVERITY="critical"
    [ "$SEVERITY" = "ok" ] && { [ "$ERROR_COUNT" -gt 10 ] || [ "$HTTP_5XX" -gt 5 ]; } && SEVERITY="high"
    [ "$SEVERITY" = "ok" ] && { [ "$ERROR_COUNT" -gt 3 ] || [ "$WARN_COUNT" -gt 20 ]; } && SEVERITY="medium"

    echo "[dream-cycle] $container: errors=$ERROR_COUNT warns=$WARN_COUNT 5xx=$HTTP_5XX severity=$SEVERITY"
  fi

  # Append to JSON array using python3
  python3 - << PYEOF
import json
with open("$STATS_FILE") as f:
    arr = json.load(f)
arr.append({
    "container": "$container",
    "status": "$STATUS",
    "severity": "$SEVERITY",
    "error_count": $ERROR_COUNT,
    "warn_count": $WARN_COUNT,
    "http_5xx": $HTTP_5XX,
    "http_4xx": $HTTP_4XX,
})
with open("$STATS_FILE", "w") as f:
    json.dump(arr, f)
PYEOF
done

# Guard Brasil specific: count API calls
GUARD_CALLS=$(docker logs guard-brasil-api --since 24h 2>&1 | grep -c "POST /v1/inspect" 2>/dev/null) || GUARD_CALLS=0
GUARD_CALLS=${GUARD_CALLS//[^0-9]/}; GUARD_CALLS=${GUARD_CALLS:-0}
echo "[dream-cycle] Guard Brasil /v1/inspect calls last 24h: $GUARD_CALLS"

# Compute summary
CRITICAL_COUNT=$(python3 -c "
import json
with open('$STATS_FILE') as f: arr = json.load(f)
print(sum(1 for i in arr if i.get('severity')=='critical'))
")
DOWN_COUNT=$(python3 -c "
import json
with open('$STATS_FILE') as f: arr = json.load(f)
print(sum(1 for i in arr if i.get('status')=='down'))
")

# Write final JSON report
python3 - << PYEOF
import json, datetime
with open("$STATS_FILE") as f:
    containers = json.load(f)
report = {
    "date": "$DATE",
    "timestamp": "$TIMESTAMP",
    "summary": {
        "containers_checked": len(containers),
        "critical_issues": $CRITICAL_COUNT,
        "containers_down": $DOWN_COUNT,
        "guard_brasil_calls_24h": $GUARD_CALLS,
    },
    "containers": containers,
}
with open("$REPORT_FILE", "w") as f:
    json.dump(report, f, indent=2)
print(f"[dream-cycle] Report: {json.dumps(report['summary'])}")
PYEOF

# Push to Supabase
if [ -n "${SUPABASE_URL:-}" ] && [ -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
  PAYLOAD=$(python3 -c "
import json
with open('$REPORT_FILE') as f: r = json.load(f)
print(json.dumps([{
    'date': r['date'],
    'summary': json.dumps(r['summary']),
    'containers': json.dumps(r['containers']),
    'critical_count': r['summary']['critical_issues'],
    'guard_calls_24h': r['summary']['guard_brasil_calls_24h'],
}]))
")
  curl -sf -X POST "${SUPABASE_URL}/rest/v1/egos_nightly_logs" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" \
    -H "Prefer: return=minimal" \
    -d "$PAYLOAD" && echo "[dream-cycle] Supabase: OK" || echo "[dream-cycle] Supabase: push failed"
fi

# Telegram alert if critical
if [ "${CRITICAL_COUNT:-0}" -gt 0 ] || [ "${DOWN_COUNT:-0}" -gt 0 ]; then
  if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_AUTHORIZED_USER_ID:-}" ]; then
    MSG="🚨 EGOS Dream Cycle (${DATE})%0ACritical: ${CRITICAL_COUNT} | Down: ${DOWN_COUNT}%0AGuard Brasil calls: ${GUARD_CALLS}%0Ahq.egos.ia.br"
    curl -sf "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage?chat_id=${TELEGRAM_AUTHORIZED_USER_ID}&text=${MSG}" > /dev/null \
      && echo "[dream-cycle] Telegram alert sent" || echo "[dream-cycle] Telegram: send failed"
  fi
fi

rm -f "$STATS_FILE"
echo "[dream-cycle] Done. Critical=${CRITICAL_COUNT} Down=${DOWN_COUNT} GuardCalls=${GUARD_CALLS}"
