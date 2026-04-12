# EGOS — Catálogo de Ofertas (Inventário Real)

> **Version:** 1.0.0 | **Data:** 2026-04-12
> **Baseado em:** Scan completo de 16 repos, 14 npm packages, 45 agents, 400+ API routes
> **SSOT:** Este arquivo. Atualizar a cada nova capacidade verificada.

---

## Resumo Executivo

| Métrica | Quantidade |
|---------|-----------|
| Repositórios | 16 ativos |
| Pacotes npm publicados | 4 (@egosbr) |
| MCP servers próprios | 4 (knowledge, governance, memory, guard-brasil) |
| MCP servers externos ativos | 16+ (Notion, Gmail, Drive, Supabase, GitHub, Playwright, Exa, Brave, Firecrawl...) |
| Agents registrados | 45 (24 kernel + 21 lab) |
| API routes em produção | 350+ (852: 72, carteira-livre: 254, br-acc: 18 routers, egos-inteligencia: 27) |
| Scripts utilitários | 80+ |
| Domínios VPS live | 8+ (guard, hq, 852, gateway, waha, santiago, media, ratio) |
| Entidades Neo4j (br-acc) | 83.7 milhões |

---

## Ofertas por Camada

### 1. Knowledge Base Implementation (CORE — serve para TODOS)

**O que é:** Implementação de base de conhecimento com IA para qualquer profissional/empresa.

**Stack:**
- `@egosbr/knowledge-mcp` (9 tools) — search, ingest, lint, export, citations
- `scripts/kb-ingest.ts` — PDF, DOCX, MD, TXT (+ 11 formatos planejados)
- Guard Brasil PII scan automático no ingest
- Notion como interface (MCP nativo, zero código)
- CLAUDE.md setorial como "cérebro" do sistema
- Discovery Protocol para levantamento padronizado

**Para quem:** Qualquer profissional com base digital (advocacia, agro, médico, contador, delegacia, cooperativa, escola).

**Preço:** R$1.500-50k setup + R$200-5k/mês manutenção.

**Diferencial:** Guard Brasil LGPD + governança .guarani + entity extraction (KBS v2).

---

### 2. LGPD Compliance Layer (DIFERENCIAL COMPETITIVO)

**O que é:** Camada de compliance LGPD para qualquer sistema de IA.

**Stack:**
- `@egosbr/guard-brasil` (npm, 38 tests, 16 padrões PII BR)
- `@egosbr/guard-brasil-mcp` (3 tools para Claude Code)
- Guard Brasil REST API (guard.egos.ia.br, Stripe billing)
- Evidence Chain SHA-256 (provenance, receipts — LGPD Art. 37)
- ATRiAN ethical validation (score 0-100)
- Partial masking (banking-style: ***.456.789-**)
- Auditable Live Sandbox

**Para quem:** Qualquer empresa usando IA que processa dados pessoais BR.

**Preço:** Free tier (500 calls/mês) → Starter → Pro → Business → Enterprise.

---

### 3. Intelligence Platform (br-acc/egos-inteligencia — JÁ EXISTE)

**O que é:** Plataforma de inteligência com 83.7M entidades cruzadas.

**Stack:**
- Neo4j graph com 83.7M nós
- FastAPI com 27 routers (entity, search, graph, chat, investigation, analytics, patterns, ETL)
- ETL pipelines: BNMP, Datajud, PCMG-doc, PCMG-video
- Frontend Next.js (Intelink)
- Entity extraction, pattern matching, correlation

**Para quem:** Órgãos de segurança, inteligência, investigação, compliance.

**O QUE ISSO SIGNIFICA PARA KBS:** O entity extraction + relationship mapping do KBS-029/030 **já existe** no br-acc. Precisamos abstrair e modularizar para outros setores.

---

### 4. Civic Chatbot (852 — JÁ EXISTE)

**O que é:** Chatbot público com 72 rotas API, tool-calling, 27 tools.

**Stack:**
- Next.js com 72 API routes
- Chat streaming (Vercel AI SDK)
- Tool-calling (27 tools)
- Correlação de dados, extração, insights, dashboard
- Gamification (pontos, ranks, leaderboard)
- Upload, relatórios, notificações

**Para quem:** Qualquer organização que precisa de chatbot público com inteligência.

---

### 5. Chat-First ERP (Forja — JÁ EXISTE)

**O que é:** ERP conversacional para indústria.

**Stack:**
- Next.js, chat interface, WhatsApp, visão (câmeras/eventos)
- Tool execution, admin transparency, notifications

**Para quem:** PMEs industriais (metalurgia, manufatura).

---

### 6. Marketplace Platform (Carteira Livre — JÁ EXISTE)

**O que é:** Marketplace com 254+ rotas API.

**Stack:**
- Next.js, Asaas payments, WhatsApp, ambassador program
- Auth, admin, analytics completos

**Para quem:** Qualquer marketplace B2C no Brasil.

---

### 7. AI Governance Framework (ÚNICO NO BRASIL)

**O que é:** Framework completo de governança de IA testado em 12 repos.

**Stack:**
- `.guarani/` — engineering standards, preferences, rules index
- Pre-commit 9 fases (focus, secrets, typecheck, drift, evidence, PII, intelligence)
- SSOT gate (26 domínios), auto-disseminate, drift sentinel
- CLAUDE.md templates por projeto/setor/cliente
- Evidence-First principle (claim→proof chain)
- Doc-Drift Shield (4 layers: manifest, pre-commit, daily sentinel, LLM gate)

**Para quem:** Qualquer empresa que usa IA e precisa de auditabilidade, rastreabilidade, compliance.

---

### 8. Agent Orchestration (45 agents operacionais)

**O que é:** Runtime de agentes com event bus, registry, dry-run.

**Stack:**
- runner.ts + event-bus.ts (frozen, estável)
- agents.json registry (24 kernel + 21 lab)
- Agents especializados: wiki-compiler, drift-sentinel, article-writer, gem-hunter, dead-code-detector
- Master orchestrator, quota guardian, uptime monitor

**Para quem:** Empresas que querem automatizar operações com IA supervisionada.

---

## Mapa: O que serve para cada setor

| Setor | KB | Guard LGPD | Intelligence | Chatbot | ERP | Governance | Agents |
|-------|:--:|:----------:|:------------:|:-------:|:---:|:----------:|:------:|
| Delegacia/DHPP | ✅ | ✅ | ✅ (br-acc!) | ✅ (852) | — | ✅ | ✅ |
| Advocacia | ✅ | ✅ | ⚠️ (adaptar) | ✅ | — | ✅ | ⚠️ |
| Agronegócio | ✅ | ✅ | — | — | ⚠️ (Forja) | ⚠️ | — |
| Contabilidade | ✅ | ✅ | — | — | — | ✅ | — |
| Saúde | ✅ | ✅ (crítico) | — | ✅ | — | ✅ | — |
| Setor Público | ✅ | ✅ | ✅ (br-acc!) | ✅ (852!) | — | ✅ | ✅ |
| Metalurgia/Indústria | ✅ | ⚠️ | — | — | ✅ (Forja!) | ⚠️ | — |

---

## Descoberta crítica (2026-04-12)

**O br-acc/egos-inteligencia JÁ TEM o entity extraction + relationship mapping que planejamos para KBS v2.**

- 83.7M entidades no Neo4j
- 27 routers FastAPI (entity, graph, investigation, patterns, analytics)
- ETL pipelines para fontes públicas (BNMP, Datajud, PCMG)
- Frontend de visualização (Intelink)

**Isso significa:** não precisamos construir KBS-029/030 do zero. Precisamos **abstrair** o que já existe no br-acc para ser reutilizável por setor. O br-acc É o KB v2 para segurança/inteligência — só precisa de:
1. Interface simplificada (ChatGPT-like, não dashboard de analista)
2. Guard Brasil no pipeline (PII protection)
3. Knowledge MCP como camada de query (em vez de API direta)
4. Templates de entities por setor (delegacia ≠ advocacia ≠ agro)

---

*Catálogo vivo. Atualizar a cada nova capacidade verificada ou nova implementação.*
