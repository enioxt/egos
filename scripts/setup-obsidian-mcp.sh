#!/bin/bash
# Setup script for Obsidian MCP integration

echo "=== Obsidian MCP Setup ==="
echo ""

# Check Node.js and npx
if ! command -v npx &> /dev/null; then
    echo "❌ npx não encontrado. Instalando Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

echo "✅ npx encontrado"

# Install Smithery CLI globally
echo "📦 Instalando @smithery/cli..."
npm install -g @smithery/cli@latest

# Test MCP connection
echo "🧪 Testando conexão MCP com Obsidian..."
npx @smithery/cli@latest inspect @smithery/mcp-obsidian

echo ""
echo "=== Setup completo ==="
echo "MCP config: ~/.config/mcp/obsidian-mcp.json"
echo "Vault path: /home/enio/Obsidian Vault/EGOS"
echo ""
echo "⚠️  IMPORTANTE: Instale o plugin 'Local REST API' no Obsidian:"
echo "   1. Abra Obsidian → Configurações → Plugins da Comunidade"
echo "   2. Procure 'Local REST API' (by Adam Coddington)"
echo "   3. Instale e ative"
echo "   4. Copie a API Key gerada"
echo ""
