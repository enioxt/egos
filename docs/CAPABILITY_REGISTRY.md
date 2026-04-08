# EGOS Capability Registry

<!-- llmrefs:start -->
## LLM Reference Signature

- **Role:** capability map + adoption matrix for reusable EGOS surfaces
- **Summary:** Canonical registry of capabilities by domain, with SSOT source, quality, adoption, and rollout targets.
- **Read next:**
  - `TASKS.md` — execution priorities and gaps
  - `docs/SSOT_REGISTRY.md` — ownership/freshness contracts
  - `docs/SYSTEM_MAP.md` — architecture placement of capabilities
<!-- llmrefs:end -->

> **VERSION:** 1.9.0 | **UPDATED:** 2026-04-06
> **PURPOSE:** Master index of all capabilities across the EGOS ecosystem
> **SSOT STATUS:** This file IS the canonical capability map
> **LATEST:** Kernel governance sprint — Agent Claim Contract, MCP servers, Circuit Breaker, SSOT Visit Protocol v2

<!-- llmrefs:start -->

## LLM Reference Signature

- **Role:** Master capability inventory for EGOS ecosystem
- **Summary:** Cross-repo SSOT for all reusable capabilities (chatbot, security, integration, AI). Quality-rated and adoption-mapped.
- **Read next:**
  - `SSOT_REGISTRY.md` — which capabilities are canonical vs local
  - `docs/modules/CHATBOT_SSOT.md` — chatbot-specific standards
  - `TASKS.md` — what capabilities are in-flight or blocked
  - `/start` activation flow — how to use this registry during onboarding

<!-- llmrefs:end -->

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
| **Guard Brasil Python SDK** | `br-acc/etl/src/bracc_etl/guard.py` | B | br-acc | — | `privacy`, `lgpd`, `pii`, `python`, `etl`, `guard-brasil` |
| **Evidence Chain** | `egos/packages/shared/src/evidence-chain.ts` | A | egos | 852, forja, br-acc | `evidence`, `traceability`, `audit`, `guard-brasil` |

| **GuardBrasil Facade** | `egos/packages/guard-brasil/src/guard.ts` | A | egos | 852, forja, br-acc | `guard-brasil`, `facade`, `lgpd`, `sdk` |
| **PRI Safety Gate (Guard Brasil REST/MCP)** | `egos/packages/core/src/guards/pri.ts` + `egos/apps/api/src/server.ts` | B | egos | 852, forja, br-acc | `guard-brasil`, `pri`, `safety`, `privacy` |

### Guard Brasil Stack

> **EGOS Guard Brasil** (`@egosbr/guard-brasil` v0.2.3) — ATRiAN + PII Scanner + Public Guard + Evidence Chain.
> **16 PII patterns:** CPF, CNPJ, RG, CNH, SUS, NIS/PIS, MASP, REDS, Processo, Placa (2), Email, Telefone, Título de Eleitor, CEP, **Dado de Saúde** (LGPD art.11)
> **Name detection:** Detects person names after 12 context labels (Nome:, Paciente:, Requerente:, etc.)
> Package: `packages/guard-brasil/` | Product brief: `docs/strategy/FLAGSHIP_BRIEF.md`
> Demo: `bun run packages/guard-brasil/src/demo.ts`
> Tests: 20/20 pass (`bun test packages/guard-brasil/src/guard.test.ts`)

### Canonical Standard

> **`egos/docs/modules/CHATBOT_SSOT.md`** — Every chatbot MUST follow this spec.

---

## 2. AI & LLM INFRASTRUCTURE

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| Multi-LLM Provider (TS) | `egos/packages/shared/src/llm-provider.ts` | A | egos, egos-lab | 852 (has own) | `ai`, `provider`, `shared` |
| DashScope Fallback Chain | `egos/packages/shared/src/llm-provider.ts` | A | egos, egos-lab | 852, forja | `ai`, `dashscope`, `fallback` |
| qwq-plus Reasoning Tier | `egos/packages/shared/src/llm-provider.ts` | A | egos | ALL (deep tasks) | `ai`, `reasoning`, `qwq` |
| AI Coverage Map | `egos/docs/AI_COVERAGE_MAP.md` | A | egos | — | `ai`, `coverage`, `telemetry` |
| AI Coverage Scanner | `egos/scripts/ai-coverage-scan.ts` | A | egos | — | `ai`, `scan`, `pre-commit` |
| AI Client (OpenRouter) | `egos-lab/packages/shared/src/ai-client.ts` | A | egos-lab, telegram-bot | forja | `ai`, `client`, `openrouter` |
| Rate Limiter (shared) | `egos-lab/packages/shared/src/rate-limiter.ts` | A | egos-lab | forja | `ai`, `rate-limit`, `shared` |
| Cost Tracking (per-request) | `852/src/lib/ai-provider.ts` | A | 852 | ALL | `ai`, `cost`, `budget` |
| Budget Mode (conservative/balanced) | `852/src/lib/ai-provider.ts` | A | 852 | forja | `ai`, `cost`, `config` |
| Prompt System (meta-prompts) | `.guarani/prompts/PROMPT_SYSTEM.md` | B | egos | egos-lab | `ai`, `prompt`, `meta` |
| Licitação Taxonomy | `egos-lab/eagle-eye/src/types.ts` | A | eagle-eye | — | `ai`, `procurement`, `taxonomy` |

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
| **MANUAL_ACTIONS Tracker** | `egos/MANUAL_ACTIONS.md` | A | egos (wired into /start INTAKE) | ALL | `governance`, `manual`, `blocker`, `gtm` |
| Context Persistence (Fibonacci) | `scripts/context-manager.ts` + `/snapshot` command | A | ALL (9 repos) | — | `context`, `session`, `persistence` |
| Secret Leak Detection | `.gitleaks.toml` + CRCDM hook regex | A | ALL | — | `security`, `secrets`, `compliance` |
| Context Tracker | `egos/agents/agents/context-tracker.ts` | A | egos | ALL | `governance`, `context`, `observability` |
| SSOT Drift Check | `egos-lab/scripts/ssot-drift-check.ts` | A | egos-lab | — | `governance`, `drift`, `api` |
| API Registry Check | `egos-lab/scripts/ssot-api-registry-check.ts` | A | egos-lab | — | `governance`, `api`, `drift` |
| Orchestration Pipeline (7-phase) | `.guarani/orchestration/PIPELINE.md` | A | ALL | — | `governance`, `pipeline`, `frozen` |
| Frozen Zones | `egos/.windsurfrules` | A | ALL | — | `governance`, `frozen`, `security` |
| **SSOT Visit Protocol v2** | `.guarani/orchestration/DOMAIN_RULES.md §7` | A | egos (kernel law) | ALL | `governance`, `ssot`, `cross-repo`, `intra-repo` |
| **Agent Claim Contract** | `.guarani/orchestration/AGENT_CLAIM_CONTRACT.md` | A | egos | ALL | `governance`, `agent`, `taxonomy`, `proof` |
| **Agent Claim Linter** | `scripts/agent-claim-lint.ts` | A | egos | egos-lab | `governance`, `agent`, `lint`, `ci` |
| **Ecosystem Classification Registry** | `docs/ECOSYSTEM_CLASSIFICATION_REGISTRY.md` | A | egos | ALL | `governance`, `classification`, `ssot` |
| **Workflow Inheritance Report** | `docs/WORKFLOW_INHERITANCE_REPORT.md` | B | egos | — | `governance`, `workflow`, `inheritance` |
| **Workflow Sync Check** | `scripts/workflow-sync-check.sh` | B | egos | ALL | `governance`, `workflow`, `drift` |
| **Clarity Review Gate** | `.guarani/orchestration/CLARITY_REVIEW.md` | A | egos | ALL | `governance`, `review`, `monthly` |
| **Mycelium Truth Report** | `docs/MYCELIUM_TRUTH_REPORT.md` | A | egos | — | `governance`, `mycelium`, `audit` |
| **LLM Orchestration Matrix** | `.guarani/orchestration/LLM_ORCHESTRATION_MATRIX.md` | A | egos | ALL | `ai`, `orchestration`, `routing` |
| **Benchmark Enforcement** | `.guarani/orchestration/BENCHMARK_ENFORCEMENT.md` | A | egos | ALL | `governance`, `multi-agent`, `enforcement` |
| **QA Loop Contract** | `.guarani/orchestration/QA_LOOP_CONTRACT.md` | A | egos | ALL | `governance`, `qa`, `contract` |
| **Operator Map** | `docs/OPERATOR_MAP.md` | A | egos | — | `governance`, `control-plane`, `founder` |
| **Kernel Consolidation Plan** | `docs/KERNEL_CONSOLIDATION_PLAN.md` | A | egos | — | `governance`, `consolidation`, `migration` |
| **SSOT Registry v2** | `docs/SSOT_REGISTRY.md` | A | egos | ALL | `governance`, `ssot`, `30-domains` |
| **Injection Hardening Contract** | `.guarani/security/INJECTION_HARDENING.md` | B | egos | ALL | `security`, `injection`, `hardening` |
| **File Intelligence** | `scripts/file-intelligence.sh` | B | egos | ALL | `governance`, `compliance`, `pre-commit`, `classification` |
| **Rules Index** | `.guarani/RULES_INDEX.md` | A | egos | ALL | `governance`, `rules`, `discovery`, `ssot` |

---

## 5. AGENT RUNTIME

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| Agent Runner | `egos/agents/runtime/runner.ts` | A | egos (FROZEN) | — | `agent`, `runtime`, `frozen` |
| Event Bus | `egos/agents/runtime/event-bus.ts` | A | egos (FROZEN) | — | `agent`, `events`, `frozen` |
| Agent Registry | `egos-lab/agents/registry/agents.json` | A | egos-lab (29) | egos (2) | `agent`, `registry`, `ssot` |
| Agent CLI | `egos-lab/agents/cli.ts` | A | egos-lab | egos | `agent`, `cli` |
| Worker Infrastructure | `egos-lab/agents/worker/` | B | egos-lab (Railway) | — | `agent`, `worker`, `infra` |
| **Circuit Breaker** | `egos/packages/shared/src/circuit-breaker.ts` | A | egos | ALL | `resilience`, `circuit-breaker`, `shared` |
| **Mycelium Redis Bridge** | `egos/packages/shared/src/mycelium/redis-bridge.ts` | B | egos (scaffold) | egos-lab | `mycelium`, `redis`, `pubsub`, `bridge` |
| **Event Bus (Supabase Realtime)** | `egos/packages/shared/src/event-bus.ts` | B | egos | egos-lab, 852 | `agent`, `events`, `supabase`, `coordination` |
| **MasterOrchestrator** | `egos-lab/agents/agents/master-orchestrator.ts` | B | egos-lab | egos | `agent`, `orchestrator`, `scheduling`, `quota` |

## 5b. MCP SERVERS

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| **MCP Governance** | `egos/packages/mcp-governance/src/index.ts` | B | egos | ALL | `mcp`, `governance`, `ssot`, `drift` |
| **MCP Memory** | `egos/packages/mcp-memory/src/index.ts` | B | egos | ALL | `mcp`, `memory`, `recall`, `store` |

---

## 6. DEPLOYMENT & INFRA

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| Docker + Caddy + VPS | `852/docker-compose.yml` | A | 852, br-acc | forja | `deploy`, `docker`, `vps` |
| **Guard Brasil REST API** | `egos/apps/api/src/server.ts` + `apps/api/deploy.sh` | A | egos (LIVE: guard.egos.ia.br) | — | `deploy`, `docker`, `guard-brasil`, `api` |
| **Guard Brasil MCP Server** | `egos/apps/api/src/mcp-server.ts` | A | egos (stdio JSON-RPC 2.0) | — | `deploy`, `mcp`, `guard-brasil` |
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
| **WhatsApp Integration Architecture** | `egos/docs/knowledge/WHATSAPP_SSOT.md` | A | forja | 852, carteira-livre | `whatsapp`, `architecture`, `ssot` |
| **Multi-Channel Runtime Pattern** | `egos/docs/knowledge/WHATSAPP_SSOT.md` | A | forja | ALL | `whatsapp`, `multi-channel`, `runtime` |
| **Evolution API Deployment** | `egos/docs/knowledge/WHATSAPP_SSOT.md` | A | forja | ALL | `whatsapp`, `evolution`, `docker` |
| **QR Drift Recovery Protocol** | `egos/docs/knowledge/WHATSAPP_SSOT.md` | A | forja | ALL | `whatsapp`, `recovery`, `qr` |
| **WhatsApp Runtime Distribution Bundle** | `egos/integrations/distribution/whatsapp-runtime/` | A | egos | forja, 852, carteira-livre | `whatsapp`, `distribution`, `bundle` |
| **Integration Memory Pattern** | `forja/docs/INTEGRATIONS_MEMORY.md` | A | forja | ALL | `infrastructure`, `memory`, `ssot` |
| Evolution API Client | `carteira-livre/services/whatsapp/evolution-api.ts` | B | carteira-livre | — | `whatsapp`, `client`, `legacy` |
| WhatsApp Notification Service | `forja/src/lib/whatsapp/notifications.ts` | A | forja | 852, carteira-livre | `whatsapp`, `notifications`, `templates` |
| WhatsApp Webhook Handler | `forja/src/app/api/notifications/whatsapp/route.ts` | A | forja | 852, carteira-livre | `whatsapp`, `webhook`, `api` |
| WhatsApp Sharing | `852/src/components/chat/ExportMenu.tsx` | A | 852 | — | `whatsapp`, `sharing` |
| Telegram Bot | `egos-lab/apps/telegram-bot/` | B | egos-lab | — | `telegram`, `bot` |
| Notifications (webhook/Telegram) | `852/src/lib/notifications.ts` | B | 852 | forja | `notifications`, `webhook` |

### WhatsApp Integration Stack (2026-03-30)

> **Canonical Architecture:** Hetzner VPS as runtime SSOT → Evolution API (single deployment) → One instance per product/channel → Vercel app for webhooks → Supabase for audit → Redis for queue (future).
>
> **Philosophy:** WhatsApp as workflow surface (alerts, confirmations, status), NOT open-chat platform.
>
> **Validated:** forja-notifications (state: open, 2026-03-30)
>
> **Complete Guide:** `egos/docs/knowledge/WHATSAPP_SSOT.md`

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
| Integration Release Contract | `egos/.guarani/orchestration/INTEGRATION_RELEASE_CONTRACT.md` | A | egos | ALL | `integrations`, `governance`, `release-gate` |
| Chatbot Production Playbook | `852/docs/CHATBOT_PRODUCTION_REVERSE_ENGINEERING.md` | A | 852 | ALL new chatbots | `docs`, `playbook`, `deploy` |
| Archaeology Digger Agent | `egos/agents/agents/archaeology-digger.ts` | A | egos | egos-lab | `docs`, `archaeology`, `agent` |
| Evolution Tree (interactive) | `egos/docs/evolution-tree.html` | A | egos | — | `docs`, `visualization`, `history` |
| Mycelium Architecture | `egos/docs/concepts/mycelium/` | A | egos | — | `docs`, `architecture`, `mycelium` |
| **Knowledge System (wiki)** | `egos/agents/agents/wiki-compiler.ts` + `docs/knowledge/` | A | egos | — | `docs`, `wiki`, `knowledge`, `supabase` |
| **HARVEST.md Patterns** | `egos/docs/knowledge/HARVEST.md` | A | egos | ALL | `docs`, `patterns`, `learnings` |

---

## 12. GTM & COMMERCIAL

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| **Partnership Strategy** | `egos/docs/strategy/PARTNERSHIP_STRATEGY.md` | B | egos | — | `gtm`, `partners`, `distribution` |
| **Outreach Email Templates** | `egos/docs/business/OUTREACH_EMAIL_TEMPLATES.md` | B | egos | — | `gtm`, `outreach`, `lgpd` |
| **X.com Reply Bot** | `egos/scripts/x-reply-bot.ts` (VPS cron hourly) | A | egos | — | `gtm`, `x.com`, `social`, `bot` |
| **Rapid Response Thread** | `egos/scripts/rapid-response.ts` | B | egos | — | `gtm`, `x.com`, `thread`, `showcase` |
| **Gem Hunter Partner Track** | `docs/gem-hunter/SSOT.md` → partner/community track | C | egos (planned) | — | `gtm`, `gem-hunter`, `discovery` |

---

## 13. AUDITABLE LIVE SANDBOX (UX Pattern)

> **Pattern SSOT:** `docs/patterns/AUDITABLE_SANDBOX_PATTERN.md`
> Apply to any API/MCP/validation product. First impl: Guard Brasil.

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| **Auditable Live Sandbox** | `docs/patterns/AUDITABLE_SANDBOX_PATTERN.md` | A | guard-brasil-web (LIVE) | gem-hunter-web, eagle-eye-web, kb-api | `sandbox`, `ux`, `pattern`, `trust` |
| **Sandbox Dataset Generator** | `apps/guard-brasil-web/app/sandbox/README.md` | B | guard-brasil | ALL viable | `sandbox`, `dataset`, `testing` |
| **Client SHA-256 Receipt Verify** | `sandbox-client.tsx:sha256hex()` | A | guard-brasil-web | ALL APIs with receipts | `trust`, `crypto`, `receipt`, `lgpd` |
| **Session Audit Trail Export** | `sandbox-client.tsx:exportAudit()` | A | guard-brasil-web | eagle-eye, gem-hunter | `audit`, `compliance`, `export` |

---

## 14. MISSION CONTROL (HQ)

| Capability | SSOT | Quality | Adopted By | Should Adopt | Tags |
|-----------|------|---------|------------|-------------|------|
| **EGOS HQ Dashboard** | `egos/apps/egos-hq/` (hq.egos.ia.br:3060) | A | egos (LIVE) | — | `hq`, `dashboard`, `mission-control` |
| **HQ JWT Auth** | `apps/egos-hq/src/middleware.ts` + `DASHBOARD_MASTER_SECRET` | A | egos (LIVE) | — | `hq`, `auth`, `jwt` |
| **HQ X Monitor** | `apps/egos-hq/app/x/` — 3 tabs: queue/search/history | A | egos (LIVE) | — | `hq`, `x.com`, `monitor` |
| **Claude Code Skills (22+)** | `~/.claude/commands/` (22 skills) | A | egos | — | `dx`, `skills`, `automation` |
| **Claude Code Hooks (12)** | `~/.claude/hooks/` + `~/.claude/settings.json` | A | egos | — | `dx`, `hooks`, `safety` |
| **Gem Hunter deps-watch** | `agents/agents/gem-hunter.ts` → SearchTrack deps-watch | B | egos (manual) | — | `dx`, `deps`, `monitoring` |

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
| ~~OpenClaw~~ | ~~DECOMMISSIONED 2026-04-08~~ — ChatGPT subscription cancelled. Replaced by DashScope qwen-plus + OpenRouter free fallback (see §16) | N/A |
| Vercel AI SDK | Chat streaming + tool calling | Already used in 852/forja |
| Mastra | TypeScript-first graph workflows | Alternative if LangGraph too heavy |

---

*"Tudo que temos, onde vive, o que é melhor." — EGOS SSOT Discipline*
## 13. X.COM & RAPID RESPONSE (2026-04-01)

| Capability | SSOT | Quality | Adopted By | Tags |
|-----------|------|---------|------------|------|
| X Reply Bot | `egos/scripts/x-reply-bot.ts` | A | egos | `x.com`, `automation`, `social`, `oauth` |
| Rapid Response System | `egos/scripts/rapid-response.ts` | A | egos | `x.com`, `showcase`, `threads`, `rapid` |
| Task Reconciliation | `egos/scripts/task-reconciliation.ts` | A | egos | `governance`, `tasks`, `automation` |
| Legacy Code Detector | `egos/scripts/check-legacy-code.sh` | A | egos | `pre-commit`, `quality`, `non-blocking` |
| Hermes-3 Executor | `egos/packages/shared/src/llm-provider.ts` | A | egos | `llm`, `braid`, `structured-output`, `openrouter` |
| BRAID Capability Profile | `egos/scripts/rapid-response.ts#braid_serv` | B | egos | `braid`, `grd`, `multi-agent`, `showcase` |

**X.com Rate Limits (Free tier):** 50 writes/day, 10 searches/15min. Bot: 40 replies/day, 3/run, hourly cron on Hetzner.

**VPS deploy path:** `/opt/egos-lab/.env` has X API keys. Cron: `0 * * * * bun /home/enio/egos/scripts/x-reply-bot.ts`


## 14. MISSION CONTROL & CLAUDE CODE TOOLING (2026-04-05)

| Capability | SSOT | Quality | Adopted By | Tags |
|-----------|------|---------|------------|------|
| EGOS HQ Dashboard | `apps/egos-hq/` → hq.egos.ia.br | A | egos | `dashboard`, `mission-control`, `private`, `jwt-auth` |
| X.com Reply Queue | `apps/egos-hq/app/x/page.tsx` + `x_reply_runs` | A | egos | `x.com`, `queue`, `approval-flow`, `supabase` |
| HQ Health API | `apps/egos-hq/app/api/hq/health/route.ts` | A | egos | `health`, `monitoring`, `guard-brasil`, `gateway` |
| Claude Code Skills (11) | `~/.claude/commands/` | A | global | `slash-commands`, `commit`, `pr-review`, `worktrees` |
| rm-guard Hook | `~/.claude/hooks/rm-guard` | A | global | `safety`, `hooks`, `pre-tool-use`, `bash` |
| PR Review Action | `.github/workflows/pr-review.yml` | A | egos | `github-actions`, `code-review`, `claude`, `automation` |

**EGOS HQ URLs:**
- Dashboard: https://hq.egos.ia.br (private, requires DASHBOARD_MASTER_SECRET)
- Container: `docker ps | grep egos-hq` on VPS port 3060
- Deploy: `/opt/apps/egos-hq/` on Hetzner 204.168.217.125

## 15. GATEWAY P24 — AUTH + TELEGRAM COMMANDS + FTS (2026-04-06)

| Capability | SSOT | Quality | Adopted By | Tags |
|-----------|------|---------|------------|------|
| Gem Hunter API Key Auth | `egos-gateway/src/channels/gem-hunter-api.ts` | A | egos | `auth`, `sha256`, `supabase`, `middleware` |
| Gem Hunter Rate Limiting | `gem-hunter-api.ts#checkAndIncrementUsage` | A | egos | `rate-limit`, `tier`, `usage-tracking` |
| Gateway Health Monitor | `egos-gateway/src/health-monitor.ts` | A | egos | `health`, `telegram-alert`, `weighted-score` |
| Telegram /hunt /sector /trending | `egos-gateway/src/channels/telegram.ts` | A | egos | `telegram`, `slash-commands`, `gem-hunter` |
| Knowledge FTS (pg_trgm + phfts) | `egos-gateway/src/channels/knowledge.ts` | A | egos | `fts`, `pg_trgm`, `portuguese`, `search` |
| Gem Hunter Dashboard (inline SSR) | `agents/api/gem-hunter-server.ts` | A | egos | `dashboard`, `bun`, `ssr`, `gem-hunter` |
| X Bot Daily Report | `scripts/x-reply-bot.ts#sendDailyReport` | A | egos | `x.com`, `telegram`, `reporting`, `automation` |
| Rapid Response Profiles | `scripts/rapid-response.ts` | A | egos | `x.com`, `showcase`, `br_acc`, `sistema_852`, `gem_hunter` |
| Gem Signal Auto-append | `agents/agents/gem-hunter.ts` + `gem-signals.ts` | A | egos | `signals`, `world-model`, `gem-hunter`, `intel` |

**Gateway deploy:** `rsync src → /opt/apps/egos-gateway/src/ && docker compose build --no-cache && docker compose up -d`
**No volume mounts** — source baked into image. Always rebuild after rsync.

## 16. LLM EXECUTION ENGINE — DASHSCOPE + OPENROUTER (2026-04-08)

> **Replaces:** Codex Proxy + OpenClaw billing proxy (both decommissioned 2026-04-08 — ChatGPT subscription cancelled)

| Capability | SSOT | Quality | Adopted By | Tags |
|-----------|------|---------|------------|------|
| Hermes LLM Provider | `packages/shared/src/llm-providers/hermes.ts` | A | egos | `dashscope`, `qwen-plus`, `openrouter`, `fallback-chain` |
| DashScope qwen-plus (primary) | `packages/shared/src/llm-providers/hermes.ts` | A | egos, egos-hq | `alibaba`, `qwen-plus`, `cheap`, `fast` |
| OpenRouter free fallback | `packages/shared/src/llm-providers/hermes.ts` | A | egos | `openrouter`, `gemma-4-26b`, `free` |
| Constitutional Review (migrated) | `apps/egos-hq/app/api/hq/actions/codex-review/route.ts` | A | egos-hq | `governance`, `review`, `dashscope` |
| Smart TASKS.md Archive | `scripts/archive-tasks.sh` + `.husky/pre-commit` | A | egos | `governance`, `tasks`, `archiving`, `pre-commit` |
| HQ Action Endpoints | `apps/egos-hq/app/api/hq/actions/` | A | egos | `hq`, `actions`, `codex-review` |
| HQ Collapsible Dashboard | `apps/egos-hq/app/page.tsx` (v2) | A | egos | `hq`, `collapsible`, `quota-bar`, `5-services` |
| X Opportunity LLM Analysis | `scripts/x-opportunity-alert.ts#analyzeWithLLM` | A | egos | `x.com`, `ai-analysis`, `telegram`, `dashscope` |

**LLM chain (priority order):**
1. Alibaba DashScope `qwen-plus` — `ALIBABA_DASHSCOPE_API_KEY` + `dashscope-intl.aliyuncs.com/compatible-mode/v1`
2. OpenRouter `google/gemma-4-26b-a4b-it:free` — `OPENROUTER_API_KEY`
3. OpenRouter `qwen/qwen3-coder:free` — optional 3rd slot

**Hermes gateway (VPS):**
- Service: `systemctl status hermes-gateway` → port 18800, 142MB RAM
- Config: `/root/.hermes/config.yaml` (provider: alibaba_dashscope, model: qwen-plus)
- .env: `/root/.hermes/.env` (DashScope key + OpenRouter key)

## 17. DOC-DRIFT SHIELD — 4-LAYER DOCUMENTATION INTEGRITY (2026-04-07)

> **Status:** LIVE — all 4 layers operational | **SSOT:** `docs/DOC_DRIFT_SHIELD.md`

### Layer Architecture
| Layer | Artifact | Trigger | Scope |
|-------|----------|---------|-------|
| L1 | `.egos-manifest.yaml` per repo | Manual + generator | claim contracts |
| L2 | `doc-drift-verifier.ts` + `.husky/doc-drift-check.sh` | Pre-commit (staged code files) | egos repo |
| L3 | `doc-drift-sentinel.ts` | Local cron 0h17 BRT daily | all known repos |
| L3.5 | `doc-drift-analyzer.ts` | CCR `governance-drift.yml` | egos repo (GH Actions) |
| L4 | CLAUDE.md §27 + SSOT gate | Every session + pre-commit | global |

### New Agents (Registered in agents.json)
- **`doc-drift-sentinel`** — autonomous daily drift detector + fixer (branch + issue + telegram)
- **`readme-syncer`** — patches `<!-- metric:ID -->` annotations from manifest `last_value`
- **`doc-drift-verifier`** (CLI) — `--all/--repo/--fail-on-drift/--markdown`

### SSOT Gate (Pre-Commit Step 5.7)
- `.ssot-map.yaml` — 26-domain machine-readable SSOT map
- `scripts/ssot-router.ts` — LLM gate (Gemini Flash → Alibaba → keyword → warn-only)
- Triggers only on **new `.md` files** (not modifications)
- Override: `SSOT-NEW: <reason>` in commit message

### Supporting Scripts
- `scripts/manifest-generator.ts` — DRIFT-011: auto-extract claims from READMEs via LLM
- `scripts/run-doc-drift-sentinel.sh` — cron wrapper with `cd /home/enio/egos`
- `.github/workflows/governance-drift.yml` — daily CCR + doc-drift-verifier + safe-push

### Manifest Rollout Status
| Repo | Manifest | Claims | Notes |
|------|----------|--------|-------|
| egos | ✅ | 8 | Baseline, verified |
| carteira-livre | ✅ | 6 | readme-syncer annotations live |
| br-acc | ✅ | 5 | 83.7M nodes verified |
| 852 | ✅ | 5 | New this session |
| forja | ✅ | 2 | Baseline |
| egos-lab | ✅ | 4 | Baseline |
| egos-inteligencia | ✅ | 5 | Not a git repo — manifest on filesystem |

## 19. HERMES AGENT — ALWAYS-ON EXECUTOR (2026-04-07)

> **Status:** LIVE — MVP deployed | **Version:** v0.7.0 | **Author:** NousResearch (MIT)

### What It Is
Python-based AI agent runtime with persistent TUI, 40+ tools (bash, file ops, browser/CDP), scheduled automations, skills (procedural memory that self-improves), messaging gateway (Telegram/Discord), and sub-agent spawning. Not a framework — a full application.

### EGOS Integration
- **Auth (2026-04-08):** DashScope qwen-plus via `ALIBABA_DASHSCOPE_API_KEY`. OpenRouter free as fallback. Anthropic OAuth removed (key invalid).
- **Gateway service:** `systemctl status hermes-gateway` — VPS systemd, `ExecStart=cli.py --gateway`, MemoryMax=512M, Restart=always
- **Config:** `/root/.hermes/config.yaml` (provider: alibaba_dashscope, model: qwen-plus)
- **Install:**
  - Local: `~/.hermes-agent` (source) + `~/.hermes-venv` (Python env) + `~/.local/bin/hermes` (symlink)
  - VPS: `/opt/hermes-agent` + `/opt/hermes-venv` + `/root/.local/bin/hermes`

### Non-interactive (scripting)
```bash
hermes chat --provider openai --model qwen-plus -q "task here" --yolo -Q
# (provider=openai = DashScope-compatible endpoint)
```

### Next steps
- HERMES-005: 1-week trial (2026-04-07 → 2026-04-15), go/no-go gate
- HERMES-006: Scale to 6 profiles per domain (post-trial)
- HERMES-008: Connect Gem Hunter v7 as Hermes cron job

## 18. ARR — ADAPTIVE ATOMIC RETRIEVAL (DORMANT) (2026-04-07)

> **Status:** DORMANT — implemented, not wired | **Packages:** `@egos/atomizer` + `@egos/search-engine`

### What It Is
In-memory full-text search with hierarchical scoring at sentence/claim level.
Scoring: exact substring (high) > token overlap (medium) > atom confidence (base).

### Current State
- Code: `packages/atomizer/src/` + `packages/search-engine/src/`
- Consumer: **NONE** — not imported anywhere in production
- "Quantum Search" (deprecated alias) = vocab-guard blocked term in pre-commit

### Activation Path
1. **ARR-001**: `import { AtomizerCore } from '@egos/atomizer'` in gem-hunter pipeline
2. **ARR-002**: Wire into KB wiki search (replace raw grep in wiki-compiler.ts)
3. Complements (not replaces): codebase-memory-mcp graph, Supabase pg_trgm FTS

---

## §19 — Partial Masking Mode (Guard Brasil) (2026-04-07)

**Module:** `packages/guard-brasil/src/pii-patterns.ts` + `lib/public-guard.ts` + `apps/api/src/server.ts`

**Capability:** Banking-style partial PII reveal for confirmation UIs.

- `MaskMode = 'full' | 'partial'` on all masking APIs
- Per-pattern `partialMaskFn` (CPF, CNPJ, telefone, email)
- API: `POST /v1/inspect { mask_mode: "partial" }`
- Full masking remains default — partial is opt-in

---

## §20 — Schema-Driven Prompt Assembler (2026-04-07)

**Module:** `packages/shared/src/prompt-assembler.ts` (+ `852/src/lib/prompt-assembler.ts` local copy)

**Capability:** Typed, conditional, cacheable prompt section assembly.

- `PromptSection<TCtx>`: id, content, condition, cacheable, priority
- `createAssembler(sections)` → reusable builder bound to section registry
- `AssembledPrompt`: text + cacheableIds + dynamicIds for Anthropic cache integration
- 852 prompt.ts fully refactored to use this pattern

---

## §21 — MemoryStore Adapter (2026-04-07)

**Module:** `packages/shared/src/memory-store.ts`

**Capability:** Backend-agnostic conversational memory persistence.

- `MemoryStore` interface: getRecent / save / buildMemoryBlock
- `SupabaseMemoryStore` — configurable column mapping, production
- `InMemoryStore` — process-scoped, dev/test, clearable
- `NullMemoryStore` — no-op for CI/offline

---

## §22 — Eval Harness (2026-04-07)

**Module:** `packages/shared/src/eval/runner.ts` + `852/src/eval/golden/852.ts`

**Capability:** Golden case regression testing for chatbot responses.

- `GoldenCase`: mustContain, mustNotContain, minLength, maxLength, custom score fn
- `runEval(cases, chatFn, opts)` → `EvalReport` with passRate, avgScore, failures
- 20 golden cases for 852 across 7 categories: PII safety, ATRiAN, governance, legal, ops, tone, anti-hallucination
- Run: `BASE_URL=http://localhost:3001 bun run eval`

