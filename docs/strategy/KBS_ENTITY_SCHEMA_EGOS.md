# KBS Entity Schema — EGOS Demo Case

> **Version:** 1.0.0 | **Data:** 2026-04-12
> **Propósito:** Schema canônico de entidades e relacionamentos do EGOS para uso como caso de demonstração do KBS v2.
> **SSOT:** Este arquivo. Atualizar quando novos tipos de entidade forem validados.
> **Context:** EGOS é o próprio "primeiro cliente" do KBS. A base EGOS tem 82.192+ wikilinks, 45 agents, 333+ docs.

---

## Visão Geral

O KBS v2 vai além de RAG plano (doc→chunks→embedding). Para cada setor, definimos:
1. **Tipos de entidade** — o que existe naquele domínio
2. **Atributos** — propriedades de cada entidade
3. **Relacionamentos** — como entidades se conectam
4. **Fontes de extração** — de onde extrair cada tipo

O EGOS tem o schema mais maduro: é onde temos dados reais, auditoria de 60 dias, e validação de todos os tipos.

---

## Entidades EGOS

### 1. Agent

**O que é:** Agente de IA registrado no kernel — pode ser kernel (24) ou lab (21).

| Atributo | Tipo | Exemplo | Fonte |
|----------|------|---------|-------|
| `id` | string | `gem-hunter` | `agents/registry/agents.json` |
| `name` | string | `Gem Hunter` | agents.json |
| `type` | enum | `kernel \| lab \| external` | agents.json |
| `status` | enum | `active \| dormant \| deprecated` | agents.json |
| `entrypoint` | string | `agents/agents/gem-hunter.ts` | agents.json |
| `trigger` | string | `cron: 0 3 * * *` | agents.json |
| `description` | string | — | agents.json |
| `last_run` | datetime | `2026-04-11T03:00:00Z` | agent_events (Supabase) |
| `run_count_7d` | int | 7 | agent_events |
| `proof_command` | string | `bun agents/agents/gem-hunter.ts --dry` | docs/agents/*.md |

**Relacionamentos:**
- `TRIGGERS → Event` (1:N — agent dispara eventos)
- `READS → Capability` (N:M — agent lê capabilities do registry)
- `WRITES → Document` (N:M — agent gera documentos)
- `DEPENDS_ON → Agent` (N:M — orquestração)

---

### 2. Task

**O que é:** Item em TASKS.md com ID canônico, prioridade e estado.

| Atributo | Tipo | Exemplo | Fonte |
|----------|------|---------|-------|
| `id` | string | `KBS-027` | TASKS.md |
| `prefix` | string | `KBS` | TASKS.md |
| `priority` | enum | `P0 \| P1 \| P2 \| P3` | TASKS.md |
| `status` | enum | `todo \| in_progress \| done` | TASKS.md |
| `title` | string | `Entity Schema EGOS` | TASKS.md |
| `estimate` | string | `3h` | TASKS.md |
| `completed_at` | date | `2026-04-12` | TASKS.md |
| `sprint` | string | `2026-04-12` | TASKS.md / commit timestamp |

**Relacionamentos:**
- `BLOCKS → Task` (N:M — dependência)
- `IMPLEMENTS → Capability` (N:M — task entrega capacidade)
- `TRACKED_IN → Commit` (N:M — commits que avançam a task)
- `CREATED_BY → Decision` (N:1 — quórum ou sessão que gerou a task)

---

### 3. Capability

**O que é:** Capacidade funcional listada em `docs/CAPABILITY_REGISTRY.md`.

| Atributo | Tipo | Exemplo | Fonte |
|----------|------|---------|-------|
| `id` | string | `CAP-KB-001` | CAPABILITY_REGISTRY.md |
| `section` | string | `KB-as-a-Service` | CAPABILITY_REGISTRY.md |
| `name` | string | `PDF Ingest` | CAPABILITY_REGISTRY.md |
| `status` | enum | `live \| partial \| planned` | CAPABILITY_REGISTRY.md |
| `evidence` | string | `scripts/kb-ingest.ts` | CAPABILITY_REGISTRY.md |
| `tested` | boolean | `true` | test suite |
| `last_verified` | date | `2026-04-12` | pre-commit / CI |

**Relacionamentos:**
- `IMPLEMENTED_BY → Script \| Package` (1:N)
- `TESTED_BY → TestFile` (1:N)
- `PART_OF → Product` (N:1 — qual produto entrega esta capacidade)
- `DEPENDS_ON → Integration` (N:M — Supabase, Groq, Guard)

---

### 4. Incident

**O que é:** Incidente registrado (INC-001, INC-002, INC-003, INC-004).

| Atributo | Tipo | Exemplo | Fonte |
|----------|------|---------|-------|
| `id` | string | `INC-001` | docs/INCIDENTS/ |
| `title` | string | `Force Push Main` | docs/INCIDENTS/ |
| `severity` | enum | `CRITICAL \| HIGH \| MODERATE` | docs/INCIDENTS/ |
| `date` | date | `2026-04-06` | docs/INCIDENTS/ |
| `root_cause` | string | — | docs/INCIDENTS/ |
| `fix_commit` | string | `4ee5c7f` | git log |
| `prevention` | string | `husky pre-push + branch protection` | docs/INCIDENTS/ |
| `status` | enum | `resolved \| monitoring \| open` | docs/INCIDENTS/ |

**Relacionamentos:**
- `CAUSED_BY → Commit` (N:1)
- `FIXED_BY → Commit` (N:1)
- `PREVENTED_BY → Hook \| Workflow` (N:M)
- `GENERATED → Task` (1:N — tasks de remediação)

---

### 5. Decision

**O que é:** Decisão estratégica ou arquitetural registrada, tipicamente via Quórum.

| Atributo | Tipo | Exemplo | Fonte |
|----------|------|---------|-------|
| `id` | string | `DEC-2026-04-11-single-pursuit` | docs/quorum/ |
| `title` | string | `Single Pursuit Protocol` | docs/quorum/ |
| `date` | date | `2026-04-11` | docs/quorum/ |
| `quorum` | boolean | `true` | docs/quorum/ |
| `reviewers` | string[] | `[Gemini, Grok, GPT, Perplexity]` | docs/quorum/ |
| `outcome` | string | `Guard Brasil Hybrid as only pursuit` | docs/quorum/ |
| `reversibility` | enum | `reversible \| hard \| irreversible` | manual |

**Relacionamentos:**
- `GENERATES → Task` (1:N)
- `UPDATES → CLAUDE.md \| Strategy` (N:M)
- `CONTRADICTS → Decision` (N:M — quando pivota)
- `REVIEWED_BY → ExternalLLM` (N:M)

---

### 6. Pattern

**O que é:** Padrão de engenharia documentado que se repete (ex: Auditable Live Sandbox, Evidence-First).

| Atributo | Tipo | Exemplo | Fonte |
|----------|------|---------|-------|
| `id` | string | `PAT-001` | CAPABILITY_REGISTRY.md §13 |
| `name` | string | `Auditable Live Sandbox` | CAPABILITY_REGISTRY.md |
| `context` | string | `Guard Brasil GTM` | — |
| `problem` | string | `Como demo sem dados reais?` | — |
| `solution` | string | `4 zonas, SHA-256, audit trail inline` | — |
| `first_used_in` | string | `guard-brasil-web` | git log |
| `reused_in` | string[] | `[852, forja]` | grep |

**Relacionamentos:**
- `APPLIED_IN → Product` (1:N)
- `SOLVES → Problem` (N:1)
- `RELATED_TO → Pattern` (N:M)
- `DOCUMENTED_IN → Capability` (N:1)

---

### 7. Integration

**O que é:** Serviço externo integrado ao kernel (MCP, API, Supabase, etc).

| Atributo | Tipo | Exemplo | Fonte |
|----------|------|---------|-------|
| `id` | string | `INT-supabase` | integrations/manifests/ |
| `name` | string | `Supabase` | — |
| `type` | enum | `mcp \| api \| sdk \| database \| infra` | — |
| `status` | enum | `live \| degraded \| offline` | health check |
| `health_url` | string | `https://guard.egos.ia.br/health` | — |
| `manifest_file` | string | `integrations/manifests/supabase.json` | — |
| `cost_tier` | string | `Free / Pro / usage-based` | billing |

**Relacionamentos:**
- `USED_BY → Agent \| Script \| Product` (1:N)
- `REQUIRES → EnvVar` (1:N — configuração)
- `MONITORED_BY → Agent` (N:M)

---

## Relacionamentos-chave (resumo)

```
Agent ──TRIGGERS──> Event
Agent ──READS──> Capability
Task ──IMPLEMENTS──> Capability
Task ──TRACKED_IN──> Commit
Incident ──CAUSED_BY──> Commit
Incident ──GENERATED──> Task
Decision ──GENERATES──> Task
Pattern ──APPLIED_IN──> Product
Integration ──USED_BY──> Agent
```

---

## Como usar no KBS v2

### Extração automática

| Tipo | Script | Fonte |
|------|--------|-------|
| Agent | `bun scripts/extract-agents.ts` | agents.json + agents/*.ts |
| Task | `bun scripts/extract-tasks.ts` | TASKS.md (markdown parser) |
| Capability | `bun scripts/extract-capabilities.ts` | CAPABILITY_REGISTRY.md |
| Incident | `bun scripts/extract-incidents.ts` | docs/INCIDENTS/*.md |
| Decision | `bun scripts/extract-decisions.ts` | docs/quorum/*/decision.md |

### Tabelas Supabase (KBS-028)

```sql
-- egos_entities
id, tenant_id, type (agent|task|capability|incident|decision|pattern|integration),
name, attributes jsonb, source_file, created_at, updated_at

-- egos_relationships
id, source_entity_id, target_entity_id, relation_type,
context text, doc_source, created_at
```

### Relatório de Inteligência (KBS-031)

Template do relatório semanal EGOS:
1. **Agentes ativos vs dormentes** (Agent status distribution)
2. **Tasks P0 abertas há mais de 7 dias** (Task aging)
3. **Capabilities sem evidência** (Capability.tested = false)
4. **Incidents não resolvidos** (Incident.status = open)
5. **Decisões sem tasks associadas** (Decision orphans)
6. **Integrações degradadas** (Integration.status ≠ live)

---

## Adaptação por Setor

O schema EGOS serve como **template base**. Cada setor substitui os tipos:

| EGOS | Delegacia | Advocacia | Agronegócio |
|------|-----------|-----------|-------------|
| Agent | Investigador | Advogado | Agrônomo |
| Task | Diligência | Prazo Processual | Safra / Atividade |
| Capability | Técnica Policial | Área Jurídica | Técnica Agrícola |
| Incident | Ocorrência / BO | Audiência | Evento Climático |
| Decision | Decisão Judicial | Decisão do Processo | Plano de Cultivo |
| Pattern | Modus Operandi | Jurisprudência | Boas Práticas |
| Integration | BNMP / Datajud | TJ / CNPJ | IBGE / CPTEC |

Ver: `docs/strategy/KBS_DELEGACIA_ENTITY_SCHEMA.md` (KBS-033) — a ser criado.

---

*SSOT: este arquivo. Próximo passo: KBS-028 (migração Supabase) + KBS-029 (extrator automático).*
