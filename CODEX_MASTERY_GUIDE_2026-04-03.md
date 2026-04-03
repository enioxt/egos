# Codex Mastery Guide — Understand Everything
> **Purpose:** Deep understanding of Codex capabilities, limitations, and optimal use  
> **Date:** 2026-04-03  
> **Status:** RESEARCH PHASE

---

## WHAT IS CODEX?

**Codex** is your **strategic code generation agent** that:
- Analyzes large repositories (entire codebase understanding)
- Generates PRs with detailed explanations
- Provides architecture-level suggestions
- Understands your EGOS governance rules deeply
- Creates **actionable research** (not just code)

**NOT:** A copilot for quick edits. This is a **strategic thinker**.

---

## CODEX WITHIN EGOS ECOSYSTEM

### Current Codex Work in Your Repos

**PR #30: QA Observability Suite** (Just merged)
- ✅ Analyzed EGOS telemetry gaps
- ✅ Created 45-file PR with:
  - Telemetry APIs (recordAgentSession, recordToolCall)
  - QA automation scripts (9 Python scripts)
  - CI integration + workflow updates
  - Comprehensive docs
- ✅ Quality assessment: ⭐⭐⭐⭐⭐
- **Impact:** Solved observability blind spots you had

### What This Tells Us About Codex

1. **Strength:** Deep architectural understanding
   - Identified where telemetry was missing
   - Proposed comprehensive solution
   - Integrated across 45 files seamlessly

2. **Limitation:** Takes weeks for large features
   - PR #30 took days to create
   - Rate-limited after certain volume
   - Needs guidance on what to focus on

3. **Best Use:** Strategic research + architecture PRs
   - NOT quick fixes
   - NOT daily coding tasks
   - YES large-scale refactors/features

---

## CODEX CAPABILITIES (What It's Actually Good At)

### ✅ EXCELLENT AT

1. **Architectural Analysis**
   - "Analyze our agent runtime and suggest improvements" → 20-page deep dive
   - "Find inconsistencies between docs and code" → Identifies drift
   - "Design a new system that fits our governance" → Produces specification

2. **Large Feature Development**
   - "Build Guard Brasil landing page" → Full Vercel deployment
   - "Create Gem Hunter GitHub app" → Complete implementation
   - Multi-file changes across domains

3. **Code Quality at Scale**
   - Runs `bun run typecheck` and fixes all errors
   - Catches governance violations
   - Enforces SSOT consistency

4. **Research + Documentation**
   - "Compare us to LangChain/CrewAI" → Detailed competitive analysis (PR #30 context)
   - "What are the top concerns from governance reports?" → Extracts patterns
   - "Generate GTM positioning" → Creates messaging docs

5. **Strategic Decision Support**
   - "Should we pivot to X?" → Analyzes trade-offs
   - "What's our competitive moat?" → Identifies differentiators
   - "What should we stop doing?" → Prioritization analysis

---

### ⚠️ DECENT AT (With Guidance)

1. **Testing**
   - ✅ Creates tests when spec is clear
   - ⚠️ May miss edge cases without examples
   - Recommendation: Pair with you for test design

2. **Performance Optimization**
   - ✅ Identifies bottlenecks
   - ⚠️ Needs benchmarks to validate improvements
   - Recommendation: You decide metrics, Codex implements

3. **Integration Work**
   - ✅ Connects systems when APIs are stable
   - ⚠️ Struggles with undocumented APIs
   - Recommendation: Write integration specs first

---

### ❌ POOR AT / AVOID

1. **Quick Bug Fixes**
   - Overkill for 1-line changes
   - Wastes context on small tasks
   - Use Windsurf/Cursor instead

2. **Experimentation**
   - "What if we try X framework?" → Wastes time
   - You're paying for thinking, not exploration
   - Recommendation: Decide architecturally first, then Codex implements

3. **Routine Maintenance**
   - Updating dependencies
   - Formatting code
   - CI config tweaks
   - Use Windsurf + pre-commit hooks instead

4. **Vague Requirements**
   - "Make this better" → Will spend cycles asking clarifying questions
   - "Help with the codebase" → Too broad
   - Recommendation: Be specific about the 5-page output you want

---

## THE CODEX WORKFLOW (Optimal Process)

### Step 1: Brief (You)
**What to provide:**
- Specific goal (not "improve the code")
- Context (what you tried, what didn't work)
- Success criteria (how will we know this worked?)
- Constraints (governance rules, performance budgets, tech choices)

**Example:**
```
Goal: Build Guard Brasil landing page that drives API signups
Context: We have a working API (0.2.0), need beautiful presentation
Success: 100+ visitor→signup conversion within 30 days
Constraints: 
  - Must follow Windsurf/.windsurfrules
  - Supabase-backed for metrics
  - Mobile-first + PWA-ready
  - Link to live API demo
```

### Step 2: Codex Research (Codex)
Codex will:
- Analyze similar landing pages
- Check your existing codebase
- Propose architecture
- Ask clarifying questions (if needed)

### Step 3: Specification (You Confirm)
Review Codex's proposal:
- Does it align with your vision?
- Any changes to architecture?
- Approve or iterate

### Step 4: Implementation (Codex)
Codex creates PR with:
- Full feature implementation
- Tests
- Documentation
- Deployment instructions

### Step 5: You Test & Merge
- Run locally
- Verify behavior
- Merge if good

---

## RATE LIMITING & COSTS

**Codex has limits:**

| Constraint | Details | Implication |
|-----------|---------|------------|
| **Tokens/Day** | ~100k per day | Can't run 5 major PRs simultaneously |
| **Context Window** | 200k tokens | Can handle repos up to ~50k lines |
| **Response Time** | 5-30 min | Not for real-time feedback |
| **Rate Limit** | 1 PR per hour (soft) | Plan work in advance |
| **Cost** | Claude API pricing | ~$50-200 per major feature |

**Strategy:**
- **Batch work:** Submit 1 big request, get 1 big PR
- **Weekly cadence:** Codex on Mon/Wed/Fri, you code in between
- **Cost-effective:** Use Windsurf for 80% of work, Codex for 20% strategic work

---

## USING CODEX FOR GUARD BRASIL

### Week 1: Landing Page
```
"Create Guard Brasil landing page with:
- Hero section: 'LGPD-Compliant PII Detection'
- Live API demo (can inspect 'CPF: 123.456.789-00' text)
- Pricing table (Free 150/mo, Pro R$ 497/mo, Enterprise custom)
- Blog link
- GitHub link
- Contact form (Supabase backend)
Target: Vercel deploy, beautiful, conversion-focused
Use: React + Next.js + TailwindCSS + Supabase"
```

### Week 2: GitHub Integration for Gem Hunter
```
"Create GitHub app for Gem Hunter:
- Installable from GitHub Marketplace
- Analyzes repo on pull_request webhooks
- Returns summary: skills gaps, tech debt patterns, opportunities
- Stores results in Supabase
- Links back to gem-hunter.egos.ia.br dashboard
Success: Can install, analyze 3 public repos, see results"
```

### Week 3: Guard Brasil Consultancy Sales Package
```
"Create 'LGPD Compliance Audit' sales package:
- 1-page overview of service
- 5-page technical specification
- Pricing: R$ 25k for audit + deployment
- Success criteria document
- Proposal template
Target: Email to 10 government agencies"
```

---

## USING CODEX FOR GEM HUNTER

### Week 1: Algorithm Finalization
```
"Review and improve Gem Hunter's fingerprinting algorithm:
- Currently identifies: patterns, skills, tech debt
- Should also identify: integration opportunities, risks
- Run on 5 diverse repos (Django, React, Rust, Go, Python)
- Generate comparison: what makes each unique?
- Success: Can clearly articulate what each repo is 'about'"
```

### Week 2: Dashboard MVP
```
"Build Gem Hunter dashboard showing:
- Repos analyzed (timeline)
- Key metrics for each (skills, patterns, opportunities)
- Comparison view (repo A vs repo B)
- Export as PDF/JSON
- GitHub OAuth login
Target: gem-hunter.egos.ia.br live with 3 example repos"
```

---

## CODEX AGENT CONFIGURATION

Your optimal Codex setup (from `docs/qa/CODEX_GLOBAL_PREFERENCES_V3.md`):

```markdown
## EGOS Codex Agent Preferences

**Role:** Strategic code generator + architecture advisor

**Core Operating Principles:**
1. Investigative: Validate every claim with code evidence
2. SSOT-First: Read TASKS.md + governance docs before proposing changes
3. Risk-Aware: Prioritize governance drift, security, compliance
4. Async: Issue PRs with detailed descriptions, expect review

**Critical Files to Read:**
- TASKS.md (current priorities)
- STRATEGIC_FOCUS_PLAN_2026-04-03.md (new focus)
- docs/SSOT_REGISTRY.md (what's canonical)
- .windsurfrules (governance rules)

**Never:**
- Edit frozen zones (agents/runtime/*)
- Hardcode secrets
- Create experiments without explicit approval
- Merge without all gates passing

**Always:**
- Run `bun run typecheck` before submitting PR
- Run `bun run ssot:check` before large changes
- Include telemetry in all PRs (observability mandatory)
- Explain architectural decisions in PR body
```

---

## THIS WEEK: CODEX TASKS

Prioritize Codex in this order:

### Priority 1: Guard Brasil Landing (Do First)
```
Goal: Live landing page by EOW
Effort: 1 Codex PR
Impact: First revenue touchpoint
```

### Priority 2: Gem Hunter GitHub App (Do Second)
```
Goal: Installable + functioning by EOW
Effort: 1 Codex PR
Impact: First user acquisition mechanism
```

### Priority 3: Codex-Generated GTM Content
```
Goal: 3 blog posts + Twitter threads
Effort: 0.5 Codex PR (content only)
Impact: SEO + organic reach
```

**NOT This Week:**
- New agent experiments
- Refactoring for fun
- Exploring new frameworks
- Deep dives into competitor code

---

## ASKING CODEX EFFECTIVELY

### ❌ Bad Prompts
- "Help me with the codebase"
- "Make this better"
- "Improve performance"
- "What should we do next?"

### ✅ Good Prompts
- "Build Guard Brasil landing page that converts visitors to API signups. Success metric: 100+ conversions within 90 days. Use React + Next.js + TailwindCSS. Link to live API demo."
- "Create GitHub app that installs from Marketplace, analyzes repos for skill gaps + technical debt, returns findings as PR comment. Supabase backend for results storage."
- "Write 3 technical blog posts explaining: (1) How to detect CPF patterns safely, (2) Why LGPD compliance matters for AI, (3) Gem Hunter's fingerprinting algorithm. Each ~2000 words."

---

## SUCCESS METRIC FOR CODEX THIS QUARTER

| Metric | Target | Measure |
|--------|--------|---------|
| **Major PRs Shipped** | 4-6 | Features customers see |
| **Code Quality** | 100% typecheck pass | No style issues |
| **PR Review Time** | <1hr | You can merge quickly |
| **Developer Happiness** | 9/10 | Codex PRs feel right |

---

## FINAL: CODEX IS A TOOL, NOT A SOLUTION

**Remember:**
- Codex writes code, YOU define strategy
- Codex analyzes, YOU make decisions
- Codex implements, YOU validate
- Codex is expensive, use it for high-value work only

**This quarter:** Use Codex for Guard Brasil + Gem Hunter GTM.  
**Everything else:** Use Windsurf, it's free.

---

*Prepared by: Claude (Strategic Planning)*  
*Date: 2026-04-03 UTC*
