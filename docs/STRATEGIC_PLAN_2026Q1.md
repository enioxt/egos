# EGOS Strategic Plan — Q1 2026

> **Prepared:** 2026-03-27 | **Horizon:** 90 days
> **Status:** Evidence-based (web research + codebase analysis)
> **Model:** Internal Fork (Bun-native) + selective OSS patterns

---

## 1. POSIÇÃO NO ECOSSISTEMA DAG — Onde Estamos?

### O Mercado Real de DAG/Multi-Agent (2026)

**Projetos com uso prático confirmado:**

| Framework | Usuários em Produção | Diferencial | GitHub Stars |
|-----------|---------------------|-------------|--------------|
| **LangGraph** | LinkedIn, Uber, Klarna, 400+ | Stateful graph + loops | 11k+ |
| **Apache Airflow** | 50k+ deployments | Batch workflow scheduling | 38k+ |
| **Dagster** | Grandes empresas data | Asset-centric DAG | 12k+ |
| **CrewAI** | Startups/devs | Declarative multi-agent | 25k+ |
| **Temporal** | Mission-critical infra | Durable execution engine | 12k+ |

**Referências:** [LangGraph Docs](https://blog.langchain.com/building-langgraph/), [Top OSS Frameworks 2025](https://apipie.ai/docs/blog/top-10-opensource-ai-agent-frameworks-may-2025)

### EGOS vs. Mercado — Gap Analysis Honesta

| Dimensão | LangGraph/CrewAI | EGOS Hoje |
|----------|-----------------|-----------|
| **Registry/SSOT** | Básico | ✅✅ Avançado (agents.json, schema) |
| **Governance** | Nenhum | ✅✅ .guarani/ + Tsun-Cha |
| **Dry-run Safety** | Parcial | ✅✅ Universal (todo agente) |
| **Multi-LLM** | Sim | ✅ Qwen + OpenRouter |
| **Event Bus** | Sim | ✅ JSONL + correlação |
| **UI/Dashboard** | Básico | ⚠️ egos-web (em dev) |
| **GitHub Stars** | 11k-38k | 🔴 <100 (unknown) |
| **Docs públicas** | Extensas | ⚠️ Parciais |
| **Community** | Forte | 🔴 Inexistente |
| **Production usage** | 400+ empresas | 🔴 0 (além de nos próprios) |
| **A2A standard** | CrewAI alinhando | ⚠️ Em planejamento |
| **MCP standard** | Alguns | ✅ EXA, Supabase, Morph |

**Distância para viabilidade pública:** 3-6 meses de trabalho focado

**O que temos que eles NÃO têm:**
- Governance filosófica (Tsun-Cha, ATRiAN, Mycelium meta-prompts)
- Sistema de regras propagável (kernel → leaf repos)
- CRCDM blockchain-style audit trail
- Separação explícita agents[] vs tools[] com validação

---

## 2. PLANO DE VIABILIDADE — Quem Nos Usaria?

### Target Users (Realistas)

**Tier 1 — Imediato (Week 1-4):**
1. **Devs brasileiros** que querem framework local com governança
2. **Projetos LGPD/compliance** precisam de audit trail completo
3. **Pequenas equipes AI** que querem governance sem complexidade Enterprise

**Tier 2 — Médio Prazo (Month 2-3):**
1. **Governos/Setor Público BR** (Intelink já aponta para isso — PCMG bot)
2. **Jurídico/Forense** (Intelink extrai BOs, depoimentos → mercado real)
3. **Fintech/Carteiras** (Carteira Livre + ASAAS API já existe)

**Tier 3 — Longo Prazo (Month 4-6):**
1. **Pesquisadores** que precisam de multi-agent reproduzível
2. **Empresas enterprise** que precisam de AI governance
3. **OSS community** via GitHub momentum

### O Que Falta para Ser Usado

**P0 — Blocking para qualquer uso externo:**
1. README.md claro com "Quick Start em 5 minutos"
2. Pelo menos 1 exemplo de agente funcional end-to-end
3. Deploy funcionando (VPS, não só local)

**P1 — Para crescimento orgânico:**
1. GitHub Actions CI/CD
2. Documentação pública (egos.ia.br/docs)
3. 1 post técnico no X.com/DEV.to

**P2 — Para momentum:**
1. Telegram bot como ponto de entrada (já temos @EGOSin_bot!)
2. Demo ao vivo via egos.ia.br
3. Integração com 1 caso de uso real (Intelink? Carteira Livre?)

---

## 3. VISÃO DO FRONTEND — O GRAFO UNIFICADO

### O Que o Usuário Quer
> "Um mesmo modelo completo de grafos, que suporta entrada de todos tipos de dados — texto, vídeo, áudio, linguagem natural — com agentes AI por trás"

### Implementação em 3 Camadas

```
┌─────────────────────────────────────────────────────┐
│  FRONTEND GRAPH VISUALIZATION (egos.ia.br)          │
│                                                      │
│  ● React/Three.js ou D3.js force-directed graph     │
│  ● Nós = Agentes, Repos, Dados                      │
│  ● Arestas = Correlações, Dependências, Eventos     │
│  ● Real-time via Supabase Realtime                  │
└────────────────────┬────────────────────────────────┘
                     │ WebSocket/REST
┌────────────────────▼────────────────────────────────┐
│  API GATEWAY (packages/shared + edge functions)     │
│                                                      │
│  POST /api/chat → Chatbot → Agent Chain             │
│  GET  /api/graph → CRCDM + Agent Status             │
│  GET  /api/events → Event Bus JSONL stream          │
│  POST /mcp → MCP Protocol handler                   │
│  POST /a2a → A2A Agent Card protocol                │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│  AGENT RUNTIME (VPS / Hetzner)                      │
│                                                      │
│  6 Kernel Agents (egos) — governance, audit         │
│  18 Lab Agents (egos-lab) — feature agents          │
│  Telegram Bots (@EGOSin_bot, @IntelinkBOT, etc.)   │
│  Cron Jobs (scheduler.ts, Redis queue)              │
└────────────────────────────────────────────────────┘
```

### Input Types para Grafo Universal

| Input | Tecnologia Atual | Gap |
|-------|-----------------|-----|
| Texto | ✅ LLM providers (Qwen, Gemini) | - |
| Código | ✅ Agentes de análise | - |
| PDFs | ⚠️ Intelink (parcial) | EXA crawling |
| Áudio | ❌ Não implementado | Whisper API |
| Vídeo | ❌ Não implementado | Frame extraction |
| URLs | ✅ EXA MCP | - |
| Imagens | ⚠️ Vision models | Integrar vision |

**Para visão completa:** Adicionar Whisper + Vision para completar o ciclo multimodal.

---

## 4. API + MCP + A2A — Ser Ubíquo

### Estratégia "Estar em Todos os Lugares"

```
EGOS como Plataforma
├── REST API (/api/*)          ← já parcialmente em egos-lab
├── MCP Server (/mcp)          ← Supabase, EXA, Morph MCPs existem
├── A2A Agent Cards (/a2a)     ← Novo — seguir padrão Google ADK
├── Telegram Bot              ← @EGOSin_bot ATIVO
├── Web Chat (egos.ia.br)     ← Precisa chatbot widget
└── GitHub Actions            ← Agent como CI check
```

### A2A Implementation (Google ADK Padrão)
```json
// /.well-known/agent.json (A2A Agent Card)
{
  "name": "EGOS Kernel",
  "description": "Governance-first multi-agent orchestration",
  "url": "https://egos.ia.br/a2a",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "multimodal": false
  },
  "agents": ["dep_auditor", "archaeology_digger", "context_tracker"]
}
```

---

## 5. VPS / HETZNER MIGRATION — Plano de Execução

### Situação Atual

| Item | Status |
|------|--------|
| Oracle VPS | Ativo (oracle-instance-launcher existe em /home/enio/egos/scripts/) |
| Hetzner | Target para esse mês |
| Agents em VPS | ❌ Não deployados ainda |
| Cron/Systemd | ❌ Não configurado |

### Plano Hetzner (Este Mês)

**Fase A — Preparação (1-2 dias):**
1. Criar `docker-compose.yml` na raiz do egos-lab com todos os serviços
2. Criar `systemd/egos-agents.service` para auto-restart
3. Testar localmente com `docker compose up`

**Fase B — Deploy (1 dia):**
1. Provisionar Hetzner CX31 (€ ~10/mês — 4 vCPU, 8GB RAM)
2. SSH + clone repos
3. `docker compose up -d`
4. Setup nginx reverse proxy para egos.ia.br

**Fase C — Monitoramento (ongoing):**
1. Context tracker rodando a cada 30 min
2. Governance sync a cada 1h
3. Gem Hunter semanal (terça 09:00)
4. Alertas via @EGOSin_bot quando agentes detectam issues

### Services para docker-compose.yml
```yaml
services:
  egos-agents:
    build: ./egos-lab
    environment:
      - NODE_ENV=production
    restart: always

  redis:
    image: redis:alpine
    restart: always

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
      - "443:443"
    restart: always
```

---

## 6. BOTS ATIVOS — Inventário Completo

### Telegram Bots Confirmados

| Bot | Username | Projeto | Status |
|-----|----------|---------|--------|
| EGOS | @EGOSin_bot | egos-lab + INPI | ✅ Ativo |
| Intelink | @IntelinkBOT | INPI | ✅ Ativo |
| CarteiraLivre | @CarteiraLivreBOT | carteira-livre | ✅ Ativo |

**Ação:** Unificar comandos e routing — todos os bots podem rotear para o EGOS kernel via webhook

### X.com / Twitter

**Credenciais:** X_API_KEY, X_API_SECRET, X_BEARER_TOKEN (em /home/enio/egos/.env)

**Status:** 401 (autenticação falhando — pode ser token expirado ou OAuth v1 vs v2)

**Ação para Ativar:**
1. Verificar se o app ainda está ativo em developer.twitter.com
2. Regenerar tokens se necessário
3. Testar com OAuth 2.0 (X_API_OAUTH2_CLIENT_SECRET existe no .env)

**Estratégia de Conteúdo X.com:**
- Posts técnicos semanais (Agent updates, governance insights)
- Repostar Gem Hunter findings de relevância
- Engajar com comunidades: #AIAgents, #TypeScript, #OpenSource, #LLM

---

## 7. GESTÃO SEGURA DE CHAVES — Central Vault

### Inventário de Integrações Atualmente Espalhadas

| Serviço | Localização | Status |
|---------|-------------|--------|
| Alibaba DashScope | egos/.env | ✅ Primary LLM |
| OpenRouter | egos/.env | ✅ Fallback LLM |
| OpenAI | egos/.env | ✅ Backup |
| Anthropic | egos/.env | ✅ Claude API |
| Groq | egos/.env | ✅ Fast inference |
| EXA Search | egos/.env | ✅ Research |
| GitHub | egos/.env | ✅ Repos |
| Supabase | egos-lab/.env | ✅ Database |
| ASAAS | egos/.env | ✅ Pagamentos |
| X.com/Twitter | egos/.env | ⚠️ 401 erro |
| Telegram (@EGOSin) | egos-lab/.env + INPI | ✅ Bots ativos |
| Discord | egos/.env | ⚠️ Não testado |
| Serper | egos/.env | ✅ Search |
| Brave | egos/.env | ✅ Search |
| STITCH | egos/.env | ✅ Stitch API |

### Plano Central Vault (Recomendação)

**Opção 1: .egos/secrets.env (local apenas, gitignored)**
```bash
# ~/.egos/secrets.env — SSOT para todos os tokens
# Nunca commitar este arquivo!
source ~/.egos/secrets.env
```

**Opção 2: Hashicorp Vault (Hetzner VPS)**
- Setup simples com docker compose
- Todos os serviços buscam tokens do Vault
- Auditoria automática de acesso

**Opção 3: Supabase Edge Functions + secrets**
- Tokens armazenados no Supabase Vault
- Edge Functions de autenticação
- Já temos Supabase setup

**Recomendação:** Começar com **~/.egos/secrets.env** (simples, seguro, local) + migrar para Vault quando no Hetzner.

---

## 8. GRAFOS EGOS — Pesquisa dos Melhores

### SSOT (Single Source of Truth) — Estado Atual

**Kernel (egos/):**
- `agents/registry/agents.json` — Registry SSOT ✅
- `.guarani/` — Governance SSOT ✅
- `docs/SSOT_REGISTRY.md` — Cross-repo SSOT ✅
- `packages/shared/src/mycelium/reference-graph.ts` — Graph API (dead code, unused) ⚠️

**Lab (egos-lab/):**
- 18 agents com acesso a Supabase ✅
- CRCDM em ~/.egos/crcdm/ (blockchain-style DAG) ⚠️

### Grafos Identificados no Código

1. **Reference Graph** (`packages/shared/src/mycelium/reference-graph.ts`)
   - API: createGraph, findNode, findEdgesFrom, findEdgesTo, nodesByType, nodesByStatus
   - Status: ❌ Dead code (nenhum agente importa)
   - **Oportunidade:** Este é exatamente o grafo unificado que o usuário quer!

2. **CRCDM (Cross-Repo Change Detection Mesh)**
   - Location: `~/.egos/crcdm/`
   - Formato: Blockchain-style JSONL com hashes
   - Status: Parcialmente implementado

3. **Event Bus** (`agents/runtime/event-bus.ts`)
   - Grafo de eventos pub/sub
   - Status: ✅ Funcional, JSONL logging

4. **Intelink Intelligence Graph**
   - Location: `/home/enio/INTELINK/`
   - Extrai entidades de BOs, depoimentos, documentos policiais
   - Status: ⚠️ Precisa verificar

### Prioridade: Ativar Reference Graph

```typescript
// reference-graph.ts já tem toda a API. Falta integrar:
import { createGraph, findNode, addEdge } from "@egos/shared/mycelium/reference-graph";

// 1. Ao rodar dep_auditor → adicionar nós/arestas de dependências
// 2. Ao rodar archaeology_digger → adicionar nós de histórico
// 3. Visualizar no egos-web com D3.js ou Cytoscape.js
```

---

## 9. MOMENTUM — Como Crescer Agora

### Semana 1 (Foco: Fundação)
- [ ] Corrigir X.com API (regenerar tokens)
- [ ] Criar ~/.egos/secrets.env como SSOT de credenciais
- [ ] Setup @EGOSin_bot com comando /health (retorna status dos 6 agentes)
- [ ] Criar docker-compose.yml para Hetzner

### Semana 2 (Foco: Visibilidade)
- [ ] Publicar no GitHub (README + Quick Start)
- [ ] 1 post técnico no X.com sobre EGOS governance
- [ ] Ativar reference-graph com dados reais
- [ ] Deploy de staging no Hetzner

### Semana 3 (Foco: Usuários)
- [ ] Chatbot funcional em egos.ia.br
- [ ] @EGOSin_bot como ponto de entrada público
- [ ] Documentação /docs no site
- [ ] Primeiro demo ao vivo

### Semana 4 (Foco: Escala)
- [ ] A2A Agent Card publicado
- [ ] MCP server público
- [ ] Intelink demo real (extração de BO)
- [ ] Relatório de progresso Q1

### KPIs Q1 2026
| Métrica | Target | Status |
|---------|--------|--------|
| GitHub Stars | 50+ | 🔴 <10 |
| Telegram @EGOSin_bot users | 100+ | 🔴 0 |
| Agents no VPS | 6/6 | 🔴 0 |
| Projetos usando EGOS | 2+ | 🔴 1 (interno) |
| Posts X.com | 10+ | 🔴 0 |

---

## 10. DISSEMINATE — Ação Imediata

### O que Disseminar Hoje

1. **GitHub público** — Tornar egos e egos-lab públicos (ou criar mirror)
2. **@EGOSin_bot** — Ativar como ponto de entrada com /help, /health, /run
3. **egos.ia.br** — Deploy do egos-web com grafo de agentes
4. **npm registry** — Publicar @egos/shared como pacote público
5. **X.com** — Post anunciando EGOS governance framework

### Arquitetura de Disseminação

```
egos (kernel) ──── governance sync ──→ egos-lab
                                    ──→ 852
                                    ──→ br-acc
                                    ──→ commons
                                    ──→ carteira-livre

@EGOSin_bot ←──── webhook ─────────── egos-lab/apps/telegram-bot
egos.ia.br  ←──── deploy ─────────── Vercel/Hetzner
GitHub      ←──── git push ────────── mirror/público
npm         ←──── publish ─────────── @egos/shared
```

---

## CONCLUSÃO: Próximas 3 Ações (em ordem)

### 1. 🔑 CENTRALIZAR CHAVES (30 min)
Criar `~/.egos/secrets.env` com todos os tokens + rotear todos os repos para este arquivo

### 2. 🤖 ATIVAR @EGOSin_bot (2h)
Implementar /health e /run commands no egos-lab telegram-bot + deploy no Hetzner

### 3. 🌐 PUBLICAR NO GITHUB (4h)
README claro + Quick Start + tornar repositório público = começa a ter visibilidade

**Depois disso, o momentum se constrói sozinho.**

---

*"Formiguinha" funciona, mas com GitHub + bot público, você passa de formiguinha para colmeia.*

