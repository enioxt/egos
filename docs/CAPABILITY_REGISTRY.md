# EGOS Capability Registry

> **VERSION:** 1.3.0 | **UPDATED:** 2026-03-21
> **PURPOSE:** Master index of all capabilities across the EGOS ecosystem
> **SSOT STATUS:** This file IS the canonical capability map

---

## How to Read This Registry

Each capability has:
- **SSOT**: The canonical source (best implementation)
- **Quality**: A/B/C rating (A = production-proven, B = functional, C = prototype)
- **Adopted By**: Repos currently using it
- **Should Adopt**: Repos that would benefit from adoption
- **Tags**: For filtering and cross-referencing

---

## 1. CHATBOT & CONVERSATION

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| Modular Prompt Architecture | `egos/docs/modules/CHATBOT_SSOT.md` | A | 852, intelink, forja, egos-web | carteira-livre, br-acc | `chatbot`, `prompt`, `composable`, `ssot` |
| ATRiAN Ethical Validation | `egos/packages/shared/src/atrian.ts` | A | 852 (origin), egos, intelink, carteira-livre, forja, egos-web, br-acc | — | `chatbot`, `ethics`, `validation`, `atrian` |
| PII Scanner (Brazilian) | `egos/packages/shared/src/pii-scanner.ts` | A | 852 (origin), egos, intelink, carteira-livre, forja, egos-web, br-acc | — | `chatbot`, `privacy`, `lgpd`, `pii` |
| Conversation Memory | `egos/packages/shared/src/conversation-memory.ts` | A | 852 (origin), egos, intelink, carteira-livre, forja, egos-web, br-acc | — | `chatbot`, `memory`, `context` |
| Task-Based Model Routing | `852/src/lib/ai-provider.ts` | A | 852, intelink, carteira-livre, forja, egos-web (basic) | br-acc | `chatbot`, `ai`, `routing`, `cost` |
| AI Conversation Review | `852/src/app/api/review/route.ts` | A | 852 | forja | `chatbot`, `review`, `quality` |
| Smart Correlation Engine | `852/src/app/api/correlate/route.ts` | A | 852 | forja, intelink | `chatbot`, `correlation`, `ai` |
| Chat Streaming (Vercel AI SDK) | `852/src/app/api/chat/route.ts` | A | 852, intelink | forja | `chatbot`, `streaming`, `api` |
| Export (PDF/DOCX/MD/WhatsApp) | `852/src/components/chat/ExportMenu.tsx` | A | 852 | forja, intelink | `chatbot`, `export`, `pdf` |
| Hot Topics / Trending | `852/src/app/api/hot-topics/route.ts` | A | 852 | — | `chatbot`, `community`, `engagement` |
| Tool-Calling Chat (27 tools) | `br-acc/api/src/bracc/routers/chat.py` | A | br-acc | forja (adapted) | `chatbot`, `tools`, `python` |
| Public Guard / LGPD Masking (Python) | `br-acc/api/src/bracc/services/public_guard.py` | A | br-acc | forja | `privacy`, `lgpd`, `masking` |
| **Public Guard BR (TypeScript)** | `egos/packages/shared/src/public-guard.ts` | A | egos | carteira-livre, forja, egos-web | `privacy`, `lgpd`, `masking`, `guard-brasil` |
| **Evidence Chain** | `egos/packages/shared/src/evidence-chain.ts` | A | egos | 852, forja, br-acc | `evidence`, `traceability`, `audit`, `guard-brasil` |

### Guard Brasil Stack

> **EGOS Guard Brasil** — ATRiAN + PII Scanner + Public Guard + Evidence Chain.
> Full product definition: `docs/products/GUARD_BRASIL.md`
> CLI: `bun scripts/guard.ts` or `npm run guard:demo`

### Canonical Standard

> **`egos/docs/modules/CHATBOT_SSOT.md`** — Every chatbot MUST follow this spec.

---

## 2. AI & LLM INFRASTRUCTURE

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| Multi-LLM Provider (TS) | `egos/packages/shared/src/llm-provider.ts` | B | egos, egos-lab | 852 (has own) | `ai`, `provider`, `shared` |
| AI Client (OpenRouter) | `egos-lab/packages/shared/src/ai-client.ts` | A | egos-lab, telegram-bot | forja | `ai`, `client`, `openrouter` |
| Rate Limiter (shared) | `egos-lab/packages/shared/src/rate-limiter.ts` | A | egos-lab | forja | `ai`, `rate-limit`, `shared` |
| Cost Tracking (per-request) | `852/src/lib/ai-provider.ts` | A | 852 | ALL | `ai`, `cost`, `budget` |
| Budget Mode (conservative/balanced) | `852/src/lib/ai-provider.ts` | A | 852 | forja | `ai`, `cost`, `config` |
| Prompt System (meta-prompts) | `.guarani/prompts/PROMPT_SYSTEM.md` | B | egos | egos-lab | `ai`, `prompt`, `meta` |

---

## 3. AUTHENTICATION & IDENTITY

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| Anonymous Identity (nicknames) | `852/src/lib/nickname-generator.ts` | A | 852 | — | `auth`, `anonymous`, `privacy` |
| AI Name Validator | `852/src/lib/name-validator.ts` | A | 852 | — | `auth`, `privacy`, `ai` |
| PBKDF2 + Supabase Sessions | `852/src/lib/user-auth.ts` | A | 852 | — | `auth`, `supabase`, `sessions` |
| MASP Registration Flow | `852/src/app/api/auth/register/route.ts` | A | 852 | — | `auth`, `registration`, `domain` |
| Supabase Auth (GoTrue) | `carteira-livre/services/api-utils.ts` | A | carteira-livre | forja | `auth`, `supabase`, `rbac` |
| Admin Auth | `852/src/lib/admin-auth.ts` | B | 852 | — | `auth`, `admin` |

---

## 4. GOVERNANCE & SSOT

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| Governance Symlink Converter (legacy) | `~/.egos/governance-symlink.sh` | C | Manual cleanup only | — | `governance`, `symlink`, `legacy` |
| Governance Sync Plane | `egos/scripts/governance-sync.sh` + `~/.egos/sync.sh` | A | Kernel + synced leaves | — | `governance`, `sync`, `ssot` |
| SSOT Registry | `egos/docs/SSOT_REGISTRY.md` | A | egos (canonical) | ALL | `governance`, `ssot`, `registry` |
| Pre-commit Drift Detection | `.husky/pre-commit` | A | carteira-livre, forja | — | `governance`, `drift`, `hooks` |
| CRCDM Universal Hook | `scripts/hooks/crcdm-pre-commit.sh` → `~/.egos/hooks/pre-commit` | A | ALL (symlink) | — | `governance`, `security`, `crcdm`, `hooks` |
| Cross-Repo Health Dashboard | `egos/scripts/egos-repo-health.sh` | A | egos (run before installers) | — | `observability`, `governance`, `git` |
| Context Persistence (Fibonacci) | `scripts/context-manager.ts` + `/snapshot` command | A | ALL (9 repos) | — | `context`, `session`, `persistence` |
| Secret Leak Detection | `.gitleaks.toml` + CRCDM hook regex | A | ALL | — | `security`, `secrets`, `compliance` |
| Context Tracker | `egos/agents/agents/context-tracker.ts` | A | egos | ALL | `governance`, `context`, `observability` |
| SSOT Drift Check | `egos-lab/scripts/ssot-drift-check.ts` | A | egos-lab | — | `governance`, `drift`, `api` |
| API Registry Check | `egos-lab/scripts/ssot-api-registry-check.ts` | A | egos-lab | — | `governance`, `api`, `drift` |
| Orchestration Pipeline (7-phase) | `.guarani/orchestration/PIPELINE.md` | A | ALL | — | `governance`, `pipeline`, `frozen` |
| Frozen Zones | `egos/.windsurfrules` | A | ALL | — | `governance`, `frozen`, `security` |

---

## 5. AGENT RUNTIME

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| Agent Runner | `egos/agents/runtime/runner.ts` | A | egos (FROZEN) | — | `agent`, `runtime`, `frozen` |
| Event Bus | `egos/agents/runtime/event-bus.ts` | A | egos (FROZEN) | — | `agent`, `events`, `frozen` |
| Agent Registry | `egos-lab/agents/registry/agents.json` | A | egos-lab (29) | egos (2) | `agent`, `registry`, `ssot` |
| Agent CLI | `egos-lab/agents/cli.ts` | A | egos-lab | egos | `agent`, `cli` |
| Worker Infrastructure | `egos-lab/agents/worker/` | B | egos-lab (Railway) | — | `agent`, `worker`, `infra` |

---

## 6. DEPLOYMENT & INFRA

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| Docker + Caddy + VPS | `852/docker-compose.yml` | A | 852, br-acc | forja | `deploy`, `docker`, `vps` |
| One-Command Release | `852: npm run release:prod` | A | 852 | forja | `deploy`, `release`, `automation` |
| Vercel Auto-Deploy | `egos-lab/apps/egos-web` | A | egos-lab | — | `deploy`, `vercel` |
| Brand Import (Stitch) | `852: npm run brand:import` | B | 852 | — | `deploy`, `assets`, `stitch` |
| Smoke Tests (curl) | `852: npm run smoke:public` | A | 852 | ALL VPS projects | `deploy`, `smoke`, `testing` |

---

## 7. TELEMETRY & OBSERVABILITY

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| Dual Telemetry (logs + Supabase) | `852/src/lib/telemetry.ts` | A | 852 | forja | `telemetry`, `logging`, `supabase` |
| Microsoft Clarity | `852/src/components/ClarityAnalytics.tsx` | A | 852, egos-lab | forja | `telemetry`, `analytics` |
| ATRiAN Violations Dashboard | `852/src/app/admin/telemetry/page.tsx` | A | 852 | — | `telemetry`, `atrian`, `admin` |
| Activity Feed | `br-acc/api/src/bracc/routers/activity.py` | A | br-acc | forja | `telemetry`, `feed`, `audit` |
| Rho Health Score | `egos-lab/scripts/rho.ts` | B | egos-lab | egos | `telemetry`, `health`, `score` |

---

## 8. GAMIFICATION & ENGAGEMENT

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| Points + Ranks (Recruta-Comissario) | `852/src/lib/gamification.ts` | A | 852 | — | `gamification`, `ranks`, `engagement` |
| Leaderboard API | `852/src/app/api/leaderboard/route.ts` | A | 852 | — | `gamification`, `leaderboard` |
| Voting (issues upvote/downvote) | `852/src/app/issues/page.tsx` | A | 852 | — | `gamification`, `voting`, `community` |

---

## 9. WHATSAPP & MESSAGING

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| Evolution API Client | `carteira-livre/services/whatsapp/evolution-api.ts` | A | carteira-livre | forja | `whatsapp`, `messaging`, `evolution` |
| WhatsApp Sharing | `852/src/components/chat/ExportMenu.tsx` | A | 852 | — | `whatsapp`, `sharing` |
| Telegram Bot | `egos-lab/apps/telegram-bot/` | B | egos-lab | — | `telegram`, `bot` |
| Notifications (webhook/Telegram) | `852/src/lib/notifications.ts` | B | 852 | forja | `notifications`, `webhook` |

---

## 10. DATA & SEARCH

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| Supabase + RLS Pattern | `852/sql/schema.sql` | A | 852, carteira-livre | forja | `database`, `rls`, `supabase` |
| Evidence Chain (audit trail) | `br-acc/api/src/bracc/routers/chat.py` | A | br-acc | forja | `audit`, `evidence`, `compliance` |
| Redis Cache Layer | `br-acc/api/src/bracc/services/cache.py` | A | br-acc | forja | `cache`, `redis` |
| pgvector RAG | — (planned for Forja) | C | — | forja | `rag`, `vector`, `search` |

---

## 11. DOCUMENTATION & KNOWLEDGE

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| Chatbot Production Playbook | `852/docs/CHATBOT_PRODUCTION_REVERSE_ENGINEERING.md` | A | 852 | ALL new chatbots | `docs`, `playbook`, `deploy` |
| Archaeology Digger Agent | `egos/agents/agents/archaeology-digger.ts` | A | egos | egos-lab | `docs`, `archaeology`, `agent` |
| Evolution Tree (interactive) | `egos/docs/evolution-tree.html` | A | egos | — | `docs`, `visualization`, `history` |
| Mycelium Architecture | `egos/docs/concepts/mycelium/` | A | egos | — | `docs`, `architecture`, `mycelium` |

---

## Cross-Reference: Module Reuse Matrix

| Module | 852 | carteira-livre | intelink | forja | br-acc | egos-web |
|--------|-----|---------------|----------|-------|--------|----------|
| ATRiAN Validation | SSOT | HAS | HAS | HAS | HAS | HAS |
| PII Scanner | SSOT | HAS | HAS | HAS | HAS (Python) | HAS |
| Conversation Memory | SSOT | HAS | HAS | HAS | HAS (Python) | HAS |
| Model Routing | SSOT | HAS | HAS | HAS | Python variant | HAS |
| Telemetry | SSOT | HAS | BASIC | HAS | Python variant | BASIC |
| Rate Limiting | SSOT | BASIC | BASIC | HAS | Python variant | BASIC |
| Evolution API | -- | SSOT | -- | PLAN | -- | -- |
| Tool-Calling (27) | -- | -- | -- | PLAN | SSOT | -- |
| Supabase RLS | HAS | SSOT | -- | PLAN | -- | -- |
| Export (PDF/DOCX) | SSOT | -- | -- | PLAN | -- | -- |

**Legend:** SSOT = canonical source, HAS = implemented and verified (compliance-checker 100/100), BASIC = minimal variant present, PLAN = planned, -- = not applicable

---

## Tag Index

| Tag | Capabilities |
|-----|-------------|
| `chatbot` | 12 capabilities |
| `ai` | 8 capabilities |
| `governance` | 7 capabilities |
| `deploy` | 5 capabilities |
| `telemetry` | 5 capabilities |
| `auth` | 6 capabilities |
| `privacy` | 4 capabilities |
| `agent` | 5 capabilities |
| `whatsapp` | 3 capabilities |
| `gamification` | 3 capabilities |

---

## 12. MCP & UNIFIED AGENT ARCHITECTURE (Planned)

> **Research completed:** 2026-03-21 | **Status:** Architecture designed, implementation pending

### Custom MCP Servers (TO BUILD)

| MCP Server | Purpose | Priority | Depends On |
|-----------|---------|----------|------------|
| `@egos/mcp-governance` | SSOT drift, task management, deployment gates | P1 | `@egos/shared` |
| `@egos/mcp-memory` | Persistent conversation memory via Supabase/Redis | P1 | cross-session-memory.ts |
| `@egos/mcp-intelligence` | Investigation tools, OVM, report gen (852/policia) | P2 | 852 domain logic |
| `@egos/mcp-marketplace` | Lesson scheduling, instructor matching (carteira-livre) | P2 | carteira-livre domain |
| `@egos/mcp-erp` | Quoting, inventory, production orders (forja) | P2 | forja tool contracts |
| `@egos/mcp-osint` | Company network analysis, Neo4j graph queries (br-acc) | P2 | br-acc chat tools |

### Existing MCPs Already Covering Needs (DO NOT REBUILD)

| MCP | Coverage | Used By |
|-----|---------|---------|
| `filesystem` | File operations | All IDE agents |
| `memory` | Knowledge graph | All IDE agents |
| `supabase` | Raw DB access | carteira-livre, egos-lab |
| `exa` | Web search | All IDE agents |
| `github` | Repo operations | All IDE agents |
| `sequential-thinking` | Reasoning | All IDE agents |

### Architecture Layers

```
L1: @egos/shared (kernel)     — ATRiAN, PII, memory, model-router, telemetry
L2: Chatbot Runtime (extract)  — Standardized chat loop from 852
L3: Custom MCP Servers (build) — Domain-specific outcome-oriented tools
L4: Mycelium Bus (extend)      — Redis Pub/Sub bridge for cross-process events
L5: Agent Registry + Skills    — Auto-discovery, hot-reload, marketplace pattern
```

### Key Design Decisions

1. **Outcomes over operations** — MCP tools expose domain goals, not raw API wrappers
2. **5-15 tools per server** — Curated, not exhaustive
3. **Guardrails at MCP layer** — PII/ATRiAN baked into servers, not per-chatbot
4. **Mycelium events from MCP** — Tool calls auto-emit to event bus
5. **Graceful degradation** — If MCP server down, chatbot falls back to tool-less mode

### Framework Landscape (2026 Research)

| Framework | Best For | Our Relevance |
|-----------|----------|---------------|
| LangGraph | Complex branching workflows | Reference for Mycelium Phase 2 |
| CrewAI | Fast prototyping role-based agents | Inspiration for agent registry |
| OpenClaw | MCP-native skills marketplace (13K+ skills) | Pattern for skills layer |
| Vercel AI SDK | Chat streaming + tool calling | Already used in 852/forja |
| Mastra | TypeScript-first graph workflows | Alternative if LangGraph too heavy |

---

*"Tudo que temos, onde vive, o que é melhor." — EGOS SSOT Discipline*
