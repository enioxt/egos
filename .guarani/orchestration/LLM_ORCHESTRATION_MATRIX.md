# LLM Orchestration Matrix — EGOS-080

> **Version:** 1.0.0 | **Created:** 2026-03-30
> **SSOT:** `packages/shared/src/llm-router.ts` (routing formula)
> **Applies to:** All AI calls within the EGOS ecosystem

---

## Lane Definitions

| Lane | Authority | Owns | Approval Mode | Cost Tier |
|------|-----------|------|---------------|-----------|
| `planner` | Architect | Multi-step reasoning, architecture decisions, complex analysis | confirm | $$$  (gpt-5.4, ~$0.0025/1k) |
| `executor` | Implementer | Code generation, structured JSON output, high-precision tasks | auto | $$  (claude-sonnet, ~$0.003/1k) |
| `cheap` | Bulk runner | Classification, PII detection, summarization, high-volume calls | auto | $  (qwen-turbo, gemini-flash, ~$0.0001/1k) |
| `sovereign` | BR-compliance | Any task requiring data sovereignty or offline-capable routing | confirm | $  (qwen-plus via DashScope, ~$0.0004/1k) |

---

## Orchestrator Ownership

### Claude Code (this session — terminal)
- **Authority:** Executor + Planner for kernel tasks
- **Allowed:** Architecture decisions, new files, governance changes, agent wiring, SSOT edits
- **Approval mode:** auto for code writes; confirm for frozen zone edits
- **Model used:** claude-sonnet-4-6 (hardcoded — this IS the orchestrator, not a routed call)
- **Do NOT route through llm-router.ts** — Claude Code is the router consumer, not a consumer target

### Codex (background, async)
- **Authority:** Executor
- **Allowed:** Code generation from specs, test writing, refactoring scoped tasks
- **Approval mode:** confirm (never runs autonomously on kernel files without human ACK)
- **Model used:** routeTask('code_generation', { preferLane: 'executor' })
- **Conflict rule:** If Claude Code session is active on same task → Codex defers

### Windsurf / Cascade
- **Authority:** Executor (IDE-bound)
- **Allowed:** UI/component work, file edits within one repo, local test runs
- **Approval mode:** auto for leaf repos; confirm for kernel (egos/)
- **Model used:** Cascade internal (not routed through llm-router.ts)
- **Conflict rule:** NEVER run Cascade and Claude Code on the same task simultaneously
  - Active session → check `.guarani/worktrees.json` for lock before starting

### Alibaba DashScope (sovereign lane)
- **Authority:** Cheap + Sovereign
- **Allowed:** PII classification, bias analysis, high-volume Guard Brasil API calls
- **Models:** qwen-plus (sovereign), qwen-turbo (cheap)
- **Approval mode:** auto
- **Route via:** `routeTask(taskType, { preferLane: 'sovereign' })` or `routeGuardBrasil()`
- **Use when:** Data cannot leave BR jurisdiction, or cost > R$0.50 per 1k calls

### OpenRouter (aggregator)
- **Authority:** Planner + Executor
- **Allowed:** Any task not requiring sovereignty; fallback when DashScope is down
- **Models:** claude-sonnet (executor), gpt-5.4 (planner), gemini-flash (cheap)
- **Approval mode:** auto
- **Route via:** `routeTask(taskType)` — default path when no lane preference given
- **Cost guard:** never use planner lane for bulk/classification tasks

---

## When to Use llm-router.ts vs Hardcode

### Use `routeTask()` (llm-router.ts)
- Agent code making API calls at runtime
- Guard Brasil API (PRI layer, bias analysis, classification)
- Any task type from the `TaskType` union
- When cost optimization matters (>100 calls/day)

### Hardcode the model
- Claude Code session = always claude-sonnet-4-6 (this process IS the model)
- Cascade = always Cascade internal (not in registry)
- One-off scripts where exact reproducibility matters more than cost
- Emergency runbook steps (use the specific model that was tested)

---

## Routing Decision Flow

```
New AI call needed?
  ├─ Is this Claude Code session itself? → No route. You ARE the model.
  ├─ Does task require BR data sovereignty? → routeTask(type, { preferLane: 'sovereign' })
  ├─ Is it Guard Brasil API? → routeGuardBrasil(type)
  ├─ Is it complex_reasoning or architecture? → routeTask(type, { preferLane: 'planner' })
  ├─ Is it code_generation or structured_output? → routeTask(type, { preferLane: 'executor' })
  └─ Default → routeTask(type) — formula picks best
```

---

## Emergency Fallback Chain

When a model is down or quota-exhausted, the router builds `fallbackChain` automatically (different providers preferred). Manual override:

```
1. qwen-plus (DashScope) — always available, sovereign
2. gemini-flash (OpenRouter) — cheapest, high quota
3. claude-sonnet (OpenRouter) — most capable, use last (cost)
```

If ALL providers are down: return cached result if <1h old, else surface `503 / DEFER` via PRI gate.

---

## Conflict Resolution

| Scenario | Rule |
|----------|------|
| Claude Code + Cascade on same file | Claude Code wins. Cascade must exit worktree first. |
| Codex + Cascade on same task | Check worktrees.json lock. First writer wins. |
| Two agents hit same model quota | Router auto-demotes to next lane. Log in `cost_usd` field. |
| DashScope + OpenRouter both available | Prefer DashScope for sovereign tasks; OpenRouter for speed. |
| Planner lane hit for bulk task (>50 calls) | Block. Force reclassify as cheap/executor. Cost gate in agent checklist. |

---

## Escalation Rules

| Trigger | Escalate to |
|---------|-------------|
| Task requires frozen zone edit | Human confirm required. Claude Code cannot self-approve. |
| Cost projection >$5 for single task | Stop. Log. Show projection. Await human ACK. |
| Model returns confidence <60% on PII | PRI gate: DEFER → human review queue |
| Two orchestrators claim same worktree | Lock wins. Challenger logs conflict in TASKS.md and waits. |

---

## References

- Routing formula: `packages/shared/src/llm-router.ts` — `routeTask()`, `routeGuardBrasil()`
- Model registry: `DEFAULT_MODELS` in llm-router.ts (qwen-plus, qwen-turbo, gemini-flash, claude-sonnet, gpt-5.4)
- PRI safety gate: `packages/core/src/guards/pri.ts`
- Worktree locks: `.guarani/worktrees.json`
- Domain rules: `.guarani/orchestration/DOMAIN_RULES.md` §2
