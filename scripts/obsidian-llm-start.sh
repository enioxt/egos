#!/bin/bash
# Quick start script for Obsidian + LLM integration

echo "🚀 Obsidian LLM Quick Start"
echo "============================"
echo ""

VAULT_PATH="/home/enio/Obsidian Vault/EGOS"
CONFIG_FILE="/home/enio/egos/.obsidian-llm-config.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if vault exists
if [ ! -d "$VAULT_PATH" ]; then
    echo -e "${RED}❌ Vault não encontrado em: $VAULT_PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Vault encontrado${NC}: $VAULT_PATH"

# Check API keys
if [ -z "$ALIBABA_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  ALIBABA_API_KEY não configurada${NC}"
    echo "   Configure: export ALIBABA_API_KEY=sk-xxxxx"
fi

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  OPENROUTER_API_KEY não configurada${NC}"
    echo "   Configure: export OPENROUTER_API_KEY=sk-or-v1-xxxxx"
fi

echo ""
echo "📋 Configuração do Obsidian Copilot:"
echo "   1. Abra Obsidian"
echo "   2. Ctrl+P → 'Copilot: Chat'"
echo "   3. Settings → OpenAI Format → Custom Model"
echo ""
echo "   Alibaba DashScope:"
echo "      Base URL: https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
echo "      Model: qwen-plus"
echo ""
echo "   OpenRouter:"
echo "      Base URL: https://openrouter.ai/api/v1"
echo "      Model: anthropic/claude-3.7-sonnet"
echo ""

# List vault structure
echo "📁 Estrutura do Vault:"
ls -la "$VAULT_PATH" | grep "^d" | tail -n +2 | awk '{print "   " $NF}'

echo ""
echo "🔗 MCP Servers configurados em: /home/enio/egos/.mcp.json"
echo "   - egos-memory: Memória persistente"
echo "   - egos-governance: Governança EGOS"
echo "   - obsidian: Acesso ao vault"
echo ""
echo "📝 Próximos passos:"
echo "   1. Instale 'Local REST API' plugin no Obsidian"
echo "   2. Execute: bash /home/enio/egos/scripts/setup-obsidian-mcp.sh"
echo "   3. Configure API keys no seu .bashrc ou .zshrc"
echo ""
