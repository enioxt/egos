# Gem Hunter v6.0 — Master Plan

> **Version:** 1.0.0 | **Created:** 2026-04-02
> **Owner:** EGOS Kernel | **Domain:** Discovery Intelligence
> **Status:** APPROVED — User confirmed all 5 decisions 2026-04-02
> **SSOT Ref:** `docs/gem-hunter/SSOT.md`

---

## User Decisions (Confirmed 2026-04-02)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Paper output format** | **B** (scaffold .ts + .md spec) | Maximum value extraction; use free/low-cost models |
| **Trend awareness** | **B** (fully autonomous) with C fallback | Self-aware agent that reads project context + X.com |
| **Budget** | **~$15/month** | Free tiers first, Gemini Flash paid, Alibaba free quota |
| **Standalone priority** | **D** (all: API → Bot → Dashboard → NPM) | Sequential rollout: revenue first |
| **Scoring IP** | **Percentage-based pricing** | Modern x402/pix model, easy for laypeople |

---

## Cost Analysis

### LLM Fallback Chain (for paper reading + synthesis)

```
Priority 1: Alibaba Qwen-plus (free tier)
  - 1M tokens one-time (90-day validity)
  - Cost: $0.00 (within quota)
  - Speed: Fast
  - Quality: Good for triage + abstract analysis

Priority 2: OpenRouter free models
  - Qwen-2.5-7b: FREE (unlimited)
  - Llama 3.1 8B: FREE
  - Gemma 2 9B: FREE
  - Cost: $0.00
  - Speed: Variable (queue-based)
  - Quality: Acceptable for bulk filtering

Priority 3: Gemini 2.0 Flash (paid)
  - $0.075 per 1M input tokens
  - $0.30 per 1M output tokens
  - Cost: ~$0.01 per paper (avg 8K tokens)
  - Speed: Fast
  - Quality: Excellent for deep reading

Priority 4: OpenRouter paid models
  - Claude 3.5 Haiku: $0.80/1M input
  - Cost: ~$0.008 per paper
  - Speed: Fast
  - Quality: High
```

### Cost Per Pipeline Stage

| Stage | Volume/Day | Model Used | Cost/Day | Cost/Month |
|-------|-----------|------------|----------|------------|
| **L1: Discovery** (API calls) | 14 sources × 3 queries | Free APIs (arXiv, GitHub, PWC, HF, etc.) | $0.00 | $0.00 |
| **L2: Abstract Triage** | ~200 papers filtered | Qwen free → OpenRouter free | $0.00 | $0.00 |
| **L3: Deep Reading** | ~20 papers selected | Gemini Flash (paid) | $0.20 | $6.00 |
| **L4: Scaffold Generation** | ~5 top papers | Gemini Flash or Qwen | $0.05 | $1.50 |
| **L5: Synthesis Report** | 1 daily report | Qwen free | $0.00 | $0.00 |
| **L6: Trend Monitor** (X.com) | 50 tweets/day | Exa ($0.05/query × 5) | $0.25 | $7.50 |
| **TOTAL** | | | **$0.50/day** | **$15.00/month** |

### Existing Integrations (Zero Additional Cost)

| Integration | Free Tier | Used For |
|-------------|-----------|----------|
| arXiv API | Unlimited (1 req/3s) | Paper discovery, abstracts |
| Papers With Code API | Unlimited | Paper+code pairings, papers WITHOUT code |
| GitHub API | 5K req/hr (authenticated) | Repo discovery, code search |
| HuggingFace API | Unlimited | Model/space discovery |
| NPM Registry | Unlimited | Package discovery |
| Reddit API | Unlimited (1.5s buffer) | Community signals |
| HackerNews API | Unlimited | Tech news, trending |
| StackOverflow API | 300 req/day (no auth) | Q&A signals |
| Zenodo API | Unlimited | Research data |
| Telegram Bot API | Unlimited | Alert distribution |
| Supabase | Free tier (2GB) | Data persistence |
| Brave Search | Free tier | Web search backup |

### Cost Comparison: Options A vs B vs C

| Option | Description | Cost/Month | Value |
|--------|-------------|------------|-------|
| **C** (task only) | Paper → TASKS.md entry | $0.00 | Low (manual follow-up) |
| **A** (report) | Paper → .md spec report | $6.00 | Medium (actionable docs) |
| **B** (scaffold) | Paper → .ts stubs + .md spec | $7.50 | **High (ready to implement)** |

**Decision: B** — Only $1.50/month more than A, but delivers ready-to-implement scaffolds.

---

## Architecture: Papers Without Code Pipeline

### The Vision

```
User's method (2017-2025, crypto gem hunting):
  "Follow KOLs on X → Read posts/conversations → 
   Spot project announcements → Read whitepapers → 
   Evaluate potential → Document findings"

Codified as:
  L1 Discover → L2 Filter → L3 Read Abstract → 
  L4 Read Full → L5 Select → L6 Scaffold + Report
```

### Pipeline: 6-Stage Paper Intelligence

```
┌─────────────────────────────────────────────────────────┐
│ STAGE 1: DISCOVERY (Free APIs, 3x/day)                  │
│                                                         │
│ arXiv API: cat:cs.AI + cat:cs.MA + cat:cs.SE            │
│   → Filter: papers with NO github.com link              │
│   → Filter: published last 30 days                      │
│   → Extract: title, abstract, authors, categories       │
│                                                         │
│ Papers With Code API: /papers/?no_code=true              │
│   → Papers with 0 implementations                       │
│   → High citation count but no code                     │
│                                                         │
│ X.com KOL Monitor (Exa + X API):                        │
│   → Track 50+ curated accounts                          │
│   → Extract: paper links, project announcements          │
│   → Keywords: "new paper", "novel approach", "framework" │
│                                                         │
│ Output: ~200 paper candidates/day                        │
├─────────────────────────────────────────────────────────┤
│ STAGE 2: ABSTRACT TRIAGE (Free LLM)                     │
│                                                         │
│ Model: Qwen-plus (free) → OpenRouter free fallback      │
│                                                         │
│ Prompt: "Read this abstract. Score 0-100 on:            │
│   - Implementability (can this become code?)             │
│   - EGOS relevance (agents, governance, search, etc.)    │
│   - Novelty (is this genuinely new?)                     │
│   - Specificity (concrete architecture vs vague idea?)   │
│   Return: score, 1-line summary, top 3 keywords"        │
│                                                         │
│ Filter: score >= 60 passes to Stage 3                    │
│ Output: ~20 papers/day                                   │
├─────────────────────────────────────────────────────────┤
│ STAGE 3: DEEP READING (Low-cost LLM)                    │
│                                                         │
│ Model: Gemini Flash ($0.01/paper)                        │
│                                                         │
│ Read: Introduction + Methodology + Architecture sections │
│ (Not full paper — targeted extraction)                   │
│                                                         │
│ Prompt: "Extract from this paper:                        │
│   1. Core architecture (components, data flow)           │
│   2. Key algorithms (pseudocode if present)              │
│   3. Evaluation metrics (benchmarks, comparisons)        │
│   4. Implementation requirements (stack, dependencies)    │
│   5. EGOS integration points (where would this fit?)     │
│   6. Estimated implementation effort (hours/days)        │
│   Return: structured JSON"                               │
│                                                         │
│ Filter: integration_score >= 70 passes to Stage 4        │
│ Output: ~5 papers/day                                    │
├─────────────────────────────────────────────────────────┤
│ STAGE 4: SCAFFOLD GENERATION (Low-cost LLM)             │
│                                                         │
│ Model: Gemini Flash or Qwen                              │
│                                                         │
│ For each top paper:                                      │
│   1. Generate TypeScript interfaces from architecture    │
│   2. Create stub functions with JSDoc from algorithms    │
│   3. Write test spec skeleton from evaluation criteria   │
│   4. Create integration spec (.md) for EGOS             │
│                                                         │
│ Output per paper:                                        │
│   docs/gem-hunter/papers/<paper-id>/                     │
│   ├── REPORT.md          (full analysis)                 │
│   ├── architecture.ts    (interfaces + types)            │
│   ├── stubs.ts           (function signatures + JSDoc)   │
│   ├── spec.test.ts       (test skeleton)                 │
│   └── integration.md     (EGOS fit analysis)             │
│                                                         │
│ Output: ~5 scaffold packages/day                         │
├─────────────────────────────────────────────────────────┤
│ STAGE 5: SCORING + WORLD MODEL (Free)                   │
│                                                         │
│ Score using 9-factor algorithm (weights.yaml)            │
│ If score > 80: append to world-model signals[]           │
│ If score > 85: auto-create TASKS.md entry               │
│ If score > 90: Telegram alert + X.com thread candidate   │
│                                                         │
│ Output: docs/gem-hunter/papers/daily-digest.md           │
├─────────────────────────────────────────────────────────┤
│ STAGE 6: TREND EVOLUTION (Free + Exa)                   │
│                                                         │
│ Read: git log --oneline -20 (what WE are building)      │
│ Read: TASKS.md P0/P1 (current priorities)               │
│ Read: X.com trending (via Exa, $0.25/day)               │
│ Read: Previous discovery reports (what we already found) │
│                                                         │
│ Generate: Next-round queries (auto-update DEFAULT_QUERIES│
│ Generate: KOL activity summary                           │
│ Generate: Trend direction report                         │
│                                                         │
│ Output: docs/gem-hunter/trends/YYYY-MM-DD.md             │
└─────────────────────────────────────────────────────────┘
```

---

## Standalone Rollout (Sequential)

### Phase 1: API + Bot (Week 1-2) — Revenue First

```
POST /v1/hunt     → Trigger discovery run
GET  /v1/findings → List scored findings
GET  /v1/papers   → Papers Without Code results
POST /v1/alert    → Configure Telegram/Discord alerts

Authentication: API key (shared with Guard Brasil tenant system)
Pricing: Percentage-based (% of LLM cost + margin)
  - Free tier: 10 findings/day
  - Pro: unlimited, $0.02/finding + 20% margin on LLM costs
  - Enterprise: dedicated instance + custom scoring weights
```

### Phase 2: Dashboard (Week 3-4)

```
gemhunter.egos.ia.br
  /dashboard      → Live findings feed
  /papers         → Papers Without Code browser
  /trends         → Trend evolution charts
  /settings       → Scoring weight customization
  /alerts         → Notification configuration
```

### Phase 3: NPM Package (Month 2)

```
@egosbr/gem-hunter
  CLI: npx gem-hunter --track=papers --topic=agents
  Library: import { hunt, score } from '@egosbr/gem-hunter'
  Config: .gem-hunter.yaml (custom sources, weights, filters)
```

### Phase 4: Multi-Channel Distribution (Month 2-3)

```
Telegram Bot  → /hunt <topic> → returns top 5 findings
Discord Bot   → !gems today → daily digest
WhatsApp      → Evolution API → structured alerts
X.com         → Auto-thread on score > 90 findings
```

---

## Pricing Model: Percentage-Based

Inspired by the user's crypto experience + modern agentic economy:

```
Revenue = User's LLM cost × (1 + margin%)

Example:
  User requests deep paper analysis
  LLM cost: $0.05 (Gemini Flash reads 5 papers)
  EGOS margin: 40%
  User pays: $0.05 × 1.40 = $0.07

Payment methods:
  - Stripe (credit card, instant)
  - Pix (Brazilian instant, 0% fee)
  - x402 Protocol (M2M agent payments, crypto)
  - Bitcoin Lightning (micropayments)

Tiers:
  Free:       10 findings/day, basic scoring, no scaffolds
  Pro:        Unlimited, full scoring, scaffolds, alerts ($0.02/finding + LLM%)
  Enterprise: Custom weights, dedicated instance, SLA ($499/mo)
```

---

## Competitive Advantages (What We Already Have)

| Advantage | Details | Competitors Lack |
|-----------|---------|-----------------|
| **14 integrated sources** | GitHub + arXiv + PWC + HF + Exa + Reddit + X + 7 more | aixbt: X only. Kaito: crypto only. Elicit: papers only. |
| **Papers WITHOUT Code** | Unique pipeline: find ideas before implementation exists | Nobody does this systematically |
| **9-factor scoring** | Configurable weights, research bonuses, CJK filters | Generic star-count sorting |
| **SSOT Lego Atomization** | Extract reusable code blocks from discoveries | No competitor does this |
| **Governance integration** | Pre-commit hooks, frozen zones, drift detection | No competitor has governance |
| **World Model feedback** | Discoveries feed back into project intelligence | Closed-loop intelligence |
| **Multi-LLM fallback** | Qwen → OpenRouter → Gemini → Claude (cost-optimized) | Single-provider lock-in |
| **Your 8 years of pattern recognition** | 1000+ projects evaluated, codified in weights | Cannot be replicated |

---

## Implementation Order

### Week 1 (Foundation)

| Priority | Task ID | Description | Effort | Model |
|----------|---------|-------------|--------|-------|
| 1 | GH-051 | Papers Without Code: arXiv `no_code` filter + PWC `no_implementations` | 3h | Free APIs |
| 2 | GH-054 | Multi-LLM fallback chain (Qwen → OpenRouter → Gemini → Claude) | 3h | Code |
| 3 | GH-053 | Evolution Engine auto-integrate (trending → next queries) | 2h | Code |
| 4 | GH-050 | World model signal ingestion (score > 80 → signals[]) | 2h | Code |
| 5 | GH-055 | Telegram alerts (score > 80 → notification) | 2h | Telegram API |
| 6 | CLEAN-001 | Remove outdated reports, unify SSOT locations | 1h | Housekeeping |

### Week 2 (Intelligence)

| Priority | Task ID | Description | Effort | Model |
|----------|---------|-------------|--------|-------|
| 1 | GH-056 | Multi-stage paper reading (6-stage pipeline) | 8h | Gemini Flash |
| 2 | GH-057 | Context awareness (git log + TASKS.md + X.com → query adjustment) | 6h | Exa + free LLM |
| 3 | GH-052 | KOL list curated (50+ X.com accounts for monitoring) | 2h | User input |
| 4 | GH-059 | Cost budgeting (token counter + projection) | 3h | Code |
| 5 | GH-060 | Structural validation (README, tests, benchmarks check) | 3h | Code |

### Week 3-4 (Monetization)

| Priority | Task ID | Description | Effort | Model |
|----------|---------|-------------|--------|-------|
| 1 | GH-058 | Standalone API (POST /v1/hunt + GET /v1/findings + auth) | 4h | Code |
| 2 | BIZ-001 | Unified monetization SSOT | 4h | Docs |
| 3 | GH-065 | Percentage-based pricing implementation | 2h | Stripe + Code |
| 4 | GH-061 | Dashboard web (gemhunter.egos.ia.br) | 2 weeks | React |

### Month 2-3 (Scale)

| Priority | Task ID | Description | Effort |
|----------|---------|-------------|--------|
| 1 | GH-062 | NPM package (@egosbr/gem-hunter CLI) | 1 week |
| 2 | GH-063 | x402 pay-per-call (M2M agent payments) | 1 week |
| 3 | GH-064 | Multi-channel distribution (WhatsApp, Discord) | 3 days |
| 4 | GH-066 | Paper → Code generator (LLM reads paper, generates full scaffold) | 2 weeks |

---

## Success Metrics

| Metric | Target (Month 1) | Target (Month 3) | Target (Month 6) |
|--------|------------------|-------------------|-------------------|
| **Papers discovered/day** | 200 | 500 | 1000 |
| **Papers scaffolded/day** | 5 | 15 | 30 |
| **Score accuracy** | 70% (human agreement) | 80% | 90% |
| **LLM cost/day** | $0.50 | $1.00 | $2.00 |
| **API customers** | 0 | 5 | 20 |
| **MRR** | $0 | $100 | $500 |
| **Telegram subscribers** | 10 | 50 | 200 |

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| arXiv rate limiting | LOW | MEDIUM | Built-in 3s delay + caching |
| Free LLM tier exhaustion | MEDIUM | LOW | Multi-model fallback chain |
| Low scoring accuracy | MEDIUM | HIGH | Human-in-the-loop validation first month |
| Paper reading hallucinations | MEDIUM | MEDIUM | Cross-reference with original PDF |
| Competitor copies approach | LOW | LOW | 8 years of weights + governance = hard to replicate |

---

## References

- **SSOT:** `docs/gem-hunter/SSOT.md`
- **Weights:** `docs/gem-hunter/weights.yaml`
- **Registry:** `docs/gem-hunter/registry.yaml`
- **Engine:** `agents/agents/gem-hunter.ts` (v5.1, 1618 LOC)
- **Integration Map:** `docs/gem-hunter/GEM_HUNTER_v6_MASTER_PLAN.md` (this file)
- **Business Model:** `docs/strategy/FREE_VS_PAID_SURFACE.md` (Guard Brasil reference)
- **Pricing Research:** `docs/strategy/GUARD_BRASIL_PRICING_RESEARCH.md`

---

*Created: 2026-04-02 | Author: Claude Opus 4.6 + Enio Rocha (dialectic refinement)*
