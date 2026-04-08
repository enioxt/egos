# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.49.0 | **Updated:** 2026-04-07 | **LAST SESSION:** MemPalace+CORAL+GovTech — 17 tasks criadas (MEM-001..004, CORAL-001..003, GOV-TECH-001..010), compressão seções legacy

---

### X.com Monitoring System (2026-04-07)
**SSOT:** `docs/social/X_POSTS_SSOT.md` | **Features Roadmap:** `docs/social/X_FEATURES_INTEGRATION_ROADMAP.md` | **Scripts:** `scripts/x-opportunity-alert.ts`, `scripts/x-approval-bot.ts`, `scripts/setup-x-monitoring.sh`
**Context:** Sistema completo de monitoramento de oportunidades X.com. Busca automática a cada 2h, alertas WhatsApp/Telegram, aprovação manual via bot. Integrando melhores features de ferramentas pagas (AutoTweet, TweetHunter, Hypefury) em solução própria self-hosted.

**✅ DONE 2026-04-07/08:** X-COM-001..005 (alert+approval bots, setup, SSOT templates, roadmap) | X-COM-018..024 (LLM analysis layer DashScope+OpenRouter, recordFeedback, HTML format, diagnostic — all in `scripts/x-opportunity-alert.ts`)

**P0 — Deploy + Core (Esta semana):**
- [ ] **X-COM-006**: Adaptar setup script para `/opt/x-automation/` (evitar conflito com `/opt/xmcp` existente)
- [ ] **X-COM-007**: Deploy no VPS — testar alertas end-to-end Telegram/WhatsApp
- [ ] **X-COM-008**: x-smart-scheduler.ts — análise de audiência para melhores horários
- [ ] **X-COM-009**: x-evergreen-recycler.ts — recompartilhamento inteligente de top posts

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
- [ ] **HQC-009**: Build `@egosbr/guard-brasil-mcp` and register OpenClaw/ClawHub path
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
- [ ] GTM-002-unblock: Post Guard Brasil thread after XMCP-001

---

### Block Intelligence + Eagle Eye (compressed)
**WM-001..008:** Local LLM + world model (P2, post-PMF). **INTEL-006..010:** Proactive detection, mermaid, DRI auto-assign (P1-P2). SSOT: `docs/strategy/WORLD_MODEL_SSOT.md`
**Eagle Eye v2:** EAGLE-GH-001..005 done. P0: GH-003/004 (classification/extraction). Deadline: EAGLE-023 R$250k proposal 2026-04-29.
- [ ] MONETIZE-011: Deploy v0.2.3 to VPS with STRIPE_METER_ID env var
- [ ] MONETIZE-012: NOWPayments webhook URL config — ENIO action required

### Partnership & Distribution Strategy (2026-04-05)
**Compressed:** See `docs/GTM_SSOT.md` + `docs/MONETIZATION_SSOT.md` for full roadmap.
- [ ] **PART-001**: Publish npm + ProductHunt (M-007 emails first)
- [/] **M-007**: 3/5 enviados ✅ (Nubank, Memed, RD Station). 2 falharam — endereços inválidos: contact@lgpd-brasil.com.br (domínio não existe), contato@rocketseat.com.br (não aceita). Buscar emails corretos.
- [ ] **M-007-FIX**: Encontrar emails corretos para Rocketseat (site: rocketseat.com.br) e LGPD Brasil (site: lgpdbrasil.com.br ou lgpd-brasil.info)
- [ ] **PART-016**: Decide PARTNER-D1 co-founder model

---

### Evaluated & Deferred (2026-04-05)

**HiClaw (agentscope-ai/HiClaw):** Analyzed. Matrix rooms + MinIO + Higress = overhead for zero users. Already have WhatsApp gateway + Caddy + Supabase. **SKIP.**
**PAL (agno-agi/pal):** Analyzed. Compiler + Linter pattern adopted via wiki-compiler agent. Syncer not needed (Supabase > Git sync). **ADOPTED partially.**
**Karpathy LLM Wiki gist:** Adopted. 3-layer pattern (raw → wiki → schema) is now KB-001..007. **ADOPTED fully.**
**Fine-tuning próprio (Gemma 2B/Qwen 7B):** VPS has 540MB free RAM, 0 GPU. Fine-tune on Colab is possible but not 90-day focus. WM-001..004 covers dataset prep. **DEFERRED to P2.**

### GTM & Incidents (P25-P35)

**SSOT:** `docs/GTM_SSOT.md` | **ICP:** CTOs/backend devs at fintechs+healthtechs (confirmed).  
**INC-001 (2026-04-06):** Force-push incident — recovered. Mitigations: `.husky/pre-push` blocks, GitHub branch protection enabled, CLAUDE.md §25 added.

**P0 — Social & Outreach:**
- [/] **M-007**: 3/5 enviados (Nubank, Memed, RD Station). Ver M-007-FIX acima.
- [ ] **GTM-002**: X.com thread demo (4 tweets, drafts ready)
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
- [ ] GTM-016: Build `guard-brasil-mcp` — wraps guard.egos.ia.br as Claude tool, publish as `@egosbr/guard-brasil-mcp` (GTM play: devs install it in their Claude session)
- [ ] KB-019: `bun wiki:dedup` — fix HARVEST.md 1944-line triplication caused by wiki:compile running without dedup

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

### ~~OpenClaw Integration Roadmap~~ — DECOMMISSIONED 2026-04-08
**OC-006..034 CANCELED.** ChatGPT subscription cancelled → Codex proxy + billing proxy + OpenClaw gateway removed. Replaced by DashScope qwen-plus + OpenRouter free fallback (see §16 CAPABILITY_REGISTRY) + Hermes systemd service. Channels (WhatsApp/Telegram) continue via existing Evolution API + egosin_bot direct.

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
- [ ] **XMCP-002** [UNBLOCKED]: Atualizar /opt/xmcp/.env no VPS com X keys rotados + iniciar serviço
- [ ] **SOCIAL-003 [P1]**: x-reply-bot — busca por "LGPD", "licitação", "split payment", "análise de vínculos"
- [ ] **SOCIAL-004 [P1]**: Fila Supabase de DMs candidatas para aprovação manual via Telegram antes de enviar
- [ ] **SOCIAL-005 [P2]**: Reply automático a @mentions com link produto relevante (aprovação manual)
- [ ] **SOCIAL-006 [P2]**: HQ dashboard tab social — candidatos DM, DMs enviadas, respostas
- [ ] **XMCP-003** (dep: XMCP-002): Adicionar UFW rule VPS: `ufw allow from 172.19.0.0/16 to any port 8000`. Ativar x-mcp no openclaw.json (remover nota INACTIVE).
- [ ] **XMCP-004** (dep: XMCP-002): Criar skill `egos-x-researcher` — usa XMCP searchPostsRecent para monitorar: lgpd, anpd, dpo, "proteção de dados". Saída → Supabase + HQ.
- [ ] **GTM-002-unblock**: Thread Guard Brasil (4 tweets prontos em GTM_SSOT.md §4.1) — BLOQUEADO por X credentials 401. Usar `bun /tmp/post-guard-thread.ts` após XMCP-001.

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

### Ratio VPS Deployment (2026-04-07)
**Context:** Ratio deployed on VPS — ratio-api:3085 + ratio-frontend:3086 live. Guard Brasil connected (PII enabled). Caddy routes: ratio.egos.ia.br + ratio-api.egos.ia.br. .env synced (Gemini/OpenRouter/Alibaba/Anthropic keys).


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

- [ ] **CORAL-001 [P1]**: Criar tabela Supabase `gem_discoveries`. Schema: `{id, repo_url, gem_name, category, score, discovered_by, discovered_at, summary, tags[], last_seen_at}`. RLS habilitado. Migration em `supabase/migrations/`. [1h]
- [ ] **CORAL-002 [P1]** (dep: CORAL-001): Modificar Gem Hunter stage-1 para consultar `gem_discoveries` antes de scrape. Skip repos score ≥ 7 nos últimos 14 dias. Log: "X repos skipped (already discovered)". Esperado: 30-50% redução em API calls. [3h]
- [ ] **CORAL-003 [P2]** (dep: CORAL-001): Hermes escreve em `gem_discoveries` após research tasks. Qualquer agent que encontrar "gem" (tool/pattern relevante) chama `event-bus.ts` → upsert `gem_discoveries`. [2h]

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

### Git Workflow — Branch Protection (INC-001 follow-up)
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


