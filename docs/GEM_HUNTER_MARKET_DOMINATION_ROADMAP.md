# Gem Hunter — Market Domination Roadmap (2026-04-08)

> **Based on:** Competitive research + feature gap analysis + newsletter strategy analysis
> **Target:** $30K MRR by 2026-06-30 (90 days)
> **Path:** Multi-source discovery → Distribution → Community → B2B security
> **Owner:** Enio (researcher mindset validated — Gem Hunter aligns perfectly)

---

## 1. The Opportunity (Why Now)

The GitHub repo discovery market is **fragmented and immature:**
- **OSSInsight** (100K users) = analytics, not curation
- **Trendshift** (50K users) = better trending, not quality
- **SimilarRepos** (259 users) = context-aware, zero scale
- **Console.dev** (50K users) = editorial, not discovery
- **No one** combines discovery + quality + distribution + community

**Market signal:** 6 competitors means demand exists, none have solved it.

**Gem Hunter's unfair advantage:**
- Multi-dimensional scoring (9 factors) ✅ — only Gem Hunter has this
- Multi-source (6 sources: GitHub, arXiv, npm, HN, Reddit, X) ✅ — competitors are single-source
- Autonomous (runs 2-4d without human input) ✅ — others are manual
- Open source + MIT ✅ — competitors are proprietary or closed
- Already processing 165+ gems/run ✅ — scale exists

**Why distribution matters more than discovery:**
- TLDR: 500K subscribers, mid-tier content quality, #1 in category
- Bytes: 250K subscribers, JavaScript-focused, mid-tier quality
- Console.dev: 50K subscribers, elite quality, high engagement
- Pattern: **Distribution > quality of discovery algorithm**

**Path to $30K MRR:**
1. **Weeks 1-2:** Weekly digest newsletter (email list)
2. **Weeks 2-3:** Community voting + bookmark lists
3. **Weeks 3-4:** Slack/Discord bot for team consumption
4. **Weeks 4-6:** B2B security tier (supply-chain risk)
5. **Weeks 6-12:** Paid tiers (freemium)

---

## 2. Competitive Positioning

| Competitor | Does better | Gem Hunter owns |
|------------|------------|-----------------|
| **OSSInsight** | GitHub analytics, NLP queries | Multi-dimensional quality scoring, multi-source |
| **Trendshift** | GitHub trending algorithm | Community context, supply-chain risk |
| **Console.dev** | Editorial taste (50K audience) | Autonomous discovery, open source |
| **Libraries.io** | Cross-language packages | Repo quality signals (not just deps) |
| **SimilarRepos** | On-page context | Scale + community + quality tiers |
| **TLDR/Bytes** | Newsletter distribution | Customizable + quality-first (not hype) |

**Gem Hunter's unique position:**
> *"The discovery platform for developers who care more about shipping than trends. Multi-source, quality-scored, autonomous, open source."*

**Brand thesis:** Gem Hunter = *"What HN + TLDR + GitHub Trending should have been."*

---

## 3. Phased Roadmap to $30K MRR

### PHASE A: Distribution Foundation (Weeks 1-2, 4h/day)

**Goal:** Get 500 email subscribers week 1, 2K by week 4.

**GH-074: Weekly Digest Email Pipeline**
- [ ] Create `scripts/gem-hunter-digest.ts` — aggregates top 3-5 repos/week by score
- [ ] Write 1-line "why it matters" for each (curated tone, not marketing)
- [ ] Send via Substack (free tier, no code required) on Thursday 08:00 UTC
- [ ] Subject: "Gem Hunter Weekly #001 — [trending category]"
- [ ] CTA: "Find more at gemhunter.egos.ia.br" (landing page needed)

**GH-075: Landing Page (gemhunter.egos.ia.br)**
- [ ] Deploy `apps/egos-site` public page (reuse Timeline architecture)
- [ ] Design: 3-section page
  1. "What is Gem Hunter?" (2 paragraphs)
  2. "This week's gems" (latest 3 items from digest)
  3. "Subscribe" button → Substack form
- [ ] Caddy routing: gemhunter.egos.ia.br → egos-site:3070/gem-hunter

**GH-076: Substack Newsletter Setup**
- [ ] Create substack.com/gemhunter
- [ ] First 5 emails: manual writes about the engine + philosophy
- [ ] Auto-send digest from CRON (03:00 UTC) → webhook → Substack API

**Metrics to track:**
- Email open rate (baseline: 20-25% for dev newsletters)
- Click-through to website
- Signup conversion

**Revenue:** $0 this phase (list-building)

---

### PHASE B: Community Features (Weeks 2-3, 6h/day)

**Goal:** Launch voting + lists. Shift from "Gem Hunter recommends" → "Developers love."

**GH-077: Bookmark Lists & Voting**
- [ ] New Supabase tables: `gem_lists` (user-created lists), `gem_votes` (upvotes)
- [ ] API endpoints:
  - `POST /api/gems/{id}/upvote` (togglable)
  - `POST /api/lists` (create list)
  - `POST /api/lists/{id}/gems/{gem_id}` (add gem to list)
  - `GET /api/gems?sort=votes_week` (trending by community vote)
- [ ] Auth: email-only signup (Firebase or Supabase Auth)

**GH-078: Dashboard Voting UI**
- [ ] Add 👍 button to each gem card (shows live vote count)
- [ ] "Top voted this week" section on home
- [ ] "Your bookmarks" tab (MY_LISTS page)
- [ ] Public lists: show top 10 community lists (e.g., "ML Ops Tools", "Rust Frameworks")

**GH-079: "Awesome Gems" Public List (on GitHub)**
- [ ] New repo: github.com/enioxt/awesome-gems
- [ ] Weekly top-voted repos → curate into lists by category
- [ ] Community can submit PRs with new repos + vote counts
- [ ] Pattern: copy awesome-github-projects but add **quality score** as a column

**Metrics to track:**
- List creation rate (target: 100+ lists by week 3)
- Vote count trending
- GitHub stars on awesome-gems

**Revenue:** $0 this phase (engagement building)

---

### PHASE C: Distribution Multipliers (Weeks 3-4, 4h/day)

**Goal:** Reach developers where they are (Slack, Discord, teams).

**GH-080: Slack Bot Integration**
- [ ] Slash command: `/gem-hunter trending [language]`
- [ ] Returns: Top 3 gems for language + vote counts
- [ ] Button: "View on web"
- [ ] Setup: `scripts/slack-bot.ts` using Bolt framework
- [ ] Install URL: gemhunter.egos.ia.br/slack/install

**GH-081: Discord Bot**
- [ ] Command: `!gems [language]`
- [ ] Embed format (rich Discord cards)
- [ ] Button: "Vote" + "Save"
- [ ] Setup: `scripts/discord-bot.ts` using discord.py or discord.js

**GH-082: Telegram Channel + Bot**
- [ ] Channel: @gem_hunter_weekly (auto-post digest)
- [ ] Bot: @gem_hunter_bot — `/trending [lang]`, `/random`, `/subscribe`
- [ ] Setup: `scripts/telegram-bot.ts` using telegraf

**Metrics to track:**
- Slack/Discord installs (target: 500+)
- Telegram subscribers (target: 1K+)
- DAU (daily active users) from each platform

**Revenue:** $0 this phase (platform reach)

**Total distribution reach by week 4:** Email (2K) + Slack (500 teams) + Discord (300+) + Telegram (1K+) = **4K+ developers aware of Gem Hunter**

---

### PHASE D: Monetization (Weeks 5-6, 6h/day)

**Goal:** Launch freemium tiers. Target: 200 paid customers @ $15/mo avg = $3K/mo baseline.

**GH-083: Stripe Billing Infrastructure**
- [ ] Supabase tables: `subscriptions` (user_id, tier, cycle, stripe_id)
- [ ] Stripe setup: 3 tiers:
  1. **Free:** 10 API calls/day, 5 lists, vote
  2. **Pro:** 100 API calls/day, unlimited lists, $15/mo
  3. **Team:** 1000 API calls/day, team workspace, Slack/Discord sync, $49/mo

**GH-084: Supply-Chain Risk Tier (B2B)**
- [ ] New endpoint: `GET /api/gems/{id}/supply-chain-risk`
- [ ] Queries: Dependencies.dev API, shows:
  - Vulnerable transitive dependencies
  - License compatibility issues
  - Last dependency update age
  - Maintenance health
- [ ] B2B tier: $99/mo "Security" (unlimited calls + risk scoring)
- [ ] Target: 10 companies = $990/mo

**GH-085: Dashboard Pro Features**
- [ ] Team workspace: invite members, shared bookmarks
- [ ] API key dashboard (shows usage, regenerate)
- [ ] Webhook API (repos matched certain criteria → POST to your server)
- [ ] CSV export (top 100 gems of month)
- [ ] Slack/Discord sync (auto-post discoveries to team channel)

**Pricing model:**
```
Free           $0/mo   10 API calls/day
Pro            $15/mo  100 API calls/day + team workspace
Team           $49/mo  Unlimited + Slack/Discord sync
Security (B2B) $99/mo  Risk scoring + compliance reporting
```

**Revenue targets:**
- Week 5: 50 Pro signups @ $15 = $750/mo (+0 churn)
- Week 6: 100 Pro + 10 Team + 2 Security = $1,500 + $490 + $198 = **$2,188/mo**
- By week 12: 300 Pro + 30 Team + 15 Security = $4,500 + $1,470 + $1,485 = **$7,455/mo**

**Path to $30K MRR:** Scale Pro to 1,500 users (1.5% penetration of 100K addressable market) + 100 Team seats + 50 Security = $22.5K + $4.9K + $4.95K = **$32.35K MRR by month 6**

---

## 4. Feature Priorities (for implementation)

### Must-Have (Weeks 1-4)
- [ ] GH-074: Weekly digest email
- [ ] GH-075: Landing page
- [ ] GH-077: Voting + lists
- [ ] GH-080: Slack bot
- [ ] GH-083: Stripe billing

### Should-Have (Weeks 5-6)
- [ ] GH-078: Dashboard voting UI
- [ ] GH-081: Discord bot
- [ ] GH-082: Telegram bot
- [ ] GH-084: Supply-chain risk scoring

### Nice-to-Have (Later)
- [ ] GH-085: Team workspace
- [ ] GH-079: Awesome-gems public list
- [ ] Chrome extension (like SimilarRepos)
- [ ] Webhook API

---

## 5. Why This Works for Enio

### Aligns with Researcher Mindset
- ✅ Discovery (what Gem Hunter does best) > distribution
- ✅ Multi-source (research from 6 places) — familiar
- ✅ Autonomous agents (script does the heavy lifting) — leverages existing skills
- ✅ Open source first (Gem Hunter is MIT) — no proprietary/sales overhead
- ✅ Quality over hype (9-factor scoring) — research-grade, not marketing-grade

### Solves the GTM Gap
- ✅ Newsletter = passive distribution (not sales)
- ✅ Community voting = self-selection (builders find themselves)
- ✅ Freemium = no cold outreach needed
- ✅ B2B security = inbound (companies seek compliance tools)

### Leverages Existing EGOS Infrastructure
- ✅ Reuses Timeline architecture (React + Supabase)
- ✅ Reuses Hermes/x-reply-bot infrastructure (distribution)
- ✅ Reuses Guard Brasil (can extend to scan gems for secrets)
- ✅ Reuses Telegram/Slack bots (already connected)

---

## 6. Key Success Metrics

| Metric | Week 2 | Week 4 | Week 8 | Week 12 |
|--------|--------|--------|--------|---------|
| **Newsletter subscribers** | 500 | 2K | 5K | 10K |
| **Community lists created** | 20 | 100 | 300 | 500 |
| **Slack/Discord installs** | 50 | 500 | 1K | 2K |
| **Paid customers** | 0 | 50 | 150 | 300 |
| **MRR** | $0 | $750 | $3.5K | $7.5K+ |
| **DAU** | 200 | 800 | 2.5K | 5K+ |

---

## 7. Implementation Quick-Start (This Week)

**Do this today (30 min):**
1. [ ] Create Substack account (substack.com/gemhunter)
2. [ ] Write draft of Week 1 email (3 repos, why they matter)
3. [ ] Set reminder: first email Thursday 08:00 UTC

**Do this week (GH-074 + GH-075):**
1. [ ] `scripts/gem-hunter-digest.ts` — read last 7 days of gems, select top 3-5
2. [ ] Landing page skeleton (HTML + Tailwind, 30 min)
3. [ ] Caddy config: gemhunter.egos.ia.br routing
4. [ ] Substack webhook + auto-send

**Do next week (GH-077):**
1. [ ] Supabase migrations: gem_lists, gem_votes tables
2. [ ] API routes (CRUD)
3. [ ] Dashboard React component (vote button, bookmark)

**Commit to:** 1 feature per week (GH-074 → GH-075 → GH-077 → GH-080 → GH-083).

---

## 8. The Ask (Enio)

This roadmap assumes:
1. ✅ **You approve the features** (GH-074..085 go into TASKS.md P36)
2. ✅ **Gem Hunter is your #1 product** (allocate 50% focus vs. Guard Brasil, Eagle Eye, etc.)
3. ✅ **You'll iterate on newsletter copy** (first 5 weeks = manual, then automate)
4. ✅ **You're OK with freemium pricing** (not SaaS purist, not open-core)
5. ✅ **You'll engage the community** (respond to first 20 votes/comments, set tone)

**If approved:** 60-day sprint → $7.5K MRR + 300 customers + product-market signal → Series A runway.

---

*Roadmap v0.1 — Ready for implementation upon approval.*
*Total effort estimate: 120h across 12 weeks (~15h/week, solo)*
