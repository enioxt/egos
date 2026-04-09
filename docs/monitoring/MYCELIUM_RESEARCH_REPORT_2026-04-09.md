# Relatório de Pesquisa: Mycelium — Estado Atual e Decisões
> **Data:** 09/04/2026 16:45 UTC-3  
> **Pesquisa:** Ampla análise cronológica e documental  
> **Fontes:** 93 arquivos, 1082 matches, git history, decisões arquivadas

---

## 🎯 Resposta Direta às Perguntas

### 1. Qual o nome técnico atual do Mycelium?

**Resposta:** **Ainda é "Mycelium" no código**, mas existe uma **decisão arquivada** (EGOS-118) para renomear para **"Repository Mesh"** em contextos técnicos.

| Contexto | Nome Atual | Nome Planejado | Status |
|----------|-----------|----------------|--------|
| Código (`event-bus.ts`, `reference-graph.ts`) | `MyceliumBus`, `MyceliumEvent` | Manter (custo de refactor alto) | ✅ Ativo |
| Documentação técnica | Mycelium | **Repository Mesh** | ⚠️ EGOS-118 pendente |
| BLUEPRINT-EGOS (filosofia) | Mycelium | Mycelium (mantido) | ✅ Apropriado |

**Decisão Documentada:**
> "Mycelium" → "Repository Mesh" in technical docs (EGOS-118)  
> Keep "Mycelium" in BLUEPRINT-EGOS (philosophy context is appropriate)  
> — `egos-archive/docs/TERMINOLOGY_SANITIZATION_ANALYSIS.md`, 2026-03-24

---

## 2. NÃO, o Mycelium não ficou obsoleto — mas foi **contido**

### O que aconteceu (Cronologia):

| Data | Evento | Impacto |
|------|--------|---------|
| **2026-03-07** | `REFERENCE_GRAPH_DESIGN.md` criado | Define escopo realista |
| **2026-03-19** | `NETWORK_PLAN.md` v2.1.1 | Fase 1 LIVE, Fase 2 PLANNED |
| **2026-03-24** | `TERMINOLOGY_SANITIZATION_ANALYSIS.md` | EGOS-118: rename para "Repository Mesh" |
| **2026-03-30** | `MYCELIUM_TRUTH_REPORT.md` | **AUDIT CRÍTICO** — separação real vs aspiracional |
| **2026-04-01** | `SSOT.md` v1.0.0 | Consolida código real (~1600 LOC) |
| **2026-04-09** | Estado atual | **3 camadas LIVE**, 4 planejadas |

### Decisão Fundamental (MYCELIUM_TRUTH_REPORT.md):

**O Mycelium foi dividido em 3 camadas canônicas + 1 legado:**

```
┌─────────────────────────────────────────────────────────────┐
│  CAMADA 1 — Runtime Bus Local (LIVE)                        │
│  • agents/runtime/event-bus.ts (327 LOC)                   │
│  • In-memory, sync, TypeScript-native                      │
│  • JSONL audit trail                                       │
│  Status: ✅ IMPLEMENTADO                                    │
├─────────────────────────────────────────────────────────────┤
│  CAMADA 2 — Snapshot/Projeção (LIVE)                      │
│  • docs/SYSTEM_MAP.md                                      │
│  • docs/_current_handoffs/                                 │
│  • .windsurf/workflows/mycelium.md                         │
│  Status: ✅ DOCUMENTAÇÃO ATIVA                            │
├─────────────────────────────────────────────────────────────┤
│  CAMADA 3 — Reference Graph (LIVE)                          │
│  • packages/shared/src/mycelium/reference-graph.ts         │
│  • 27 nodes, 32 edges (seed estático)                      │
│  • 300 LOC — canonical schema                              │
│  Status: ✅ IMPLEMENTADO (Phase 1)                          │
├─────────────────────────────────────────────────────────────┤
│  CAMADA 4 — Distributed Bridge (PLANNED)                    │
│  • Redis Pub/Sub wrapper (337 LOC em redis-bridge.ts)      │
│  • Producer/consumer pair — NÃO VERIFICADO ativo           │
│  • NATS — NUNCA implementado (só em docs)                  │
│  Status: 🟡 PLANEJADO (Phase 2)                            │
├─────────────────────────────────────────────────────────────┤
│  CAMADA 5 — ZKP / Shadow Nodes (ASPIRACIONAL)               │
│  • Referenciado em NETWORK_PLAN.md Phase 3                 │
│  • Zero código: sem snarkjs, sem circom                    │
│  Status: 🔴 NÃO INICIADO                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Função ATUAL do Mycelium (não aspiracional)

### Implementado (Código Real):

#### A. Event Bus Local (`agents/runtime/event-bus.ts`)

```typescript
// Eventos tipados com topic namespacing
export interface MyceliumEvent<T = unknown> {
  id: string;
  topic: string;           // "security.finding", "qa.regression"
  source: string;
  correlationId: string;
  timestamp: string;
  payload: T;
}

// Features reais:
// • Wildcard subscriptions ("security.*", "*.critical")
// • JSONL audit trail para forensics
// • Sync-first (Redis-ready mas não ativo)
// • Conditional routing via topic matching
```

**Uso real:** Agents emitem eventos localmente, audit trail em disco.

#### B. Reference Graph (`packages/shared/src/mycelium/reference-graph.ts`)

```typescript
// Grafo de referência topológica (NÃO é event stream)
export interface ReferenceNode {
  id: string;
  type: ReferenceEntityType;  // 'workspace_root', 'repository', 'agent', etc.
  label: string;
  status: NodeStatus;         // 'active' | 'degraded' | 'offline' | 'planned'
  evidence: ReferenceEvidence[];  // 'code' | 'runtime' | 'log' | 'plan'
}

// Seed atual: 27 nodes, 32 edges (estático)
// Exemplo de nós reais:
// • workspace_root: "/home/enio/egos"
// • repository: "egos-lab"
// • agent: "ssot-auditor"
// • surface: "agents/runtime/runner.ts"
```

**Função:** Mapa do sistema — o que existe, como conecta, qual evidência.

#### C. Redis Bridge (`packages/shared/src/mycelium/redis-bridge.ts`)

```typescript
// 337 LOC — Redis Pub/Sub abstraction
// Status: Código existe, wiring NÃO confirmado ativo
// Decisão: Redis foi escolhido sobre NATS (zero custo infra adicional)
```

### NÃO Implementado (Documentação vs Realidade):

| Claim na Doc | Realidade | Arquivo de Verdade |
|--------------|-----------|-------------------|
| NATS transport | ❌ NUNCA codificado | Só existe em `docs/plans/` |
| ZKP Shadow Nodes | ❌ NÃO EXISTE | `status: 'planned'` nos tipos apenas |
| Distributed broker | ⚠️ Railway Worker health endpoint existe | Mas NÃO é Mycelium event broker |
| `node.ts` wrapper | ❌ NÃO ENCONTRADO | Referenciado em docs, não existe |
| `schema.ts` Zod | ❌ NÃO ENCONTRADO | Referenciado em docs, não existe |
| `test-poc.ts` | ❌ NÃO ENCONTRADO | Referenciado em docs, não existe |

---

## 4. Decisões Arquiteturais Críticas

### Decisão 1: NATS foi abandonado em favor de Redis

**Documentado em:** `NETWORK_PLAN.md` §2.1

> "Why Redis over NATS? We already run Redis on Railway for the worker queue.  
> Adding Pub/Sub to the same Redis instance = zero new infrastructure cost."

**Impacto:** Sua visão original de NATS para interconexão foi **adaptada** para Redis Pub/Sub (mais pragmático).

---

### Decisão 2: Separação Kernel vs Consumidor

**Documentado em:** `MYCELIUM_TRUTH_REPORT.md` §4

> "The kernel currently ships no `apps/` directory and no `agents/worker/` directory.  
> Any Mycelium dashboard, API, or worker claim must therefore be treated as either  
> a consumer-repo surface or stale documentation until runtime evidence proves otherwise."

**Significado:** Dashboards e APIs de snapshot moram em **superfícies consumidoras** (egos-lab/apps/egos-web), não no kernel `egos/`.

---

### Decisão 3: Neo4j NÃO é Mycelium

**Documentado em:** `MYCELIUM_TRUTH_REPORT.md` §2.2, `SSOT.md`

> "The `bracc-neo4j` Docker service running on Hetzner VPS (77M entities) belongs to `br-acc` —  
> a standalone Python OSINT platform. It is **correctly classified** in `ECOSYSTEM_CLASSIFICATION_REGISTRY.md`  
> and is **not part of Mycelium**."

**Erro detectado:** Comandos `.claude/commands/mycelium.md` e `vps.md` rotulavam `bracc-neo4j` como "Neo4j/Mycelium" — **corrigido** para "Neo4j/br-acc".

---

### Decisão 4: Terminologia em Transição (EGOS-118)

**Documentado em:** `TERMINOLOGY_SANITIZATION_ANALYSIS.md` §3, §5

| Fase | Prazo | Ação | Status |
|------|-------|------|--------|
| Phase 1 | 24h | Sacred Code → Governance Version | ✅ Completo |
| **Phase 2** | **48h** | **Mycelium → Repository Mesh** | ⚠️ **PENDENTE (EGOS-118)** |
| Phase 3 | 72h | disseminate → propagate | ⚠️ Pendente |
| Phase 4 | 1 week | Philosophy → BLUEPRINT-EGOS | ⚠️ Pendente |
| Phase 5 | 2 weeks | Tool standardization | ⚠️ Pendente |

**Racional:** "Mycelium" como metáfora biológica tem valor filosófico mas sobrecarga cognitiva técnica.

---

## 5. Evolução da Visão Original

### Sua Visão Inicial (conforme documentado):

> "Interconexão NATS entre todo nosso sistema"  
> — Visão arquitetural original

### Evolução para Realidade:

```
Visão Original          Decisões Intermediárias         Estado Atual
────────────────────────────────────────────────────────────────────────
NATS mesh          →    Redis Pub/Sub (custo zero)   →   Wrapper existe,
                                              wiring NÃO confirmado
                                                        
Cross-process      →    Kernel local only             →   Event bus: local
communication           Consumer repos: distributed      Reference graph: local
                                                         Redis bridge: planned
                                                          
ZKP + Shadow Nodes →    Aspiracional                   →   NÃO IMPLEMENTADO
(Phase 3)
                                                          
Neo4j como         →    Separar concerns               →   br-acc = OSINT
Mycelium store          Mycelium ≠ banco de dados      Intelink = produto
                                                          EGOS kernel = orquestração
```

---

## 6. O que NUNCA foi implementado (Gap Analysis)

Arquivos **referenciados em documentação** mas **inexistentes no código:**

| Arquivo Referenciado | Local da Referência | Status Real |
|----------------------|---------------------|-------------|
| `packages/shared/src/mycelium/node.ts` | `egos-lab/MYCELIUM_OVERVIEW.md` | ❌ NÃO EXISTE |
| `packages/shared/src/mycelium/schema.ts` | `egos-lab/MYCELIUM_OVERVIEW.md` | ❌ NÃO EXISTE |
| `scripts/mycelium/test-poc.ts` | `egos-lab/MYCELIUM_OVERVIEW.md` | ❌ NÃO EXISTE |
| `apps/egos-web/api/mycelium-stats.ts` | `REFERENCE_GRAPH_DESIGN.md` | ❌ NÃO EXISTE (kernel) |
| `apps/egos-web/src/lib/mycelium.ts` | `MYCELIUM_OVERVIEW.md` | ❌ NÃO EXISTE (kernel) |
| `apps/egos-web/src/components/MyceliumDashboard.tsx` | `MYCELIUM_NETWORK.md` | ❌ NÃO EXISTE (kernel) |

**Significado:** Documentação `egos-lab` continha **claims inflados** que não correspondiam ao kernel.

---

## 7. Recomendações Baseadas na Pesquisa

### Imediato (Hoje):

1. **Decisão sobre EGOS-118:** 
   - Executar rename "Mycelium" → "Repository Mesh" em docs técnicos?
   - **Trade-off:** Clareza técnica vs. custo de atualização mental

2. **Remover referências obsoletas:**
   - Limpar docs `egos-lab` que referenciam arquivos inexistentes
   - Corrigir comandos `.claude/commands/` que conflacionam Neo4j/br-acc com Mycelium

### Curto prazo (Semana):

3. **Validar Redis Bridge:**
   - Testar se `redis-bridge.ts` está efetivamente conectado
   - Se não: documentar como PLANNED (não LIVE)

4. **Completar Reference Graph:**
   - Expandir de 27 nodes/32 edges para refletir sistema real
   - Adicionar evidence tags para cada nó

### Médio prazo (Mês):

5. **Revisar ZKP/Shadow Nodes:**
   - Decisão GO/NO-GO: implementar ou remover do roadmap?
   - Se NO-GO: limpar de todos os docs e tipos

6. **Implementar distributed bridge (Phase 2):**
   - Se necessário para arquitetura distribuída real

---

## 📎 Referências Primárias

| Documento | Data | Propósito |
|-----------|------|-----------|
| `MYCELIUM_TRUTH_REPORT.md` | 2026-03-30 | **AUDIT** — separação real vs aspiracional |
| `SSOT.md` | 2026-04-01 | **CONSOLIDAÇÃO** — código real (~1600 LOC) |
| `TERMINOLOGY_SANITIZATION_ANALYSIS.md` | 2026-03-24 | **DECISÃO** — rename para "Repository Mesh" (EGOS-118) |
| `NETWORK_PLAN.md` | 2026-03-19 | **ROADMAP** — Fase 1 LIVE, Fase 2 PLANNED |
| `MYCELIUM_OVERVIEW.md` | 2026-03-08 | **VISÃO** — 4 camadas canônicas + legado |
| `REFERENCE_GRAPH_DESIGN.md` | 2026-03-07 | **DESIGN** — schema e rationale |

---

## 📊 Métricas da Pesquisa

| Métrica | Valor |
|---------|-------|
| Arquivos analisados | 93 |
| Matches "Mycelium/mycelium" | 1082 |
| Commits git analisados | 24 |
| Documentos principais | 6 |
| Linhas de código real | ~1600 |
| Decisões arquiteturais críticas | 4 |
| Tasks pendentes (EGOS-118+) | 5 |

---

Gerado por: Cascade (pesquisa aprofundada)  
Data: 09/04/2026 16:45 UTC-3  
Referências: 93 arquivos, git history completo, decisões arquivadas

---

> **"Sanitize the language, preserve the structure, separate the philosophy."**  
> — EGOS Terminology Sanitization Analysis, 2026-03-24
