# Guia de Configuração MCP + Obsidian + Alibaba API

## ✅ Status Atual

**Vault encontrado:** `/home/enio/Obsidian Vault/EGOS`
- 01 - Inputs
- 02 - Processos  
- 03 - Sessions
- 04 - Outputs
- 05 - Templates
- 99 - Archive

**MCP Configurado:** `/home/enio/egos/.mcp.json`
- egos-memory ✅
- egos-governance ✅
- obsidian ✅ (aguardando plugin)

---

## 🔴 PASSO 1: Instalar Local REST API no Obsidian (OBRIGATÓRIO)

O MCP só funciona com o plugin Local REST API instalado. **Você precisa fazer isso manualmente no Obsidian:**

### Passos:
1. **Abra o Obsidian** (já está rodando? Verifique a barra de tarefas)
2. **Aperte Ctrl+P** (ou Cmd+P no Mac)
3. Digite **"Open Settings"** e clique
4. Na lateral esquerda, clique em **"Community Plugins"**
5. Desative o **"Safe Mode"** (modo seguro)
6. Clique em **"Browse"** (procurar)
7. Busque por: **`Local REST API`**
8. **Instale** o plugin de **Adam Coddington**
9. **Ative** o plugin
10. Clique em **"Options"** do plugin
11. **Copie a API Key** gerada (será algo como `abc123def456`)
12. Deixe a porta padrão: **27124**

⚠️ **Sem esse plugin, o MCP não consegue acessar o Obsidian!**

---

## 🟡 PASSO 2: Configurar Alibaba API

### 2.1 Obter API Key
1. Acesse: https://dashscope.console.aliyun.com
2. Crie uma conta ou faça login
3. Vá em **API Key Management**
4. Gere uma nova API Key
5. Copie a chave (começa com `sk-`)

### 2.2 Configurar variável de ambiente
```bash
# Adicione ao seu ~/.bashrc ou ~/.zshrc:
export ALIBABA_API_KEY="sk-sua-chave-aqui"

# Recarregue:
source ~/.bashrc
```

Ou configure no Obsidian Copilot diretamente:
```
Settings → Copilot → OpenAI Format
Base URL: https://dashscope-intl.aliyuncs.com/compatible-mode/v1
API Key: sk-sua-chave-aqui
Model: qwen-plus
```

---

## 🟢 PASSO 3: Testar MCP (depois do Passo 1)

Depois de instalar o Local REST API no Obsidian:

```bash
# Testar conexão MCP
bash /home/enio/egos/scripts/setup-obsidian-mcp.sh

# Ou testar diretamente:
npx @smithery/cli@latest run @smithery/mcp-obsidian --config '{"vaultPath":"/home/enio/Obsidian Vault/EGOS"}'
```

---

## 📁 Arquivos Criados

| Arquivo | Propósito |
|---------|-----------|
| `/home/enio/egos/.mcp.json` | Configuração MCP servers |
| `/home/enio/.config/mcp/obsidian-mcp.json` | Config específica Obsidian |
| `/home/enio/egos/.obsidian-llm-config.json` | Config LLM providers |
| `/home/enio/egos/scripts/setup-obsidian-mcp.sh` | Script de instalação |
| `/home/enio/egos/scripts/obsidian-llm-start.sh` | Script de diagnóstico |

---

## 🤖 Como eu (Cascade/Windsurf) acesso seu Obsidian

### Opção A: MCP (recomendado - precisa do Passo 1)
- Leitura/escrita estruturada
- Acesso a notas, tags, frontmatter
- Edição cirúrgica de seções
- Criação de daily notes
- Análise de imagens

### Opção B: Arquivos diretos (disponível agora)
- Posso ler diretamente de `/home/enio/Obsidian Vault/EGOS/`
- Somente leitura
- Útil para análise de notas existentes

---

## 🚀 Uso Imediato (sem MCP)

Enquanto configura o Local REST API, posso já ajudar lendo seus arquivos:

```
"Leia minhas notas de hoje"
"Resuma o conteúdo da pasta 03 - Sessions"
"Crie uma nota nova sobre..."
```

**Quer que eu leia algo do seu vault agora?**

---

## ❓ Solução de Problemas

### "Failed to connect to Obsidian"
- Verifique se o plugin Local REST API está instalado
- Verifique se a API Key está correta
- Verifique se a porta 27124 está livre: `lsof -i :27124`

### "ALIBABA_API_KEY not found"
- Configure a variável de ambiente
- Ou configure diretamente no Copilot settings

### MCP não lista ferramentas
- Execute: `npx @smithery/cli@latest inspect @smithery/mcp-obsidian`
- Verifique se o vault path está correto
