# Guia de Integração LLM com Obsidian

## TL;DR - Melhores Opções

| Caso de Uso | Plugin/Recomendação | Por Quê |
|-------------|---------------------|---------|
| **Chat com vault** | Obsidian Copilot | Maturidade, múltiplos providers |
| **Busca semântica** | Smart Connections | Embeddings locais, privacidade |
| **Integração externa (Claude/Cursor)** | MCP + Local REST API | 35+ ferramentas nativas |
| **APIs customizadas** | Copilot + Custom Model | OpenRouter, DashScope, etc. |

---

## Opção 1: Obsidian Copilot (Recomendado para iniciar)

### Instalação
1. Abra Obsidian → Configurações → Plugins da Comunidade
2. Desative o "Modo Seguro"
3. Clique "Procurar" → Busque "Copilot"
4. Instale e ative

### Configuração de APIs

#### OpenRouter (Acesso a 100+ modelos)
```
Settings → Copilot → OpenAI Format → Custom Base URL
Base URL: https://openrouter.ai/api/v1
API Key: sk-or-v1-xxxxxxxx
Model: anthropic/claude-3.7-sonnet
```

#### Alibaba DashScope (Qwen)
```
Settings → Copilot → OpenAI Format → Custom Base URL
Base URL: https://dashscope-intl.aliyuncs.com/compatible-mode/v1
API Key: sk-xxxxxxxx
Model: qwen-plus
```

#### Outros providers suportados nativamente
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3.x)
- Google (Gemini)
- Ollama (local)
- LM Studio (local)

---

## Opção 2: MCP (Model Context Protocol) - Integração Avançada

Para conectar **Claude Desktop**, **Cursor**, **Windsurf** ou **Codex** diretamente ao Obsidian:

### Passo 1: Instalar Local REST API no Obsidian
1. Configurações → Plugins da Comunidade
2. Busque "Local REST API" (by Adam Coddington)
3. Instale → Ative
4. Configure API Key (copie para uso posterior)

### Passo 2: Instalar MCPBundles Proxy
```bash
pip install mcpbundles
mcpbundles login
mcpbundles proxy start
```

### Passo 3: Conectar AI Clients

#### Claude Desktop
```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "obsidian": {
      "command": "mcpbundles",
      "args": ["proxy", "start"]
    }
  }
}
```

#### Cursor
Settings → MCP → Add Server → URL do MCPBundles

#### Windsurf/Cascade
Configurado via `.mcp.json` no projeto.

---

## Opção 3: Smart Connections (Busca Semântica)

Melhor para **encontrar notas relacionadas** sem enviar dados para a nuvem.

### Instalação
1. Plugins da Comunidade → "Smart Connections"
2. Escolha embedding:
   - **Local**: all-MiniLM (privado, offline)
   - **API**: OpenAI, Ollama, etc.

### Uso
- Painel lateral mostra notas semanticamente relacionadas
- Chat com vault via Smart Chat (plugin separado)

---

## Configuração Rápida - OpenRouter

OpenRouter é a **melhor opção** para acesso a múltiplos modelos (Claude, GPT, Qwen, etc.):

1. Crie conta: https://openrouter.ai
2. Gere API Key
3. No Copilot settings:
   - **Custom Base URL**: `https://openrouter.ai/api/v1`
   - **API Key**: `sk-or-v1-xxxxx`
   - **Model**: `anthropic/claude-3.7-sonnet` ou `openai/gpt-4o`

---

## Configuração Rápida - Alibaba DashScope

Para usar **Qwen-plus** (modelo usado no EGOS):

1. Crie conta: https://dashscope.console.aliyun.com
2. Gere API Key
3. No Copilot settings:
   - **Custom Base URL**: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
   - **API Key**: `sk-xxxxx`
   - **Model**: `qwen-plus`

---

## Como eu (Cascade/Windsurf) acesso seu Obsidian?

### Opção A: Via Arquivos (somente leitura)
```
Leio diretamente de: ~/Documents/Obsidian Vault/
```

### Opção B: Via MCP (leitura/escrita)
Se você configurar o MCPBundles proxy, posso acessar seu vault com 35 ferramentas:
- Ler notas estruturadas (frontmatter, tags)
- Editar seções específicas (PATCH)
- Criar daily notes
- Analisar imagens
- Listar tarefas
- Detectar links quebrados

---

## Próximos Passos

1. **Instale Copilot** no Obsidian (5 min)
2. **Configure OpenRouter** com Claude 3.7 Sonnet (5 min)
3. Teste: Abra Copilot chat e pergunte sobre uma nota
4. (Opcional) Instale **Local REST API + MCP** para integração externa

Quer que eu configure algum específico agora?
