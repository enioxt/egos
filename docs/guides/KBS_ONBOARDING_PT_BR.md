# Guia de Setup: EGOS Knowledge Base (PT-BR)

**Para:** Novos usuários configurando o sistema de base de conhecimento EGOS com Claude Code + Notion  
**Tempo estimado:** 20–40 minutos  
**Nível:** Iniciante

---

## O que você vai configurar

```
Claude Code (terminal)
    └── MCP Notion (autenticação OAuth)
            └── Base de Conhecimento Notion
                    ├── 📁 Documentos da empresa
                    ├── ❓ Perguntas & Respostas
                    └── 📋 Registro de Decisões
```

Após o setup, você poderá digitar `/ingest` para indexar um documento do Notion, e `/ask` para fazer perguntas em linguagem natural sobre o conteúdo indexado.

---

## Passo 1 — Instalar o Claude Code

### Requisitos
- Node.js 18+ ou Bun 1.x instalado
- Terminal (Linux, macOS ou WSL no Windows)
- Conta na Anthropic (anthropic.com)

### Instalação

```bash
# Opção A — via npm
npm install -g @anthropic-ai/claude-code

# Opção B — via Bun (mais rápido)
bun install -g @anthropic-ai/claude-code
```

### Verificar instalação

```bash
claude --version
# deve mostrar: claude-code x.x.x
```

### Primeiro login

```bash
claude login
# Abre o navegador para autenticação com sua conta Anthropic
```

---

## Passo 2 — Configurar o MCP do Notion

O MCP (Model Context Protocol) Notion permite que o Claude Code acesse e escreva em seu workspace do Notion diretamente do terminal.

### 2.1 Criar integração no Notion

1. Acesse: **[notion.so/my-integrations](https://notion.so/my-integrations)**
2. Clique em **"+ Nova integração"**
3. Preencha:
   - **Nome:** `Claude Code EGOS`
   - **Workspace:** selecione seu workspace
   - **Tipo:** Interno
4. Clique em **"Salvar"**
5. Copie o **"Token de integração interno"** (começa com `secret_...`)

### 2.2 Adicionar o MCP ao Claude Code

```bash
# Adicionar servidor MCP Notion
claude mcp add notion

# Quando solicitado, cole o token do passo anterior
# Token: secret_xxxxxxxxxxxxxxxx
```

### 2.3 Verificar conexão

```bash
claude mcp list
# deve mostrar: notion  ✓ connected
```

### 2.4 Dar acesso ao Notion

No Notion, para cada página/banco de dados que você quer que o Claude acesse:
1. Clique em **"···"** (menu da página) → **"Adicionar conexões"**
2. Busque **"Claude Code EGOS"** e clique para adicionar

---

## Passo 3 — Criar a estrutura no Notion

### 3.1 Usar o template EGOS

Se você já tem acesso ao template EGOS Knowledge Base:

```bash
# No terminal, dentro do seu projeto
/notion-setup
# O comando duplica o template para seu workspace automaticamente
```

### 3.2 Criar manualmente (alternativa)

Se preferir criar do zero, crie no Notion:

**Página principal:** `🧠 Base de Conhecimento — [Nome da Empresa]`

Dentro dela, crie 3 bancos de dados:

| Nome | Tipo | Propriedades principais |
|------|------|------------------------|
| 📁 Documentos | Database | Título, Categoria, Data, Status, Resumo |
| ❓ Perguntas & Respostas | Database | Pergunta, Resposta, Fonte, Tags |
| 📋 Decisões | Database | Decisão, Contexto, Data, Responsável |

> **Dica:** O Claude pode criar esses bancos de dados por você. Apenas abra o Claude Code e diga: "Crie a estrutura de base de conhecimento no Notion com 3 bancos de dados: Documentos, Q&A e Decisões."

---

## Passo 4 — Primeiro `/ingest`

O comando `/ingest` indexa um documento do Notion na base de conhecimento, gerando um resumo e extraindo os pontos principais.

### Uso básico

```bash
# Abra o Claude Code no terminal
claude

# Dentro da sessão, use o skill:
/ingest https://notion.so/sua-pagina-aqui
```

### O que acontece durante o ingest

1. Claude lê o conteúdo da página via MCP Notion
2. Gera um resumo estruturado
3. Extrai entidades, decisões e perguntas respondidas
4. Salva no banco de dados "Documentos" com metadados

### Exemplo de saída

```
✅ Documento indexado: "Manual de Processos — Fundição"
   Resumo: 3 parágrafos
   Entidades detectadas: 12
   Decisões encontradas: 3
   Adicionado a: 📁 Documentos (ID: abc123)
```

### Ingerir múltiplos documentos

```bash
# Indexar uma pasta inteira do Notion
/ingest-folder https://notion.so/sua-pasta-aqui

# O Claude vai processar cada página filha sequencialmente
```

---

## Passo 5 — Primeiro `/ask`

O comando `/ask` faz perguntas em linguagem natural sobre o conteúdo indexado.

### Uso básico

```bash
# Dentro da sessão do Claude Code:
/ask Qual é o prazo de entrega padrão para clientes do interior?

/ask Quem é responsável pelo processo de fundição de peças grandes?

/ask Quais foram as últimas decisões sobre fornecedores?
```

### O que acontece durante o ask

1. Claude busca nos bancos de dados Documentos e Q&A
2. Compara semanticamente com a pergunta
3. Retorna resposta com citação da fonte
4. Opcionalmente salva a Q&A para uso futuro

### Exemplo de saída

```
📖 Com base em "Manual de Processos — Fundição" (indexado hoje):

O prazo padrão para clientes do interior é **15 dias úteis** a partir
da confirmação do pedido. Pedidos acima de 500kg têm prazo estendido
para 21 dias úteis.

Fonte: Seção 4.2 — Prazos de Entrega
```

### Perguntas avançadas

```bash
# Comparar documentos
/ask Compare o processo antigo e o novo de controle de qualidade

# Extrair ações
/ask Quais são os próximos passos definidos nas reuniões desta semana?

# Resumir por período
/ask Resuma as decisões tomadas em março de 2026
```

---

## Configurações opcionais

### Idioma padrão

Adicione ao `CLAUDE.md` do seu projeto:

```markdown
## Preferências de Idioma
- Responder sempre em PT-BR
- Documentos gerados: PT-BR
- Termos técnicos: manter em inglês quando não há tradução estabelecida
```

### Categorias personalizadas por setor

**Metalurgia/Forjaria:**
```
Categorias: Processos de Produção | Controle de Qualidade | Manutenção | Segurança | Fornecedores | Clientes
```

**Jurídico:**
```
Categorias: Contratos | Pareceres | Jurisprudência | Clientes | Prazos | Legislação
```

**Saúde:**
```
Categorias: Protocolos Clínicos | Pacientes | Equipamentos | Fornecedores | Regulatório | Treinamento
```

### Atalhos úteis

| Comando | O que faz |
|---------|-----------|
| `/ingest <url>` | Indexa uma página do Notion |
| `/ask <pergunta>` | Consulta a base de conhecimento |
| `/kb-status` | Mostra estatísticas da base (total de docs, última atualização) |
| `/kb-search <termo>` | Busca direta por termo no índice |

---

## Solução de problemas

### "MCP Notion não conectado"

```bash
# Reconectar
claude mcp remove notion
claude mcp add notion
# Cole o token novamente
```

### "Página não encontrada no Notion"

Verifique se a integração tem acesso à página:
- Notion → Página → `···` → Conexões → verifique se "Claude Code EGOS" aparece

### "Erro de permissão ao escrever Q&A"

A integração precisa de permissão de edição:
- notion.so/my-integrations → sua integração → Permissões → marque "Inserir conteúdo"

### Claude não encontra informações que existem nos documentos

O documento pode não ter sido indexado ainda. Execute:
```bash
/ingest <url-do-documento>
```

---

## Próximos passos

Após o setup básico, explore:

1. **Ingerir toda a documentação existente** — comece pelos 10 documentos mais consultados
2. **Configurar ingest automático** — documentos novos adicionados ao Notion são indexados diariamente
3. **Instalar Guard Brasil** (se lida com dados pessoais) — filtra CPF, RG, dados de saúde antes de indexar
4. **Compartilhar com a equipe** — cada membro instala o Claude Code e usa a mesma base

---

## Suporte

- Documentação técnica: `docs/knowledge/HARVEST.md`
- Issues: github.com/enioxt/egos/issues
- Comunidade: em construção

---

*Versão 1.0.0 — 2026-04-09 | EGOS Knowledge Base System*
