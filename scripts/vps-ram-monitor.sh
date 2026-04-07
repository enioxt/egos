#!/bin/bash
# VPS-MEMORY-001: RAM Monitoring with Telegram Alerts
# Runs via cron: */5 * * * * bash /opt/egos/bin/vps-ram-monitor.sh
# Alerts: <1GB (info), <500MB (warning), <100MB (critical)

set -e

# Load VPS config
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"
LOG_FILE="/var/log/egos/ram-monitor.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Get current RAM state
read_ram_state() {
    # free -b: bytes; awk gets available RAM (including buffers/cache)
    local available=$(free -b | grep "^Mem:" | awk '{print $7}')
    echo "$available"
}

# Convert bytes to MB
bytes_to_mb() {
    echo "scale=0; $1 / 1024 / 1024" | bc
}

# Convert bytes to GB
bytes_to_gb() {
    echo "scale=2; $1 / 1024 / 1024 / 1024" | bc
}

# Send Telegram alert
send_alert() {
    local level="$1"
    local message="$2"

    if [[ -z "$TELEGRAM_BOT_TOKEN" ]] || [[ -z "$TELEGRAM_CHAT_ID" ]]; then
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: Telegram not configured, alert skipped" | tee -a "$LOG_FILE"
        return 1
    fi

    local emoji="ℹ️"
    [[ "$level" == "warning" ]] && emoji="⚠️"
    [[ "$level" == "critical" ]] && emoji="🚨"

    local full_msg="$emoji **VPS RAM Alert** ($level)

$message

🖥️ Timestamp: $(date +'%Y-%m-%d %H:%M:%S %Z')"

    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "text=${full_msg}" \
        -d "parse_mode=Markdown" > /dev/null 2>&1

    echo "[$(date +'%Y-%m-%d %H:%M:%S')] Telegram alert sent ($level)" | tee -a "$LOG_FILE"
}

# Main monitoring logic
main() {
    local available=$(read_ram_state)
    local available_mb=$(bytes_to_mb "$available")
    local available_gb=$(bytes_to_gb "$available")
    local total=$(free -b | grep "^Mem:" | awk '{print $2}')
    local total_gb=$(bytes_to_gb "$total")
    local used=$(free -b | grep "^Mem:" | awk '{print $3}')
    local used_gb=$(bytes_to_gb "$used")

    # Log current state
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] RAM: ${available_mb}MB free (${available_gb}GB) / ${total_gb}GB total (${used_gb}GB used)" >> "$LOG_FILE"

    # CRITICAL: < 100MB
    if [[ "$available" -lt 104857600 ]]; then
        local msg="CRITICAL: Only ${available_mb}MB (${available_gb}GB) RAM available!

**Action Required:**
- Kill non-critical containers (except Neo4j)
- Consider emergency swap usage
- Check for memory leaks"

        send_alert "critical" "$msg"

        # Log and potentially trigger emergency measures
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] CRITICAL: RAM < 100MB" | tee -a "$LOG_FILE"

        # Optional: Auto-kill non-critical containers (disabled by default, requires manual approval)
        # docker ps --format='table {{.Names}}\t{{.MemoryUsage}}' | grep -vE 'neo4j|egos-hq' | ...

    # WARNING: < 500MB
    elif [[ "$available" -lt 524288000 ]]; then
        local msg="WARNING: Low RAM available (${available_mb}MB / ${available_gb}GB)

Current state:
- Neo4j may be approaching limit
- New container deployment risky
- Consider Neo4j heap tuning (VPS-NEO4J-TUNE-001)

Threshold: < 500MB triggers this alert"

        send_alert "warning" "$msg"
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: RAM < 500MB" | tee -a "$LOG_FILE"

    # INFO: < 1GB
    elif [[ "$available" -lt 1073741824 ]]; then
        local msg="INFO: RAM monitor (below 1GB threshold)

Available: ${available_mb}MB (${available_gb}GB)
Total: ${total_gb}GB
Used: ${used_gb}GB

Next checks:
- VPS-NEO4J-TUNE-001 (heap analysis)
- VPS-CAPACITY-001 (capacity model)

Threshold: < 1GB triggers this alert"

        send_alert "info" "$msg"
        echo "[$(date +'%Y-%m-%d %H:%M:%S')] INFO: RAM < 1GB" | tee -a "$LOG_FILE"
    fi

    # Always log to monitoring system (optional: push to Supabase)
    # curl -s -X POST "http://localhost:3000/api/vps/memory" \
    #     -H "Content-Type: application/json" \
    #     -d "{\"available_mb\": $available_mb, \"total_gb\": $total_gb, \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
}

# Execute
main "$@"
