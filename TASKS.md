# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.9.1 | **Updated:** 2026-03-28 | **Last:** Hetzner Migration ✅ + OpenClaw Plan
> **Archived:** Historical tasks (EGOS-001..102 + Sessions 2026-03-25/27) → `docs/TASKS_ARCHIVE_2026-03.md`

---

## Session 2026-03-28: Dead Code Removal + P0/P1 Verification

### P0 (Critical) — Code Cleanup

- [x] **P0.1**: Remove dead code (52 unused exports in packages/shared)
  > **Completed:** 2026-03-28 | Commit: c8c703a
  > **What was removed:** 5 stub implementations (ExaMCPClient, SequentialThinkingMCPClient, MemoryMCPClient, MCPManager, mcpManager, MODEL_REGISTRY, LLMOrchestrator, llmOrchestrator)
  > **What was marked @public:** 29 core exports (llm-provider, model-router, atrian, pii-scanner, conversation-memory, rate-limiter, telemetry, cross-session-memory, metrics-tracker, mycelium, repo-role, public-guard, evidence-chain)
  > **What was deleted:** scripts/test-alibaba-orchestrator.ts (obsolete test for removed class)
  > **Verification:** TypeScript: ✅ PASS | 0 type errors
  > **Files changed:** 6 files | Lines: +240 -574

- [x] **P0.2**: Dependency Alignment (verify no blocking conflicts)
  > **Completed:** 2026-03-28
  > **Verification:** bun install — ✅ PASS | No peer dependency conflicts detected
  > **Current versions:** eslint ^9.0.0, typescript ^5.7.0, zod 3.22.4
  > **Status:** All dependencies aligned, workspace healthy

### P1 (Important) — Agent Testing + Verification

- [x] **P1.1**: Test blocked agents (contract_tester, integration_tester, report_generator, etl_orchestrator)
  > **Completed:** 2026-03-28
  > **Results:**
  > - contract-tester: ✅ PASS (dry mode: 10 test cases planned)
  > - integration-tester: ✅ PASS (dry mode: 10 RLS integrity tests planned)
  > - report-generator: ✅ PASS (dry mode: ready for LLM-based reports)
  > - etl-orchestrator: ✅ PASS (dry mode: connected, awaiting ETL API infrastructure)
  > **Finding:** Agents are NOT code-blocked. Ready for --exec once infrastructure available.
  > **Next:** Monitor infrastructure deployment for Supabase + br-acc ETL API

- [ ] **P1.2**: Weekly symlink verification automation
  > **Status:** Pending | **Priority:** P1 | **Effort:** 1-2 hours
  > **Purpose:** Ensure ~/.egos/workflows/start.md v5.5 symlinks stay aligned across 9 repos
  > **Implementation:** cron job + verify script (check in CI/CD pre-push hook)

- [ ] **P1.3**: v5.6+ monitoring setup
  > **Status:** Pending | **Priority:** P1 | **Effort:** 1 hour
  > **Purpose:** Alert when /start workflow updates available
  > **Implementation:** Version footer parser + notification system

- [ ] **P1.4**: CI/CD governance:check integration
  > **Status:** Pending | **Priority:** P1 | **Effort:** 1 hour
  > **Purpose:** Enforce `bun run governance:check` as pre-push gate
  > **Implementation:** Add to `.husky/pre-push` hook

---

## Session 2026-03-28 Continued: Hetzner + OpenClaw + Security

### P0 (Critical) — Infrastructure Migration

- [x] **INFRA-001**: Migrate all services from Contabo → Hetzner (204.168.217.125)
  > **Status:** ✅ Complete | 2026-03-28
  > **Services verified:**
  > - bracc (Neo4j 83.7M nodes + API + Frontend) → inteligencia.egos.ia.br ✅
  > - 852 (News aggregator) → 852.egos.ia.br ✅
  > - WAHA (Telegram connector) → waha.egos.ia.br ✅
  > - Redis ✅ | Caddy (SSL) ✅
  > **Remaining:** Contabo shutdown (user action)
  > **Verification:** All domains HTTP 200, Neo4j node count 83,773,683 confirmed

- [x] **852 rebuild:** Fresh git clone + security updates
  > **Status:** ✅ Complete | Commit: 81c48ed
  > **Result:** 14 vulns → 6 vulns (Next.js beta + serialize-js breaking changes)
  > **Next:** Upgrade Next.js 16.2.1 + @ducanh2912/next-pwa when ready

### P0/P1 — OpenClaw Sandbox Setup

- [ ] **OPENCLAW-001**: Configure LLM Provider Chain
  > **Status:** Pending user action | **Priority:** P0 | **Effort:** 2h
  > **File:** docs/OPENCLAW_CONFIG_PLAN.md
  > **Your action items:**
  > 1. Create Telegram bot via @BotFather → get token
  > 2. Get OpenRouter API key (https://openrouter.ai/keys)
  > 3. Test Codex auth: `codex auth login`
  > 4. Test Gemini auth: `gcloud auth application-default login`
  > **Providers:** Alibaba (primary ✅), OpenRouter (free+paid), Codex (testing), Gemini CLI (pro)
  > **Cost:** ~$0.25-0.50/month (low usage)

- [ ] **OPENCLAW-002**: Deploy Telegram integration → blocked on OPENCLAW-001

- [ ] **OPENCLAW-003**: Test all provider chains → blocked on OPENCLAW-001/002

### P1 — AGENTS SSOT + Dashboard Sync

- [ ] **AGENTS-SSOT-001**: Establish single source of truth for agent definitions
  > **Status:** In Progress | **Priority:** P1 | **Effort:** 3h
  > **File:** docs/AGENTS_SSOT.md
  > **Gaps:** bracc API /api/agents (unknown), 852 dashboard (unknown), @egos_bot (unknown)
  > **Phase 1:** Auto-generate agents-registry.ts from agents.json in CI
  > **Phase 2:** Verify bracc exposes /api/agents
  > **Phase 3:** Verify 852 dashboard consumes bracc API
  > **Phase 4:** Weekly SSOT auditor drift detection

### P1/P2 — Security + Latency

- [ ] **SECURITY-001**: Setup CloudFlare protection
  > **Status:** Pending user action | **Priority:** P1 | **Effort:** 4h
  > **File:** docs/SECURITY_CLOUDFLARE_PLAN.md
  > **Your action items:**
  > 1. Sign up CloudFlare
  > 2. Add egos.ia.br as new site
  > 3. Update nameservers at registrar
  > 4. Wait 24h for DNS propagation
  > 5. Enable: DDoS, Bot Management, WAF, SSL/TLS (Full), rate limiting
  > **Expected gains:** DDoS protection + 40-50% latency improvement

- [ ] **SECURITY-002**: Harden Caddy with rate limiting + security headers
  > **Status:** Pending | **Priority:** P1 | **Effort:** 1h
  > **Rules:** /api/* (100/m), /auth/* (10/m), static/* (bypass)
  > **File to update:** /opt/bracc/infra/Caddyfile

---

## Summary: User Action Items (March 28)

| Priority | Item | Effort | Status |
|----------|------|--------|--------|
| P0 | Create Telegram bot via @BotFather | 30m | ⏳ Waiting |
| P0 | Get OpenRouter API key | 10m | ⏳ Waiting |
| P0 | Test Codex auth | 20m | ⏳ Waiting |
| P0 | Test Gemini CLI auth | 20m | ⏳ Waiting |
| P1 | Add CloudFlare DNS | 1h | ⏳ Waiting |
| P1 | Enable CloudFlare security rules | 2h | ⏳ Blocked (after DNS) |
| P1 | Shutdown Contabo + cancel account | 30m | ⏳ Waiting |
| P1 | Verify AGENTS SSOT gaps | 2h | ⏳ Waiting |

---

> **See:** `docs/TASKS_ARCHIVE_2026-03.md` for historical tasks (Sessions 2026-03-25, 2026-03-27, Hetzner migration steps)
