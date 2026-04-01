# AI Coverage Map — EGOS Ecosystem

> **VERSION:** 1.0.0 | **STATUS:** Canonical | **Updated:** 2026-04-01
> **Purpose:** Single source of truth for AI/LLM usage across all EGOS repos.
> **Auto-update:** `bun scripts/ai-coverage-scan.ts --update` (or fires on pre-commit via hook)

<!-- llmrefs:start -->

## LLM Reference Signature

- **Role:** Inventory of all AI/LLM dependencies and costs across ecosystem
- **Summary:** Maps which models (Claude, Qwen, Gemini) are used in each repo/file. Tracks estimated costs and active status. Auto-synced via `ai-coverage-scan.ts`.
- **Read next:**
  - `CAPABILITY_REGISTRY.md` — AI-related capabilities and their status
  - `docs/modules/CHATBOT_SSOT.md` — model selection rules
  - `ENVIRONMENT_REGISTRY.md` — approved providers and hosts

<!-- llmrefs:end -->

---

## Coverage Summary

| Repo | AI Files | Models Used | Est. Cost/mo | Status |
|------|----------|-------------|--------------|--------|
| `egos/packages/shared` | 5 | Claude Sonnet, Qwen Plus/Max/Flash, Gemini Flash | library (N/A) | ✅ Active |
| `egos-lab/eagle-eye` | 6 | Gemini 2.0 Flash | ~$3–5 USD | ✅ Active |
| `egos-lab/agents` | 5 | Qwen Plus, Gemini Flash | ~TBD | ✅ Active |
| `852` | 10 | Qwen Plus/Max, Gemini Flash, GPT-4o-mini | ~$5–15 USD | ✅ Active |
| `forja` | 4 | Qwen Plus, Gemini 2.0 Flash | ~$2–5 USD | ✅ Active |
| `br-acc` | 3 | Gemini 2.0 Flash, GPT-4o-mini | ~$8–12 USD | ✅ Active |
| `carteira-livre` | 0 | — | $0 | ⬜ None |
| `santiago` | 0 | — | $0 | ⬜ None |
| `smartbuscas` | 0 | — | $0 | ⬜ None |

**Total ecosystem AI files:** ~33 | **Est. total cost/mo:** ~$20–40 USD

---

## Provider Hierarchy

```
Primary Gateway: OpenRouter
  └─ Default cheap: google/gemini-2.0-flash-001 (~$0.00015/1K output)
  └─ Balanced: qwen-plus via DashScope ($0.0008/1K input)

Secondary: Alibaba DashScope (Brazil-compliant sovereign)
  └─ qwen-flash (free tier, 1M tokens/model 90-day quota)
  └─ qwen-plus ($0.0008/1K input)
  └─ qwen-max ($0.0016/1K input)
  └─ qwq-plus (deep reasoning, ~$0.003/1K input)

Fallback: OpenAI (emergency only)
  └─ gpt-4o-mini ($0.00015/1K input)
```

**Rate limit fallback chain** (defined in `packages/shared/src/llm-provider.ts`):
```
fast tier:    qwen-flash → gemini-2.0-flash-001 → gpt-4o-mini
default tier: qwen-plus → qwen-max → claude-sonnet-4-6
deep tier:    qwen-max → qwq-plus → claude-sonnet-4-6
```

---

## Repo Details

### egos / packages/shared

Core AI infrastructure — all repos inherit from this.

| File | Function | Model(s) | Max Tokens | Notes |
|------|----------|----------|------------|-------|
| `src/llm-provider.ts` | `chatWithLLM()` | Multi-model (tier-based) | 200K ctx | Canonical fallback chain |
| `src/llm-router.ts` | `routeTask()` | Claude, Qwen, Gemini | 8K–200K | Task-type routing |
| `src/model-router.ts` | `resolveModel()` | 8 models registered | 32K–200K | Model registry |
| `src/llm-orchestrator.ts` | `executeTask()` | Qwen Plus, Gemini Flash | 8K–32K | Agent coordination |
| `src/social/ai-engine.ts` | Social generation | Router-based | 8K | X/social content |

**Coverage notes:** DashScope endpoint `dashscope-intl.aliyuncs.com` (Singapore). `isRateLimitError()` detects 429/503 for automatic fallback.

---

### egos-lab / eagle-eye

Gazette intelligence — analyzes Brazilian Diários Oficiais for procurement opportunities.

| File | Function | Model(s) | Max Tokens | Temp | Cost/call |
|------|----------|----------|------------|------|-----------|
| `src/analyze_gazette.ts` | `analyzeGazette()` | google/gemini-2.0-flash-001 | 2,500 | 0.2 | ~$0.0003 |
| `src/lib/shared.ts` | `chatWithLLM()` | Gemini 2.0 Flash | 2,000 | 0.3 | ~$0.0002 |
| `src/analyze_viability.ts` | `analyzeOpportunity()` | Gemini 2.0 Flash | 4,000 | 0.4 | ~$0.0005 |
| `src/intelligence-reports.ts` | `generateIntelligenceReport()` | Gemini 2.0 Flash | 1,500 | 0.3 | ~$0.0002 |
| `src/research/timeline_tracer.ts` | Timeline analysis | OpenRouter (default) | TBD | — | — |
| `scripts/local-expansion/city_opportunity_scanner.ts` | City scanning | Gemini 2.0 Flash | TBD | — | — |

**Key prompt:** `buildSystemPrompt()` in `analyze_gazette.ts` — licitação taxonomy, 26 patterns, CoT.
**Coverage:** 84 territories (Wave 1 capitals + Wave 2/3 hubs). Querido Diário coverage ~6–7% of BR municipalities.
**Schema enrichment:** `ExtractedData` now includes `segmento`, `modalidade`, `porte`, `srp`, `exclusivo_me_epp`, `esfera`.

---

### egos-lab / agents

Agent runtime — 29 registered agents.

| File | Agent | Model(s) | Notes |
|------|-------|----------|-------|
| `agents/gem-hunter.ts` | Gem Hunter | Qwen Plus / Gemini Flash | Multi-track discovery (early-warning added 2026-04-01) |
| `agents/orchestrator.ts` | Master Orchestrator | Qwen Plus (DashScope) | Agent coordination, telemetry |
| `agents/ai-verifier.ts` | AI Verifier | google/gemini-2.0-flash-001 | Task validation |
| `agents/report-generator.ts` | Report Generator | Qwen Plus | Synthesis |
| `agents/ui-designer.ts` | UI Designer | google/gemini-2.0-flash-001 | UI code generation |

---

### 852

Issue-tracking + AI civic intelligence.

| File | Endpoint/Function | Model(s) | Max Tokens | Temp | Notes |
|------|-------------------|----------|------------|------|-------|
| `lib/ai-provider.ts` | `getModelConfig()` | DashScope → OpenRouter → OpenAI (fallback chain) | variable | 0.1–0.7 | Task-routing |
| `app/api/chat/route.ts` | Chat | Qwen Plus or Gemini Flash | 1,200–2,000 | 0.7 | Civic chat |
| `app/api/report/route.ts` | Report generation | Qwen (variable) | TBD | 0.5 | Intelligence reports |
| `lib/report-generator.ts` | Reports | DashScope (Qwen) | TBD | 0.1 | Low-temp, deterministic |
| `lib/name-validator.ts` | Name validation | Gemini 2.0 Flash | TBD | 0 | Deterministic |
| `app/api/review/route.ts` | Content review | Multi-provider | TBD | 0.2 | |
| `app/api/extract/route.ts` | Data extraction | Multi-provider | TBD | 0.1 | |
| `app/api/issues/reanalyze/route.ts` | Issue reanalysis | Multi-provider | TBD | 0.4 | |
| `app/api/ai-reports/generate/route.ts` | AI insights | Multi-provider | TBD | 0.3 | |
| `app/api/admin/telemetry/ai-insights/route.ts` | Telemetry AI | Multi-provider | TBD | 0.3 | Admin only |

**Tier routing:**
- `intelligence_report` → Qwen Max/Plus (premium) or Gemini Flash (fallback)
- `news_summarization` → Qwen Turbo (~$0.0001/1K)
- `name_validation` → Gemini Flash

---

### forja

Supply chain + production management.

| File | Function | Model(s) | Max Tokens | Temp |
|------|----------|----------|------------|------|
| `lib/chat/runtime.ts` | `chatWithLLM()` | Qwen Plus or Gemini 2.0 Flash | 1,200 | 0.3 |
| `app/api/chat/route.ts` | Chat | Default routing | 1,200 | 0.3 |
| `app/api/vision/insights/route.ts` | Vision analysis | OpenRouter (vision model) | TBD | 0.3 |
| `app/api/tools/pitch-score/route.ts` | Pitch scoring | OpenRouter | TBD | 0.2 |

---

### br-acc

Brazilian accountability/transparency tools (Python).

| File | Function | Model(s) | Max Tokens | Temp | Notes |
|------|----------|----------|------------|------|-------|
| `api/src/bracc/routers/chat.py` | `route_chat()` | google/gemini-2.0-flash-001 | 2,000 | 0.3 | ~$0.0003/query |
| `api/src/bracc/config.py` | Config | gpt-4o-mini (fallback) | TBD | TBD | Hardcoded fallback |
| `scripts/audit_openrouter.py` | Audit tool | Gemini Flash | 8,192 | 0.2 | Evaluation only |

**Multi-tool calling:** Up to 8 rounds/query. Premium (10 msgs/day): gpt-4o-mini. Free (20 msgs/day): Gemini Flash.

---

## Cost Model

```
Per 1,000 tokens (input/output):
  qwen-flash:       free (90-day quota via DashScope)
  qwen-turbo:       $0.0001 / $0.0002
  qwen-plus:        $0.0008 / $0.002
  qwen-max:         $0.0016 / $0.007
  qwq-plus:         ~$0.003 / $0.009 (reasoning)
  gemini-2.0-flash: ~$0.00015 / $0.00060
  gpt-4o-mini:      $0.00015 / $0.0006
  claude-sonnet-4.6:$0.003 / $0.015
```

**Monthly estimate (active usage):**
- Development/testing: < $5/mo
- Production (moderate load): $20–40/mo
- Heavy load (1K+ queries/day): $100–200/mo

---

## Gaps & Coverage Radar

| Gap | Status | Priority |
|-----|--------|----------|
| `carteira-livre` has zero AI integration | Instructor matching? Risk scoring? | P3 |
| `santiago` has zero AI integration | Depends on project goals | P3 |
| Eagle Eye: truncates gazette at 15K chars — misses 93%+ of content | Chunking strategy needed | P2 |
| `br-acc` Python stack diverges from TypeScript llm-provider | Consider port or bridge | P2 |
| No unified cost dashboard across all repos | OBS-012 task covers this | P2 |
| Telemetry not wired in `forja` API calls | TELEMETRY_SSOT.md Phase 4 | P3 |

---

## Auto-Update Mechanism

This document can be regenerated by:

```bash
# Scan all repos and update this file
bun /home/enio/egos/scripts/ai-coverage-scan.ts --update

# Dry-run (shows diff without writing)
bun /home/enio/egos/scripts/ai-coverage-scan.ts --dry-run
```

**Pre-commit hook** (`.claude/hooks/ai-coverage-update`): fires when any of these patterns change:
- `**/llm-provider.ts`
- `**/ai-provider.ts`
- `**/analyze_gazette.ts`
- Any file matching `**/chat/route.ts`
- `packages/shared/src/llm*.ts`

The hook calls `bun scripts/ai-coverage-scan.ts --check` which exits non-zero if coverage map is stale (new AI calls found that aren't registered here).

---

## Related Documents

- [TELEMETRY_SSOT.md](TELEMETRY_SSOT.md) — Telemetry schema (API call recording, cost tracking)
- [MODEL_SPECIALIZATIONS.md](MODEL_SPECIALIZATIONS.md) — Model capability matrix
- [strategy/MULTI_MODEL_PLANNING.md](strategy/MULTI_MODEL_PLANNING.md) — Strategic routing decisions
- [MCP_INTEGRATION_MAP.md](MCP_INTEGRATION_MAP.md) — MCP server integrations
- `packages/shared/src/llm-provider.ts` — Canonical fallback chain implementation

---

*Auto-update: `bun scripts/ai-coverage-scan.ts --update`*
*Version: 1.0.0 — 2026-04-01*
