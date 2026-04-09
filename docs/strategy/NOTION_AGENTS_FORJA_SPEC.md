# Agentes EGOS na Forja — Spec de Solução

> **Versão:** 1.0.0 — 2026-04-09
> **SSOT:** `docs/strategy/NOTION_AGENTS_FORJA_SPEC.md`
> **Tarefa:** NOTION-AGENTS-003
> **Contexto:** Notion anunciou em 2026-04-08 o suporte nativo a Claude AI Agents. "Your task board is Claude's to-do list."

---

## 1. Visão

A Notion agora permite que agentes Claude leiam e executem diretamente a partir de task boards. Para a FORJA (metalúrgica em Patos de Minas, MG), isso significa:

**Task board FORJA → Claude pega como to-do → executa com governança EGOS → time aprova no Notion**

Sem o EGOS como kernel de governança, isso é um agente solto com acesso à base de dados da empresa. Com o EGOS, cada ação tem rastreabilidade, regras aplicadas e conformidade LGPD.

---

## 2. Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│  NOTION (UI + Orquestração)                                 │
│  ┌────────────┐  ┌─────────────────┐  ┌──────────────────┐ │
│  │ Task Board │  │ Formulários     │  │ KB da FORJA      │ │
│  │ FORJA      │  │ de Clientes     │  │ (specs, ABNT)    │ │
│  └─────┬──────┘  └────────┬────────┘  └────────┬─────────┘ │
└────────┼──────────────────┼────────────────────┼────────────┘
         │                  │                    │
         ▼                  ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│  CLAUDE AGENT HARNESS (Anthropic)                           │
│  - Lê tasks do Notion como to-do list                       │
│  - Executa passos autonomamente                             │
│  - Retorna resultado ao Notion                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  EGOS GOVERNANCE KERNEL                                     │
│  ┌──────────────────┐  ┌─────────────────┐                 │
│  │ .guarani/ rules  │  │ Frozen Zones    │                 │
│  │ - PIPELINE.md    │  │ - runner.ts     │                 │
│  │ - PREFERENCES.md │  │ - event-bus.ts  │                 │
│  │ - RULES_INDEX.md │  │ - .husky/hooks  │                 │
│  └──────────────────┘  └─────────────────┘                 │
│  ┌──────────────────┐  ┌─────────────────┐                 │
│  │ Audit Trail      │  │ Guard Brasil    │                 │
│  │ agent_events     │  │ LGPD Check      │                 │
│  │ (Supabase)       │  │ (CPF/CNPJ/PII)  │                 │
│  └──────────────────┘  └─────────────────┘                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
         Resultado volta ao Notion para aprovação humana
```

**Camadas de responsabilidade:**

| Camada | Papel | Tecnologia |
|--------|-------|------------|
| Orquestração / UI | Task boards, contexto, aprovação | Notion |
| Execução de agente | Raciocínio, geração, chamadas de tool | Claude (Anthropic) |
| Governança | Regras, frozen zones, audit trail | EGOS `.guarani/` |
| Conformidade LGPD | Detecção e mascaramento de PII | Guard Brasil API |
| Persistência | Eventos, logs, auditoria | Supabase `agent_events` |

---

## 3. Casos de Uso Imediatos

### 3.1 Orçamento Automático

**Gatilho:** Cliente preenche formulário Notion com especificações de peça (material, dimensões, tolerância, quantidade, prazo).

**Fluxo:**
1. Notion cria página "Orçamento #042 — Cliente X" no board com status `Novo`
2. Claude Agent detecta a página via Notion Agents harness
3. Verifica Guard Brasil: CPF/CNPJ do cliente → mascarado antes de entrar no contexto
4. Busca na KB FORJA: tabela de preços de insumos, histórico de orçamentos similares
5. Gera documento de orçamento com valores, prazo de entrega e observações técnicas
6. Cria subpágina "Proposta #042" e move status para `Aguardando Aprovação Comercial`
7. Auditoria registrada em `agent_events`: `{agent_id: "notion-budget-agent", action: "draft_created", doc_id: "ORC-042", timestamp: "..."}`

**Gate humano:** Supervisor comercial aprova ou ajusta antes de enviar ao cliente.

---

### 3.2 Atualização de Status de Produção

**Gatilho:** Operador atualiza status de uma ordem de produção no Notion (ex.: `Em Usinagem` → `Controle de Qualidade`).

**Fluxo:**
1. Notion trigger detecta mudança de status na página da ordem
2. Claude Agent consulta: quem precisa saber? (próximo responsável na fila, supervisor de turno)
3. Guard Brasil verifica se há dados pessoais nas notas do operador
4. Envia notificação Notion para as pessoas relevantes com resumo da transição
5. Atualiza campos calculados: tempo em cada etapa, estimativa de conclusão
6. Registra evento no audit trail com `stage_transition`, `operator_id`, `timestamp`

**Diferencial:** Sem o agente, operador avisa manualmente. Com o agente, a informação flui automaticamente com rastreabilidade de quem fez o quê e quando.

---

### 3.3 Consulta Técnica ABNT

**Gatilho:** Engenheiro digita pergunta em página Notion: "Qual é a tolerância dimensional para eixos de transmissão em aço SAE 1045 conforme ABNT?"

**Fluxo:**
1. Página com template "Consulta Técnica" detectada pelo Notion Agent harness
2. Claude busca na KB FORJA: documentos ABNT indexados, especificações internas
3. Responde diretamente na página com:
   - Resposta técnica objetiva
   - Citação: `ABNT NBR 6158:2013 — Tabela 3, Grau IT7`
   - Link interno para o documento na KB FORJA
4. Status da página muda para `Respondido — Revisar`
5. Evento auditado: `{query: "tolerância SAE 1045", norm_cited: "NBR 6158:2013", confidence: 0.94}`

**Gate EGOS:** Respostas técnicas com confiança < 0.85 recebem flag automático `Requer Revisão Humana`.

---

## 4. Governança EGOS

### Regras `.guarani/` aplicadas

| Arquivo | Regra aplicada |
|---------|---------------|
| `PIPELINE.md` | Toda ação do agente passa pela sequência: read → validate → execute → audit |
| `PREFERENCES.md` | Agente não envia comunicações externas sem aprovação humana explícita |
| `RULES_INDEX.md` | Lookup de qual regra aplicar por tipo de ação |

### Frozen Zones

As seguintes zonas **nunca são modificadas** por agentes Notion, mesmo com permissão explícita:

```
agents/runtime/runner.ts       — runtime de execução de agentes
agents/runtime/event-bus.ts    — barramento de eventos
.husky/pre-commit              — pipeline de validação de commits
.guarani/orchestration/        — regras de orquestração
```

Qualquer tentativa de modificação nesses caminhos é bloqueada no pré-commit e registrada como evento de segurança.

### Audit Trail

Cada ação do agente gera um registro em Supabase (`agent_events`):

```json
{
  "agent_id": "notion-forja-agent",
  "action": "budget_draft_created",
  "context": {
    "notion_page_id": "...",
    "client_id_masked": "CPF_***",
    "doc_ref": "ORC-042"
  },
  "outcome": "success",
  "reviewed_by": null,
  "timestamp": "2026-04-09T14:32:11Z"
}
```

O campo `reviewed_by` é preenchido quando um humano aprova a ação no Notion. Ações não revisadas em 48h geram alerta no HQ (`hq.egos.ia.br`).

---

## 5. Diferencial vs Usar Claude Diretamente

**Sem EGOS:**

- Claude acessa o Notion sem regras → pode modificar qualquer página
- Sem Guard Brasil → CPF de cliente aparece literalmente no contexto do modelo
- Sem audit trail → ninguém sabe o que o agente fez, quando, e por quê
- Sem frozen zones → agente pode alterar configurações críticas de sistema
- Conformidade LGPD: responsabilidade de quem? Ninguém sabe

**Com EGOS como kernel:**

| Dimensão | Sem EGOS | Com EGOS |
|----------|----------|----------|
| Dados pessoais | No prompt do modelo | Mascarados via Guard Brasil antes |
| Rastreabilidade | Zero | `agent_events` com timestamp + actor |
| Zonas proibidas | Tudo acessível | Frozen zones bloqueadas em pré-execução |
| Aprovação humana | Opcional | Forçada por `PREFERENCES.md` |
| Responsabilidade LGPD | Difusa | Mapeada: EGOS como processador, FORJA como controlador |

**O EGOS transforma um agente poderoso em um funcionário responsável.**

---

## 6. Próximos Passos

| ID | Ação | Owner | Prazo |
|----|------|-------|-------|
| NOTION-AGENTS-001 | Entrar na waitlist Notion Claude Agents (notion.so/agents) | Enio (ação humana) | ASAP |
| NOTION-AGENTS-002 | Atualizar CAPABILITY_REGISTRY §27 — documentar Notion como orchestration layer | Claude | Sprint atual |
| NOTION-AGENTS-004 | Template Notion "EGOS-Governed Task Board" com propriedades: `priority`, `agent`, `spec_link`, `audit_id`, boards Backlog/In Progress/Review/Done | Claude | Após waitlist |
| NOTION-AGENTS-005 | Video PT-BR "Orçamentos 10x mais rápidos na metalúrgica com Notion + Claude + EGOS" | Enio | Após feature live |

**Gate para execução real:** Notion Claude Agents precisa sair da waitlist. Enquanto isso, o fluxo pode ser simulado com Notion API + script TS que chama o EGOS kernel manualmente.

---

> **Fato:** Notion anunciou suporte nativo a Claude Agents em 2026-04-08.
> **Inferência:** A integração com EGOS governance é diferencial competitivo claro para clientes industriais com obrigações LGPD.
> **Proposta:** FORJA como projeto-piloto = caso de uso real + material de marketing para o segmento industrial brasileiro.
