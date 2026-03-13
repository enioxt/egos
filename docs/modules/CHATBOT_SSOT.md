# CHATBOT_SSOT — Canonical Chatbot Standard

> **VERSION:** 1.1.0 | **UPDATED:** 2026-03-13
> **REFERENCE IMPLEMENTATION:** `/home/enio/852` (852 Inteligência) + reusable core modules in `/home/enio/egos/packages/shared`
> **STATUS:** Active — all new chatbots MUST follow this standard

---

## Purpose

This document defines the canonical chatbot architecture for the EGOS ecosystem.
Every chatbot (852, Forja, carteira-livre, future projects) MUST implement these
modules or explicitly document why a module is skipped.

The 852 project is the reference implementation — battle-tested in production
with real users, VPS deployment, and full governance integration.

---

## 1. Modular Prompt Architecture

**Reference:** `852/src/lib/prompt.ts`

### Pattern

Prompts are assembled from composable sections, not monolithic strings:

```
FOUNDATION + GOVERNANCE + GUARDRAILS + PRIVACY + DOMAIN_REFERENCES + TASK_INSTRUCTIONS + OUTPUT_FORMAT
```

### Required Sections

| Section | Purpose | Required |
|---------|---------|----------|
| `FOUNDATION` | EGOS identity, project context, core principles | YES |
| `GOVERNANCE` | Legal boundaries, channel limits, formal redirects | YES |
| `GUARDRAILS` | ATRiAN truth layer (see Module 2) | YES |
| `PRIVACY` | PII rules, anonymization requirements | YES |
| `DOMAIN_REFERENCES` | Domain-specific knowledge (laws, acronyms, etc.) | Per project |
| `TASK_INSTRUCTIONS` | Context-specific behavior (chat vs review vs report) | YES |
| `OUTPUT_FORMAT` | Structured output schemas (JSON for non-chat tasks) | Per task |

### Required Function

```typescript
function buildPrompt(context: TaskContext, memoryBlock?: string | null): string
```

- Accepts a task context enum and optional memory block
- Memory block is prepended (most recent context first)
- Returns fully assembled system prompt

### Task Contexts (minimum)

Every chatbot MUST support at least: `chat`, `review`, `conversation_summary`.
Additional contexts are project-specific.

---

## 2. ATRiAN Ethical Validation Layer

**Reference:** `egos/packages/shared/src/atrian.ts` (ported from `852/src/lib/atrian.ts`)

### Architecture

ATRiAN operates as a **post-response validator** — it checks AI output AFTER generation,
not just at the prompt level. This catches hallucinations that bypass prompt instructions.

### Required Checks

| # | Category | Level | Description |
|---|----------|-------|-------------|
| 1 | `blocked_entity` | CRITICAL | Domain-specific blocklist (entities that must never appear) |
| 2 | `invented_acronym` | WARNING | Acronyms not in known whitelist |
| 3 | `absolute_claim` | WARNING | Claims without epistemic hedging |
| 4 | `fabricated_data` | ERROR | References to unverifiable statistics/studies |
| 5 | `false_promise` | ERROR | Promises of action the system cannot fulfill |

### Required Interface

```typescript
interface AtrianResult {
  passed: boolean;        // false if any CRITICAL or ERROR
  violations: AtrianViolation[];
  score: number;          // 0-100, 100 = fully compliant
}

function validateResponse(text: string): AtrianResult;
function validateAndReport(text: string): AtrianResult;
function filterChunk(chunk: string): string;  // Stream-level critical filter
```

### Scoring

| Level | Deduction | Action |
|-------|-----------|--------|
| info | -2 | Log only |
| warning | -5 | Log + flag in telemetry |
| error | -15 | Log + block sharing/publishing |
| critical | -30 | Log + redact from output |

### Customization Per Project

Each project MUST define its own:
- `BLOCKED_ENTITIES` list (domain-specific)
- `KNOWN_ACRONYMS` whitelist (domain-specific)
- Additional pattern detectors as needed

---

## 3. PII Scanner

**Reference:** `egos/packages/shared/src/pii-scanner.ts` (ported from `852/src/lib/pii-scanner.ts`)

### Required Categories (Brazilian context)

| Category | Pattern | Suggestion |
|----------|---------|------------|
| `cpf` | `\d{3}.\d{3}.\d{3}-\d{2}` | `[CPF REMOVIDO]` |
| `phone` | Brazilian phone formats | `[TELEFONE REMOVIDO]` |
| `email` | Standard email regex | `[EMAIL REMOVIDO]` |
| `name` | Heuristic (role + capitalized words) | `[NOME REMOVIDO]` |

Additional categories are project-specific (RG, MASP, plates, REDS, etc.).

### Required Functions

```typescript
function scanForPII(text: string): PIIFinding[];
function sanitizeText(text: string, findings: PIIFinding[]): string;
function getPIISummary(findings: PIIFinding[]): string;
```

### UI Integration

Findings include `start` and `end` positions for highlighting in the UI.

---

## 4. Conversation Memory

**Reference:** `egos/packages/shared/src/conversation-memory.ts` (ported from `852/src/lib/conversation-memory.ts`)

### Pattern

1. After a conversation reaches 4+ messages, generate an AI summary (max 6 bullets)
2. Store summary in conversation metadata (Supabase or equivalent)
3. On new conversation, fetch last N summaries for same identity
4. Inject as a `## MEMÓRIA DE SESSÕES ANTERIORES` block in the system prompt

### Epistemic Safety

Memory block MUST include hedging:
> "Use apenas como contexto, sem afirmar como fato novo."
> "Se algo parecer desatualizado, confirme com o usuário antes de assumir continuidade."

### Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MAX_MEMORY_ITEMS` | 3 | Max previous conversation summaries |
| `MIN_MESSAGES_FOR_SUMMARY` | 4 | Min messages before generating summary |
| `MAX_SUMMARY_LENGTH` | 1200 chars | Truncation limit |
| `SUMMARY_TEMPERATURE` | 0.2 | Low temperature for factual summaries |

---

## 5. Task-Based Model Routing

**Reference:** `852/src/lib/ai-provider.ts`

### Pattern

Different tasks route to different models based on cost/quality tradeoffs:

| Task Type | Recommended Model | Reasoning |
|-----------|-------------------|-----------|
| `chat` | Primary (Qwen-plus) | Best quality for conversation |
| `review` | Fast (Gemini Flash) | Structured output, speed matters |
| `html_report` | Fast (Gemini Flash) | Template generation |
| `intelligence_report` | Premium (Qwen-max) | Complex synthesis |
| `conversation_summary` | Fast (Gemini Flash) | Short, factual |
| `name_validation` | Fast (Gemini Flash) | Binary classification |

### Required: 3-Tier Fallback

```
Primary (DashScope/Alibaba) → Fallback (OpenRouter/Gemini) → Emergency (OpenAI)
```

### Required: Budget Mode

Support `AI_BUDGET_MODE` env var: `conservative` | `balanced` | `aggressive`

### Required: Cost Tracking

Every AI call MUST calculate and record cost:
```typescript
const cost = (inputTokens / 1000) * pricing.input + (outputTokens / 1000) * pricing.output;
```

---

## 6. Writing Style Rules

### Mandatory for ALL Chatbots

| Rule | Description |
|------|-------------|
| **Epistemic markers** | Use "com base no que foi relatado", "isso sugere", "isso pode indicar" |
| **Question limit** | Max 2 questions per response |
| **Depth over breadth** | Explore one topic deeply before switching |
| **No fabrication** | Never invent facts, statistics, or institutional links |
| **No false promises** | Never promise actions the system cannot fulfill |
| **Transparency** | Be explicit about limitations and uncertainty |
| **Conciseness** | Professional, direct, human tone |

### Configurable Per Project

| Rule | 852 Value | Forja Value | Default |
|------|-----------|-------------|---------|
| **No em-dashes** | Yes (public copy) | TBD | No |
| **Language** | pt-BR (formal) | pt-BR (informal/field) | pt-BR |
| **Tone** | Institutional | Operational | Professional |

---

## 7. Telemetry

**Reference:** `852/src/lib/telemetry.ts`

### Required Events

| Event Type | When | Data |
|------------|------|------|
| `chat_completion` | After every AI response | model, provider, tokens, cost, IP |
| `chat_error` | On API error | error message, IP |
| `rate_limit_hit` | On 429 | IP, endpoint |
| `atrian_violation` | On ATRiAN check fail | score, categories, levels |
| `provider_unavailable` | On 503 | — |

### Dual Output

1. **Structured logs** (JSON to stdout for Docker/observability)
2. **Persistent store** (Supabase or equivalent for dashboards)

---

## 8. Production Hardening

### Required for ALL Public Chatbots

| Control | Default | Description |
|---------|---------|-------------|
| Rate limiting | 12 msgs / 5 min / IP | In-memory or Redis |
| Message sanitization | Max 12 messages, 4000 chars each | Prevent context overflow |
| Provider availability check | Before every request | Return 503 if no provider |
| Input validation | Reject empty/malformed | Return 400 |
| Cost headers | X-Model-Id, X-Provider, X-Model-Free | Transparency |
| Rate headers | X-RateLimit-Remaining, X-RateLimit-Reset | Client awareness |

---

## 9. Implementation Checklist

For any new chatbot project, verify all modules:

- [ ] Modular prompt with composable sections
- [ ] ATRiAN validation layer with project-specific blocklists
- [ ] PII scanner with Brazilian patterns (minimum: CPF, phone, email, name)
- [ ] Conversation memory with epistemic hedging
- [ ] Task-based model routing with 3-tier fallback
- [ ] Writing style rules documented in `.guarani/PREFERENCES.md`
- [ ] Telemetry (dual output: logs + persistent store)
- [ ] Rate limiting
- [ ] Message sanitization
- [ ] Provider availability check
- [ ] Cost tracking per request
- [ ] ATRiAN violations dashboard (admin)

---

## 10. Live Replication Protocol

Every chatbot/module rollout MUST follow this order:

1. **Analyze** — locate the real chat surface, prompt assembly point, provider layer, telemetry path, and memory store.
2. **Research** — compare target code against `docs/CAPABILITY_REGISTRY.md`, this SSOT, and the strongest repo-specific implementation.
3. **Implement minimally** — prefer shared modules from `@egos/shared` before copying local logic.
4. **Test** — run the narrowest typecheck/build validation that proves integration did not break the target.
5. **Validate** — run `chatbot_compliance_checker` and record the score as evidence, not as proof of production parity.
6. **Human loop** — stop for explicit review when auth, frozen zones, destructive migrations, or product-direction choices appear.
7. **Disseminate** — update `TASKS.md`, `docs/CAPABILITY_REGISTRY.md`, `/disseminate`, and the adoption table below.

Minimum evidence per rollout:

- typecheck/build output
- compliance checker output
- exact files changed
- adoption status updated with nuanced maturity (`SSOT`, `HAS`, `FOUNDATION`, `BASIC`, `PLAN`)

---

## 11. Adoption Status

| Project | Status | Verified State | Next Gap |
|---------|--------|----------------|----------|
| **852** | SSOT Reference | Production-grade reference implementation with prompt, ATRiAN, PII, memory, routing, telemetry, and hardening. | Keep as origin benchmark. |
| **carteira-livre** | HAS | Shared ATRiAN/PII/memory modules integrated in `app/api/tutor/route.ts`; validated by typecheck + `chatbot_compliance_checker` `100/100`. | Broader 852 parity remains optional (exports/dashboard-level extras). |
| **intelink** | HAS | Shared ATRiAN/PII/memory modules integrated in `app/api/chat/route.ts`; validated by typecheck + `chatbot_compliance_checker` `100/100`. | Deeper parity with 852 review/export surfaces remains optional. |
| **egos-web** | BASIC | Public chat has provider fallback, rate limiting, cost guard, prompt hardening, and file-context awareness; `chatbot_compliance_checker` currently scores `64/100`. | Adopt shared ATRiAN/PII/memory modules and align maturity tags in registry. |
| **Forja** | FOUNDATION | Prompt builder + `/api/chat` foundation integrated with shared modules; validated by typecheck + `chatbot_compliance_checker` `100/100`. | DB-backed memory, durable telemetry, tools, and full production workflow still pending. |
| **br-acc** | Python variant | Tool-calling chat, public guard, in-memory conversation state, evidence chain, and rate limits exist in Python; `chatbot_compliance_checker` currently scores `71/100`. | Define ATRiAN/shared-module adapter path and align replication contract to this SSOT. |

---

*"Confiança verificável, não crença cega." — ATRiAN*
