# EGOS LLM Connector - Plugin Obsidian

Plugin customizado para Obsidian que conecta diretamente com:
- **Alibaba DashScope (Qwen)** - Modelos Qwen Plus, Max, Turbo
- **Claude (Anthropic)** - Claude 3.7 Sonnet, Opus, Haiku
- **Codex (OpenAI)** - Com autenticação OAuth via navegador

## Funcionalidades

- 💬 **Chat panel** lateral integrado ao Obsidian
- 📝 **Comandos rápidos** (Ctrl+P): Ask Alibaba, Ask Claude, Ask Codex
- 🔍 **Resumir nota** automaticamente
- 🏷️ **Gerar tags** com base no conteúdo
- 📄 **Adicionar contexto** da nota atual ao chat
- 🔐 **Autenticação OAuth** para Codex (abre navegador)

## Instalação

### Passo 1: Build do plugin

```bash
cd /home/enio/egos/obsidian-egos-llm-plugin
npm install
npm run build
```

### Passo 2: Instalar no Obsidian

1. Copie os arquivos para o vault:
```bash
mkdir -p ~/"Obsidian Vault/EGOS/.obsidian/plugins/egos-llm-connector"
cp main.js manifest.json styles.css ~/"Obsidian Vault/EGOS/.obsidian/plugins/egos-llm-connector/"
```

2. No Obsidian:
   - Settings → Community Plugins
   - Desative "Safe Mode"
   - Ative "EGOS LLM Connector"

### Passo 3: Configurar APIs

1. **Alibaba DashScope** (recomendado):
   - Vá para https://dashscope.console.aliyun.com/apiKey
   - Gere uma API Key
   - Cole em Settings → EGOS LLM Connector → Alibaba API Key

2. **Claude**:
   - Vá para https://console.anthropic.com/settings/keys
   - Gere uma API Key
   - Cole em Settings → EGOS LLM Connector → Claude API Key

3. **Codex**:
   - Ctrl+P → "EGOS LLM Connector: Login to Codex (Browser)"
   - Complete login no navegador
   - Cole o código de autorização no modal

## Uso

### Chat Panel
- Clique no ícone EGOS na ribbon (lateral esquerda)
- Ou: Ctrl+P → "EGOS LLM Connector: Open LLM Chat"

### Comandos Rápidos
| Comando | Ação |
|---------|------|
| Ask Alibaba | Pergunta rápida via Qwen |
| Ask Claude | Pergunta rápida via Claude |
| Ask Codex | Pergunta rápida via Codex |
| Summarize Current Note | Resume a nota atual |
| Generate Tags for Note | Gera tags automaticamente |
| Login to Codex (Browser) | Autentica Codex via OAuth |

### Atalhos
- `Ctrl+Enter` no chat: Envia mensagem
- Botão "Add Note": Adiciona conteúdo da nota atual como contexto

## Estrutura do Plugin

```
obsidian-egos-llm-plugin/
├── src/
│   ├── main.ts                 # Entry point do plugin
│   ├── settings.ts             # Interfaces de configuração
│   ├── settings-ui.ts          # UI de configurações
│   ├── llm-providers/
│   │   ├── base.ts             # Interface base
│   │   ├── alibaba.ts          # Alibaba DashScope
│   │   ├── claude.ts           # Anthropic Claude
│   │   └── codex.ts            # OpenAI Codex (OAuth)
│   └── ui/
│       └── chat-panel.ts       # Panel de chat
├── manifest.json               # Metadata do plugin
├── package.json                # Dependências
├── tsconfig.json               # Config TypeScript
├── esbuild.config.mjs          # Build config
├── styles.css                  # Estilos
└── README.md                   # Este arquivo
```

## Configuração de Models

### Alibaba (padrão EGOS)
- Modelo: `qwen-plus`
- URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Contexto: 131K tokens

### Claude
- Modelo: `claude-3-7-sonnet-20250219`
- URL: `https://api.anthropic.com/v1`
- Contexto: 200K tokens

### Codex
- Modelo: `o3-mini`
- OAuth: PKCE flow com browser
- Refresh automático de token

## Troubleshooting

### "Provider not configured"
Verifique se a API Key está configurada em Settings.

### Codex: "No refresh token"
Re-autentique via comando "Login to Codex (Browser)".

### Build errors
```bash
npm install
npm run build
```

## Desenvolvimento

```bash
# Dev mode (auto-rebuild)
npm run dev

# Production build
npm run build
```

## Licença
MIT - EGOS Framework
