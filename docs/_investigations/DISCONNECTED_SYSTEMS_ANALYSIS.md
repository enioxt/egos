# EGOS SISTEMAS DESCONECTADOS — Diagnóstico de Integração

> **Date:** 2026-04-06  
> **Analyst:** Cascade  
> **Status:** INVESTIGATION COMPLETE — decisões principais absorvidas nos docs fixos; questões arquiteturais remanescentes seguem abertas

<!-- llmrefs:start -->
## LLM Reference Signature

- **Role:** temporary investigation artifact for disconnected-system evidence
- **Summary:** preserves the evidence behind the disconnected-system analysis after BRACC, Self-Discovery, and Booking Agent product decisions were already taken
- **Type:** TEMPORÁRIO
- **Read next:**
  - `docs/EXECUTIVE_SUMMARY_DECISION_MATRIX.md` — decision state and remaining fronts
  - `docs/SSOT_REGISTRY.md` — BRACC boundary and ownership contract
  - `docs/DOCUMENTATION_ARCHITECTURE_MAP.md` — archival policy for temporary investigation docs
<!-- llmrefs:end -->

---

## 🔍 RESUMO EXECUTIVO

Após revisão completa do VPS, archive (v2-v5), e kernel atual, identifiquei **7 sistemas críticos desconectados** que deveriam estar integrados para o EGOS funcionar como ecossistema unificado.

---

## 🚨 SISTEMAS DESCONECTADOS (Por ordem de prioridade)

### 1. BRACC Neo4j ↔ EGOS Mycelium Reference Graph

**Status:** DESCONNECTED  
**Impacto:** ALTO — Duplicação de grafos, dados não fluem

**O que existe:**
- **BRACC Neo4j** (VPS): 77M entidades, OSINT platform Python (porta 7474/7687)
- **Mycelium Reference Graph** (EGOS kernel): 27 nodes, 32 edges, TypeScript in-memory

**Problema:**
- BRACC é standalone (br-acc repo), não é considerado parte do Mycelium
- Mycelium Reference Graph é estático, sem persistência
- Neo4j tem 77M entidades mas não alimenta o reference-graph.ts

**Decisão registrada (2026-04-06):**
- [x] **B)** Manter separado — BRACC é produto standalone (OSINT)
- [ ] **A)** Integrar BRACC Neo4j como backend persistido do Mycelium
- [ ] **C)** Criar sync periódico: Neo4j → Reference Graph (read-only)

**Próximo passo válido:** manter boundary explícito em SSOTs; avaliar adapter/API apenas se surgir caso de uso real.

---

### 2. Self-Discovery (v2) ↔ EGOS Kernel Moderno

**Status:** DESCONNECTED  
**Impacto:** ALTO — Sistema terapêutico abandonado no archive

**O que existe no v2:**
- `core/maieutic_engine/question_generator.py` — Gera perguntas socráticas
- `core/intelligence/pattern_detector.py` — Detecta padrões psicológicos
- API endpoints: `/api/v1/self/patterns/detect`, `/api/v1/self/maieutic/generate`
- Frontend: `/self-discovery` no websiteNOVO

**O que falta no kernel moderno:**
- Nenhum agente de psicologia/pattern detection
- Nenhum endpoint de maieutic engine
- Nenhum sistema de Self-Discovery

**Decisão registrada (2026-04-06):**
- [x] **A)** Reviver como produto standalone (tipo Eagle Eye, Gem Hunter)
- [ ] **B)** Portar padrões para Guard Brasil ou outro produto
- [ ] **C)** Integrar como feature do egos-web (platform)

**Próximo passo válido:** seguir com `VPS-002` e definição de ICP/rollout do produto.

---

### 3. Booking Agent (v2) ↔ EGOS Produtos

**Status:** DESCONNECTED  
**Impacto:** MÉDIO-ALTO — Produto potencial não aproveitado

**O que existe no v2:**
- Sistema completo de agendamento com IA
- FastAPI backend + Next.js frontend
- Multi-tenant (admin + provider dashboards)
- Pattern detection para clientes
- Notificações WhatsApp/email automáticas
- Target: Prestadores de serviço (salões, clínicas, etc.)

**Estado atual:**
- No archive v2, não portado
- Não está rodando no VPS
- Não integrado com EGOS Gateway ou OpenClaw

**Decisão registrada (2026-04-06):**
- [x] **C)** Arquivar — mercado saturado (Calendly, etc.)
- [ ] **A)** Reviver como produto standalone (SaaS de agendamento)
- [ ] **B)** Integrar como módulo do egos-web

**Próximo passo válido:** manter no archive v2; extrair apenas padrões reaproveitáveis se houver demanda futura.

---

### 4. AAR (Search Engine) ↔ codebase-memory-mcp

**Status:** PARCIALMENTE CONECTADO  
**Impacto:** MÉDIO — Duas buscas similares, sem unificação clara

**O que existe:**
- **AAR** (`packages/search-engine/`): In-memory full-text, sentence-level atoms
- **codebase-memory-mcp**: Graph search via Neo4j (BRACC)

**Problema:**
- AAR busca em átomos locais (rápido, sem persistência)
- codebase-memory-mcp busca em Neo4j (persistido, mas dados desconectados do EGOS)
- Sem roteamento claro: quando usar qual?

**Decisão necessária:**
- [ ] **A)** AAR como cache L1, Neo4j como L2 (hierarquia)
- [ ] **B)** Unificar em único sistema de busca
- [ ] **C)** Manter separado — AAR para kernel, Neo4j para OSINT

**Abordagem recomendada:** Claude Code (orquestrador) + human (arquitetura)

---

### 5. Gem Hunter API (VPS) ↔ EGOS Agent Registry

**Status:** PARCIALMENTE CONECTADO  
**Impacto:** MÉDIO — Agente rodando mas não integrado ao registry

**O que existe:**
- **Gem Hunter API** (VPS:204.168.217.125:3095): Container Docker ativo
- **agents/registry/agents.json**: Registry com 22 campos

**Problema:**
- Gem Hunter está no registry (`gem-hunter` e `gem-hunter-api`)
- Mas não está claro se reporta para Mycelium/Event Bus
- API roda isolada, sem integração com gateway

**Decisão necessária:**
- [ ] **A)** Promover para standalone (como Guard Brasil)
- [ ] **B)** Integrar completamente ao agent runtime
- [ ] **C)** Manter como external service via gateway

**Abordagem recomendada:** VPS agent (health check) + human (decisão produto)

---

### 6. MCP Hub (v2) ↔ MCP Moderno (.guarani/mcp-config.json)

**Status:** SUPERCEDED  
**Impacto:** BAIXO-MÉDIO — v2 obsoleto, mas padrões reusáveis

**O que era no v2:**
- Python MCP Hub (porta 8112)
- 9 tools: System Identity, ETHIK Score, Code Intelligence, etc.
- Protocolo EGOS_MCP_STANDARD v1.0

**O que existe agora:**
- `.guarani/mcp-config.json`: 9 servidores MCP configurados
- LLM Router, Git Advanced, File System Watch, Calendar, Sequential Thinking, EXA Research, Memory
- Guard Brasil MCP registrado em `.claude.json`

**Problema:**
- v2 MCP Hub tinha ferramentas específicas EGOS (ETHIK Score, Code Intelligence)
- MCP moderno usa servidores genéricos (Exa, Memory, etc.)
- Perdeu-se integração específica EGOS?

**Decisão necessária:**
- [ ] **A)** Portar tools EGOS-specific para MCP moderno (code_intel, ethik)
- [ ] **B)** Manter genérico — usar quando necessário
- [ ] **C)** Criar EGOS-specific MCP server (Guard Brasil style)

**Abordagem recomendada:** Claude Code (orquestrador) — implementar tools faltantes

---

### 7. Event Bus (agents/runtime) ↔ Redis Bridge (packages/shared)

**Status:** PARCIALMENTE IMPLEMENTADO  
**Impacto:** MÉDIO — Arquitetura planejada mas não ativa

**O que existe:**
- `agents/runtime/event-bus.ts`: In-memory, local, JSONL audit
- `packages/shared/src/mycelium/redis-bridge.ts`: Redis abstraction (337 linhas)

**Problema:**
- MYCELIUM_TRUTH_REPORT.md confirma: Redis Bridge não está ativa
- Event Bus é local apenas (intra-processo)
- Sem cross-process / cross-container eventos

**Decisão necessária:**
- [ ] **A)** Ativar Redis Bridge para eventos cross-container
- [ ] **B)** Manter local — cada container tem seu event bus
- [ ] **C)** Usar Supabase realtime como alternativa ao Redis

**Abordagem recomendada:** VPS agent (infra) + human (arquitetura)

---

## 📋 TASKS ORGANIZADAS POR RESPONSÁVEL

### 🤖 ORQUESTRADOR (Claude Code)

| ID | Task | Priority | System |
|----|------|----------|--------|
| **ORC-001** | Documentar boundary: BRACC Neo4j vs Mycelium Reference Graph | P0 | Knowledge Graph |
| **ORC-002** | Documentar arquitetura de Self-Discovery (produto standalone) | P0 | Self-Discovery |
| **ORC-003** | Implementar MCP tools EGOS-specific (code_intel, ethik) em mcp-config.json | P1 | MCP |
| **ORC-004** | Definir hierarquia AAR ↔ codebase-memory-mcp | P1 | Search |
| **ORC-005** | Confirmar este documento como artefato temporário em `_investigations/` | P1 | Docs |
| **ORC-006** | Atualizar ARCHIVE_GEMS_CATALOG.md com decisões de portar/arquivar | P0 | Archive |
| **ORC-007** | Revisar terminologia: remover "sacred" restante, padronizar técnico | P2 | Governance |

### 🖥️ VPS AGENTS (Containers/Scripts)

| ID | Task | Priority | Location |
|----|------|----------|----------|
| **VPS-001** | ~~Implementar sync script: BRACC Neo4j → Mycelium~~ | ❌ Cancelado | VPS:204.168.217.125 |
| **VPS-002** | Reviver Self-Discovery como container Docker standalone | P1 | VPS |
| **VPS-003** | ~~Reviver Booking Agent como container Docker~~ | ❌ Cancelado | VPS |
| **VPS-004** | Ativar Redis Bridge para cross-container events (se decidido) | P2 | VPS |
| **VPS-005** | Health check automático: Gem Hunter API status → Telegram | P2 | VPS cron |
| **VPS-006** | Log harvester: integrar com EGOS Mycelium Event Bus | P3 | VPS cron |

### 👤 HUMANOS (Decisões de Produto/Arquitetura)

| ID | Task | Priority | Owner |
|----|------|----------|-------|
| **HUM-001** | **DECISÃO CRÍTICA:** BRACC Neo4j — integrar ao EGOS ou manter standalone? | ✅ Done | Enio |
| **HUM-002** | **DECISÃO CRÍTICA:** Self-Discovery — produtizar como terapêutico ou arquivar? | ✅ Done | Enio |
| **HUM-003** | **DECISÃO CRÍTICA:** Booking Agent — SaaS de agendamento ou arquivar? | ✅ Done | Enio |
| **HUM-004** | Definir ICP (Ideal Customer Profile) para cada produto standalone | P1 | Enio |
| **HUM-005** | Priorizar roadmap: qual sistema desconectado integrar primeiro? | P1 | Enio |
| **HUM-006** | Revisar terminologia: "Talmudic" apropriado? Substituir por? | P2 | Enio |
| **HUM-007** | Decidir destino de 100+ scripts v2 (portar gems ou arquivar) | P2 | Enio |

---

## 🔗 MAPA DE INTEGRAÇÃO PROPOSTO

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EGOS ECOSYSTEM MAP                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────────┐         ┌──────────────┐         ┌──────────┐ │
│   │   KERNEL     │◄───────►│  MYCELIUM    │◄───────►│  AGENTS  │ │
│   │  (egos/)     │         │  Event Bus   │         │ (registry│ │
│   └──────────────┘         └──────┬───────┘         └──────────┘ │
│           │                         │                             │
│           │         ┌───────────────┘                             │
│           │         │                                             │
│           ▼         ▼                                             │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│   │    AAR       │  │ Reference    │  │   Redis      │            │
│   │Search Engine │  │ Graph (27)   │  │   Bridge     │            │
│   │  (L1 Cache)  │  │  (in-mem)    │  │ (planned)    │            │
│   └──────┬───────┘  └──────┬───────┘  └──────────────┘            │
│          │                  │                                      │
│          │                  │  ? SYNC ?                           │
│          │                  ▼                                      │
│          │         ┌──────────────┐                              │
│          │         │ BRACC Neo4j  │                              │
│          │         │   (77M)      │                              │
│          │         │  (VPS)       │                              │
│          │         └──────────────┘                              │
│          │                                                        │
│   ═══════╪══════════════════════════════════════════════════════  │
│          │                                                        │
│          ▼                                                        │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│   │ Gem Hunter   │  │Self-Discovery│  │Booking Agent│            │
│   │   (API)      │  │  (archive)   │  │  (archive)  │            │
│   │   :3095      │  │              │  │             │            │
│   └──────────────┘  └──────────────┘  └──────────────┘            │
│        │                  │                  │                   │
│        └──────────────────┴──────────────────┘                   │
│                           │                                      │
│                           ▼                                      │
│                   ┌──────────────┐                              │
│                   │ EGOS Gateway │                              │
│                   │   :3050      │                              │
│                   └──────────────┘                              │
│                           │                                      │
│                           ▼                                      │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│   │ Guard Brasil │  │    HQ        │  │  OpenClaw    │         │
│   │   :3099      │  │   :3060      │  │  :18789      │         │
│   └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 PRÓXIMOS PASSOS RECOMENDADOS

### Semana 1 (Imediato)
1. **Fechar rodada documental** — refletir decisões e paths corretos nos docs fixos
2. **VPS-002** — Planejar container Self-Discovery
3. **HUM-004** — Definir ICP detalhado de Self-Discovery

### Semana 2-3
4. **ORC-004** — Definir estratégia AAR ↔ codebase-memory-mcp
5. **ORC-003** — Portar tools EGOS para MCP moderno
6. **HUM-007** — Decidir destino dos scripts v2 restantes

### Mês 2
7. **VPS-002** — Implementar container Self-Discovery
8. **VPS-004** — Ativar Redis Bridge se a decisão arquitetural aprovar
9. **ORC-004** — Executar a estratégia de busca escolhida (AAR + Neo4j)

---

**Preparado por:** Cascade  
**Data:** 2026-04-06  
**Status:** DECISÕES PRINCIPAIS FECHADAS — manter como evidência temporária para integrações remanescentes
