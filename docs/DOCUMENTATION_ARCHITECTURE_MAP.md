# EGOS DOCUMENTATION ARCHITECTURE — Mapa de Referências

> **Date:** 2026-04-06  
> **Analyst:** Cascade  
> **Purpose:** Definir documentos fixos vs temporários e criar cross-references  
> **Status:** Consolidação documental em andamento — mapa já usável como guia canônico

<!-- llmrefs:start -->
## LLM Reference Signature

- **Role:** documentation navigation map for the kernel documentation sweep
- **Summary:** separates canonical docs, durable references, and temporary investigation artifacts, with the read order that minimizes drift
- **Type:** FIXO
- **Read next:**
  - `.guarani/RULES_INDEX.md` — governance canon
  - `docs/MASTER_INDEX.md` — ecosystem inventory
  - `docs/SSOT_REGISTRY.md` — ownership and freshness contract
<!-- llmrefs:end -->

---

## 📚 DOCUMENTOS CRIADOS NESSA INVESTIGAÇÃO

### NOVOS (4 documentos criados hoje)

| # | Documento | Tipo | Status | Destino Final |
|---|-----------|------|--------|---------------|
| 1 | `EXECUTIVE_SUMMARY_DECISION_MATRIX.md` | **FIXO** | Ativo | Mantém como dashboard executivo |
| 2 | `docs/_investigations/DISCONNECTED_SYSTEMS_ANALYSIS.md` | **TEMPORÁRIO** | Ativo | Arquivar após integrações |
| 3 | `ARCHIVE_GEMS_CATALOG.md` | **FIXO** | Ativo | Mantém como catálogo do archive |
| 4 | `INFRASTRUCTURE_ARCHIVE_AUDIT.md` | **FIXO** | Ativo | Mantém como inventário VPS |

---

## 🗂️ DOCUMENTOS FIXOS (Permanentes)

### Tier 1: SSOT Mestre (Sempre referenciar estes)

```
📍 .guarani/RULES_INDEX.md                  ← ENTRADA CANÔNICA DE GOVERNANÇA
    ├── Define onde procurar regras primeiro
    └── Referencia: AGENTS.md, SSOT_REGISTRY.md, SYSTEM_MAP.md

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
    ├── Resumo executivo + decisões confirmadas + pendências restantes
    └── Referencia: MASTER_INDEX.md
```

### Tier 2: Registros Permanentes (Referenciar quando relevante)

```
📍 ARCHIVE_GEMS_CATALOG.md                   ← Catálogo do archive
    ├── 20 gems catalogados do v2-v5
    ├── Status: decisões parciais já registradas; restante segue em avaliação
    └── Referencia: MASTER_INDEX.md (seção Archive)

📍 INFRASTRUCTURE_ARCHIVE_AUDIT.md           ← Inventário VPS
    ├── Runtime surfaces, jobs recorrentes e boundaries operacionais
    ├── Atualizar quando runtime topology ou ownership mudar
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
📍 docs/_investigations/DISCONNECTED_SYSTEMS_ANALYSIS.md  ← TEMPORÁRIO
    ├── 7 sistemas desconectados identificados
    ├── Status: decisões principais já tomadas; manter como evidência de investigação
    └── ⚠️ ARQUIVAR quando:
        - Boundaries e decisões estiverem absorvidos pelos SSOTs fixos
        - Integrações/containers pendentes forem implementados ou cancelados
        - Ou: virar apenas referência histórica

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

1º  .guarani/RULES_INDEX.md      → Governança canônica
    ↓
2º  MASTER_INDEX.md              → Scope geral, "o que temos"
    ↓
3º  DOCUMENTATION_ARCHITECTURE_MAP.md → Onde cada doc vive e como envelhece
    ↓
4º  EXECUTIVE_SUMMARY_...        → Decisões confirmadas e pendências reais
    ↓
5º  [Documento específico]       → Detalhe técnico
    
    - Infraestrutura → INFRASTRUCTURE_ARCHIVE_AUDIT.md
    - Archive v2-v5  → ARCHIVE_GEMS_CATALOG.md
    - Sistemas desc. → docs/_investigations/DISCONNECTED_SYSTEMS_ANALYSIS.md
    - Tasks ativas   → TASKS.md
```

### Se você é humano e precisa decidir:

```
FLUXO DE DECISÃO:

1º  EXECUTIVE_SUMMARY_DECISION_MATRIX.md    → Veja decisões tomadas e pendências reais
    ↓
2º  docs/_investigations/DISCONNECTED_SYSTEMS_ANALYSIS.md → Entenda impacto e evidência
    ↓
3º  ARCHIVE_GEMS_CATALOG.md                → Veja o que pode ser portado
    ↓
4º  Decida → Atualize EXECUTIVE_SUMMARY, MASTER_INDEX e SSOTs
    ↓
5º  Task implementada → Arquive o material temporário quando o fixo absorver o contexto
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
✅ `INFRASTRUCTURE_ARCHIVE_AUDIT.md` — Tem LLM refs  
✅ `docs/_investigations/DISCONNECTED_SYSTEMS_ANALYSIS.md` — Tem LLM refs  
✅ `INVESTIGATION_FINAL_SUMMARY.md` — Tem LLM refs  

### Documentos que PRECISAM de LLM References:

Nenhum dos documentos principais desta rodada permanece sem `llmrefs`.

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
| `DISCONNECTED_SYSTEMS_...` | Após boundaries/decisões refletidos nos docs fixos e tarefas estabilizadas | 2-4 semanas |
| `*_current_handoffs/*.md` | Após sessão completada | 1 semana |
| `DISCONNECTED_SYSTEMS_...` | Integrações implementadas ou canceladas | 1 mês |

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
- [ ] Sincronizar os últimos docs fixos que ainda carregam status antigo
- [ ] Adicionar LLM refs aos temporários que ainda faltam
- [ ] Preparar `/disseminate` e `/end`

### Após consolidação
- [ ] Arquivar ou resumir investigações temporárias absorvidas pelos docs fixos
- [ ] Atualizar EXECUTIVE_SUMMARY com próximos passos finais
- [ ] Atualizar MASTER_INDEX.md com novos status, se necessário
- [ ] Criar/executar tasks de implementação quando a fase documental encerrar

---

**Preparado por:** Cascade  
**Data:** 2026-04-06  
**Status:** Mapa consolidado — pronto para orientar a rodada anti-drift
