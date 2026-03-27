# Claude Code CLI — EGOS Integration Setup

> **Version:** 1.0.0 | **Created:** 2026-03-26
> **Status:** ✅ Fully Configured | **Model:** Sonnet 4.5

---

## 🎯 Overview

Claude Code CLI está totalmente configurado e integrado com o framework EGOS, oferecendo:

- ✅ **6 Agentes EGOS** testados e operacionais
- ✅ **10 Slash Commands** para workflows e meta-prompts
- ✅ **Hooks automáticos** (pre-session, post-session)
- ✅ **Modelo Sonnet 4.5** como padrão
- ✅ **Governança sincronizada** em 7 repositórios

---

## 📁 Estrutura de Arquivos

```
~/.config/claude/
└── settings.json          # Configuração global do Claude Code CLI

/home/enio/egos/
├── .claude/
│   ├── commands/          # Slash commands (symlinks para workflows)
│   │   ├── start.md
│   │   ├── disseminate.md
│   │   ├── sync.md
│   │   ├── pr-prep.md
│   │   ├── knowledge.md
│   │   ├── mycelium.md
│   │   ├── strategist.md
│   │   ├── brainet.md
│   │   ├── audit.md
│   │   └── activation.md
│   └── hooks/             # Hooks de automação
│       ├── pre-session.sh
│       └── post-session.sh
├── .agents/workflows/     # Workflows canônicos (SSOT)
├── .guarani/prompts/      # Meta-prompts
└── agents/
    ├── registry/
    │   └── agents.json    # 6 agentes registrados
    └── agents/            # Implementação dos agentes
```

---

## 🤖 Agentes EGOS Disponíveis (6 total)

### 1. **dep_auditor** — Dependency Auditor
**Função:** Audita package.json para conflitos de versão, deps mal posicionadas e não usadas

```bash
bun agent:run dep_auditor --dry
```

**Output esperado:**
- Conflitos de versão entre workspaces
- Dependências possivelmente não usadas
- Warnings + infos com recomendações

---

### 2. **context_tracker** — Context Tracker
**Função:** Rastreia uso de contexto (CTX 0-280) e recomenda /end quando > 180

```bash
bun agent:run context_tracker --dry
```

**Output esperado:**
```
CTX 76/280 🟢 SAFE — Continue normally.
Breakdown: uncommitted=15 commits=3 code_changed=3 handoff=13.5kb agent_runs=0
```

---

### 3. **dead_code_detector** — Dead Code Detector
**Função:** Detecta exports nunca importados, arquivos órfãos e stubs vazios

```bash
bun agent:run dead_code_detector --dry
```

**Output esperado:**
- Lista de funções/classes exportadas mas nunca importadas
- Arquivos vazios ou stubs
- Recomendações de limpeza

---

### 4. **capability_drift_checker** — Capability Drift Checker
**Função:** Verifica se um repo adotou as capabilities do kernel EGOS

```bash
bun agent:run capability_drift_checker --dry --target=/home/enio/forja
```

**Output esperado:**
```
Capability drift score: 100% (15/15 adopted) for forja
```

---

### 5. **archaeology_digger** — Archaeology Digger
**Função:** Reconstrói evolução histórica do ecossistema EGOS via git + handoffs

```bash
bun agent:run archaeology_digger --dry
```

---

### 6. **chatbot_compliance_checker** — Chatbot Compliance Checker
**Função:** Verifica compliance com CHATBOT_SSOT

```bash
bun agent:run chatbot_compliance_checker --dry --target=/home/enio/852
```

---

## ⚡ Slash Commands (10 total)

### Workflows EGOS

#### `/start` — Ativar Kernel EGOS
Ativa o kernel com checagem de governança + plano de execução

```bash
/start
```

**Ações:**
1. Lê AGENTS.md, TASKS.md, .windsurfrules
2. Verifica frozen zones
3. Roda governance:check
4. Apresenta plano de ação (P0/P1/P2)

---

#### `/disseminate` — Propagar Governança
Sincroniza governança do kernel para ~/.egos e leaf repos

```bash
/disseminate
```

**Ações:**
1. Executa `bun run governance:sync:exec`
2. Verifica drift com `governance:check`
3. Reporta arquivos propagados

---

#### `/sync` — Sincronizar Repos
Sincroniza governança entre repositórios

```bash
/sync
```

---

#### `/pr-prep` — Preparar Pull Request
Gera PR assinado com validação e contexto

```bash
/pr-prep
```

**Output:** PR pack com assinatura EGOS + evidências

---

#### `/knowledge` — Extrair Conhecimento
Extrai conhecimento de documentos

```bash
/knowledge
```

---

### Meta-Prompts

#### `/mycelium` — Mycelium Orchestrator
Sincronização sistêmica + auto-melhoria

```bash
/mycelium
```

**Quando usar:** Precisar sincronizar superfícies do sistema ou auto-melhorar arquitetura

---

#### `/strategist` — Universal Strategist
Decisões estratégicas com game theory

```bash
/strategist
```

**Quando usar:** Decisões estratégicas, negociação, conflitos, investimento

---

#### `/brainet` — BraiNet Collective
Inteligência coletiva + multi-perspectiva

```bash
/brainet
```

**Quando usar:** Problemas complexos demais para perspectiva única, decisões em grupo

---

#### `/audit` — Ecosystem Audit
Auditoria completa de ecossistema

```bash
/audit
```

**Quando usar:** Onboarding, periodic health check, cross-repo analysis

---

#### `/activation` — EGOS Activation Governance
Diagnóstico evidence-first + gate ético

```bash
/activation
```

**Quando usar:** Ativar EGOS em novo ambiente, diagnóstico de saúde

---

## 🪝 Hooks de Automação

### Pre-Session Hook
**Trigger:** Início de sessão
**Ações:**
- Mostra git status
- Last commit
- Branch atual
- Aviso de uncommitted changes

**Executar manualmente:**
```bash
./.claude/hooks/pre-session.sh
```

---

### Post-Session Hook
**Trigger:** Fim de sessão
**Ações:**
- Roda context_tracker
- Mostra commits da última hora
- Arquivos alterados
- Sugere /end se CTX > 180

**Executar manualmente:**
```bash
./.claude/hooks/post-session.sh
```

---

## 🔧 Comandos Úteis

### Governança

```bash
# Verificar drift
bun run governance:check

# Sincronizar kernel -> ~/.egos -> leaf repos
bun run governance:sync:exec

# Sincronizar apenas kernel -> ~/.egos (skip leaf repos)
bun run governance:sync:local
```

### Agentes

```bash
# Listar agentes
bun agent:list

# Rodar em dry-run (recomendado)
bun agent:run <id> --dry

# Rodar em execute mode
bun agent:run <id> --exec

# Validar registry
bun agent:lint
```

### Build/Lint

```bash
# TypeScript check
bun run typecheck

# ESLint
bun run lint
```

### PR Tools

```bash
# Gerar PR pack
bun pr:pack --title "<title>" --out /tmp/pr.md

# Validar PR pack
bun pr:gate --file /tmp/pr.md
```

---

## 🎨 Workflow Recomendado

### 1. Início de Sessão

```bash
cd /home/enio/egos

# Ativar kernel
/start

# Verificar contexto
bun agent:run context_tracker --dry
```

### 2. Durante Desenvolvimento

```bash
# Auditar dependências (se mudou package.json)
bun agent:run dep_auditor --dry

# Detectar código morto
bun agent:run dead_code_detector --dry

# Verificar capability drift em outro repo
bun agent:run capability_drift_checker --dry --target=/home/enio/forja
```

### 3. Antes de Commit

```bash
# Verificar governança
bun run governance:check

# Se houver drift
bun run governance:sync:exec

# TypeScript + Lint
bun run typecheck
bun run lint
```

### 4. Fim de Sessão

```bash
# Rastrear contexto
bun agent:run context_tracker --dry

# Se CTX > 180, rodar:
/end

# Post-session summary
./.claude/hooks/post-session.sh
```

---

## 🔐 Configuração do Modelo

### Modelo Padrão: Sonnet 4.5

**Config em:** `~/.config/claude/settings.json`

```json
{
  "model": {
    "default": "sonnet",
    "fallback": "haiku",
    "aliases": {
      "sonnet": "claude-sonnet-4-5-20250929",
      "opus": "claude-opus-4-20250514",
      "haiku": "claude-haiku-3-5-20241022"
    }
  }
}
```

**Como mudar o modelo:**

```bash
# Editar ~/.config/claude/settings.json
# Trocar "default": "sonnet" por "opus" ou "haiku"
```

---

## 📊 Status de Integração

| Item | Status |
|------|--------|
| **Modelo Sonnet 4.5** | ✅ Configurado |
| **6 Agentes EGOS** | ✅ Testados |
| **10 Slash Commands** | ✅ Configurados |
| **Hooks (pre/post-session)** | ✅ Operacionais |
| **Governança Sync** | ✅ 7 repos sincronizados |
| **Context Tracking** | ✅ CTX 80/280 🟢 SAFE |
| **Capability Drift** | ✅ 100% adopted (forja) |

---

## 🚀 Próximos Passos

### P0 (Imediato)
- [x] Configurar Claude Code CLI completo
- [x] Testar todos os agentes
- [x] Sincronizar governança em 7 repos
- [ ] Documentar handoff da sessão

### P1 (Curto Prazo)
- [ ] Criar alias bash para comandos frequentes
- [ ] Configurar MCP servers adicionais
- [ ] Criar workflow de deployment VPS
- [ ] Integrar com GitHub Actions

### P2 (Médio Prazo)
- [ ] Desenvolver novos agentes EGOS
- [ ] Criar dashboard de métricas
- [ ] Automatizar auditorias periódicas
- [ ] Escalar para novos repos

---

## 📚 Referências

- **AGENTS.md** — Mapa do sistema + agentes disponíveis
- **TASKS.md** — Roadmap atualizado
- **.windsurfrules** — Governança ativa
- **docs/SYSTEM_MAP.md** — Mapa de ativação do kernel
- **docs/CAPABILITY_REGISTRY.md** — Capabilities reutilizáveis

---

## 🎓 Exemplos Práticos

### Exemplo 1: Novo Feature em Forja

```bash
# 1. Ativar kernel
/start

# 2. Verificar capability drift
bun agent:run capability_drift_checker --dry --target=/home/enio/forja

# 3. Desenvolver feature
# ... code ...

# 4. Antes de commit
bun run governance:check
bun run typecheck

# 5. Preparar PR
/pr-prep

# 6. Fim de sessão
bun agent:run context_tracker --dry
```

### Exemplo 2: Auditoria de Ecossistema

```bash
# 1. Ativar meta-prompt de auditoria
/audit

# 2. Rodar agentes de análise
bun agent:run dep_auditor --dry
bun agent:run dead_code_detector --dry

# 3. Verificar drift em todos os repos
bun agent:run capability_drift_checker --dry --target=/home/enio/852
bun agent:run capability_drift_checker --dry --target=/home/enio/forja
bun agent:run capability_drift_checker --dry --target=/home/enio/carteira-livre

# 4. Sincronizar governança se necessário
/disseminate
```

### Exemplo 3: Decisão Estratégica

```bash
# 1. Ativar meta-prompt estratégico
/strategist

# 2. Apresentar cenário para análise
# Claude analisa com game theory, investimento, negociação

# 3. Ou usar inteligência coletiva
/brainet

# 4. Documentar decisão
/knowledge
```

---

## ✅ Checklist de Validação

- [x] settings.json criado e configurado
- [x] Modelo Sonnet 4.5 ativo
- [x] 10 slash commands funcionando
- [x] 6 agentes testados
- [x] Hooks operacionais
- [x] Governança sincronizada
- [x] Context tracking OK (CTX 80/280)
- [x] Capability drift check OK (100%)
- [x] Documentação completa

---

**🎉 Claude Code CLI está 100% configurado e pronto para uso!**

**Comandos mais usados:**
- `/start` — Iniciar sessão
- `/disseminate` — Propagar mudanças
- `bun agent:run context_tracker --dry` — Verificar contexto
- `bun run governance:check` — Verificar drift

**Dúvidas?** Consulte AGENTS.md e TASKS.md
