# EGOS 24/7 Agent Swarm — Arquitetura & Blueprint de Implementação

> **Investigation Date:** 2026-03-26
> **Scope:** EGOS Ecosystem (egos, egos-lab, forja, carteira-livre, br-acc, 852, smartbuscas, INPI, policia)
> **Objective:** Definir arquitetura para agentes autônomos 24/7 e criar plano de implementação

---

## Executive Summary

Após análise profunda de toda a infraestrutura EGOS, pesquisa sobre orquestradores de agentes, e mapeamento dos ~30 agentes existentes, cheguei à seguinte conclusão:

**A melhor arquitetura para EGOS é: Swarm de Agentes via Railway Worker (24/7) + MCPs como Tools + NPM Package como SDK + API Gateway para integração externa**

**O que falta para 24/7:**
1. Railway Worker já existe (egos-lab/agents/worker/) — precisa apenas de scale e triggers
2. Scheduler para agentes autônomos (cron jobs)
3. 5 agentes críticos faltantes (listados abaixo)
4. Integração MCP → Agent Registry
5. NPM Package `@egos/agents` como interface unificada

---

## 1. Estado Atual — Inventário Completo

### 1.1 Infraestrutura EGOS

| Componente | Status | Capacidade | Custo/mês |
|------------|--------|------------|-----------|
| **Supabase** (4 projetos) | ✅ Ativo | PostgreSQL + RLS + Realtime | $0-25/projeto |
| **Vercel** (forja, carteira-livre) | ✅ Ativo | Next.js hosting auto-deploy | $0 |
| **Railway** (egos-lab-worker) | ✅ Ativo | Bun/Node workers 24/7 | ~$5-20 |
| **Contabo VPS** (br-acc, 852) | ✅ Ativo | Docker Compose, 5 serviços | $36 |
| **Redis** (Railway + VPS) | ✅ Ativo | Cache, queues, rate limiting | Incluído |
| **Evolution API** (WhatsApp) | 🔧 Partial | Self-hosted, precisa deploy | $0 |

**Gap Crítico:** Não temos um scheduler centralizado para agentes autônomos 24/7. O worker existe mas só roda sob demanda/manual.

### 1.2 Agentes Existentes (~30 no Registry)

#### Kernel (egos/agents/registry/agents.json)
| ID | Área | Status | Risco |
|----|------|--------|-------|
| dep_auditor | architecture | active | T0 |
| archaeology_digger | knowledge | active | T0 |
| chatbot_compliance_checker | knowledge | active | T0 |
| dead_code_detector | qa | active | T0 |
| capability_drift_checker | architecture | active | T0 |
| context_tracker | observability | active | T0 |

#### Lab (egos-lab/agents/registry/agents.json)
| ID | Área | Status | Trigger Atual |
|----|------|--------|---------------|
| security_scanner | security | active | pre-commit |
| idea_scanner | knowledge | active | pre-commit/manual |
| rho_calculator | observability | active | manual/weekly |
| code_reviewer | qa | active | pre-commit/manual |
| disseminator | knowledge | active | manual |
| ui_designer | design | active | manual |
| ssot_auditor | architecture | active | manual/weekly |
| ssot_fixer | architecture | active | manual |
| auth_roles_checker | auth | active | manual/ci |
| e2e_smoke | qa | pending | manual/pre-deploy |
| dep_auditor | architecture | active | manual/weekly |
| dead_code_detector | qa | active | manual/weekly |
| contract_tester | qa | active | manual/pre-push |
| integration_tester | qa | active | manual/pre-push |
| regression_watcher | qa | active | manual/pre-push |
| ai_verifier | qa | active | manual |
| orchestrator | orchestration | active | manual |
| ambient_disseminator | knowledge | active | session-end/manual |
| domain_explorer | architecture | active | manual |
| living_laboratory | architecture | active | session-end/weekly |
| social_media_agent | knowledge | pending | schedule/manual |
| security_scanner_v2 | security | active | manual/pre-push |
| showcase_writer | qa | active | manual |
| open_source_readiness | orchestration | active | manual |
| carteira_x_engine | observability | active | manual/webhook |
| gem_hunter | knowledge | active | manual/daily/pre-commit |
| ghost_hunter | discovery | dormant | discovery |
| autoresearch | qa | active | manual |
| report_generator | observability | active | manual/scheduled |

### 1.3 MCPs Ativos

| MCP | Provedor | Uso Principal | Status |
|-----|----------|---------------|--------|
| EXA | Exa AI | Web search, research | ✅ Active |
| Sequential-Thinking | MCP oficial | Complex reasoning | ✅ Active |
| Memory | MCP oficial | Persistent learning | ✅ Active |
| Filesystem | MCP oficial | File operations | ✅ Active |
| GitHub | MCP oficial | Repo operations | ✅ Active |
| Supabase | MCP oficial | DB operations | ✅ Active |
| Morph | Morph Labs | Code editing | ✅ Active |

### 1.4 Documentação Consolidada

| Repositório | Docs Count | Status |
|-------------|------------|--------|
| egos | ~5 | ✅ Enxuto |
| egos-lab | 100+ | 🔴 Crítico (necessita purge) |
| forja | 4 | ✅ Consolidado (nesta sessão) |
| carteira-livre | ~0 | ✅ Mínimo |
| br-acc | 30+ | 🔴 Necessita consolidação |
| 852 | ~10 | 🟡 Ok |
| smartbuscas | 15+ | 🔴 Duplicação Cloudflare |
| INPI | ~5 | 🟡 Ok |
| policia | ~3 | ✅ Enxuto |

---

## 2. Análise de Orquestradores (Gem Hunter Research)

### 2.1 Frameworks Comparados

| Framework | Melhor Para | Learning Curve | Produção | Stars |
|-----------|-------------|----------------|----------|-------|
| **LangGraph** | Workflows complexos, state machines | Medium-High | ✅ Excelente | 25k |
| **CrewAI** | Multi-agent crews, roles | Low | 🟡 Bom | 44.6k |
| **AutoGen/AG2** | Pesquisa, conversação | Medium | 🟡 Experimental | 4.2k |
| **OpenAI Agents SDK** | OpenAI ecosystem, simplicidade | Low | ✅ Excelente | 19.1k |
| **Pydantic AI** | Type-safe, produção | Low-Medium | ✅ Excelente | 15.1k |
| **Temporal** | Workflows duráveis, retries | Medium | ✅ Enterprise | N/A |

### 2.2 Descobertas Críticas

**De acordo com pesquisa multi-fonte (2025-2026):**

> **"The framework matters far less than the infrastructure you build around it."** — BSWEN Analysis

Fatores que determinam sucesso 24/7:
1. **State persistence** — Can you resume after crashes?
2. **Retry logic** — Can you handle transient failures?
3. **Observability** — Can you debug what happened?
4. **Rate limiting** — Can you avoid API quota exhaustion?
5. **Domain knowledge** — Can you validate outputs?

---

## 3. Arquitetura Recomendada: EGOS Agent Swarm

### 3.1 Visão Geral

```
┌─────────────────────────────────────────────────────────────────────┐
│                     EGOS AGENT SWARM 24/7                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐        │
│  │   SCHEDULER  │    │   WORKER     │    │   QUEUE      │        │
│  │   (cron)     │◄──►│   (Railway)  │◄──►│  (Redis)     │        │
│  │              │    │  Bun/Node    │    │              │        │
│  └──────────────┘    └──────────────┘    └──────────────┘        │
│         │                    │                    │                 │
│         ▼                    ▼                    ▼                 │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │              AGENT ORCHESTRATOR (egos-lab)                 │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │  │
│  │  │Security │ │  QA     │ │Knowledge│ │Arch     │          │  │
│  │  │Scanner  │ │Tester   │ │Dissem.  │ │Explorer │          │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘          │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                    │
│                              ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │                    MCP TOOL LAYER                            │  │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐    │  │
│  │  │  EXA   │ │GitHub  │ │Supabase│ │ Files  │ │ Memory │    │  │
│  │  │(search)│ │(repos) │ │  (db)  │ │(fs)    │ │(learn) │    │  │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘    │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                              │                                    │
│                              ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │              LLM ROUTER (Multi-Provider)                     │  │
│  │    Alibaba (Qwen) ◄──► OpenRouter ◄──► Groq ◄──► Local      │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     INTERFACES EXTERNAS                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  NPM Package │  │   REST API   │  │   WebSocket  │              │
│  │ @egos/agents │  │  /api/agent  │  │  /ws/stream  │              │
│  │   (SDK)      │  │              │  │              │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Componentes Detalhados

#### A. Scheduler (Novo — 24/7 Trigger)

**Tecnologia:** node-cron / bullmq / temporal (MVP = node-cron)

```typescript
// agents/scheduler/cron-jobs.ts
export const SCHEDULED_AGENTS = [
  { agent: 'gem_hunter', cron: '0 9 * * *', timezone: 'America/Sao_Paulo' },
  { agent: 'rho_calculator', cron: '0 0 * * 0', timezone: 'UTC' }, // Weekly
  { agent: 'security_scanner', cron: '0 */6 * * *', timezone: 'UTC' }, // Every 6h
  { agent: 'social_media_agent', cron: '0 10,14,18 * * *', timezone: 'America/Sao_Paulo' },
  { agent: 'living_laboratory', cron: '0 0 * * 0', timezone: 'UTC' },
  { agent: 'report_generator', cron: '0 8 * * *', timezone: 'America/Sao_Paulo' },
];
```

#### B. Worker (Existente — egos-lab/agents/worker/)

Já temos um worker hardened em produção no Railway:
- Rate limiting (30 req/min)
- Task timeout (10 min)
- Queue depth guard (max 100)
- Structured JSON logging
- Health + metrics endpoints
- Redis integration

**Gap:** Só falta conectar o scheduler para triggers automáticos.

#### C. Agent Orchestrator (Existente)

```typescript
// agents/agents/orchestrator.ts (já existe)
export class AgentOrchestrator {
  async runAll(mode: 'dry_run' | 'execute'): Promise<HealthReport> {
    const agents = await this.registry.listActive();
    const results = await Promise.all(
      agents.map(agent => this.runAgent(agent, mode))
    );
    return this.aggregate(results);
  }
}
```

#### D. MCP Tool Layer (Existente)

MCPs já estão ativos e funcionando. Precisamos apenas de um wrapper para expor como tools aos agentes.

#### E. LLM Router (Existente — @egos/shared)

```typescript
// packages/shared/src/model-router.ts (já existe)
export class ModelRouter {
  route(task: Task): LLMProvider {
    if (task.type === 'reasoning') return 'claude-opus-4.6';
    if (task.type === 'fast') return 'qwen-flash';
    if (task.type === 'code') return 'qwen3-coder-plus';
    return 'qwen-plus'; // default
  }
}
```

#### F. NPM Package @egos/agents (Novo)

**Proposta:** Criar um package NPM que exporte:

```typescript
// @egos/agents SDK
export { AgentOrchestrator } from './orchestrator';
export { AgentRegistry } from './registry';
export { ModelRouter } from './model-router';
export { MCPToolKit } from './mcp-tools';
export { Scheduler } from './scheduler';

// CLI
export { runAgent, listAgents, scheduleAgent } from './cli';
```

**Uso:**
```bash
npm install @egos/agents
npx @egos/agents run gem_hunter --dry
npx @egos/agents schedule --list
```

#### G. REST API Gateway (Novo)

```typescript
// api/src/routes/agents.ts
app.post('/api/agent/:id/run', async (req, res) => {
  const { id } = req.params;
  const { mode, params } = req.body;
  const result = await orchestrator.runAgent(id, mode, params);
  res.json(result);
});

app.get('/api/agent/:id/status', async (req, res) => {
  const status = await registry.getStatus(req.params.id);
  res.json(status);
});

app.ws('/ws/agent/:id/stream', (ws, req) => {
  // Real-time agent execution streaming
});
```

---

## 4. Agentes 24/7 — O Que Falta

### 4.1 Agentes Críticos Faltantes

| Agente | Prioridade | Função 24/7 | Trigger |
|--------|------------|-------------|---------|
| **uptime_monitor** | P0 | Monitora saúde de todos os serviços | Every 5 min |
| **quota_guardian** | P0 | Monitora quotas de API, alerta antes de exceder | Every 15 min |
| **drift_sentinel** | P0 | Detecta drift entre SSOT e projeções | Every 1 hour |
| **cost_optimizer** | P1 | Analisa custos de LLM, sugere otimizações | Daily |
| **auto_remediator** | P1 | Tenta auto-corrigir problemas detectados | On alert |
| **pr_curator** | P1 | Monitora PRs abertos, sugere merges/actions | Every 2 hours |
| **community_manager** | P2 | Responde a issues, discussions automaticamente | On event |
| **content_curator** | P2 | Seleciona e publica conteúdo de destaque | Daily |

### 4.2 Agentes Existentes que Precisam de 24/7

| Agente | Status Atual | Precisa de | Esforço |
|--------|--------------|------------|---------|
| gem_hunter | manual/daily | schedule: daily 9am | 30 min |
| social_media_agent | pending | schedule: 3x/day | 2 horas |
| security_scanner | pre-commit/manual | schedule: every 6h | 30 min |
| rho_calculator | manual/weekly | schedule: weekly | 30 min |
| living_laboratory | session-end/weekly | schedule: weekly | 30 min |
| report_generator | manual/scheduled | schedule: daily 8am | 30 min |

---

## 5. Blueprint de Implementação

### Fase 1: Foundation (1-2 semanas)

#### Semana 1: Scheduler + Worker Integration
- [ ] Implementar `agents/scheduler/` com node-cron
- [ ] Conectar scheduler ao worker existente
- [ ] Adicionar triggers automáticos para agentes existentes
- [ ] Testar: gem_hunter, security_scanner, rho_calculator

#### Semana 2: Agentes Críticos P0
- [ ] Criar `uptime_monitor` (ping Supabase, Vercel, VPS)
- [ ] Criar `quota_guardian` (monitor Alibaba/OpenRouter/Groq)
- [ ] Criar `drift_sentinel` (compara AGENTS.md vs código real)

### Fase 2: SDK + API (2-3 semanas)

#### Semana 3: NPM Package
- [ ] Criar package `@egos/agents`
- [ ] Exportar orchestrator, registry, scheduler
- [ ] CLI: `npx @egos/agents run <id>`
- [ ] Publicar no NPM (private ou public)

#### Semana 4: REST API
- [ ] Criar `api/src/routes/agents.ts`
- [ ] Endpoints: POST /run, GET /status, GET /list
- [ ] WebSocket streaming
- [ ] Deploy no Railway

#### Semana 5: Integração MCP → Agents
- [ ] Criar `MCPToolKit` wrapper
- [ ] Mapear MCPs como tools para agentes
- [ ] Documentar: como agentes usam MCPs

### Fase 3: Autonomous Agents (3-4 semanas)

#### Semana 6: Agentes P1
- [ ] Criar `cost_optimizer`
- [ ] Criar `auto_remediator` (auto-fix simples)
- [ ] Criar `pr_curator`

#### Semana 7: Observability Completa
- [ ] Dashboard de agentes (status, histórico, métricas)
- [ ] Alertas (WhatsApp/Email) quando agente falha
- [ ] Logs centralizados (Supabase + JSON)

#### Semana 8: Documentação + Disseminação
- [ ] Criar `docs/AGENT_SWARM.md`
- [ ] Tutorial: "Como criar um agente 24/7"
- [ ] Disseminar para todos os repos via `/disseminate`

---

## 6. Arquitetura: Por Que Não Outras Opções?

### 6.1 Por Que Não Só MCP?

**Problema:** MCPs são tools, não orquestradores. Eles não têm:
- Scheduling
- State persistence
- Retry logic
- Multi-agent coordination

**Veredito:** MCPs são a **tool layer**, não a **orchestration layer**.

### 6.2 Por Que Não Só NPM Package?

**Problema:** Package é consumido, não executa sozinho.

**Veredito:** NPM package é o **SDK para desenvolvedores**, não o **runtime 24/7**.

### 6.3 Por Que Não Só API?

**Problema:** API é chamada, não proativa.

**Veredito:** API é o **interface externo**, não o **scheduler interno**.

### 6.4 Por Que Swarm?

**Vantagens:**
- Cada agente é autônomo
- Podem comunicar entre si (Mycelium events)
- Escalável (adicionar novo agente = 1 arquivo)
- Resiliente (falha de um não derruba outros)
- Observável (cada agente loga separadamente)

---

## 7. Métricas de Sucesso

| Métrica | Atual | Target (3 meses) |
|---------|-------|------------------|
| Agentes rodando 24/7 | 0 | 15+ |
| Agentes autônomos | 0 | 10+ |
| Tempo médio entre falhas | N/A | >7 dias |
| Coverage de repos monitorados | 2 | 9 (100%) |
| Alertas proativos/mês | 0 | 20+ |
| Auto-remediações/mês | 0 | 5+ |

---

## 8. Custo Estimado (24/7 Swarm)

| Componente | Custo/mês | Justificativa |
|------------|-----------|---------------|
| Railway Worker (scheduler) | ~$5-10 | 1 container always-on |
| Railway Worker (executor) | ~$10-20 | 1-2 containers burst |
| Redis (Railway) | ~$0-5 | Small plan |
| Supabase (logs/metrics) | ~$0 | Free tier |
| LLM calls (agentes) | ~$10-30 | Qwen/Gemini Flash |
| **TOTAL** | **~$25-65/mês** | Para 15 agentes 24/7 |

---

## 9. Próximos Passos Imediatos

### Hoje (Action Items)

1. **Aprovar arquitetura** — Revisar este documento, ajustar se necessário
2. **Criar TASKS.md entries** — Adicionar tasks EGOS-XXX para cada fase
3. **Começar Fase 1** — Implementar scheduler (estimativa: 4-8 horas)

### Esta Semana

1. Implementar scheduler + conectar 3 agentes existentes
2. Criar 3 agentes P0 (uptime_monitor, quota_guardian, drift_sentinel)
3. Testar swarm em modo dry_run

### Próximo Mês

1. Completar Fase 2 (SDK + API)
2. Ter 10 agentes rodando 24/7
3. Dashboard observability funcional

---

## 10. Referências

### Documentos Relacionados
- `/home/enio/egos/docs/MCP_ORCHESTRATION_STRATEGY.md` — Model routing
- `/home/enio/egos-lab/agents/worker/index.ts` — Worker hardened
- `/home/enio/egos-lab/agents/registry/agents.json` — Agent registry completo
- `/home/enio/egos/docs/SYSTEM_MAP.md` — Kernel system map
- `/home/enio/egos/.guarani/templates/pre-commit-canonical.sh` — Automation

### Pesquisa (Gem Hunter)
- LangGraph vs CrewAI vs AutoGen: BSWEN, Roast Dev, Softmax Data
- Framework comparison 2025-2026
- Production agent patterns

---

*"Agentes 24/7 não são sobre ter mais código. São sobre ter código que trabalha enquanto você dorme."*
