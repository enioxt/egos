# TASKS.md — EGOS Framework Core (SSOT)

> **Version:** 2.22.0 | **Updated:** 2026-04-01 | **LAST SESSION:** 2026-04-01 — Vocab guard in pre-commit, Gem Hunter CCR extended with pair analysis, BRACC-001..003 extracted to shared, GOV-001..003 complete, LEAK-001 hook wired

---

### Guard Brasil Monetization Roadmap

**Completed:**
- [x] EGOS-151..157: v0.2.0 (15 patterns), MCP server, market report, VPS orchestrator, /disseminate, /diag, VPS paths
- [x] EGOS-158: npm publish @egosbr/guard-brasil@0.2.0 — **DONE 2026-04-01** (token expires ~2026-04-07)
- [x] EGOS-161: MCP server registered in Claude Code
- [x] Consumer apps PII sync: 852/forja/carteira-livre → 15 patterns each

**P0 — Revenue blocking:**
- [x] EGOS-159: @egosbr/guard-brasil@0.2.0 wired into VPS Docker API — CPF/PII live ✅ 2026-04-01
- [x] EGOS-160: Reversible redaction — tokenize()/restore() in packages/guard-brasil/src/lib/tokenizer.ts ✅ 2026-04-01

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

**P0 — Standalone extraction (egos-lab being deactivated):**
- [x] EAGLE-000: @egos-lab/shared removed, lib/shared.ts inlined, 5 imports updated ✅ 2026-04-01
- [x] EAGLE-001: 4 API endpoints confirmed in ui/server.ts (opportunities/territories/scans/scan-now) ✅ 2026-04-01
- [x] EAGLE-002: Frontend already uses fetch() to all 4 endpoints ✅ 2026-04-01
- [x] EAGLE-003: Dockerfile.standalone, docker-compose.prod.yml, Caddy route eagleeye.egos.ia.br ✅ 2026-04-01
- [x] EAGLE-004: VPS running — eagleeye.egos.ia.br, 15 territories seeded, Caddy reloaded ✅ 2026-04-01

**P1 — Production:**
- [ ] EAGLE-005: Email/Telegram alert service (SendGrid + Telegram Bot API)
- [ ] EAGLE-006: Expand to 50+ territories (add all state capitals + TI hubs)
- [ ] EAGLE-007: PNCP enrichment — wire pncp-client.ts into analysis pipeline
- [x] EAGLE-008: VPS cron added (0 12 * * * = 9am BRT, docker exec eagle-eye bun fetch) ✅ 2026-04-01

**P2 — Revenue:**
- [ ] EAGLE-009: Stripe/Pix payment for Pro tier (R$497/mo, 50+ territories)
- [ ] EAGLE-010: Customer onboarding flow + dashboard customization
- [ ] EAGLE-011: E2E tests (Playwright)

---

### br-acc (EGOS Inteligência) — Valuable Code Mining (2026-04-01)

**6 reusable modules identified (~3000 LOC total):**
- `provenance.py` (63 LOC) — **Proof-of-research hash system**: SHA-256 non-repudiation for data rows + source fingerprinting. Score: 9/10.
- `guard.py` (293 LOC) — Guard Brasil client + offline PII fallback. Score: 8/10.
- `base.py` (177 LOC) — Universal ETL pipeline base class + IngestionRun tracking. Score: 9/10.
- `cache.py` (122 LOC) — Redis cache-aside with graceful degradation. Score: 9/10.
- `neo4j_service.py` (90 LOC) + 47 .cypher files — Neo4j query abstraction. Score: 8/10.
- `transparency_tools.py` (1372 LOC) — 21 Brazilian gov API clients with circuit breaker. Score: 7/10.

**Tasks:**
- [x] BRACC-001: Extract provenance.py → packages/shared/src/provenance.ts ✅ 2026-04-01
- [x] BRACC-002: Extract cache.py pattern → packages/shared/src/cache.ts ✅ 2026-04-01
- [x] BRACC-003: Extract ETL base class → packages/shared/src/pipeline-base.ts ✅ 2026-04-01
- [ ] EGOS-128: Phase 2+3 (Python imports + Docker rename)
- [ ] EGOS-129: Docker network rename + redeploy Hetzner

---

### Governance Registry Health (2026-04-01)

**Triple registry system found (working at ~60%):**
- `docs/CAPABILITY_REGISTRY.md` v1.8.0 — 130+ capabilities, 12 domains. **Working.**
- `docs/SSOT_REGISTRY.md` v2.0.0 — 30+ domain SSOTs. **Working.**
- `docs/ECOSYSTEM_CLASSIFICATION_REGISTRY.md` v2.0.0 — repo governance classes. **NOT synced to leaves.**

**Tasks:**
- [x] GOV-001: Add ECOSYSTEM_CLASSIFICATION_REGISTRY.md to governance-sync.sh CANONICAL_DOCS ✅ 2026-04-01
- [x] GOV-002: Sync leaf repos (carteira-livre/forja/852/smartbuscas) — all 3 registries fresh ✅ 2026-04-01
- [x] GOV-003: Daily governance-sync cron added (0 12 * * * = 9am BRT) ✅ 2026-04-01

> **Archived:** All session summaries, ARCH project, benchmark plans, Grok intake → `docs/knowledge/TASKS_ARCHIVE_2026.md`

---

### Gem Hunter v2 — Pair Analysis Engine (2026-04-01)

**Source:** ChatGPT conversation analysis + egos-lab Gem Hunter v5.0 handoff
**Architecture:** 6-layer pipeline (Discovery→Triage→Pair Diagnosis→Decision Intelligence→SSOT→Continuous Operation)

**Done:**
- [x] Gem Hunter v5.0 Atomic Discovery Engine (anti-poisoning ≥40, -15 non-code, CJK block)
- [x] CCR scheduled job: Gem Hunter Adaptive Intelligence (seg+qui 2h37 BRT)
- [x] Report: 24 gems found 2026-04-01 (top: gptme ACP agent.py, 89pts)

**P0 — Pair Analysis Core:**
- [x] GH-001: Create `/study` skill — pair-analysis session for EGOS ↔ 1 reference repo
- [x] GH-002: Create `/study-end` skill — mandatory closure (9 sections: scorecard, transplants, blind spots, next recs)
- [x] GH-003: SSOT structure: `docs/gem-hunter/registry.yaml`, `pairs/`, `weights.yaml`, `SSOT.md`
- [x] GH-004: Weighted scoring config: `docs/gem-hunter/weights.yaml` (9-factor rubric)
- [x] GH-010: EGOS ↔ Continue — score 71/100, 5 transplants identified, 3 anti-patterns

**New tasks from Continue study:**
- [ ] GH-025: `/pr` workflow + GitHub App — pre-merge gate invoking ssot-auditor + code-intel on branch diffs
- [ ] GH-026: Upgrade codebase-memory-mcp to HTTP/SSE transport (enables SaaS deployments)
- [ ] GH-027: `.guarani/checks/` layer — markdown-as-config for non-technical rule authoring

**Gem Hunter CCR:**
- [x] GH-028: Gem Hunter Adaptive CCR extended with Mission 2 (pair analysis Phase 6) ✅ 2026-04-01

**P1 — Reference Repo Study Queue (priority order):**
- [ ] GH-010: EGOS ↔ Continue (`continuedev/continue`) — repo-native governance, checks, config-driven agents
- [ ] GH-011: EGOS ↔ Aider (`Aider-AI/aider`) — safe edit/diff/git loop, audit trail
- [ ] GH-012: EGOS ↔ Cline (`cline/cline`) — IDE agent autonomy, human-in-the-loop UX
- [ ] GH-013: EGOS ↔ OpenHands (`OpenHands/OpenHands`) — full software agent SDK/CLI/GUI
- [ ] GH-014: EGOS ↔ LangGraph (`langchain-ai/langgraph`) — stateful long-running agents, durable execution
- [ ] GH-015: EGOS ↔ OpenAI Agents SDK (`openai/openai-agents-python`) — handoffs, guardrails, tracing
- [ ] GH-016: EGOS ↔ LiteLLM (`BerriAI/litellm`) — multi-model proxy, cost tracking, routing
- [ ] GH-017: EGOS ↔ Langfuse (`langfuse/langfuse`) — observability, prompt versioning, evals

**P2 — Advanced Studies:**
- [ ] GH-020: EGOS ↔ Mem0 — persistent agent memory layer
- [ ] GH-021: EGOS ↔ Temporal TS SDK — durable workflow engine
- [ ] GH-022: EGOS ↔ Haystack — RAG/retrieval/context engineering
- [ ] GH-023: EGOS ↔ DSPy — programmatic prompt optimization
- [ ] GH-024: Lego Assembler agent — consumes `.md` SSOT blocks from discovery engine

---

### Claude Code Leak Intelligence (2026-04-01)

**Source:** X threads analysis (2038965567269249484, 2038894956459290963), clean-room approach
**Principle:** Learn from public patterns, never use leaked code. Evidence-based only.

**Done:**
- [x] CLAUDE.md v2.1 employee-grade overrides (verification gates, context management, edit safety)
- [x] settings.json: permissions + hooks configured
- [x] Awareness: 44 feature flags, KAIROS, BUDDY, Coordinator Mode, anti-distillation patterns

**P1 — Claude Code Hardening:**
- [x] LEAK-001: Frustration-detection hook wired (UserPromptSubmit → ~/.claude/hooks/frustration-detector) ✅ 2026-04-01
- [ ] LEAK-002: autoDream-inspired memory consolidation — scheduled CCR job to prune/consolidate MEMORY.md (24h trigger)
- [ ] LEAK-003: Coordinator Mode skill — `/coordinator` to launch multi-agent orchestration (Research→Synthesis→Implementation→Verification)
- [ ] LEAK-004: Expand hook coverage — add PostToolUse hooks for format/lint after Write/Edit
- [ ] LEAK-005: Anti-compaction guard — re-read critical files after 10+ turns (hook or skill reminder)

**P1 — Architecture Insights (from zainhas blog analysis):**
- [x] LEAK-006: Tool result budgeting — note added to /end Phase 1 ✅ 2026-04-01
- [x] LEAK-007: Structured session memory — fixed sections + 2K cap added to /end Phase 7 ✅ 2026-04-01
- [ ] LEAK-008: Read-parallel/Write-sequential — enforce in EGOS sub-agent swarm patterns
- [ ] LEAK-009: Audit settings.json deny rules — add wildcard patterns for sensitive files (*.env, credentials.*)

**P2 — Awareness (no action needed yet):**
- [ ] LEAK-010: Monitor `Piebald-AI/claude-code-system-prompts` for per-release prompt changes
- [ ] LEAK-011: Monitor `nblintao/awesome-claude-code-postleak-insights` for community patterns
- [ ] LEAK-012: Evaluate Guard Brasil anti-distillation patterns (fake-tool injection for API protection)

---

### Atrian Observability Module (2026-04-01)

**Source:** ChatGPT architecture + OTel public patterns + Claude Code hook system
**Principle:** Collect metadata, not payload. Telemetry mínima de conteúdo, máxima de comportamento.

**P1 — Foundation:**
- [ ] OBS-001: Create `packages/atrian-observability/` module skeleton (instrumentation/, collector/, analytics/, policies/)
- [ ] OBS-002: Define telemetry policy: what can/cannot be logged, retention, opt-out
- [ ] OBS-003: Define 12 trace spans (session.start → session.close) with OTel-compatible format
- [ ] OBS-004: Define 10 core metrics (latency, tokens, failure rate, override rate, stuck loops)

**P2 — Integration:**
- [ ] OBS-010: Wire hooks → OTel spans (PreToolUse/PostToolUse emit span events)
- [ ] OBS-011: Gem Hunter session telemetry (pair analysis duration, transplant acceptance rate)
- [ ] OBS-012: Runtime dashboard vs Product analytics dashboard — separate concerns
- [ ] OBS-013: Privacy-preserving structured logs (no raw code, masked secrets, redacted paths)

---

### Reference Repos — Awareness Registry (2026-04-01)

**Repos identified for study (from ChatGPT analysis + Gem Hunter + leak threads):**

| ID | Repo | Category | Priority |
|----|------|----------|----------|
| continuedev/continue | coding_surface, governance | P1 |
| Aider-AI/aider | coding_surface, agent_runtime | P1 |
| cline/cline | coding_surface, agent_runtime | P1 |
| OpenHands/OpenHands | agent_runtime, product_surface | P1 |
| langchain-ai/langgraph | agent_runtime, durable_workflow | P1 |
| openai/openai-agents-python | agent_runtime, governance_safety | P1 |
| BerriAI/litellm | model_gateway | P1 |
| langfuse/langfuse | observability_evals | P1 |
| pydantic/pydantic-ai | agent_runtime | P2 |
| mem0ai/mem0 | memory_context | P2 |
| Arize-ai/phoenix | observability_evals | P2 |
| vercel/ai | product_surface | P2 |
| temporalio/sdk-typescript | durable_workflow | P2 |
| deepset-ai/haystack | retrieval_context | P2 |
| stanfordnlp/dspy | agent_runtime | P2 |
| modelcontextprotocol/servers | protocol_tooling | P2 |
| hesreallyhim/awesome-claude-code | protocol_tooling | Ref |
| disler/claude-code-hooks-multi-agent-observability | observability_evals | Ref |
| rohitg00/awesome-claude-code-toolkit | protocol_tooling | Ref |
| nblintao/awesome-claude-code-postleak-insights | protocol_tooling | Ref |
