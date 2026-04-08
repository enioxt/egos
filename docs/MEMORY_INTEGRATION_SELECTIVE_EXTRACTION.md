# Memory Integration v2 — Selective Extraction Strategy

> **Version:** 1.0.0 | **Updated:** 2026-04-08 | **Status:** Planning
> **SSOT:** `TASKS.md` §Memory Integration v2

---

## Contexto

Três sistemas de memory/agent discovery emergiram em abril/2026:

| Sistema | Origem | Destaque | Status EGOS |
|---------|--------|----------|-------------|
| **CORAL** | MIT/Han Zheng | Multi-agent autonomous discovery, 50%+ breakthroughs from knowledge reuse | Não integrado |
| **MemPalace** | milla-jovovich | 96.6% R@5 LongMemEval, AAAK 30× compression | Não integrado |
| **Hindsight** | vectorize-io | 91.4% accuracy, biomimetic Retain/Recall/Reflect | EGOS-134 pending |

**Decisão arquitetural:** Não integrar frameworks completos. Extrair apenas os padrões e algoritmos que encaixam na arquitetura EGOS existente.

---

## Princípios de Extração Seletiva

1. **Reuse over Replace:** Manter Supabase persistence, não substituir por ChromaDB/PostgreSQL nativo dos sistemas externos
2. **Interface over Implementation:** Extrair APIs e contratos, não código completo
3. **Pattern over Framework:** Adotar algoritmos específicos, não arquiteturas completas
4. **Incremental over Big-Bang:** Cada extração entrega valor isolado, sem dependências bloqueantes

---

## O que Extrair de Cada Sistema

### MemPalace — Extrair

| Componente | Ação | Motivo |
|------------|------|--------|
| **AAAK compression** | ✅ Portar `aaak.py` → TypeScript | 30× compressão lossless única no mercado |
| **Palace structure** | ✅ Adaptar wings/rooms/halls | Organização hierárquica superior ao flat storage atual |
| **MCP tools** | ✅ Reduzir 19 → 6 essenciais | Interface com agents EGOS já existentes |
| **ChromaDB backend** | ❌ Manter Supabase | EGOS já usa Supabase, zero migração necessária |
| **Local-first offline** | ❌ Manter cloud | VPS já provisionado, não há ganho real com local-only |

### Hindsight — Extrair

| Componente | Ação | Motivo |
|------------|------|--------|
| **Retain/Recall/Reflect ops** | ✅ Portar lógica | Lifecycle de memory mais sofisticado que CRUD simples |
| **Biomimetic lifecycle** | ✅ Adaptar estados | `encoding → consolidating → retrievable` melhor que `created → updated` |
| **NPM SDK** | ❌ Não usar | Implementar interface própria, não dependência externa |
| **PostgreSQL native** | ❌ Manter Supabase | Compatibilidade com stack existente |
| **Vector embeddings** | ❌ Não adotar | ARR (full-text) + AAAK (compression) cobrem 90% dos casos |

### CORAL — Extrair

| Componente | Ação | Motivo |
|------------|------|--------|
| **Knowledge reuse algorithm** | ✅ Implementar | 50%+ breakthroughs vêm de reuso — não temos isso hoje |
| **Discovery prioritization** | ✅ Adaptar | Score `novelty × applicability × cost` para Gem Hunter |
| **Shared discovery store** | ✅ Criar tabela `gem_discoveries` | Já parcialmente planejado em CORAL-001 |
| **Framework CORAL completo** | ❌ Não integrar | Overhead de agent lifecycle, já temos runner.ts |
| **Evolutionary search** | ❌ Não adotar | Gem Hunter já tem pipeline eficiente, não precisa de evolução genética |

---

## Arquitetura Alvo

```
┌─────────────────────────────────────────────────────────────────┐
│                      Unified Memory Store v2                     │
│              (packages/shared/src/unified-memory.ts)           │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Supabase    │  │  Hindsight   │  │    MemPalace         │  │
│  │ Persistence  │  │   Lifecycle  │  │   AAAK Compression   │  │
│  │              │  │              │  │                      │  │
│  │ • tables     │  │ • retain()   │  │ • compress()         │  │
│  │ • RLS        │  │ • recall()   │  │ • decompress()       │  │
│  │ • policies   │  │ • reflect()  │  │ • 30× ratio          │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                    Palace Structure Adapter                    │
│              (packages/shared/src/palace-adapter.ts)           │
│                                                                  │
│  Wings (repos)      Rooms (domains)       Halls (types)         │
│  ├── egos           ├── guard-brasil      ├── decisions         │
│  ├── egos-lab       ├── hq                ├── patterns          │
│  ├── 852            ├── gem-hunter        ├── discoveries       │
│  ├── br-acc         ├── licitacoes        └── ...               │
│  └── ratio          └── ...                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     CORAL Knowledge Reuse                      │
│           (packages/shared/src/knowledge-reuse.ts)               │
│                                                                  │
│  ┌─────────────────┐    ┌──────────────────┐                   │
│  │ gem_discoveries │◄───┤ findRelevant()   │                   │
│  │   (Supabase)    │    │ score: novelty × │                   │
│  └─────────────────┘    │ applicability ×  │                   │
│                         │ cost             │                   │
│                         └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Mycelium Event Bus                          │
│            (packages/shared/src/event-bus.ts)                  │
│                                                                  │
│  Topics:                                                         │
│  • memory.retained                                             │
│  • knowledge.discovered                                        │
│  • knowledge.reused                                            │
│  • palace.room.entered                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Roadmap de Implementação

### Fase 1: Fundação (P1 — Semana 1-2)
- [ ] MEM-005: AAAK compression portado
- [ ] MEM-009: Hindsight operations implementadas
- [ ] CORAL-001: Tabela `gem_discoveries` criada

### Fase 2: Integração (P1 — Semana 3-4)
- [ ] MEM-006: Palace structure adapter
- [ ] MEM-010: Biomimetic lifecycle hooks
- [ ] CORAL-004: Knowledge reuse algorithm

### Fase 3: Unificação (P2 — Mês 2)
- [ ] MEM-011: Unified Memory Store v2
- [ ] MEM-007: MCP tools reduzidas
- [ ] CORAL-006: Shared knowledge event protocol

### Fase 4: Otimização (P2 — Mês 2-3)
- [ ] MEM-008: AAAK em conversation-memory.ts
- [ ] CORAL-005: Discovery prioritization no Gem Hunter
- [ ] Benchmark: Comparar antes/depois (storage, latency, accuracy)

---

## Métricas de Sucesso

| Métrica | Baseline (hoje) | Target (pós Fase 4) |
|---------|-----------------|---------------------|
| Memory storage | 100% (raw) | 30% (AAAK compressed) |
| Retrieval latency | ~200ms | ~50ms (indexed palace) |
| Cross-session accuracy | ~70% (resumos) | ~90% (AAAK verbatim) |
| API call reduction (Gem Hunter) | 0% | 30% (knowledge reuse) |
| Agent cycle time | 100% | 70% (prioritization) |

---

## Anti-Padrões Evitados

1. ❌ **Framework Invasion:** Não deixar CORAL/MemPalace/Hindsight tomarem conta do runtime
2. ❌ **Database Sprawl:** Não adicionar ChromaDB/PostgreSQL nativo — manter Supabase
3. ❌ **Big-Bang Migration:** Não substituir tudo de uma vez — cada componente é opcional
4. ❌ **External Dependency Lock:** Não depender de SDKs/npm packages que podem mudar

---

## Referências

- **MemPalace:** https://github.com/milla-jovovich/mempalace
- **Hindsight:** https://github.com/vectorize-io/hindsight
- **CORAL:** https://github.com/Human-Agent-Society/CORAL | arXiv:2604.01658
- **EGOS Memory (atual):** `packages/shared/src/memory-store.ts`
- **EGOS Event Bus:** `packages/shared/src/event-bus.ts`
- **EGOS Tasks:** `TASKS.md` §Memory Integration v2

---

## Notas de Decisão

**2026-04-08:** Decisão de NÃO integrar frameworks completos, extrair apenas padrões. Justificativa:
- EGOS já tem agent runtime maduro (runner.ts + event-bus.ts)
- Supabase já é production-ready, não precisamos de outro DB
- Cada sistema externo tem overlap parcial — nenhum cobre 100% das necessidades
- Abordagem seletiva permite mix-and-match otimizado

---

*Documento vivo — atualizar conforme implementação progride*
