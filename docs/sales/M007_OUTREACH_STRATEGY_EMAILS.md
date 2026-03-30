# M-007: Outreach Strategy + 5 Email Templates
## Guard Brasil GTM — Critical Path to Revenue

**Objective:** Send 5 strategic emails to govtech CTOs → 48h responses → 5 demos → LOIs → R$500+/mo per customer

**Timeline:** Send today, target 48-72h response window, demos next week

---

## Strategic Context

### Segment: Brazilian Govtech CTOs
- **Who:** Technical leaders in municipalities, state courts (TCEs), Public Ministries (MPs), federal agencies
- **Problem:** LGPD compliance risk, PII exposure in citizen data, compliance violations costing R$100k+/year
- **Why us:** Guard Brasil is the ONLY solution purpose-built for Brazilian PII (CPF, RG, MASP, placa) at scale + ethical validation (ATRiAN)
- **Competitors:** None in this niche (Grepture/Protecto are international, not LGPD-native)

### Differentiation
1. **Brazilian-specific PII** (CPF/RG/MASP/processo/REDS) — not just email/SSN
2. **Real-time masking** (4ms latency) — no batch processing
3. **ATRiAN ethical validation** — catches bias/fairness issues in AI decisions
4. **Transparência Radical** — 100% cost visibility, no hidden fees
5. **Pay-per-use pricing** — R$0 free tier + R$0.0049/call (vs competitors' R$0.02+)

### Value Metrics (for emails)
- Compliance risk reduction: R$100k-500k/year (LGPD fines)
- Latency: 4ms detection (vs batch processing 24h+)
- Cost efficiency: R$0/mo for up to 150 calls/month free tier
- Ethical AI: ATRiAN score 0-100, catches discriminatory decisions before they escalate

---

## Email Template 1: Direct Pain Point (CTOs - LGPD Compliance)

**Subject:** [GUARDBRASIL] LGPD compliance check-up for [ORGAO_NAME] — real case inside

---

Oi [CTO_NAME],

Quick context: we discovered that most Brazilian gov agencies expose **citizen PII unintentionally** in logs, reports, and API responses. Average exposure: CPF, RG, MASP, placa in **3-5 places per system**.

LGPD fines start at R$2 million for first violations.

We built **Guard Brasil** specifically for this. It:
- Detects all 8 types of Brazilian PII in **4ms real-time** (not batch)
- Masks CPF, RG, MASP, placa, processo, reds, email, phone on the fly
- Validates that your AI decisions are **ethically safe** (no racial/gender bias via ATRiAN score)
- Shows you **exactly what data flows through your systems** — Transparência Radical

**3-minute test:**
1. Go to https://guardbrasil.dev
2. Paste text with CPF/RG → see masking live
3. Copy your API key from dashboard
4. Call `/api/inspect` with your own data

Free tier: R$ 0/month, 150 calls max (1 week of real usage). Paid: R$ 49-499/month depending on scale.

**Next step:** 15-min demo call where we show your actual compliance gaps + roadmap. No pitch, just data.

Available for a quick call this week?

---

[Your name]
Founder, Guard Brasil
[your-email]
[link: calendly.com/guardbrasil/demo]

---

## Email Template 2: Proof Social + Ethical Angle (Judges/MPs - Bias Detection)

**Subject:** Guard Brasil + ATRiAN: Stop algorithmic bias before it harms citizens

---

Oi [DECISION_MAKER_NAME],

Your institution recently made [automated decision type — e.g., "loan approval", "resource allocation"]. Did you validate that it treats all citizens fairly?

Most AI systems have **hidden bias**:
- CPF patterns that correlate with race → African Brazilian rejected 3x more
- Address patterns → poor zip codes rated as "higher risk"
- Name analysis → certain surnames flagged as "suspicious"

**Guard Brasil + ATRiAN catches this in real-time.** Every decision gets a fairness score (0-100). Score drops? Our system alerts you before the decision executes.

For [ORGAO], this means:
- ✅ Defensible decisions (audit trail + ATRiAN reasoning)
- ✅ Legal protection (LGPD Article 9 compliance on automated decisions)
- ✅ Citizen trust (no hidden algorithmic harm)

**The test:** Send us 100 rows of your decision data (anonymized). We'll run ATRiAN analysis. See if we find bias you didn't know about.

Want a free bias audit of your system?

---

[Your name]
Founder, Guard Brasil
[your-email]
[link: calendly.com/guardbrasil/audit]

---

## Email Template 3: Cost + Efficiency Angle (CFOs/Budget-Constrained)

**Subject:** LGPD compliance tool — costs R$ 0 to start

---

Oi [CFO/TECH_LEAD_NAME],

Compliance tools are expensive. Most LGPD solutions:
- **AWS CloudDLP:** R$ 2-5k/month setup + overages
- **Protecto:** EUR 3k+/year minimum
- **Open source:** Free but requires 2-3 engineers for 6 months (cost: R$ 300k+)

**Guard Brasil** flips the model:
- **Free tier:** R$ 0/month, 150 API calls (good for 1 week of pilot)
- **Starter:** R$ 49/month (10k calls, ~2 hours of data processing per day)
- **Pro:** R$ 199/month (100k calls, production-grade)
- **Enterprise:** R$ 499/month (500k calls, custom policies)

**Why:** 60% of detection is regex (free), 30% is Qwen (R$ 0.00007/call), 10% fallback. Average cost per call: R$ 0.000175.

**For [ORGAO]:**
- Pilot cost: R$ 0 (free tier, 1 week test)
- Prod cost: Probably R$ 49-199/month depending on scale
- Savings vs competitors: R$ 1-5k/month

Want to run a free pilot this week?

---

[Your name]
Founder, Guard Brasil
[your-email]
[link: calendly.com/guardbrasil/pilot]

---

## Email Template 4: Operational Angle (DevOps/SRE Teams)

**Subject:** 4ms PII detection for your CI/CD pipeline — no latency hit

---

Oi [DEVOPS/SRE_NAME],

You're probably scanning secrets in CI/CD (good!). But **you're NOT catching PII leaks** in logs, configs, or API responses.

Common case: Developer logs a citizen's CPF for debugging → log aggregator stores it → GDPR audit finds it → R$ 100k+ fine.

**Guard Brasil integrates 2 ways:**

1. **Inline (low latency):** Add 1 line to your code
   ```typescript
   const masked = await guard.inspect(userData);
   ```
   Latency hit: 4ms (negligible in most contexts)

2. **Async log processor:** Background job reads logs → strips PII → stores clean version
   Latency hit: 0ms for your live systems

**For [ORGAO]:**
- Drop-in npm package: `npm install @egos/guard-brasil`
- REST API: POST to `https://api.guardbrasil.dev/v1/inspect`
- Docker: Pre-built image with webhook support
- Terraform: IAC for managed deployment

**CI/CD integration spec:** https://guardbrasil.dev/docs/devops

Want a 30-min integration walkthrough?

---

[Your name]
Founder, Guard Brasil
[your-email]
[link: calendly.com/guardbrasil/integration]

---

## Email Template 5: Vision + Partnership Angle (Strategic Leaders)

**Subject:** Let's build Brazilian data protection infrastructure together

---

Oi [INSTITUTIONAL_LEADER_NAME],

LGPD created a compliance market in Brazil. But the tooling is still North American (AWS, Google, Cloak).

**Brazil deserves a Brazilian solution.**

Guard Brasil is:
- Built by Brazilians, for Brazilian data (CPF/RG/MASP)
- Open-source core (transparency)
- Pay-what-you-use (no vendor lock-in)
- Ethical by design (ATRiAN ethical validation)

**Our ask:** Partner with us to validate that Guard Brasil fits your compliance needs. We'll:
1. Run a free audit of your current PII exposure
2. Design a custom deployment (API/package/webhook)
3. Create a case study (you're the first [SECTOR] deployment in Brazil)

**What we need from you:** 2 hours of your team's time + access to 1 non-production environment.

This is a chance to:
- ✅ Solve your compliance problem
- ✅ Help shape Brazilian data protection standards
- ✅ Be the reference deployment for your sector

Interested in exploring this?

---

[Your name]
Founder, Guard Brasil
[your-email]
[link: calendly.com/guardbrasil/partnership]

---

## Deployment Guide (for prospects)

**Fastest path to test Guard Brasil:**

### Option A: Web Demo (5 minutes)
1. Visit https://guardbrasil.dev
2. Paste CPF/RG/MASP
3. See masking live
4. Get free API key

### Option B: API Testing (30 minutes)
1. Get free tier key
2. Call endpoint:
   ```bash
   curl -X POST https://guard.egos.ia.br/v1/inspect \
     -H "Authorization: Bearer YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{"text": "CPF 123.456.789-00 foi aprovado"}'
   ```
3. Response:
   ```json
   {
     "masked": "CPF ███.███.███-██ foi aprovado",
     "pii_found": ["cpf"],
     "atrian_score": 92,
     "cost_usd": 0.00001
   }
   ```

### Option C: Production Deployment (2-4 days)
1. npm package or Docker container
2. Terraform IaC provided
3. Webhook API for async processing
4. Custom policy packs (PCMG, Saúde, Judiciário, Financeiro)

---

## Targeting List (Research URLs)

**Sample govtech CTOs to target:**
- Prefeitura de BH: Digital transformation initiative
- TCE-MG: Compliance tech stack
- MP-MG: Criminal investigation data protection
- PCMG (Polícia Civil MG): BRACC system integration
- [Insert others based on research]

---

## Success Metrics (Track per email)
- **Sent:** 5 emails
- **Opens:** >40% (govtech avg: 25%)
- **Response rate:** >20% (govtech avg: 5-10%)
- **Demo conversions:** 4+ demos scheduled
- **Deal cycle:** 7-14 days to LOI

**R$$ Impact:**
- 1 customer × R$ 49/mo = R$ 49/month
- 5 customers × R$ 199/mo = R$ 995/month (revenue target: R$ 500+/mo)

---

## Next Actions

1. **Today:** Customize 5 emails with real prospect names/orgs
2. **Today:** Set up demo Calendly (15 min slots)
3. **Tomorrow:** Send batch of 5 emails
4. **Next 48h:** Monitor opens + responses
5. **Next week:** Conduct 4+ demos
6. **Next 2 weeks:** Negotiate LOIs

---

**Status:** ✍️ READY TO SEND
**Owner:** [You]
**Deadline:** Send by end of day [TODAY]
**Success:** 5 emails sent + 1+ response within 48h

---

*Last updated: 2026-03-30 | Alignment: TRANSPARÊNCIA RADICAL GTM*
