# M-007: Outreach Strategy + 5 Email Templates
## Guard Brasil GTM — Critical Path to Revenue

**Objective:** Send 5 strategic emails to govtech CTOs → 48h responses → 5 demos → LOIs → R$500+/mo per customer

**Timeline:** Send today, target 48-72h response window, demos next week

---

## Strategic Context

### Segment: Brazilian Govtech CTOs
- **Who:** Technical leaders in municipalities, state courts (TCEs), Public Ministries (MPs), federal agencies
- **Problem:** LGPD compliance risk, PII exposure in citizen data, and low auditability in AI-assisted workflows
- **Why us:** Guard Brasil is a Brazil-first layer for CPF, RG, MASP, placa, processo and auditable AI output review
- **Competitors:** International privacy/security tools exist, but usually are not LGPD-native or Brazilian-ID-first

### Differentiation
1. **Brazilian-specific PII** (CPF/RG/MASP/processo/REDS) — not just email/SSN
2. **Low-latency masking** — built for inline use, not only batch review
3. **ATRiAN ethical validation** — flags risky claims, false promises and unsupported assertions
4. **Audit visibility** — evidence, masking and policy decisions can be logged and reviewed
5. **Accessible entry point** — free local SDK + hosted plans starting at R$49/mês

### Value Metrics (for emails)
- Compliance risk reduction: lower chance of exposing Brazilian identifiers in AI outputs
- Latency: low-overhead inspection suitable for real-time flows
- Cost efficiency: free local evaluation + hosted API tiers from R$49/mês
- Ethical AI: ATRiAN score 0-100 for review workflows in sensitive contexts

---

## Email Template 1: Direct Pain Point (CTOs - LGPD Compliance)

**Subject:** [GUARDBRASIL] LGPD compliance check-up for [ORGAO_NAME] — real case inside

---

Oi [CTO_NAME],

Quick context: many Brazilian AI workflows still let citizen PII reach logs, reports and model prompts without a dedicated masking layer.

LGPD raises the bar for accountability when personal data is processed in these systems.

We built **Guard Brasil** specifically for this. It:
- Detects Brazilian PII in real time (CPF, RG, MASP, placa, processo, REDS, email, phone)
- Masks sensitive identifiers before output leaves the app
- Adds ethical review signals through ATRiAN for high-stakes text
- Preserves an auditable trail for inspection and compliance review

**Fast validation path:**
1. Share a sample text flow you already process
2. We run a guided inspection live or send a curl example
3. You validate output, latency and masking policy with your team

Free local SDK for evaluation. Hosted API plans start at R$49/mês.

**Next step:** 15-min demo call where we test on a real sample from your environment.

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

Your institution recently made [automated decision type — e.g., "loan approval", "resource allocation"]. Did you validate that the reasoning and output are reviewable before they reach citizens or operators?

Common risk factors in AI-assisted decisions include:
- Proxy variables hidden in names, addresses, geography or socioeconomic markers
- Outputs that sound certain without sufficient evidence
- No audit trail showing what was masked, flagged or escalated

**Guard Brasil + ATRiAN helps review this before production.** Every output can be scored, flagged and routed for human review.

For [ORGAO], this means:
- ✅ Defensible decisions (audit trail + ATRiAN review signals)
- ✅ Better review posture for high-risk automated flows
- ✅ Clearer documentation for compliance and governance teams

**The test:** Send us anonymized sample outputs or rules. We'll run ATRiAN analysis and show where review gates should exist.

Want a free bias and governance review of your flow?

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
- **Free SDK:** R$ 0/month for local evaluation
- **Starter:** R$ 49/month (10k calls)
- **Pro:** R$ 199/month (100k calls)
- **Business:** R$ 499/month (500k calls, expanded support)

**Why:** a large portion of detection is deterministic and low-cost, which makes the hosted layers commercially viable without enterprise-only pricing.

For [ORGAO]:
- Pilot cost: local evaluation or a small hosted pilot
- Prod cost: probably R$49-199/mês depending on scale
- Savings vs enterprise-only vendors: significant for early rollout

Want to run a pilot this week?

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
   const result = guard.inspect(userData);
   ```
   Latency hit: low enough for interactive flows

2. **Hosted inspection API:** Send text to a managed endpoint when you want auth, rate limits and shared usage

**For [ORGAO]:**
- Drop-in npm package: `npm install @egosbr/guard-brasil`
- REST API: POST to `https://guard.egos.ia.br/v1/inspect`
- Reference server: Bun/TypeScript, self-hostable
- MCP surface: `guard_inspect`, `guard_scan_pii`, `guard_check_safe`

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

### Option A: Local SDK evaluation (5 minutes)
1. Install `@egosbr/guard-brasil`
2. Run local inspection against sample text
3. Review masked output and ATRiAN score

### Option B: API Testing (30 minutes)
1. Get a test key
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
     "safe": false,
     "blocked": false,
     "output": "[CONTEÚDO PROTEGIDO]",
     "atrian": {
       "passed": true,
       "score": 100,
       "violationCount": 0
     },
     "masking": {
       "sensitivityLevel": "critical",
       "findingCount": 1
     },
     "meta": {
       "durationMs": 4
     }
   }
   ```

### Option C: Production Deployment (2-4 days)
1. SDK local or hosted API
2. Policy review by your team
3. Logging / evidence retention definition
4. Optional sector-specific policy packs

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
