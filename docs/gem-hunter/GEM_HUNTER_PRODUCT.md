# Gem Hunter — Product Spec v1.0
> SSOT: This document. Updated: 2026-04-04. Owner: Enio Rocha.

## Vision

Gem Hunter is a **discovery-as-a-service** product: it finds the world's best open-source tools, papers, models, and frameworks for developers, researchers, and builders — by sector, by need, in real time.

**Delivery layers:**
1. **API** — REST API for programmatic discovery (B2B, developers)
2. **Chatbot** — WhatsApp/Telegram bot with natural language queries (B2C)
3. **AI Agents** — Orchestrator behind the chatbot, tool-calling gem-hunter

---

## Sectors (Focus for 90-day window)

| Sector | Keywords | Audience |
|--------|----------|----------|
| AI/LLM | agents, MCP, orchestration, LLM, tool use | AI engineers |
| Crypto | DeFi, x402, blockchain, on-chain payments | Web3 builders |
| Systems Dev | runtime, compiler, bun, TypeScript, Rust | Backend devs |
| Agent Orchestration | swarm, multi-agent, A2A, coordination | AI architects |
| Governance/Rules | SSOT, compliance, policy, audit, governance | Platform teams |
| Research | arXiv, papers, benchmarks, implementations | Researchers |

---

## Architecture

```
User Query
    │
    ├── API caller ──────────────────────► POST /v1/hunt {topic, sector, limit}
    │                                           │
    └── WhatsApp/Telegram ──────────────► egos-gateway /channels/whatsapp
                                               │
                                    Orchestrator Agent (Qwen2.5)
                                               │ tool calls
                                    ┌──────────┴──────────┐
                                    │                     │
                               gem-hunter             wiki-compiler
                               (discover)             (synthesize)
                                    │                     │
                                    └──────────┬──────────┘
                                               │
                                      Ranked Results + AI synthesis
                                               │
                                         Return to user
```

**Orchestrator agent logic (chatbot flow):**
1. Parse user intent: `"find me best agent orchestration tools"`
2. Extract sector + optional filters (language, min-stars, recency)
3. Call `GET /gem-hunter/sector/{sector}` or trigger `POST /v1/hunt`
4. If async hunt: wait for job completion (poll `/v1/jobs/:id`)
5. Post-process: rank by relevance to user query, summarize top 5
6. Reply with curated list + "want more?" follow-up

---

## Revenue Model

| Tier | Price | Limits | Extras |
|------|-------|--------|--------|
| **Free** | R$0/mo | 5 searches/day, top 5 results | GitHub + arXiv only |
| **Starter** | R$99/mo | 50 searches/day, top 20 results | 4 sources, email delivery |
| **Pro** | R$499/mo | Unlimited, top 100, all sectors | AI synthesis, webhooks, history export |
| **Pay-per-use** | R$0.15/search | Top 20, all sectors | No monthly commitment |
| **Chatbot** | R$149/mo | 200 chatbot queries/mo | WhatsApp + Telegram |

**Revenue path (90-day):**
- Month 1: 5 Starter + 2 Pro = R$2.5k MRR
- Month 2: 15 Starter + 5 Pro = R$4k MRR
- Month 3: 30 Starter + 10 Pro + 20 Pay-per-use = R$8k MRR
- **Target:** R$10k MRR from Gem Hunter by June 30, 2026

---

## Implementation Roadmap

### Week 1 — API Public Launch
- [x] GH-058: Standalone API (port 3097) — `/v1/hunt`, `/v1/findings`, `/v1/papers`
- [x] GH-065: Pricing/billing module
- [ ] **GH-066**: Deploy gem-hunter-server to VPS (gemhunter.egos.ia.br, port 3097)
- [ ] **GH-067**: Caddy routing: `gemhunter.egos.ia.br → :3097`
- [ ] **GH-068**: Auth: issue API keys via Supabase `gem_hunter_api_keys` table
- [ ] **GH-069**: Rate limiting middleware (tier-aware, by API key)

### Week 2 — Dashboard (GH-061)
- [ ] **GH-061**: gemhunter.egos.ia.br web dashboard
  - Findings feed (latest gems by category)
  - Trending over time (SQLite → Supabase sync)
  - Sector filters + search
  - API key management
  - Tech: Next.js in `apps/gem-hunter-web/` OR extend guard-brasil-web

### Week 3 — Chatbot
- [ ] **GH-070**: Orchestrator agent in WhatsApp channel
  - Natural language intent parser (Qwen via callAI)
  - Tool definitions: search_gems(sector, limit), get_trends(), get_paper()
  - Tool dispatch → gem-hunter-server API
  - Response formatter (top 5 gems with one-liner each)
- [ ] **GH-071**: Telegram bot (separate from WhatsApp)
  - `/hunt <query>` slash command
  - `/trending` — weekly top gems
  - `/sector ai|crypto|systems|agents|governance` — filtered feed
- [ ] **GH-072**: Chatbot tier enforcement (200 queries/mo for R$149/mo)

### Ongoing
- [ ] **GH-073**: Email digest — weekly Gem Hunter report (top 10 gems) to subscribers
- [ ] **GH-074**: NPM package `@egosbr/gem-hunter` public release with API client
- [ ] **GH-075**: Webhook delivery — POST to customer URL on each new top-scoring gem

---

## Current State (2026-04-04)

| Component | Status | Notes |
|-----------|--------|-------|
| gem-hunter.ts v6.1 | ✅ Running | 2249 lines, 20+ topics, 12 sources |
| Standalone API (3097) | ✅ Built | Not deployed to VPS yet |
| Gateway API (/gem-hunter) | ✅ Built | Sector filtering, product pricing |
| Knowledge UI (/ui) | ✅ Built | Visual dashboard for wiki pages |
| Dashboard web | ❌ Pending | GH-061 — highest priority |
| Chatbot (WhatsApp) | ❌ Pending | GH-070 — Week 3 |
| VPS Deploy | ❌ Pending | GH-066/067 — Week 1 |
| Auth + Rate limiting | ❌ Pending | GH-068/069 — Week 1 |

---

## Gem Hunter vs Guard Brasil

| | Guard Brasil | Gem Hunter |
|--|-------------|------------|
| **Core** | PII/LGPD compliance | Open-source discovery |
| **Target** | Enterprise, compliance teams | Developers, researchers, builders |
| **Pricing** | R$0.02/call, R$99+ tiers | R$99-499/mo or R$0.15/search |
| **Status** | Live (guard.egos.ia.br) | API built, not deployed |
| **MRR goal** | R$20k+ | R$10k+ |
| **Timeline** | Production now | Deploy Week 1 |

Both products together: **R$30k+ MRR by June 30, 2026** ✅

---

*v1.0.0 — 2026-04-04 | Session: R&D — Knowledge + Revenue strategy*
