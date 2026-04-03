# Handoff 2026-04-03 — Agent Registry Ghost Cleanup

> **Session:** P17 — EGOS Framework Core  
> **Agent:** cascade  
> **Context:** CTX 183/280 🔴 HIGH — /end triggered

---

## Accomplished

### 1. Agent Registry Ghost Investigation (P0)

**Problema:** `drift-sentinel` reportava 4 drifts falsos.

**Investigação:**

| Agente | Status Real | Entrypoint | Ação |
|--------|-------------|------------|------|
| aiox-gem-hunter | [KILLED 2026-03-31] | morto | ✅ Removido do registry |
| mastra-gem-hunter | [KILLED 2026-03-31] | morto | ✅ Removido do registry |
| kol-discovery | ✅ VIVO | `scripts/kol-discovery.ts` | ✅ Falso positivo |
| gem-hunter-api | ✅ VIVO | `agents/api/gem-hunter-server.ts` | ✅ Falso positivo |

**Root Cause:** `drift-sentinel.ts` só verificava `agents/agents/*.ts`.

**Fix:**
- `agents/registry/agents.json` — Removidos 2 agentes mortos
- `agents/agents/drift-sentinel.ts` — Agora verifica `entrypoint` em qualquer path

**Resultado:** `bun agent:run drift-sentinel --dry` → **0 drifts** ✅

### 2. LLM Provider — Docs Atualizadas

- Claude Code: **Opus + Sonnet + Haiku** (ilimitados)
- Alibaba: Fallback prioritário (esgotar todos 8 modelos)
- OpenRouter: Último fallback (sem Claude)

### 3. Codex via Cline

**Veredito:** Não automatizável. Usa OAuth browser-only. Precisaria de API Key separada.

---

## Files Changed

- `agents/registry/agents.json`
- `agents/agents/drift-sentinel.ts`
- `packages/shared/src/llm-provider.ts`
- `packages/shared/src/index.ts`
- `docs/knowledge/HARVEST.md`
- `TASKS.md`

---

## Next Steps

1. Commit 30 arquivos modificados
2. `bun run governance:sync:exec`
3. `bun run governance:check` = 0 drift

---

*Signed: cascade — 2026-04-03*
