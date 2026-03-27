# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.7.0 | **Updated:** 2026-03-25 | **Last:** FORJA Auth Completion + BLUEPRINT-EGOS Absorption
> **Archived:** Historical tasks (EGOS-001..102) moved to `docs/TASKS_ARCHIVE_2026-03.md`

---
## Session 2026-03-25: FORJA + BLUEPRINT-EGOS Sprint

### P1 (Critical) — FORJA Signup Flow

- [x] FORJA-AUTH-001: Implement no-confirmation signup endpoint
  > Completed: `/api/auth/signup` using Supabase Admin API (`email_confirm: true`)
  > Status: Tested end-to-end, user created + immediately can login
  > Files: `src/app/api/auth/signup/route.ts`, `src/middleware.ts`
  > Commit: `feat(auth): implement no-confirmation signup flow`

- [x] FORJA-AUTH-002: Add signup form to login page
  > Completed: Tab-based UI (Login | Signup), password validation, confirmation
  > Pre-filled test credentials: `admin@forja.local` / `Test123!456`
  > Status: Tested, build passes TypeScript checks
  > Files: `src/app/page.tsx`
  > Commit: Included in `feat(auth)...` commit

- [x] FORJA-AUTH-003: Update middleware to allow signup endpoint
  > Completed: Added `/api/auth/signup` to public routes
  > Status: ✅ No auth required to register
  > Files: `src/middleware.ts`

- [x] FORJA-SIGNUP-001: User can immediately login after signup
  > Verified: Test user registered + authentication successful
  > Status: Live on main branch, pushed to production
  > Next: Monitor signup completion rates in analytics

### P2 (Important) — BLUEPRINT-EGOS Integration

- [ ] BLUEPRINT-001: Clone BLUEPRINT-EGOS to `/home/enio/blueprint-egos`
  > Purpose: Mission Control architecture separation from kernel
  > Status: Pending

- [ ] BLUEPRINT-002: Deploy Mission Control frontend to `kernel.egos.ia.br`
  > Frontend: React dashboard with GitHub event stream + provenance
  > Dependency: EGOS-110 (kernel infrastructure)
  > Status: Code ready, awaiting VPS deployment

- [ ] BLUEPRINT-003: Develop FastAPI gateway for GitHub webhook ingestion
  > Endpoints: `/api/webhooks/github`, `/api/governance/gate`
  > Status: Architecture documented, not yet implemented
  > Dependency: EGOS-111

- [ ] BLUEPRINT-004: Integrate BLUEPRINT Gem Hunter (web scraper + Cloudflare bypass)
  > Uses: playwright-mcp + FlareSolverr
  > Purpose: Autonomous OSINT for 852 + Forja agents
  > Status: Proposed, not yet implemented
  > Duration: Phase 2

- [ ] BLUEPRINT-005: Implement lightweight web automation (replace OpenClaw)
  > Alternative: browser-use pattern with playwright-mcp
  > Benefit: 90% less resource consumption
  > Status: Proposed architecture, awaiting implementation
  > Duration: Phase 3

### P2 (Important) — VPS Consolidation

- [ ] VPS-DEPLOY-001: Migrate FORJA from Vercel to VPS 217.216.95.126
  > Current: Vercel ($20/mo), slow builds (30-60s)
  > Target: VPS ($0, 5-10s builds), fixed IP for webhooks
  > Steps: Docker build, Nginx config, SSL via Let's Encrypt
  > Savings: $20/mo
  > Status: Documented, not yet executed
  > Duration: 2 hours

- [ ] VPS-DEPLOY-002: Deploy 852 to VPS
  > Current: Not deployed (only local/Docker config)
  > Target: VPS as Vite SPA + backend API
  > Dependency: FastAPI gateway (BLUEPRINT-003)
  > Savings: $15/mo
  > Status: Docker config ready, pending VPS setup
  > Duration: 1.5 hours

- [ ] VPS-DEPLOY-003: Deploy carteira-livre to VPS
  > Current: Vercel
  > Target: VPS + Supabase
  > Savings: $15/mo
  > Status: Docker config ready, pending VPS setup
  > Duration: 1.5 hours

- [ ] VPS-DEPLOY-004: Setup Nginx reverse proxy for all sites
  > Sites: kernel.egos.ia.br, 852.egos.ia.br, forja.egos.ia.br, commons.egos.ia.br
  > SSL: Let's Encrypt with auto-renewal
  > Monitoring: Health checks + alerting
  > Status: Not yet started
  > Duration: 2 hours

- [ ] VPS-OPS-001: Setup automated backups (daily rsync)
  > Target: Backup VPS or external storage
  > Retention: 7-day rolling backup
  > Status: Not yet started
  > Duration: 1 hour

- [ ] VPS-OPS-002: Configure GitHub Actions for auto-deploy
  > Trigger: git push to main
  > Flow: Pull latest → npm build → Docker build → Deploy to VPS
  > Status: Not yet started
  > Duration: 2 hours

### P3 (Future) — Advanced EGOS Orchestration

- [ ] EGOS-ORCH-001: Build Agent Router/Supervisor for EGOS Kernel
  > Pattern: Router decides which agent handles the task (Forja/852/Gem Hunter/ATRiAN)
  > Tech: LLM-driven routing with capability registry
  > Status: Proposed in BLUEPRINT-EGOS
  > Duration: Sprint 3+

- [ ] EGOS-ORCH-002: Implement composable agent chaining
  > Use case: Forja needs external data → delegates to Gem Hunter → validates via ATRiAN
  > Tech: MCP-based message passing
  > Status: Proposed, not yet implemented
  > Duration: Sprint 3+

- [ ] EGOS-ORCH-003: Multi-LLM orchestration matrix
  > Lanes: Cascade (Google), Codex (cloud), Claude Code (local), Alibaba (API)
  > Decision: Which lane handles which task class (security/code/analysis/ops)
  > Status: Proposed, not yet implemented
  > Duration: Sprint 4

---

### Summary: Session 2026-03-25

**Completed:**
- ✅ FORJA signup without email confirmation (tested, live)
- ✅ BLUEPRINT-EGOS absorption + architecture documentation
- ✅ VPS hosting strategy analysis + cost savings calculation ($60-100/mo)
- ✅ EGOS agent orchestration blueprint (Router/Supervisor pattern)
- ✅ Memory + HARVEST.md updates
- ✅ System-wide dissemination (this TASKS.md update)

**Ready for Next Session:**
- 🚀 Deploy Mission Control to `kernel.egos.ia.br`
- 🚀 Develop FastAPI gateway
- 🚀 Migrate FORJA, 852, carteira-livre to VPS
- 🚀 Setup CI/CD pipeline for auto-deploy
- 🚀 **Agent Swarm 24/7** — Full autonomous agent orchestration

---

## 🆕 NEW: Agent Swarm 24/7 — EGOS-103..110

> **Created:** 2026-03-26 | **Scope:** Autonomous agent orchestration
> **Blueprint:** `docs/AGENT_SWARM_24_7_BLUEPRINT.md`

### P0 (Critical) — Foundation

- [x] **EGOS-103**: Implementar Agent Scheduler (node-cron)
  > ✅ Completado: 2026-03-26 (scheduler.ts) + ETL Orchestrator Agent 2026-03-27
  > `egos-lab/agents/worker/scheduler.ts` — Redis-backed, hourly/daily/weekly/monthly triggers
  > `egos-lab/agents/agents/etl-orchestrator.ts` — AGENT-031, monitoramento br-acc 24/7
  > `egos-lab/agents/registry/agents.json` — etl_orchestrator registrado (hourly, active)
  > `egos-lab/agents/worker/start-all.sh` — Start Worker + Scheduler para Railway

- [ ] **EGOS-104**: Criar agente `uptime_monitor` (24/7)
  > Monitora saúde: Supabase (4 projetos), Vercel (2), VPS (Contabo), Railway
  > Ping endpoints a cada 5 minutos
  > Alerta via WhatsApp/Email quando serviço down
  > **Estimativa:** 4 horas | **Dependências:** EGOS-103

- [ ] **EGOS-105**: Criar agente `quota_guardian` (24/7)
  > Monitora quotas: Alibaba (Qwen), OpenRouter, Groq
  > Alerta quando quota >80% ou erro 429 detectado
  > Sugere fallback automático
  > **Estimativa:** 4 horas | **Dependências:** EGOS-103

### P1 (Important) — Autonomous Agents

- [ ] **EGOS-106**: Criar agente `drift_sentinel` (24/7)
  > Detecta drift entre SSOT (AGENTS.md, TASKS.md) e código real
  > Compara registry com implementação atual
  > Alerta quando divergência encontrada
  > **Estimativa:** 6 horas | **Dependências:** EGOS-103

- [ ] **EGOS-107**: Criar agente `cost_optimizer` (daily)
  > Analisa custos de LLM calls diariamente
  > Identifica oportunidades de otimização (modelo mais barato, caching)
  > Report: quais agentes gastam mais, como reduzir
  > **Estimativa:** 6 horas | **Dependências:** EGOS-103

- [ ] **EGOS-108**: Criar agente `pr_curator` (every 2h)
  > Monitora PRs abertos em todos os repos (9 repos)
  > Identifica: stale PRs (>7 dias), PRs prontos para merge, conflitos
  > Sugere ações: merge, rebase, close
  > **Estimativa:** 6 horas | **Dependências:** EGOS-103, GitHub MCP

### P2 (Strategic) — SDK + API

- [ ] **EGOS-109**: Criar NPM Package `@egos/agents`
  > SDK para desenvolvedores usarem agentes EGOS
  > Exporta: AgentOrchestrator, Scheduler, Registry, MCPToolKit
  > CLI: `npx @egos/agents run <id>`, `npx @egos/agents schedule --list`
  > **Estimativa:** 8 horas | **Dependências:** EGOS-103..105

- [ ] **EGOS-110**: Criar REST API Gateway
  > Endpoints: POST /api/agent/:id/run, GET /api/agent/:id/status
  > WebSocket: /ws/agent/:id/stream (real-time execution)
  > Deploy no Railway
  > **Estimativa:** 8 horas | **Dependências:** EGOS-103..105

---

**Total Value to Deliver:**
- 15 agentes rodando 24/7 (vs 0 hoje)
- 100% coverage de infraestrutura monitorada
- SDK + API para integração externa
- Custo: ~$25-65/mês para swarm completo
- 1 critical feature (frictionless signup)
- 1 major architecture integration (BLUEPRINT-EGOS)
- $60-100/month cost savings identified
- 3 new phase plans (Gem Hunter, web automation, orchestration)
