# Handoff — 2026-03-30 — Guard Brasil GTM + Rename Phase 1

> **Sessão encerrada por:** Claude Code (Sonnet 4.6)
> **Próxima sessão começa aqui.**

---

## Estado do Sistema Agora

### Infraestrutura Hetzner (204.168.217.125)
```
guard-brasil-api   Up, healthy, porta 3099, restart: unless-stopped
852-app            Up, healthy
bracc-neo4j        Up, healthy
infra-caddy-1      Up, TLS automático
evolution-api      Up
waha-santiago      Up
```
- Cron watchdog: `*/5 * * * *` — restart automático se guard-brasil-api cair
- API key: `/opt/apps/guard-brasil/.env` no servidor
- Redeploy: `bash /home/enio/egos/apps/api/deploy.sh`

### Guard Brasil API
- **Container live** no Hetzner, porta 3099, healthy
- **DNS PENDENTE** — `guard.egos.ia.br` não tem registro A ainda → API inacessível publicamente
- Teste interno: `ssh hetzner 'curl -sf http://localhost:3099/health'` → OK
- Teste público (após DNS): `curl https://guard.egos.ia.br/health`

### EGOS-Inteligencia (ex-br-acc)
- GitHub repo: `enioxt/EGOS-Inteligencia` (já renomeado)
- Rename Phase 1 ✅ — 47 docs atualizados, commitado
- Rename Phases 2-5 ❌ — pendente (Python imports, Docker configs, shell scripts)
- Script pronto: `bash /home/enio/br-acc/scripts/rename-to-egos-inteligencia.sh --execute`

---

## MANUAL_ACTIONS — Ler Antes de Tudo

Arquivo: `MANUAL_ACTIONS.md` na raiz do repo.
**Wired no /start INTAKE — agente vai reportar isso automaticamente.**

Itens ativos:
| ID | Ação | Tempo | Prioridade |
|---|---|---|---|
| M-001 | npm login + npm publish @egos/guard-brasil | 5 min | 🔴 |
| M-002 | DNS A: guard → 204.168.217.125 | 2 min | 🔴 |
| M-003 | rename fases 2-5 em br-acc | 15 min | 🟡 |
| M-005 | docker network rename no Hetzner | 5 min | 🟡 |
| M-006 | NPM_TOKEN no GitHub Secrets | 5 min | 🟢 |
| M-007 | Outreach 20 CTOs govtech | 2h | 🟢 |

---

## O Que Foi Feito Nesta Sessão

### Código e Infraestrutura
- `apps/api/docker-compose.prod.yml` — config de produção para guard-brasil-api
- `apps/api/deploy.sh` — script rsync + build + Caddy + healthcheck em 1 comando
- `.github/workflows/publish-npm.yml` — auto-publish npm no tag `guard-brasil/v*`
- `MANUAL_ACTIONS.md` — sistema de rastreio de bloqueios manuais (wired no /start)

### EGOS-Inteligencia (rename)
- `scripts/rename-to-egos-inteligencia.sh` — script 5-fases, dry-run safe
- `scripts/rename-phase1-docs.sh` — executor Phase 1 isolado
- Phase 1 executada: 47 arquivos docs renomeados e pushados

### GTM / Vendas
- `docs/strategy/GUARD_BRASIL_1PAGER.md` — 1-pager PT-BR para CTOs govtech
- `docs/strategy/GUARD_BRASIL_DEMO_SCRIPT.md` — demo 30min com FAQ
- `docs/strategy/OUTREACH_EMAILS.md` — 3 templates + 20 targets governamentais

### Governance
- `HARVEST.md` v2.3.0 — padrões Docker deploy, Caddy, rename script, MANUAL_ACTIONS
- `CAPABILITY_REGISTRY.md` v1.5.0 — Guard Brasil REST API, MCP Server, MANUAL_ACTIONS Tracker
- `.agents/workflows/start-workflow.md` — MANUAL_ACTIONS.md obrigatório no INTAKE

---

## Próximas Tasks por Prioridade

### P0 — Bloqueio de Receita (MANUAL)
1. **M-001:** `cd packages/guard-brasil && npm login && npm publish --access public`
2. **M-002:** Adicionar registro A `guard → 204.168.217.125` no painel DNS de `egos.ia.br`

### P0 — Automático (próxima sessão)
3. **EGOS-130:** Criar `etl/src/egos_inteligencia_etl/guard.py` — cliente Python para Guard Brasil API
   - Dep: M-002 (DNS ativo) + M-003 (rename Python)

### P1 — Manual
4. **M-003:** `bash /home/enio/br-acc/scripts/rename-to-egos-inteligencia.sh --execute`
5. **M-005:** `docker network rename infra_bracc infra_egos_inteligencia` no Hetzner

### P1 — Automático
6. **EGOS-130:** Wire Guard Brasil no pipeline ETL do egos-inteligencia
7. **Audit Dashboard MVP:** Desbloquearia tier Pro R$499/mo

### P2
8. **M-006:** NPM_TOKEN no GitHub Secrets (após M-001)
9. **M-007:** 5 emails outreach CTOs esta semana

---

## Arquivos Chave para a Próxima Sessão

| Arquivo | Para que serve |
|---|---|
| `MANUAL_ACTIONS.md` | Estado atual dos bloqueios manuais |
| `TASKS.md` → seção "Guard Brasil GTM" | EGOS-123 a 130 com status atual |
| `apps/api/deploy.sh` | Redeploy da API |
| `docs/strategy/GUARD_BRASIL_DEMO_SCRIPT.md` | Script de demo para clientes |
| `docs/strategy/OUTREACH_EMAILS.md` | Templates prontos para envio |
| `/home/enio/br-acc/scripts/rename-to-egos-inteligencia.sh` | Rename fases 2-5 |

---

## Validações Rápidas para Começar Próxima Sessão

```bash
# 1. API guard-brasil no Hetzner
ssh -i ~/.ssh/hetzner_ed25519 root@204.168.217.125 'curl -sf http://localhost:3099/health'
# esperado: {"status":"healthy"}

# 2. DNS guard.egos.ia.br (após M-002)
curl https://guard.egos.ia.br/health
# esperado: {"status":"healthy"}

# 3. npm package publicado (após M-001)
npm info @egos/guard-brasil
# esperado: version: 0.1.0

# 4. Estado rename egos-inteligencia
cd /home/enio/br-acc && git log --oneline -3
# deve mostrar: feat(rename): Phase 1 — rename br-acc → egos-inteligencia in all docs
```

---

## Burn Rate vs Receita

- **Burn:** R$650-1.500+/mês (Hetzner + Vercel + APIs)
- **Receita:** R$0/mês
- **Caminho mais curto para R$1:** M-001 + M-002 + M-007 (5 emails) = R$99/mês Starter

---

*Handoff gerado em: 2026-03-30 | Claude Code Sonnet 4.6*
*Próxima ação obrigatória: ler `MANUAL_ACTIONS.md` antes de qualquer planejamento*
