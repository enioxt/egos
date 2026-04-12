# KBS — Client Dashboard Template (Notion)

> **Version:** 1.0.0 | **Data:** 2026-04-12
> **KBS-039 SSOT:** Este arquivo documenta a estrutura do dashboard Notion por cliente.
> **Setup time:** ~10 minutos por cliente (duplicate + preencher variáveis).
> **Notion root:** Criar uma página por cliente em `KBS / Clientes / [Nome do Cliente]`.

---

## Estrutura da Página Raiz: `[Cliente] — Knowledge Base`

```
📁 [Cliente] — Knowledge Base
  ├── 📊 Visão Geral (database view)
  ├── 🔍 Perguntar à KB (chat interface / link)
  ├── 🗄️ Entidades (database)
  ├── 📄 Documentos Indexados (database)
  ├── 📈 Relatório Semanal de Inteligência (recurring page)
  ├── 🔒 Compliance LGPD (Guard Brasil status)
  └── ⚙️  Configuração (kb config)
```

---

## Sub-página 1: Visão Geral

**Layout:** Full-width. Blocos callout + gallery view.

### Bloco: Métricas Rápidas (4 callouts em linha)
```
📄 Documentos indexados    🧩 Entidades extraídas    🔗 Relacionamentos    🔍 Queries últimos 7d
     [N]                        [N]                       [N]                     [N]
```

### Bloco: Saúde da KB (tabela simples)
| Indicador | Status | Última verificação |
|-----------|--------|--------------------|
| Documentos sem lint | 🟢 0 | [data] |
| Entidades sem fonte | 🟡 [N] | [data] |
| Documentos desatualizados (>30d) | 🔴 [N] | [data] |
| PII detectado não revisado | 🟢 0 | [data] |
| Guard Brasil auditoria | 🟢 OK | [data] |

### Bloco: Últimas Atualizações
- Lista das últimas 5 páginas indexadas (título + data + categoria)

---

## Sub-página 2: Perguntar à KB

**Layout:** Simples, centrado. Um link + instruções.

```
🔍 Acesse: [URL do chatbot ou MCP] 

Como perguntar bem:
→ "Quais documentos falam sobre [tema]?"
→ "Liste todos os [tipo de entidade] relacionados a [nome/caso]"
→ "Resumo do caso [número]"
→ "Qual o histórico do suspeito [nome]?"

Última atualização da base: [data]
Documentos ativos: [N]
Modelo: Claude Haiku (rápido) / Claude Sonnet (análise profunda)
```

---

## Sub-página 3: Entidades (Notion Database)

**Tipo:** Full database (table view default + gallery view opcional).

### Propriedades da Database

| Coluna | Tipo Notion | Valores |
|--------|-------------|---------|
| Nome | Title | — |
| Tipo | Select | (varia por setor — ver schema) |
| Status | Select | ativo / inativo / suspeito / arquivado |
| Importância | Select | alta / média / baixa |
| Casos Relacionados | Relation → Documentos | — |
| Última atualização | Date | — |
| Fonte | Text | arquivo de origem |
| PII | Checkbox | — |
| Notas | Text | campo livre para investigador |

### Views pré-configuradas
1. **Por Tipo** — Group by: Tipo
2. **Alta Importância** — Filter: Importância = alta
3. **Recentes** — Sort: Última atualização DESC, Limit 20
4. **Com PII** — Filter: PII = ✓

---

## Sub-página 4: Documentos Indexados (Notion Database)

**Tipo:** Full database.

### Propriedades

| Coluna | Tipo Notion | Valores |
|--------|-------------|---------|
| Título | Title | — |
| Categoria | Select | (por setor) |
| Formato | Select | pdf / docx / md / xlsx / json |
| Status | Select | indexado / pendente / erro / desatualizado |
| Qualidade | Number | 0-100 (score do kb-lint) |
| PII Detectado | Checkbox | — |
| Data Indexação | Date | — |
| Tamanho | Number | chars |
| Slug | Text | identificador único |
| Tags | Multi-select | — |

### Views
1. **Por Categoria** — Group by: Categoria
2. **Problemas** — Filter: Status ≠ indexado OR Qualidade < 60
3. **Recentes** — Sort: Data Indexação DESC, Limit 30

---

## Sub-página 5: Relatório Semanal de Inteligência

**Formato:** Template de página repetível (criar nova toda segunda-feira).

### Template: `Relatório [YYYY-MM-DD] — [Cliente]`

```
# Relatório Semanal — [Data]
**Período:** [data início] → [data fim]
**Gerado por:** EGOS Knowledge Base Agent
**Cliente:** [nome]

---

## 1. Alertas Críticos
> [lista de alertas gerados automaticamente]
- ...

## 2. Novos Documentos Indexados esta Semana
- [N] documentos adicionados
- Destaques: [lista]

## 3. Entidades com Novas Conexões
- [lista de entidades com novas relações descobertas]

## 4. Queries mais Frequentes
| Query | Vezes |
|-------|-------|
| ... | N |

## 5. Saúde da Base
- Documentos desatualizados: [N]
- Entidades sem fonte: [N]
- PII pendente de revisão: [N]

## 6. Recomendações
- [ ] [ação sugerida pelo agente]
- [ ] [ação sugerida pelo agente]

---
*Próximo relatório: [próxima segunda-feira]*
```

---

## Sub-página 6: Compliance LGPD (Guard Brasil)

**Layout:** Status page simples.

```
🔒 Guard Brasil — Status LGPD

API: guard.egos.ia.br ● Online
Versão do pacote: @egosbr/guard-brasil v0.2.3
Última auditoria: [data]

── Dados detectados na base ──────────────────────
CPF: [N ocorrências] em [N documentos]
RG: [N ocorrências] em [N documentos]
Telefone: [N ocorrências] em [N documentos]
[...]

── Audit Trail ────────────────────────────────────
[link para tabela de acessos Supabase]
Acessos registrados (últimos 7d): [N]
Usuários com acesso: [lista]

── Evidências (SHA-256) ───────────────────────────
[link para evidence chain — LGPD Art. 37]

── Base Legal ─────────────────────────────────────
Finalidade: Gestão de investigações / Base de conhecimento profissional
Responsável pelos dados: [Nome] — [Cargo]
DPO: [Nome] (se aplicável)
Tempo de retenção: conforme política [link]
```

---

## Sub-página 7: Configuração

**Acesso restrito (somente Enio + cliente admin).**

```
⚙️ Configuração da KB

── Credenciais ────────────────────────────────────
Tenant ID: [cliente-slug]
Supabase URL: [URL]
Knowledge MCP: @egosbr/knowledge-mcp v1.1.0
Guard API Key: *****

── Ingest ─────────────────────────────────────────
Pasta monitorada: [caminho local ou Drive ID]
Formatos ativos: pdf, docx, md, xlsx, json, jsonl
Frequência: manual | diária | semanal

── Modelos ────────────────────────────────────────
Query padrão: claude-haiku-4-5 (rápido, econômico)
Análise profunda: claude-sonnet-4-6
Entity extraction: BERTimbau (PT-BR)

── Integrações ────────────────────────────────────
[ ] Notion (este workspace)
[ ] WhatsApp (Evolution API)
[ ] Telegram
[ ] Email (IMAP)

── Contato EGOS ───────────────────────────────────
Suporte: [contato Enio]
SLA: [definido em contrato]
```

---

## Setup Rápido (10 min por cliente)

```bash
# 1. Duplicate este template no Notion (root page da KB)
# 2. Renomear: "[NomeCliente] — Knowledge Base"
# 3. Preencher configuração (Sub-página 7): tenant_id, credenciais
# 4. Primeira ingestão:
bun scripts/kb-ingest.ts \
  --dir /caminho/docs-cliente/ \
  --tenant nome-cliente \
  --category geral \
  --dry  # verificar primeiro

# 5. Verificar Visão Geral: métricas devem aparecer
# 6. Testar: "Perguntar à KB" com uma query simples
# 7. Guard Brasil: verificar compliance status
```

---

## Preços de Referência (para proposta)

| Tier | Setup | Mensal | Inclui |
|------|-------|--------|--------|
| Starter | R$ 2.500 | R$ 500 | até 500 docs, 1 usuário, 1 setor |
| Pro | R$ 5.000 | R$ 1.200 | até 2.000 docs, 5 usuários, 3 setores |
| Enterprise | R$ 15.000+ | R$ 3.000+ | ilimitado, multi-tenant, relatórios IA diários |

*Consultoria LGPD incluída no setup. Guard Brasil API inclusa na mensalidade.*

---

*Próximo passo: KBS-031 (gerador de relatório de inteligência automático) + KBS-036 (validação DHPP).*
