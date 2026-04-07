# Handoff — 2026-04-07 (Guard Brasil Bugs Fixed + M-007 Complete)

**Session commits:** 26 total today | **Branch:** main | **Wiki:** 74 páginas

---

## Accomplished Esta Rodada

### Guard Brasil — Bugs Corrigidos e Deployados
- **GUARD-BUG-001 ✅** — RG detecta `12.345.678-9` sem keyword. Regex: `\b\d{1,2}\.\d{3}\.\d{3}-\d\b`. Verificado em prod.
- **GUARD-BUG-005 ✅** — Whitelist expandida: 27 estados BR + termos médicos (HIV/AIDS/UTI) + siglas comuns. MG/HIV não são mais false positives.
- **GUARD-SEC-001 ✅** — `middleware.ts` criado em `apps/guard-brasil-web/`. Basic Auth protege `/dashboard-v{1,2,3}` e `/x-dashboard`. Usa `DASHBOARD_SECRET` env var.
- **ATRiAN demo ✅** — Demo trocado de "viés racial" (nunca existiu) para afirmações absolutas (real). Input: "Com certeza... SEMPRE... Segundo dados do Ministério...". Score 80, 2 violations.
- **Landing honesty ✅** — "Pronto para produção" → "API em desenvolvimento ativo" (P22 rule).

### M-007 — Emails Corretos Encontrados
- **Rocketseat** — email real: `oi@rocketseat.com.br` (fonte: GitHub org). Draft pronto: [abrir](https://mail.google.com/mail/u/0/#drafts?compose=19d69782d2737797)
- **LBCA Advogados** — empresa real por trás de "LGPD Brasil". Email: `lgpd@lbca.com.br` (fonte: lgpdbrasil.com.br). Draft pronto: [abrir](https://mail.google.com/mail/u/0/#drafts?compose=19d697848a37dadf)
- **3 emails já enviados anteriormente**: Nubank, Memed, RD Station ✅

### Commits Chave
- `185b0f7` — fix(guard-brasil): RG + whitelist + middleware + ATRiAN demo
- `4cdce6e` — chore(tasks): tasks atualizadas

---

## Bloqueado — Ação Manual Necessária

### 1. DASHBOARD_SECRET no Vercel [URGENTE]
O middleware está deployado mas **sem a env var o dashboard retorna 503 em produção**.

**Ação:** Vercel dashboard → guard-brasil-web → Settings → Environment Variables → adicionar:
```
DASHBOARD_SECRET = <senha forte gerada: openssl rand -hex 32>
```
Depois redeploy manual ou aguardar próximo push.

### 2. M-007-FIX — Enviar 2 emails restantes
Abrir os drafts acima e enviar. Completa o M-007 (5/5).

---

## Tasks Pendentes para Próxima Sessão

### P0
- [ ] **DASHBOARD_SECRET** — configurar no Vercel (ação manual de 2min, bloqueante para GUARD-SEC-001 ser efetivo)
- [ ] **M-007-FIX** — enviar 2 drafts (Rocketseat + LBCA)

### P1
- [ ] **GUARD-BUG-003** — Nome de pessoa não mascarado. "João da Silva" permanece no output mesmo quando CPF é detectado. Precisa de NER ou regex de nome próprio BR.
- [ ] **GUARD-BUG-004** — Condição médica não mascarada. "HIV positivo", "diabetes", diagnósticos permanecem. Precisa de lista de termos médicos sensíveis.
- [ ] **GTM-002** — X.com thread (4 tweets com demos Guard Brasil, rascunhos prontos em GTM_SSOT §4.1)
- [ ] **CHAT-002** — Fix duplicate Section 11 em CHATBOT_SSOT.md + bump v2.0.0
- [ ] **CHAT-004** — Input-side PII scan em 852 antes do LLM (usa `pii-scanner.ts` existente)
- [ ] **CHAT-005** — `MemoryStore` adapter interface + Supabase impl em `packages/shared/src/memory-store.ts`
- [ ] **CHAT-007** — Abort signal propagation em 852 — `req.signal` → `streamText abortSignal`
- [ ] **CHAT-008** — Per-identity budget em `packages/shared/src/rate-limit.ts`
- [ ] **CHAT-010** — egos-web compliance jump 64→90+

### P2
- [ ] **GUARD-BUG-006** — guardVersion inconsistente (receipt=0.2.1 vs meta=0.2.2). Sync GUARD_VERSION constant.
- [ ] **SSOT-MCP** — Consolidar 7 MCP_*.md → `docs/MCP_SSOT.md`
- [ ] **SSOT-OUTREACH** — Migrar docs/outreach/ (8 arquivos) → GTM_SSOT.md §partnerships
- [ ] **HERMES-005 monitoring** — Gate 2026-04-15. Verificar `/tmp/hermes-token-refresh.log`

### Backlog
- [ ] RATIO-001..003 — PRs para Carlos Victor (Guard Brasil PII guard no carlosvictorodrigues/ratio)
- [ ] ARR-001..003 — Ativar search-engine em Gem Hunter + KB
- [ ] DRIFT-012/013 — Drift dashboard no HQ

---

## Environment State

| Serviço | Status |
|---------|--------|
| Guard Brasil API | ✅ v0.2.2, RG fix deployed |
| guard-brasil-web (Vercel) | ✅ middleware deployed, ⚠️ DASHBOARD_SECRET não configurado |
| VPS RAM | 5.4GB/15GB |
| HERMES-005 trial | 🔄 monitoring até 2026-04-15 |
| M-007 | 3/5 enviados, 2 drafts prontos para envio |
| Wiki KB | ✅ 74 páginas, avg 80/100 |

---

## Contexto Crítico para Próximo Agente

**Guard Brasil sandbox agora tem 4/6 demos funcionando corretamente** (CPF ✅, RG ✅, Placa ✅, ATRiAN ✅). Faltam: nome próprio e condição médica (GUARD-BUG-003/004).

**ATRiAN bias nunca existiu** — era feature prometida no frontend mas sem implementação. Demos agora mostram o que realmente funciona. Se o produto quiser oferecer detecção de viés, é uma feature nova (GUARD-FUTURE-001).

**M-007:** 5 emails prontos (3 enviados). Para os 2 restantes, os drafts estão no Gmail — só abrir e enviar.
