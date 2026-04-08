# KB-as-a-Service — "EGOS Knowledge" para Profissionais Brasileiros

> **Version:** 1.0.0 — 2026-04-08
> **SSOT:** Este arquivo. Tasks operacionais em `TASKS.md` seção **KBS-***.
> **Parent:** `docs/strategy/GO_TO_MARKET_RESEARCH.md`, `docs/GTM_SSOT.md`
> **Filosofia:** Build what needs to be built, in the right order. Sem urgência de MRR. Qualidade antes de escala.

---

## 0. TL;DR

Produtizar o que EGOS já tem (wiki-compiler, atomizer, ARR, Guard Brasil, 92 wiki pages live) como um serviço de **"Cérebro Externo Governado"** para profissionais brasileiros. Interface = **Notion** (curva de aprendizado baixa, já conhecido). Motor = **Claude Code + MCP** rodando no computador do cliente ($20/mês Claude Pro). Backend = **EGOS governance layer** (Guard Brasil para LGPD, wiki-compiler para ingestão, SSOT lint para saúde). Primeiro beta = **FORJA (metalurgia)**. Monetização dupla: **serviço de implementação/manutenção** (R$) + **APIs x402** (AgentCash/APINow, USDC global).

**Unlock crítico (descoberto 2026-04-08):** Notion MCP já está nativamente conectado a este Claude Code session (`mcp__claude_ai_Notion__*`). Eliminou o blocker de "construir integração Notion" da auditoria anterior. Podemos criar templates, databases e páginas Notion direto daqui.

---

## 1. O que JÁ temos (READY)

| Camada | Asset | Path | Estado |
|--------|-------|------|--------|
| **Atomização** | `DefaultAtomizer` — quebra markdown em atoms semânticos | `packages/atomizer/` | ✅ Production |
| **Busca** | `InMemorySearchEngine` (ARR — Adaptive Atomic Retrieval) | `packages/search-engine/` | ✅ Production |
| **Wiki compiler** | Agent com modos `compile/lint/dedup/enrich/index/world` | `agents/agents/wiki-compiler.ts` | ✅ Production |
| **Schema Supabase** | `egos_wiki_pages`, `egos_learnings`, `egos_wiki_changelog` + RLS | `supabase/migrations/20260405_egos_knowledge_system.sql` | ✅ 92 pages live |
| **Knowledge MCP** | Package seed para expor KB via MCP | `packages/knowledge-mcp/` | ⚠️ Seed — precisa completar |
| **Obsidian arch** | Padrão Karpathy documentado (raw→wiki→outputs) | `docs/EGOS_KNOWLEDGE_BASE_ARCHITECTURE.md` | ✅ Doc |
| **Guard Brasil** | PII masking (CPF/RG/CNPJ/telefone/email) — 4ms — LGPD layer | `packages/guard-brasil/` | ✅ v0.2.2 live |
| **Guard Brasil MCP** | MCP server expondo `guard_inspect` + `guard_scan_pii` | `packages/guard-brasil-mcp/` | ✅ Pronto |
| **HARVEST.md** | 1944-line knowledge SSOT (auto-disseminate target) | `docs/knowledge/HARVEST.md` | ✅ Live |
| **Notion MCP (nativo)** | Claude Code session já conectado ao workspace Notion | `mcp__claude_ai_Notion__*` | ✅ **Descoberto 2026-04-08** |

**Veredito:** ~70% do produto já existe. Falta empacotar + apresentar + onboarding.

---

## 2. O que FALTA (gap analysis)

| Gap | Impacto | Effort |
|-----|---------|--------|
| **Notion templates PT-BR** para o cliente duplicar | BLOCKER — primeira impressão | S (1 dia, via Notion MCP) |
| **Ingestor de PDFs/Docx** (orçamentos, normas ABNT, contratos) | BLOCKER para FORJA | M (2 dias — plugar em wiki-compiler) |
| **Schema multi-tenant** (isolamento por cliente na Supabase) | BLOCKER antes do 2º cliente | M (RLS tuning + namespace) |
| **Guia de setup Claude Code + Notion MCP PT-BR** | BLOCKER — cliente não vai ler docs em inglês | S (0.5 dia) |
| **Loom demo em português** — 3–5 min "zero conhecimento técnico" | BLOCKER de vendas | S (1 dia) |
| **KB-lint adaptado** (contradições, páginas órfãs, staleness) para cliente | HIGH — diferencial vs copiadores do thread | M (reusar ssot-auditor) |
| **FORJA namespace**: pasta, .guarani adaptado, dados piloto | HIGH — validação interna | M (1 dia de setup) |
| **Landing page "EGOS Knowledge"** no egos-site | MEDIUM | S |
| **Pricing page** | MEDIUM | S |
| **Citation export** (Markdown + PDF com fontes) | NICE-to-have | S |
| **Multi-idioma** (PT-BR + EN no mesmo vault) | NICE-to-have | M |

---

## 3. Produto: "EGOS Knowledge"

### 3.1 Nome e posicionamento
- **Nome interno:** EGOS Knowledge
- **Nome de venda (BR):** *"Inteligência da Empresa — Sua memória que não esquece"* ou *"Cérebro da [FORJA/Escritório/Clínica]"*
- **Posicionamento:** *"Seu conhecimento vira consulta em segundos. Com governança LGPD desde o dia 1."*
- **Anti-posicionamento:** NÃO é Notion AI. NÃO é "ChatGPT com seus docs". NÃO é ferramenta para devs. É **consultoria + sistema entregue + manutenção**.

### 3.2 Arquitetura (3 camadas)

```
┌─────────────────────────────────────────────────────────┐
│ CAMADA 1 — Interface (cliente vê)                        │
│ Notion workspace (template duplicado)                    │
│   ├─ Página "Pergunte aqui"                              │
│   ├─ Database "Documentos"                               │
│   ├─ Database "Decisões/Orçamentos"                      │
│   ├─ Database "Normas & Compliance"                      │
│   └─ Página "Histórico / Mudanças"                       │
└─────────────────────────────────────────────────────────┘
                         ▲
                         │ MCP (OAuth nativo)
                         │
┌─────────────────────────────────────────────────────────┐
│ CAMADA 2 — Motor (cliente roda localmente)               │
│ Claude Code CLI ($20/mês Claude Pro)                     │
│   ├─ CLAUDE.md — schema EGOS-governado                   │
│   ├─ .guarani/kbs-rules.md — philosophy + limits         │
│   ├─ MCP servers:                                        │
│   │   • notion (nativo, OAuth)                           │
│   │   • guard-brasil-mcp (LGPD — via npx)                │
│   │   • knowledge-mcp (ARR query — via npx)              │
│   │   • filesystem (leitura de PDFs locais)              │
│   └─ Slash commands: /ingest /ask /lint /export          │
└─────────────────────────────────────────────────────────┘
                         ▲
                         │
┌─────────────────────────────────────────────────────────┐
│ CAMADA 3 — Governance + manutenção (nós rodamos)         │
│ EGOS kernel + Supabase (opcional p/ clientes enterprise) │
│   ├─ wiki-compiler — compilação periódica                │
│   ├─ ssot-auditor adaptado — KB-lint                     │
│   ├─ HARVEST pattern — aprendizados do cliente           │
│   └─ Audit trail — provenance de todo query              │
└─────────────────────────────────────────────────────────┘
```

### 3.3 Tiers de produto

| Tier | Quem | O que recebe | Preço (draft) |
|------|------|--------------|---------------|
| **Starter** | Profissional autônomo (advogado, consultor, médico) | Template Notion + setup Claude Code (1h remoto) + manual PT-BR + 30d suporte | **R$ 1.500 setup + R$ 200/mês manutenção** |
| **Pro** | PME (até 5 usuários) | Starter + ingestão inicial de 100 docs + custom schema + Guard Brasil LGPD + 90d suporte | **R$ 5.000 setup + R$ 800/mês** |
| **Enterprise** | Indústria / escritório grande (FORJA tier) | Pro + multi-tenant Supabase + integração com sistemas legados + SLA + on-call | **R$ 15k–50k setup + R$ 2.5k–5k/mês** |

> **Regra:** Cliente assina Claude Pro ($20/mês) separadamente com cartão próprio. Não repassamos custo de LLM — cliente é dono dos limites.

### 3.4 Fluxo de onboarding (cliente PME)

1. **Descoberta** (30min call) — dores reais, tipos de documentos, quem vai usar.
2. **Contrato + acesso** — cliente cria conta Notion + Claude Pro. Nós ganhamos acesso ao workspace.
3. **Setup técnico** (1h remoto) —
   - Duplicar template Notion (via `notion-duplicate-page` MCP)
   - Instalar Claude Code no máquina do cliente
   - Configurar MCPs (notion + guard-brasil + filesystem)
   - Copiar `CLAUDE.md` + `.guarani/kbs-rules.md` para pasta do projeto
4. **Ingestão piloto** — pegar 10–30 documentos reais, rodar `/ingest`, validar resultado.
5. **Treinamento** (1h) — 5 perguntas típicas, mostrar citações, mostrar linting.
6. **Manutenção** — semanalmente rodar `/lint`, mensalmente revisar staleness, trimestralmente auditoria.

---

## 4. Monetização (duas camadas)

### 4.1 Camada A — Serviço (R$, imediato)
Implementação + manutenção de KB para clientes brasileiros. Tiers acima. **Foco nos próximos 90 dias.**

### 4.2 Camada B — APIs x402 (USDC global, médio prazo)
Publicar capacidades EGOS em marketplaces agent-native. Já documentado em AgentCash analysis (`~/.codeium/windsurf-next/API_MARKETPLACES_MASTER_ANALYSIS.md` referenciado) e tasks **API-001..019** existentes.

**Estratégia multi-plataforma:**
- **Tier 1 (P0):** AgentCash, APINow.fun, Proxies.sx (x402 nativo, 0% comissão)
- **Tier 2 (P1):** RapidAPI, Replicate, DigitalAPI (tradicional, discovery)
- **Primeira API a publicar:** Guard Brasil (zero competidores brasileiros, LGPD edge)

**Sinergia com Camada A:** Clientes PME pagam em R$ pelo serviço; agentes globais pagam em USDC pelo uso das APIs que sustentam o serviço. Dupla monetização do mesmo core.

---

## 5. Plano de tracks (execução)

### Track A — Dogfooding interno (nós mesmos primeiro)
**Objetivo:** Usar EGOS Knowledge para gerenciar o próprio EGOS (TASKS.md, HARVEST.md, handoffs). Gerar vídeos e exemplos reais. **Pré-requisito para vender qualquer coisa.**

### Track B — Beta FORJA (metalurgia)
**Objetivo:** Primeiro cliente real. Ingestar orçamentos antigos + fichas de produção + normas ABNT. Validar ROI ("orçamento que demorava 2h agora demora 5min").

### Track C — Produto público (template + guia + landing)
**Objetivo:** Template duplicável + guia PT-BR + landing page. Pronto para apresentar em X.com/LinkedIn/DMs aos potenciais parceiros (referência §24 CLAUDE.md — "aligned builders").

### Track D — Monetização APIs (x402)
**Objetivo:** Onboarding em AgentCash + APINow + Proxies.sx. Guard Brasil como primeira publicação.

### Track E — Manutenção da sessão anterior (carryover)
**Objetivo:** Não perder DISS-002/003/005, GH-086, PAP-002, LS-002, XMCP-002 (start.sh no VPS).

---

## 6. Tasks — ver `TASKS.md` seção **KBS-*** (append 2026-04-08)

Resumo:
- **P0 BLOQUEADORES:** KBS-001 (Notion template), KBS-002 (CLAUDE.md cliente), KBS-003 (guia setup PT-BR), KBS-004 (FORJA namespace), KBS-005 (Loom demo), XMCP-002, DISS-002
- **P0 PRODUTO:** KBS-006 (PDF ingestor), KBS-007 (KB-lint adaptado), KBS-008 (knowledge-mcp completo), KBS-009 (pricing page), KBS-010 (landing)
- **P1 MONETIZAÇÃO:** API-001..019 (x402 marketplaces), KBS-015..018 (Stripe tiers), KBS-019 (contract template)
- **P1 SCALE:** KBS-020 (multi-tenant Supabase), KBS-021 (citation export), KBS-022 (multi-idioma)
- **P2 CARRYOVER:** PAP-002, LS-002, GH-086 (gem-hunter-mcp segue plano Sprint 1)

---

## 7. Primeiras 48h (concretas)

1. **KBS-001** — Criar template Notion via `notion-create-database` + `notion-create-pages`. Estrutura:
   - DB "Documentos" (título, categoria, data, fonte, status ingestão)
   - DB "Q&A" (pergunta, resposta IA, fontes citadas, data)
   - DB "Decisões" (para orçamentos/compliance)
   - Página root "Como usar"
2. **KBS-002** — Escrever `CLAUDE.md` para cliente (≤100 linhas, PT-BR, com placeholders por setor)
3. **KBS-003** — Guia setup em PT-BR (Markdown + screenshots): instalar Claude Code → conectar Notion MCP → primeiro /ask
4. **KBS-004** — Criar `clients/forja/` namespace no repo egos-lab (ou FORJA repo), com `.guarani/forja-rules.md`
5. **XMCP-002** — Desbloquear GTM: `ssh ... "cd /opt/xmcp && bash start.sh"`
6. **DISS-002** — Continuar a sessão anterior (propagator)

---

## 8. Riscos e mitigações

| Risco | Mitigação |
|-------|-----------|
| Cliente trava no "instalar Claude Code" (CLI barrier) | Loom passo-a-passo + sessão remota 1h incluída no Starter |
| Claude Pro não dar conta do volume (limite de uso) | Começar com Pro, migrar para Max ($100) se bater limite — custo do cliente, transparente |
| Cliente não entende "provenance" / citações | Template Notion expõe `source_files` como propriedade visível |
| LGPD — cliente enviar dado sensível sem saber | Guard Brasil MCP wrapping no `/ingest` — auto-redaction + alerta |
| Cliente churn após setup (não usa) | Manutenção mensal obriga contato + onboarding estendido de 30d no Starter |
| Concorrente copia o template grátis (thread do X) | Diferencial = governance + lint + LGPD + manutenção humana. Open-source o template, monetizar serviço. |
| EGOS kernel instável mid-client | Frozen zones já protegem; client-facing code em `packages/knowledge-mcp/` isolado do runner |

---

## 9. Métricas de sucesso (90 dias)

| Métrica | Target | Gate |
|---------|--------|------|
| **Dogfooding interno live** | /ask funcional sobre TASKS.md+HARVEST | 2026-04-15 |
| **FORJA beta ativo** | 1 cliente usando semanalmente | 2026-04-30 |
| **Template público publicado** | Notion + GitHub + landing | 2026-05-10 |
| **2º cliente Starter pago** | R$ 1.500 entrou no caixa | 2026-05-31 |
| **Guard Brasil em 1 marketplace x402** | AgentCash onboard + 1ª chamada paga | 2026-06-15 |
| **5 clientes Starter + 1 Pro** | ~R$ 12k MRR setup + R$ 1.8k recorrente | 2026-06-30 |

**Regra §23 CLAUDE.md:** Não tratar essas como metas de urgência. São sinais de saúde. Se atrasar, diagnosticar por que (não empurrar mais esforço cego).

---

## 10. Relação com outras SSOTs

- **GTM_SSOT.md** — KB-as-a-Service é novo canal, complementa Guard Brasil outreach
- **CAPABILITY_REGISTRY.md** — adicionar §27 (futuro) "KB-as-a-Service delivery"
- **HARVEST.md** — aprendizados de cada onboarding de cliente vão para cá
- **TASKS.md** — operacional (KBS-*)
- **AGENTCASH/API marketplaces** — `API-001..019` existentes, reapontados para alinhar com KBS
- **FORJA repo** — cliente zero, acoplamento via adapter (limite standalone preservado)

---

*Fim do plano. Manutenção: revisar a cada 2 semanas na primeira fase, a cada 4 semanas depois que 3+ clientes ativos.*
