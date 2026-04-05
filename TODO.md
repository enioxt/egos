# TODO.md — EGOS Unified Task List

> **Updated:** 2026-04-05 | **Open:** 104 | **Done (archived):** 150+ | **MRR:** R$0
> **Focus:** Guard Brasil + Gem Hunter (até Jun/26) | **Goal:** R$30k+ MRR

---

## URGENTE — Fazer HOJE

| # | Task | Owner | Tempo | Notas |
|---|------|-------|-------|-------|
| 1 | **M-007: Enviar 5 emails outreach** | ENIO | 30min | Templates em docs/business/OUTREACH_EMAIL_TEMPLATES.md |
| 2 | Privy: add guard.egos.ia.br nos domínios | ENIO | 5min | Dashboard Privy → Settings → Allowed Origins |
| 3 | Privy: ativar HttpOnly cookies | ENIO | 1min | Toggle na mesma tela |
| 4 | Gravar vídeo demo 30s (Loom) | ENIO | 5min | Roteiro em docs/strategy/GUARD_BRASIL_WEBSITE_CRITIQUE.md |
| 5 | Post X.com + LinkedIn com vídeo | ENIO | 15min | Usar imagens em public/ |

---

## P0 — Revenue (Guard Brasil)

| ID | Task | Owner | Est. |
|----|------|-------|------|
| EGOS-163 | Pix billing integration (Stripe Pix) | Claude | 3h |
| GH-063 | x402 pay-per-call (M2M agent payments via Coinbase) | Claude | 4h |
| CRYPTO-001 | NOWPayments integration (350+ coins) | Claude + ENIO (conta) | 4h |
| MONETIZE-010 | Stripe checkout button funcional na landing | Claude | 1h |
| MONETIZE-011 | Deploy v0.2.3 ao VPS com STRIPE_METER_ID | Claude | 30min |

---

## P0 — Master API (Habilita WhatsApp/Telegram commands)

| ID | Task | Owner | Est. |
|----|------|-------|------|
| MASTER-003 | Evolution webhook → gateway routing | Claude | 30min |
| MASTER-004 | Deploy gateway Docker VPS (porta 3050) | Claude | 1h |
| MASTER-005 | NLP intent classifier (Haiku) | Claude | 2h |

---

## P1 — Frontend & Marketing

| ID | Task | Owner | Est. |
|----|------|-------|------|
| WEB-001 | Integrar hero image na landing (hero-shield.jpg) | Claude | 30min |
| WEB-002 | Seção "Como Funciona" (3 passos) | Claude | 1h |
| WEB-003 | Tabela comparação vs Presidio/AWS/Google | Claude | 30min |
| WEB-004 | Footer profissional (links, termos, contato) | Claude | 30min |
| WEB-005 | DashboardV1Giant mobile responsive (sidebar) | Claude | 1h |
| WEB-006 | Integrar Privy login (auth + embedded wallet) | Claude | 2h |
| GH-061 | Dashboard gemhunter.egos.ia.br | Claude | 8h |
| EGOS-165 | White-label outreach | ENIO | ongoing |
| EGOS-166 | REST API gateway mode | Claude | 4h |

---

## P1 — Knowledge System (criado P21)

| ID | Task | Owner | Est. |
|----|------|-------|------|
| KB-008 | wiki:compile no Governance Drift CCR | Claude | 1h |
| KB-009 | /start Phase 0 com KB stats | Claude | 1h |
| KB-010 | Record learnings on /end | Claude | 2h |
| KB-011 | Guard Brasil KB tab no dashboard | Claude | 2h |
| KB-012 | Cross-reference enrichment | Claude | 3h |
| KB-013 | Deduplication de páginas similares | Claude | 2h |
| KB-014 | LLM summarization (<60 score) | Claude | 3h |
| KB-015 | Full-text search (pgvector) | Claude | 4h |
| KB-016 | Knowledge graph visualization | Claude | 4h |
| KB-017 | Auto-learning from git commits | Claude | 3h |
| KB-018 | MCP server knowledge-mcp | Claude | 4h |

---

## P1 — Infraestrutura & Monitoring

| ID | Task | Owner | Est. |
|----|------|-------|------|
| START-006 | Monitor /start performance 1 semana | Claude | ongoing |
| START-007 | v6.1 distributed health (SSH parallel) | Claude | 4h |
| START-008 | Dashboard integration Grafana | Claude | 4h |
| START-009 | Telegram alerts health < 40% | Claude | 1h |
| EGOS-169 | @aiready/pattern-detect pre-commit | Claude | 3h |
| EGOS-173 | CRCDM hooks: llmrefs staleness | Claude | 2h |
| CTX-001 | Context recovery hook no /start | Claude | 1h |
| CTX-002 | Auto-index codebase-memory-mcp | Claude | 1h |
| DASH-001 | Avaliar ClawBridge/mission-control | Claude | 2h |
| DASH-002 | Mobile dashboard (agents, costs, WA) | Claude | 8h |

---

## P1 — Gem Hunter

| ID | Task | Owner | Est. |
|----|------|-------|------|
| GH-013 | Study: EGOS ↔ OpenHands | Claude | 2h |
| GH-014 | Study: EGOS ↔ LangGraph | Claude | 2h |
| GH-015 | Study: EGOS ↔ OpenAI Agents SDK | Claude | 2h |
| GH-016 | Study: EGOS ↔ LiteLLM | Claude | 2h |
| GH-017 | Study: EGOS ↔ Langfuse | Claude | 2h |
| GH-025 | /pr workflow + GitHub App | Claude | 4h |
| GH-026 | codebase-memory-mcp HTTP/SSE | Claude | 4h |
| GH-027 | .guarani/checks/ markdown-as-config | Claude | 3h |
| GH-032 | EGOS edit benchmark (SWE-Bench) | Claude | 4h |
| GH-036 | OpenHarness adapter | Claude | 3h |
| GH-066 | Paper → Code generator | Claude | 8h |
| GH-070 | Crypto X.com KOL monitoring | Claude | 3h |
| GH-071 | Daily X.com auto-scan | Claude | 2h |

---

## P1 — X.com Presence

| ID | Task | Owner | Est. |
|----|------|-------|------|
| X-006 | Capability profiles in rapid-response.ts | Claude | 2h |
| X-007 | --post-thread flag | Claude | 2h |
| X-008 | Daily X report to Telegram | Claude | 2h |
| X-009 | Trending topic scanner | Claude | 3h |
| X-010 | Clean showcase branch creator | Claude | 2h |
| X-011 | Upgrade to Basic tier ($100/mo) | ENIO | decision |
| X-012 | Thread scheduler (multi-tweet) | Claude | 3h |
| X-013 | Analytics dashboard | Claude | 4h |

---

## P2 — Eagle Eye (Licitações)

| ID | Task | Owner | Est. |
|----|------|-------|------|
| EAGLE-009 | Stripe/Pix Pro tier | Claude | 3h |
| EAGLE-011 | E2E tests Playwright | Claude | 4h |
| EAGLE-019 | Integrador outreach | ENIO | ongoing |
| EAGLE-020 | Proposta R$250k (deadline 2026-04-29) | ENIO | 4h |
| EAGLE-GH-003 | classification-service.ts | Claude | 3h |
| EAGLE-GH-004 | extraction-service.ts | Claude | 3h |
| EAGLE-GH-006 | profile-service.ts | Claude | 3h |
| EAGLE-GH-007 | feedback-learning.ts | Claude | 3h |
| EAGLE-GH-008 | REST API v2 | Claude | 4h |
| EAGLE-GH-009 | MCP server eagle-eye-mcp | Claude | 4h |
| EAGLE-GH-010 | Stripe Pix Eagle Eye | Claude | 2h |
| EAGLE-GH-011 | Dashboard v2 radar chart | Claude | 6h |
| EAGLE-GH-012 | Telegram alert routing | Claude | 2h |
| EAGLE-GH-013 | Chatbot interface | Claude | 4h |
| EAGLE-021 | Proposal generator | Claude | 4h |
| EAGLE-022 | Compliance checklist | Claude | 3h |
| EAGLE-023 | Submit proposta 2026-04-29 | ENIO | deadline |

---

## P2 — Outros

| ID | Task | Owner | Est. |
|----|------|-------|------|
| COMM-002 | Document commons services | Claude | 1h |
| SANT-001 | Santiago partner onboarding | ENIO | waiting |
| EGOS-128 | Python imports + Docker rename | Claude | 4h |
| EGOS-129 | Docker network rename Hetzner | Claude | 2h |
| GH-020 | Study: Mem0 | Claude | 2h |
| GH-021 | Study: Temporal TS SDK | Claude | 2h |
| GH-022 | Study: Haystack | Claude | 2h |
| GH-023 | Study: DSPy | Claude | 2h |
| GH-024 | Lego Assembler agent | Claude | 4h |
| HERMES-001 | Hermes-3 BRAID executor | Claude | 4h |
| OPENCLAW-001 | Guard Brasil as OpenClaw skill | Claude | 2h |
| REWARDS-001 | Unified rewards engine | Claude | 8h |
| MOAT-001 | Data flywheels | Claude | ongoing |

---

## DEFERRED (Pós Jun/26 — World Model)

| ID | Task |
|----|------|
| WM-001..004 | Local LLM setup + integration |
| WM-005..008 | Dynamics model + causal discovery |
| WM-009..012 | Ethics + safety + intervention |
| WM-013..016 | AGI capabilities (auto-observação, auto-modificação) |
| INTEL-005..010 | Signal layer + proactive detection |

---

## Resumo

| Prioridade | Total | Claude | ENIO |
|------------|-------|--------|------|
| URGENTE (hoje) | 5 | 0 | 5 |
| P0 Revenue | 5 | 4 | 1 |
| P0 Master API | 3 | 3 | 0 |
| P1 Frontend | 9 | 8 | 1 |
| P1 Knowledge | 11 | 11 | 0 |
| P1 Infra | 10 | 10 | 0 |
| P1 Gem Hunter | 13 | 13 | 0 |
| P1 X.com | 8 | 7 | 1 |
| P2 Eagle Eye | 17 | 14 | 3 |
| P2 Outros | 13 | 10 | 3 |
| DEFERRED | 16 | 16 | 0 |
| **TOTAL** | **110** | **96** | **14** |

**96 tasks são minhas (Claude). 14 são suas (ENIO). R$0 MRR porque M-007 não foi feito.**
