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
| `@egosbr/guard-brasil` SDK | ATRiAN, PII Scanner, Public Guard, Evidence Chain | MIT |
| CLI tool (`egos-guard`) | Validate files/text from terminal | MIT |
| Spec & docs | Protocol specs, integration guides | MIT |
| Reference implementation | br-acc as working example | MIT |

**Why free:** Drives adoption. Developers integrate, validate value, discover limits.

---

### Paid (Hosted / Enterprise)

| Tier | Target | Price | Surface |
|------|--------|-------|---------|
| **API Starter** | Indie devs / startups | R$49/mo | Hosted REST API, 10k inspeções/mês, dashboard básico |
| **API Pro** | SMBs / production teams | R$199/mo | 100k inspeções/mês, audit visibility, alertas, prioridade |
| **Business** | Times regulados | R$499/mo | 500k inspeções/mês, SLA, operação multi-time |
| **Enterprise** | Gov / large corps | Custom | Custom SLA, on-prem deploy, policy packs, evidence archival |

---

## Feature Breakdown

| Feature | Free SDK | API Starter | API Pro | Business | Enterprise |
|---------|----------|-------------|---------|----------|-----------|
| ATRiAN validation | ✅ | ✅ | ✅ | ✅ | ✅ |
| PII Scanner BR | ✅ | ✅ | ✅ | ✅ | ✅ |
| Public Guard masking | ✅ | ✅ | ✅ | ✅ | ✅ |
| Evidence Chain | ✅ | ✅ | ✅ | ✅ | ✅ |
| REST API endpoint | ❌ | ✅ | ✅ | ✅ | ✅ |
| API key management | ❌ | ✅ | ✅ | ✅ | ✅ |
| Compliance dashboard | ❌ | Basic | Full | Full + SLA views | Custom |
| Audit log retention | ❌ | Basic | Extended | Extended | Custom |
| Violation alerts | ❌ | Email | Email + webhook | Multi-channel | Custom |
| SLA | ❌ | Best-effort | Standard | Expanded | 99.9% |
| Custom policies | ❌ | ❌ | ❌ | Optional | ✅ |
| On-premise deploy | ❌ | ❌ | ❌ | ❌ | ✅ |
| Priority support | ❌ | ❌ | ✅ | ✅ | Dedicated |

---

## Monetization Logic

### Why this works

1. **Self-serve funnel:** `npm install @egosbr/guard-brasil` → evaluate locally → needs hosted API/dashboard → upgrades
2. **B2B expansion:** Enterprise buys for compliance mandate (LGPD enforcement). One contract = 12+ months ARR.
3. **Brazil-first wedge:** Guard Brasil combines Brazilian identifiers, masking, ethics, and evidence in one layer.
4. **Evidence archival:** Legal teams need evidence trails. Charged by retention period and support level.

### Revenue targets

| Milestone | Metric | Revenue/mo |
|-----------|--------|-----------|
| MVP | 10 API Starter | R$2K |
| Early | 30 API Starter + 5 Pro | R$10K |
| Scale | 5 Enterprise + 100 Starter | R$50K+ |

---

## What Stays Free Forever

To protect ecosystem trust and adoption:
- Core SDK (`@egosbr/guard-brasil`)
- ATRiAN spec and patterns
- PII scanner patterns and logic
- Evidence chain protocol
- br-acc reference implementation

**Commitment:** Open source core is never paywalled. Only hosted infrastructure is paid.

---

## Next Steps (EGOS-064)

1. **Expand `@egosbr/guard-brasil` adoption** — SDK docs, examples, and migration guides
2. **Build CLI `egos-guard`** — `egos-guard validate <file>` + `egos-guard mask <text>`
3. **Stabilize landing page** — public demo + pricing + dashboard preview
4. **Convert first paid pilots** — internal references + 1 external prospect

---

*Maintained by: EGOS Kernel*
*Related: EGOS-062, EGOS-063, EGOS-064*
