# EGOS Inteligência — Reality Check & Canonical Topology

> **Date:** 2026-04-06  
> **Status:** DOCUMENTED BUT NOT PHYSICALLY MERGED  
> **SSOT:** This document + `docs/business/MONETIZATION_SSOT.md` §11

---

## 🎯 Realidade do Estado Físico

| Path | Estado | Conteúdo Real |
|------|--------|---------------|
| `/home/enio/egos-inteligencia/` | **ESQUELETO** | Apenas configs (.env, package.json), diretórios vazios |
| `/home/enio/br-acc/` | **PRODUÇÃO ATIVA** | Backend Python + Neo4j 77M+ nós, ETLs, APIs reais |
| `/home/enio/INTELINK/` | **ARQUIVO/DORMENTE** | Frontend legado, 128 dias sem commit |
| `/home/enio/egos-lab/apps/intelink/` | **LAB ATIVO** | Frontend mais recente, Next.js 16, funcional |

**Conclusão:** O merge documentado em `INTELINK_BRACC_MERGE.md` e `AGENTS.md` é **teórico/arquitetural**, não físico.

---

## 🏗️ Topologia Canônica Decidida

```
┌─────────────────────────────────────────────────────────────┐
│  EGOS Inteligência (produto comercial unificado)           │
│  ───────────────────────────────────────────────             │
│  • Interface: Next.js (portar de egos-lab/apps/intelink/)    │
│  • Dados: API Python + Neo4j (consumir de br-acc/)         │
│  • Deploy: VPS separado, domínio inteligencia.egos.ia.br   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  BR-ACC (data engine standalone)                             │
│  ─────────────────────────────                             │
│  • 77M+ entidades Neo4j @ Contabo VPS                      │
│  • 46 ETL pipelines Python                                 │
│  • APIs REST já funcionais                                 │
│  • NÃO será absorvido no kernel EGOS                       │
│  • SERÁ consumido via API por EGOS Inteligência            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Intelink Legado (ativo de UX/UI)                          │
│  ────────────────────────────────                          │
│  • Código fonte de referência para portar patterns           │
│  • NÃO é surface de venda independente                       │
│  • Portar componentes selecionados para EGOS Inteligência  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Decisões Arquiteturais

### 1. BR-ACC permanece standalone (HUM-001)
**Rationale:** 77M entidades OSINT não fazem sentido no Mycelium (27 nós do kernel). BR-ACC é produto independente funcionando bem.

### 2. EGOS Inteligência é o shell comercial
- Consome dados BR-ACC via API
- Porta UX sofisticada de Intelink (lab)
- Adota documentação legal completa de BR-ACC (ETHICS.md, LGPD.md, etc.)

### 3. Intelink (legado) é ativo de patterns
- Não vende-se separadamente
- Fonte de componentes UI, investigação cockpit, cross-references
- Portar seletivamente, não mergear completamente

---

## 🚦 Status por Componente

| Componente | Localização Física | Status | Ação Requerida |
|------------|-------------------|--------|----------------|
| Backend API | `br-acc/api/` | ✅ Funcional | Expor endpoint para EGOS Inteligência |
| Neo4j 77M+ | Contabo VPS | ✅ Produção | Manter standalone |
| ETLs 46 | `br-acc/etl/` | ⚠️ 70% stuck | Restart após deploy |
| Frontend v1 | `INTELINK/frontend/` | ❌ Arquivo | Referência apenas |
| Frontend v2 | `egos-lab/apps/intelink/` | ✅ Funcional | Portar para `egos-inteligencia/` |
| Legal docs | `br-acc/docs/legal/` | ✅ Completo | Copiar para `egos-inteligencia/docs/` |

---

## 🎯 Próximos Passos Físicos (NÃO DOCUMENTAIS)

### Opção A — Deploy rápido (recomendado para validação):
1. Copiar frontend de `egos-lab/apps/intelink/` para `egos-inteligencia/frontend/`
2. Configurar `.env` apontando para BR-ACC API em Contabo
3. Build local (`npm run build`)
4. Deploy em subdomínio de teste
5. Smoke test: busca → Neo4j → resultado

### Opção B — Merge completo (mais trabalho):
1. Migrar backend br-acc para `egos-inteligencia/api/`
2. Renomear pacotes `bracc` → `egos_inteligencia`
3. Criar Docker Compose unificado
4. Migrar ETLs
5. Deploy como stack única

**Recomendação:** Opção A primeiro — validar comercialmente antes de investir migração completa.

---

## 🔗 Referências

- `docs/EXECUTIVE_SUMMARY_DECISION_MATRIX.md` — HUM-001
- `docs/business/MONETIZATION_SSOT.md` — §11 (product partnership map)
- `egos-lab/docs/plans/INTELINK_BRACC_MERGE.md` — Inventário técnico (histórico)
- `/home/enio/br-acc/AGENTS.md` — BR-ACC data engine reality
- `/home/enio/br-acc/TASKS.md` — TASK-001 (CNPJ ETL stuck at 70%)

---

*Sacred Code: 000.111.369.963.1618*
