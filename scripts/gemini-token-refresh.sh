#!/bin/bash
# GEM-TOKEN-001: Gemini CLI Token Refresh
# Cron: */2 * * * * bash /opt/egos/bin/gemini-token-refresh.sh
# Pattern: Similar to Codex proxy refresh (packages/shared/orchestrator/codex-proxy.ts)

set -e

LOG_FILE="/var/log/egos/gemini-token-refresh.log"
GEMINI_CONFIG="${HOME}/.config/gcloud/application_default_credentials.json"
BACKUP_CONFIG="${HOME}/.config/gcloud/application_default_credentials.backup.json"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"

# Ensure log directory
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Validate token freshness
validate_token() {
    if [[ ! -f "$GEMINI_CONFIG" ]]; then
        log "ERROR: Gemini config not found at $GEMINI_CONFIG"
        return 1
    fi

    # Extract expiry time from token (if JWT)
    local expiry=$(cat "$GEMINI_CONFIG" | jq -r '.expiry_date // .expires_at // empty' 2>/dev/null || echo "")

    if [[ -z "$expiry" ]]; then
        log "WARN: Could not extract expiry from token (using file mtime as fallback)"
        # Use file modification time as fallback
        expiry=$(stat -c %Y "$GEMINI_CONFIG" 2>/dev/null || stat -f %m "$GEMINI_CONFIG" 2>/dev/null || echo "0")
    fi

    # Convert to timestamp if needed and check if < 15 min from now
    local now=$(date +%s)
    local expiry_epoch=$(date -d "$expiry" +%s 2>/dev/null || echo "$expiry")

    if (( expiry_epoch - now < 900 )); then
        log "TOKEN EXPIRING: $((expiry_epoch - now))s remaining"
        return 1
    else
        log "TOKEN OK: $((expiry_epoch - now))s remaining"
        return 0
    fi
}

# Refresh token via gcloud
refresh_token() {
    log "Refreshing Gemini CLI token..."

    # Backup current config
    if [[ -f "$GEMINI_CONFIG" ]]; then
        cp "$GEMINI_CONFIG" "$BACKUP_CONFIG"
        log "Backup saved: $BACKUP_CONFIG"
    fi

    # Refresh via gcloud CLI
    if command -v gcloud &> /dev/null; then
        if gcloud auth application-default print-access-token > /dev/null 2>&1; then
            log "✓ Token refreshed via gcloud"
            return 0
        else
            log "ERROR: gcloud refresh failed"
            return 1
        fi
    fi

    # Fallback: refresh via Google OAuth (requires GOOGLE_APPLICATION_CREDENTIALS set)
    if [[ -n "$GOOGLE_APPLICATION_CREDENTIALS" ]]; then
        log "Fallback: attempting OAuth refresh..."
        # This would use a Python script or similar to refresh via Google API
        # For now, log and alert
        log "WARN: Fallback OAuth not implemented yet"
        return 1
    fi

    return 1
}

# Alert on failure
alert_failure() {
    local msg="$1"

    if [[ -n "$TELEGRAM_BOT_TOKEN" ]] && [[ -n "$TELEGRAM_CHAT_ID" ]]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TELEGRAM_CHAT_ID}" \
            -d "text=🚨 **Gemini Token Issue**

$msg

Action: Check /var/log/egos/gemini-token-refresh.log

Timestamp: $(date +'%Y-%m-%d %H:%M:%S %Z')" \
            -d "parse_mode=Markdown" > /dev/null 2>&1

        log "Telegram alert sent"
    fi
}

# Fallback chain if token refresh fails
fallback_chain() {
    log "TOKEN REFRESH FAILED: Activating fallback chain..."

    # Option 1: Try DashScope (free tier, same Gemini API)
    if [[ -n "$DASHSCOPE_API_KEY" ]]; then
        log "✓ Fallback 1: Routing to DashScope (free tier)"
        # Code in orchestrator will check GEMINI_STATUS and route accordingly
        export GEMINI_STATUS="fallback_dashscope"
        return 0
    fi

    # Option 2: Try MiniMax-M2.7 (paid, cheaper than Claude)
    if [[ -n "$MINIMAX_API_KEY" ]]; then
        log "✓ Fallback 2: Routing to MiniMax-M2.7"
        export GEMINI_STATUS="fallback_minimax"
        return 0
    fi

    # Option 3: Route to Claude Code (most expensive, but available)
    log "⚠️ Fallback 3: Queuing to Claude Code session (expensive)"
    export GEMINI_STATUS="fallback_claude"
    return 0
}

# Main routine
main() {
    log "=============== Gemini Token Refresh Check ==============="

    # Step 1: Validate current token
    if validate_token; then
        log "Status: Token is fresh, no action needed"
        export GEMINI_STATUS="ok"
        return 0
    fi

    # Step 2: Attempt refresh
    log "Token expiring soon or invalid, attempting refresh..."
    if refresh_token; then
        log "Status: Token refresh SUCCESS"
        export GEMINI_STATUS="ok"
        return 0
    fi

    # Step 3: Fallback chain
    log "Status: Token refresh FAILED, activating fallback chain"
    if fallback_chain; then
        alert_failure "Gemini token refresh failed. Using fallback: $GEMINI_STATUS"
        export GEMINI_STATUS
        return 0
    fi

    # Step 4: Critical failure
    log "Status: ALL fallbacks exhausted"
    alert_failure "CRITICAL: Gemini token refresh and all fallbacks failed. Manual intervention required."
    export GEMINI_STATUS="critical_failure"
    return 1
}

# Execute
main "$@"

# Export status for orchestrator to consume
if [[ -f "/tmp/gemini-status.env" ]]; then
    source "/tmp/gemini-status.env"
fi
echo "GEMINI_STATUS=${GEMINI_STATUS:-ok}" > /tmp/gemini-status.env

log "Status exported to /tmp/gemini-status.env"
