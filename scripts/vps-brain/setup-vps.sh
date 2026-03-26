#!/bin/bash
# EGOS VPS Brain Setup
# Instala claude CLI + configura sessão tmux persistente + multi-provider stack
# Rode: bash setup-vps.sh
# Requer: VPS acessível via SSH como "contabo"

set -e
VPS="contabo"
EGOS_VPS_DIR="/root/egos-brain"

echo "🚀 EGOS VPS Brain Setup"
echo "========================"

# 1. Instala claude no VPS
echo ""
echo "📦 [1/5] Instalando Claude Code no VPS..."
ssh $VPS "npm install -g @anthropic-ai/claude-code 2>&1 | tail -3"
ssh $VPS "claude --version"

# 2. Sync credenciais (OAuth token do claude.ai Pro)
echo ""
echo "🔐 [2/5] Sincronizando credenciais claude..."
ssh $VPS "mkdir -p /root/.claude"
scp ~/.claude/.credentials.json $VPS:/root/.claude/.credentials.json
ssh $VPS "chmod 600 /root/.claude/.credentials.json"
echo "✅ Credenciais sincronizadas"

# 3. Sync configuração claude
echo ""
echo "⚙️  [3/5] Sincronizando settings claude..."
scp ~/.claude/settings.json $VPS:/root/.claude/settings.json 2>/dev/null || true

# 4. Cria estrutura EGOS no VPS
echo ""
echo "📁 [4/5] Criando estrutura EGOS no VPS..."
ssh $VPS "mkdir -p $EGOS_VPS_DIR/{jobs,queue,results,logs}"

# Copia orchestrator e scripts
scp /home/enio/egos/scripts/vps-brain/orchestrator.py $VPS:$EGOS_VPS_DIR/
scp /home/enio/egos/scripts/vps-brain/job-runner.sh    $VPS:$EGOS_VPS_DIR/
scp /home/enio/egos/scripts/token-scheduler/pending-tasks.json $VPS:$EGOS_VPS_DIR/jobs/

# 5. Inicia sessão tmux persistente com claude
echo ""
echo "🖥️  [5/5] Iniciando sessão tmux 'egos-brain'..."
ssh $VPS "
  # Encerra sessão antiga se existir
  tmux kill-session -t egos-brain 2>/dev/null || true

  # Cria nova sessão em background
  tmux new-session -d -s egos-brain -x 220 -y 50

  # Aguarda inicialização
  sleep 1

  # Verifica se está rodando
  tmux list-sessions | grep egos-brain
  echo '✅ Sessão tmux egos-brain iniciada'
"

echo ""
echo "✅ SETUP COMPLETO!"
echo ""
echo "Comandos úteis:"
echo "  ssh contabo 'tmux attach -t egos-brain'  → ver sessão ao vivo"
echo "  bash sync-credentials.sh                  → re-sync quando token expirar"
echo "  python3 orchestrator.py --run              → executar próxima task"
echo ""
