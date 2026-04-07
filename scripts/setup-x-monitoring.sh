#!/bin/bash
#
# 🚀 Setup X.com Monitoring System
# 
# Configura o sistema completo de monitoramento de oportunidades X.com
# no VPS Hetzner com cron jobs e serviços systemd
#
# Usage: bash scripts/setup-x-monitoring.sh [--check]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EGOS_DIR="$(dirname "$SCRIPT_DIR")"
VPS_HOST="${VPS_HOST:-hetzner}"
REMOTE_DIR="/opt/x-automation"  # NOT /opt/xmcp (used by X MCP server)
DRY_RUN=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Parse args
if [[ "$1" == "--check" ]]; then
    CHECK_MODE=true
else
    CHECK_MODE=false
fi

if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    log_info "Modo DRY-RUN — nenhuma mudança será aplicada"
fi

echo "═══════════════════════════════════════════════════════════════"
echo "  🐦 X.com Monitoring System — Setup"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# ── 1. Check Local Environment ─────────────────────────────────────────────

log_info "Verificando ambiente local..."

# Check env files
if [[ -f "$HOME/.egos/secrets.env" ]]; then
    log_success "~/.egos/secrets.env encontrado"
    
    # Source it to check variables
    set -a
    source "$HOME/.egos/secrets.env" 2>/dev/null || true
    set +a
    
    # Check X credentials
    if [[ -n "$X_BEARER_TOKEN" && -n "$X_API_KEY" && -n "$X_ACCESS_TOKEN" ]]; then
        log_success "X API credentials configuradas"
    else
        log_error "X API credentials INCOMPLETAS"
        log_info "Adicione em ~/.egos/secrets.env:"
        log_info "  X_API_KEY=..."
        log_info "  X_API_SECRET=..."
        log_info "  X_ACCESS_TOKEN=..."
        log_info "  X_ACCESS_TOKEN_SECRET=..."
        log_info "  X_BEARER_TOKEN=..."
        exit 1
    fi
    
    # Check Telegram
    if [[ -n "$TELEGRAM_BOT_TOKEN" && -n "$TELEGRAM_ADMIN_CHAT_ID" ]]; then
        log_success "Telegram configurado"
    else
        log_warn "Telegram NÃO configurado (opcional, mas recomendado)"
    fi
else
    log_error "~/.egos/secrets.env NÃO ENCONTRADO"
    log_info "Crie o arquivo com as credenciais X e Telegram"
    exit 1
fi

# Check scripts exist
if [[ -f "$EGOS_DIR/scripts/x-opportunity-alert.ts" ]]; then
    log_success "x-opportunity-alert.ts encontrado"
else
    log_error "x-opportunity-alert.ts NÃO ENCONTRADO"
    exit 1
fi

if [[ -f "$EGOS_DIR/scripts/x-approval-bot.ts" ]]; then
    log_success "x-approval-bot.ts encontrado"
else
    log_error "x-approval-bot.ts NÃO ENCONTRADO"
    exit 1
fi

echo ""

# ── 2. Check VPS Connection ───────────────────────────────────────────────

log_info "Verificando conexão com VPS..."

if ssh -o ConnectTimeout=5 "$VPS_HOST" "echo 'OK'" 2>/dev/null | grep -q "OK"; then
    log_success "Conexão SSH com $VPS_HOST OK"
else
    log_error "Não foi possível conectar ao VPS $VPS_HOST"
    log_info "Verifique:"
    log_info "  1. Se ~/.ssh/config tem configuração para 'hetzner'"
    log_info "  2. Se a chave SSH está adicionada ao agente"
    log_info "  3. Se o VPS está online"
    exit 1
fi

# Check if directory exists on VPS
if ssh "$VPS_HOST" "test -d $REMOTE_DIR" 2>/dev/null; then
    log_success "Diretório $REMOTE_DIR existe no VPS"
else
    log_warn "Diretório $REMOTE_DIR não existe no VPS"
    log_info "Será criado durante o setup"
fi

echo ""

# ── 3. Deploy Files ───────────────────────────────────────────────────────

if [[ "$CHECK_MODE" == true ]]; then
    log_info "Modo CHECK — pulando deploy"
else
    log_info "Deployando arquivos para VPS..."
    
    if [[ "$DRY_RUN" == true ]]; then
        log_info "[DRY-RUN] Simulando deploy..."
        log_info "  → Copiar scripts/x-opportunity-alert.ts → $REMOTE_DIR/"
        log_info "  → Copiar scripts/x-approval-bot.ts → $REMOTE_DIR/"
        log_info "  → Copiar ~/.egos/secrets.env → $REMOTE_DIR/.env"
    else
        # Create remote directory
        ssh "$VPS_HOST" "mkdir -p $REMOTE_DIR"
        
        # Copy scripts
        scp "$EGOS_DIR/scripts/x-opportunity-alert.ts" "$VPS_HOST:$REMOTE_DIR/"
        scp "$EGOS_DIR/scripts/x-approval-bot.ts" "$VPS_HOST:$REMOTE_DIR/"
        
        # Copy env file
        scp "$HOME/.egos/secrets.env" "$VPS_HOST:$REMOTE_DIR/.env"
        
        # Create logs directory
        ssh "$VPS_HOST" "mkdir -p $REMOTE_DIR/logs"
        
        log_success "Arquivos copiados para VPS"
    fi
fi

echo ""

# ── 4. Setup Cron Jobs ────────────────────────────────────────────────────

log_info "Configurando cron jobs..."

CRON_ALERT="# X Opportunity Alert — a cada 2 horas
0 */2 * * * cd $REMOTE_DIR && /usr/local/bin/bun x-opportunity-alert.ts >> logs/alert.log 2>&1
"

CRON_STATUS="# X Status — resumo diário às 9h
0 9 * * * cd $REMOTE_DIR && /usr/local/bin/bun x-opportunity-alert.ts --status >> logs/status.log 2>&1
"

if [[ "$CHECK_MODE" == true ]]; then
    log_info "Modo CHECK — pulando cron setup"
elif [[ "$DRY_RUN" == true ]]; then
    log_info "[DRY-RUN] Simulando cron setup..."
    log_info "  → Adicionar cron: a cada 2h x-opportunity-alert.ts"
    log_info "  → Adicionar cron: 9h daily status report"
else
    # Install cron jobs
    ssh "$VPS_HOST" "(crontab -l 2>/dev/null | grep -v 'x-opportunity-alert'; echo \"$CRON_ALERT\") | crontab -"
    log_success "Cron job para x-opportunity-alert.ts configurado"
fi

echo ""

# ── 5. Setup Systemd Service (Approval Bot) ─────────────────────────────────

log_info "Configurando serviço systemd (Approval Bot)..."

SYSTEMD_SERVICE="[Unit]
Description=X Approval Bot (Telegram)
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$REMOTE_DIR
Environment=TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN
Environment=TELEGRAM_ADMIN_CHAT_ID=$TELEGRAM_ADMIN_CHAT_ID
ExecStart=/usr/local/bin/bun x-approval-bot.ts
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"

if [[ "$CHECK_MODE" == true ]]; then
    log_info "Modo CHECK — pulando systemd setup"
elif [[ "$DRY_RUN" == true ]]; then
    log_info "[DRY-RUN] Simulando systemd setup..."
    log_info "  → Criar: /etc/systemd/system/x-approval-bot.service"
    log_info "  → systemctl enable x-approval-bot"
    log_info "  → systemctl start x-approval-bot"
else
    # Create systemd service file
    echo "$SYSTEMD_SERVICE" | ssh "$VPS_HOST" "sudo tee /etc/systemd/system/x-approval-bot.service > /dev/null"
    
    # Reload and enable
    ssh "$VPS_HOST" "sudo systemctl daemon-reload"
    ssh "$VPS_HOST" "sudo systemctl enable x-approval-bot"
    
    log_success "Serviço systemd x-approval-bot configurado"
    
    # Ask if should start now
    log_info "Para iniciar o bot agora, execute no VPS:"
    log_info "  sudo systemctl start x-approval-bot"
fi

echo ""

# ── 6. Test Configuration ─────────────────────────────────────────────────

log_info "Testando configuração..."

if [[ "$CHECK_MODE" == true || "$DRY_RUN" == true ]]; then
    log_info "Pulando testes (modo check/dry-run)"
else
    # Test alert system (dry-run on VPS)
    log_info "Testando x-opportunity-alert.ts..."
    ssh "$VPS_HOST" "cd $REMOTE_DIR && /usr/local/bin/bun x-opportunity-alert.ts --dry-run" || {
        log_warn "Teste falhou — verifique logs"
    }
fi

echo ""

# ── 7. Summary ──────────────────────────────────────────────────────────────

echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ Setup Completo!"
echo "═══════════════════════════════════════════════════════════════"
echo ""

if [[ "$CHECK_MODE" == true ]]; then
    echo "Modo CHECK concluído — nenhuma mudança aplicada"
elif [[ "$DRY_RUN" == true ]]; then
    echo "Modo DRY-RUN concluído — nenhuma mudança aplicada"
    echo "Execute sem --dry-run para aplicar:"
    echo "  bash scripts/setup-x-monitoring.sh"
else
    log_success "Sistema de monitoramento X.com configurado!"
    echo ""
    echo "📋 Resumo:"
    echo "  • Alertas: a cada 2h via cron"
    echo "  • Aprovação: bot Telegram rodando 24/7"
    echo "  • Logs: $REMOTE_DIR/logs/"
    echo ""
    echo "🚀 Comandos úteis:"
    echo "  Ver logs:        ssh $VPS_HOST 'tail -f $REMOTE_DIR/logs/alert.log'"
    echo "  Status bot:      ssh $VPS_HOST 'sudo systemctl status x-approval-bot'"
    echo "  Restart bot:     ssh $VPS_HOST 'sudo systemctl restart x-approval-bot'"
    echo "  Testar alerta:   ssh $VPS_HOST 'cd $REMOTE_DIR && bun x-opportunity-alert.ts --test-alert'"
    echo ""
    echo "📱 Telegram:"
    echo "  Envie /start para @seu_bot para ver comandos"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
