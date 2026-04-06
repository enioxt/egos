# MONETIZATION SSOT — EGOS Ecosystem
**Version:** 1.1.0 | **Owner:** enioxt | **Updated:** 2026-04-06

> Single source of truth for pricing, revenue, payment infrastructure, partner model, and product monetization decisions across the ecosystem.
> **Update this file.** Do NOT create new pricing or partnership docs elsewhere.
> Guard-specific social/outreach execution remains in `docs/GTM_SSOT.md`; ecosystem-level economic and partner strategy lives here.

---

## 1. Products & Pricing Matrix

| Product | Free Tier | Starter | Growth | Enterprise | Model |
|---------|-----------|---------|--------|------------|-------|
| **Guard Brasil** | 150 calls/mo | R$49/mo (5K calls) | R$199/mo (50K calls) | R$499/mo (unlimited) | Fixed tiers |
| **Eagle Eye** | 50 analyses/mo | 500 analyses/mo (R$49) | 5K analyses/mo (R$149) | Unlimited API + MCP (R$499) | Usage-based |
| **Gem Hunter** | 10 findings/day | R$19.90/mo base | R$49/mo + LLM% | API: % of LLM cost | Percentage |

### Pricing Philosophy per Product

**Guard Brasil** — Fixed tiers (predictable cost for compliance-sensitive customers)
- Target: DPO, CTO, CFO buying monthly budget
- Cost floor: R$0.000175/call → 2000% margin at starter tier
- Validated model: SaaS compliance tooling (TOTVS, Sankhya benchmarks)

**Eagle Eye** — Usage-based decision intelligence (chatbot / API / MCP)
- Model: pay-per-analysis (licitação scoring, opportunity alerts, document parsing)
- Channels: REST API (B2B integrations), MCP tool (Claude Code / AI assistants), Chatbot UI
- Free: 50 analyses/mo — enough for a team to discover 1 real opportunity
- Starter R$49: 500 analyses (~10 opportunities/day fully scored)
- Growth R$149: 5K analyses; Enterprise R$499: unlimited + SLA + white-label
- Pricing anchor: Licitações consultancies charge R$800-1200/mo → Eagle Eye API = 10x cheaper
- ⚠️ Eagle Eye pricing is PROPOSED (v2 — GenHunter spec). Validate BIZ-D1 with 3 pilots.

**Gem Hunter** — Percentage-based (aligns incentives with LLM usage)
- User decision 2026-04-02: Option D + % pricing (x402/Pix/Stripe)
- Formula: `customer_charge = llm_cost_usd × 1.5 + base_fee_usd`
- 50% margin on LLM pass-through + fixed base ($0.30/hunt API call)
- Free: 10 findings/day (no LLM deep analysis)

---

## 2. Free Tier Philosophy

**Rule:** Free tier must demonstrate value, not give away the product.

| Product | Free Limit | Why This Number |
|---------|-----------|-----------------|
| Guard Brasil | 150 calls/mo | ~1 dev integration test cycle |
| Eagle Eye | 3 territories | Enough to see the map, not enough to run a business |
| Gem Hunter | 10 findings/day | 1 discovery session; no LLM analysis |

**Standard:** All free tiers expire after 90 days inactivity → convert to freemium prompt.

---

## 3. Payment Infrastructure

| Method | Products | Status | Provider |
|--------|----------|--------|----------|
| Stripe (card/link) | All products | ✅ Live (pk_live configured) | Stripe |
| Pix (via Stripe) | All products | 🔲 BIZ-D2 — enable Stripe Pix (Brazil) | Stripe (native Pix support) |
| x402 (M2M) | Gem Hunter API | 🔲 GH-063 roadmap | x402 protocol |
| Bitcoin Lightning | Gem Hunter | 🔲 future experiment | LNBits or Alby |

**Stripe-unified strategy:** Stripe supports Pix natively in Brazil (PM type `pix`). No second provider needed.
Implement once in `packages/shared/src/billing/` — covers card + Pix + Apple/Google Pay.

**Single payment SSOT:** Use `packages/shared/src/billing/` for all payment logic.
Never implement payment code outside this package.

---

## 4. Cost Model (LLM + Infrastructure)

### Guard Brasil
| Component | Cost/call | Volume for breakeven |
|-----------|-----------|---------------------|
| LLM (PII scan) | $0.000050 | — |
| PostgreSQL/Supabase | $0.000025 | — |
| **Total** | **$0.000175** | 285 paid calls = $0.05 → covers Supabase free tier |

### Gem Hunter (per hunt run)
| Component | Cost/run | Notes |
|-----------|---------|-------|
| arXiv + GitHub + HN | $0.00 | Free APIs |
| Exa (10 queries) | $0.05 | $5/100 queries |
| LLM triage (5 papers × 1K tokens) | $0.0004 | Gemini Flash |
| LLM scaffold (3 papers × 3K tokens) | $0.0009 | Gemini Flash |
| **Total** | **~$0.06/run** | At 50% margin: charge $0.09/run |

### Eagle Eye
| Component | Cost/mo | Notes |
|-----------|---------|-------|
| Supabase storage (80+ territories) | ~$0 | Free tier |
| AI scanning (Gemini Flash) | ~$4.23/mo | Current demo estimate |
| VPS share | ~$3/mo | Proportional Hetzner |
| **Total** | **~$7/mo** | R$99 starter = 1300% margin |

---

## 5. ICP (Ideal Customer Profile)

| Product | Primary ICP | Secondary ICP | ACV Target |
|---------|-------------|--------------|------------|
| Guard Brasil | DPO at mid-corp (50-500 employees) | Fintechs, healthtechs with LGPD compliance obligations | R$2.400/yr |
| Eagle Eye | Head of procurement / compliance at SME bidding regularly | AI builders who want licitações as MCP tool in Claude | R$1.800/yr |
| Gem Hunter | Staff engineer at AI startup | Independent researcher / crypto investor | R$600/yr |

**Combined ICP Overlap:** CTO at Brazilian tech startup (buys Guard Brasil + Gem Hunter together).

---

## 6. Revenue Targets

| Product | Month 1 | Month 3 | Month 6 | Year 1 |
|---------|---------|---------|---------|--------|
| Guard Brasil | R$500 | R$2.000 | R$5.000 | R$24.000 |
| Eagle Eye | R$0 | R$300 | R$1.500 | R$9.000 |
| Gem Hunter | R$100 | R$500 | R$2.000 | R$12.000 |
| **Total** | **R$600** | **R$2.800** | **R$8.500** | **R$45.000** |

---

## 7. Open Decisions (need resolution)

| # | Decision | Owner | Deadline |
|---|----------|-------|----------|
| BIZ-D1 | Eagle Eye pricing — validate usage-based R$49/149/499 with 3 pilot customers | enioxt | 2026-05-01 |
| BIZ-D2 | Enable Stripe Pix (native Brazil PM) — test checkout flow end-to-end | enioxt | 2026-04-20 |
| BIZ-D3 | Gem Hunter free-tier LLM analysis — include or gate behind paid? | enioxt | 2026-04-15 |
| BIZ-D4 | x402 rollout — Gem Hunter only or all products in Phase 1? | enioxt | 2026-05-15 |

---

## 8. Files Superseded by This SSOT

These files remain as historical reference but THIS file is authoritative:
- `docs/business/FREE_VS_PAID_SURFACE.md` — tier definitions (archived)
- `docs/gem-hunter/GEM_HUNTER_v6_MASTER_PLAN.md` — pricing section
- Memory: `stripe_credentials.md` — credentials location only, not pricing
- Memory: `guardbrasil_transparencia_radical_pattern.md` — GTM pivot reference

---

## 9. Founder Operating Model — What Enio Does vs What Must Be Complemented

### Enio's highest-value role

| Capability | Reality | Strategic value |
|-----------|---------|-----------------|
| **Research + synthesis** | Very high | Turns ambiguous domains into product theses quickly |
| **Zero-to-one product building** | Very high | Ships full-stack systems without waiting for teams |
| **Architecture under ambiguity** | Very high | Connects data, AI, workflow, infra, and governance |
| **Brazil-first adaptation** | Very high | CPF/CNPJ/LGPD/PIX/public-data constraints are native, not bolted on |
| **Cross-product reuse** | Very high | One insight becomes shared capability across products |
| **Operational sales discipline** | Low | Follow-up, pipeline, procurement, and CRM are not the founder edge |
| **Bureaucratic finishing work** | Low | Deploy gates, contracts, procurement packs, repetitive ops drain energy |

### Rule: do not look for a second Enio first

The first complementary partner should usually **not** be another pure developer.

The ecosystem already has technical depth. The missing complement is one of these:

1. **Revenue operator** — sells, follows up, closes, runs pipeline
2. **Distribution partner** — already owns audience or access to buyers
3. **Domain credibility partner** — DPO, govtech operator, procurement specialist, industry insider
4. **Customer development operator** — interviews, pilots, implementation follow-through

### Default founder-partner split of responsibilities

| Area | Enio | Partner |
|------|------|---------|
| Product thesis | DRI | Contribute market feedback |
| Architecture + code | DRI | Optional support |
| GTM messaging | Joint | DRI on packaging to market |
| Outreach + pipeline | Support | DRI |
| Partnerships + channels | Support | DRI |
| Sales process + follow-up | Support | DRI |
| Enterprise docs / procurement | Technical input | DRI |
| Customer feedback loop | Joint | DRI on scheduling and collection |

---

## 10. Universal Partner Personas

### 10.1 If only one person joined the ecosystem

**Ideal persona:** a high-agency Brazilian operator with consultative selling skill, comfortable with ambiguity, equity, and early-stage productization.

**Best fit profile:**
- Ex-founder, ex-head of sales, ex-solutions engineer, or ex-operator in B2B SaaS
- Has network in one of: compliance, govtech, enterprise IT, industrial ops, or developer communities
- Can run outreach every day without founder supervision
- Understands how to turn prototypes into pilots, pilots into retained accounts
- Comfortable saying "this product is not ready for that customer yet"
- Does not need salary-first certainty to move

**Bad fit profile:**
- Generalist marketer without buyer access
- Junior SDR needing a mature playbook
- Pure investor with no operating time
- Another architect who wants to redesign everything before selling

### 10.2 If only one company joined the ecosystem

**Ideal company type:** a small or mid-size specialist firm that already sells trust, compliance, intelligence, or digital transformation to the exact buyer we need.

**Best fit characteristics:**
- Already has distribution in a niche where the product can be embedded
- Comfortable with white-label, OEM, or revenue-share models
- Can bring first customers faster than we can build a direct sales team
- Does not require enterprise bureaucracy on day 1
- Accepts that the moat is the combination of product + founder speed + domain adaptation

**Best company archetypes:**
- Compliance consultancy with recurring clients
- Govtech integrator or procurement intelligence boutique
- Industrial software implementer with field relationships
- Developer tooling/media/community operator with audience access

---

## 11. Product-by-Product Partnership Map

### Priority Legend

- **P1** — should actively search partner now
- **P2** — valuable, but after first revenue surfaces mature
- **P3** — maintain/document only, not immediate partner search

| Product | Current state | Enio's role | Missing roles / functions | 1-person ideal partner | 1-company ideal partner | Deal model | Priority | Evidence / SSOT |
|---------|---------------|-------------|----------------------------|------------------------|-------------------------|-----------|----------|-----------------|
| **Guard Brasil** | Live, MRR path, strongest monetization surface | Product/tech/infra owner | Enterprise sales, DPO trust, channel partnerships, procurement packs | DPO/compliance seller or B2B SaaS GTM operator | LGPD/compliance SaaS, consultancy, enterprise integrator | Revenue share, co-founder equity, white-label | **P1** | `docs/GTM_SSOT.md`, `packages/guard-brasil/`, `apps/api/` |
| **EGOS Inteligência** | Merge partially built, high-value data moat, not fully validated/deployed | Research architect + product shell owner | Deploy, testing, domain packaging, pilot design, enterprise narrative | Investigator/analyst operator with govtech or due-diligence sales ability | Govtech intelligence boutique, compliance/intelligence consultancy | Pilot-based revenue share + project-based pilots + equity | **P1** | `/home/enio/egos-inteligencia/AGENTS.md`, `/home/enio/br-acc/AGENTS.md`, `egos-lab/docs/plans/INTELINK_BRACC_MERGE.md` |
| **BR-ACC (data engine)** | 77M+ Neo4j graph, strongest data moat, should remain runtime boundary | Data/ETL architecture owner | Runtime hardening, API packaging, data licensing narrative, pilot proof | OSINT or due-diligence operator | Intelligence consultancy, govtech integrator, compliance intelligence boutique | Pilot + API/data licensing + rev-share | **P2** | `/home/enio/br-acc/AGENTS.md`, `/home/enio/br-acc/TASKS.md` |
| **Intelink (legacy UI asset)** | Dormant as standalone, still valuable for UX, flows, and investigation cockpit patterns | Source of UX patterns and product interaction ideas | Archive discipline, parity tracking, selective porting into EGOS Inteligência | Not a separate partner search surface | Not a separate partner search surface | No direct selling — migrate or archive | **P3** | `/home/enio/INTELINK/frontend/package.json`, `/home/enio/egos-lab/apps/intelink/package.json` |
| **Eagle Eye** | Active candidate, strong B2G thesis, low cost, real pipeline found | Product/AI/data owner | Territory-specific sales, procurement customer discovery, recurring alert workflow validation | Govtech seller, procurement consultant, B2G operator | Bidding consultancy, public procurement intelligence firm | Pilot contracts + rev-share per alert/customer | **P1** | `egos-lab/apps/eagle-eye/README.md`, `docs/MASTER_INDEX.md` |
| **Gem Hunter** | MVP with API and 288 gems, good proof surface | Engine/research owner | Audience growth, developer distribution, API packaging, paid plan conversion | DevRel operator, technical creator, community builder | Devtools media/community or AI research membership business | Rev-share on subscriptions/API usage | **P1** | `agents/agents/gem-hunter.ts`, `docs/business/MONETIZATION_SSOT.md` |
| **Forja** | Beta, WhatsApp-native, good industrial wedge | Product/tech owner | Vertical sales, onboarding, field discovery, quoting workflows | Industrial ops seller, ERP implementer, factory-savvy operator | Metalworking/industrial software reseller or automation consultancy | Pilot + implementation fee + recurring SaaS share | **P1** | `/home/enio/forja/AGENTS.md` |
| **Carteira Livre** | Production, valuation proof, marketplace complexity | Systems/product owner | Growth, distribution, partnerships with instructors and schools, lifecycle marketing | Marketplace growth operator | Driving-school network, regional marketplace operator, mobility partner | Growth rev-share or country/region operator model | **P2** | `/home/enio/carteira-livre/AGENTS.md` |
| **Self-Discovery** | Architecture decided, differentiated concept, not deployed | Core concept + method owner | Productization, B2C growth, retention loops, positioning boundaries | Consumer growth founder with habit/wellness experience | Wellness/coaching platform or digital therapy-adjacent brand | Revenue share with strict scope limits | **P2** | `docs/SELF_DISCOVERY_ARCHITECTURE.md` |
| **852 Inteligência** | Strong proof of capability, institutional usage | Reference implementation owner | Replication model, public-safe packaging, enterprise expansion | Govtech account opener | Security/govtech contractor or public-sector integrator | Pilot/implementation + support | **P2** | `/home/enio/852/AGENTS.md` |
| **SmartBuscas** | Interesting workflow product, not yet fully packaged | Workflow/automation owner | Sales process, lead-gen niche definition, commercial compliance boundary | Performance marketer or sales-ops operator | Lead-gen agency or contact-center tooling firm | Rev-share on recovered leads or SaaS seats | **P2** | `/home/enio/smartbuscas/AGENTS.md` |
| **INPI** | Useful operational assistant, clear niche, modest surface | Builder of guided flow and guardrails | ICP validation, channel access, partnerships with lawyers/consultants | Trademark consultant with digital reach | IP law firm or trademark consultancy | White-label + referral | **P2** | `/home/enio/INPI/AGENTS.md` |
| **Commons** | Governance exists, product thesis absent | Incubator owner | Definition of what it is | Not applicable yet | Not applicable yet | No partnership until product definition | **P3** | `/home/enio/commons/AGENTS.md` |
| **Santiago** | Candidate, purpose still vague, deploy broken | Technical owner | Product definition, ICP, GTM | Too early | Too early | No partnership until problem is clear | **P3** | `/home/enio/santiago/AGENTS.md` |
| **Policia** | Operational/private workspace, strong utility, low shareability | Workflow owner | Internal adoption, controlled validation | Internal champion only | Institutional partner only | Service/internal adoption, not broad GTM | **P3** | `/home/enio/policia/AGENTS.md` |
| **EGOS Self** | Useful tool, but not core revenue path right now | Creator/maintainer | Distribution and productization if pursued | Open-source advocate or device-power-user builder | Device utility distributor | OSS growth or sponsorship | **P3** | `/home/enio/egos-self/AGENTS.md` |

---

### 11.1 Proof Points by Product (numbers we can responsibly use)

| Product | Proof points we can state now |
|---------|------------------------------|
| **Guard Brasil** | 15 BR-native PII patterns, 4ms-class runtime claim in GTM materials, F1 benchmark 85.3%, SDK + API live |
| **EGOS Inteligência / BR-ACC** | 77M+ Neo4j entities, 25M+ relationships, 36 data sources loaded, 46 ETL pipelines, 26+ AI chat tools |
| **Eagle Eye** | 50+ territories tracked, live scan pipeline, real opportunity detection in production workflow |
| **Gem Hunter** | 288 findings surfaced, multi-source discovery engine, API + Telegram surface active |
| **Forja** | WhatsApp live, CRM/ERP operational wedge, active candidate product |
| **Carteira Livre** | Production surface, strong build maturity, valuation thesis already documented |
| **852 Inteligência** | Production chatbot, 50+ active capabilities, live public deployment |
| **Self-Discovery** | Container architecture defined, dedicated domain `self.egos.ia.br`, clear differentiation: AI that asks, not answers |
| **SmartBuscas** | BullMQ workers, PDF parsing, phone scraping, leads persistence, urgency UI already implemented |
| **INPI** | 44 tests, guarded AI assistant, 9-stage guided wizard |

**Rule:** if a number is not in a project SSOT, benchmark, or directly verifiable runtime surface, do not pitch it as fact.

---

## 12. Product Needs by Role Archetype

### 12.1 Role archetypes we repeatedly need

| Role | Core responsibilities | Best product matches |
|------|-----------------------|----------------------|
| **GTM Operator** | Pipeline, outreach, meetings, CRM, follow-up, demos | Guard Brasil, Gem Hunter, Forja |
| **Domain Seller** | Speak buyer language, qualify pain, package offers | Guard Brasil, EGOS Inteligência, Eagle Eye |
| **Distribution Partner** | Bring audience/channel immediately | Gem Hunter, INPI, Self-Discovery |
| **Implementation Partner** | Deploy, onboard, customize, support | Forja, 852, EGOS Inteligência |
| **Growth Operator** | Funnel, landing pages, content, conversion | Gem Hunter, Carteira Livre, Self-Discovery |
| **Customer Development Lead** | Interviews, pilot design, learnings, retention loop | Eagle Eye, Forja, SmartBuscas |

### 12.2 What each role actually replaces in Enio's workload

| Pain today | Role that solves it |
|-----------|---------------------|
| Builds continue, revenue lags | GTM Operator |
| Many products, weak packaging | Domain Seller |
| No systematic follow-up | GTM Operator / Customer Development Lead |
| Strong code, weak trust surface | Domain Seller / Implementation Partner |
| High-value pilots not opened | Distribution Partner |
| Ideas keep multiplying | Customer Development Lead filters demand with real users |

---

## 13. Recommended Partner Search Order (Next 90 Days)

### Tier A — Search immediately

1. **Guard Brasil partner**
   - Why: shortest path to cash
   - Who: DPO/compliance operator or LGPD consultancy
   - Model: rev-share or co-founder-style equity

2. **EGOS Inteligência partner**
   - Why: highest hidden technical gold, strongest moat after Guard Brasil
   - Who: due diligence, OSINT, govtech, or public-data intelligence operator
   - Model: paid pilot + revenue share + optional equity

3. **Eagle Eye partner**
   - Why: low-cost engine with provable B2G value
   - Who: licitações/procurement operator
   - Model: paid alerts/pilots + channel rev-share

4. **Forja partner**
   - Why: practical operational pain, WhatsApp-native, easy pilot motion
   - Who: industrial ops seller or ERP implementer
   - Model: implementation + recurring share

### Tier B — Search after first cash motion is proven

5. **Gem Hunter**
6. **Carteira Livre**
7. **Self-Discovery**
8. **INPI**
9. **SmartBuscas**

### Tier C — Maintain, not actively sell yet

10. **Commons**
11. **Santiago**
12. **Policia**
13. **EGOS Self**

---

## 14. Hard Rules for New Partnerships

1. **Do not give equity to replace a task you could hire cheaply later.** Equity is for distribution, trust, market access, or operating ownership.
2. **If a partner does not bring customers, credibility, or recurring distribution, prefer revenue share over equity.**
3. **For products with unclear ICP, do not start with cap-table complexity.** Start with pilot + revenue split.
4. **Do not let a partner reposition the product away from Enio's actual edge.** The moat is founder speed + Brazil-first system design + research synthesis.
5. **Do not search for one universal operator for all products at once.** Search for one operator with one wedge, then expand.

---

## 15. Cross-References

- `docs/GTM_SSOT.md` — Guard Brasil outreach, social posts, partner targets, scripts
- `docs/MASTER_INDEX.md` — ecosystem inventory and repo classification
- `docs/SSOT_REGISTRY.md` — ownership and canonical document map
- `/home/enio/egos-inteligencia/AGENTS.md` — unified intelligence product shell
- `/home/enio/br-acc/AGENTS.md` — BR-ACC data engine and runtime reality
- `egos-lab/docs/plans/INTELINK_BRACC_MERGE.md` — merge plan and migration status

---

## 16. Open Decisions (Founder / Partnering)

| ID | Decision | Why it matters |
|----|----------|----------------|
| PARTNER-D1 | Guard Brasil first: co-founder operator or channel partner first? | Changes equity vs revenue-share path |
| PARTNER-D2 | EGOS Inteligência: position as due diligence platform, govtech intelligence, or OSINT API? | Defines who can sell it |
| PARTNER-D3 | Forja: sell to one vertical first or keep generic ERP narrative? | Affects partner profile and onboarding |
| PARTNER-D4 | Gem Hunter: creator-led distribution or API-first B2B? | Defines whether to recruit DevRel or sales |
| PARTNER-D5 | Carteira Livre: growth operator or strategic distribution partner? | Changes pace and channel mix |
