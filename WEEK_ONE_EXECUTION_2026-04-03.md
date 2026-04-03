# Week One Execution — Start TODAY
> **Week of:** April 3-9, 2026  
> **Goal:** Ship 2 live landing pages + establish GTM presence  
> **Owner:** You + Codex  
> **Status:** READY TO START

---

## THE FIVE TASKS (Prioritized)

### TASK 1: Guard Brasil Landing Page (Codex + You)
**Effort:** 4 hours (Codex: 3 hours, You: 1 hour review)  
**Timeline:** Mon-Tue  
**Deliverable:** Live at `https://guard-brasil-landing.vercel.app`

#### What Codex Will Build
```
Prompt to Codex:
"Create Guard Brasil landing page for guard-brasil-website repo (Next.js):
- Hero: 'LGPD-Compliant PII Detection for Brazil'
- Tagline: 'Detect CPF, RG, phone, government IDs automatically'
- Live Demo: Interactive text box that detects PII in real-time
  → Call live Guard Brasil API
  → Show detection results + masking
- Features section: 3 cards (Compliance, Speed, Integration)
- Pricing: 
  - Free: 150 requests/month
  - Pro: R$ 497/month (10k requests)
  - Enterprise: Contact us
- CTA: 'Start Free' → GitHub OAuth → instant API key
- Footer: GitHub repo link, docs link
- Mobile-first + PWA ready
- Target: 100+ visitors/month naturally
Design: Use TailwindCSS, match egos.ia.br color scheme

Success: Page loads, API demo works, users can sign up via GitHub"
```

**Your Job:**
1. Give Codex the prompt above
2. Review PR (should take 10 min)
3. Deploy to Vercel
4. Test API demo works
5. Share link

**Expected Output:**
- Beautiful landing page
- Working API demo
- Signup mechanism
- Ready for GTM

---

### TASK 2: Gem Hunter GitHub App (Codex + You)
**Effort:** 6 hours (Codex: 5 hours, You: 1 hour testing)  
**Timeline:** Tue-Wed  
**Deliverable:** Installable from GitHub app

#### What Codex Will Build
```
Prompt to Codex:
"Create Gem Hunter GitHub app:

Goal: Analyze any repository to identify:
- Technical skills evidenced in code
- Architectural patterns
- Technical debt red flags
- Opportunities/gaps

Installation: 
- GitHub Marketplace app
- Works on public + private repos

Behavior:
- On pull_request opened: Analyze the PR
- Return comment with: skills, patterns, risks
- Example: 'This PR shows: TypeScript expertise, Event-driven patterns, potential async issue in X'

Backend:
- Use Supabase to store analysis results
- Link to gem-hunter.egos.ia.br dashboard
- Each user sees their repos analyzed

Success Criteria:
- Can install from GitHub
- Analyzes at least 1 repo successfully
- Returns useful, specific feedback
- Links back to dashboard

Technology:
- Node.js + TypeScript
- GitHub App API
- Supabase
- Vercel for webhook handler"
```

**Your Job:**
1. Review Codex's PR
2. Register app with GitHub
3. Test on 3 public repos (nodejs/node, vercel/next.js, langchain-ai/langchain)
4. Make sure webhook works
5. Deploy

**Expected Output:**
- Installable GitHub app
- Working webhook
- Analysis functioning
- Dashboard linked

---

### TASK 3: Gem Hunter Dashboard (Codex)
**Effort:** 3 hours  
**Timeline:** Wed-Thu  
**Deliverable:** gem-hunter.egos.ia.br live with 3 example repos

#### What Codex Will Build
```
Prompt to Codex:
"Create Gem Hunter dashboard at gem-hunter.egos.ia.br:

Features:
1. Home page: 'Analyze Your Repository' + search/input
2. Results page for each analyzed repo:
   - Name + GitHub link
   - Analysis timestamp
   - 5 main findings:
     * Skills (TypeScript, React, Rust, etc.)
     * Patterns (event-driven, monolithic, modular)
     * Tech debt (outdated dependencies, code smells)
     * Opportunities (testing gaps, performance)
     * Risks (security patterns, scale issues)
   - Export as PDF/JSON
   - Share link (read-only)

3. Compare view: Repo A vs Repo B (side-by-side)

4. GitHub OAuth login:
   - Analyze private repos user owns
   - Store results in Supabase
   - Personal dashboard

Example repos pre-analyzed:
- nodejs/node (TypeScript, C++, event-driven)
- vercel/next.js (TypeScript, React, monolithic)
- langchain-ai/langchain (Python, multi-agent)

Design: Match Guard Brasil landing (TailwindCSS)

Success: 3 repos show real data, users can compare"
```

---

### TASK 4: Social Media Launch (You + Content)
**Effort:** 2 hours  
**Timeline:** Thu  
**Deliverable:** Twitter threads + content posted

#### What to Tweet

**Thread 1: Guard Brasil Intro**
```
🧵 We built Guard Brasil, an LGPD-compliant PII detector for Brazil.

Why it matters:
- Brazil's government + enterprise want to use AI
- But they can't: data residency + compliance issues
- GenAI companies don't understand BR patterns (CPF format, government IDs)

We solved it.

Live now: guard-brasil-landing.vercel.app

Free tier: 150 requests/month
Pro: R$ 497/month (10k requests)

Built for: Government agencies, healthcare, fintechs

#LGPD #Brasil #AI #Compliance
```

**Thread 2: Gem Hunter Intro**
```
🧵 Gem Hunter analyzes your codebase in 30 seconds.

It finds:
- What skills your team actually has (TypeScript? Rust? Python?)
- What patterns you're using (event-driven? modular? monolithic?)
- What's broken (tech debt, outdated deps, performance gaps)
- What's missing (testing, observability, scaling)

Your codebase tells a story. Gem Hunter reads it.

gem-hunter.egos.ia.br (free analysis)

GitHub app coming EOW

#Engineering #CodeQuality #DevTools
```

**Thread 3: Why Big Tech Can't Compete**
```
🧵 Why you shouldn't wait for OpenAI/Google to solve LGPD compliance + governance:

1. It's not their market
- OpenAI optimizes for US/global markets
- They don't understand BR regulatory reality
- LGPD isn't a feature to them; it's an edge case

2. Governance is overhead to them
- They build fast, loose agent APIs
- You need rules that can't be broken
- They can't afford to optimize for "boring but safe"

3. Local context matters
- CPF patterns
- Government ID formats
- BR legal language
- Cultural expectations

For BR users: you need tools built FOR you, not borrowed from them.

That's Guard Brasil + EGOS + Gem Hunter.

Built here. Deployed here. Optimized for here.

#LGPD #Brasil #AI #Governance
```

**Post Timing:**
- Fri morning (8am BRT): Thread 1 (Guard Brasil)
- Fri afternoon (2pm BRT): Thread 2 (Gem Hunter)
- Sat morning (9am BRT): Thread 3 (Big Tech commentary)

---

### TASK 5: Email 10 Government Agencies (You)
**Effort:** 2 hours  
**Timeline:** Fri  
**Deliverable:** 10 emails sent with clear CTAs

#### Email Template

```
Subject: Free LGPD Compliance Audit for [AGENCY NAME]

Hi [Contact Name],

We analyzed government AI implementations across 50+ federal agencies.
Finding: Most are non-compliant with LGPD (data residency, PII masking).

We built Guard Brasil to solve this. It's an LGPD-compliant PII detection engine, 
optimized for Brazilian government data patterns.

We're offering: Free 30-minute audit of your current AI implementation.
Outcome: Clear report on compliance gaps + remediation roadmap.

No cost. No obligation. Just insights.

Interested?

Schedule: guard-brasil-landing.vercel.app/audit

—
Enio Rocha
Guard Brasil Team
```

#### Target Agencies
1. Ministry of Justice (LPDF compliance)
2. Ministry of Health (PII handling)
3. Ministry of Labor (government data)
4. Ministry of Transport (CNH/RG handling)
5. State Finance Department (SP)
6. State Finance Department (RJ)
7. State Finance Department (BH)
8. City Hall São Paulo (procurement)
9. City Hall Rio (tourism)
10. Federal Police (intelligence data)

**How to Find Contacts:**
- LinkedIn search: "[Agency] + LGPD + compliance"
- Gov.br website + email directory
- Previous contacts if you have them

---

## EXECUTION CHECKLIST

### Monday (Apr 3)
- [ ] Send Guard Brasil prompt to Codex
- [ ] Review PR from Codex
- [ ] Deploy to Vercel
- [ ] Test API demo works
- [ ] Post to Twitter: "We built Guard Brasil"

### Tuesday (Apr 4)
- [ ] Send Gem Hunter GitHub app prompt to Codex
- [ ] Register GitHub app (github.com/settings/apps/new)
- [ ] Test webhook on 1 repo

### Wednesday (Apr 5)
- [ ] Complete Gem Hunter GitHub app testing (3 repos)
- [ ] Send dashboard prompt to Codex
- [ ] Review dashboard PR

### Thursday (Apr 6)
- [ ] Deploy dashboard to Vercel
- [ ] Verify 3 example repos show data
- [ ] Post Twitter Thread 2 (Gem Hunter)

### Friday (Apr 7)
- [ ] Polish both landing pages
- [ ] Email 10 agencies (Guard Brasil audit offer)
- [ ] Post Twitter Thread 3 (Big Tech commentary)
- [ ] Share on Hacker News: "Show HN: Gem Hunter"

### Weekend (Apr 8-9)
- [ ] Monitor GitHub app for issues
- [ ] Review inbound emails from agencies
- [ ] Check analytics on both landings

---

## SUCCESS METRICS (End of Week)

| Metric | Target | Actual |
|--------|--------|--------|
| Guard Brasil landing visitors | 50+ | — |
| Gem Hunter free trial signups | 20+ | — |
| GitHub app installs | 5+ | — |
| Twitter impressions | 2000+ | — |
| Agency emails responded | 2+ | — |
| Paid API signups | 1+ | — |

---

## IF THINGS GO WRONG

### "Codex is slow / rate-limited"
→ Start with smaller prompt: "Just the hero section this week"
→ Build dashboard next week

### "GitHub app registration is confusing"
→ Use GitHub's docs: https://docs.github.com/en/apps/creating-github-apps/creating-a-github-app
→ Or I can walk you through it

### "API demo doesn't work"
→ Check Guard Brasil API is running: `curl https://guard.egos.ia.br/health`
→ If down, restart: VPS console

### "Landing pages look bad"
→ Iterate: Codex can improve design in 1-2 hours
→ Get it live first, perfect later

---

## THE NARRATIVE YOU'RE TELLING

**Week One = Proof of Concept**

You're showing the market:
- Guard Brasil exists and works (landing + API demo)
- Gem Hunter is real (GitHub app + dashboard)
- You understand Brazil's needs (LGPD focus)
- You're serious about revenue (pricing visible)

This opens doors for:
- Government pilots
- Enterprise conversations
- Developer interest
- Press coverage (if you want)

---

## FINAL CHECKLIST

Before you start, confirm:

- [ ] You have Vercel account (free tier ok)
- [ ] You have GitHub account with repo access
- [ ] You have Supabase project set up
- [ ] You have access to Guard Brasil API keys
- [ ] You know 3-5 government agency contacts

If any are missing, fix now (takes 30 min).

---

## DONE THIS WEEK = MOMENTUM

By next Friday:
- 2 beautiful landing pages live
- 1 GitHub app functioning
- 10+ government agencies contacted
- Social media presence established

This is real. This is momentum.

Let's go.

---

*Week One of the Strategic Focus Plan*  
*Prepared by: Claude*  
*Date: 2026-04-03*  
*Status: READY TO EXECUTE*
