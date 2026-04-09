# Repository Mesh (Mycelium): Ecossistema EGOS

> **Data:** 2026-04-09 | **Versão:** 1.1.0 | **EGOS-118** — Nome técnico: Repository Mesh
> **Status:** Visão canônica consolidada
> **Metáfora:** "O Sistema Radicular Fúngico". Assim como o micélio conecta florestas há bilhões de anos, transportando nutrientes e sinais de alerta, o **Repository Mesh** (codename: Mycelium) conecta superfícies, eventos e referências do ecossistema EGOS.
> 
> **Nota sobre nomenclatura:** "Repository Mesh" é o nome técnico padrão (EGOS-118). "Mycelium" permanece como codename reconhecido por voz para compatibilidade com comandos históricos.

<!-- llmrefs:start -->

## LLM Reference Signature

- **Role:** canonical Repository Mesh layer map
- **Summary:** Separates runtime bus, snapshot, reference graph, and legacy Repository Mesh (Mycelium) meanings.
- **Read next:**
  - `packages/shared/src/mycelium/reference-graph.ts` — **implementation** — Phase 1 canonical schema + kernel seed graph (27 nodes, 32 edges)
  - `docs/concepts/mycelium/REFERENCE_GRAPH_DESIGN.md` — **topology** — records the design rationale and relation vocabulary
  - `docs/concepts/mycelium/NETWORK_PLAN.md` — **roadmap** — tracks planned Mycelium expansion and integration boundaries
  - `.windsurf/workflows/mycelium.md` — **workflow** — defines the sync loop and layer checks for Mycelium work

<!-- llmrefs:end -->

## 1. Significado Canônico Atual

Hoje, **Repository Mesh** (codename: Mycelium) é um nome técnico padrão para **três camadas canônicas** e **um histórico legado**. O problema não é o nome em si, mas misturar essas camadas como se fossem a mesma coisa.

> **EGOS-118 Compliance:** Este documento usa "Repository Mesh" como termo técnico primário. O termo "Mycelium" é preservado para compatibilidade com comandos de voz e referências históricas.

### 1.1. Camada 1 — Runtime Bus Local

Arquivos canônicos:

- `agents/runtime/event-bus.ts`
- `docs/SYSTEM_MAP.md`
- `.windsurf/workflows/mycelium.md`

Esta camada cobre a movimentação de eventos.

- **`event-bus.ts`** = barramento local factual do kernel.
- **Verdade atual:** o barramento local existe e funciona; módulos Mycelium dedicados fora do event bus **não estão implementados neste repo**.

### 1.2. Camada 2 — Snapshot e Projeção de Topologia

Arquivos canônicos:

- `docs/SYSTEM_MAP.md`
- `docs/_current_handoffs/`
- `.windsurf/workflows/mycelium.md`

Esta camada cobre a leitura pública do estado do Mycelium.

- **Verdade atual:** no kernel, esta camada existe como documentação, handoff e workflow de verificação; dashboards e APIs de snapshot pertencem a superfícies consumidoras como `egos-lab`, não a este repo.

### 1.3. Camada 3 — Reference Graph / Reporting Mesh

Arquivos canônicos:

- `docs/concepts/mycelium/REFERENCE_GRAPH_DESIGN.md`
- `docs/concepts/mycelium/NETWORK_PLAN.md`
- `.windsurf/workflows/mycelium.md`

Esta camada cobre o mapa do sistema.

- **Event bus** = o que aconteceu.
- **Reference graph** = o que existe, como se conecta e com qual evidência.
- **Verdade atual:** o desenho e a linguagem do grafo existem no kernel como SSOT documental; a implementação concreta do grafo ainda é **parcial/planejada** neste repo.

### 1.4. Camada Legada — Arquivos Históricos com o Mesmo Nome

Encontramos usos históricos de `Mycelium` fora do SSOT atual, especialmente em:

- `egos-archive/v3/EGOSv3CLEAN/docs/MYCELIUM.MD`
- `egos-archive/v5/EGOSv5/docs/_archive/architecture/MYCELIUM_ARCHITECTURE.md`
- `br-acc/docs/analysis/MYCELIUM_AUDIT_TRAIL_2026-03.md`

Esses materiais são úteis como arqueologia, mas **não são SSOT do Mycelium atual do kernel `egos`**. Alguns deles usam o nome para significados bem diferentes, como harness sintético de personas ou trilha de auditoria/proveniência.

---

## 2. Verdade Operacional Atual

O que está de fato implementado hoje:

- **Event bus local** em `agents/runtime/event-bus.ts`
- **System map local** em `docs/SYSTEM_MAP.md`
- **Workflow de realidade** em `.windsurf/workflows/mycelium.md`
- **Design docs canônicos** em `docs/concepts/mycelium/`

O que continua planejado:

- **Bridge distribuída validada** entre producers/consumers reais
- **Snapshot/dashboard vivo** em superfícies consumidoras
- **Implementação concreta do reference graph** no kernel ou em pacote compartilhado
- **Shadow Nodes / ZKP** com pipeline de prova e verificação

---

## 3. Fronteiras de Nomenclatura

Use estes nomes para não misturar camadas (EGOS-118 padrão):

| Termo Técnico (Documentação) | Codename (Voz) | Função |
|------------------------------|----------------|--------|
| **RepositoryMesh** | Mycelium | Sistema completo |
| **MeshBus** | MyceliumBus | Runtime local do orquestrador |
| **MeshNode** | MyceliumNode | Wrapper Redis Pub/Sub / bridge PoC |
| **Mesh Snapshot** | Mycelium Snapshot | Contrato da API + dashboard |
| **Mesh Graph** | Reference Graph | Grafo de referências cross-repo |

> **Regra:** Use termos técnicos (Repository Mesh, MeshBus) em documentação e código. Use codenames (Mycelium) apenas para comandos de voz e referências informais.
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
- `docs/concepts/mycelium/NETWORK_PLAN.md`
- `.windsurf/workflows/mycelium.md`
