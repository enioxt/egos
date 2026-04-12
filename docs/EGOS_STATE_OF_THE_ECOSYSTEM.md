# EGOS — State of the Ecosystem
# SSOT: Diagnóstico completo, atualizado em 2026-04-12
# Versão: 1.0.0 | Criado na sessão Opus plan + Sonnet execution

> Este documento é o SSOT vivo do ecossistema EGOS. Atualizar a cada sessão /end ou quando houver mudança estrutural.
> Leitura primária para: onboarding de novos colaboradores, pitch de parcerias, decisões de arquitetura.

---

## 🗺️ O QUE É O EGOS

EGOS é uma **plataforma de orquestração de agentes de IA com governança nativa**. Não é um produto único — é um **kernel que potencializa múltiplos produtos** através de módulos compartilhados, regras de governança, e infraestrutura de agents.

```
EGOS = Compliance Layer  (Guard Brasil — LGPD/PII, 4ms, 16 padrões)
     + Intelligence Layer (Gem Hunter + Eagle Eye + BR-ACC)
     + Execution Layer    (Hermes Agent + DashScope/OpenRouter LLM chain)
     + Automation Layer   (X-Alert + auto-disseminate + session-aggregator)
     + Knowledge Layer    (KBS / Notion MCP / wiki-compiler / ARR search)
     + Governance Layer   (.guarani/ + 26 SSOT domains + pre-commit gates)
```

**Score de saúde:** 8.5/10 | **Commits 30 dias:** 1179+ | **Repositórios ativos:** 6

---

## 📦 PRODUTOS E SISTEMAS VIVOS

### 1. Guard Brasil
**URL:** [guard.egos.ia.br](https://guard.egos.ia.br) | **Status:** ✅ Healthy (4ms, v0.2.2)
**NPM:** `@egosbr/guard-brasil` | **SSOT:** `packages/guard-brasil/`

```
Única API de LGPD art.11 (dados de saúde) open-source no Brasil
16 padrões PII: CPF, CNPJ, RG, CNH, SUS, NIS/PIS, MASP, REDS, 
               Processo, Placa (2 formatos), Email, Telefone, 
               Título de Eleitor, CEP, Dado de Saúde
```

**Stack:** TypeScript/Bun | **Deploy:** Docker/Hetzner VPS | **Endpoints:** `/v1/inspect`, `/v1/meta`, `/health`
**Projeção revenue:** $3,058/mês (AgentCash + x402 + RapidAPI)
**Diferencial único:** ATRiAN integration — valida ética + PII em uma chamada

**Teste rápido:**
```bash
curl -s https://guard.egos.ia.br/v1/inspect \
  -H "Content-Type: application/json" \
  -d '{"text":"CPF do cliente: ***.***.***-**"}' | jq .
```

---

### 2. Gem Hunter
**URL:** [gemhunter.egos.ia.br](https://gemhunter.egos.ia.br) | **Status:** ✅ Live
**SSOT:** `agents/agents/gem-hunter.ts` (2350 linhas) | `docs/gem-hunter/SSOT.md`

```
14 fontes simultâneas: GitHub, NPM, arXiv, Papers-with-Code, 
HackerNews, Reddit, Product Hunt, X.com, Discord, Exa, 
Papers-without-code, Substack, agent-marketplaces, strategic-signals
```

**Stack:** TypeScript/Bun | **Scoring:** heurística composta `scoreGem()` + Qwen LLM (papers) + Exa enrichment
**CCR job:** Segunda 9h BRT semanal | **Telegram alerts:** hot gems score ≥80
**Community:** `gem_lists` + `gem_votes` + trending API (port 3070)
**Scoring prompts SSOT:** `docs/gem-hunter/prompts/scoring-v1.md` (versionado 2026-04-08)

**Últimas melhorias (2026-04-08):**
- CORAL-002: dedup cache `gem_discoveries` (skip gems já descobertos em 14 dias)
- `gem_feedback` table + `gem_seen_cache` (Supabase migration pendente de aplicar)
- Scoring prompts extraídos e versionados

---

### 3. Eagle Eye
**URL:** [eagleeye.egos.ia.br](https://eagleeye.egos.ia.br) | **Status:** ✅ Live (egos-lab)
**SSOT:** `egos-lab/apps/eagle-eye/` | **Dados:** Supabase

```
OSINT de licitações públicas brasileiras em tempo real
84 territórios monitorados (municípios + estados)
Fontes: PNCP + Querido Diário
5-axis scoring: Viabilidade, Complexidade, Mercado, Risk, Potencial
```

**Stack:** Next.js + TypeScript + Python (ETL) | **LLM:** Qwen + Gemini
**Funcionalidades:** document-parser (regex+LLM edital extraction), insight-generator (BID/INVESTIGATE/SKIP), territory map, scoring dashboard
**Revenue model:** B2G integradores 70/30 rev-share | R$99-499/mês SaaS

---

### 4. FORJA
**URL:** [forja-orpin.vercel.app](https://forja-orpin.vercel.app) | **Status:** ✅ Live (MVP)
**Repo:** `/home/enio/forja/` (standalone) | **SSOT:** `docs/FORJA_P0_P1_FOCUS.md`

```
Chat-first ERP para metalúrgicas e oficinas industriais
Cliente piloto: Rocha Implementos (Patos de Minas)
UX: "Modo Oficina" — botões 64px+, dark mode, bottom nav, voz-first
```

**Stack:** Next.js 15 + React 19 + Tailwind 4 + Supabase + TypeScript
**LLM:** Alibaba Qwen-plus primary + Gemini 2.0 Flash fallback
**Tools ativos:** `search_products`, `get_stock_level`, `create_quote`, `get_production_status`
**Integrações:** WhatsApp (Evolution API on VPS), PII Scanner 15 padrões, ATRiAN validation

**P0 pendentes para pilot:** FORJA-003 (RLS multi-tenant), FORJA-019B (Email pipeline), FORJA-020 (WhatsApp bidirecional), FORJA-TOOLS-001 (budget_tool/cost_history/ata_extractor)

---

### 5. 852 Inteligência (EGOS Police Platform)
**URL:** [852.egos.ia.br](https://852.egos.ia.br) | **Status:** ✅ Production
**Repo:** `/home/enio/852/` | **SSOT:** Local

```
Chatbot policial com anonimato total + 27 ferramentas especializadas
MASP (matrícula anônima), sem CPF, sem rastreabilidade de identidade
Integração: BR-ACC (9.1M nós Neo4j) + Guard Brasil + ATRiAN
```

**Stack:** Next.js + TypeScript + Python FastAPI (br-acc)
**Capacidades:** correlação inteligente, revisão de conversas AI, hot topics, export PDF/DOCX/WhatsApp
**Projeção revenue:** $3,473/mês

---

### 6. BR-ACC (EGOS Inteligência)
**URL:** [inteligencia.egos.ia.br](https://inteligencia.egos.ia.br) | **Status:** ✅ Production
**Repo:** `/home/enio/br-acc/` (standalone)

```
OSINT platform com 9.1M nós Neo4j (83.7M verificado 2026-04-07)
27 ferramentas: consulta de vínculos, análise de redes, score criminal
LGPD: Guard Brasil Python SDK + public_guard masking
```

**Stack:** Python FastAPI + Neo4j + Guard Brasil Python SDK
**Dados:** 10 tópicos confirmados, bulk graph analysis

---

### 7. Timeline AI Publishing
**URL:** [egos.ia.br/timeline](https://egos.ia.br/timeline) | **Status:** ✅ Live (TL-001..011 done)
**SSOT:** `docs/TIMELINE_AI_PUBLISHING_ARCHITECTURE.md`

```
Commits → artigos automáticos → aprovação HITL (Telegram) → publish
Zero publicação sem aprovação humana
Auto-post X.com com queue Supabase + aprovação inline
```

**Stack:** Bun/Hono + Supabase + Telegram Bot API + OpenRouter Qwen
**Aprovação:** 3 opções (✅ Publicar / ✏️ Editar / ❌ Cancelar) com 48h timeout
**Cron:** `timeline-cron-daily.sh` (03:00 UTC)

---

### 8. KBS — Knowledge Base as a Service (Patos de Minas)
**Status:** ✅ Templates criados, 12 Notion databases populados | **SSOT:** `docs/strategy/KB_AS_A_SERVICE_PLAN.md`

```
Assistente de conhecimento para 10 perfis profissionais de Patos de Minas:
Consultor Agrícola, Veterinário, Agrônomo, Engenheiro Civil, 
Médico/Clínica, Contador Rural, Advogado (Direito Agrário),
Cooperativa, Imobiliária Rural, SENAR/Escola
```

**Stack:** Notion MCP (nativo Claude Code) + wiki-compiler + ARR search + Guard Brasil
**Modelo:** Claude Code motor local (R$0/mês no tier gratuito) + Notion UI (zero curva de aprendizado BR)
**Pricing:** R$1.5k setup + R$200/mês | R$5k setup + R$800/mês

---

### 9. X.com Reply Bot
**Status:** ✅ Live (VPS hourly cron) | **SSOT:** `scripts/x-reply-bot.ts`

```
14 queries temáticas: LGPD, agentes AI, Eagle Eye, Guard Brasil, Claude Code
Queue mode: replies vão para Supabase (status=pending) → aprovação HQ
Scoring melhorado (2026-04-08): few-shot examples + low-visibility bypass + news detector
```

---

## 🛠️ INFRAESTRUTURA

### VPS Hetzner (204.168.217.125)
**RAM:** 8.6GB free | **Disk:** 78GB/301GB (27%) | **Uptime:** 9+ dias

| Serviço | Container | Porta | Status |
|---------|-----------|-------|--------|
| Guard Brasil API | egos-guard | 3010 | ✅ |
| EGOS HQ | egos-hq | 3060 | ✅ |
| Gem Hunter API | gem-hunter | 3070 | ✅ |
| EGOS Site | egos-site | 3071 | ✅ |
| 852 Chatbot | 852 | 3052 | ✅ |
| BR-ACC (Inteligência) | br-acc | 3080 | ✅ |
| Ratio API | ratio-api | 3085 | ✅ |
| X MCP | xmcp | 8200 | ✅ |
| Caddy (reverse proxy) | — | 80/443 | ✅ |

**Crons ativos (VPS):**
- `vps-watchdog.sh` → `*/5 * * * *` (10 containers monitoring)
- `session-aggregator.sh` → `30 23 * * *` (daily handoff)
- `timeline-cron-daily.sh` → `0 3 * * *` (article generation)
- `x-reply-bot hourly` → `0 * * * *`
- `portfolio-sync.ts` → `0 8 * * *` (living portfolio daily 8h BRT)

### Supabase
**Tabelas ativas principais:** `egos_wiki_pages` (92), `knowledge_base` (1648 ARR rows), `gem_discoveries`, `gem_votes`, `gem_lists`, `x_reply_runs`, `timeline_drafts`, `x_post_queue`, `x_post_hitl`, `agent_events`
**Applied (2026-04-08):** `gem_feedback`, `gem_seen_cache`

---

## ⚙️ STACKS & LINGUAGENS

### TypeScript / Bun (primária — 80% do codebase)
- Runtime: Bun v1.x
- Frontend: Next.js 15, React 19, Tailwind 4, Hono
- Packages: `@egos/shared`, `guard-brasil`, `atomizer`, `search-engine`, `knowledge-mcp`, `mcp-governance`
- Repos: egos, forja, 852, egos-lab, carteira-livre

### Python (15% — ETL + ML)
- FastAPI: br-acc API (27 tools), eagle-eye ingestors
- Libraries: Neo4j driver, Guard Brasil Python SDK, scikit-learn, pgvector
- Repos: br-acc, egos-lab/eagle-eye

### SQL / Supabase (5%)
- PostgreSQL + RLS + pgvector (ARR vector search)
- Migrations em `supabase/migrations/*.sql`

### Outros
- Bash: hooks, scripts VPS, governance-sync.sh
- YAML: `.egos-manifest.yaml` (doc-drift claims), GitHub Actions workflows
- Markdown: `.guarani/` governance docs (48 files)

---

## 🔮 MÓDULOS COMPARTILHADOS (`packages/shared/src/`)

| Módulo | Arquivo | Adotado por |
|--------|---------|-------------|
| LLM Provider (multi-provider) | `llm-provider.ts` | egos, forja, egos-lab |
| Model Router (8 modelos, 10 tarefas) | `model-router.ts` | egos |
| ATRiAN (7 axiomas éticos) | `atrian.ts` | 852, forja, egos, intelink, br-acc |
| PII Scanner BR (16 padrões) | `pii-scanner.ts` | 852, forja, egos, intelink, br-acc |
| Conversation Memory | `conversation-memory.ts` | 852, forja, egos |
| Circuit Breaker | `circuit-breaker.ts` | egos |
| Evidence Chain | `evidence-chain.ts` | egos |
| Event Bus (Supabase Realtime) | `event-bus.ts` | egos, egos-lab |
| Public Guard BR | `public-guard.ts` | egos, carteira-livre, forja |
| World Model | `world-model.ts` | egos (/start) |

---

## 🔗 INTEGRAÇÕES ATIVAS

| Sistema | Como | Status | Uso |
|---------|------|--------|-----|
| Telegram | Bot API (HITL approval + alerts) | ✅ | Timeline, Gem Hunter, watchdog |
| X.com | API v2 OAuth 1.0a + X MCP (VPS:8200) | ✅ | x-reply-bot, opportunity alerts |
| WhatsApp | Evolution API (VPS:8080) | ✅ | FORJA, 852, Timeline |
| Notion | MCP nativo Claude Code | ✅ | KBS-PM, knowledge base |
| Supabase | MCP + REST + Realtime | ✅ | Todos os produtos |
| OpenRouter | API HTTP | ✅ | LLM fallback chain |
| Alibaba DashScope | API HTTP | ✅ | Qwen-plus primary (orquestrador) |
| Vercel | Deploy automático | ✅ | forja, egos-lab, carteira-livre |
| GitHub Actions | CCR jobs (3 slots) | ✅ | Gem Hunter, Governance Drift, Code Intel |
| AgentCash | SDK (invite code in TASKS.md API-021) | ✅ Done (API-001) | Guard Brasil monetização |

---

## 🏛️ GOVERNANÇA (`.guarani/` — 48 arquivos)

```
.guarani/
├── RULES_INDEX.md          — ponto de entrada das regras
├── PREFERENCES.md          — preferências do sistema
├── IDENTITY.md             — identidade da plataforma
├── PHILOSOPHY.md           — princípios filosóficos
├── orchestration/
│   ├── PIPELINE.md         — 7-fase pipeline (FROZEN)
│   ├── DOMAIN_RULES.md     — regras por domínio
│   ├── AGENT_CLAIM_CONTRACT.md — contrato de claims de agents
│   ├── LLM_ORCHESTRATION_MATRIX.md — roteamento de LLMs
│   └── QA_LOOP_CONTRACT.md
└── security/
    └── INJECTION_HARDENING.md
```

**26 SSOT domains mapeados** em `.ssot-map.yaml` com SSOT gate (Gemini→Alibaba→keyword fallback)
**Pre-commit gates:** gitleaks, focus enforcement, doc-drift verifier, SSOT drift, vocabulary guard, file intelligence, legacy detector

---

## 📊 ÚLTIMAS 48H — O QUE FOI ENTREGUE

### 2026-04-08 (51+ commits)

| Horário | Entrega | Tasks |
|---------|---------|-------|
| 13:00 | TL-002..011 live — Timeline + egos-site + Telegram approval | 10 tasks |
| 13:00 | GH-075..080 — Gem Hunter landing + voting API + awesome-gems | 6 tasks |
| 14:00 | SOCIAL-001..008 queued — 8 posts X.com aprovados | 8 tasks |
| 14:00 | Governance kernel propagation v1.0 + RULES-002/003 | 3 tasks |
| 14:00 | X.com HITL approval 3-option system | novo sistema |
| 15:30 | DISS-001/004 auto-disseminate pipeline + post-commit hook | P0 |
| 15:30 | PAP-001 heartbeat.ts (frozen wrapper pattern) | P1 |
| 16:00 | CORAL-001 gem_discoveries Supabase + CORAL-002 dedup | P1 |
| 16:00 | Supabase cleanup: 42 tabelas mortas dropped | SUPA-001/002/004 |
| 17:30 | XMCP-002/003 X MCP live on VPS port 8200 | P0 |
| 17:50 | Session /end3 — 51 commits, handoff escrito | |
| 18:30 | KBS-PM-001..011 — 10 perfis + 12 databases Notion populados | 11 tasks |
| 19:00 | a03875a — API monetization research (30+ platforms, Windsurf) | docs |
| 19:20 | 5 sector templates (industrial-forja, médico, advocacia, contador, agrônomo) | KBS |
| 19:56 | GH-089/090 scoring prompts extraídos + gem_feedback migration | P1 |
| 19:56 | XRB-002/003/004 x-reply-bot scoring improvements | P1 |
| 19:57 | FORJA tasks synced para repo standalone | FORJA |

---

## 💪 PONTOS FORTES ÚNICOS

### 1. Guard Brasil — O único detector LGPD art.11 open-source
- 16 padrões PII em 4ms
- Categoria especial: dados de saúde (art.11 LGPD)
- ATRiAN integrado (ética + PII em uma chamada)
- Versão Python + TypeScript + API REST + MCP server

### 2. Governança nativa com enforcement pre-commit
- Nenhum commit passa sem: gitleaks + focus check + doc-drift + vocabulary guard
- 26 domínios SSOT mapeados automaticamente
- Frozen zones: runner.ts, event-bus.ts, pre-commit chain (intocáveis)
- Auto-disseminate: task IDs em commits → TASKS.md automático

### 3. Knowledge Layer multi-formato
- Atomizer: chunking semântico sentence-level
- ARR: vector search com pgvector (1648 embeddings ativos)
- wiki-compiler: ingerir qualquer doc → searchable em segundos
- Notion MCP: nativo no Claude Code (zero integração custom)
- 10 templates de setor prontos (metalurgia, medicina, direito, agro...)

### 4. LLM Orchestration multi-provider
```
Primary:  Alibaba Qwen-plus (orquestrador)
Tier 2:   Google Gemini 2.0 Flash (volume)
Tier 3:   OpenRouter qwen-2.5-7b-instruct:free (x-reply-bot)
Reasoning: qwq-plus (deep analysis)
Fallback: keyword-based (sem LLM)
```

### 5. HITL (Human-In-The-Loop) em tudo
- Nenhum artigo, post X.com, ou ação crítica é feita sem aprovação
- Telegram como canal de aprovação (✅✏️❌ inline buttons)
- Queue Supabase com timeout 48h

### 6. Feedback loop nascente (entregue hoje)
- gem_feedback table + Telegram inline keyboard (GH-092/093 pendentes)
- Scoring prompts versionados e editáveis sem deploy
- 2x/dia AI lê comentários → relatórios → tasks auto-geradas (GH-093 pendente)

### 7. ATRiAN — Validação de Integridade de Outcomes
**Arquivo:** `packages/shared/src/atrian.ts`
- 7 axiomas éticos (não apenas LGPD — inclui equidade, transparência, reversibilidade)
- 5 categorias de violação: absolute claims, fabricated data, false promises, invented acronyms, blocked entities
- 4 níveis de severidade: CRITICAL / HIGH / MEDIUM / LOW
- Padrões específicos ao português brasileiro ("não se preocupe", "garanto que")
- Único framework ético-técnico PT-BR open-source disponível

### 8. Evidence Chain — Proveniência para LGPD DPO
**Arquivo:** `packages/shared/src/evidence-chain.ts`
- Ledger de proveniência: `timestamp + agent_id + action + output_hash + compliance_score`
- Auditável por DPO (encarregado LGPD art.41) e por autoridade (ANPD)
- Hash SHA-256 de cada saída de LLM — prova de que o modelo não alucinorq
- Nenhuma solução concorrente brasileira tem isso a nível de SDK

### 9. Doc-Drift Shield — Contratos de Documentação Verificáveis
**Arquivo:** `docs/DOC_DRIFT_SHIELD.md` | **Sentinel:** `scripts/doc-drift-sentinel.ts`
- Todo número em README é um contrato com `last_value + proof_command` no `.egos-manifest.yaml`
- 4 camadas: manifest YAML + pre-commit + sentinel diário VPS + CCR semanal
- Derive de incidente real: Carteira Livre README dizia 54 páginas (real: 134), 68 APIs (real: 254)
- Tolerance rules por claim_type: percentages (±5%), counts (±10%), tech names (exact match)

### 10. World Model — Snapshot Estruturado para Raciocínio Causal de LLMs
**Arquivo:** `packages/shared/src/world-model.ts`
- JSON estruturado do estado do ecossistema, desenhado para LLM causal reasoning (não humanos)
- Alimenta o `/start` e a consciência dos agentes sobre o estado atual da plataforma
- Inclui: health%, P0 blockers, critical signals, top sprint tasks — carregado a cada sessão
- Padrão inovador: ecosystems-as-structured-data para multi-agent coordination

### 11. SIGNAL_MESH — Arquitetura de Coleta Intencional Anti-Poisoning
**Arquivo:** `docs/SIGNAL_MESH.md`
- 14 fontes simultâneas com orçamento definido ($15/mês)
- Cross-validation: Exa + arXiv + GitHub stars como triangulação anti-ruído
- arXiv penalty para papers sem código, PWC bonus para papers reproduzíveis
- Design explícito: "qual sinal, de onde, com qual confiança" — não descoberta aleatória

### 12. Auditable Sandbox Pattern — UX de Transparência Radical
**Arquivo:** `docs/patterns/AUDITABLE_SANDBOX_PATTERN.md` | **Live:** guard.egos.ia.br/sandbox
- 4 zonas na UI: Input → Processing → Result → Audit Trail (SHA-256 de cada passo)
- Usuário final vê o hash e pode verificar que o resultado não foi manipulado
- Padrão de produto (CAPABILITY_REGISTRY §13): reutilizável em todos os produtos EGOS
- Único "produto demo" que também é documento de arquitetura e prova de compliance

---

## 🚧 PRÓXIMOS PASSOS PRIORITÁRIOS

| Task | Produto | Esforço | Por quê agora |
|------|---------|---------|---------------|
| GH-092: Telegram inline keyboard | Gem Hunter | 6h | Fecha feedback loop |
| GH-093: scoring-feedback-reader cron | Gem Hunter | 6h | Self-improvement |
| GH-091: Qwen scoring gems gerais | Gem Hunter | 4h | Fix @zhuokaiz undervaluation |
| FORJA-003: RLS multi-tenant | FORJA | 8h | Desbloqueia pilot Rocha |
| KBS-004: FORJA namespace KB | KBS | 4h | Demo piloto |
| API-006: x402-mcp wrapper Guard | Guard Brasil | 6h | Monetização live |
| Apply gem_feedback migration | Infra | 30min | GH-092 depende disso |

---

## 📁 MAPA DE ARQUIVOS CRÍTICOS

| Arquivo | O que é |
|---------|---------|
| `TASKS.md` | SSOT de prioridades (1073 linhas) |
| `docs/CAPABILITY_REGISTRY.md` | Mapa de capacidades cross-repo |
| `docs/MASTER_INDEX.md` | Inventário universal (v1.3.0) |
| `docs/gem-hunter/SSOT.md` | Gem Hunter canonical |
| `docs/gem-hunter/prompts/scoring-v1.md` | Prompts de scoring versionados |
| `docs/strategy/KB_AS_A_SERVICE_PLAN.md` | KBS architecture |
| `docs/strategy/KBS_PATOS_DE_MINAS_PERSONAS.md` | 10 perfis de negócio |
| `docs/strategy/ERP_REPLACEMENT_NARRATIVE.md` | Sales narrative PT-BR |
| `docs/GTM_SSOT.md` | Go-to-market canônico |
| `packages/guard-brasil/src/guard.ts` | Guard Brasil facade |
| `agents/agents/gem-hunter.ts` | Gem Hunter runtime (2350 linhas) |
| `scripts/x-reply-bot.ts` | X.com bot |
| `scripts/auto-disseminate.sh` | Post-commit pipeline |
| `/home/enio/forja/TASKS.md` | FORJA tasks (standalone repo) |
| `~/.claude/CLAUDE.md` | Global rules (v3.1.0, 31 seções) |
| `.guarani/RULES_INDEX.md` | Governance entry point |

---

## 🔄 COMO ATUALIZAR ESTE DOCUMENTO

```bash
# Ao final de cada sessão, atualizar:
# 1. Seção "Últimas 48h" com novos commits
# 2. Status dos produtos (URLs + versões)
# 3. Tabela de infra (novos containers)
# 4. Próximos passos prioritários
# 5. Bump versão no header

# SSOT check:
grep "EGOS_STATE_OF_THE_ECOSYSTEM" docs/MASTER_INDEX.md  # deve existir
```

---

*Versão: 1.1.35 | Criado: 2026-04-08 | Atualizado: 2026-04-12************************************
