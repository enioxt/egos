# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.19.0 | **Updated:** 2026-04-01 | **LAST SESSION:** 2026-04-01 — Neural Mesh composed, npm published, 3 CCR jobs, Eagle Eye planned

---

### Guard Brasil Monetization Roadmap

**Completed:**
- [x] EGOS-151..157: v0.2.0 (15 patterns), MCP server, market report, VPS orchestrator, /disseminate, /diag, VPS paths
- [x] EGOS-158: npm publish @egosbr/guard-brasil@0.2.0 — **DONE 2026-04-01** (token expires ~2026-04-07)
- [x] EGOS-161: MCP server registered in Claude Code
- [x] Consumer apps PII sync: 852/forja/carteira-livre → 15 patterns each

**P0 — Revenue blocking:**
- [ ] EGOS-159: Wire npm package into Hono server on VPS (currently hardcoded patterns)
- [ ] EGOS-160: Reversible redaction — tokenized mask+restore

**P1 — Competitive:**
- [ ] EGOS-162: Accuracy benchmark vs Presidio/anonym.legal
- [ ] EGOS-163: Pix billing integration
- [ ] EGOS-164: Dashboard — real data from guard_brasil_events

**P2 — Growth:**
- [ ] EGOS-165: White-label outreach
- [ ] EGOS-166: REST API gateway mode

---

### Neural Mesh — Composed (2026-04-01)

**Verdict:** COMPOSE — see `docs/research/NEURAL_MESH_INVESTIGATION_REPORT.md`

**Done:**
- [x] EGOS-167: codebase-memory-mcp installed, 7 repos indexed (51K nodes, 75K edges), 3D graph UI, 4 skills
- [x] PreToolUse hook fixed (allows .md/.json, only blocks first code read)
- [x] CLAUDE.md v2.1 — codebase-memory-mcp rules + scheduled jobs reference

**Remaining:**
- [ ] EGOS-168: llmrefs blocks on 10 more governance docs (manual, 1h)
- [ ] EGOS-169: @aiready/pattern-detect pre-commit (duplicate detection)
- [ ] EGOS-173: CRCDM hooks: llmrefs staleness + auto-heal rename
- [ ] EGOS-175: Kernel llmrefs pointers in 7 leaf AGENTS.md files

---

### Scheduled Jobs — 3 CCR slots (2026-04-01)

All Haiku, 00-06h BRT, reports in `docs/jobs/` + `docs/gem-hunter/`

- [x] Governance Drift Sentinel — diário 0h17 BRT (trig_01S5za...)
- [x] Code Intel + Security Audit — seg+qui 1h42 BRT (trig_01RDDk...)
- [x] Gem Hunter Adaptive Intelligence — seg+qui 2h37 BRT (trig_01Sn7Y...)
- [x] /start v5.6 — Phase 6 reads job results, flags CRITICAL as P0
- [x] GitHub Actions audit: 9 failing workflows disabled, only essential kept

---

### Eagle Eye — OSINT Licitações (2026-04-01)

**Code:** `/home/enio/egos-lab/apps/eagle-eye/`
**Domain:** `eagleeye.egos.ia.br` (DNS configured, Caddy pending)
**Supabase:** `lhscgsqhiooyatkebose` — 6 tables created, 15 territories seeded

**Done:**
- [x] Backend pipeline: Querido Diário API → AI analysis (Gemini Flash ~$0.01/gazette) → 26 patterns
- [x] Supabase migration executed (territories, opportunities, scans, users, alerts, notifications)
- [x] React frontend (Dashboard, Reports, Analytics) — renders with mock data
- [x] Detection patterns: 26 across 3 tiers (licitações, LGPD, INPI, fiscal, etc.)

**P0 — MVP (blocks demo):**
- [ ] EAGLE-001: Implement 4 API endpoints in server.ts (GET /api/opportunities, territories, scans, POST /api/scan/trigger)
- [ ] EAGLE-002: Wire frontend → API (replace mock data with fetch() calls in Dashboard.tsx, Reports.tsx, Analytics.tsx)
- [ ] EAGLE-003: Deploy to VPS — Dockerfile build, docker-compose, Caddy route for eagleeye.egos.ia.br
- [ ] EAGLE-004: Run first real scan and verify data flows end-to-end

**P1 — Production:**
- [ ] EAGLE-005: Email/Telegram alert service (SendGrid + Telegram Bot API)
- [ ] EAGLE-006: Expand to 50+ territories (add all state capitals + TI hubs)
- [ ] EAGLE-007: PNCP enrichment — wire pncp-client.ts into analysis pipeline
- [ ] EAGLE-008: VPS cron for daily scan (replace GitHub Actions, use crontab on Hetzner)

**P2 — Revenue:**
- [ ] EAGLE-009: Stripe/Pix payment for Pro tier (R$497/mo, 50+ territories)
- [ ] EAGLE-010: Customer onboarding flow + dashboard customization
- [ ] EAGLE-011: E2E tests (Playwright)

---

### Other Active

**br-acc rename:**
- [ ] EGOS-128: Phase 2+3 (Python imports + Docker) — `bash rename-to-egos-inteligencia.sh --execute`
- [ ] EGOS-129: Docker network rename + redeploy Hetzner

> **Archived:** All session summaries, ARCH project, benchmark plans, Grok intake, P0-P2 historical completion → `docs/knowledge/TASKS_ARCHIVE_2026.md`
