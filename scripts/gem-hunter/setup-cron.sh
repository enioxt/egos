#!/bin/bash
# EGOS Gem Hunter + Token Scheduler — Setup de Crons
# Executa: bash setup-cron.sh

set -e

EGOS_ROOT="/home/enio/egos"
GEM_HUNTER="$EGOS_ROOT/scripts/gem-hunter/gem-hunter.py"
SCHEDULER="$EGOS_ROOT/scripts/token-scheduler/scheduler.py"

echo "🔧 Configurando crons EGOS..."

# Preserva crons existentes
existing_crons=$(crontab -l 2>/dev/null || echo "")

# Remove entradas EGOS antigas para evitar duplicatas
clean_crons=$(echo "$existing_crons" | grep -v "EGOS-GEM-HUNTER\|EGOS-SCHEDULER\|gem-hunter.py\|scheduler.py")

# Novos crons EGOS
new_crons="
# EGOS-GEM-HUNTER: Pesquisa de gemas por tópico (semanal)
0 9 * * 1 python3 $GEM_HUNTER --topic scraping >> $EGOS_ROOT/logs/gem-hunter.log 2>&1
0 9 * * 3 python3 $GEM_HUNTER --topic ai-agents >> $EGOS_ROOT/logs/gem-hunter.log 2>&1
0 9 * * 5 python3 $GEM_HUNTER --topic security >> $EGOS_ROOT/logs/gem-hunter.log 2>&1

# EGOS-SCHEDULER: Verifica status da janela de tokens (a cada hora)
0 * * * * python3 $SCHEDULER status >> $EGOS_ROOT/logs/scheduler.log 2>&1
"

# Aplica crons
echo "$clean_crons$new_crons" | crontab -

echo "✅ Crons configurados:"
echo ""
echo "  Seg 09:00 — Gem Hunter: scraping (Cloudflare bypass, TLS)"
echo "  Qua 09:00 — Gem Hunter: ai-agents (Agent frameworks)"
echo "  Sex 09:00 — Gem Hunter: security (CVEs, zero-days)"
echo "  Toda hora — Scheduler: status da janela de tokens"
echo ""
echo "Logs em: $EGOS_ROOT/logs/"
echo ""
echo "📋 Crontab atual:"
crontab -l | grep -A1 "EGOS"
