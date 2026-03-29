# LLM Orchestration Matrix

> **SSOT Owner:** `egos/docs/governance/LLM_ORCHESTRATION_MATRIX.md`
> **Version:** 1.0.0 | **Created:** 2026-03-29 | **Status:** ACTIVE
> **Task:** EGOS-080

---

## Purpose

Explicit lane ownership for every LLM environment in the EGOS ecosystem. Prevents conflicting orchestration, clarifies authority level, and sets allowed task classes per lane.

---

## Orchestration Lanes

### Lane 1: Alibaba Qwen (Primary Orchestrator)

| Field | Value |
|-------|-------|
| **Environment** | Terminal / Bun scripts / kernel agents |
| **Model** | `qwen-plus` via DashScope API |
| **Fallback** | Gemini via OpenRouter |
| **Approval mode** | Autonomous (no confirmation for T0/T1 tasks) |
| **Authority level** | HIGH — can write files, run agents, execute governance scripts |
| **Trigger** | `bun run agent:run`, kernel scripts, `llm-provider.ts` |
| **Allowed task classes** | Agent execution, SSOT drift check, governance sync, capability audit, code generation for packages |
| **NOT allowed** | Push to remote, delete branches, modify frozen zones, publish npm |
| **Cost gate** | Budget mode: conservative by default; balanced for complex orchestration |

---

### Lane 2: Claude Code (Interactive + Strategic)

| Field | Value |
|-------|-------|
| **Environment** | Claude Code CLI (`claude`) |
| **Model** | `claude-sonnet-4-6` (this session) |
| **Approval mode** | Interactive — user approves tool calls |
| **Authority level** | HIGH — full file system + git access, confirmed by user |
| **Trigger** | User session, `/start`, task instructions |
| **Allowed task classes** | Implementation, governance docs, architecture decisions, PR preparation, complex refactors, agent design |
| **NOT allowed** | Autonomous push without user confirmation, modify `.husky/pre-commit` without frozen-zone override |
| **Signature** | All commits include `https://claude.ai/code/session_...` footer |

---

### Lane 3: Windsurf / Cascade (IDE Pair)

| Field | Value |
|-------|-------|
| **Environment** | Windsurf IDE |
| **Model** | Cascade (contextual) |
| **Approval mode** | Interactive — user reviews diffs |
| **Authority level** | MEDIUM — file writes, no direct git push without review |
| **Trigger** | IDE open, `.windsurf/workflows/` slash commands |
| **Allowed task classes** | Code completion, inline refactoring, workflow execution (`/start`, `/end`, `/disseminate`), quick docs |
| **NOT allowed** | Modify canonical SSOT docs without running governance check, push to main |
| **Governance files** | `.windsurf/workflows/`, `.windsurf/skills/` |

---

### Lane 4: Google AI Studio (Research + Prototyping)

| Field | Value |
|-------|-------|
| **Environment** | Google AI Studio (browser) |
| **Model** | Gemini Pro / Flash |
| **Approval mode** | Manual — user copies outputs |
| **Authority level** | LOW — read-only for repo; outputs require reconciliation pass |
| **Trigger** | Manual session |
| **Allowed task classes** | Research, market analysis, architecture brainstorming, PRD drafting |
| **NOT allowed** | Direct code push without reconciliation; planning decisions based on outputs that weren't verified against kernel SSOT (EGOS-097) |
| **Reconciliation rule** | Any AI Studio output that affects TASKS.md or architecture must be reconciled via `/restore-context` or manual kernel SSOT check before acting |

---

### Lane 5: OpenAI Codex (Batch Code Generation)

| Field | Value |
|-------|-------|
| **Environment** | Codex CLI / OpenAI API |
| **Model** | GPT-4o / o3 |
| **Approval mode** | Manual review of output |
| **Authority level** | MEDIUM — generates code, user applies |
| **Trigger** | `codex` CLI, explicit invocation |
| **Allowed task classes** | Bulk code generation, test writing, boilerplate, migration scripts |
| **NOT allowed** | Direct commits; every output requires human review + tsc pass before staging |

---

### Lane 6: OpenRouter (Multi-Model Routing)

| Field | Value |
|-------|-------|
| **Environment** | `packages/shared/src/llm-provider.ts` |
| **Models** | Gemini Flash (fast), Qwen-plus (balanced), Claude Haiku (structured), GPT-4o-mini (fallback) |
| **Approval mode** | Autonomous (runtime routing) |
| **Authority level** | RESPONSE ONLY — no file system access from this lane |
| **Trigger** | `createLLMProvider()`, AI client in leaf apps |
| **Allowed task classes** | Chat responses, summarization, classification, embedding, streaming |
| **NOT allowed** | File writes, git operations, governance decisions |
| **Cost routing** | Flash for speed, Qwen for balance, Claude for structure |

---

## Decision Matrix

| Task Class | Primary Lane | Fallback Lane |
|-----------|-------------|--------------|
| Governance doc writing | Claude Code (Lane 2) | Windsurf (Lane 3) |
| Agent execution | Alibaba Qwen (Lane 1) | Bun CLI direct |
| Architecture brainstorming | Claude Code (Lane 2) | AI Studio (Lane 4) |
| Market research | AI Studio (Lane 4) | Claude Code (Lane 2) |
| Bulk code gen | Codex (Lane 5) | Claude Code (Lane 2) |
| Chat response (production) | OpenRouter (Lane 6) | Alibaba Qwen (Lane 1) |
| SSOT drift check | Alibaba Qwen (Lane 1) | `bun run governance:check` |
| PR review | Claude Code (Lane 2) | Windsurf (Lane 3) |
| npm publish | Human only | — |

---

## Conflict Resolution Rules

1. **When two lanes disagree on architecture:** Claude Code (Lane 2) has final say for kernel decisions. Document the disagreement in TASKS.md.
2. **When AI Studio produces a plan:** Must be reconciled against kernel SSOT before any task is created. Do not act on unreconciled AI Studio plans.
3. **When Codex produces code:** Must pass `tsc --noEmit` and pre-commit hooks before staging.
4. **Frozen zones:** No lane may modify frozen zone files without user confirmation + proof-of-work, regardless of authority level.

---

## Cost Budget Guidelines

| Lane | Monthly budget | Alert threshold |
|------|---------------|----------------|
| Alibaba Qwen | ~R$50 | R$80 |
| OpenRouter (runtime) | ~R$30 | R$60 |
| Claude Code | OpenAI subscription | N/A |
| AI Studio | Free tier | — |

---

*Maintained by: EGOS Kernel*
*Related: EGOS-080, EGOS-071, packages/shared/src/llm-provider.ts, packages/shared/src/model-router.ts*
