# Handoff — 2026-04-07 (Hermes Claude OAuth + Haiku Default)

**Session commits:** 11 | **TASKS.md:** 497 lines | **Branch:** main

---

## Accomplished

- **Hermes v0.7.0 deployed** — local + VPS with Claude OAuth auto-detection
  - Local: [`~/.hermes-agent/`](.hermes-agent/) + `~/.local/bin/hermes`
  - VPS: `/opt/hermes-agent` + `/opt/hermes-venv` (Hetzner enioxt-egos)
  - Auth: reads `~/.claude/.credentials.json` — `claude_code oauth ←` active on both
- **Haiku 4.5 default** — `claude-haiku-4-5-20251001` set on default + egos-kernel profile (local + VPS)
- **Profile `egos-kernel`** — created on both machines with EGOS system prompt
- **Token refresh cron** — `*/5 * * * *` local: refresh if <10min → scp to VPS → `hermes auth reset anthropic`
- **Script** — [`~/.hermes-agent/scripts/refresh-token.py`](.hermes-agent/scripts/refresh-token.py) (proactive, <10min threshold)
- **Tests 3/3 ✅** — `HAIKU_LOCAL_OK`, `EGOS_KERNEL_HAIKU_OK`, `HAIKU_VPS_OK` (ran real bash tools)
- **HARVEST.md v4.3.0** — P36 patterns: OAuth, rotating refreshToken, exhaustion reset, profiles
- **CAPABILITY_REGISTRY.md §19** — Hermes Agent always-on executor capability
- **TASKS.md** — HERMES-001..004 marked complete, Phase 4 tests updated
- **Telegram** — milestone notification sent (message_id: 1456)

---

## In Progress (80%)

- **HERMES-005 trial** — 1-week trial started 2026-04-07, gate 2026-04-15
  - Monitor: uptime, RAM, token consumption, error rate on VPS
  - Validate: at least 1 auto-generated skill persisted to SQLite

---

## Blocked

- **HERMES-004-P3 (Telegram integration)** — Deferred to HERMES-006 scope. Chat ID confirmed (171767219) but Hermes gateway not configured yet.
- **19 stale llmrefs** — non-blocking, `python3 scripts/qa/llmrefs_staleness.py --root .` to fix

---

## Next Steps (priority order)

1. **HERMES-005 monitoring** — check `/tmp/hermes-token-refresh.log` after 30min to confirm cron works
2. **HERMES-006** (post-trial 2026-04-15) — scale to 6 profiles if trial passes
3. **Guard Brasil GTM** — M-007 outreach emails still the #1 revenue blocker
4. **RATIO-001..006** — Carlos Victor collaboration PRs (see memory/project_ratio_collaboration.md)

---

## Environment State

| Service | Status |
|---------|--------|
| Guard Brasil API | ✅ healthy v0.2.2 |
| VPS RAM | 5.5GB used / 15GB total (healthy) |
| Hermes local | ✅ v0.7.0, claude-haiku-4-5-20251001 |
| Hermes VPS | ✅ v0.7.0, credentials synced |
| Token refresh cron | ✅ active (*/5 local) |
| Claude OAuth token | ✅ valid ~7h (expires 23:25 BRT) |

## Critical Note: refreshToken rotation

The OAuth refreshToken rotates on each use. **Only the local machine** may refresh. If VPS somehow refreshes independently (e.g., manual `hermes` run that triggers a refresh), local credentials become invalid. The cron guards this by always syncing local→VPS. Monitor `/tmp/hermes-token-refresh.log`.
