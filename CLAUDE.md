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

- **SSOT:** `AGENTS.md`, `TASKS.md`, `agents/registry/agents.json`
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

## 90-Day Focus (April 3 - June 30, 2026)

**ALLOWED:** Guard Brasil API/Web/Infra + Gem Hunter (algorithm, dashboard, API)
**GOAL:** R$ 30k+ MRR
**ENFORCEMENT:** Pre-commit hook blocks commits outside focus scope

---

*Gerado em: 2026-04-04 | Claude Code v2.3.0*
