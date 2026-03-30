# Handoff Canônico — 2026-03-30

> **Gerado por:** Claude Code Sonnet 4.6 — /end completo
> **Próxima sessão:** ler `MANUAL_ACTIONS.md` antes de qualquer planejamento

---

## Estado do Sistema Agora

### Infra Hetzner (204.168.217.125) — 12 containers

```
guard-brasil-api   Up 2h (healthy)   127.0.0.1:3099  ← NOVO esta sessão
852-app            Up 2 dias (healthy) 127.0.0.1:3001
bracc-neo4j        Up 2 dias (healthy) 127.0.0.1:7474/7687
infra-caddy-1      Up 2 dias           :80/:443 (TLS auto)
evolution-api      Up 16h             :8080
waha-santiago      Up 2 dias          :3002
egos-media-web-1   Up 2 dias          :3015
infra-frontend-1   Up 2 dias (healthy) 127.0.0.1:3000
infra-api-1        Up 2 dias (healthy) 127.0.0.1:8000
infra-redis-1      Up 2 dias (healthy)
openclaw-sandbox   Up 2 dias (healthy)
evolution-postgres Up 16h (healthy)
```

### Guard Brasil API
- Container: `guard-brasil-api` saudável, 4ms latência
- Caddy: entrada `guard.egos.ia.br` configurada, TLS automático
- **DNS faltando** (M-002) — registro A `guard → 204.168.217.125` não criado
- Cron watchdog: `*/5 * * * *` → restart automático se cair
- API key: `/opt/apps/guard-brasil/.env`
- Teste interno: `ssh hetzner 'curl -sf http://localhost:3099/health'`

### Testes e Build
- Guard Brasil: 15/15 pass — `bun test packages/guard-brasil/src/guard.test.ts`
- TypeScript: `tsc --noEmit` OK
- Governance: 0 drift

---

## Accomplishments — Esta Sessão (7 commits)

| # | Commit | O que foi feito |
|---|--------|-----------------|
| 1 | `a524a44` | Guard Brasil REST API (`apps/api/src/server.ts`) + MCP Server |
| 2 | `dcc6bb5` | Diretiva renovada: GTM chain P0 |
| 3 | `c761380` | **API deployed no Hetzner** + `deploy.sh` + `docker-compose.prod.yml` |
| 4 | `54380ec` | HARVEST.md v2.2.0 — Docker, Caddy, rename patterns |
| 5 | `a52971e` | MANUAL_ACTIONS.md + GitHub Actions `publish-npm.yml` + outreach kit |
| 6 | `48849cb` | TASKS.md EGOS-123–130 atualizados |
| 7 | `f667b76` | /end handoff + CAPABILITY_REGISTRY v1.5.0 + HARVEST v2.3.0 |

### Arquivos criados
- `apps/api/docker-compose.prod.yml` — config produção
- `apps/api/deploy.sh` — 1-comando deploy
- `.github/workflows/publish-npm.yml` — auto-publish npm no tag
- `MANUAL_ACTIONS.md` — sistema de rastreio de bloqueios (wired no /start)
- `docs/strategy/GUARD_BRASIL_1PAGER.md` — 1-pager PT-BR govtech
- `docs/strategy/GUARD_BRASIL_DEMO_SCRIPT.md` — demo 30min com FAQ
- `docs/strategy/OUTREACH_EMAILS.md` — 3 templates + 20 targets
- `br-acc/scripts/rename-to-egos-inteligencia.sh` — rename 5-fases
- `br-acc/scripts/rename-phase1-docs.sh` — Phase 1 executada (47 docs)

---

## Em Progresso

| Task | % | Próximo passo |
|------|---|---------------|
| EGOS-123: npm publish | 90% | `npm login` + `npm publish` (M-001) |
| EGOS-124: API pública | 95% | DNS A record (M-002) — 2 min |
| EGOS-128: rename Python | 0% | `bash scripts/rename-to-egos-inteligencia.sh --execute` (M-003) |
| EGOS-130: Guard Brasil no ETL | 0% | Dep: M-002 + M-003 |

---

## Bloqueado — MANUAL_ACTIONS

Ver [`MANUAL_ACTIONS.md`](../../MANUAL_ACTIONS.md) para passo a passo completo.

| ID | Bloqueia | Ação | Tempo |
|----|----------|------|-------|
| **M-001** 🔴 | npm package público | `cd packages/guard-brasil && npm login && npm publish --access public` | 5 min |
| **M-002** 🔴 | API demo e outreach | DNS A `guard → 204.168.217.125` no painel de `egos.ia.br` | 2 min |
| **M-003** 🟡 | Python imports renomeados | `bash /home/enio/br-acc/scripts/rename-to-egos-inteligencia.sh --execute` | 15 min |
| **M-005** 🟡 | infra consistente | `ssh hetzner 'docker network rename infra_bracc infra_egos_inteligencia'` | 5 min |
| **M-006** 🟢 | npm auto-publish futuro | `npm token create` → GitHub Secret `NPM_TOKEN` | 5 min |
| **M-007** 🟢 | primeiros clientes | 5+ emails de `docs/strategy/OUTREACH_EMAILS.md` | 2h |

---

## Próximas Tasks (por prioridade)

### P0 — Imediato (manual, <30 min total)
1. **M-001** → `npm login` + `npm publish` (5 min)
2. **M-002** → DNS A no painel `egos.ia.br` (2 min)
3. **M-006** → `npm token create` → GitHub Secret (5 min, logo após M-001)

### P0 — Automático (próxima sessão, após M-002)
4. **EGOS-130** → `etl/src/egos_inteligencia_etl/guard.py` — cliente Python Guard Brasil API

### P1 — Manual (30 min)
5. **M-003** → `bash rename-to-egos-inteligencia.sh --execute` + `git mv bracc_etl`
6. **M-005** → `docker network rename` no Hetzner

### P1 — Automático
7. Audit Dashboard MVP → desbloquearia tier Pro R$499/mês
8. Policy Pack "Segurança Pública" — MASP/REDS rules extras

### P2 — Esta semana
9. **M-007** → 5 emails outreach CTOs govtech
10. Validar `curl https://guard.egos.ia.br/health` após M-002

---

## Ambiente / Build Status

```
TypeScript:    tsc --noEmit     → ✅ 0 erros
Tests:         bun test         → ✅ 15/15 pass (guard-brasil)
Governance:    governance:check → ✅ 0 drift
Gitleaks:      pre-commit scan  → ✅ clean
Guard Brasil:  localhost:3099   → ✅ healthy (4ms)
npm package:   @egos/guard-brasil → ❌ não publicado (aguarda M-001)
DNS:           guard.egos.ia.br  → ❌ sem registro A (aguarda M-002)
```

---

## Arquivos Chave para Próxima Sessão

| Arquivo | Para que serve |
|---------|----------------|
| [`MANUAL_ACTIONS.md`](../../MANUAL_ACTIONS.md) | Bloqueios manuais com passo a passo |
| [`TASKS.md`](../../TASKS.md) — seção GTM | EGOS-123–130 com status real |
| [`apps/api/deploy.sh`](../../apps/api/deploy.sh) | Redeploy da API Guard Brasil |
| [`docs/strategy/OUTREACH_EMAILS.md`](../strategy/OUTREACH_EMAILS.md) | Templates prontos |
| [`docs/strategy/GUARD_BRASIL_DEMO_SCRIPT.md`](../strategy/GUARD_BRASIL_DEMO_SCRIPT.md) | Demo 30min |
| `/home/enio/br-acc/scripts/rename-to-egos-inteligencia.sh` | Rename fases 2-5 |

---

## Burn Rate vs Receita

| | Valor |
|---|---|
| Burn mensal | R$650–1.500+/mês |
| Receita | **R$0** |
| Caminho mais curto | M-001 + M-002 + 1 email → R$99/mês Starter |
| Break-even Starter | 7–15 clientes Starter ou 2–3 Pro |

---

```
SESSION SUMMARY
===============
Repo:          egos (github.com/enioxt/egos)
Branch:        main
Commits:       7 esta sessão
Security:      Clean (gitleaks, 0 secrets)
Tests:         15/15 pass
Build:         tsc OK, 0 erros
Files changed: 15+ arquivos criados/modificados
Infra:         guard-brasil-api LIVE no Hetzner (4ms, healthy)
Rename:        Phase 1 done (47 docs), fases 2-5 aguardam M-003
GTM:           1-pager + demo script + 20 targets + templates prontos
Bloqueios:     M-001 (npm, 5min) + M-002 (DNS, 2min) = API pública

Next P0:       M-001 + M-002 → @egos/guard-brasil no npm + guard.egos.ia.br live
Context:       ~180/280
Signed by:     claude-code/sonnet-4.6 — 2026-03-30T12:50:00Z
```
