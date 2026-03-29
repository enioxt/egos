# LLM Orchestration Matrix — EGOS-080

> **VERSION:** 1.0.0 | **DATE:** 2026-03-29
> **PURPOSE:** Explicit lane ownership, authority levels, and task routing for all LLM providers.
> **SSOT:** `model-router.ts` is the code SSOT. This doc is the governance SSOT.

## Lane Definitions

| Lane | Provider | Models | Authority | Approval | Cost Tier |
|------|----------|--------|-----------|----------|-----------|
| **Alibaba** | DashScope API | qwen-max, qwen-plus, qwen3-coder-plus, qwen-flash | Autonomous | None | Economy–Premium |
| **OpenRouter** | OpenRouter API | Gemini Flash, GPT-4o Mini, Claude Sonnet 4, DeepSeek V3 | Autonomous | None | Economy–Premium |
| **Claude Code** | Anthropic (this session) | Opus 4.6, Sonnet 4.6, Haiku 4.5 | Orchestrator | User-approved | Premium |
| **Codex** | OpenAI terminal | codex | Autonomous (terminal) | None | Economy |
| **Windsurf/Cursor** | IDE-embedded | Cascade/Claude | IDE-controlled | None | IDE plan |
| **Google AI Studio** | Google API | Gemini Pro/Flash | Manual | User-initiated | Free–Premium |

## Task-to-Lane Routing

| Task Type | Primary Lane | Fallback | Rationale |
|-----------|-------------|----------|-----------|
| `orchestration` | Alibaba (qwen-max) | OpenRouter (Claude Sonnet 4) | Complex reasoning, cost-aware |
| `code_generation` | Alibaba (qwen3-coder-plus) | OpenRouter (DeepSeek V3) | Code-specialized models |
| `code_review` | Alibaba (qwen-max) | OpenRouter (Claude Sonnet 4) | Needs deep analysis |
| `analysis` | Alibaba (qwen-plus) | OpenRouter (DeepSeek V3) | Balanced cost/quality |
| `summarization` | Alibaba (qwen-flash) | OpenRouter (Gemini Flash) | Economy tier sufficient |
| `classification` | Alibaba (qwen-flash) | OpenRouter (GPT-4o Mini) | Fast, cheap |
| `chat` | Alibaba (qwen-plus) | OpenRouter (Gemini Flash) | General purpose |
| `translation` | Alibaba (qwen-flash) | OpenRouter (Gemini Flash) | Economy |
| `extraction` | Alibaba (qwen-plus) | OpenRouter (GPT-4o Mini) | Structured output |
| `fast_check` | Alibaba (qwen-flash) | OpenRouter (Gemini Flash) | Speed priority |

## Cost Ceiling Policy

| Tier | Max per call | Monthly budget | Escalation |
|------|-------------|---------------|------------|
| Economy | $0.01 | $10 | None |
| Balanced | $0.10 | $50 | Warn at 80% |
| Premium | $1.00 | $100 | Require approval >$0.50 |

## Cheap-First Principle (EGOS-071)

1. Always try qwen-flash (FREE) first for simple/classification/fast_check tasks
2. Escalate to qwen-plus only when task type requires it
3. Use premium models (qwen-max, Claude Sonnet 4) only for orchestration/code_review
4. Track cost per session in `metrics-tracker.ts`

## SSOT Merge: llm-orchestrator.ts → model-router.ts

`llm-orchestrator.ts` has been **deprecated** (2026-03-29). It contained 4 stale models with a different schema. `model-router.ts` with `resolveModel()` is the canonical code SSOT for all LLM routing decisions.

## Subagent Cost Optimization (Claude Code)

When running as Claude Code Opus:
- Use `model: "haiku"` for quick searches, file reads, code grep
- Use `model: "sonnet"` for medium tasks (writing tests, analysis, documentation)
- Keep Opus for orchestration decisions, architecture, complex governance

## Integration Points

- `resolveModel(task)` → returns best model for task + cost tier
- `chatWithLLM({ model, provider })` → executes the call with cost tracking
- `createTelemetryRecorder()` → logs model, tokens, cost per call
- `MetricsTracker` → aggregates session-level cost data
