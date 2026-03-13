# 🍄 Mycelium Network: Ecossistema EGOS

> **Data:** 08/03/2026
> **Status:** Visão canônica consolidada
> **Metáfora:** "O Sistema Radicular Fúngico". Assim como o micélio conecta florestas há bilhões de anos, transportando nutrientes e sinais de alerta, o Mycelium conecta superfícies, eventos e referências do ecossistema EGOS.

<!-- llmrefs:start -->

## LLM Reference Signature

- **Role:** canonical Mycelium layer map
- **Summary:** Separates runtime bus, snapshot, reference graph, and legacy Mycelium meanings.
- **Read next:**
  - `packages/shared/src/mycelium/reference-graph.ts` — **implementation** — contains the canonical graph seed for the reference layer
  - `docs/research/MYCELIUM_REFERENCE_GRAPH_DESIGN_2026-03-07.md` — **topology** — records the design rationale and relation vocabulary
  - `.windsurf/workflows/mycelium.md` — **workflow** — defines the sync loop and layer checks for Mycelium work

<!-- llmrefs:end -->

## 1. Significado Canônico Atual

Hoje, **Mycelium** é um nome guarda-chuva para **três camadas canônicas** e **um histórico legado**. O problema não é o nome em si, mas misturar essas camadas como se fossem a mesma coisa.

### 1.1. Camada 1 — Runtime Bus Local

Arquivos canônicos:

- `agents/runtime/event-bus.ts`
- `packages/shared/src/mycelium/schema.ts`
- `packages/shared/src/mycelium/node.ts`
- `scripts/mycelium/test-poc.ts`

Esta camada cobre a movimentação de eventos.

- **`MyceliumBus`** = barramento local, em memória, síncrono, com trilha JSONL.
- **`MyceliumNode`** = wrapper Redis Pub/Sub para bridge distribuída/PoC.
- **Verdade atual:** o barramento local existe e funciona; a bridge distribuída existe como abstração e prova de conceito, mas **não há producer/consumer distribuído confirmado em produção**.

### 1.2. Camada 2 — Snapshot e Projeção de Topologia

Arquivos canônicos:

- `apps/egos-web/src/lib/mycelium.ts`
- `apps/egos-web/api/mycelium-stats.ts`
- `apps/egos-web/src/components/MyceliumDashboard.tsx`

Esta camada cobre a leitura pública do estado do Mycelium.

- **`DECLARED_MYCELIUM_SURFACES`** = superfícies declaradas e seus tipos de evidência.
- **`/api/mycelium-stats`** = snapshot honesto baseado em código, worker health e log local.
- **`MyceliumDashboard`** = UI que renderiza esse snapshot.
- **Verdade atual:** existe **topologia declarada com evidência**, não uma malha distribuída live em tempo real.

### 1.3. Camada 3 — Reference Graph / Reporting Mesh

Arquivos canônicos:

- `packages/shared/src/mycelium/reference-graph.ts`
- `docs/research/MYCELIUM_REFERENCE_GRAPH_DESIGN_2026-03-07.md`

Esta camada cobre o mapa do sistema.

- **Event bus** = o que aconteceu.
- **Reference graph** = o que existe, como se conecta e com qual evidência.
- **Verdade atual:** o grafo de referência já existe como estrutura canônica inicial e alimenta a narrativa de reporting, mas não substitui o barramento de eventos.

### 1.4. Camada Legada — Arquivos Históricos com o Mesmo Nome

Encontramos usos históricos de `Mycelium` fora do SSOT atual, especialmente em:

- `egos-archive/v3/EGOSv3CLEAN/docs/MYCELIUM.MD`
- `egos-archive/v5/EGOSv5/docs/_archive/architecture/MYCELIUM_ARCHITECTURE.md`
- `br-acc/docs/analysis/MYCELIUM_AUDIT_TRAIL_2026-03.md`

Esses materiais são úteis como arqueologia, mas **não são SSOT do Mycelium atual do egos-lab**. Alguns deles usam o nome para significados bem diferentes, como harness sintético de personas ou trilha de auditoria/proveniência.

---

## 2. Verdade Operacional Atual

O que está de fato implementado hoje:

- **Event log local** em `agents/.logs/events.jsonl`
- **Worker health/metrics** consultados pelo snapshot público
- **Dashboard** atualizado por polling do snapshot
- **Reference graph** inicial para reporting e topologia

O que continua planejado:

- **Bridge distribuída validada** entre producers/consumers reais
- **Stream de eventos em tempo real** para o dashboard
- **Shadow Nodes / ZKP** com pipeline de prova e verificação

---

## 3. Fronteiras de Nomenclatura

Use estes nomes para não misturar camadas:

- **MyceliumBus** = runtime local do orquestrador
- **MyceliumNode** = wrapper Redis Pub/Sub / bridge PoC
- **Mycelium Snapshot** = contrato da API + dashboard
- **Mycelium Reference Graph** = mapa canônico de topologia, relações e evidência
- **Mycelium Network** = termo guarda-chuva para o conjunto acima

---

## 4. Próximo Passo Canônico

Toda nova mudança em Mycelium deve declarar primeiro **qual camada está sendo alterada**:

- runtime local
- bridge distribuída
- snapshot/dashboard
- reference graph

Se uma mudança tocar mais de uma camada, ela deve atualizar pelo menos:

- este overview
- `docs/plans/tech/MYCELIUM_NETWORK.md`
- `.windsurf/workflows/mycelium.md`
