# Handoff 2026-04-03 — Session P17 Complete

> **Agent:** cascade  
> **Session:** P17 — Agent Registry Ghost Cleanup + SSOT Validation Layer  
> **Context:** 183/280 HIGH → /end triggered  
> **Duration:** ~2h  

---

## Accomplished

### 1. Agent Ghost Investigation & Fix (P0)

**Problem:** `drift-sentinel` reported 4 ghost agents, but reality was different.

**Investigation:**

| Agente | Status Real | Entrypoint | Ação |
|--------|-------------|------------|------|
| aiox-gem-hunter | [KILLED 2026-03-31] | morto | ✅ Removido do registry |
| mastra-gem-hunter | [KILLED 2026-03-31] | morto | ✅ Removido do registry |
| kol-discovery | ✅ VIVO | `scripts/kol-discovery.ts` | ✅ Falso positivo |
| gem-hunter-api | ✅ VIVO | `agents/api/gem-hunter-server.ts` | ✅ Falso positivo |

**Root Cause:** `drift-sentinel.ts` only checked `agents/agents/*.ts`, ignoring `scripts/` and `agents/api/` entrypoints.

**Fixes Applied:**
- `agents/registry/agents.json` — Removed 2 dead agents
- `agents/agents/drift-sentinel.ts` — Refactored to check any entrypoint path
- `agents/agents/agent-validator.ts` — NEW validation agent
- `agents/registry/validation.json` — NEW validation cache
- `agents/registry/VALIDATION.md` — NEW documentation

**Result:** `bun agent:run drift-sentinel --dry` → **0 drifts** ✅

### 2. SSOT Validation Hierarchy (P0)

**Created 3-layer ground truth system:**

| Layer | File | Purpose |
|-------|------|---------|
| Definition | `agents.json` | SSOT of what SHOULD exist |
| Verification | `validation.json` | SSOT of what WAS CONFIRMED to exist |
| Detection | `drift-sentinel` | Drift alerts (may have false positives) |

**Validation Agent:**
```bash
bun agents/agents/agent-validator.ts --check  # Cache fresh? (< 24h)
bun agents/agents/agent-validator.ts --exec   # Re-validate + write
bun agents/agents/agent-validator.ts --dry    # Preview
```

**Stats:** 16 agents, 14 alive, 2 dead (intentional), 0 ghosts ✅

### 3. Governance Updates (P0)

**Files Modified:**
- `.windsurfrules` — Added Rule 13: AGENT VALIDATION
- `.windsurf/workflows/start.md` — SSOT hierarchy + 4-Point Check
- `docs/knowledge/HARVEST.md` — AI Agent Validation Checklist Pattern
- `docs/knowledge/SSOT_VALIDATION_PATTERN.md` — NEW pattern doc
- `TASKS.md` — Added EGOS-176 (Agent registry cleanup)

### 4. Hermes-3 Status Check (P1)

| Fase | Status |
|------|--------|
| Configurado em llm-provider.ts | ✅ |
| Wired como BRAID executor | ⏳ Pendente (HERMES-001) |
| Capability Registry | ✅ A |

**Task HERMES-001:** Wire Hermes-3 as BRAID mechanical executor (OpenRouter free tier, 2h, 30-40% cost savings) — P1 em aberto.

### 5. Codex via Cline Investigation (Info)

**Verdict:** Não automatizável. OAuth browser-only na extensão VS Code. Para usar Codex no EGOS, precisaria de API Key da OpenAI (billing separado), não subscription ChatGPT.

---

## Environment State

| Check | Status |
|-------|--------|
| TypeScript | ✅ Limpo |
| Tests | ✅ 32 pass (guard-brasil) |
| Drift Sentinel | ✅ 0 drifts |
| Validation Cache | ✅ Fresh (< 24h) |
| Context Tracker | 🔴 183/280 HIGH |

**Uncommitted Files:** ~35 (incluindo validation.json, agent-validator.ts, handoffs)
**Commits This Session:** 0 (aguardando confirmação)

---

## Next Steps (P0)

1. **Commit changes:**
   ```bash
   git add agents/registry/validation.json
   git add agents/agents/agent-validator.ts
   git add agents/registry/VALIDATION.md
   git add docs/knowledge/SSOT_VALIDATION_PATTERN.md
   git add docs/_current_handoffs/handoff_2026-04-03*.md
   # etc...
   ```

2. **Governance sync:**
   ```bash
   bun run governance:sync:exec
   bun run governance:check  # Should be 0 drift
   ```

3. **Validation:**
   ```bash
   bun agents/agents/agent-validator.ts --check  # Should exit 0
   bun agent:run drift-sentinel --dry  # Should show 0 drifts
   ```

---

## Key Decisions

1. **Manter kol-discovery/gem-hunter-api no registry?** ✅ SIM — entrypoints válidos em paths não-padrão
2. **Remover agentes KILLED?** ✅ SIM — aiox-gem-hunter e mastra-gem-hunter removidos
3. **Criar validation.json?** ✅ SIM — cache leve de verificação, não atualiza automaticamente
4. **Atualizar /start workflow?** ✅ SIM — SSOT hierarchy obrigatório
5. **Wire Hermes-3 agora?** ⏳ NÃO — ficou como HERMES-001 P1

---

## Patterns Created

1. **AI Agent Validation Checklist** (HARVEST.md) — 4-Point Check para evitar falsos positivos
2. **SSOT Validation Hierarchy** (SSOT_VALIDATION_PATTERN.md) — 3 camadas de ground truth

---

## Meta-Prompts Used

- `audit.ecosystem` — Ghost agent investigation
- `systems.mycelium` — Drift fix + validation layer

---

*Signed: cascade-agent — 2026-04-03T12:45:00Z*
