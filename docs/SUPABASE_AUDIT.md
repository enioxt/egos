# Supabase Audit — `lhscgsqhiooyatkebose` (egos project)
**Date:** 2026-04-08 | **Tables:** 173 in `public` | **Top consumer:** `agent_events` (43 MB / 149.8k rows)

## Domain Map

| Domain | Status | Tables (sample) | Action |
|--------|--------|-----------------|--------|
| **EGOS Core (observability)** | ✅ ACTIVE | `agent_events` (149.8k), `claude_sessions`, `consciousness_reports` (49) | KEEP — hot path |
| **EGOS Wiki / Knowledge** | ✅ ACTIVE | `egos_wiki_pages` (91), `egos_wiki_changelog` (3.9k) | KEEP |
| **Gem Hunter** | ✅ ACTIVE | `gem_hunter_gems` (541), `gem_lists`, `gem_votes`, `gem_list_items` | KEEP |
| **Guard Brasil** | ✅ ACTIVE | `guard_brasil_tenants` (10), `guard_brasil_*` | KEEP |
| **852 Police Bot** | ✅ ACTIVE | `conversations_852` (8), `reports_852` (8), `telemetry_852` (348), `issues_852` (13) | KEEP |
| **Intelink** | ✅ ACTIVE | `intelink_relationships` (4.8k), `intelink_entities` (2.2k), `intelink_*` | KEEP — production |
| **Eagle Eye / OSINT** | ✅ ACTIVE | `opportunities` (121), `osint_events` (117), `osint_costs` (89), `territories` (80) | KEEP |
| **Timeline** | ✅ NEW | `timeline_*` | KEEP |
| **X.com HITL (NEW)** | ✅ NEW | `x_post_queue`, `x_post_options`, `x_post_choices`, `x_post_preferences` | KEEP |
| **Audit Agent** | ✅ ACTIVE | `audit_agent_results` (93), `auth_audit_log` (28), `auth_sessions` (19) | KEEP |
| **Tasks (CCR)** | ⚠️ LOW USE | `tasks` (31), `commits` (60) | KEEP — but evaluate vs TASKS.md |
| **knowledge_base** | ⚠️ HEAVY | 9 rows / **28 MB** (likely vectors stored as bytea) | INVESTIGATE — possibly duplicate of egos_wiki_pages |
| **code_*** indexer | 💀 DEAD | `code_chunks`, `code_symbols`, `code_files`, `code_relations` (all 0 rows, 8.3 MB residual) | DROP — replaced by codebase-memory-mcp |
| **resources** | 💀 DEAD | 0 rows / 2.3 MB | DROP |
| **telemetry_events_v2 / messages_v3 / conversations_v3 / ai_call_metrics / ai_response_cache / detected_patterns / conversation_logs / audit_logs / profiles / rate_limits / user_consents / knowledge_vectors** | 💀 DEAD | All 0 rows | DROP |
| **ethik_*** (12 tables) | 💀 ASPIRATIONAL | 0 rows across all 12 ($ETHIK token system) | ARCHIVE schema, DROP tables |
| **volante_*** (6 tables) | 💀 UNRELATED | 0 rows (driving school product, abandoned) | DROP |
| **nexusmkt_*** (7 tables) | 💀 UNRELATED | Mostly 0 rows, marketplace prototype | DROP |
| **hub_*** (12 tables) | 💀 LOW VALUE | 1-15 rows in 3 tables, rest 0 (legal lab prototype) | ARCHIVE → DROP |

## Bloat Summary

- **~37 dead tables** (0 rows, ~13 MB residual + indexes/policies overhead)
- **4 unrelated domains** (ethik, volante, nexusmkt, hub) = 37 tables total
- **`knowledge_base` 28 MB** with 9 rows = needs investigation (likely fat embeddings or migration debris)
- **No row-level security audit** — many `*_v2`/`*_v3` tables suggest incomplete migrations left both versions

## Duplication Risks

| Pair | Likely winner | Action |
|------|---------------|--------|
| `knowledge_base` vs `egos_wiki_pages` | egos_wiki_pages (active, structured) | Migrate KB → wiki, drop KB |
| `messages_v3` / `conversations_v3` (0) vs `conversations_852` (active) | 852 versions | Drop v3 |
| `telemetry_events_v2` (0) vs `telemetry_852` (348) | 852 version | Drop v2 |
| `auth_audit_log` vs `audit_logs` (0) | auth_audit_log | Drop generic audit_logs |
| `profiles` (0) vs `user_accounts_852` (2) vs `hub_profiles` (1) | Pick 1 canonical for chatbot | Decide post-cleanup |

## Recommendations (priority)

1. **P0 — Drop dead unrelated domains** (`ethik_*`, `volante_*`, `nexusmkt_*`, `hub_*` empty tables): ~30 tables, zero risk.
2. **P0 — Drop empty `*_v2`/`*_v3` migration leftovers**: 8 tables.
3. **P1 — Investigate `knowledge_base` 28 MB**: dump schema + sample, decide migrate-or-drop.
4. **P1 — Drop `code_*` indexer tables**: replaced by codebase-memory-mcp.
5. **P2 — Run `pg_total_relation_size` weekly via CCR**, alert if any non-core table > 50 MB.
6. **P2 — Add naming convention rule**: every new table prefixed with active domain (`egos_`, `gem_`, `guard_`, `intelink_`, `eagle_`, `x_post_`, `timeline_`, `852_`).

## Verification commands

```bash
# Run via Supabase Management API (token in .env SUPABASE_ACCESS_TOKEN)
PROJECT=lhscgsqhiooyatkebose
psql_via_api() { curl -s -X POST "https://api.supabase.com/v1/projects/$PROJECT/database/query" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" -H "Content-Type: application/json" -d "$1"; }

# 1. List dead tables
psql_via_api '{"query":"SELECT relname FROM pg_stat_user_tables WHERE schemaname='\''public'\'' AND n_live_tup=0 ORDER BY relname;"}'

# 2. Total schema size
psql_via_api '{"query":"SELECT pg_size_pretty(sum(pg_total_relation_size(schemaname||'\''.'\''||relname))) FROM pg_stat_user_tables WHERE schemaname='\''public'\'';"}'
```
