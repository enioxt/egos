# EGOS DOCUMENTATION ARCHITECTURE — Mapa de Referências

> **Date:** 2026-04-06  
> **Analyst:** Cascade  
> **Purpose:** Definir documentos fixos vs temporários e criar cross-references

---

## 📚 DOCUMENTOS CRIADOS NESSA INVESTIGAÇÃO

### NOVOS (4 documentos criados hoje)

| # | Documento | Tipo | Status | Destino Final |
|---|-----------|------|--------|---------------|
| 1 | `EXECUTIVE_SUMMARY_DECISION_MATRIX.md` | **FIXO** | Ativo | Mantém como dashboard executivo |
| 2 | `DISCONNECTED_SYSTEMS_ANALYSIS.md` | **TEMPORÁRIO** | Ativo | Arquivar após integrações |
| 3 | `ARCHIVE_GEMS_CATALOG.md` | **FIXO** | Ativo | Mantém como catálogo do archive |
| 4 | `INFRASTRUCTURE_ARCHIVE_AUDIT.md` | **FIXO** | Ativo | Mantém como inventário VPS |

---

## 🗂️ DOCUMENTOS FIXOS (Permanentes)

### Tier 1: SSOT Mestre (Sempre referenciar estes)

```
📍 MASTER_INDEX.md                          ← COMEÇAR AQUI SEMPRE
    ├── É o SSOT universal do EGOS
    ├── Referencia TODOS os outros documentos
    └── Deve ser atualizado quando qualquer coisa muda

📍 AGENTS.md                                 ← Identidade do kernel
    ├── Propósito, arquitetura, comandos
    └── Referencia: MASTER_INDEX.md

📍 TASKS.md                                  ← Roadmap ativo
    ├── Todas as tasks em execução
    └── Referencia: MASTER_INDEX.md, DECISION_MATRIX

📍 EXECUTIVE_SUMMARY_DECISION_MATRIX.md      ← Dashboard decisões
    ├── Criado hoje
    ├── Resumo executivo + decisões pendentes
    └── Referencia: MASTER_INDEX.md
```

### Tier 2: Registros Permanentes (Referenciar quando relevante)

```
📍 ARCHIVE_GEMS_CATALOG.md                   ← Catálogo do archive
    ├── 20 gems catalogados do v2-v5
    ├── Status: Aguardando suas decisões PORT/STUDY/ARCHIVE
    └── Referencia: MASTER_INDEX.md (seção Archive)

📍 INFRASTRUCTURE_ARCHIVE_AUDIT.md           ← Inventário VPS
    ├── 10 containers, 3 cron jobs, scripts /opt/
    ├── Atualizar quando infra mudar
    └── Referencia: MASTER_INDEX.md (seção VPS)

📍 ECOSYSTEM_CLASSIFICATION_REGISTRY.md      ← Classificação repos
    ├── kernel, standalone, candidate, lab
    └── Referencia: MASTER_INDEX.md

📍 CAPABILITY_REGISTRY.md                     ← Capabilities 160+
    ├── Referencia técnica detalhada
    └── Referencia: MASTER_INDEX.md

📍 SSOT_REGISTRY.md                           ← Ownership contracts
    ├── Quem é responsável por cada domínio
    └── Referencia: MASTER_INDEX.md
```

### Tier 3: Análises Técnicas (Manter, atualizar periodicamente)

```
📍 MYCELIUM_TRUTH_REPORT.md                  ← Estado real do Mycelium
    ├── O que existe vs o que é aspiracional
    └── Referencia: MASTER_INDEX.md, SSOT.md

📍 SYSTEM_MAP.md                             ← Mapa de ativação
    ├── Fluxo de inicialização
    └── Referencia: MASTER_INDEX.md

📍 INCIDENT_RESPONSE_MCP.md                 ← Playbooks incidentes
    ├── Resposta a falhas
    └── Referencia: MASTER_INDEX.md
```

---

## 🗑️ DOCUMENTOS TEMPORÁRIOS (Arquivar após resolução)

### Investigação Atual (Arquivar após decisões)

```
📍 DISCONNECTED_SYSTEMS_ANALYSIS.md           ← TEMPORÁRIO
    ├── 7 sistemas desconectados identificados
    ├── Status: Aguardando HUM-001, HUM-002, HUM-003
    └── ⚠️ ARQUIVAR quando:
        - Decisões tomadas (HUM-001, 002, 003)
        - Integrações implementadas
        - Ou: movido para `docs/_archived_handoffs/`

📍 *_current_handoffs/*.md                   ← TEMPORÁRIO
    ├── Handoffs de sessão
    └── ⚠️ Arquivar quando sessão completada

📍 *REPORT_*.md temporários                   ← TEMPORÁRIO
    ├── Relatórios de análise pontuais
    └── ⚠️ Arquivar quando ações completadas
```

### Arquivados (Já movidos para `_archived_handoffs/`)

```
📁 _archived_handoffs/
    ├── handoff_2026-03-22.md
    ├── handoff_2026-03-25.md
    └── ... (24 itens)
    
    ⚠️ Estes são históricos, referenciar apenas se necessário
```

---

## 🔗 CROSS-REFERENCES — COMO NAVEGAR

### Se você é IA e precisa entender o sistema:

```
FLUXO DE LEITURA:

1º  MASTER_INDEX.md              → Scope geral, "o que temos"
    ↓
2º  EXECUTIVE_SUMMARY_...        → Decisões pendentes, status atual
    ↓
3º  [Documento específico]       → Detalhe técnico
    
    - Infraestrutura → INFRASTRUCTURE_ARCHIVE_AUDIT.md
    - Archive v2-v5  → ARCHIVE_GEMS_CATALOG.md
    - Sistemas desc. → DISCONNECTED_SYSTEMS_ANALYSIS.md
    - Tasks ativas   → TASKS.md
```

### Se você é humano e precisa decidir:

```
FLUXO DE DECISÃO:

1º  EXECUTIVE_SUMMARY_DECISION_MATRIX.md    → Veja decisões pendentes
    ↓
2º  DISCONNECTED_SYSTEMS_ANALYSIS.md         → Entenda impacto de cada uma
    ↓
3º  ARCHIVE_GEMS_CATALOG.md                → Veja o que pode ser portado
    ↓
4º  Decida → Atualize EXECUTIVE_SUMMARY... com decisão
    ↓
5º  Task implementada → Arquive DISCONNECTED_SYSTEMS quando integrado
```

---

## 📋 LLM REFERENCES (Para IAs lerem)

### Template para novos documentos:

```markdown
<!-- llmrefs:start -->

## LLM Reference Signature

- **Role:** [purpose of this document]
- **Summary:** [one-line description]
- **Type:** [FIXO | TEMPORÁRIO]
- **Read next:**
  - `MASTER_INDEX.md` — scope everything
  - `EXECUTIVE_SUMMARY_DECISION_MATRIX.md` — current decisions
  - [other specific docs]
- **Archive when:** [conditions for temporary docs]

<!-- llmrefs:end -->
```

### Documentos já com LLM References:

✅ `MASTER_INDEX.md` — Tem LLM refs  
✅ `EXECUTIVE_SUMMARY_DECISION_MATRIX.md` — Tem LLM refs  
✅ `MYCELIUM_TRUTH_REPORT.md` — Tem LLM refs  
✅ `ECOSYSTEM_CLASSIFICATION_REGISTRY.md` — Tem LLM refs  
✅ `SSOT_REGISTRY.md` — Tem LLM refs  

### Documentos que PRECISAM de LLM References:

🔲 `ARCHIVE_GEMS_CATALOG.md` — Adicionar refs  
🔲 `DISCONNECTED_SYSTEMS_ANALYSIS.md` — Adicionar refs  
🔲 `INFRASTRUCTURE_ARCHIVE_AUDIT.md` — Adicionar refs  

---

## 🎯 ESTRATÉGIA DE MANUTENÇÃO

### Documentos Fixos (Manter atualizados)

| Documento | Quando atualizar | Responsável |
|-----------|-----------------|-------------|
| `MASTER_INDEX.md` | Sempre que estrutura muda | Claude Code / drift-sentinel |
| `EXECUTIVE_SUMMARY_...` | Quando decisões tomadas | Claude Code / human |
| `ARCHIVE_GEMS_CATALOG` | Quando decisões de gems | Human + Claude Code |
| `INFRASTRUCTURE_...` | Quando VPS muda | VPS agent / watchdog |
| `TASKS.md` | Semanalmente | Human + Claude Code |

### Documentos Temporários (Arquivar quando)

| Documento | Condição de arquivamento | Prazo |
|-----------|-------------------------|-------|
| `DISCONNECTED_SYSTEMS_...` | Após HUM-001, 002, 003 decididos | 2-4 semanas |
| `*_current_handoffs/*.md` | Após sessão completada | 1 semana |
| `DISCONNECTED_SYSTEMS_...` | Integrações implementadas | 1 mês |

---

## 📁 ESTRUTURA DE DIRETÓRIOS SUGERIDA

```
docs/
├── MASTER_INDEX.md                          ← [FIXO] Entrada principal
├── EXECUTIVE_SUMMARY_DECISION_MATRIX.md     ← [FIXO] Dashboard decisões
├── ARCHIVE_GEMS_CATALOG.md                  ← [FIXO] Catálogo archive
├── INFRASTRUCTURE_ARCHIVE_AUDIT.md          ← [FIXO] Inventário VPS
│
├── _archived_handoffs/                      ← [ARQUIVO] Histórico
│   └── (sessões antigas)
│
├── _current_handoffs/                         ← [TEMP] Handoffs ativos
│   └── (mover para _archived quando completado)
│
├── _investigations/                         ← [TEMP] Análises pontuais
│   └── DISCONNECTED_SYSTEMS_ANALYSIS.md      ← Mover aqui ou arquivar
│
├── SSOT_REGISTRY.md                           ← [FIXO]
├── CAPABILITY_REGISTRY.md                     ← [FIXO]
├── ECOSYSTEM_CLASSIFICATION_REGISTRY.md       ← [FIXO]
├── MYCELIUM_TRUTH_REPORT.md                   ← [FIXO]
├── SYSTEM_MAP.md                              ← [FIXO]
├── INCIDENT_RESPONSE_MCP.md                 ← [FIXO]
│
└── [outros docs fixos existentes...]
```

---

## ✅ CHECKLIST DE CONSOLIDAÇÃO

### Hoje (Já feito)
- [x] Criar EXECUTIVE_SUMMARY_DECISION_MATRIX.md
- [x] Criar DISCONNECTED_SYSTEMS_ANALYSIS.md
- [x] Criar ARCHIVE_GEMS_CATALOG.md
- [x] Criar INFRASTRUCTURE_ARCHIVE_AUDIT.md
- [x] Criar este mapa de documentos

### Próximo passo (Sua decisão)
- [ ] Revisar este mapeamento
- [ ] Decidir HUM-001 (BRACC Neo4j)
- [ ] Decidir HUM-002 (Self-Discovery)
- [ ] Decidir HUM-003 (Booking Agent)

### Após decisões
- [ ] Mover DISCONNECTED_SYSTEMS_ANALYSIS.md para `_investigations/` ou arquivar
- [ ] Atualizar EXECUTIVE_SUMMARY com decisões tomadas
- [ ] Atualizar MASTER_INDEX.md com novos status
- [ ] Criar/executar tasks de implementação

---

**Preparado por:** Cascade  
**Data:** 2026-04-06  
**Status:** Mapa criado — Aguardando decisões para consolidar
