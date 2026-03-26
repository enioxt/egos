#!/bin/bash
# Sincroniza credenciais claude Pro para o VPS
# Execute quando o token expirar: bash sync-credentials.sh

VPS="contabo"

echo "🔐 Sincronizando credenciais claude.ai Pro → VPS..."
ssh $VPS "mkdir -p /root/.claude && chmod 700 /root/.claude"
scp ~/.claude/.credentials.json $VPS:/root/.claude/.credentials.json
ssh $VPS "chmod 600 /root/.claude/.credentials.json"

# Testa no VPS
echo "🧪 Testando claude no VPS..."
ssh $VPS "claude --model claude-haiku-4-5-20251001 --print 'responda: VPS OK' 2>&1"
echo "✅ Sync completo"
