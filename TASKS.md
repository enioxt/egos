# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.55.0 | **Updated:** 2026-04-08 | **NEW:** GH-089..097 (Gem Hunter Feedback Loop v8), XRB-001..004 (scoring quality), FORJA tasks → `/home/enio/forja/TASKS.md`, SAFETY-001..002, API-024 | **LAST SESSION:** Opus planned FORJA vision + feedback loop + API monetization complement. Execution starts now.
> **Philosophy:** Build what needs to be built, in the right order, without urgency.

---

### X.com Monitoring System (2026-04-07)
**SSOT:** `docs/social/X_POSTS_SSOT.md` | **Features Roadmap:** `docs/social/X_FEATURES_INTEGRATION_ROADMAP.md` | **Scripts:** `scripts/x-opportunity-alert.ts`, `scripts/x-approval-bot.ts`, `scripts/setup-x-monitoring.sh`
**Context:** Sistema completo de monitoramento de oportunidades X.com. Busca automática a cada 2h, alertas WhatsApp/Telegram, aprovação manual via bot. Integrando melhores features de ferramentas pagas (AutoTweet, TweetHunter, Hypefury) em solução própria self-hosted.

**✅ DONE 2026-04-07/08:** X-COM-001..005 (alert+approval bots, setup, SSOT templates, roadmap) | X-COM-018..024 (LLM analysis layer DashScope+OpenRouter, recordFeedback, HTML format, diagnostic — all in `scripts/x-opportunity-alert.ts`)

**P0 — Deploy + Core (Esta semana):**
- [x] **X-COM-008**: x-smart-scheduler.ts — análise de audiência para melhores horários
- [x] **X-COM-009**: x-evergreen-recycler.ts — recompartilhamento inteligente de top posts

**P1 — Growth (Próximas 2 semanas):**
- [ ] **X-COM-010**: Thread composer web — interface no HQ para criar threads
- [ ] **X-COM-011**: x-viral-library.ts — biblioteca de conteúdo viral por nicho
- [ ] **X-COM-012**: x-lead-crm.ts — tracking de leads no Supabase
- [ ] **X-COM-013**: Auto-DM sequences — workflow day 0/3/7 pós-aprovação

**P2 — Scale (Mês 2):**
- [ ] **X-COM-014**: Social listening avançado — Brand24-style monitoring
- [ ] **X-COM-015**: Analytics dashboard no HQ — heatmaps, métricas de crescimento
- [ ] **X-COM-016**: Auto-plug — promoção inteligente em tweets virais
- [ ] **X-COM-017**: Variations generator — A/B testing com LLM local (Gemma)

**P0 — Refinement (2026-04-08):**
- [ ] **X-COM-023**: Hermes integration — Agent para análise semanal e refinement automático de keywords
- [ ] **X-COM-024**: Templates DM específicos — OSINT/Investigação, AI/Framework, GovTech separados

---

### GovTech — Documentação de Oportunidades (2026-04-07)
**SSOT:** `docs/knowledge/GOVTECH_LICITACOES_ABERTAS_2026-04-07.md`
**Context:** Documentar licitações abertas para apresentar Eagle Eye e stack EGOS a potenciais parceiros. **NÃO participar de licitações diretamente** — falta habilitação completa (SICAF, atestados). Foco em documentar e prospectar parcerias com software houses habilitadas.

**Done (2026-04-07):**
- GOV-TECH-001: Levantamento de 7 licitações abertas com match técnico
- GOV-TECH-002: Template de proposta técnica reutilizável
- GOV-TECH-003: Pitch de parceria para software houses
- GOV-TECH-004: Análise SAAE Linhares — match perfeito com Evolution API

**P1 — Documentação + Parcerias (Esta semana):**
- [ ] **GOV-TECH-005**: Atualizar documento com novas licitações (monitoramento diário)
- [ ] **GOV-TECH-006**: Criar one-pager "Eagle Eye para Parceiros" (stack técnica)
- [ ] **GOV-TECH-007**: Identificar 5 software houses habilitadas para abordar
- [ ] **GOV-TECH-008**: Preparar deck de 5 minutos para calls de parceria

**P2 — Pilotos (Mês 2-3, se parceria confirmada):**
- [ ] **GOV-TECH-009**: Atestado técnico via piloto gratuito (após parceria)
- [ ] **GOV-TECH-010**: Registro SICAF (se viável economicamente)

**Nota:** Licitações identificadas são para documentação e apresentação a parceiros. Não executar propostas sem parceiro habilitado.

---

### OSINT Brasil — Toolkit & Matriz Operacional (2026-04-08)
**SSOT:** `docs/knowledge/OSINT_BRASIL_TOOLKIT.md` | **Matrix:** `docs/knowledge/OSINT_BRASIL_MATRIX.md` | **Keywords:** `docs/social/X_MOAT_KEYWORDS.md`
**Context:** Curadoria operacional de ferramentas OSINT focadas no Brasil, priorizando portais oficiais (Receita, Transparência, TSE), ferramentas ativas (Blackbird, Maigret, Sherlock), e conformidade LGPD/Marco Civil/LAI.

**Done (2026-04-08):**
- OSINT-001: `OSINT_BRASIL_TOOLKIT.md` — curadoria completa com 8 categorias de ferramentas
- OSINT-002: `OSINT_BRASIL_MATRIX.md` — matriz por objetivo (8 tipos de investigação)
- OSINT-003: `X_MOAT_KEYWORDS.md` — keywords e anti-keywords com contexto Brasil
- OSINT-004: Queries X.com otimizadas para policial/jurídico/dados públicos BR
- OSINT-005: x-opportunity-alert.ts v2.1 — enhanced MOAT keywords (10 categorias)

**P0 — Integração 852 (Esta semana):**
- [ ] **OSINT-006**: Mapear integração de Brasil.IO, Escavador, Jusbrasil na plataforma 852
- [ ] **OSINT-007**: Criar templates DM específicos para delegacias (PCMG, PMMG, PF)
- [ ] **OSINT-008**: Implementar alertas de vazamentos de dados (HIBP API) no Guard Brasil
- [ ] **OSINT-009**: Testar queries X.com policiais com conta de teste

**P1 — Automação & Alertas (Próximas 2 semanas):**
- [ ] **OSINT-010**: Script de monitoramento de diários oficiais (Querido Diário API)
- [ ] **OSINT-011**: Integração com Portal da Transparência para novos contratos
- [ ] **OSINT-012**: API wrapper para Receita Federal (CNPJ/CPF) — com cache e provenance
- [ ] **OSINT-013**: Alertas automáticos de novos processos (Escavador webhook)

**P2 — Avançado (Mês 2-3):**
- [ ] **OSINT-014**: Integração Maltego para visualização gráfica de vínculos
- [ ] **OSINT-015**: Plugin 852 para análise de metadados (ExifTool)
- [ ] **OSINT-016**: GEOINT module — TerraBrasilis + Sentinel Hub para casos ambientais

---

### API Marketplaces — Estratégia Multi-Plataforma EGOS (2026-04-08) [EXPANDED]
**SSOTs:** `/home/enio/.codeium/windsurf-next/AGENTCASH_OPPORTUNITY_ANALYSIS.md` | `/home/enio/.codeium/windsurf-next/API_MARKETPLACES_MASTER_ANALYSIS.md` | `/home/enio/.codeium/windsurf-next/API_MARKETPLACES_EXTENDED_RESEARCH.md`
**Context:** Pesquisa ampla (X/Twitter, Reddit, Web) identificou **20+ plataformas** em 5 camadas: Payment Protocols (x402, Stripe MPP), Agent-Native Marketplaces (0%), MCP Ecosystem (11,000+ servers, <5% monetizados), Web3/On-chain (Virtuals, ai16z, Sahara, Heurist, Talus), Traditional + Hybrid. Mercado projetado: **$52B até 2030**.

**Camada 1 — Payment Protocols:**
- **x402** (Coinbase + Cloudflare) — HTTP 402, USDC, 0%, Apache 2.0, Linux Foundation
- **Stripe MPP** (Stripe + Tempo) — Session-based, USDC + Fiat, enterprise focus, Mar 2026

**Camada 2 — Agent-Native Marketplaces (x402-first, 0%):**
- **AgentCash** — 300+ APIs, `agentwallet-sdk`, invite: `AC-LZR4-C5AX-F5DH-EAB2`
- **APINow.fun** — Tokenization endpoints + API coins, leaderboards
- **Proxies.sx** — 0%, 4G/5G proxies, bounties, ~95% take rate
- **ToolOracle** — 73 MCP servers, 708 tools, $0.01-0.08/call, AgentGuard security

**Camada 3 — MCP Ecosystem:**
- **Smithery** — 5,000+ servers, one-click install, gateway 6500
- **Glama** — 20,771 servers, SEO discovery (80% inbound)
- **MCP Hive, MCP Market, mcpservers.org** — Directories
- **TrueFoundry** — Enterprise gateway, RBAC, audit

**Camada 4 — Web3/On-chain:**
- **Virtuals Protocol** — Agent tokenization on Base, $VIRTUAL liquidity
- **ai16z / ELIZAOS** — AI-led VC DAO, Eliza framework
- **Sahara AI** — 40+ enterprise clients, AI marketplace
- **Heurist Mesh** — 25 providers, 100 tools, 40 agents, Web3 skills
- **Talus** — Sui blockchain, autonomous AI agents
- **Nevermined** — Visa + Coinbase integration, card rails

**Camada 5 — Traditional + Hybrid:**
- **RapidAPI** — 4M devs, 40k APIs, 20% commission
- **Replicate** — ML models, per-compute billing
- **DigitalAPI, API Layer, APYHub, Zyla** — Curated marketplaces

**P0 — Payment Protocols & x402 Onboarding (Esta semana):**
- [x] **API-001**: AgentCash onboard + testar consumer ✅ 2026-04-08
- [ ] **API-002**: APINow.fun — criar conta, explorar tokenization
- [ ] **API-003**: Proxies.sx — avaliar match OSINT scraping
- [ ] **API-004**: Análise x402 vs Stripe MPP — escolher primary protocol
- [ ] **API-005**: Criar wallet Base chain única para pagamentos

**P1 — MCP Ecosystem (Próximas 2 semanas):**
- [ ] **API-006**: Implementar x402-mcp wrapper (Vercel SDK)
- [ ] **API-007**: Submit Guard Brasil em Smithery (5,000+ servers)
- [ ] **API-008**: Listar em Glama (20,771 servers, SEO)
- [ ] **API-009**: Criar llms.txt para AI discovery
- [ ] **API-010**: Documentar X402_INTEGRATION.md

**P2 — Web3/On-chain (Mês 2):**
- [ ] **API-011**: Avaliar Virtuals tokenization para 852 Intelligence
- [ ] **API-012**: Submit skills ao Heurist Mesh (Web3 audience)
- [ ] **API-013**: Explorar Nevermined (Visa integration)
- [ ] **API-014**: Publicar OSINT Brasil wrappers (Brasil.IO, Escavador)
- [ ] **API-015**: ATRiAN Validator como compliance-as-a-service

**P3 — Traditional Scale (Mês 2-3):**
- [ ] **API-016**: RapidAPI provider account + freemium tiers
- [ ] **API-017**: Replicate — avaliar Gem Hunter como "model"
- [ ] **API-018**: DigitalAPI curated listing

**P4 — Otimização & Scale (Mês 3+):**
- [ ] **API-019**: A/B test pricing cross-platform
- [ ] **API-020**: Consolidar métricas revenue/usage/discovery (all platforms)
- [ ] **API-021**: Case study: "Guard Brasil: from local API to global agent marketplace"
- [ ] **API-022**: Avaliar criação API coins/tokens (APINow model)
- [ ] **API-023**: Stripe MPP integration (enterprise clients)

**Insights da Pesquisa (Atualizado 2026-04-08):**
- **30+ plataformas** identificadas em 5 camadas (Payment, Agent-Native, MCP, Web3, Traditional)
- 11,000+ MCP servers listados, **<5% monetizados** (oportunidade enorme)
- **xpay MCP**: Proxy wrapper para monetizar MCP servers sem code changes
- **ToolOracle**: 73 servers, 708 tools, 15% conversion free→paid via health_check discovery
- **Stripe MPP**: session batching para high-frequency (vs 1 TX/call x402)
- **Nevermined + Visa**: partnership abril 2026 — card rails tradicionais para agents
- **Hyperbolic**: GPU marketplace para AI agents (descentralized compute)
- **PinAI**: Personal AI Network — smartphone AI agents

**Diferenciais EGOS para Monetização:**
1. **Guard Brasil** — Único PII BR + LGPD art.11 (dados de saúde), zero competidores
2. **Gem Hunter** — Discovery engine 14 fontes (competidores têm 1-3)
3. **852 Inteligência** — Chatbot policial anônimo + ATRiAN (52 capabilities)
4. **ATRiAN** — Validação ética 90+ acrônimos policiais
5. **OSINT Brasil** — 12 ferramentas curadas + LGPD compliant
6. **X Opportunity** — Monitoramento X.com policial (23 queries)

**Documentos Consolidados:**
- `/home/enio/.codeium/windsurf-next/EGOS_API_MONETIZATION_COMPLETE.md` — Documento único 30+ plataformas
- `/home/enio/.codeium/windsurf-next/EGOS_DIFERENCIAIS_UNICOS.md` — Análise dos 6 diferenciais EGOS
- `/home/enio/.codeium/windsurf-next/ATRIAN_VS_GUARD_ANALYSIS.md` — ATRiAN vs Guard Brasil comparativo
- `/home/enio/.codeium/windsurf-next/API_MARKETPLACES_EXTENDED_RESEARCH.md` — Pesquisa ampla

**Recursos:**
- Awesome x402: https://github.com/xpaysh/awesome-x402
- x402 vs MPP (WorkOS): https://workos.com/blog/x402-vs-stripe-mpp
- MCP State 2026: https://settlegrid.ai/learn/state-of-mcp-2026
- xpay MCP: https://docs.xpay.sh/en/products/mcp-monetization
- ToolOracle: https://tooloracle.io/blog/how-to-monetize-mcp-servers-x402-usdc-micropayments

---

### Doc-Drift Shield Implementation (2026-04-07)
**SSOT:** `docs/DOC_DRIFT_SHIELD.md` | **Handoff:** `docs/_current_handoffs/handoff_2026-04-07_doc-drift-shield-plan.md`
**Context:** P33 discovered severe drift (Carteira Livre 54→134 pages +148%, BR-ACC 77M→83.7M Neo4j). 4-layer shield: L1 manifest + L4 CLAUDE.md §27 + L2 pre-commit + L3 VPS sentinel + L4 CCR module — ALL DONE (P33-P35).
**Done P33-P35 (2026-04-07):** doc-drift-verifier.ts, doc-drift-sentinel.ts, readme-syncer.ts, doc-drift-check.sh, agents.json (19 agents), manifests (br-acc/carteira-livre/852/forja/egos-lab/egos-inteligencia), MASTER_INDEX v1.3.0, governance-drift.yml CCR, manifest-generator.ts, .ssot-map.yaml (21 domains), ssot-router.ts (pre-commit step 5.7), X_POSTS_SSOT consolidation (5→1), doc-drift-analyzer.ts (L3.5)

**P1 — Pending:**
- [ ] **DRIFT-012**: Drift dashboard in hq.egos.ia.br showing status across all repos
- [ ] **DRIFT-013**: Integrate with Gem Hunter for third-party claim verification
- [ ] **SSOT-MCP**: Create `docs/MCP_SSOT.md` — consolidate 7 MCP_*.md files (MCP_DEPLOYMENT_CHECKLIST, MCP_ENV_VARS_REFERENCE, MCP_INTEGRATION_GUIDE, MCP_INTEGRATION_MAP, MCP_ORCHESTRATION_STRATEGY, MCP_SCOPE_POLICY, MCP_IMPLEMENTATION_SUMMARY)
- [ ] **SSOT-OUTREACH**: Migrate docs/outreach/ (8 files) → GTM_SSOT.md §partnerships
- [ ] **ARR-001**: Wire AAR (`@egos/search-engine`) into Gem Hunter content indexing (first activation use case)
- [ ] **ARR-002**: Wire AAR into KB wiki search (replaces raw grep in wiki-compiler)
- [ ] **ARR-003**: Hybrid retrieval pattern — AAR (precision/exact) + pg_trgm FTS (recall) for Guard Brasil + EGOS Inteligência. Validated by 2025 research (Meilisearch/Redis/Glean): full-text superior to vectors for identifier-heavy domains (CPF/CNPJ/PEPs/contracts). NOT a vector DB replacement.

### HQ Integration Masterplan (2026-04-07)
**Goal:** HQ shows live data for ALL 19 VPS containers — no service invisible, no number hardcoded.
**Diagnostic:** 2026-04-07 — hq.egos.ia.br covers 5/19 services. 14 containers invisible. Placeholder cards shipped (page.tsx + health/route.ts extended). Integration in 4 phases.
**SSOT:** `apps/egos-hq/app/page.tsx` + `apps/egos-hq/app/api/hq/health/route.ts`

**Phase 1 — Wiring internal services (health/route.ts already extended):**
- [ ] **HQI-001**: Eagle Eye → add counts from Supabase (territories, opportunities) via `/api/hq/eagle-eye` route
- [ ] **HQI-002**: 852 Police Bot → expose messages_today from 852-app internal API (find correct health endpoint)
- [ ] **HQI-003**: SINAPI → verify internal Docker URL + expose entry_count from DB
- [ ] **HQI-004**: br-acc/Neo4j → live node count via bolt (find creds in VPS docker-compose)
- [ ] **HQI-008**: OpenClaw real config → read actual fallback_chain from openclaw-sandbox (not hardcoded)

**Phase 2 — Volume mounts + data routes:**
- [ ] **HQV2-000**: VPS docker-compose: volume mounts → TASKS.md, agents.json, CAPABILITY_REGISTRY.md, docs/jobs/ → /data/*
- [ ] **HQV2-001**: `/api/hq/tasks` — parse /data/TASKS.md → `{total, pending, p0, p1, stale_p0}`
- [ ] **HQV2-002**: `/api/hq/world-model` — read /data/world-model/current.json → health%, blockers
- [ ] **HQV2-003**: `/api/hq/gems` — gem-hunter API → top gems, last run, sector breakdown
- [ ] **HQV2-004**: `/api/hq/drift` — read /data/jobs/doc-drift-sentinel.md → structured drift per repo (DRIFT-012)

**Phase 3 — New dashboard pages:**
- [ ] **HQV2-006**: `/tasks` page — Kanban P0/P1/P2, done/pending counts (dep: HQV2-001)
- [ ] **HQV2-007**: `/world-model` page — health% gauge, P0 blockers, agent inventory
- [ ] **HQV2-008**: `/gems` page — filterable cards (score, source, category)
- [ ] **HQV2-009**: `/system-map` page — D3 graph from agents.json + CAPABILITY_REGISTRY
- [ ] **HQV2-010**: Nav update — add tasks, world-model, gems, system-map, drift links

**Phase 4 — Intelligence + Dream Cycle:**
- [ ] **DC-007**: HQ "Last Night" card — Dream Cycle results from egos_nightly_logs
- [ ] **HQC-012**: Intelligence engine — `intelligence-engine.ts` + Gemma 4 31B free → auto-task creation
- [ ] **GRF-002**: Knowledge Graph panel — vis.js embed from codebase-memory-mcp
- [ ] **ORB-004**: Orchestration Status widget — MCP server health (brave, github, filesystem, etc.)
- [ ] **HQC-011**: Remove all remaining hardcoded data — drive from canonical registries

---

### P2 — SSOT Limpeza / Misc
- [ ] **CLEAN-001..004 [P2]**: XCOM→GTM_SSOT, X_POST_PROFILE→delete, outreach/→GTM_SSOT §partnerships, sales/→MONETIZATION_SSOT
- [ ] **EGOS-132 [P2]**: Resolve brand conflict: BRAND_CANONICAL.md (kernel) vs egos-lab/branding/BRAND_GUIDE.md
- [ ] **DOC-005 [P2]**: Remove `Sacred Code`/`Frozen Zones` from legacy governance docs

---

**Archive (P1-P26):** EGOS-151..176, MONETIZE-001..015, KB-001..018, GH-001..071, X-001..008, THEATER, WA, EAGLE, GOV, BRACC, PART — all ✅. Products: Guard Brasil v0.2.2 API+web+npm, Gateway v0.3.0, Gem Hunter dashboard, HQ, Eagle Eye, KB. Codex/OpenClaw/billing proxy decommissioned 2026-04-08 → DashScope+Hermes.

### Guard Brasil Monetization Roadmap

**Completed:** EGOS-151..161, MONETIZE-001..015, EGOS-162/164 — all DONE ✅ (see archive)

**P1 — Remaining:**
- [ ] EGOS-163: Pix billing integration

**P2 — Growth:**
- [ ] EGOS-165: White-label outreach
- [ ] EGOS-166: REST API gateway mode

---

### HQ Completion Program (2026-04-06)
**SSOT:** `docs/MASTER_INDEX.md` + `docs/SSOT_REGISTRY.md` + `docs/SYSTEM_MAP.md`
**Goal:** HQ becomes the non-hardcoded control plane for verified ecosystem reality.

**P0 — Truth normalization + /start evidence:**
- [ ] **HQC-004**: Add kernel SSOT pointers to `852`, `br-acc`, `carteira-livre`, `forja`, `egos-lab`; audit `policia`, `INPI`, `commons`

**P1 — Wiring + contracts:**
- [ ] **HQC-008**: Complete MCP setup gaps (obsidian, stripe, telegram) and make HQ consume installation truth
- [x] **HQC-009**: DUPLICATE of GTM-016 — guard-brasil-mcp package already exists
- [ ] **HQC-010**: Configure OpenClaw Gateway / WhatsApp / Telegram path without duplicated orchestration
- [ ] **HQC-011**: Remove hardcoded HQ data dependencies and drive HQ from canonical registries (`TASKS.md`, `agents.json`, `validation.json`, `CAPABILITY_REGISTRY.md`, `MASTER_INDEX.md`)
- [ ] **HQC-012**: Build `intelligence-engine.ts` and connect Dream Cycle outputs to HQ

**P2 — Ecosystem consolidation:**
- [ ] **HQC-013**: Fix HARVEST/KB dedup and freshness so HQ can trust knowledge surfaces
- [ ] **HQC-014**: Archive 11 dormant repos and close Santiago fix-or-kill
- [ ] **HQC-015**: Execute egos-lab kernel consolidation wave (`LAB-ARCHIVE-001..006`)

---

**Infra+Init DONE:** Neural Mesh telemetry ✅, codebase-memory-mcp 51K nodes ✅, KB wiki-compiler 50 pages ✅, CCR 3 jobs ✅
- [ ] **KB-017 [P2]**: Auto-learning from git commits | EGOS-169: @aiready/pattern-detect | EGOS-173: CRCDM auto-heal rename

---

### Eagle Eye — OSINT Licitações LIVE
**eagleeye.egos.ia.br** | 84 territories | 121 opportunities | daily cron 9am BRT
**Done (EAGLE-000..023):** standalone Docker, Supabase 6 tables, 26 detection patterns, Telegram alerts, PNCP enrichment, 80 territories seeded, integrador 70/30 channel doc, daily cron, real pipeline (36 opps R$10.5M).
- [ ] EAGLE-009: Stripe/Pix for Pro tier (R$497/mo)
- [ ] EAGLE-019: Integrador partnership outreach
- [ ] EAGLE-020: R$250k proposal — deadline 2026-04-29
- [ ] EAGLE-GH-003..010: Classification + extraction + profile + API v2 + MCP + Pix
- [ ] SANT-001: Santiago partner onboarding (MVP ready, waiting partner)

---

### Gem Hunter v6 — Research Discovery Engine LIVE
**CCR:** seg+qui 2h37 BRT | **Standalone API:** port 3097 | **npm:** @egosbr/gem-hunter v6.0.0
**Done (GH-001..066):** /study+/study-end skills, pair studies (Continue 71/100, Aider 74/100, Cline 72.8/100), PWC pipeline, Papers Without Code, KOL discovery, Telegram+Discord alerts, BRAID GRD, X-reply-bot (VPS hourly cron), ArchitectureSelector, cost-tracker, world-model signals, gem-hunter-server API, pricing.ts, Gateway /gem-hunter channel.

**Active — Pair Studies Queue:**
- [ ] GH-013: EGOS OpenHands | GH-014: EGOS LangGraph | GH-015: EGOS OpenAI Agents SDK | GH-016: EGOS LiteLLM | GH-017: EGOS Langfuse
- [ ] GH-020: EGOS Mem0 | GH-021: EGOS Temporal | GH-022: EGOS Haystack | GH-023: EGOS DSPy | GH-036: OpenHarness adapter

**Active — Product:**
- [ ] GH-025: `/pr` workflow + GitHub App (pre-merge gate)
- [ ] GH-026: Upgrade codebase-memory-mcp to HTTP/SSE transport
- [ ] GH-027: `.guarani/checks/` layer
**Gem Hunter product (revenue):**
- [ ] GH-073: Weekly email digest

**Gem Hunter CCR:**

**P1 — Reference Repo Study Queue (priority order):**
- [ ] GH-013: EGOS OpenHands (`OpenHands/OpenHands`) — full software agent SDK/CLI/GUI
- [ ] GH-014: EGOS LangGraph (`langchain-ai/langgraph`) — stateful long-running agents, durable execution
- [ ] GH-015: EGOS OpenAI Agents SDK (`openai/openai-agents-python`) — handoffs, guardrails, tracing
- [ ] GH-016: EGOS LiteLLM (`BerriAI/litellm`) — multi-model proxy, cost tracking, routing
- [ ] GH-017: EGOS Langfuse (`langfuse/langfuse`) — observability, prompt versioning, evals

**Aider study done (GH-031..039):** pre-edit-safety hook, CLAUDE.md §13 model guide, OpenHarness early-warning, Telegram gem alerts, BRAID Mode GRD, x-reply-bot VPS cron. Details: git log.
- [ ] GH-032: EGOS edit benchmark (SWE-Bench inspired, 20 tasks)
- [ ] GH-036: OpenHarness adapter in packages/shared/harness/

**Gem Hunter v5.1+v6.0 DONE (GH-043..065):** PWC pipeline, low-star scoring, ArchitectureSelector adapter, structural validation, auto-queue, signals ingestion, Papers Without Code, KOL discovery, evolution engine, multi-LLM fallback, Telegram alerts, multi-stage paper pipeline, cost budgeting, standalone API, MONETIZATION_SSOT, pricing.ts, gem-hunter npm v6.0.0. Details: git log.

*Month 2-3 — Product Scale:*
- [ ] GH-063: x402 pay-per-call — M2M agent payments via x402 protocol
- [ ] GH-067: Deploy gem-hunter-server to VPS (gemhunter.egos.ia.br) + Caddy routing → P0 revenue
- [ ] GH-070: Chatbot orchestrator — WhatsApp channel NLP intent → tool calls → gem-hunter → curated reply
- [ ] GH-072: Chatbot tier enforcement (200 queries/mo for R$149/mo chatbot plan)
- [ ] GH-073: Email digest — weekly top 10 gems to subscribers
- SSOT: docs/gem-hunter/GEM_HUNTER_PRODUCT.md

**P2:** GH-020..024 (Mem0, Temporal, Haystack, DSPy, Lego Assembler) — post PMF.

---

### Claude Code Hardening + Observability (archived)
LEAK/AI/OBS 001..013 done. P2 pending: LEAK-010..012, AI-008..010, OBS-010..013. Ref repos: Continue 71, Aider 74, Cline 72.8, agent-scaling-laws 87. P1 queue: OpenHands, LangGraph, OpenAI Agents SDK, LiteLLM, Langfuse, Mem0.

---

### X.com Presence (2026-04-01)
**BLOCKER:** XMCP-001 (X credentials 401 — regenerate at developer.twitter.com first)
- [ ] X-009: Trending topic scanner (hourly, keywords vs capabilities)
- [ ] X-012: Thread scheduler (multi-tweet, 2-min gaps) — dep XMCP-001

---

### Block Intelligence + Eagle Eye (compressed)
**WM-001..008:** Local LLM + world model (P2, post-PMF). **INTEL-006..010:** Proactive detection, mermaid, DRI auto-assign (P1-P2). SSOT: `docs/strategy/WORLD_MODEL_SSOT.md`
**Eagle Eye v2:** EAGLE-GH-001..005 done. P0: GH-003/004 (classification/extraction). Deadline: EAGLE-023 R$250k proposal 2026-04-29.
- [ ] MONETIZE-011: Deploy v0.2.3 to VPS with STRIPE_METER_ID env var
- [ ] MONETIZE-012: NOWPayments webhook URL config — ENIO action required

### Partnership & Distribution Strategy (2026-04-05)
**Compressed:** See `docs/GTM_SSOT.md` + `docs/MONETIZATION_SSOT.md` for full roadmap.
- [ ] **PART-001**: Publish npm + ProductHunt (M-007 emails first)
- [ ] **PART-016**: Decide PARTNER-D1 co-founder model

---

### Evaluated & Deferred (2026-04-05)
**HiClaw:** SKIP. **PAL:** ADOPTED partial (wiki-compiler). **Karpathy LLM Wiki:** ADOPTED full (KB-001..007). **Fine-tuning Gemma/Qwen:** DEFERRED to P2 (no GPU, not 90-day focus).

### GTM & Incidents (P25-P35)

**SSOT:** `docs/GTM_SSOT.md` | **ICP:** CTOs/backend devs at fintechs+healthtechs (confirmed).  
**INC-001 (2026-04-06):** Force-push incident — recovered. Mitigations: `.husky/pre-push` blocks, GitHub branch protection enabled, CLAUDE.md §25 added.

**P0 — Social & Outreach:**
- [x] **GTM-002**: X.com thread demo (4 tweets, drafts ready) — aguarda XMCP-002 start.sh ✅ 2026-04-08
- [ ] **GTM-001**: x-reply-bot search tuning (lgpd/anpd/dpo keywords)

**Guard Brasil Bugs — Status (2026-04-07):**
- [/] **GUARD-BUG-002**: ATRiAN bias **não existe no código**. Demo corrigido para mostrar o que funciona (absolute_claim, fabricated_data). Feature futura.

**P1 — Content & Integrations:** GTM-006..013 (docs playground, ProductHunt, dev.to, partnerships) — see git log for status.

---

### HQ Dashboard v2 (2026-04-06)
**Goal:** Mission Control shows full system state. **Prereq:** Volume mounts on VPS (data → /data/).
- [ ] **HQV2-000 [P0]**: Docker volume mounts (TASKS.md, world-model/, gem-hunter/latest-run.json, agents.json, CAPABILITY_REGISTRY.md → /data/*)
- [ ] **HQV2-001..005 [P1]**: API routes — tasks, world-model, gems, system-map, gtm
- [ ] **HQV2-006..010 [P2]**: Dashboard pages — /tasks Kanban, /world-model gauge, /gems cards, /system-map D3, nav update

---

### P26 — MCPs + Focus v2.0 (2026-04-06)

**Completed:**

**Pending:**
- [ ] MCP-005: Obsidian MCP — needs vault path from Enio (`setup-obsidian-mcp.sh` ready, smithery CLI)
- [ ] MCP-006: Stripe MCP (`@stripe/mcp`) — needs Stripe secret key (on VPS only)
- [ ] MCP-007: Telegram MCP (`mcp-telegram`) — needs bot token
- [ ] MCP-008: Move `egos-knowledge` MCP from `egos/.claude/settings.json` → `~/.claude/settings.json` (make global)
- [/] GTM-016: `guard-brasil-mcp` package EXISTS at packages/guard-brasil-mcp/ — needs npm publish + Claude tool registration — wraps guard.egos.ia.br as Claude tool, publish as `@egosbr/guard-brasil-mcp` (GTM play: devs install it in their Claude session)
- [x] KB-019: `bun wiki:dedup` ✅ command exists in package.json — fix HARVEST.md 1944-line triplication caused by wiki:compile running without dedup

---

### Dream Cycle — Overnight Intelligence (2026-04-06)
**SSOT:** `docs/strategy/DREAM_CYCLE_SSOT.md`
**Goal:** Wake up to briefed HQ showing all nightly work. LLM cost: $0 (Gemma 4 31B free).

**Phase 2 — Intelligence (pending):**
- [ ] DC-004: `agents/agents/intelligence-engine.ts` — reads nightly logs + TASKS.md, uses Gemma 4 31B, writes egos_nightly_reports + auto-creates TASKS entries
- [ ] DC-005: Extend CCR Governance Sentinel to run intelligence-engine after drift check
- [ ] DC-006: Auto-Healer script — restart containers on known patterns (rule-based, no LLM)
- [ ] DC-011: Tune log-harvester Caddy pattern (false-positive: 472 TLS entries flagged as critical)

**Phase 3 — HQ Integration:**
- [ ] DC-007: HQ "Last Night" card on home page — shows Dream Cycle results from egos_nightly_logs
- [ ] DC-008: HQ `/events` page (CTRL-014) — real-time stream from egos_agent_events + nightly reports
- [ ] DC-009: Morning Briefing (06h30 BRT) — Telegram + WhatsApp summary of overnight work

---

### Skills + Hooks Backlog (2026-04-06)

**Skills:**
- [ ] SKILL-001: `/gate` — manual quality gate scoring (G1-G5 template from .guarani/orchestration/GATES.md). Create `~/.claude/commands/gate.md`
- [ ] SKILL-002: `/mycelium-think` — thinking meta-prompt (different from /mycelium VPS check). Create `~/.claude/commands/mycelium-think.md`
- [ ] SKILL-003: `/brainet` — sync content from .guarani/prompts/meta/brainet.md (if outdated). Verify ~/.claude/commands/brainet.md exists.

**Hooks:**
- [ ] HOOK-001: `~/.claude/hooks/skill-auto-trigger` — UserPromptSubmit hook that detects keywords from .guarani/prompts/triggers.json (7 triggers: strategy, brainet, mycelium, audit, debate, extraction, activation) and injects meta-prompt content as context
- [ ] HOOK-002: `~/.claude/hooks/refinery-gate` — UserPromptSubmit hook for vague prompts (<50 chars) or risky keywords (deletar/remover/migrar/deploy/produção) → inject clarification guidance from .guarani/refinery/classifier.md

---

### ~~OpenClaw~~ — DECOMMISSIONED 2026-04-08 (OC-006..034 CANCELED). Replaced by DashScope qwen-plus + OpenRouter free fallback + Hermes systemd. Channels via Evolution API + egosin_bot.

---
 
 ### Self-Discovery Product (2026-04-06)
 **SSOT:** `docs/SELF_DISCOVERY_ARCHITECTURE.md` | self.egos.ia.br → VPS | B2C wellness (não medical device)
- **Execution order:** SD-001 → 002 → 003 → 004 → 005 → 006/007/008 → 009 → 010..019
- **Named gates:** `deploy` = SD-006 | `security` = SD-007 | `ux` = SD-008 | `launch` = SD-009
- [ ] **SD-001..009 [P0]**: Inventory (001) → boundaries (002) → env contract (003) → Dockerfiles spec (004) → proxy spec (005) → gates: deploy (006) / security (007) / ux (008) / launch (009). Full detail: `docs/SELF_DISCOVERY_ARCHITECTURE.md`.
- [ ] **SD-010..014 [P1]**: ICP + pricing hypothesis (010), landing scope (011), pattern taxonomy (012), onboarding flow (013), analytics signals (014). [DEP: SD-009]
- [ ] **SD-015..019 [P2]**: Post-alpha — pattern packs, auth/history, API docs, TS migration, freeze backlog.

### VPS Infrastructure Optimization & Resource Management (P34-P35)

**Investigation Complete (2026-04-07):** Full VPS audit reveals healthy infrastructure (19 containers stable, 23 agents active, 9-day uptime) but critical RAM pressure (622MB free / 15GB total). Neo4j BR-ACC consuming 4.8GB (31.5% of total). `/opt/backups/` = 15GB of dated Neo4j dumps (2026-04-03/04/05). Decision: Keep BR-ACC online as production SSOT; clean backups; implement intelligent resource management before Hermes MVP.

**SSOT:** `/home/enio/.egos/memory/mcp-store/vps_hetzner_complete_infrastructure_map_2026-04-07.md` | **Handoff:** docs/_current_handoffs/handoff_2026-04-07_doc-drift-shield-plan.md §2

**P1 — Infrastructure Baseline (P35):**

- [ ] **VPS-CAPACITY-001**: Create capacity planning model — given: current 19 containers, Neo4j 4.8GB, how much RAM remains for Hermes+Codex? Simulate: "if we add X, what breaks?" [OWNER: arch, 2h]
- [ ] **VPS-SWAP-001**: Add 4GB swap partition if cleanup + Neo4j tuning insufficient. Benchmark: does swapping kill performance? (defer if not needed) [OWNER: infra, P1]

---

### Hermes MVP Deployment (P35 — Proposed Start 2026-04-08)

**Investigation Complete (2026-04-07):** Hermes Agent (24/7 executor framework) ready for MVP. Design documented. Deployment path clear. ✅ **RAM cleanup DONE (VPS-BACKUP-001).** ROI: R$0-40/month marginal cost, unlocks always-on research + self-improving skills. Risk: Low (can remove in 1h if needed). Trial period: 1 week, go/no-go gate at 2026-04-19.

**SSOT:** `/home/enio/.egos/memory/mcp-store/hermes_agent_investigation_deep_dive_2026-04-07.md`

**✅ HERMES-001..004 DONE (2026-04-07/08):** systemd service (hermes-gateway) running 142MB RAM. DashScope qwen-plus primary, OpenRouter gemma-4-26b free fallback. Codex/OpenClaw/billing proxy decommissioned.

**Phase 5: Trial (2026-04-07 through 2026-04-15)**
- [ ] **HERMES-005-P1**: Run production trial — Hermes stays online 7 days. Measure: uptime, RAM usage, token consumption, error rate. [Owner: infra, monitoring]
- [ ] **HERMES-005-P2**: Validate: At least 1 auto-generated skill created and persisted to SQLite. Test invoking skill. [Owner: infra]
- [ ] **HERMES-005-P3**: Cost tracking — capture actual token spend vs estimate (R$0-10 for trial week expected). [Owner: infra]
- [ ] **HERMES-005-P4**: Decision gate (2026-04-15): Go/no-go for scaling to 6 profiles. If YES → P35 scope expands. If NO → remove, document learnings. [Owner: Enio]

**P1 — Scaling (P35+ Post-MVP):**

- [ ] **HERMES-006**: Scale to 6 profiles (egos-kernel, egos-strategy, egos-governance, egos-research, egos-ops, egos-learning) — one per domain. [DEP: HERMES-005-P4 go]
- [ ] **HERMES-007**: Integrate Hindsight SDK (persistent memory + world-model sync) — enables GEPA self-improvement. [DEP: HERMES-006]
- [ ] **HERMES-008**: Connect Gem Hunter v7 as Hermes job — automate cross-repo discovery runs. Cron: `0 2 * * * hermes task --profile egos-kernel "analyze-cross-repo-patterns"`. [DEP: HERMES-006 + GEM_HUNTER_V7]
- [ ] **HERMES-009**: Add watchdog for Hermes itself — if process dies, auto-restart. Alert via Telegram. [DEP: HERMES-006]

---

### VPS Orchestration — DashScope + Hermes + Gemini CLI (P35)

**2026-04-08:** Codex + OpenClaw + Billing proxy DECOMMISSIONED. Engine: DashScope qwen-plus (primary) + OpenRouter free (fallback). Hermes systemd running.

- [ ] **ORB-003**: Cost attribution per task → Supabase [dev, 3h]
- [ ] **ORB-004**: HQ widget "Orchestration Status" [UI, 2h]

---

### Gem Research — P31 (2026-04-06): Graphify + A-Evolve + XMCP
**Source:** Grok analysis. Decisions: Graphify=adopt patterns only (codebase-memory-mcp overlap 80%); A-Evolve=bookmark pós PMF; XMCP=install now.

**XMCP — X MCP Server oficial (xdevplatform/xmcp):**
- [x] **XMCP-002**: Keys regeneradas e .env atualizado ✅ 2026-04-07. Serviço iniciado ✅ 2026-04-08 — PID 802844, port 8200, VPS 204.168.217.125. Dois patches em server.py: (1) usar tokens existentes ao invés de OAuth flow, (2) load_env() antes de ler MCP_PORT.
- [ ] **SOCIAL-003 [P1]**: x-reply-bot — busca por "LGPD", "licitação", "split payment", "análise de vínculos"
- [x] **SOCIAL-004 [P1]**: X Post HITL bot live ✅ 2026-04-08 — 3 alternatives + Telegram inline keyboard + choice learning (x_post_options, x_post_choices, x_post_preferences tables). VPS daemon running.
- [ ] **SOCIAL-005 [P2]**: Reply automático a @mentions com link produto relevante (aprovação manual)
- [ ] **SOCIAL-006 [P2]**: HQ dashboard tab social — candidatos DM, DMs enviadas, respostas
- [x] **XMCP-003** (dep: XMCP-002): UFW rules adicionadas (172.19.0.0/16 + 172.17.0.0/16 → port 8200). ✅ 2026-04-08
- [x] **XMCP-004** (dep: XMCP-002): Criar skill `egos-x-researcher` — usa XMCP searchPostsRecent para monitorar: lgpd, anpd, dpo, "proteção de dados". Saída → Supabase + HQ. ✅ 2026-04-08

**Graphify patterns (adotar sem instalar a lib):**
- [ ] **GRF-001 (P2)**: Criar CCR job `graph-report` — usa codebase-memory-mcp query_graph para gerar GRAPH_REPORT.md semanal (god nodes, surprising connections, clusters). Output em `docs/jobs/`.
- [ ] **GRF-002 (P2)**: Embutir graph.html (vis.js) no HQ como painel "Knowledge Graph" — feed de codebase-memory-mcp export. Parte de HQV2-009.
- [ ] **GRF-003 (P2)**: Adicionar ingestão multimodal ao wiki-compiler: PDFs + papers → Supabase `egos_wiki_pages`. Usa Graphify padrão (PDF→AST→nodes).

**A-Evolve patterns (bookmark pós PMF):** AEV-001..002 (P3) — manifest.yaml per skill + evolution loop. See git log for design.

### Governance Mesh Cleanup (2026-04-06 audit)
- [ ] **GOV-001**: CLAUDE.md → thin adapter to `.guarani` kernel [constitution drift]
- [ ] **GOV-002**: Unify workflow catalog (.windsurf/workflows + ~/.egos/workflows + workflow-sync-check.sh)
- [ ] **GOV-003**: Canonical skill distribution ~/.egos/skills vs ~/.claude/skills
- [ ] **GOV-004**: manifest.json SSOT hierarchy → kernel-first `.guarani`
- [ ] **GOV-005**: settings.local.json allowlist audit — hardcoded tokens, unsafe legacy permissions
- [ ] **GOV-006**: Sanitize stale ~/.egos artifacts (.windsurfrules, SSOT_STATUS_20260328.txt)
- [ ] **GOV-007**: Unify repo mesh registry (sync.sh + sync-all-leaf-repos.sh + manifest.json)

### Ratio Collaboration (2026-04-07) — PR #1 open, Guard Brasil wired
**Context:** Fork `enioxt/ratio` — Carlos Victor Rodrigues, Brazilian legal RAG + LangGraph drafting. Goal: PRs that demonstrate EGOS assets and open organic partnership. Branch: `feat/escritorio-multi-provider-llm`, PR #12 (103 tests passing).

**Done:** llm_provider 4 providers ✅ | pii_guard Guard Brasil ✅ | planning id-coercion ✅ | bot review issues ✅ | live pipeline 4/4 ✅ | frontend local ✅

- [ ] **RATIO-001 [P1]**: Submit PR #2 (Guard Brasil) as separate branch after PR #1 merged. Branch: `feat/escritorio-pii-guard`. LGPD compliance, fail-open, 8 tests.
- [ ] **RATIO-002 [P1]**: Open Issue on Carlos's repo re: LGPD gap (fatos_brutos with CPF → Gemini unmasked). Offer Guard Brasil free tier. Frame constructively. Metric: Carlos responds.
- [ ] **RATIO-003 [P2]**: br-acc entity resolution adapter — `entity_resolver.py` + `resolve_parties()` in intake. Maps party names → CPF/CNPJ/OAB/process history via br-acc API. PR #3.
- [ ] **RATIO-004 [P2]**: `.ratio-manifest.yaml` Doc-Drift Shield adoption PR. Claims: `total_documents: 471366`, `lancedb_store_gb: 8.5`. Verified via LanceDB count.
- [ ] **RATIO-005 [P2]**: Full end-to-end test via API with Caso 1 (STJ PDF real) → intake → planning → redaction → adversarial → formatter → download DOCX.
- [ ] **RATIO-006 [P3]**: Draft br-acc API pricing model for Carlos (free 100 lookups/mês + paid). Monetization path proposal.

### Ratio VPS Deployment (2026-04-07) — DONE: ratio-api:3085 + ratio-frontend:3086 live. Caddy: ratio.egos.ia.br + ratio-api.egos.ia.br. Guard Brasil PII enabled.


### Chatbot SSOT v2.0 — World-Class Upgrade (2026-04-07)
**Context:** Opus investigation complete. 16 modules (8 upgraded + 8 new). Dual-runtime TS+Python. Disseminate to 852/br-acc/egos-web/ratio/intelink/forja.
**SSOT:** `docs/modules/CHATBOT_SSOT.md` | **Arch decisions:** Vercel AI SDK v4+, LangGraph (Python), JSON Schema source-of-truth for TS↔Py parity, OTel+Supabase dual telemetry.

**✅ CHAT-001..010 DONE:** 001 ATRiAN stream | 002 SSOT v2 | 003 prompt-assembler | 004 PII scan | 005 MemoryStore | 006 circuit breaker | 007 abort | 008 per-identity budget | 009 eval 20 golden | 010 egos-web 90+

**P1 — CHAT-011..022:** structured output, multimodal Message, runAgentLoop, semantic memory, OTel, prompt caching, cost ledger, Python shared_py, br-acc/ratio adoption, conformance test, streaming PII
**P2 — CHAT-023..031:** resumable streams, fork/edit, agent handoff, eval CI gate, file ingest, entity memory, racing fallback, Forja/Intelink/carteira-livre pass, HQ panel

---

### Memory Intelligence — MemPalace + ARR Activation (2026-04-07)
**Context:** MemPalace (96.6% R@5, MIT, local ChromaDB, 13.8k stars em 2 dias) resolveu o mesmo problema que nosso ARR (dormant desde ARR-001). CORAL (arXiv 2604.01658, MIT) prova: 50%+ dos breakthroughs vêm de reutilização de conhecimento entre agents. Nenhum dos dois está ativo no EGOS hoje.
**SSOT:** `packages/shared/src/cross-session-memory.ts` + `.guarani/mcp-config.json`

- [ ] **MEM-001 [P1]**: Benchmark MemPalace. `pip install mempalace`, `mempalace mine --mode convos` nas últimas sessões Claude Code. Comparar R@5 vs file-based memory (`memory/*.md`). Critério de avanço: R@5 ≥ 80%. [2h]
- [ ] **MEM-002 [P1]** (dep: MEM-001 pass): Mapear Palace structure para domínios EGOS. Wings = repos (egos, egos-lab, 852, br-acc, ratio). Rooms = domínios (guard-brasil, hq, gem-hunter, licitações, governance). Documentar em `docs/MEM_PALACE_SSOT.md`. [2h]
- [ ] **MEM-003 [P1]** (dep: MEM-001 pass): Adicionar `mempalace-mcp` ao `.guarani/mcp-config.json`. Expor 6 tools: mine, wake-up, search, add, list-wings, get-room. Configurar auto-detect de wings a partir dos repos. [2h]
- [ ] **MEM-004 [P2]** (dep: MEM-003): Migrar handoffs anteriores para MemPalace. `mempalace mine --mode general` nos `docs/_current_handoffs/` + `memory/*.md`. Verificar retrieval de decisões-chave (INC-001, LGPD pricing, Docker network). [1h]
- [ ] **GTM-X-001 [P1]**: Thread X.com sobre MemPalace + CORAL (trending agora — 13.8k stars). `bun scripts/rapid-response.ts --topic "MemPalace CORAL memory agents"`. Ângulo: "EGOS já tem governance layer que ambos precisam — LGPD + evidence-first." [1h — UNBLOCKED após XMCP-001]

---

### CORAL Pattern — Shared Agent Discovery Store (2026-04-07)
**Context:** CORAL (MIT, arXiv 2604.01658) mostra que agents compartilhando descobertas = 50%+ dos breakthroughs. Gem Hunter hoje: cada run é isolado, zero memória entre runs. Padrão a adotar (não o framework completo): tabela `gem_discoveries` + agents consultam antes de explorar.
**SSOT:** `agents/agents/gem-hunter.ts` + `packages/shared/src/event-bus.ts`

- [x] **CORAL-001 [P1]**: Criar tabela Supabase `gem_discoveries`. Schema: `{id, repo_url, gem_name, category, score, discovered_by, discovered_at, summary, tags[], last_seen_at}`. RLS habilitado. Migration em `supabase/migrations/`. ✅ 2026-04-08
- [x] **CORAL-002 [P1]** (dep: CORAL-001): Modificar Gem Hunter stage-1 para consultar `gem_discoveries` antes de scrape. Skip repos score ≥ 7 nos últimos 14 dias. Log: "X repos skipped (already discovered)". Esperado: 30-50% redução em API calls. [3h] ✅ 2026-04-08
- [x] **CORAL-003 [P2]** (dep: CORAL-001): Hermes escreve em `gem_discoveries` após research tasks. Qualquer agent que encontrar "gem" (tool/pattern relevante) chama `event-bus.ts` → upsert `gem_discoveries`. [2h] ✅ 2026-04-08

---

### GovTech — Licitações de Software (2026-04-07)
**Context:** Mercado govtech software BR = ~R$20-30bi/ano em prefeituras/estados (FATO: Intercept/UFSM 2025). Big techs dominam federal via inexigibilidade. Janela real: prefeituras pequenas (5k-50k hab), Pregão ME/EPP até R$80k/ano. EGOS assets: Guard Brasil (LGPD mandatório pós 14.133), Eagle Eye (OSINT), 852 (chatbot municipal). TCU audita TI federal 2026 = janela para novos players compliance-first.
**SSOT:** `docs/GTM_SSOT.md` §govtech | **Fontes:** pncp.gov.br, IN SGD/ME 94/2022, Lei 14.133/2021, análise 12 buscas 2026-04-07

**P1 — Discovery + Habilitação:**
- [ ] **GOV-TECH-001 [P1]**: Configurar Eagle Eye para monitorar PNCP — filtros: objeto `%software%|%sistema%|%plataforma%|%desenvolvimento%`, valor R$15k-80k, exclusivo ME/EPP, UF alvo SC/PR/SP. Alerta Telegram diário. [4h]
- [ ] **GOV-TECH-002 [P1]**: Dashboard vencedores licitações software. Query PNCP API + ComprasNet: top 15 empresas, ticket médio, modalidade, CNPJ, setor dominante. Output: `docs/knowledge/GOVTECH_WINNERS_MAP.md`. [6h]
- [ ] **GOV-TECH-003 [P1]**: Checklist habilitação EGOS. Verificar: CNPJ ativo, CNAE 6201-5/00 ou 6202-3/00, SICAF cadastro, certidões (CND Federal/Estadual/Municipal, CRF FGTS, CNDT), capital social ≥ 10% valor contrato-alvo. [2h MANUAL]
- [ ] **GOV-TECH-004 [P1]**: Mapa oportunidades abertas agora. Buscar 5 pregões ME/EPP no PNCP: ouvidoria municipal, gestão LGPD, portal cidadão, sistema saúde municipal. Verificar objeto + requisitos + prazo. [3h]

**P1 — Produto:**
- [ ] **GOV-TECH-005 [P1]**: Brief produto "Ouvidoria Municipal + LGPD Compliance SaaS". Core: Guard Brasil mascaramento PII (CPF/RG/nome), relatórios ANPD-compliant, painel prefeitura. Ticket-alvo: R$30k-80k/ano. Público: prefeituras 5k-50k hab. [4h]
- [ ] **GOV-TECH-006 [P1]**: Análise técnica de 3 sistemas verificáveis (e-cidade PHP/PostgreSQL, Softplan Obras.gov Java/Spring, Betha Cloud SaaS). Identificar gaps LGPD que Guard Brasil resolve. Output: tabela comparativa. [3h]

**P2 — Parcerias:**
- [ ] **GOV-TECH-007 [P2]**: Parceria Softplan — Guard Brasil como módulo LGPD para Obras.gov/SAJ. Pitch: "EGOS Guard Brasil cobre o gap que TCU está auditando em 2026." LinkedIn + GitHub. [2h prep]
- [ ] **GOV-TECH-008 [P2]**: Parceria Betha Sistemas — Guard Brasil como add-on LGPD no Betha Cloud (+3000 prefeituras). Modelo: R$0.02/call × volume municipal. Revenue share 70/30. [2h prep]
- [ ] **GOV-TECH-009 [P2]**: Estratégia primeiro atestado. Pilot gratuito/subsidiado para prefeitura pequena SC/PR/SP (5-15k hab) → obter atestado capacidade técnica. Mínimo viável: 3 meses contrato assinado. [5h MANUAL]
- [ ] **GOV-TECH-010 [P2]**: Estudar Diálogo Competitivo (Lei 14.133 art.32) para produto inovador IA+LGPD. Municípios que não sabem especificar → EGOS pode ser único habilitado. Mapear 3 prefeituras usando esta modalidade. [2h]

---

## Intelink v3 — Consolidação SSOT ✅ COMPLETA (2026-04-09)
**SSOT:** `/home/enio/egos-inteligencia/` | 94 TS files + 81 Python files portados | 934MB liberados
> Detalhes em TASKS_ARCHIVE.md — Intelink CONS/PORT/CLEAN (2026-04-09)

---

### Intelink v3 — Segurança + Multi-Device (2026-04-09)
**SSOT:** `docs/knowledge/INTELINK_V3_SECURITY_ARCHITECTURE.md`
**Decisões aprovadas:** Híbrido local+cloud | TIER 3 max | MASP+senha+2FA | CRDT (Automerge) | RxDB | PBKDF2 | Hetzner MVP→HA→Edge

**✅ Decisões críticas — APROVADAS 2026-04-09:**
- [x] **INTELINK-DEC-001**: RxDB v15 + plugin AES-256 — CRDT nativo, web PWA + React Native mesma codebase
- [x] **INTELINK-DEC-002**: PBKDF2(MASP+senha, salt_device, 600K iter.) — chave nunca sai do device
- [x] **INTELINK-DEC-003**: Plano faseado: Hetzner CX31 MVP → HA dual (produção) → Edge delegacia (expansão)

**P0 — Fase 0: Fundação de Segurança:**
- [ ] **INTELINK-SEC-001**: Auth server — MASP + bcrypt (14 rounds) + JWT RS256 + refresh token (8h campo / 30d base)
- [ ] **INTELINK-SEC-002**: 2FA — portar bot Telegram existente do Intelink + adicionar opção email institucional
- [ ] **INTELINK-SEC-003**: RxDB v15 inicializado com plugin AES-256-GCM + PBKDF2 key derivation
- [ ] **INTELINK-SEC-004**: Audit log append-only (PostgreSQL tabela imutável + Merkle tree tamper-proof)
- [ ] **INTELINK-SEC-005**: Device registration — fingerprint + revogação remota por MASP

**P0 — Fase 1: Sync Engine CRDT:**
- [ ] **INTELINK-SYNC-001**: Automerge v2 integrado no cliente (web PWA + React Native)
- [ ] **INTELINK-SYNC-002**: Delta sync endpoint FastAPI — envia apenas ops CRDT pendentes (WebSocket + HTTPS)
- [ ] **INTELINK-SYNC-003**: Offline queue persistente — ops não perdidas entre reinicializações do app
- [ ] **INTELINK-SYNC-004**: Testes de merge: 2 devices editam mesmo registro offline → merge correto verificado

**P1 — Fase 2: Multi-device:**
- [ ] **INTELINK-DEVICE-001**: PWA desktop Next.js — testado Windows + Linux (Electron opcional)
- [ ] **INTELINK-DEVICE-002**: React Native MVP para tablet Android — mesma codebase do web
- [ ] **INTELINK-DEVICE-003**: Session lock — background > 5min → PIN ou biometria nativa do OS
- [ ] **INTELINK-DEVICE-004**: Wipe remoto — admin revoga sessão → dados TIER 3 inacessíveis imediatamente

**P1 — Fase 3: TIER + Auditoria:**
- [ ] **INTELINK-TIER-001**: Classificador TIER 1-4 por campo — automático + override manual delegado
- [ ] **INTELINK-TIER-002**: Partição TIER 3 com chave AES separada no RxDB local
- [ ] **INTELINK-TIER-003**: Wazuh SIEM + alertas Telegram para Corregedoria (acesso anômalo, fora horário, exfiltração)
- [ ] **INTELINK-TIER-004**: Dashboard auditoria read-only — Merkle root + eventos TIER 1-2 apenas

**P2 — Fase 4: Hardening + Piloto:**
- [ ] **INTELINK-HARD-001**: Pen test OWASP Top 10 (auth, injection, broken access control)
- [ ] **INTELINK-HARD-002**: Stress test sync — 100 devices simultâneos sem corrompimento de dados
- [ ] **INTELINK-HARD-003**: Runbook: device perdido, senha esquecida, servidor comprometido
- [ ] **INTELINK-HARD-004**: Piloto 1 delegacia PCMG — 5 usuários, 30 dias, métricas coletadas

---

### Telegram Alerts Consolidation (2026-04-08)
**SSOT:** `docs/knowledge/TELEGRAM_ALERTS_AUDIT_2026-04-08.md`
**Context:** Audit de 8 fontes de alerta @EGOSin_bot. 5 ativos, 2 para verificar, 1 legado (OpenClaw). Meta: <10 alertas relevantes/dia.

**P0 — Limpeza:**
- [x] **NOTIFY-001**: OpenClaw already stopped on VPS — no systemctl service found (`systemctl stop/disable`)
- [x] **NOTIFY-002**: RAM monitor already configured correctly — warning <500MB, critical <100MB (vps-ram-monitor.sh:91/74)
- [ ] **NOTIFY-003**: Consolidar Doc Drift alerts em 1 sumário diário

**P1 — Botões e Interatividade:**
- [ ] **NOTIFY-004**: Inline keyboard no X Approval Bot
- [ ] **NOTIFY-005**: Botões no X Opportunity Alert
- [ ] **NOTIFY-006**: Comando `/task nova` no Telegram
- [ ] **NOTIFY-007**: Comando `/task lista`
- [ ] **NOTIFY-008**: Comando `/task feita` com auto-commit

**P2 — Config via Bot:**
- [ ] **NOTIFY-009**: Mapear serviços VPS para `/env` commands
- [ ] **NOTIFY-010**: Menu principal `/menu`

---

### Timeline + AI Publishing System (2026-04-08)
**SSOT:** `docs/TIMELINE_AI_PUBLISHING_ARCHITECTURE.md` | **Status:** TL-001 ✅ schema live.
**Context:** Auto-generate articles from commits → Supabase drafts → Human approval (Telegram/WhatsApp/HQ) → Publish to egos.ia.br/timeline + X.com. Principles: transparência radical, HITL (never blind publish), PII guard.

| Phase | Task | Description | Status |
|-------|------|-------------|--------|
| **1: Foundation** | TL-001 | Supabase: timeline_drafts + timeline_articles + x_post_queue | ✅ Done |
| | TL-002 | Agent: article-writer.ts — reads commit/diff, calls qwen-plus, writes draft | [x] |
| | TL-003 | Script: publish.sh manual trigger | [x] |
| | TL-004 | Telegram bot: approve flow (✅/✏️/❌) with 48h timeout | [x] |
| **2: Site público** | TL-005 | Bun/Hono: apps/egos-site — /timeline + /timeline/[slug] | [x] |
| | TL-006 | Route: GET /timeline — list articles paginated | [x] |
| | TL-007 | Route: GET /timeline/[slug] — render article + metrics | [x] |
| | TL-008 | Caddy: egos.ia.br → egos-site:3071 — live | [x] |
| **3: Automação** | TL-009 | timeline-cron-daily.sh — scan commits 24h (cron 03:00 UTC) | [x] |
| | TL-010 | Crontab: add timeline-cron-daily.sh | [x] |
| | TL-011 | auto-disseminate.sh: detect PUBLISH: → article-writer background | [x] |
| | TL-012 | x-reply-bot: postArticle(snippet, url) method | [ ] |
| **4: Multi-canal** | TL-013 | WhatsApp via Evolution API (same approval flow) | [ ] |
| | TL-014 | HQ tab: /timeline/pending with inline edit | [ ] |
| | TL-015 | OG image generation: apps/og-gen | [ ] |
| **5: Intelligence** | TL-016 | Weekly digest agent: 7 days → "What shipped this week" | [ ] |
| | TL-017 | Engagement feedback: low-engagement → flag for tone adjustment | [ ] |
| | TL-018 | PT→EN auto-translation via Deepl API | [ ] |

---

### Gem Hunter — Product Roadmap (2026-04-08)
**SSOT:** `docs/GEM_HUNTER_MARKET_DOMINATION_ROADMAP.md` | **Status:** GH-074 ✅ digest live.
**Context:** Build well, distribute honestly, let the right people find it. Multi-source + autonomous + quality-scored = genuine value for developers.

| Phase | Task | Description | Status |
|-------|------|-------------|--------|
| **A: Distribution** | GH-074 | gem-hunter-digest.ts — top 3-5 repos/week, markdown+Telegram (cron Thu 02:00 UTC) | ✅ Done |
| | GH-075 | Landing page: gemhunter.egos.ia.br (Bun/Hono, dark mode) — live | [x] |
| | GH-076 | Substack: Telegram HITL draft Thu 08:00 UTC — cron live | [x] |
| **B: Community** | GH-077 | Supabase: gem_lists + gem_votes + vote_count — RLS live | [x] |
| | GH-078 | API: /gems/:url/upvote + /trending + /lists/* — live port 3070 | [x] |
| | GH-079 | Dashboard: 👍 voting button + Top voted tab + dynamic API load | [x] |
| | GH-080 | github.com/enioxt/awesome-gems — created, README + 2026-04-08 gems | [x] |
| **C: Distribution** | GH-081 | Slack bot: /gem-hunter trending [lang] | [ ] |
| | GH-082 | Discord bot: !gems [lang] embed + buttons | [ ] |
| | GH-083 | Telegram @gem_hunter_bot: /trending /random /subscribe | [ ] |
| **D: Optional tiers** | GH-084 | Stripe: Free/Pro/Team tiers when community validates demand | [ ] |
| | GH-085 | Supply-chain risk endpoint: /gems/{id}/supply-chain-risk | [ ] |
| **E: MCP + Multi-Domain** | GH-086 | `@egosbr/gem-hunter-mcp` — MCP server (tools: search/trending/by_domain) for Claude Code/Windsurf/Cursor/Copilot, install by repo URL | [ ] |
| | GH-087 | Multi-domain sources: medical (PubMed/arXiv-bio), engineering (IEEE/papers-with-code), veterinary, finance/traders (QuantConnect/QuantStack), web3 (Awesome lists, Etherscan dev tools) — adapter pattern in `agents/gem-hunter/sources/` | [ ] |
| | GH-088 | Persona-aware scoring: same gem ranks differently for `--persona=doctor` vs `trader` vs `web3-dev` | [ ] |
| **Fixes 2026-04-08** | GH-FIX-1 | Caddyfile: gemhunter upstream `egos-site:3070` → `gem-hunter-landing:3070` (was 502) | [x] |
| | GH-FIX-2 | server.ts + index.html: query column `language` → `category` (404 in trending API) | [x] |

---

### X.com Public Posts — Transparency & Partnerships (2026-04-08)
**SSOT:** `docs/social/X_POSTS_SSOT.md` §8.5 | **Schedule:** N1 Mon 2026-04-14 → N8 Wed 2026-04-23 (2/week)
**Context:** 8 posts approved. Transparency strategy: show what's being built, attract aligned builders naturally.

| ID | Post | CTA | Schedule | Status |
|----|------|-----|----------|--------|
| **SOCIAL-001** | Open partnerships (equity flexible) | "DM aberta" | 2026-04-14 | ✅ Queued Supabase |
| **SOCIAL-002** | Gem Hunter spotlight | "DM para parceria" | 2026-04-15 | ✅ Queued Supabase |
| **SOCIAL-003** | Guard Brasil LGPD | "parceria compliance" | 2026-04-16 | ✅ Queued Supabase |
| **SOCIAL-004** | Researcher mindset | "DM aberta" | 2026-04-17 | ✅ Queued Supabase |
| **SOCIAL-005** | Transparência radical | "building in public" | 2026-04-18 | ✅ Queued Supabase |
| **SOCIAL-006** | Hermes decommission (Codex → qwen-plus chain) | "Vale ler pra agentic builders" | 2026-04-15 | ⏳ Queue |
| **SOCIAL-007** | Governance (26 SSOTs, 4-layer doc-drift) | "Vale ver se tá nesse pico" | 2026-04-17 | ⏳ Queue |
| **SOCIAL-008** | Call for builders | "DM aberta" | 2026-04-23 | ⏳ Queue |


---

### Supabase Cleanup (2026-04-08)
**SSOT:** `docs/SUPABASE_AUDIT.md` | **Project:** `lhscgsqhiooyatkebose` | **State:** 173 tables, ~37 dead, 4 unrelated domains

- [x] **SUPA-001 [P0]**: Drop unrelated domains (`ethik_*` 12, `volante_*` 6, `nexusmkt_*` 7, empty `hub_*`) — 0 risk, ~30 tables ✅ 2026-04-08
- [x] **SUPA-002 [P0]**: Drop empty `*_v2`/`*_v3` migration leftovers (`telemetry_events_v2`, `messages_v3`, `conversations_v3`, `ai_call_metrics`, `ai_response_cache`, `audit_logs`, `profiles`, `rate_limits`, `user_consents`, `knowledge_vectors`, `detected_patterns`, `conversation_logs`) ✅ 2026-04-08
- [x] **SUPA-003 [P1]**: Investigate `knowledge_base` — KEEP. 1648 rows / 28 MB (task had stale "9 rows"). pgvector embeddings = ARR data. `egos_wiki_pages` (92 rows) = separate wiki system. Different purposes, no migration needed. ✅ 2026-04-08
- [x] **SUPA-004 [P1]**: Drop `code_*` indexer tables (chunks/symbols/files/relations) — replaced by codebase-memory-mcp ✅ 2026-04-08
- [ ] **SUPA-005 [P2]**: CCR weekly job — alert if any non-core table > 50 MB
- [ ] **SUPA-006 [P2]**: Naming convention rule — every new table prefixed with active domain (`egos_`, `gem_`, `guard_`, `intelink_`, `eagle_`, `x_post_`, `timeline_`, `852_`)

---

### CLAUDE.md Modular Refactor (2026-04-08)
**SSOT:** `~/.claude/CLAUDE.md` | **Evidence:** arXiv "Curse of Instructions" + Lost in Middle + HumanLayer analysis
**Context:** 639 linhas, 30 seções = above reliable compliance threshold. §10-§20 systematically 30%+ lower compliance (middle blind spot). Solution: modular architecture — core file <120 lines + domain files loaded on demand.

**P0 — Reorder critical rules (30 min, immediate impact):**
- [x] **RULES-001 [P0]**: ✅ Critical rules block at top of ~/.claude/CLAUDE.md — 5 non-negotiables in primacy position.
- [x] **RULES-001b [P1]**: GUARD_BRASIL_API_KEY missing — PII check in article-writer fails silently. Set in ~/.egos/secrets.env. Found: TL-002 dry-run. ✅ 2026-04-08

**P1 — Modular split (2-3h, correct fix):**
- [x] **RULES-002 [P1]**: ✅ ~/.claude/egos-rules/ created — ssot-map.md, doc-drift.md, jobs-monitoring.md, llm-routing.md, product-gtm.md
- [x] **RULES-003 [P1]**: ✅ §12, §13, §28, §29 compressed → references to egos-rules/ — 653→615 lines
- [ ] **RULES-004 [P1]**: Compress core ~/.claude/CLAUDE.md to <120 lines — only MUST/MUST NOT rules
- [x] **RULES-005 [P1]**: ✅ Pointer table added after CRITICAL NON-NEGOTIABLES block
- [x] **RULES-008 [P1]**: ✅ Governance kernel propagation live 2026-04-08 — scripts/governance-propagate.sh applied to 12 local + 4 VPS repos. Crons: local 04:00 + VPS 05:00. git init wrapper in ~/.bashrc for new repos. ~/.egos/sync.sh updated (egos-inteligencia added).

**P2 — Skills for on-demand loading:**
- [ ] **RULES-006 [P2]**: Convert §12 (Scheduled Jobs) to a /start skill that loads on session open
- [ ] **RULES-007 [P2]**: Convert §28 (Auto-Disseminate) to a /disseminate skill

**Target after refactor:** ~100 lines core file, 7 domain files, compliance for critical rules at primacy position.
---
## Git Workflow — Branch Protection (INC-001 follow-up)
**Decision (2026-04-08):** Manter branch protection. GIT-001..003 RESOLVIDOS (já em main, divergência resolvida via rebase). Branch protection funcionando como esperado.
- [ ] **GIT-004 [P1]**: Documentar workflow PR-first em `CLAUDE.md` para mudanças >5 arquivos ou >100 linhas
- [ ] **GIT-005 [P1]**: `scripts/create-pr.sh` — automatiza branch+push+gh CLI
- [ ] **GIT-006 [P1]**: Comando `egos pr "título"` em `agents.json`

---

### LLM Model Monitor — OpenRouter Intelligence System (2026-04-08)
**Context:** Pesquisa aprofundada revela 28+ modelos free no OpenRouter (Qwen3 Coder, Nemotron 3 Super, MiniMax M2.5, Step 3.5 Flash) e dezenas de modelos pagos com excelente custo-benefício (Kimi K2.5, DeepSeek V3.2, MiMo-V2-Pro). Necessário sistema automatizado para monitorar novos modelos, testar, comparar e adaptar fallbacks dinamicamente.
**SSOT:** `docs/knowledge/LLM_MODEL_MONITOR.md` (a criar) | **Fontes:** CostGoat, OpenRouter Rankings April 2026, TeamDay AI, Reddit r/LocalLLaMA, Digital Applied

**Models catalogued:** Qwen3 Coder 480B, Nemotron 3 Super, MiniMax M2.5, Step 3.5 Flash, Qwen3.6 Plus (free S-tier); Kimi K2.5, DeepSeek V3.2, MiMo-V2-Pro (paid best-value). Full tables: `docs/knowledge/LLM_MODEL_MONITOR.md`.

**P0 — Foundation (Agente Monitor):**
- [ ] **LLM-MON-001 [P1]**: Criar `scripts/llm-model-monitor.ts` — agente que roda no VPS a cada 6h, consulta OpenRouter API `/models`, detecta novos modelos (free ou paid)
- [ ] **LLM-MON-002 [P1]**: Integração MCP Exa — para cada novo modelo detectado, pesquisar reviews no Reddit, X.com, blogs técnicos (qualidade, benchmarks, casos de uso)
- [ ] **LLM-MON-003 [P1]**: Supabase schema `llm_models` — armazenar: id, provider, name, pricing, context_length, capabilities, is_free, discovery_date, review_sentiment, benchmark_scores, egos_recommendation
- [ ] **LLM-MON-004 [P1]**: Notificações — alertar no Telegram/WhatsApp quando modelo promissor (S-tier) é detectado, com summary do research Exa

**P1 — Test & Comparison Engine:**
- [ ] **LLM-MON-005 [P1]**: Test Suite Standard — 5 categorias de prompts: (1) Coding (gerar + debug), (2) Reasoning (lógica matemática), (3) Context Longo (128K+), (4) Agentic (tool calling), (5) Creative (copywriting)
- [ ] **LLM-MON-006 [P1]**: Auto-Test Runner — para cada modelo novo S-tier, rodar test suite automaticamente, medir: latency, token usage, quality score (LLM-as-judge), success rate
- [ ] **LLM-MON-007 [P2]**: Benchmark Comparison — comparar resultados do novo modelo vs current fallback chain, gerar report `docs/knowledge/LLM_MODEL_COMPARISON_YYYY-MM-DD.md`
- [ ] **LLM-MON-008 [P2]**: Fallback Chain Auto-Update — se novo modelo supera current fallback em quality/cost, propor atualização de `packages/shared/src/llm-provider.ts` via PR automático

**P2 — Intelligence & Adaptation:**
- [ ] **LLM-MON-009 [P2]**: Task-Based Routing — mapear cada categoria de teste para tipo de task EGOS (chat, review, summary, intelligence, coding) e sugerir modelos específicos por tarefa
- [ ] **LLM-MON-010 [P2]**: Cost Optimization Engine — monitorar gasto real do OpenRouter (via API key usage), alertar quando alternativa free/cheaper atinge paridade de qualidade
- [ ] **LLM-MON-011 [P2]**: Dashboard no HQ — visualizar: modelos monitorados, scores de testes, fallback chain atual, economia gerada por otimizações
- [ ] **LLM-MON-012 [P2]**: Integration com CORAL — quando modelo é validado como S-tier, salvar discovery no `gem_discoveries` para reuso por outros agentes

---

### Content Orchestrator v2 — OpenMontage + OpenScreen Deep Integration (2026-04-08)
**Context:** Pesquisa aprofundada revela OpenMontage (AGPL-3.0, 498⭐) com 11 pipelines completos: Reference Video Analysis → Concept Generation → Asset Generation → Voice/Narration → Music → Editing → Composition. Cada vídeo custa $0.15-$1.33. OpenScreen (MIT, 8400+⭐) é alternativa open-source ao Screen Studio com auto-zoom, motion blur, animated cursor — ideal para demos de produto.
**SSOT:** `docs/knowledge/CONTENT_ORCHESTRATOR_V2.md` (a criar) | **Fontes:** calesthio/OpenMontage GitHub, PyShine, AI Heartland, Mintlify docs

**Pipelines:** 7-stage OpenMontage (Reference → Concept → Assets → Voice → Music → Edit → Review, $0.15-$1.33/video) + OpenScreen (auto-zoom, motion blur, no watermark). Full detail: `docs/knowledge/CONTENT_ORCHESTRATOR_V2.md`.

**P0 — Foundation (Deep Integration):**
- [ ] **CONTENT-001 [P1]**: Fork OpenMontage para `.egos/content-orchestrator/openmontage/` com wrapper EGOS: (a) Guard Brasil PII scan em todos scripts gerados, (b) Audit trail de cada pipeline, (c) Cost approval gate antes de gerar assets pagos
- [ ] **CONTENT-002 [P1]**: Fork OpenScreen para `.egos/content-orchestrator/openscreen/` com wrapper EGOS: (a) LGPD compliance para webcam/audio, (b) Evidence chain de gravações
- [ ] **CONTENT-003 [P1]**: Meta-prompt `content.orchestrator.v2` — linguagem natural → escolhe pipeline (OpenMontage full video vs OpenScreen demo vs combined)
- [ ] **CONTENT-004 [P1]**: Integração em `agents.json` — comando `egos content "descrição" [--type=video|demo|combined] [--budget=$X]`

**P1 — Advanced Workflows:**
- [ ] **CONTENT-005 [P1]**: MemPalace integration — salvar em wing "content": scripts, assets, config de cada pipeline, room por projeto EGOS
- [ ] **CONTENT-006 [P1]**: Event-bus integration — tópicos: `content.pipeline.started`, `content.asset.generated`, `content.completed`, `content.demo.recorded`
- [ ] **CONTENT-007 [P2]**: Combined Pipeline — vídeo OpenMontage com demos OpenScreen injetados (ex: intro animada + demo real EGOS + outro)
- [ ] **CONTENT-008 [P2]**: Auto-Content Calendar — integrar com X-COM para: detectar release EGOS → gerar vídeo explicativo → publicar no X automaticamente (com approval)
- [ ] **CONTENT-009 [P2]**: Content Variants — usar LLM para gerar 3 variações de cada vídeo (short 30s, medium 2min, long 5min) a partir do mesmo conceito
- [ ] **CONTENT-010 [P2]**: A/B Testing Framework — publicar variações no X, medir engagement, reportar winner para futuros vídeos

**P2 — Scale & Intelligence:**
- [ ] **CONTENT-011 [P2]**: Template Library — pre-built templates: "Product Release", "Feature Demo", "Tutorial", "Case Study", "Behind the Scenes"
- [ ] **CONTENT-012 [P2]**: Voice Clone Integration — clonar voz do time EGOS para narração consistente em todos vídeos (ElevenLabs voice clone)
- [ ] **CONTENT-013 [P2]**: Auto-Thumbnail Generator — FLUX/GPT-4o para gerar thumbnails otimizados para X/YouTube a partir do vídeo
- [ ] **CONTENT-014 [P2]**: Content Performance Analytics — dashboard no HQ: views, engagement, cost per view, ROI de conteúdo

---

### Test & Validation Orchestrator v2 — Multi-Agent Review System (2026-04-08)
**Context:** Pesquisa Braintrust, AutoEvals, EPOCH-Bench revelam padrão comum: agent evaluation requer tracing completo, scorers (deterministic + LLM-as-judge), regression gates em CI/CD, e feedback loop produção→teste. Thread X Bruno Pinheiro confirma: breakdown estruturado (epic→stories) + E2E tests auto-gerados + multi-agent swarm review = crescimento rápido validado.
**SSOT:** `docs/knowledge/TEST_ORCHESTRATOR_V2.md` (a criar) | **Fontes:** Braintrust Agent Evaluation Framework, AutoEvals Medium, EPOCH-Bench, Arun Baby Testing AI Agents

**6-Agent Swarm:** Planner → Generator → Reviewer1/2 (coverage+security) → Validator → Reporter. Full design: `docs/knowledge/TEST_ORCHESTRATOR_V2.md`.

**P0 — Core Swarm:**
- [ ] **TEST-001 [P1]**: Criar `.egos/test-orchestrator/` com 6 agentes especializados (Planner, Generator, Reviewer1, Reviewer2, Validator, Reporter)
- [ ] **TEST-002 [P1]**: Meta-prompt `test.validation.orchestrator` — aceita: "valide epic X", "gere E2E para story Y", "regression test para bug Z"
- [ ] **TEST-003 [P1]**: E2E Test Generator — templates Playwright (web) + TestNG (API) + geração via LLM a partir de stories
- [ ] **TEST-004 [P1]**: Integração `agents.json` — comandos: `egos validate "epic"`, `egos test story X`, `egos regression-check`

**P1 — Validation Pipeline:**
- [ ] **TEST-005 [P1]**: Self-Verification Gates — pre-commit hook que chama swarm para: lint → type-check → unit tests → E2E (paralelizável)
- [ ] **TEST-006 [P1]**: Evidence Chain Auto-Generation — cada validação cria evidence entry com: test results, coverage, security scan, timestamp, agent signatures
- [ ] **TEST-007 [P2]**: MemPalace Wake-Up — antes de validar, puxar contexto de testes passados similares (CORAL pattern aplicado a testes)
- [ ] **TEST-008 [P2]**: Content Orchestrator Integration — após validação bem-sucedida, trigger `egos content` para gerar demo video da feature automaticamente

**P2 — Intelligence & Scale:**
- [ ] **TEST-009 [P2]**: Self-Healing Tests — quando teste quebra, agent tenta corrigir automaticamente usando LLM (diff suggestion) com aprovação humana
- [ ] **TEST-010 [P2]**: Flaky Test Detection — detectar testes instáveis via análise estatística (variance > threshold), quarentenar e notificar
- [ ] **TEST-011 [P2]**: Test Analytics Dashboard — no HQ: cobertura por repo, tempo médio de execução, taxa de falha, economia de tempo com auto-tests
- [ ] **TEST-012 [P2]**: Regression Prediction — ML simples para prever quais arquivos têm maior risco de regressão baseado em histórico de mudanças
- [ ] **TEST-013 [P2]**: Integration com LLM-MON — usar modelos mais baratos/free do OpenRouter para geração de testes quando qualidade for equivalente
- [ ] **TEST-013 [P2]**: Integration com LLM-MON — usar modelos mais baratos/free do OpenRouter para geração de testes quando qualidade for equivalente

---

### Auto-Disseminate Agent Pipeline (2026-04-08)
**SSOT:** `docs/CAPABILITY_REGISTRY.md` §25 | **Context:** `/disseminate` hoje é manual e custoso em tokens. Goal: 3-agent pipeline post-commit → propagação automática → Enio aprova via Telegram.

- [x] **DISS-001 [P1]**: `scripts/disseminate-scanner.ts` — lê `git diff HEAD~1` nos kernel files, identifica seções que mudaram, gera manifest `{changed_rules: [], affected_repos: []}` | 2h ✅ 2026-04-08
- [ ] **DISS-002 [P1]**: `scripts/disseminate-propagator.ts` — recebe manifest, para cada repo: atualiza bloco kernel no marker `# EGOS-KERNEL-PROPAGATED`, cria commit `chore(kernel): propagate YYYY-MM-DD` | 3h
- [ ] **DISS-003 [P1]**: `scripts/disseminate-verifier.ts` — re-lê cada repo após propagação, verifica marker + conteúdo + data, output: `{repo, status: pass|fail, missing_rules: []}` | 2h
- [x] **DISS-004 [P1]**: post-commit hook trigger — quando CLAUDE.md | .windsurfrules | CAPABILITY_REGISTRY.md muda, auto-chama scanner | 1h ✅ 2026-04-08
- [ ] **DISS-005 [P1]**: Telegram approval gate — verifier envia summary ao Telegram (`@ethikin`): lista repos + status, botões [✅ Approve All][❌ Review] | 2h
- [ ] **DISS-006 [P2]**: VPS propagation — após aprovação local, SSH push kernel block para os 4 repos no VPS (`/opt/852`, `/opt/bracc`, `/opt/egos`, `/opt/egos-lab`) | 2h

---

### Paperclip Integration Patterns (2026-04-08)
**SSOT:** `docs/knowledge/HARVEST.md` KB-028 | **Source:** github.com/paperclipai/paperclip (49.9K⭐, MIT) | **Strategy:** EGOS = safety/compliance kernel inside Paperclip, not competing.

**Adoptable NOW (sem Paperclip dependency):**
- [x] **PAP-001 [P1]**: Heartbeat loop nativo — `agents/runtime/heartbeat.ts` (wrapper, runner.ts FROZEN): ciclo wake(30min) → checkWorkQueue() → runAgent() → emit(bus) → sleep. Configurable per-agent. ✅ 2026-04-08
- [ ] **PAP-002 [P1]**: Per-agent budget enforcement — estender Guard Brasil token counter: campo `monthly_cap` per agent_id, auto-pause signal quando 100%, warning Telegram 80%. | 3h
- [ ] **PAP-003 [P2]**: Goal ancestry em TASKS.md — adicionar coluna `WHY` em tasks (link para parent goal). Template: `[PAP-003] Fix X → goal: Y → mission: Z`. | 1h

**Integration (com Paperclip):**
- [ ] **PAP-004 [P2]**: EGOS↔Paperclip adapter — registra agents EGOS como "employees" do Paperclip. Guard Brasil valida outputs antes de retornar ao Paperclip. Repositório: `@egosbr/paperclip-adapter`. | 8h
- [ ] **PAP-005 [P3]**: Pitch adapter para @dotta (criador Paperclip) — "EGOS adds LGPD/PII compliance layer for Brazilian Paperclip users." DM via GitHub Issues ou X.com. | 1h

---

### Live School — The Observatory (reativação EGOSv2)
**SSOT:** `egos-archive/v2/EGOSv2/live_school_redesign/` + `modules/egos_learning_orbit/` | **Status:** EGOSv2 completo, precisa rewrite Bun/TS
**Conceito:** Tela inteira cosmos 3D (React Three Fiber) + 3 agentes AI (EVA/GUARANI/MAIÊUTICA). "Ensinar é recordar o que já se é" — método maiêutico socrático (do grego μαιευτική: arte de parir ideias).

- [x] **LS-001 [P2]**: Análise assets EGOSv2 — ObservatoryLanding.tsx (React Three Fiber), 3 agentes Python, design_concept.md → gerar spec moderna Bun/TS. Decisão: standalone app ou integrar em egos-site? | 2h ✅ 2026-04-08
- [ ] **LS-002 [P2]**: Port EVA+GUARANI+MAIÊUTICA para TypeScript — usar EGOS agent-runner como base. Guard Brasil wrapping dados de alunos (LGPD). | 6h
- [ ] **LS-003 [P3]**: Observatory UI — Bun/Hono + React Three Fiber — tela cósmica full-screen. Stars, órbitas gravitacionais, portal de entrada. Base: `live_school_redesign/src/components/ObservatoryLanding.tsx` | 8h

---

### KB-as-a-Service — "EGOS Knowledge" (2026-04-08)
**SSOT:** `docs/strategy/KB_AS_A_SERVICE_PLAN.md` | **Parent:** Track A+B+C+D
**Contexto:** Produtizar wiki-compiler + atomizer + ARR + Guard Brasil + Notion MCP nativo como serviço de "Cérebro Externo Governado" para profissionais brasileiros. FORJA = beta. Notion = frontend (curva baixa). Claude Code $20/mês = motor no cliente. EGOS kernel = governance.
**Unlock 2026-04-08:** Notion MCP nativo descoberto (`mcp__claude_ai_Notion__*`) — eliminou blocker de integração custom.

**P0 — Dogfooding + template + FORJA (próximas 2 semanas):**
- [ ] **KBS-001 [P0]**: Criar template Notion "Inteligência da Empresa" via MCP — DB Documentos, DB Q&A, DB Decisões, página "Como usar" PT-BR. Duplicável. | 4h
- [ ] **KBS-002 [P0]**: Escrever `CLAUDE.md` cliente (≤100 linhas, PT-BR, placeholders por setor — metal/jurídico/saúde). Salvar em `packages/knowledge-mcp/templates/CLAUDE.md.tpl`. | 2h
- [ ] **KBS-003 [P0]**: Guia setup PT-BR — `docs/guides/KBS_ONBOARDING_PT_BR.md` — install Claude Code → OAuth Notion MCP → primeiro `/ingest` + `/ask`. Com screenshots. | 3h
- [ ] **KBS-004 [P0]**: FORJA namespace beta — `clients/forja/` ou branch no FORJA repo, `.guarani/forja-rules.md`, ingestar 10 docs piloto (orçamento antigo, ficha produção, ABNT referenciada). | 6h
- [ ] **KBS-005 [P0]**: Loom demo 3–5min PT-BR — "Sua Inteligência da Empresa em 5 minutos". Gravar usando dogfooding interno (TASKS.md + HARVEST.md como exemplo). | 2h
- [ ] **KBS-006 [P0]**: PDF/Docx ingestor — plugar em `wiki-compiler.ts` via `unpdf` + `mammoth`. Input: pasta, output: atoms no `egos_wiki_pages`. | 8h
- [ ] **KBS-007 [P0]**: KB-lint adaptado — fork de `ssot-auditor.ts` focado em: órfãos, contradições, staleness >90d, citações quebradas. Modo `bun kb:lint --tenant=forja`. | 6h
- [ ] **KBS-008 [P0]**: `packages/knowledge-mcp/` completar — expor tools: `kb_ingest`, `kb_ask`, `kb_lint`, `kb_export`. Publicar como `@egosbr/knowledge-mcp`. | 8h
- [ ] **KBS-009 [P0]**: Dogfooding interno — apontar knowledge-mcp para TASKS.md + HARVEST.md + handoffs. Usar 2 semanas antes de qualquer venda. Gate: 10 queries/dia por 14 dias. | on-going

**P1 — Produto público + pricing (semanas 3-6):**
- [ ] **KBS-010 [P1]**: Landing page "EGOS Knowledge" no `egos-site/` — 1 página, hero + 3 tiers + demo embed + CTA WhatsApp. PT-BR. | 6h
- [ ] **KBS-011 [P1]**: Pricing page detalhada — Starter R$1.5k / Pro R$5k / Enterprise R$15k+. Comparação com consultoria tradicional. | 3h
- [ ] **KBS-012 [P1]**: Contract template — serviço de implementação + manutenção. Revisado por advogado (network Enio). | 4h
- [ ] **KBS-013 [P1]**: Onboarding checklist — `docs/guides/KBS_DELIVERY_CHECKLIST.md` — passo-a-passo replicável (discovery → contrato → setup → treinamento → handoff). | 3h
- [ ] **KBS-014 [P1]**: Primeiros 3 leads aligned (não vaga, não cold sales) — advogado brasileiro, PME metal além de FORJA, clínica. Research via exa/firecrawl em grupos WhatsApp/Telegram e Twitter. | 4h
- [ ] **KBS-015 [P1]**: Template Notion público no GitHub (`egosbr/knowledge-template`) — MIT, com instruções de duplicação. | 2h
- [ ] **KBS-016 [P1]**: Multi-tenant Supabase — RLS por `tenant_id`, migration `egos_wiki_pages_tenanted`. Antes do 2º cliente Pro. | 8h
- [ ] **KBS-017 [P1]**: Stripe billing tiers (Starter/Pro/Enterprise) — reusar infra Guard Brasil. Cartão BRL aceito. | 4h
- [ ] **KBS-018 [P1]**: Citation export — comando `/export` produz Markdown + PDF com fontes numeradas. | 4h
- [ ] **KBS-019 [P1]**: Guard Brasil hook no ingest — todo `/ingest` roda via `guard_scan_pii` primeiro, redação automática, alerta no Telegram se PII detectada. | 4h

**P2 — Scale + evolução (mês 2+):**
- [ ] **KBS-020 [P2]**: Multi-idioma PT+EN no mesmo vault — tag `lang` no schema, query filter. Para clientes bilíngues. | 6h
- [ ] **KBS-021 [P2]**: Dream Cycle integration — KB linting automático noturno (batch `kb:lint` em todos tenants ativos). | 4h
- [ ] **KBS-022 [P2]**: Agente "KB-Librarian" — agente EGOS dedicado que mantém KB do cliente (dedup, sugere cross-refs, flagga staleness). Roda via hermes-gateway. | 8h
- [ ] **KBS-023 [P2]**: `/ingest` via web clipper — Chrome extension que envia URL para o KB do cliente. | 6h
- [ ] **KBS-024 [P2]**: Health dashboard por tenant — página Notion auto-atualizada com stats (total docs, staleness, queries/semana, linting score). | 4h
- [ ] **KBS-025 [P2]**: Vídeos de caso de uso por setor — jurídico, metal, saúde, consultoria. 2–3 min cada, PT-BR. | 8h
- [ ] **KBS-026 [P2]**: Certificação "EGOS Knowledge Implementer" — programa leve para parceiros que queiram revender serviço. | on-going

---

### API Monetization — x402 Marketplaces (carry-over 2026-04-07)
**SSOT:** `docs/strategy/KB_AS_A_SERVICE_PLAN.md` §4.2 + `~/.codeium/windsurf-next/API_MARKETPLACES_MASTER_ANALYSIS.md` | **Parent:** Camada B monetização
**Context:** Publicar Guard Brasil + (futuramente) knowledge-mcp + OSINT Brasil em marketplaces agent-native para receber USDC global via protocolo x402. AGENTCASH-001..012 foram consolidados em API-001..019.

**P0 — Tier 1 x402 native (0% comissão):**
- [ ] **API-001 [P0]**: AgentCash onboard — `npx agentcash@latest onboard AC-LZR4-C5AX-F5DH-EAB2` (rodar local, não sandbox). Salvar wallet info em vault. | 1h
- [ ] **API-002 [P0]**: APINow.fun provider signup — criar conta em `https://www.apinow.fun/providers`, instalar `apinow-sdk`. | 1h
- [ ] **API-003 [P0]**: Proxies.sx marketplace avaliação — verificar fit com OSINT Brasil scraping em `https://proxies.sx/marketplace`. | 1h
- [ ] **API-004 [P0]**: Wallet Base chain — criar wallet dedicada para receber USDC (não usar wallet pessoal). Documentar em `memory/infra_credentials_ssot.md`. | 1h
- [ ] **API-005 [P0]**: x402 middleware no Guard Brasil — branch `feat/x402-marketplaces`, middleware HTTP 402 que aceita USDC on-demand. | 6h
- [ ] **API-006 [P0]**: Publicar Guard Brasil v0.2.3 no AgentCash — primeiro deploy, pricing $0.001-0.005/call. | 3h

**P1 — Tier 1 expansão:**
- [ ] **API-007 [P1]**: Publicar Guard Brasil no APINow.fun — avaliar tokenization do endpoint popular. | 2h
- [ ] **API-008 [P1]**: Publicar OSINT Brasil scraping no Proxies.sx — match perfeito com 0% comissão. | 4h
- [ ] **API-009 [P1]**: OpenAPI spec universal — `openapi.yaml` que serve todos os marketplaces. | 3h
- [ ] **API-010 [P1]**: Dashboard monetização no HQ — mostra receita x402 por plataforma, calls/dia, top consumers. | 4h

**P2 — Tier 2 tradicionais:**
- [ ] **API-011 [P2]**: RapidAPI freemium listing do Guard Brasil (4M+ devs, 20% comissão). | 4h
- [ ] **API-012 [P2]**: Replicate — avaliar fit (foco ML models, pode não servir). | 2h
- [ ] **API-013 [P2]**: DigitalAPI — curated enterprise listing. | 3h
- [ ] **API-014 [P2]**: APILayer listing. | 2h
- [ ] **API-015 [P2]**: APYHub credits system. | 2h
- [ ] **API-016 [P2]**: Zyla Labs listing. | 2h
- [ ] **API-017 [P2]**: Mintlify docs sync para API portal. | 3h
- [ ] **API-018 [P2]**: Knowledge MCP publicado como API x402 — `@egosbr/knowledge-mcp` exposto via AgentCash após KBS-008 pronto. | 4h
- [ ] **API-019 [P2]**: x402 + Stripe hybrid billing — cliente escolhe crypto ou cartão na checkout. | 6h

---

### Session Carry-over — DISS + PAP + LS (2026-04-08 → próximas sessões)
**SSOT:** `docs/_current_handoffs/handoff_2026-04-08_end.md` | **Parent:** Track E manutenção
**Context:** Tasks pendentes do session end 2026-04-08. Não perder de vista enquanto KBS-* toma espaço.

**P0 — Desbloqueio GTM:**
- [ ] **XMCP-002 [P0]**: SSH VPS e rodar `cd /opt/xmcp && bash start.sh`. Keys já estão no .env. Desbloqueia GTM-002 (X thread demo). | 15min
- [ ] **DISS-002 [P0]**: `scripts/disseminate-propagator.ts` — propaga kernel blocks pós-scanner (DISS-001 ✅). Target: blocks de rules via `scripts/auto-disseminate.sh`. | 3h
- [ ] **DISS-003 [P0]**: `scripts/disseminate-verifier.ts` — re-verifica propagação (hash check). | 2h
- [ ] **DISS-005 [P0]**: Telegram approval gate para propagação — /approve antes de push. | 2h
- [ ] **PAP-002 [P0]**: Per-agent monthly token budget — estender Guard Brasil token counter com `monthly_cap` por agent_id, auto-pause + alerta 80%. | 3h

**P1 — GH-086 + LS-002 (Sprint 1 continuação):**
- [ ] **GH-086 [P1]**: `@egosbr/gem-hunter-mcp` — MCP server (3 tools: `gh_search`, `gh_trending`, `gh_score`) para Claude Code/Windsurf/Cursor. Blocked by §26 completion. | 6h
- [ ] **LS-002 [P2]**: Port EVA+GUARANI+MAIÊUTICA para TypeScript — ver seção Live School acima. | 6h

---

### KB-as-a-Service — Patos de Minas (KBS-PM-*) (2026-04-08)
**SSOT:** `docs/strategy/KBS_PATOS_DE_MINAS_PERSONAS.md` | **Notion workspace:** https://www.notion.so/33ce6358f08081ac8d41c001a87a7445
**Contexto:** 10 perfis profissionais de Patos de Minas criados no Notion via MCP. Templates com databases reais e dados demo. ERP replacement narrative: EGOS não substitui ERP — vira camada de inteligência em cima. Ingestão de DOC/DOCX/PDF/áudio/vídeo.
**Notion pages criadas:**
- 🧠 Root: https://www.notion.so/33ce6358f08081ac8d41c001a87a7445
- 🌾 Agrônomo: https://www.notion.so/33ce6358f08081159239f78684c78794
- ⚖️ Advocacia: https://www.notion.so/33ce6358f08081afa23de233c4e2639d
- 💰 Contador: https://www.notion.so/33ce6358f08081afbce2d227d3639f79
- 🏭 FORJA Demo: https://www.notion.so/33ce6358f08081a4baccd88685b62f29

**P0 — Dados demo + dogfooding (próximas 48h):**
- [x] **KBS-PM-001 [P0]**: Popular Agrônomo com 5 fazendas demo (Boa Vista/São João/Vereda/Estrela/Lagoa Azul) + 10 visitas técnicas + 8 defensivos aprovados com dados reais MAPA. | 3h ✅ 2026-04-08
- [x] **KBS-PM-002 [P0]**: Popular Advocacia com 8 processos demo TJMG + 5 jurisprudências STJ (direito agrário) + 3 modelos de petição posse rural. | 3h ✅ 2026-04-08
- [x] **KBS-PM-003 [P0]**: Popular Contador com 6 clientes rurais demo + 12 obrigações fiscais (ITR/Funrural/INSS) + 5 normas tributárias rurais. | 2h ✅ 2026-04-08
- [x] **KBS-PM-004 [P0]**: Popular FORJA com 8 peças demo (eixo/flange/bucha/suporte) + 5 orçamentos históricos + 3 atas de reunião transcritas. | 4h ✅ 2026-04-08
- [x] **KBS-PM-005 [P0]**: Escrever `CLAUDE.md` para cada perfil (5 arquivos, PT-BR) — contexto setorial, tom correto, limites, fontes prioritárias. Salvar em `packages/knowledge-mcp/templates/sectors/`. | 4h ✅ 2026-04-08
- [ ] **KBS-PM-006 [P0]**: Gravar Loom demo 5min PT-BR usando FORJA como exemplo — "Do orçamento em 2h para resposta em 10s". Usar dados demo populados. | 2h

**P1 — Completar perfis P1 com databases (próximas 2 semanas):**
- [x] **KBS-PM-007 [P1]**: Criar databases para Consultor de Gestão Rural (perfil 04) — Fazendas, Custo Produção, Benchmarks. | 2h ✅ 2026-04-08
- [x] **KBS-PM-008 [P1]**: Criar databases para Veterinário (perfil 05) — Pacientes, Medicamentos+carência, Protocolos+Vacinações. | 2h ✅ 2026-04-08
- [x] **KBS-PM-009 [P1]**: Criar databases para Engenheiro (perfil 06) — ARTs, Projetos, Normas Técnicas. | 2h ✅ 2026-04-08
- [x] **KBS-PM-010 [P1]**: Criar databases para Médico (perfil 07) — Protocolos Clínicos, Medicamentos, Regulação ANS/CFM. | 2h ✅ 2026-04-08
- [x] **KBS-PM-011 [P1]**: Popular perfis P1 com dados demo relevantes (5 registros cada, 12 databases). | 4h ✅ 2026-04-08
- [ ] **KBS-PM-012 [P1]**: PDF/áudio ingestor — plugar `unpdf` + `mammoth` + `whisper-api` no wiki-compiler. Input: pasta com arquivos mistos, output: atoms em egos_wiki_pages. | 8h
- [ ] **KBS-PM-013 [P1]**: Testar pipeline completo: ingestar 5 documentos reais de cada perfil P0 → query com citações → verificar accuracy. | 4h

**P1 — Narrativa ERP Replacement (posicionamento):**
- [x] **KBS-PM-014 [P1]**: Escrever 1-pager "Por que a Inteligência da Empresa substitui o ERP burro" em PT-BR. Foco em FORJA/metalurgia. Salvar em `docs/strategy/ERP_REPLACEMENT_NARRATIVE.md`. | 2h ✅ 2026-04-08
- [ ] **KBS-PM-015 [P1]**: Post X.com thread sobre ERP replacement + demo FORJA (3 tweets). Usar narrativa do 1-pager. Agendar via sistema de aprovação. | 1h
- [ ] **KBS-PM-016 [P1]**: Abordagem direta de 3 metalúrgicas em Patos de Minas via LinkedIn/WhatsApp — oferecer demo gratuita com dados deles. | 2h

**P2 — Completar perfis P2 + escala:**
- [ ] **KBS-PM-017 [P2]**: Criar databases para Cooperativa (perfil 08) — Cooperados, Preços, Insumos, CONAB, Safra. | 2h
- [ ] **KBS-PM-018 [P2]**: Criar databases para Imobiliária Rural (perfil 09) — Propriedades, CAR/CCIR, Histórico transações, Situação ambiental. | 2h
- [ ] **KBS-PM-019 [P2]**: Criar databases para SENAR/Escola (perfil 10) — Cursos, Competências, Experimentos, Turmas. | 2h
- [ ] **KBS-PM-020 [P2]**: Guia de replicação — documento PT-BR "Como duplicar e configurar em 15 minutos" para qualquer um dos 10 perfis. | 3h
- [ ] **KBS-PM-021 [P2]**: Gravar 2 vídeos demo adicionais: Advocacia (prazo processual em segundos) + Agrônomo (defensivo por carência). | 4h

---

### Gem Hunter — Feedback Loop v8 (2026-04-08)
**Context:** Root cause encontrado: `scoreGem()` em `gem-hunter.ts:1778` é heurística composta — Qwen só pontua papers. Low-star bonus só dispara com arXiv/PWC signal, por isso @zhuokaiz (Meta eng) foi subavaliado. Telegram alerts sem inline keyboard. `gem_feedback` table não existe.

**P1 — Fundações (fazer primeiro, desbloqueiam todo o resto):**
- [ ] **GH-089 [P1]**: Extrair scoring prompts hardcoded do `gem-hunter.ts:2274` → `docs/gem-hunter/prompts/scoring-v1.md` (versionado, editável sem deploy). | 2h
- [ ] **GH-090 [P1]**: Supabase migration: `gem_feedback(id uuid, alert_id text, gem_url text, reaction text, comment text, run_id text, created_at timestamptz)` + RLS policy (service role only). | 1h
- [ ] **GH-091 [P1]**: Qwen-based scoring para gems gerais (não só papers) — adicionar categoria `"low_visibility_research_gem"` em `scoreGem()`: big-tech eng + poucos likes/stars + código real = +25 pts. | 4h
- [ ] **GH-092 [P1]**: Telegram inline keyboard em alerts — botões 👍👎🔍💬 + webhook handler que salva em `gem_feedback`. Usar `sendMessage` com `reply_markup.inline_keyboard`. | 6h
- [ ] **GH-093 [P1]**: `scripts/scoring-feedback-reader.ts` — cron 2x/dia (09:00 + 21:00 BRT) lê `gem_feedback` → gera relatório `docs/jobs/scoring-feedback-YYYY-MM-DD.md` → auto-cria tasks via auto-disseminate. | 6h
- [ ] **GH-094 [P1]**: Repetition detector — hash URL+author, score -30 se mesma gem apareceu nos últimos 30 dias. Persistir hashes em `gem_seen_cache` table. | 3h
- [ ] **GH-095 [P1]**: `docs/gem-hunter/preferences.md` — SSOT de preferências co-editado Enio+AI: categorias valorizadas, red-flags, exemplos curados dos 8 posts analisados. | 2h

**P2 — Self-improvement loop:**
- [ ] **GH-096 [P2]**: HQ aba "Feedback Loop" — score drift chart, approve/reject rate, top false positives. | 8h
- [ ] **GH-097 [P2]**: `scripts/scoring-prompt-evolver.ts` — agrega feedback mensal, propõe rewrite de `scoring-v1.md` → Enio aprova via HQ → vira `scoring-v2.md`. | 6h

---

### X.com Reply Bot — Scoring Quality (2026-04-08)
**Context:** 8 posts analisados revelaram: Qwen subavalia low-visibility gems (ex: @zhuokaiz Meta eng, poucas stars); overvalue news (ex: @claudeai 92 pts); repetitivo não detectado (ex: @hasantoxr). Root cause: `min_likes` threshold em `x-reply-bot.ts` — scoring não usa Qwen diretamente para relevância, só para geração de reply.

**P1 — Fixes imediatos:**
- [ ] **XRB-001 [P1]**: Validar manualmente post `@claudeai/2041927687460024721` — feature útil ou notícia genérica? Se feature → criar task de integração. Se notícia → adicionar ao few-shot de rejeição. *(30min — ação manual do Enio ou pesquisa web)* | 30min
- [ ] **XRB-002 [P1]**: Update sistema de scoring com 8 few-shot examples em `x-reply-bot.ts` prompt: vacacafe/MrCl0wnLab/PreyWebthree/zhuokaiz/TFTC21 = gem (score +); hasantoxr/LOWTAXALT/claudeai-news = reject (score -). | 2h
- [ ] **XRB-003 [P1]**: Adicionar categoria "low-visibility gem" ao scoring: post de engenheiro de big-tech (Meta/Google/OpenAI em bio) com código real + poucos likes → score mínimo 70. | 3h
- [ ] **XRB-004 [P1]**: News-post detector: conta oficial (@claudeai, @openai, @anthropic) + padrão "announcing/introducing/launching" → penalidade -40 pts (não é gem, é PR corporativo). | 3h

---

### FORJA Chatbot Pilot — Referência (repo standalone)
**FORJA é repo standalone em `/home/enio/forja/`. Tasks FORJA adicionadas lá.**
- Tasks P0 em `/home/enio/forja/TASKS.md`: FORJA-003 (RLS), FORJA-004B (Design Oficina), FORJA-019B (Email Pipeline), FORJA-020 (WhatsApp bidirecional), FORJA-TOOLS-001 (budget_tool/cost_history/ata_extractor), FORJA-TOOLS-002 (Whisper), FORJA-KBS-001 (namespace EGOS Knowledge)
- KBS-003..007 já existem em egos/TASKS.md (seção KB-as-a-Service)
- Para trabalhar no FORJA: `cd /home/enio/forja && claude`

---

### Safety & Testing — Guard Brasil + ATRiAN (2026-04-08)
**Context:** Windsurf session identificou gap: faltam 50 amostras reais + k6 load test + fuzzing. ATRiAN ⊆ Guard (componente do resultado + uso standalone em 852).
- [ ] **SAFETY-001 [P1]**: Coletar 50 amostras de texto real da internet (notícias, tweets, docs públicos) contendo PII brasileiro para validar Guard Brasil + ATRiAN. Salvar em `packages/guard-brasil/test/fixtures/real-world-samples/`. | 1 dia
- [ ] **SAFETY-002 [P2]**: Prompt injection detection module — Guard Brasil extension: detecta tentativas de override ("ignore previous instructions", "você é um assistente diferente"). | 3 dias

---

### API Monetization — Carry-over + Novos (2026-04-08)
**Nota:** API-001..023 já existem em seção anterior. Abaixo apenas IDs novos.
- [ ] **API-024 [P2]**: Churn tracker — cliente sem chamadas à API por 14 dias → Telegram alert. Implementar como cron diário em `scripts/churn-tracker.ts` lendo `gem_hunter_usage` + billing events. | 3h

---

### Bugs e Incidentes de Sistema (2026-04-08)
**P1 — Auto-disseminate pipeline fix:**
- [x] **DISS-BUG-001 [P1]**: auto-disseminate faz match de task IDs em range notation (`KBS-001..026` → marca KBS-001 como done). Fix: adicionar guard que ignora IDs em contexto de range notation ou em commits com "fix/revert" no subject. Arquivo: `scripts/auto-disseminate.sh`. | 2h ✅ 2026-04-08

**P1 — LLMRefs staleness (19 links quebrados, job 2026-04-07):**
- [ ] **QA-001 [P1]**: Resolver 19 stale llmrefs em docs. Rodar `python3 scripts/qa/llmrefs_staleness.py --root . --fix` e revisar. Não-bloqueador mas polui CI. | 1h
