# Guard Brasil — Competitive Market Research
**Date:** 2026-04-05 | **Scope:** LGPD compliance API + PII detection tools

---

## Market Size

Global privacy compliance software market is on a strong upward trajectory (WMR, March 2026). Brazil-specific estimates are not widely published, but ANPD's 2025-2026 Regulatory Agenda shows accelerating enforcement on data aggregators, AI systems, and cross-border transfers — creating direct compliance urgency. Conservative estimate for Brazil's addressable market (LGPD tools + DPO services): **R$ 500M–1B/year**, growing at 20–30% YoY as ANPD sanctions increase.

---

## Top Competitors

### 1. OneTrust (onetrust.com/solutions/brazil-lgpd-compliance)
- **What they do:** Enterprise consent management, DSAR automation, LGPD-specific module, data mapping
- **Pricing:** Enterprise contracts, typically R$ 50k–500k/year. No self-serve API.
- **Target:** Compliance/legal teams at large corporations (Fortune 500, banks, telcos)
- **Guard Brasil's edge:** OneTrust is a GRC platform, not a developer API. No per-call PII scanning. Guard Brasil serves devs who need programmatic PII detection in their pipelines — OneTrust can't do that.

### 2. BigID (bigid.com/compliance/lgpd)
- **What they do:** Data discovery, LGPD data mapping, sensitive data classification across cloud/on-prem
- **Pricing:** Enterprise only (~$100k+/year USD). No public self-serve pricing.
- **Target:** CISOs and data governance teams at large enterprises
- **Guard Brasil's edge:** BigID requires full data infrastructure integration. Guard Brasil is a lightweight REST API call (4ms, no infrastructure) — ideal for startups, fintechs, and mid-market that can't afford BigID's implementation cost.

### 3. Privacy Tools BR (privacytools.com.br)
- **What they do:** Brazilian LGPD governance platform — consent records, ROPA (Record of Processing Activities), DSAR management, DPO workflows
- **Pricing:** Tiered SaaS (estimated R$ 500–5k/month based on company size). Demo-gated.
- **Target:** DPOs and legal/compliance teams at Brazilian companies
- **Guard Brasil's edge:** Privacy Tools is a process/workflow tool, not a detection API. It has no real-time PII inspection capability. Guard Brasil is the technical layer that feeds into platforms like Privacy Tools — complementary, not competing.

### 4. Microsoft Presidio (open-source, github.com/microsoft/presidio)
- **What they do:** Open-source PII detection library (Python), NLP-based, no Brazil-specific patterns out of the box
- **Pricing:** Free (self-hosted). Costs come from compute and integration engineering.
- **Target:** Data engineers and ML teams building internal pipelines
- **Guard Brasil's edge:** Presidio has zero Brazilian PII patterns natively (CPF, RG, MASP, CNH, NIS). Requires significant customization to be LGPD-aware. Guard Brasil delivers 15 BR-specific patterns at 4ms with zero setup — a direct upgrade for any dev using Presidio for BR data.

### 5. Expunct.ai / Generic PII Detection APIs
- **What they do:** Generic PII detection APIs (email, phone, credit card), GDPR/CCPA focus, no LGPD specificity
- **Pricing:** Expunct offers free tier (1M tokens/month), then paid tiers. Pay-per-use model — similar to Guard Brasil's approach.
- **Target:** Developers in US/EU markets building LLM pipelines
- **Guard Brasil's edge:** These tools are GDPR/CCPA-optimized. They miss Brazil-specific identifiers entirely (CPF regex, MASP format, PIS/PASEP). Guard Brasil is the only API purpose-built for LGPD/Brazilian PII patterns with ATRiAN ethical validation layer.

---

## Guard Brasil's Core Differentiators (Summary)

| Differentiator | vs. Who |
|---|---|
| 15 BR-specific PII patterns (CPF, RG, MASP, CNH, NIS, etc.) | vs. Presidio, Expunct, all non-BR tools |
| 4ms latency, REST API, zero infrastructure | vs. BigID, OneTrust (enterprise-heavy) |
| Pay-per-use from R$ 0 (free tier) | vs. OneTrust/BigID (R$ 50k+ contracts) |
| LGPD + ATRiAN ethical validation | vs. all competitors (unique positioning) |
| Developer-first (npm + Python SDK) | vs. Privacy Tools BR (DPO-workflow tool) |

---

## GTM Angle: Who to Target First

**Primary target: Brazilian CTOs and backend developers at fintechs, healthtechs, and LegalTechs** (50–500 employees).

**Why:**
- They handle CPF/RG daily (loan applications, patient records, legal docs)
- They have compliance pressure but can't afford BigID or OneTrust
- They make API purchasing decisions in days, not months (no legal procurement cycle)
- Guard Brasil fits into their CI/CD pipeline or data ingestion flow directly

**Secondary target: DPOs at mid-market companies** who need a technical "proof" layer for ANPD audits — Guard Brasil can generate inspection logs showing PII was detected and handled.

**Avoid initially:** Large enterprises (>5k employees) — procurement cycles are 6–12 months, require legal review, and compete directly with OneTrust/BigID which already have sales teams embedded there.

**Best outreach channel:** X.com threads about LGPD pain points + Brazilian dev communities (Dev.to BR, Rocketseat Discord, Alura). Frame Guard Brasil as "the Presidio for Brazil — but with a free API key and no setup."

---

## Quick Wins (GTM Actions)

1. **Write a dev.to post:** "How to detect Brazilian PII (CPF, RG, MASP) in your Node.js API in 5 minutes" — with live Guard Brasil example
2. **X.com thread:** "ANPD is accelerating enforcement in 2026. Here's a free API to check if your app leaks Brazilian PII." — link to guard.egos.ia.br free tier
3. **Target M-007 list:** Fintechs and healthtechs that process CPF/RG — they have the highest ANPD risk and lowest switching cost

---

*Sources: Exa web search (2026-04-05) — OneTrust, BigID, Privacy Tools BR, Microsoft Presidio, Expunct.ai, WMR Market Report, ANPD 2025-2026 Regulatory Agenda, Chambers & Partners Brazil Data Protection 2026*
