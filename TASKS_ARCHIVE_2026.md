# TASKS Archive — Compressed entries (2026-04-08)
_Auto-compressed by QA-002 tasks-archive. Original [x] tasks preserved here._


## ### Supabase Cleanup (2026-04-08)
- [x] **SUPA-001 [P0]**: Drop unrelated domains (`ethik_*` 12, `volante_*` 6, `nexusmkt_*` 7, empty `hub_*`) — 0 risk, ~30 tables ✅ 2026-04-08
- [x] **SUPA-002 [P0]**: Drop empty `*_v2`/`*_v3` migration leftovers (`telemetry_events_v2`, `messages_v3`, `conversations_v3`, `ai_call_metrics`, `ai_response_cache`, `audit_logs`, `profiles`, `rate_limits`, `user_consents`, `knowledge_vectors`, `detected_patterns`, `conversation_logs`) ✅ 2026-04-08
- [x] **SUPA-003 [P1]**: Investigate `knowledge_base` — KEEP. 1648 rows / 28 MB (task had stale "9 rows"). pgvector embeddings = ARR data. `egos_wiki_pages` (92 rows) = separate wiki system. Different purposes, no migration needed. ✅ 2026-04-08
- [x] **SUPA-004 [P1]**: Drop `code_*` indexer tables (chunks/symbols/files/relations) — replaced by codebase-memory-mcp ✅ 2026-04-08

## ### CLAUDE.md Modular Refactor (2026-04-08)
- [x] **RULES-001 [P0]**: ✅ Critical rules block at top of ~/.claude/CLAUDE.md — 5 non-negotiables in primacy position.
- [x] **RULES-001b [P1]**: GUARD_BRASIL_API_KEY missing — PII check in article-writer fails silently. Set in ~/.egos/secrets.env. Found: TL-002 dry-run. ✅ 2026-04-08
- [x] **RULES-002 [P1]**: ✅ ~/.claude/egos-rules/ created — ssot-map.md, doc-drift.md, jobs-monitoring.md, llm-routing.md, product-gtm.md
- [x] **RULES-003 [P1]**: ✅ §12, §13, §28, §29 compressed → references to egos-rules/ — 653→615 lines
- [x] **RULES-005 [P1]**: ✅ Pointer table added after CRITICAL NON-NEGOTIABLES block
- [x] **RULES-008 [P1]**: ✅ Governance kernel propagation live 2026-04-08 — scripts/governance-propagate.sh applied to 12 local + 4 VPS repos. Crons: local 04:00 + VPS 05:00. git init wrapper in ~/.bashrc for new repos. ~/.egos/sync.sh updated (egos-inteligencia added).

## ### KB-as-a-Service — Patos de Minas (KBS-PM-*) (2026-04-08)
- [x] **KBS-PM-001 [P0]**: Popular Agrônomo com 5 fazendas demo (Boa Vista/São João/Vereda/Estrela/Lagoa Azul) + 10 visitas técnicas + 8 defensivos aprovados com dados reais MAPA. | 3h ✅ 2026-04-08
- [x] **KBS-PM-002 [P0]**: Popular Advocacia com 8 processos demo TJMG + 5 jurisprudências STJ (direito agrário) + 3 modelos de petição posse rural. | 3h ✅ 2026-04-08
- [x] **KBS-PM-003 [P0]**: Popular Contador com 6 clientes rurais demo + 12 obrigações fiscais (ITR/Funrural/INSS) + 5 normas tributárias rurais. | 2h ✅ 2026-04-08
- [x] **KBS-PM-004 [P0]**: Popular FORJA com 8 peças demo (eixo/flange/bucha/suporte) + 5 orçamentos históricos + 3 atas de reunião transcritas. | 4h ✅ 2026-04-08
- [x] **KBS-PM-005 [P0]**: Escrever `CLAUDE.md` para cada perfil (5 arquivos, PT-BR) — contexto setorial, tom correto, limites, fontes prioritárias. Salvar em `packages/knowledge-mcp/templates/sectors/`. | 4h ✅ 2026-04-08
- [x] **KBS-PM-007 [P1]**: Criar databases para Consultor de Gestão Rural (perfil 04) — Fazendas, Custo Produção, Benchmarks. | 2h ✅ 2026-04-08
- [x] **KBS-PM-008 [P1]**: Criar databases para Veterinário (perfil 05) — Pacientes, Medicamentos+carência, Protocolos+Vacinações. | 2h ✅ 2026-04-08
- [x] **KBS-PM-009 [P1]**: Criar databases para Engenheiro (perfil 06) — ARTs, Projetos, Normas Técnicas. | 2h ✅ 2026-04-08
- [x] **KBS-PM-010 [P1]**: Criar databases para Médico (perfil 07) — Protocolos Clínicos, Medicamentos, Regulação ANS/CFM. | 2h ✅ 2026-04-08
- [x] **KBS-PM-011 [P1]**: Popular perfis P1 com dados demo relevantes (5 registros cada, 12 databases). | 4h ✅ 2026-04-08
- [x] **KBS-PM-014 [P1]**: Escrever 1-pager "Por que a Inteligência da Empresa substitui o ERP burro" em PT-BR. Foco em FORJA/metalurgia. Salvar em `docs/strategy/ERP_REPLACEMENT_NARRATIVE.md`. | 2h ✅ 2026-04-08

## ### Gem Hunter — Feedback Loop v8 (2026-04-08)
- [x] **GH-089 [P1]**: Extrair scoring prompts hardcoded do `gem-hunter.ts:2274` → `docs/gem-hunter/prompts/scoring-v1.md` (versionado, editável sem deploy). | 2h ✅ 2026-04-08
- [x] **GH-090 [P1]**: Supabase migration: `gem_feedback(id uuid, alert_id text, gem_url text, reaction text, comment text, run_id text, created_at timestamptz)` + RLS policy (service role only). | 1h ✅ 2026-04-08
- [x] **GH-091 [P1]**: Qwen-based scoring para gems gerais (não só papers) — adicionar categoria `"low_visibility_research_gem"` em `scoreGem()`: big-tech eng + poucos likes/stars + código real = +25 pts. | 4h ✅ 2026-04-08
- [x] **GH-092 [P1]**: Telegram inline keyboard em alerts — botões 👍👎🔍💬 + webhook handler que salva em `gem_feedback`. Usar `sendMessage` com `reply_markup.inline_keyboard`. | 6h ✅ 2026-04-08
- [x] **GH-093 [P1]**: `scripts/scoring-feedback-reader.ts` — cron 2x/dia (09:00 + 21:00 BRT) lê `gem_feedback` → gera relatório `docs/jobs/scoring-feedback-YYYY-MM-DD.md` → auto-cria tasks via auto-disseminate. | 6h ✅ 2026-04-08
- [x] **GH-094 [P1]**: Repetition detector — hash URL+author, score -30 se mesma gem apareceu nos últimos 30 dias. Persistir hashes em `gem_seen_cache` table. | 3h ✅ 2026-04-08
- [x] **GH-095 [P1]**: `docs/gem-hunter/preferences.md` — SSOT de preferências co-editado Enio+AI: categorias valorizadas, red-flags, exemplos curados dos 8 posts analisados. | 2h ✅ 2026-04-08 ✅ 2026-04-08
