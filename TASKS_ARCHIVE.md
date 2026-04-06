# TASKS_ARCHIVE.md — Completed Tasks
> Auto-archived from TASKS.md when approaching 500-line limit.
> Append-only. Never edit manually. Use scripts/archive-tasks.sh


## Archived 2026-04-06 (74 tasks)

- [x] KB-001: Supabase schema (3 tables + RLS + indexes) ✅ 2026-04-05
- [x] KB-002: wiki-compiler agent (--compile, --world, --lint, --index, --dry) ✅ 2026-04-05
- [x] KB-003: Gateway API endpoints (7 routes: pages, search, index, learnings, stats) ✅ 2026-04-05
- [x] KB-004: World-model integration (--world generates system overview, P0 blockers, signals) ✅ 2026-04-05
- [x] KB-005: Initial compile — 50 pages from 5 raw source dirs, avg quality 80/100 ✅ 2026-04-05
- [x] KB-006: Agent registered in agents.json + AGENTS.md ✅ 2026-04-05
- [x] KB-007: NPM scripts (wiki:compile, wiki:lint, wiki:index) ✅ 2026-04-05
- [x] KB-008: Add wiki:compile to Governance Drift CCR job (auto-compile after drift check) ✅ 2026-04-05
- [x] KB-009: /start Phase 0 — include KB stats (page count, avg quality, stale pages) ✅ 2026-04-05
- [x] KB-010: Record learnings from each Claude Code session (POST /knowledge/learnings on /end) ✅ 2026-04-05
- [x] KB-011: HQ Knowledge Base page (/knowledge) + Mission Control KB card ✅ 2026-04-05
- [x] KB-012: Cross-reference enrichment — 3-strategy enrichment (entity/slug/tag), 0 orphans ✅ 2026-04-04
- [x] KB-013: Deduplication — detect similar pages and merge (wiki:dedup) ✅ 2026-04-05
- [x] KB-014: LLM enrichment pass for low-quality pages (<60) via qwen-plus (wiki:enrich) ✅ 2026-04-05
- [x] KB-015: Full-text search with pg_trgm or pgvector embeddings ✅ 2026-04-06 — pg_trgm GIN indexes + ?mode=fts param using phfts(portuguese)
- [x] KB-016: Knowledge graph visualization — /ui dashboard (egos-gateway) with category cards, search, quality scores, learnings panel ✅ 2026-04-04
- [x] KB-018: MCP server @egos/knowledge-mcp — 5 tools: search_wiki, get_page, get_stats, record_learning, list_learnings ✅ 2026-04-05
- [x] EGOS-175: llmrefs blocks added to 5 leaf AGENTS.md (forja, carteira-livre, smartbuscas, br-acc, santiago) ✅ 2026-04-01
- [x] START-009: Alert system (Telegram on health < 40%) ✅ 2026-04-05 — health-monitor.ts polls 5min, score=100, alerts to TELEGRAM_AUTHORIZED_USER_ID
- [x] Governance Drift Sentinel — diário 0h17 BRT (trig_01S5za...)
- [x] Code Intel + Security Audit — seg+qui 1h42 BRT (trig_01RDDk...)
- [x] Gem Hunter Adaptive Intelligence — seg+qui 2h37 BRT (trig_01Sn7Y...)
- [x] /start v5.6 → v6.0 — upgraded from skill to self-contained executable ✅ 2026-04-02
- [x] GitHub Actions audit: 9 failing workflows disabled, only essential kept
- [x] GH-061: Dashboard gemhunter.egos.ia.br ✅ 2026-04-06 — 288 gems, dark SPA servida em / (sem Next.js)
- [x] GH-067: gem-hunter-server deployed to VPS port 3095, systemd, Caddy ready ✅ 2026-04-05 — [BLOCKER] DNS A record gemhunter.egos.ia.br → 204.168.217.125 needed
- [x] GH-068: API keys Supabase auth | GH-069: Rate limiting ✅ 2026-04-05
- [x] GH-070: WhatsApp v2 — AI orchestrator (Qwen+tools: gem_search/wiki_search/status/costs/agents) + all media types ✅ 2026-04-05
- [x] GH-071: Telegram @EGOSin_bot (egosin_bot) — long-polling + AI orchestrator ✅ 2026-04-05 — send /start to @EGOSin_bot to get your chat_id, then set TELEGRAM_AUTHORIZED_USER_ID
- [x] GH-028: Gem Hunter Adaptive CCR extended with Mission 2 (pair analysis Phase 6) ✅ 2026-04-01
- [x] GH-010: EGOS ↔ Continue — score 71/100 (done — see P0 section above)
- [x] GH-011: EGOS ↔ Aider — score 74/100, 4 transplants (dry-run, dirty-commit, SWE-Bench eval, weak model) ✅ 2026-04-01
- [x] GH-012: EGOS ↔ Cline (`cline/cline`) — score 72.8/100, 4 transplants (permission-flow-ux, model-gateway-abstraction, ast-aware-context, checkpoint-rollback) ✅ 2026-04-02
- [x] GH-061: Dashboard web — gemhunter.egos.ia.br ✅ 2026-04-06
- [x] GH-062: packages/gem-hunter/ — @egosbr/gem-hunter v6.0.0 ✅ 2026-04-02
- [x] GH-064: Discord webhook alerts — sendGemDiscordAlert() rich embeds (score≥80, color-coded); DISCORD_WEBHOOK_URL env ✅ 2026-04-02
- [x] GH-066*: Gateway /gem-hunter channel — sector filter, topics, product pricing, trending ✅ 2026-04-04 (NOTE: renamed from Paper→Code)
- [x] GH-068: Auth — API keys via Supabase `gem_hunter_api_keys` table + Bearer token validation ✅ 2026-04-05
- [x] GH-069: Rate limiting middleware (tier-aware: free/starter/pro/pay-per-use) ✅ 2026-04-05
- [x] GH-071: Telegram bot (/hunt, /trending, /sector slash commands) ✅ 2026-04-06 — all 3 commands live in telegram.ts, /sector validates 6 sectors
- [x] X-001: `scripts/x-reply-bot.ts` CODE ONLY (348 LOC) — NOT deployed on VPS, no cron, needs X_BEARER_TOKEN ⚠️
- [x] X-002: `scripts/rapid-response.ts` CODE ONLY (217 LOC) — manual utility, not automated ⚠️
- [x] X-003: VPS cron deploy ✅ Verified 2026-04-04 — x-reply-bot running hourly on VPS cron (0 * * * *).
- [x] X-004: Hermes-3 added to llm-provider (model config only, no active usage) ✅ 2026-04-01
- [x] X-005: `scripts/check-legacy-code.sh` in pre-commit ✅ 2026-04-01
- [x] X-006: Grow capability profiles in rapid-response.ts (add br-acc, 852, BRAID executor) ✅ 2026-04-06 — br_acc, sistema_852, gem_hunter profiles added
- [x] X-007: `--post-thread` flag in rapid-response.ts — auto-post first tweet of thread ✅ 2026-04-06 — OAuth 1.0a posting, falls back to manual instructions
- [x] X-008: Daily X report to Telegram (how many replies sent, top threads engaged) ✅ 2026-04-06 — RunStats + sendDailyReport() in x-reply-bot.ts
- [x] INTEL-005: Signal ingestion — Gem Hunter scores > 80 → auto-append to world model signals (= GH-050) ✅ 2026-04-06 — gem-hunter.ts appends type:gem_discovery, capped at 50
- [x] PART-002: Posts X.com + LinkedIn preparados ✅ 2026-04-06 — docs/GTM_SSOT.md §4 (aguarda og-image + postagem manual)
- [x] MCP-001: Firecrawl MCP installed (`fc-45cf069ee7ef4c3aa4942a41127d8629`, tested against guard.egos.ia.br) ✅ 2026-04-06
- [x] MCP-002: GitHub MCP installed (PAT token, repo access) ✅ 2026-04-06
- [x] MCP-003: Brave Search MCP installed (`BSA0E6k_mAdnrOrieC_zRvLGhuu-4lp`) ✅ 2026-04-06
- [x] MCP-004: Playwright MCP installed (headless browser automation) ✅ 2026-04-06
- [x] FOCUS-001: focus-enforcement v2.0 — FORBIDDEN-list replaces allowlist (researcher-builder profile) ✅ 2026-04-06
- [x] INFRA-001: pre-commit hook TTY graceful fallback for non-interactive environments ✅ 2026-04-06
- [x] RES-001: Guard Brasil market research — ICP confirmed, 5 competitors mapped, Privacy Tools BR = partner ✅ 2026-04-06
- [x] DC-001: Supabase tables `egos_nightly_logs` + `egos_nightly_reports` (migration applied) ✅ 2026-04-06
- [x] DC-002: Log Harvester script v1.1 (bash, 9 containers, severity classification) ✅ 2026-04-06
- [x] DC-003: VPS cron `0 2 * * *` (23h00 BRT) + Telegram alerts on critical ✅ 2026-04-06
- [x] LLM-001: Google AI Studio provider (Gemma 4 31B + Gemini 2.5 Flash free quota) ✅ 2026-04-06
- [x] LLM-002: Qwen 3.6 Plus free via OpenRouter ($0/token) — new first OpenRouter model ✅ 2026-04-06
- [x] OC-001: Telegram local — decidido: @egosmarkets_bot no VPS, local sem Telegram (evitar conflito com EGOS Gateway @EGOSin_bot). VPS pronto.
- [x] OC-002: Pipeline testado — `openclaw agent --message "..."` → billing proxy → Claude Sonnet 4.6 (PIPELINE_FINAL_OK ✅)
- [x] OC-003: Modelo padrão: `anthropic-subscription/claude-haiku-4-5-20251001` (P28: Haiku default, Sonnet complex, fallback: Qwen3-free+DashScope). Fixes: `api:"anthropic-messages"` + `apiKey` + auth-profiles.json.
- [x] OC-004: `~/.openclaw/workspace/USER.md` populado com perfil Enio (projetos, infra, preferências, estilo).
- [x] OC-005: Token auto-refresh: `0 */4 * * *` rsync credentials local→VPS. Proxy relê por request — sem restart.
- [x] OC-024..026: VPS watchdog, HQ health 4/4, UFW Docker bridge ✅ 2026-04-06
- [x] OC-027: Codex proxy (port 18802) local + VPS — gpt-5.4 via ChatGPT subscription, usage tracking 5h janela ✅ 2026-04-06
- [x] OC-028: Constitutional review cron (6h+18h) — Codex revisa commits, regras, focus, assina jobs ✅ 2026-04-06
- [x] OC-029: HQ v2 — 5 serviços, cards colapsáveis, quota bar Codex, action buttons (review + billing-refresh) ✅ 2026-04-06
- [x] OC-030: Smart TASKS.md archiving — auto-arquiva [x] a 490+ linhas, bloqueia a 600+ ✅ 2026-04-06
- [x] OC-009: `HEARTBEAT.md` configurado (Guard Brasil health, billing proxy, EGOS Gateway, Gem Hunter, daily summary).
- [x] OC-015: `TOOLS.md` configurado (SSH VPS, serviços EGOS, billing proxy, repos, bots).

## Archived 2026-04-06 (4 tasks)

- [x] DOC-001: Restore `docs/INFRASTRUCTURE_ARCHIVE_AUDIT.md` and reconnect broken references
- [x] DOC-002: Align `README.md`, `CONTRIBUTING.md`, `SYSTEM_MAP.md`, `MASTER_INDEX.md`, `SSOT_REGISTRY.md`
- [x] DOC-003: Align `EXECUTIVE_SUMMARY_DECISION_MATRIX.md`, `INVESTIGATION_FINAL_SUMMARY.md`, `ARCHIVE_GEMS_CATALOG.md`, `docs/_investigations/DISCONNECTED_SYSTEMS_ANALYSIS.md`
- [x] DOC-004: Run `bun run governance:sync:exec` + `bun run governance:check` (drift 0)

## Archived 2026-04-06 (6 tasks)

- [x] **HQC-001**: Normalize HQ task namespace — keep `HQ-*` for ecosystem backlog and move dashboard implementation track to `HQV2-*`
- [x] **HQC-002**: Register `agent-validator.ts` in `agents.json` and wire `validation.json` as HQ truth source — **DONE 2026-04-06** (18 agents verified, 0 ghosts)
- [x] **HQC-003**: Create `AGENTS.md` + `TASKS.md` for `commons/` — **DONE 2026-04-06** (Grade D→C, minimum viable governance)
- [x] **HQC-005**: Refresh `MASTER_INDEX.md` from live evidence — split verified vs inferred claims and sync task/integration snapshots — **DONE 2026-04-06** (18 agents, validated registry)
- [x] **HQC-006**: Execute `/start` evidence matrix for kernel + leaf repos + VPS + MCP + OpenClaw + key APIs with explicit pass/warn/fail — **DONE 2026-04-06** (see `docs/_investigations/START_EVIDENCE_MATRIX_2026-04-06.md`)
- [x] **HQC-007**: Create manifests for 6 integration adapters — **DONE 2026-04-06** (1 validated: whatsapp; 5 stubs: slack, discord, telegram, webhook, github — see `integrations/manifests/`)
