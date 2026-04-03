# Strategic Focus Plan — Enio Rocha 2026
> **Date:** 2026-04-03  
> **Purpose:** Consolidate vision, identify moat, and execute focused GTM  
> **Status:** PLANNING PHASE

---

## THE PROBLEM YOU'RE SOLVING

You built 10+ MVPs, 4 production apps, powerful tools, but **lacked focus**. Result: scattered revenue, fragmented narrative, hard to explain value to market.

**This plan:** Identify the ONE differentiator that big tech can't easily attack, then double down.

---

## YOUR UNIQUE MOAT (What Big Tech Struggles With)

### Three Layers of Defensibility

#### Layer 1: **Brazilian Context Obsession**
- **Guard Brasil:** PII detection optimized for BR patterns (CPF, RG, phone, address, government IDs)
- **ATRiAN:** Ethical validation framework that understands BR legal context (LGPD, data residency, cultural nuance)
- **Local Data Models:** Vana/Ocean paradigm (personal data sovereignty) vs GenAI-as-commodity
- **Big Tech Gap:** OpenAI/Google/Anthropic build for **global**. You build for **BR specificity**.

**Why it matters:** Brazil's corporate/government sector is desperate for LGPD-compliant AI. They can't use Claude API directly (data residency issues). Guard Brasil = immediate fit.

---

#### Layer 2: **Governed Agents, Not Just Orchestration**
- **EGOS Kernel:** Governance infrastructure that other agent frameworks (LangGraph, CrewAI, AutoGen) don't have
- **SSOT Enforcement:** Rules are **infrastructure**, not configuration
- **Frozen Zones:** Core execution engine that even AI can't corrupt
- **Mycelial Sync:** Multi-repo governance propagation via symlinks
- **Big Tech Gap:** They build agent APIs. You built agent **governance systems**.

**Why it matters:** Production teams running 5+ agents need boundaries, audit trails, version control. EGOS is the only framework with "governance-first" DNA.

---

#### Layer 3: **Gem Hunter + Eagle Eye: Intelligence Layer**
- **Gem Hunter:** Discovers what matters in any codebase (patterns, technical debt, skills gaps)
- **Eagle Eye:** Finds government opportunities + market signals automatically
- **Together:** A data engine for **decision-making**, not just code generation
- **Big Tech Gap:** They optimize for how agents *generate* code. You optimized for what agents *discover*.

**Why it matters:** Business value isn't in agents that write code. It's in agents that find what to build and ensure it's done safely.

---

### **THE MOAT IN ONE SENTENCE:**

> You're the only one building **Governed AI agents designed for Brazil's regulatory reality + intelligence engines that discover where to apply them.**

Big Tech can't easily copy this because:
1. ❌ They don't understand BR compliance deeply enough (not a priority market for them)
2. ❌ They don't have "governance" culture (it's overhead to them)
3. ❌ They won't spend engineering cycles on local patterns (not global scale)

---

## WHAT TO KILL / DEPRIORITIZE IMMEDIATELY

| Product | Status | Reason | Action |
|---------|--------|--------|--------|
| **Carteira Livre** | ✅ Revenue-generating | But: narrow TAM (driving schools) | Keep running, don't expand |
| **Santiago Delivery** | ✅ Deployed | But: commodity business | Sunset by 2026-Q2 |
| **Forja ERP** | MVP 80% | But: niche metalworking | Freeze, revisit if Guard Brasil open doors |
| **852 Chatbot** | Deployed | But: one-customer focus | Keep warm, seek 1-2 more pilots |
| **egos-lab experiments** | 29 agents | But: scattered research | Keep 3 "best" agents, archive rest |

**Why:** Diffused effort kills focus. Each killed product = 20 hours/month freed.

---

## FOCUS: THE TWO PILLARS

### **PILLAR 1: GUARD BRASIL** ⚖️
**What it is:** PII detection + LGPD compliance engine  
**Status:** Production-ready (0.2.0, Supabase-backed, API live)  
**Revenue Model:** SaaS API (per-request + monthly tier)  

#### Revenue Paths
1. **Path A: Self-Service API** (Immediate)
   - Free tier: 150 requests/month
   - Pro: R$ 497/month (10k requests)
   - Enterprise: Custom
   - **Target:** 10 customers in 90 days = R$ 50k/month recurring

2. **Path B: Embedded (White-Label)** (Q2 2026)
   - License to government agencies + healthcare
   - Stripe integration + hosted instance per customer
   - **Target:** 2-3 enterprise deals = R$ 100-500k/year each

3. **Path C: Consultancy** (Immediate)
   - "LGPD Audit + Guard Brasil deployment" package
   - 1-2 weeks, R$ 20-50k per client
   - **Target:** 2 pilots in 60 days

#### Metrics (Next 90 Days)
- **Landing:** guard-brasil landing page (Vercel, beautiful)
- **SEO:** "Detecção de PII Brasil" + "Conformidade LGPD"
- **Content:** 2-3 technical blog posts (ATRiAN, masking strategies, BR patterns)
- **GTM:** 10 API signups, 2 consultancy conversations, 1 POC with government agency

---

### **PILLAR 2: GEM HUNTER** 🔍
**What it is:** Codebase intelligence engine (patterns, gaps, opportunities)  
**Status:** 1.0 deployed, data pipeline working, P1 repos being analyzed  
**Revenue Model:** SaaS intelligence platform (per-repo or per-month)  

#### Revenue Paths
1. **Path A: Developer Tool (B2D)** (Immediate)
   - Self-serve: "Analyze my repo, find skills gaps"
   - Free: 1 analysis/month
   - Pro: R$ 99/month (unlimited repos + integrations)
   - **Target:** 100 developers paying = R$ 10k/month by Q3

2. **Path B: Team/Enterprise Intelligence** (Q2 2026)
   - "Understand your engineering team's strengths"
   - Dashboard + reports + API access
   - R$ 2-5k/month per team
   - **Target:** 5 teams = R$ 50-250k/year

3. **Path C: Data Licensing** (Q3 2026)
   - Anonymized insights: "What patterns exist in top 1000 JS projects?"
   - Reports sold to tech consultancies
   - **Target:** 5 reports/year, R$ 10-20k each

#### Metrics (Next 90 Days)
- **Landing:** gem-hunter.egos.ia.br (beautiful dashboard)
- **Integration:** GitHub app + CLI tool
- **Content:** 3 case studies (public repos analyzed)
- **GTM:** 20 free trial signups, 5 paying customers, 1 enterprise conversation

---

## COMPETITIVE POSITIONING (Your 30-Second Pitch)

### For Guard Brasil
> **"LGPD-compliant PII detection for Brazil's digital government. Built by the same team that handles 852 intelligence (police data) safely. If you're processing BR citizen data, you need us before you need anything else."**

### For Gem Hunter
> **"Codebase fingerprinting without the fluff. Find what matters: skills gaps, technical debt, patterns. Used internally to scale 5 government platforms. Now open for teams that want to understand their engineering reality."**

### For EGOS (Underlying Narrative)
> **"Governed agents + intelligence engines. The infrastructure that lets AI solve problems without creating compliance disasters."**

---

## THE 90-DAY EXECUTION PLAN

### **MONTH 1: FOUNDATION (APR 1-30)**

**Week 1: Landing Pages & SEO**
- [ ] Deploy Guard Brasil landing (guard-brasil-website GitHub → Vercel)
- [ ] Deploy Gem Hunter landing (gem-hunter-website GitHub → Vercel)
- [ ] Write 1 Guard Brasil blog post: "How to Detect CPF Patterns Safely"
- [ ] Write 1 Gem Hunter blog post: "5 Patterns We Found in Top 1000 GitHub Projects"
- **Effort:** 16 hours | **Owner:** You + Claude  
- **Success Metric:** Each landing gets 100+ unique visitors

**Week 2: API Hardening**
- [ ] Complete Guard Brasil API tests (currently 80%)
- [ ] Add rate limiting + quota management UI
- [ ] Write API docs (Swagger/OpenAPI)
- [ ] Deploy to production + smoke test
- **Effort:** 12 hours | **Owner:** You + Claude (coding)  
- **Success Metric:** API passes Codex validation (GH-041 smoke tests)

**Week 3: Gem Hunter MVP**
- [ ] Finalize repo fingerprinting algorithm
- [ ] Deploy first version to gem-hunter.egos.ia.br
- [ ] Write GitHub integration (app + webhook)
- [ ] Create 3 example analyses (public repos)
- **Effort:** 20 hours | **Owner:** You + Claude  
- **Success Metric:** GitHub app works, 5 test repos analyzed successfully

**Week 4: GTM Setup**
- [ ] Guard Brasil: Send API keys to 3 BR tech newsletter channels
- [ ] Gem Hunter: Submit to Hacker News + Reddit /r/programming
- [ ] Create Twitter thread comparing EGOS to LangChain/CrewAI
- [ ] Email 10 potential customers (government agencies) for Guard Brasil
- **Effort:** 8 hours | **Owner:** You  
- **Success Metric:** 20 API signups, 50 Gem Hunter free trials

---

### **MONTH 2: TRACTION (MAY 1-31)**

**Week 5-6: Customer Conversations**
- [ ] Schedule 5 calls with Guard Brasil API users
- [ ] Schedule 3 calls with government agencies (LGPD audit pitch)
- [ ] Conduct 2 Gem Hunter user interviews
- [ ] Refine messaging based on feedback
- **Effort:** 8 hours  
- **Success Metric:** 1 Guard Brasil POC, 1 Gem Hunter expansion

**Week 7: Eagle Eye Integration**
- [ ] Connect Guard Brasil to Eagle Eye (mask sensitive data in scraped opportunities)
- [ ] Deploy daily pipeline
- [ ] Create "Government Opportunities + Data Safe" marketing angle
- **Effort:** 6 hours  
- **Success Metric:** 1 government agency inbound inquiry

**Week 8: Paid Traffic**
- [ ] Start Google Ads for "LGPD compliance Brazil" + "PII detection"
- [ ] Run LinkedIn outreach to security teams + GRC officers
- [ ] Launch Twitter campaign (#LGPD #GuardBrasil)
- **Effort:** 4 hours  
- **Success Metric:** 10 qualified leads per week

---

### **MONTH 3: REVENUE (JUN 1-30)**

**Week 9-10: First Paid Customer**
- [ ] Convert 1 Guard Brasil API customer to paid tier (R$ 497/month)
- [ ] Convert 2 Gem Hunter users to Pro tier (R$ 99/month each)
- [ ] Close 1 consultancy deal (LGPD audit, R$ 25k)
- [ ] Launch enterprise sales process (3+ government targets)
- **Effort:** 12 hours  
- **Success Metric:** R$ 20k MRR + R$ 25k consultancy

**Week 11-12: Expansion**
- [ ] Document customer success stories
- [ ] Expand Guard Brasil to 10 paid API users
- [ ] Expand Gem Hunter to 20 Pro subscribers
- [ ] Announce EGOS open source + governance story
- [ ] Submit to Product Hunt (Gem Hunter)
- **Effort:** 16 hours  
- **Success Metric:** R$ 35k+ MRR, 1 enterprise POC in flight

---

## WHAT TO FOCUS ON THIS WEEK (APR 3-9)

### Priority Order

1. **Guard Brasil Landing Page** (4 hours)
   - Deploy Vercel instance with live API demo
   - Add GitHub gist example: "Detect CPF in this text"
   - Link to API docs + pricing

2. **Gem Hunter GitHub App** (6 hours)
   - Make it installable from GitHub Marketplace
   - Run it on 3 public repos as examples
   - Link to gem-hunter.egos.ia.br dashboard

3. **Codex Deep Dive** (2 hours)
   - Understand Codex's capabilities fully
   - Document how to use it for Guard Brasil + Gem Hunter development
   - Create Codex.md agent preferences

4. **Twitter/Social Launch** (2 hours)
   - Write 3 tweets explaining Guard Brasil + Gem Hunter
   - Post to your timeline
   - Monitor engagement

5. **Schedule Customer Conversations** (1 hour)
   - Email 5 government agencies: "Free LGPD audit"
   - Email 3 tech team leads: "Free codebase analysis"

**Total Effort:** 15 hours  
**Expected Output:** Live landing pages + initial traction

---

## REVENUE PROJECTION (Conservative)

### Year 1 (2026)
- **Guard Brasil:** 15 paying API customers × R$ 497/mo = R$ 7.5k/mo (staggered)
- **Guard Brasil Consultancy:** 2 deals × R$ 25k = R$ 50k (one-time)
- **Gem Hunter:** 20 Pro subscribers × R$ 99/mo = R$ 2k/mo
- **Carteira Livre:** Existing R$ 2-5k/mo
- **Total Year 1:** R$ 50k upfront + R$ 100k+ recurring = **R$ 150k+**

### Year 2 (2027) — If Focused
- **Guard Brasil:** 50 API customers × R$ 497 = R$ 25k/mo
- **Guard Brasil Enterprise:** 3 deals × R$ 100k = R$ 300k/year
- **Gem Hunter:** 100 Pro × R$ 99 = R$ 10k/mo
- **Total Year 2:** **R$ 600k+ ARR**

---

## THINGS TO STOP DOING IMMEDIATELY

| Task | Why | By When |
|------|-----|---------|
| Maintaining 29 egos-lab agents | Distraction | EOW |
| "Generic" agent experiments | No revenue path | EOW |
| Unfocused Codex PRs | Kill the backlog | EOW |
| Long-form documentation | Write only GTM-critical docs | EOW |
| Deep technical debt reduction | Can wait | Q3 |

---

## CODEX STRATEGY

**Codex Role:** Strategic code generation + QA architect  
**NOT:** Exploration, experimentation, side projects

**Focused Prompts for Codex:**
1. "Help build Guard Brasil landing page (Vercel)"
2. "Help build Gem Hunter GitHub app"
3. "Generate Eagle Eye + Guard Brasil integration"
4. "Help write marketing copy + blog posts"
5. "Help build customer dashboard for both products"

**NOT to ask Codex:**
- Explore new frameworks
- Refactor for fun
- Experiment with agent patterns
- Fix "nice to have" issues

---

## SUCCESS METRICS (90 Days)

| Metric | Target | Current |
|--------|--------|---------|
| Guard Brasil API signups | 20 | 3 |
| Guard Brasil paid customers | 3 | 0 |
| Gem Hunter free trials | 50 | ~5 |
| Gem Hunter paid subscribers | 5 | 0 |
| GitHub agencies contacted | 10 | 0 |
| Twitter followers | 500 | ~50 |
| Blog posts published | 5 | 0 |
| Revenue/month (recurring) | R$ 10k | R$ 0 |

---

## DECISION POINT: APR 15

On April 15, you must decide:
- **Are we really doing this focused approach?**
- **Or are we going back to scattered work?**

If YES: Commit to this plan and follow through.  
If NO: That's okay, but own the decision that growth will be slower.

---

## FINAL WORD

You have built:
- ✅ World-class governance infrastructure (EGOS)
- ✅ Brazil-specific compliance engine (Guard Brasil + ATRiAN)
- ✅ Codebase intelligence platform (Gem Hunter)
- ✅ Market signals detector (Eagle Eye)
- ✅ Production data in 4+ SaaS apps

**The problem wasn't lack of ideas. It was lack of focus.**

**This plan is your focus.**

You don't need to build more. You need to **sell what you have** and **double down on what's unique.**

Guard Brasil + Gem Hunter = your moat.

Everything else is supporting infrastructure.

---

**Now: Pick the first 15-hour sprint above and START TODAY.**

**Target:** One live landing page + one functional tool by end of week.

---

*Prepared by: Claude (Strategic Planning)*  
*Date: 2026-04-03 UTC*  
*Status: READY FOR EXECUTION*
