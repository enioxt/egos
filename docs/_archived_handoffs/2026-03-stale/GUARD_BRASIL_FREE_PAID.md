# EGOS Guard Brasil — Free vs Paid Surface Definition

> **VERSION:** 1.0.0 | **CREATED:** 2026-03-23 | **STATUS:** Active
> **TASK:** EGOS-063

---

## Commercial Sentence

> "We make Brazilian AI assistants safer to ship by adding LGPD-aware guardrails, masking, evidence discipline, and policy enforcement."

---

## Tiering Strategy

### Free (Open Source — MIT)

Everything needed to self-host and evaluate:

| Surface | Description | License |
|---------|-------------|---------|
| `@egos/shared` SDK | ATRiAN, PII Scanner, Public Guard, Evidence Chain | MIT |
| CLI tool (`egos-guard`) | Validate files/text from terminal | MIT |
| Spec & docs | Protocol specs, integration guides | MIT |
| Reference implementation | br-acc as working example | MIT |

**Why free:** Drives adoption. Developers integrate, validate value, discover limits.

---

### Paid (Hosted / Enterprise)

| Tier | Target | Price (est.) | Surface |
|------|--------|-------------|---------|
| **API Starter** | Indie devs / startups | R$199/mo | Hosted REST API, 50K req/mo, basic dashboard |
| **API Pro** | SMBs | R$799/mo | 500K req/mo, audit logs, email alerts, SLA 99.5% |
| **Enterprise** | Gov / large corps | Custom | Custom SLA, on-prem deploy, RBAC, evidence archival |
| **MCP Addon** | AI agent builders | R$299/mo | Guard Brasil as MCP tools for Claude/OpenAI agents |

---

## Feature Breakdown

| Feature | Free SDK | API Starter | API Pro | Enterprise |
|---------|----------|-------------|---------|-----------|
| ATRiAN validation | ✅ | ✅ | ✅ | ✅ |
| PII Scanner BR | ✅ | ✅ | ✅ | ✅ |
| Public Guard masking | ✅ | ✅ | ✅ | ✅ |
| Evidence Chain | ✅ | ✅ | ✅ | ✅ |
| REST API endpoint | ❌ | ✅ | ✅ | ✅ |
| API key management | ❌ | ✅ | ✅ | ✅ |
| Compliance dashboard | ❌ | Basic | Full | Custom |
| Audit log (30 days) | ❌ | ❌ | ✅ | Unlimited |
| Violation alerts | ❌ | Email | Email + Slack | Custom webhooks |
| SLA | ❌ | Best-effort | 99.5% | 99.9% |
| Custom policies | ❌ | ❌ | ❌ | ✅ |
| On-premise deploy | ❌ | ❌ | ❌ | ✅ |
| MCP server | ❌ | Add-on | Add-on | ✅ |
| Priority support | ❌ | ❌ | ✅ | Dedicated |

---

## Monetization Logic

### Why this works

1. **Self-serve funnel:** `npm install @egos/shared` → `egos-guard validate` → hits rate limits or needs dashboard → upgrades
2. **B2B expansion:** Enterprise buys for compliance mandate (LGPD enforcement). One contract = 12+ months ARR.
3. **MCP add-on:** Unique positioning as AI agent guardrails-as-a-service. No competitor has a Brazil-first MCP guardrail.
4. **Evidence archival:** Legal teams need evidence trails. Charged by retention period.

### Revenue targets

| Milestone | Metric | Revenue/mo |
|-----------|--------|-----------|
| MVP | 10 API Starter | R$2K |
| Early | 30 API Starter + 5 Pro | R$10K |
| Scale | 5 Enterprise + 100 Starter | R$50K+ |

---

## What Stays Free Forever

To protect ecosystem trust and adoption:
- Core SDK (`@egos/shared` modules)
- ATRiAN spec and patterns
- PII scanner patterns and logic
- Evidence chain protocol
- br-acc reference implementation

**Commitment:** Open source core is never paywalled. Only hosted infrastructure is paid.

---

## Next Steps (EGOS-064)

1. **Publish `@egos/guard-brasil` to npm** — standalone package from shared modules
2. **Build CLI `egos-guard`** — `egos-guard validate <file>` + `egos-guard mask <text>`
3. **Create landing page** — `egos.ia.br/guard` with live demo
4. **First paid customer target** — carteira-livre or br-acc as internal reference + 1 external prospect

---

*Maintained by: EGOS Kernel*
*Related: EGOS-062, EGOS-063, EGOS-064*
