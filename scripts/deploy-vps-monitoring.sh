#!/bin/bash
# Deploy VPS monitoring (VPS-MEMORY-001, VPS-NEO4J-TUNE-001)
# Usage: bash scripts/deploy-vps-monitoring.sh

set -e

VPS_HOST="${VPS_HOST:-root@204.168.217.125}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/hetzner_ed25519}"
MONITOR_SCRIPT="scripts/vps-ram-monitor.sh"

echo "🚀 Deploying VPS monitoring scripts..."

# 1. Verify SSH access
echo "✓ Testing SSH access to VPS..."
ssh -i "$SSH_KEY" "$VPS_HOST" "echo 'SSH OK'; uname -a" || {
    echo "❌ SSH failed. Verify:"
    echo "  - SSH key at: $SSH_KEY"
    echo "  - VPS host: $VPS_HOST"
    exit 1
}

# 2. Deploy RAM monitor script
echo "✓ Deploying RAM monitor script..."
ssh -i "$SSH_KEY" "$VPS_HOST" "mkdir -p /opt/egos/bin /var/log/egos"
scp -i "$SSH_KEY" "$MONITOR_SCRIPT" "$VPS_HOST:/opt/egos/bin/vps-ram-monitor.sh"
ssh -i "$SSH_KEY" "$VPS_HOST" "chmod +x /opt/egos/bin/vps-ram-monitor.sh"

# 3. Setup Telegram env vars (must be configured before this step)
echo "✓ Setting up Telegram configuration..."
ssh -i "$SSH_KEY" "$VPS_HOST" bash <<'TELEGRAMSETUP'
# Source .env or set vars manually
if [ -f /opt/egos/.env ]; then
    source /opt/egos/.env
fi

# Verify Telegram tokens are set
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "⚠️  WARNING: Telegram credentials not found in /opt/egos/.env"
    echo "   Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID before enabling alerts"
fi

echo "✓ Telegram configuration ready"
TELEGRAMSETUP

# 4. Setup cron job (runs every 5 minutes)
echo "✓ Setting up cron job..."
ssh -i "$SSH_KEY" "$VPS_HOST" bash <<'CRONSETUP'
# Export required env vars for cron
(crontab -l 2>/dev/null | grep -v "vps-ram-monitor" || true; \
 echo "*/5 * * * * export TELEGRAM_BOT_TOKEN=\$TELEGRAM_BOT_TOKEN; export TELEGRAM_CHAT_ID=\$TELEGRAM_CHAT_ID; bash /opt/egos/bin/vps-ram-monitor.sh") \
 | crontab -

echo "✓ Cron job installed (*/5 * * * *)"
crontab -l | grep vps-ram-monitor || echo "⚠️  Verify cron was installed"
CRONSETUP

# 5. Test the script
echo "✓ Testing RAM monitor script..."
ssh -i "$SSH_KEY" "$VPS_HOST" "bash /opt/egos/bin/vps-ram-monitor.sh" || {
    echo "⚠️  Script executed but may have warnings (see above)"
}

echo ""
echo "✅ VPS monitoring deployed!"
echo ""
echo "Next steps:"
echo "1. Verify Telegram alerts work: ssh -i $SSH_KEY $VPS_HOST 'tail -f /var/log/egos/ram-monitor.log'"
echo "2. Wait 5 minutes for first cron run"
echo "3. Check Telegram for alert (if free RAM < 1GB)"
echo ""
echo "Configuration:"
echo "- Script: /opt/egos/bin/vps-ram-monitor.sh"
echo "- Cron: */5 * * * * (every 5 minutes)"
echo "- Log: /var/log/egos/ram-monitor.log"
echo "- Alerts: Telegram (requires TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID in .env)"
echo ""
