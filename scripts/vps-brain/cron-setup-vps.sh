#!/bin/bash
# Configura os crons no VPS depois do setup
# Execute no VPS: bash cron-setup-vps.sh
# Ou execute local: ssh contabo "bash /root/egos-brain/cron-setup-vps.sh"

BRAIN_DIR="/root/egos-brain"
LOG="$BRAIN_DIR/logs/cron.log"

echo "⚙️  Configurando crons no VPS..."

# Carrega env vars com API keys
ENV_LOADER="source /root/.env_egos 2>/dev/null || true"

# Remove crons EGOS antigos
existing=$(crontab -l 2>/dev/null | grep -v "EGOS-VPS\|orchestrator.py")

new_crons="
# EGOS-VPS: Orchestrator — executa tasks a cada 2h (usa melhor provider disponível)
0 */2 * * * $ENV_LOADER && python3 $BRAIN_DIR/orchestrator.py --run >> $LOG 2>&1

# EGOS-VPS: Gem Hunter — pesquisa semanal scraping tools
7 12 * * 1 python3 /root/egos/scripts/gem-hunter/gem-hunter.py --topic scraping >> $LOG 2>&1

# EGOS-VPS: Gem Hunter — pesquisa semanal AI tools
7 12 * * 3 python3 /root/egos/scripts/gem-hunter/gem-hunter.py --topic ai-agents >> $LOG 2>&1

# EGOS-VPS: Health check claude credentials (toda manhã)
0 8 * * * claude --model claude-haiku-4-5-20251001 --print 'responda: OK' > /tmp/claude-health.txt 2>&1 || echo 'CREDENTIAL EXPIRED — run sync-credentials.sh' >> $LOG
"

echo "$existing$new_crons" | crontab -
echo "✅ Crons configurados no VPS"
crontab -l | grep "EGOS-VPS"
