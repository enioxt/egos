# CLAUDE.md — EGOS Kernel Context

> **Project:** EGOS Framework Core  
> **Type:** Orchestration Kernel + Agent Runtime  
> **Runtime:** Bun / TypeScript / Ubuntu  
> **Repo:** /home/enio/egos

---

## Quick Context

EGOS é um kernel de orquestração para agents de IA governados. O repositório contém:

- `agents/` — Runtime de agentes (runner.ts, event-bus.ts — FROZEN)
- `packages/` — Módulos compartilhados (shared, search-engine, atomizer, core, audit)
- `apps/` — Aplicações (api/, guard-brasil-web/, commons/)
- `integrations/` — Adaptadores (contracts, manifests, distribution)
- `.guarani/` — Governança (orchestration/, prompts/, philosophy/)

## Cross-Repo Context (16 repos, pull-based)

Quando precisar de contexto de outros repos, consulte `docs/CROSS_REPO_CONTEXT_ROUTER.md` — índice topic→repo→file. NÃO carregue tudo de uma vez. Puxe pelo fio quando o tópico surgir.

Repos-chave fora do kernel:
- **egos-inteligencia** (`/home/enio/egos-inteligencia`) — entity extraction, Neo4j 83.7M, NER PT-BR, cross-reference engine, investigation templates
- **br-acc** (`/home/enio/br-acc`) — Neo4j graph source, FastAPI, OSINT
- **852** (`/home/enio/852`) — chatbot público, 72 API routes, tool-calling
- **forja** (`/home/enio/forja`) — ERP industrial, WhatsApp
- **carteira-livre** (`/home/enio/carteira-livre`) — marketplace, 254+ routes

---

## Comandos Essenciais

```bash
# Type check
bun typecheck

# Lint agents
bun agent:lint

# Governance
bun run governance:check      # Verificar drift
bun run governance:sync:exec  # Sincronizar

# Tests
bun test

# Task management
bun agent:run context_tracker --dry  # CTX score
```

---

## Arquitetura

- **Governance canon:** `.guarani/RULES_INDEX.md` → `.guarani/PREFERENCES.md` → `.guarani/orchestration/*`
- **Repo SSOT:** `AGENTS.md`, `TASKS.md`, `agents/registry/agents.json`
- **Adapter rule:** `CLAUDE.md` is an environment adapter; if it conflicts with `.guarani`, `.guarani` wins
- **Frozen Zones:** `agents/runtime/runner.ts`, `agents/runtime/event-bus.ts`, `.husky/pre-commit`, `.guarani/orchestration/PIPELINE.md`
- **Shared:** `packages/shared/src/` — código reutilizável
- **Integrações:** MCP servers ativos na sessão

---

## Convenções

- **Commits:** Conventional commits, a cada 30-60min
- **TypeScript:** Estrito, zero any implícito
- **Testes:** `bun test` coverage obrigatória
- **DRY-RUN:** Todo agent deve suportar `--dry` antes de `--exec`
- **Edit Size:** Máximo 80 linhas por operação de escrita
- **Rollout rule:** toda task MODERATE+ de produto/deploy deve explicitar dependências, ordem exata e gates `deploy`, `security`, `ux`, `launch` antes de implementar

---

## Integrações Ativas

- Guard Brasil API: https://guard.egos.ia.br
- Supabase: MCP server disponível
- Bun: v1.x
- Git: commits assinados quando possível

---

## Guard Brasil Context

- Package: `@egosbr/guard-brasil`
- API: `/v1/inspect`, `/v1/meta`
- Capabilities: PII detection, LGPD compliance, ATRiAN validation
- Preço: Usage-based tiers (Free → Starter → Pro → Business → Enterprise)

---

## User Preferences

- Não usa autocomplete
- Foco em resultados, não em código
- Prefere terminal/agentic workflow
- Ubuntu/Linux nativo
- **Autonomia máxima**: nunca parar para pedir permissão — agir e reportar
- **Challenge mode**: cobrar P0s atrasados, empurrar de volta scope creep, ser direto sobre qualidade
- **Disseminate everything**: regras devem propagar para todos os locais simultaneamente

---

## SINGLE PURSUIT (2026-04-12 → 2026-05-12)

**SPRINT:** Validação de Campo — Delegacia + Lídia
**META 30d:** Lídia entende 80% do sistema. 1 processo real melhorado com IA.
**MODELO:** Consultoria de implementação (A) + Framework licenciável (C, depois)
**PRINCIPIO:** "Foco compoem. Dispersao dissipa." (Rian Doris)
**COMPLEXIDADE:** Entregar no nivel que o campo exige, nao no nivel que a plataforma permite.

REGRAS:
1. Prioridade = validar com a Lidia, aprender do campo, entregar o minimo util
2. Guard Brasil = ferramenta no toolkit, nao o produto central
3. Kernel complexo fica por baixo. So sobe complexidade se o campo exigir.
4. Abstracao so depois da terceira repeticao (Karpathy)
5. ZERO features novas em: 852, forja, egos-inteligencia, arch, egos-lab
6. Gem Hunter = hobby (MAX 2h/semana, sexta-feira)
7. Sessao comeca com: "O que avanca a validacao com a Lidia hoje?"
8. Sessao termina com: "Aprendemos algo novo sobre o campo hoje?"
9. Discussao e iteracao ANTES de executar (nao rushar)
10. ENFORCEMENT: hook v4.0 — sprint delegacia patterns em clean pass

## GTM-First Rule (2026-04-11, updated)

Every feature must answer: **"Who uses this? How do they find it?"**
- Revenue: R$0 (as of 2026-04-11) — #1 priority is FIRST PAYING CUSTOMER
- Customers: 0 paying — outreach + demos are the critical path
- X.com: Post demos, respond to LGPD conversations, showcase Guard Brasil
- /end must ask: "Did you advance Guard Brasil GTM today?"
- Dispersal check: "What % of this session was Guard Brasil?"

## Git Push Protocol (INC-001 — 2026-04-06)

**Hard rule:** never `git push --force` to `main`. Always use `bash scripts/safe-push.sh main`. See `docs/INCIDENTS/INC-001-force-push.md` and `~/.claude/CLAUDE.md` §25.

Layered protection:
- `.husky/pre-push` — local non-FF block
- GitHub branch protection — server-side `allow_force_pushes=false`
- `.github/workflows/push-audit.yml` — audit + alert on any forced push
- `scripts/safe-push.sh` — fetch+rebase wrapper for all automation
- `gem-hunter-adaptive.yml` — uses retry+rebase loop, no plain push

If you need to bypass: `EGOS_ALLOW_FORCE_PUSH=1 bash scripts/safe-push.sh main`. Never set this in CI or scheduled jobs.

---

*Gerado em: 2026-04-06 | Claude Code v2.6.0 — INC-001 hardening*

## SSOT-First Rule (P28 — 2026-04-06)

Cada domínio tem UM arquivo SSOT. Antes de criar documentação nova, verificar:

| Domínio | SSOT | Proibido criar |
|---------|------|---------------|
| GTM / social / outreach / equity | `docs/GTM_SSOT.md` | `docs/business/PART*.md`, `docs/sales/*` |
| OpenClaw | `docs/OPENCLAW_SSOT.md` | outros arquivos de config OpenClaw |
| Tasks | `TASKS.md` | tasks avulsas em outros arquivos |
| Capabilities | `docs/CAPABILITY_REGISTRY.md` | listas de capabilities dispersas |
| Learnings técnicos | `docs/knowledge/HARVEST.md` | notes/findings avulsos |

**Regra:** conteúdo novo vai para o SSOT do domínio. Nunca cria arquivo novo se SSOT existe.

---

## MULTI-IDE SYNC + TASKS.md PROTOCOL (2026-04-08)

**`.windsurfrules` é o SSOT canônico de regras de projeto. Este `CLAUDE.md` é um adapter.**
Quando houver conflito entre os dois, `.windsurfrules` prevalece para regras de projeto.
Regras globais de usuário vivem em `~/.claude/CLAUDE.md`.

### TASKS.md — Protocolo anti-perda (OBRIGATÓRIO)
1. **Commitar TASKS.md imediatamente** após qualquer edição. Nunca deixar staged ou só no working tree.
2. **Antes de spawnar agentes background**: `git add TASKS.md && git commit` primeiro.
3. **Agentes background DEVEM usar** `git add <arquivo-específico>` — nunca `git add -A`.
4. **Em ambiente multi-janela** (Claude Code + Windsurf simultâneos): `git pull --rebase` antes de editar TASKS.md, commitar em <2 minutos.

### Sync obrigatório quando mudar limites numéricos
Qualquer mudança de limite (linhas TASKS.md, AGENTS.md, etc.) deve atualizar SIMULTANEAMENTE:
- `.windsurfrules` (linha da tabela SSOT)
- `.husky/pre-commit` (enforcement numérico)
- `CLAUDE.md` (esta seção)

### Limite atual (2026-04-08, revisado)
| Arquivo | Hard limit | Warn em | Ação |
|---------|-----------|---------|------|
| TASKS.md | nenhum (append-only) | 900 | `bun scripts/tasks-archive.ts` (move seções [x] → TASKS_ARCHIVE.md) |
| AGENTS.md | 200 linhas | — | compressão manual |
| .windsurfrules | 200 linhas | — | compressão manual |

## TASKS.MD ANTI-HALLUCINATION (INC-003 — 2026-04-08)

**Rule:** Before adding any task, verify artifact doesn't exist. After implementing, mark `[x]` in same commit.

```bash
# Pre-add check:
find /home/enio/egos -name "*keyword*" 2>/dev/null | grep -v node_modules
grep -i "keyword" TASKS.md | head -5
git log --oneline --since="30 days ago" | grep -i "keyword"

# Post-implement (same commit):
grep -n "related keyword" TASKS.md  # find + mark [x]
```

**Duplicate prevention:** `grep -i "description" TASKS.md` before creating new ID. Update existing, never duplicate.
**Checklist rule:** Spot-check top 5 P0/P1 tasks with `ls`/`grep` before presenting as pending.
