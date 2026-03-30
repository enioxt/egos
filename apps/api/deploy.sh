#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# deploy.sh — Deploy Guard Brasil API to Hetzner
#
# Usage:
#   bash apps/api/deploy.sh              # deploy/update
#   bash apps/api/deploy.sh --logs       # tail logs after deploy
#   bash apps/api/deploy.sh --restart    # restart only (no rebuild)
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

HETZNER="root@204.168.217.125"
SSH_KEY="$HOME/.ssh/hetzner_ed25519"
REMOTE_DIR="/opt/apps/guard-brasil"
LOCAL_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

SHOW_LOGS=false
RESTART_ONLY=false
for arg in "$@"; do
  case "$arg" in
    --logs)    SHOW_LOGS=true ;;
    --restart) RESTART_ONLY=true ;;
  esac
done

echo "🛡️  Guard Brasil API — Deploy to Hetzner"
echo "   Source: $LOCAL_ROOT"
echo "   Target: $HETZNER:$REMOTE_DIR"
echo ""

# ─── 1. Sync source ───────────────────────────────────────────────────────────
if ! $RESTART_ONLY; then
  echo "📦 Syncing source code..."
  ssh -i "$SSH_KEY" "$HETZNER" "mkdir -p $REMOTE_DIR"

  rsync -az --delete \
    --exclude '.git' \
    --exclude 'node_modules' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude 'dist/' \
    -e "ssh -i $SSH_KEY" \
    "$LOCAL_ROOT/packages/guard-brasil/" \
    "$HETZNER:$REMOTE_DIR/packages/guard-brasil/"

  rsync -az --delete \
    --exclude 'node_modules' \
    -e "ssh -i $SSH_KEY" \
    "$LOCAL_ROOT/apps/api/" \
    "$HETZNER:$REMOTE_DIR/apps/api/"

  echo "✅ Source synced"
fi

# ─── 2. Generate API key if missing ──────────────────────────────────────────
echo ""
echo "🔑 Checking API key..."
ssh -i "$SSH_KEY" "$HETZNER" "
  ENV_FILE='$REMOTE_DIR/.env'
  if [ ! -f \"\$ENV_FILE\" ]; then
    API_KEY=\$(cat /proc/sys/kernel/random/uuid)
    echo \"GUARD_API_KEYS=\$API_KEY\" > \"\$ENV_FILE\"
    echo \"Generated new API key: \$API_KEY\"
  else
    echo \"Existing .env found — keeping keys\"
    cat \"\$ENV_FILE\"
  fi
"

# ─── 3. Build & start ─────────────────────────────────────────────────────────
echo ""
echo "🐳 Building and starting container..."
ssh -i "$SSH_KEY" "$HETZNER" "
  cd $REMOTE_DIR
  docker compose -f apps/api/docker-compose.prod.yml --env-file /opt/apps/guard-brasil/.env down --remove-orphans 2>/dev/null || true
  docker compose -f apps/api/docker-compose.prod.yml --env-file /opt/apps/guard-brasil/.env up -d --build
  sleep 3
  docker compose -f apps/api/docker-compose.prod.yml ps
"

# ─── 4. Health check ──────────────────────────────────────────────────────────
echo ""
echo "🏥 Health check..."
sleep 5
ssh -i "$SSH_KEY" "$HETZNER" "
  curl -sf http://localhost:3099/health | python3 -m json.tool || echo 'Health check failed'
"

# ─── 5. Caddy config ──────────────────────────────────────────────────────────
CADDYFILE="/opt/bracc/infra/Caddyfile"
GUARD_DOMAIN="guard.egos.ia.br"
echo ""
echo "🔀 Checking Caddy config for $GUARD_DOMAIN..."
ssh -i "$SSH_KEY" "$HETZNER" "
  if grep -q '$GUARD_DOMAIN' $CADDYFILE 2>/dev/null; then
    echo 'Caddy entry already exists for $GUARD_DOMAIN'
  else
    echo ''
    echo 'Adding Caddy entry for $GUARD_DOMAIN...'
    cat >> $CADDYFILE << 'CADDY_ENTRY'

$GUARD_DOMAIN {
    reverse_proxy 127.0.0.1:3099

    header {
        X-Content-Type-Options nosniff
        X-Frame-Options DENY
        Strict-Transport-Security \"max-age=63072000; includeSubDomains; preload\"
        Access-Control-Allow-Origin *
        Access-Control-Allow-Methods \"POST, GET, OPTIONS\"
        Access-Control-Allow-Headers \"Content-Type, Authorization\"
        -Server
        -X-Powered-By
    }
}
CADDY_ENTRY
    docker exec infra-caddy-1 caddy reload --config /etc/caddy/Caddyfile 2>/dev/null && echo 'Caddy reloaded ✅' || echo 'Caddy reload failed — check manually'
  fi
"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅  Guard Brasil API deployed!"
echo "   Health:   http://localhost:3099/health (on server)"
echo "   Public:   https://$GUARD_DOMAIN/health"
echo "   Inspect:  POST https://$GUARD_DOMAIN/v1/inspect"
echo ""
echo "   Test:"
echo "   curl -s https://$GUARD_DOMAIN/health"
echo "   curl -s -X POST https://$GUARD_DOMAIN/v1/inspect \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"text\": \"CPF do suspeito: 123.456.789-00\"}'"
echo "═══════════════════════════════════════════════════════════════"

if $SHOW_LOGS; then
  echo ""
  echo "📋 Tailing logs (Ctrl+C to exit)..."
  ssh -i "$SSH_KEY" "$HETZNER" "docker logs -f guard-brasil-api"
fi
