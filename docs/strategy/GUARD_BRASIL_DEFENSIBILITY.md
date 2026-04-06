# Guard Brasil — Defensibility Strategy

> **Version:** 1.0.0 — 2026-04-06
> **Author:** Enio Rocha (with Claude Opus 4.6)
> **Status:** Strategic SSOT
> **Question that prompted this:** "If anyone can copy us in 1 week using AI, why would they pay?"

---

## TL;DR

**Code is not the moat.** It never was for B2B compliance tools, and it's even less so now that LLMs collapse the cost of cloning a regex library to ~$0.

The right question is not "what stops a copy?" — it's "what stops our customers from leaving for a copy?"

Four things, ranked by strength:

1. **Regulatory trust + legal accountability** (9/10)
2. **Production data flywheel** (8/10, but currently 0 — needs immediate action)
3. **Distribution channels + marketplace presence** (6/10)
4. **Author / brand / narrative** (7/10 long-term, hardest for Enio personally)

**The real risk is not being copied — it's never reaching anyone who would pay.**

---

## Threat model: who actually copies us?

Three classes of "copy" exist. Only one actually matters.

### Class 1 — Hobby fork / GitHub clone (DOES NOT MATTER)
A solo dev forks `@egosbr/guard-brasil`, renames it, publishes their own version.
- They get 0–50 stars
- They never reach a paying customer because they have no SLA, no contract, no responsibility, no support email
- The hobby copies serve as **free marketing for the original** (Stack Overflow links back to us, blog posts cite us)
- **Pieter Levels (Nomad List) loses zero revenue to the dozen forks of his ideas. Vercel loses zero to forks of Next.js.**

### Class 2 — Big Tech encrustation (REAL RISK, MEDIUM)
AWS, Google, Microsoft, or Stripe ships native PII detection for Brazilian formats.
- AWS Comprehend already supports CPF/CNPJ as a paid feature (~$0.0001/unit)
- Google Cloud DLP supports CPF
- **Their problem:** they ship globally, don't optimize for BR edge cases (RG state variations, MASP, CNH formats), don't speak Portuguese in support, don't have ANPD relationships, charge in USD with FX volatility
- **Our defense:** be 10x cheaper (R$ pricing, no FX), 10x more BR-specific, 1x more responsive (Brazilian DPO can DM Enio on LinkedIn)
- Niche big tech doesn't optimize for = our entire market

### Class 3 — Direct competitor with funding (LOW PROBABILITY)
A Brazilian startup raises seed money and builds the same thing with a sales team.
- This would actually be **good news** — validates the market
- We'd compete on speed, openness, and Enio being the public face of LGPD-compliant tooling
- Defense: see Moats 2 and 4 below

---

## Moat 1 — Regulatory trust + legal accountability (STRONGEST)

### The insight
A DPO at a fintech with 200 employees is **personally liable** if their PII detection tool fails and data leaks. ANPD will ask: which tool, who's responsible, what's the SLA, where's the audit trail?

If the answer is "I installed an open source library mantained by `anonymous_dev_42`", that DPO is fired or sued. If the answer is "We have a contract with Guard Brasil, here's the SLA, here's the audit log, here's the LGPD compliance certificate they generate per request", that DPO has cover.

**This is the #1 reason fintechs pay for compliance tooling instead of self-hosting open source.** It's not features. It's **someone to point at when ANPD calls.**

### How we operationalize this

| What | Status | How to build |
|---|---|---|
| **SLA contract** | ❌ | Draft 1-page contract: 99.9% uptime, 4ms p95, 24h response, R$X liability cap |
| **LGPD certificate per request** | ⚠ partial (we return `lgpd_risk` field) | Sign each response with Ed25519, store hash in audit log, give customer a verifiable receipt |
| **Audit log access** | ❌ | Customer dashboard at `guard.egos.ia.br/audit` showing all their requests + signatures |
| **Independent DPO endorsement** | ❌ | Partner with 1 certified DPO (não você) to audit our API once and write a public attestation |
| **ANPD relationship** | ❌ | Apply to ANPD's public consultation working groups; submit Guard Brasil to their tools registry |
| **ISO 27001 alignment** | ❌ | Document control set; not full cert (too expensive), but a checklist showing alignment |

### Forks cannot replicate this
A copycat lib cannot offer "we are legally responsible if it fails" without becoming a real company with insurance, legal entity, support, and reputation. By the time they do that, they ARE us, but with a 6-month head start to lose.

### Action items (P0)
- [ ] DEF-001: draft 1-page SLA contract (template) → `docs/business/SLA_TEMPLATE.md`
- [ ] DEF-002: implement signed-receipt response feature (LGPD certificate per /v1/inspect call) — uses `agent-signature.ts`
- [ ] DEF-003: customer audit log dashboard at `guard.egos.ia.br/audit` (per-API-key view)
- [ ] DEF-004: outreach to 3 DPOs in Brazil for endorsement program
- [ ] DEF-005: submit Guard Brasil to ANPD public registry once they accept submissions

---

## Moat 2 — Production data flywheel (HIGH POTENTIAL, ZERO TODAY)

### The insight
Every API call is a data point: which patterns work, which fail, which formats are emerging, which contexts have which risk. A copycat lib has only static regex. We have telemetry → retraining → improvement → moat.

**6 months from now**, we have a dataset of "PII patterns observed in BR APIs in 2026" — proprietary, valuable, defensive. Forks have nothing.

### What's needed
- **Telemetry table** in Supabase logging: pattern detected, customer (anonymized), timestamp, false-positive flag, sector
- **Consent flow** built into onboarding (LGPD-compliant — customers opt-in to anonymized telemetry in exchange for free tier upgrades)
- **Quarterly retraining** of the detection model (regex → ML hybrid) using the accumulated data
- **Public reports** based on the data: "State of PII Leakage in Brazilian APIs 2026 Q3" → marketing gold

### The catch
**This moat does not exist today.** We don't store telemetry. Every passing day where we serve traffic without logging is a day of moat we're throwing away.

### Action items (P0)
- [ ] DEF-006: `guard_telemetry` table in Supabase (sector, pattern_id, timestamp_bucket, sample_count — no raw data)
- [ ] DEF-007: telemetry consent in onboarding flow (privacy-by-default OFF, opt-in for free tier upgrade)
- [ ] DEF-008: quarterly "State of BR PII" report draft (template)

---

## Moat 3 — Distribution channels + marketplace presence (MEDIUM)

### The insight
"Whoever is in front of the customer wins" beats "whoever has the best tech."
- Stripe Marketplace lists 200+ apps, 100k+ devs see them — only legal entities pass review
- Nuvemshop, VTEX, RD Station marketplaces — same dynamic, BR-specific
- ProductHunt — one-day visibility
- npm + GitHub topics — long-tail SEO

A fork cannot get into Stripe Marketplace (review requires KYC, support, terms, English-only). We can.

### Stripe Apps eligibility (researched 2026-04-06)
Per https://docs.stripe.com/stripe-apps/distribution-options:
- **Public listing requires Stripe review** (compliance, support, naming rules)
- **Naming rule:** cannot contain "Stripe", "app", "free", or "paid" — "Guard Brasil" is fine
- **Language:** marketplace only accepts English listings — we'd need to write the listing in English (Guard Brasil documentation can be PT-BR but the marketplace card must be EN)
- **What gets distributed:** Stripe Apps run **inside the Stripe Dashboard** as embedded widgets. They are NOT external APIs by themselves. To list Guard Brasil on Stripe Marketplace, we'd need to build a thin UI extension that calls our API — e.g., a "PII Scan" tab inside the Stripe customer/charge view that flags any LGPD risks
- **Private install** skips review entirely — an option for first customers (we can give them a private install link without going through public review)
- **Better fit:** **Stripe Verified Partner Program** (https://stripe.com/partners) — for service providers, not embedded apps. Less restrictive, faster, signals trust

### Recommended path
1. **Now:** apply to Stripe Verified Partners as a compliance/security partner. Free, signals trust, gets us in their partner directory.
2. **Month 2-3:** build a minimal Stripe App (Dashboard widget that shows "PII risk score" on each Customer page). Submit for marketplace review.
3. **Parallel:** Nuvemshop + VTEX app listings (lower barrier, BR-native).

### Action items (P1)
- [ ] DEF-009: apply to Stripe Verified Partner Program — https://stripe.com/partners
- [ ] DEF-010: build Stripe App MVP (Dashboard widget calling /v1/inspect on Customer.metadata) — 2-3 days
- [ ] DEF-011: Nuvemshop app submission (list as compliance plugin)
- [ ] DEF-012: VTEX app store submission (B2B compliance category)

---

## Moat 4 — Author / brand / narrative (LONG-TERM, HARDEST FOR YOU)

### The insight
"Guard Brasil de Enio Rocha que escreve sobre LGPD no X.com" beats "lgpd-pii-detector v0.1 by anonymous" not because of features, but because of trust transferred from a known person.

Examples:
- **Pieter Levels** — code is open, content is everything, makes 6 figures USD/mo
- **Theo Browne** — open-source-everything, 80k followers, T3 stack is THE choice
- **Lee Robinson** — Vercel DX person, "Lee's tweets" sell Vercel as much as the product
- **Brazilian:** Akita, Schultz, Lucas Persona — content + open source = audience + buyers

### The problem (CLAUDE.md §24 admits this)
> Enio is a researcher-builder, not a salesperson. Prefers building to selling. Wants to collaborate with the right people.

Moat 4 exigem o que você não quer fazer — ser persona pública, falar regularmente, manter cadência. **This is the bottleneck.**

### Two paths to resolve
**Path A — Find a Co-founder/Partner who handles GTM**
- Profile: BR DPO consultant, compliance specialist, ex-fintech-product-person
- They handle Moat 4 entirely; you handle Moats 1, 2, 3
- Equity split: 50/50 if they're full-time, 70/30 you if part-time
- This is the **single highest-leverage move** for Guard Brasil

**Path B — Outsource the persona to AI (this conversation!)**
- I (Claude) can draft posts, threads, replies — you approve and post
- Quality < Path A but unblocks the bottleneck
- Posts must still be in your voice, signed by you, factually checked
- **Already half-built:** x-reply-bot exists, GTM-014 (x-post.ts) is in TASKS.md

### Action items (P0)
- [ ] DEF-013: write the "ideal partner profile" doc → use it for outreach
- [ ] DEF-014: post 1 X.com thread/week as Enio (drafted by AI, posted by Enio, signed personally)
- [ ] DEF-015: comment on 5 LGPD-related posts/week (relationship building, not sales)

---

## What does NOT defend us (don't waste energy here)

| Anti-pattern | Why it fails |
|---|---|
| Closing the source code | Compliance buyers WANT open source — they need to audit before buying |
| Patenting the regex | Regex isn't patentable; even if it were, BR patent enforcement is glacial |
| Adding obscure features nobody asked for | Increases surface area without increasing trust |
| Selling at "enterprise pricing" (R$5k/mo+) | Pushes us into RFP hell where we lose to OneTrust/BigID |
| Hiding pricing | DPOs hate this; we want frictionless self-serve |
| Demanding annual contracts | DPOs want monthly to test; annual after 6 months of trust |
| Vendor lock-in via proprietary formats | Same compliance buyer wants exit ramp; lock-in destroys trust |

---

## The honest verdict

**Code is the floor, not the moat.**
**Trust + accountability + dataset + distribution = the real moat.**
**The biggest existential risk is not "being copied" — it's "never being adopted by anyone who would pay."**

Right now, on 2026-04-06:
- ✅ Code: shipped, 15 patterns, 4ms latency, npm package, API live
- ❌ Customers: 0
- ❌ SLA contract: not drafted
- ❌ Telemetry/dataset: not collecting
- ❌ Marketplace presence: nowhere
- ❌ Public author voice: barely
- ❌ Independent endorsement: none
- ❌ Co-founder/partner: not found

The technical moat work is **done**. The non-technical moat work is **0%**.

Every day spent adding features instead of building Moats 1-4 is a day moving in the wrong direction.

---

## DEF-001..015 task list (for TASKS.md)

```
P0:
- [ ] DEF-001 — SLA contract template (1 page)
- [ ] DEF-002 — Signed LGPD receipts (uses agent-signature.ts)
- [ ] DEF-003 — Customer audit log dashboard
- [ ] DEF-004 — DPO endorsement outreach (3 contacts)
- [ ] DEF-006 — guard_telemetry table + opt-in flow
- [ ] DEF-007 — Telemetry consent in onboarding
- [ ] DEF-013 — Ideal partner profile doc
- [ ] DEF-014 — Weekly X.com thread cadence

P1:
- [ ] DEF-005 — ANPD registry submission (when they open)
- [ ] DEF-008 — Quarterly "State of BR PII" report template
- [ ] DEF-009 — Stripe Verified Partner application
- [ ] DEF-010 — Stripe App MVP (Dashboard widget)
- [ ] DEF-011 — Nuvemshop app submission
- [ ] DEF-012 — VTEX app submission
- [ ] DEF-015 — 5 LGPD post comments/week
```

---

*The strategy is "build Moats 1-4 in parallel, ignore the copy threat, find the partner."*
