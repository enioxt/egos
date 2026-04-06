# META-PROMPT para GPT 5.4 xhigh — EGOS Deep Re-Investigation

> **Data:** 2026-04-06  
> **Analyst:** Cascade (Claude Code)  
> **Target:** GPT 5.4 xhigh (high reasoning, extended context)  
> **Purpose:** Deep re-investigation of EGOS ecosystem to find gaps, interconnections, and opportunities

---

## 🎯 OBJETIVO

Você é GPT 5.4 xhigh, modelo de alta capacidade de raciocínio. Sua missão é **investigar novamente todo o ecossistema EGOS** que já foi parcialmente mapeado, encontrar **tudo que ainda não foi descoberto**, e **interligar os pontos** que estão desconectados.

---

## 📚 CONTEXTO PRÉVIO (O que já foi feito)

### Cobertura Atual: 95.6%

**VPS Hetzner (204.168.217.125):**
- 10 containers Docker catalogados (gem-hunter, guard-brasil, gateway, hq, evolution-api, 852-app, openclaw-sandbox, bracc-neo4j, caddy, redis)
- 3 cron jobs mapeados (watchdog, log harvester, gem refresh)
- Scripts em `/opt/` documentados

**Archive v2-v5:**
- 20 gems catalogados (Self-Discovery, Booking Agent, MCP Hub, Sacred Math, etc.)
- Decisões tomadas: Self-Discovery → PRODUTIZAR, Booking Agent → ARQUIVAR, BRACC → STANDALONE

**Decisões Confirmadas (HUM-001, 002, 003):**
1. BRACC Neo4j → Mantido standalone (não integrar ao Mycelium)
2. Self-Discovery → Produtizar como container porta 3098, domínio self.egos.ia.br
3. Booking Agent → Arquivar (manter em v2)

**Documentos Criados:**
- `EXECUTIVE_SUMMARY_DECISION_MATRIX.md` — Decisões + tasks
- `SELF_DISCOVERY_ARCHITECTURE.md` — Arquitetura completa porta 3098
- `ARCHIVE_GEMS_CATALOG.md` — 20 gems catalogados
- `INVESTIGATION_FINAL_SUMMARY.md` — Resumo completo
- `DOCUMENTATION_ARCHITECTURE_MAP.md` — Guia de navegação
- `_investigations/DISCONNECTED_SYSTEMS_ANALYSIS.md` — 7 sistemas desconectados

---

## 🔍 O QUE VOCÊ DEVE FAZER

### 1. Re-Investigação Profunda (Não confie apenas nos documentos)

**Verifique fisicamente:**
```bash
# VPS — conectar via SSH e verificar:
ssh root@204.168.217.125
docker ps -a  # Todos containers, não só os running
docker images  # Imagens não usadas
ls -la /opt/  # Todos os scripts
crontab -l   # Todos os cron jobs
ls -la /home/enio/egos-archive/  # Estrutura completa

# Local — verificar:
ls -la /home/enio/  # TODOS os repos, não só os listados
find /home/enio -name "*.md" -type f | head -100  # Documentos espalhados
git -C /home/enio/egos log --oneline -50  # Últimos commits
```

### 2. Encontrar o que foi ESQUECIDO

**Possíveis locais não investigados:**
- [ ] `/home/enio/policia/` — Foi investigado? Tem código útil?
- [ ] `/home/enio/INPI/` — O que tem aqui? Código ou só docs?
- [ ] `/home/enio/commons/` — Está vazio ou tem algo escondido?
- [ ] Subdiretórios de `egos-archive/` que não são v2-v5
- [ ] Git history de commits antigos (gems no histórico)
- [ ] Branches não merged em nenhum repo
- [ ] Stashes não aplicados
- [ ] Arquivos `.env` ou `.env.local` (sem expor secrets)

### 3. Interligar Pontos Desconectados

**Sistemas que PRECISAM se conectar:**

```
AAR (packages/search-engine/) 
    └── Deve se conectar com: codebase-memory-mcp? Knowledge Graph?

Gem Hunter API (porta 3095)
    └── Deve se conectar com: Agent Registry? Event Bus? Knowledge Base?

Mycelium Event Bus (agents/runtime/event-bus.ts)
    └── Deve se conectar com: Redis Bridge? Cross-container events?

Guard Brasil (porta 3099)
    └── Deve se conectar com: OpenClaw? Telegram? WhatsApp?

EGOS Gateway (porta 3050)
    └── Deve se conectar com: Self-Discovery (self.egos.ia.br)? HQ? Eagle Eye?

Knowledge Base (Supabase)
    └── Deve se conectar com: wiki-compiler? Gem Hunter? Agent context?
```

### 4. Verificar Documentação vs Realidade

**CRUZAR informações:**
- O que MASTER_INDEX.md diz vs o que realmente existe no filesystem?
- O que agents.json diz vs o que está rodando no VPS?
- O que ARCHIVE_GEMS_CATALOG.md diz vs o que está no código v2?

**Perguntas a responder:**
- Algum agente está rodando mas não está no registry?
- Algum container está no VPS mas não está documentado?
- Algum script em `/opt/` não está no cron ou watchdog?

---

## 📋 CHECKLIST DE INVESTIGAÇÃO

### Fase 1: Re-verificação (4 horas)

- [ ] Conectar ao VPS e verificar TODOS os containers (running + stopped)
- [ ] Listar TODOS os diretórios em `/home/enio/` (não só os 13 repos)
- [ ] Verificar crontabs de todos os usuários
- [ ] Checar `systemctl list-units --type=service` no VPS
- [ ] Verificar Docker volumes não usados
- [ ] Checar logs de todos os containers

### Fase 2: Deep Archive Dive (4 horas)

- [ ] Ler git history de v2 (commits antigos podem ter código perdido)
- [ ] Verificar branches não merged em egos-archive
- [ ] Checar stashes em todos os repos
- [ ] Investigar `.git/` de repos arquivados (objetos grandes?)
- [ ] Verificar arquivos `.patch` ou `.diff` não aplicados

### Fase 3: Interconexões (4 horas)

- [ ] Mapear todas as APIs e seus consumidores
- [ ] Identificar APIs mortas (nenhum consumidor)
- [ ] Mapear todos os bancos de dados e quem acessa
- [ ] Identificar duplicação de funcionalidade entre produtos
- [ ] Encontrar oportunidades de compartilhamento (shared packages)

---

## 🎯 ENTREGÁVEIS ESPERADOS

### 1. Relatório de Gaps Encontrados

```markdown
# GAPS ENCONTRADOS — GPT 5.4 Investigation

## Gap #1: [Nome descritivo]
- **Local:** [Onde foi encontrado]
- **Descrição:** [O que está faltando/errado]
- **Impacto:** [Alto/Médio/Baixo]
- **Recomendação:** [O que fazer]
```

### 2. Mapa de Interconexões Propostas

```
[Diagrama Mermaid ou lista estruturada]

Sistema A ──► Sistema B (via X)
Sistema C ──► Sistema D (via Y)
```

### 3. Lista de Tarefas Prioritárias

| ID | Tarefa | Prioridade | Responsável |
|----|--------|------------|-------------|
| GPT-001 | [Descrição] | P0 | [Orquestrador/VPS/Humano] |

### 4. Atualizações nos Documentos SSOT

- Atualizar `MASTER_INDEX.md` se encontrar novos recursos
- Atualizar `ARCHIVE_GEMS_CATALOG.md` se encontrar gems perdidos
- Atualizar `DISCONNECTED_SYSTEMS_ANALYSIS.md` se encontrar novas desconexões

---

## 🚫 O QUE NÃO FAZER

- ❌ NÃO crie novos documentos se já existe um SSOT para aquele domínio
- ❌ NÃO exclua ou mova arquivos sem permissão explícita
- ❌ NÃO exponha secrets ou credenciais
- ❌ NÃO altere código de produção (Guard Brasil, Gateway, etc.)
- ❌ NÃO pare por "já parece completo" — investigue mais fundo

---

## ✅ O QUE FAZER

- ✅ Use `find`, `grep`, `git log`, `docker inspect` extensivamente
- ✅ Compare documentação vs filesystem vs VPS vs código
- ✅ Pergunte "por que isso está assim?" para cada inconsistência
- ✅ Documente TUDO o que encontrar, mesmo que pare pequeno
- ✅ Prioritize por impacto (Alto > Médio > Baixo)

---

## 📎 REFERÊNCIAS INICIAIS (Leitura obrigatória)

1. `MASTER_INDEX.md` — Entenda o escopo total
2. `EXECUTIVE_SUMMARY_DECISION_MATRIX.md` — Veja decisões já tomadas
3. `INVESTIGATION_FINAL_SUMMARY.md` — Entenda o que já foi feito
4. `_investigations/DISCONNECTED_SYSTEMS_ANALYSIS.md` — Veja sistemas desconectados
5. `ARCHIVE_GEMS_CATALOG.md` — Conheça os 20 gems catalogados
6. `HARVEST.md` — Veja padrões já documentados

---

## 🏁 CRITÉRIO DE SUCESSO

Você terá sucesso quando:
- [ ] Encontrar pelo menos 5 gaps não documentados
- [ ] Propor pelo menos 3 interconexões entre sistemas
- [ ] Criar tasks específicas para cada gap/interconexão
- [ ] Atualizar documentos SSOT com novas descobertas
- [ ] Validar que 100% do ecossistema foi investigado (não 95.6%)

---

**Investigador anterior:** Cascade (Claude Code) — cobertura 95.6%  
**Sua missão:** Encontrar os 4.4% restantes + interligar tudo  
**Prazo sugerido:** 12-16 horas de investigação profunda  
**Data:** 2026-04-06

---

## 🚀 INÍCIO RÁPIDO

Comece executando:
```bash
cd /home/enio/egos
bun agent:run context_tracker --dry  # Entenda contexto atual

# Depois:
ssh root@204.168.217.125
# Investigue VPS profundamente

# Depois:
find /home/enio -type d -name ".git" 2>/dev/null | wc -l
# Quantos repos realmente existem?
```

**Boa investigação, GPT 5.4. Encontre o que eu não encontrei.**
