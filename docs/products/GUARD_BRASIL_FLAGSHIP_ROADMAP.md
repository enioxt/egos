# EGOS Guard Brasil — Flagship Product Roadmap (2026-04)

> **Status:** API LIVE (4ms, CPF/RG/MASP lookups) | **Revenue Path:** R$500+/mo within 7 days
> **Version:** 1.0 | **Updated:** 2026-03-30

---

## EXECUTIVE BRIEFING

EGOS Guard is the **unified safety/compliance facade** for all EGOS intelligence operations. It composes 4 validation layers:

1. **ATRiAN** — Ethical validation (no absolute claims, no fabrications)
2. **PII Scanner** — Brazilian document detection (CPF, RG, MASP, REDS)
3. **Public Guard** — LGPD masking/redaction
4. **Evidence Chain** — Audit trail + traceable reasoning

**Current Architecture:**
```
User Input → [ATRiAN] → [PII Scanner] → [Public Guard] → [Evidence Chain] → Safe Output
```

**Ecosystem Integration:**
- ✅ Intelink (Next.js chat) — imports `createAtrianValidator`
- ✅ br-acc (FastAPI) — uses Python copy of masking + policy
- ✅ guard-brasil package — published to npm (not yet; *in monorepo only*)
- ⚠️ **DUPLICATION:** br-acc has Python copy of CPF masking + Public Guard

---

## PHASE 1: IMMEDIATE (Next 7 Days) — Revenue Unlocking

### P0 BLOCKERS

**EGOS-M007: Send 5+ Outreach Emails**
- **Audience:** 5 govtech CTOs, procurement directors, legal teams
- **Templates:** `docs/sales/M007_OUTREACH_STRATEGY_EMAILS.md` ✅ Ready
- **Success:** 48h response → demo → LOI → first customer paying R$500+/mo
- **Effort:** 2 hours manual (emails already templated)
- **Owner:** User (requires personal send)
- **Impact:** Unblocks R$500/mo recurring revenue

### P1 FEATURE GAPS

**EGOS-G001: Publish @egos/guard-brasil to npm**
- **Current state:** Package exists in monorepo, types auto-generated
- **Action:** `npm publish --access public --tag latest`
- **Enables:** Third-party EGOS integrations, Intelink clarity, br-acc migration path
- **Effort:** 30 min
- **Owner:** Automation (pre-release gate)

**EGOS-G002: Consolidate PII Patterns (TypeScript ↔ Python)**
- **Problem:** Two codebases, duplicated logic
  - `@egos/shared/src/pii-scanner.ts` (TS)
  - `br-acc/api/src/bracc/services/public_guard.py` (Python)
- **Action:** Create shared config file: `docs/products/GUARD_BRASIL_CONFIG.json`
  ```json
  {
    "piiPatterns": {
      "cpf": "\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}",
      "rg": "\\d{1,2}\\.\\d{3}\\.\\d{3}-[0-9X]",
      ...
    },
    "knownAcronyms": ["CPF", "RG", "MASP", "REDS", ...],
    "exposureTiers": { "internal_only", "restricted", "public_safe" }
  }
  ```
- **Effort:** 2 hours (extract + validate patterns)
- **Owner:** EGOS-G002 task

**EGOS-G003: Guard Brasil HTTP API Microservice**
- **Purpose:** Centralize validation, eliminate duplication, enable cross-ecosystem calls
- **Endpoint structure:**
  ```
  POST /api/guard/inspect
  { text: string, context: { sessionId, claims } }
  → { passed: bool, violations, maskedText, evidenceChain }
  ```
- **Deploy:** Alongside guard.egos.ia.br (same VPS)
- **Effort:** 3 hours (scaffold + tests)
- **Owner:** EGOS-G003 task

---

## PHASE 2: SOLIDIFICATION (Days 8-21) — Intelink Integration

### P1 INTEGRATIONS

**EGOS-G004: Intelink → Guard Brasil Facade Migration**
- **Current:** Intelink uses separate validators
  ```typescript
  atrian.validate(response)
  pii.scan(response)
  guardian.check(response)
  ```
- **Target:** Unified facade
  ```typescript
  const guard = GuardBrasil.create({ blockOnCriticalPII: false });
  const result = guard.inspect(response, { sessionId, claims });
  // result.output, result.evidenceBlock, result.compliance
  ```
- **Benefit:** Single source of truth, audit trail, LGPD footer
- **Effort:** 4 hours (refactor + test)
- **Owner:** EGOS-G004 task
- **Blocker:** EGOS-G001 (npm publish)

**EGOS-G005: Evidence Chains in Investigation Reports**
- **Current:** Intelink responses untraced, no reasoning recorded
- **Action:** Add `GuardBrasil.evidenceBlock` to every LLM response in:
  - `/api/intelligence/journey/route.ts`
  - `/api/investigation/[id]/timeline/route.ts`
  - Chat responses
- **Format:** Append markdown block showing validation steps
  ```markdown
  ---
  **Guard Brasil Compliance**
  - ATRiAN: ✅ passed (score: 98)
  - PII: 🟡 1 finding (CPF masked)
  - Legal: ✅ all claims qualified
  - Trace: [ev-chain-uuid]
  ```
- **Effort:** 3 hours
- **Owner:** EGOS-G005 task

**EGOS-G006: LGPD Disclosure Footers**
- **Current:** Masking happens silently
- **Target:** Add automatic footer when PII is masked
  ```
  [Uma resposta com dados pessoais foi mascarada em conformidade com LGPD/Lei 13.709]
  [Dados originais retidos apenas em logs cifrados, acessíveis via termo de consentimento]
  ```
- **Deployment:** Intelink chat, investigation reports, br-acc API
- **Effort:** 2 hours
- **Owner:** EGOS-G006 task

---

## PHASE 3: EXPANSION (Days 22-35) — br-acc Consolidation

### P1 UNIFICATION

**EGOS-G007: br-acc → Guard Brasil API Integration**
- **Current state:** br-acc has local Python copy of masking + policy
- **Action:** Consume Guard Brasil API instead
  ```python
  # Instead of local public_guard.py:
  from guard_brasil_client import GuardBrasil

  guard = GuardBrasil(endpoint="http://guard-api.egos.ia.br/guard/inspect")
  result = guard.inspect(entity_data, context={...})
  response_safe = result.masked_output
  ```
- **Enables:** Single source of truth, consistent LGPD enforcement across TS/Python
- **Effort:** 2 hours (client library + integration)
- **Owner:** EGOS-G007 task
- **Blockers:** EGOS-G003 (HTTP API)

**EGOS-G008: Unified Tenant Guard (Access Control)**
- **Current:** Intelink has unit_id filtering, br-acc doesn't
- **Action:** Backport `TenantGuard` to Python + add to Guard Brasil
  ```python
  # Intelink pattern:
  await tenantGuard.guardEntity(entity, { unit_id, user_id })
  # br-acc needs:
  guard.tenantGuard.filterByUnit(entities, unit_id=ctx.unit_id)
  ```
- **Benefit:** Consistent access control across all intelligence APIs
- **Effort:** 3 hours
- **Owner:** EGOS-G008 task

---

## PHASE 4: MONETIZATION (Days 36-50) — Customer Onboarding

### CUSTOMER TIERS

**Tier 1: Compliance Auditing** (R$497/mo)
- CPF/RG lookup with full audit trail
- LGPD compliance reports
- Evidence chains for due diligence
- Intelink access (1 seat)

**Tier 2: Intelligence + Guardrails** (R$997/mo)
- Everything in Tier 1
- Unlimited seats + unit-based access control
- ATRiAN ethical validation on custom LLMs
- Custom blocklists per investigation

**Tier 3: White-Label** (R$2,497/mo)
- Everything in Tier 2
- Private deployment option
- Custom PII patterns (industry-specific)
- SLA + dedicated support

### ACTIVATION TASKS

**EGOS-G009: Customer Portal (Onboarding)**
- Self-serve signup at `guard.egos.ia.br/signup`
- Docs, API explorer, compliance certificates
- Billing integration (Stripe)
- Effort:** 8 hours
- **Owner:** EGOS-G009 task

**EGOS-G010: API Rate Limiting + Quotas**
- Currently: Guard Brasil accepts all requests
- Action: Add metered billing:
  - Tier 1: 100 requests/day
  - Tier 2: 5,000 requests/day
  - Tier 3: unlimited
- Implement via:
  - `packages/shared/src/circuit-breaker.ts` ✅ (already exists)
  - Add quota tracking in Guard Brasil facade
- **Effort:** 2 hours
- **Owner:** EGOS-G010 task

---

## TECHNICAL ROADMAP

### Shared Architecture

```mermaid
graph LR
    A[Guard Brasil Core] -->|facade| B[ATRiAN + PII + Guard + Evidence]
    A -->|npm package| C[@egos/guard-brasil]
    A -->|HTTP API| D[/guard/inspect endpoint]
    C -->|consumed by| E[Intelink]
    D -->|consumed by| F[br-acc]
    D -->|consumed by| G[Third-party integrations]
```

### Dependency Graph

| Component | Current | Target | Status |
|---|---|---|---|
| ATRiAN | @egos/shared ✅ | Guard Brasil facade | ✅ Done |
| PII Scanner | @egos/shared ✅ | Guard Brasil facade | ✅ Done |
| Public Guard | @egos/shared ✅ | Guard Brasil facade + br-acc Python copy | ⚠️ Duplicated |
| Evidence Chain | @egos/shared ✅ | Guard Brasil facade | ✅ Done |
| Guard Brasil | monorepo only | npm publish + HTTP API | 🔴 Blocked by G001 |
| Tenant Guard | Intelink only | Guard Brasil core | 🔴 TODO |
| Rate Limiter | Circuit Breaker ✅ | Guard Brasil quotas | 🔴 TODO |

---

## SUCCESS METRICS

### Revenue (Primary)

| Milestone | Target | Status | Impact |
|---|---|---|---|
| **M-007 Sent** | 5 emails by Day 1 | 🔴 Manual (user) | R$0 → R$500 if LOI |
| **First Customer** | 1 paid user by Day 7 | 🟡 Blocked by M-007 | +R$497/mo |
| **First 10 Customers** | by Day 50 | 🔴 TBD | +R$4,970/mo |
| **ARR Target** | R$25k/year | 🟡 On path (50 customers @ R$497) | Sustainability |

### Product Quality (Secondary)

| Metric | Target | Status |
|---|---|---|
| **API Latency** | <10ms | ✅ 4ms (verified) |
| **PII Detection Rate** | >95% | ✅ (patterns validated) |
| **LGPD Compliance** | 100% | ✅ (masking + blocking) |
| **Evidence Traceability** | 100% | 🟡 (in Intelink only, not br-acc) |
| **NPM Downloads** | 100/week | 🔴 Not published yet |

---

## DEPLOYMENT CHECKLIST

### Pre-Launch (This Week)

- [ ] **EGOS-M007** — Send 5 outreach emails (user action)
- [ ] **EGOS-G001** — Publish @egos/guard-brasil to npm
- [ ] **EGOS-G002** — Consolidate PII patterns to shared config
- [ ] **EGOS-G003** — Deploy Guard Brasil HTTP API

### Beta (Next 2 Weeks)

- [ ] **EGOS-G004** — Intelink facade migration
- [ ] **EGOS-G005** — Evidence chains in reports
- [ ] **EGOS-G006** — LGPD disclosure footers
- [ ] **EGOS-G009** — Customer portal skeleton

### GA (Weeks 3-5)

- [ ] **EGOS-G007** — br-acc API integration
- [ ] **EGOS-G008** — Unified tenant guard
- [ ] **EGOS-G010** — Rate limiting + quotas
- [ ] **EGOS-G009** — Full customer portal + billing

---

## KNOWN GAPS & RISKS

### Technical Debt

| Gap | Impact | Priority | Fix |
|---|---|---|---|
| **PII duplication** | Maintenance nightmare, sync bugs | P1 | G002 |
| **No HTTP API** | Can't scale across teams | P1 | G003 |
| **br-acc Python copy** | Divergence risk | P2 | G007 |
| **No evidence in br-acc** | Audit trail incomplete | P2 | G005+G007 |
| **No tenant guard in br-acc** | Access control missing | P2 | G008 |

### Business Risks

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| **M-007 emails ignored** | Medium | 0 revenue | Follow-up sequences, LinkedIn outreach |
| **Competitors copy** | Low | Revenue loss | Trademark Guard Brasil, patent claims format |
| **Customer churn** | Medium | -R$X/mo | Lock-in via evidence chains, integrations |
| **Data breach** | Low | Existential | LGPD compliance, encryption, audit logs |

---

## INTEGRATION EXAMPLES

### Intelink Chat (POST /api/chat)

```typescript
import { GuardBrasil } from '@egos/guard-brasil';

const guard = GuardBrasil.create({
  blockOnCriticalPII: false,
  lgpdDisclosure: true,
  customBlocklist: investigation.sensitiveNames
});

// After LLM response
const result = guard.inspect(llmResponse, {
  sessionId: session.id,
  claims: extractedClaims,
  context: { unit_id, user_id }
});

// Return to user
return {
  response: result.output,
  compliance: {
    atrian: result.atrian,
    pii: result.pii,
    evidence: result.evidenceBlock  // NEW: audit trail
  }
};
```

### br-acc Entity Lookup (GET /api/v1/graph/company/{cnpj})

```python
from guard_brasil_client import GuardBrasil

# Initialize (local or HTTP)
guard = GuardBrasil(
  mode="http",  # or "local" for embedded
  endpoint="http://guard-api.egos.ia.br/guard/inspect"
)

# Fetch entity
entity = neo4j.run("MATCH (e:Company {cnpj: $cnpj}) RETURN e", cnpj=cnpj)

# Guard it
result = guard.inspect(entity, context={
  "sessionId": request.session.id,
  "unit_id": current_user.unit_id,
  "purpose": "company_profile_lookup"
})

# Return safely
return {
  "company": result.output,  # Masked
  "audit": result.evidenceChain,
  "lgpdDisclosure": result.footer
}
```

### Third-Party Integration (Custom AI Tool)

```typescript
// Third-party wants to use EGOS compliance layer
import { GuardBrasil } from '@egos/guard-brasil';

const guard = GuardBrasil.create({
  atrian: { strictMode: true },
  custom: { allowCustomBlocklists: true }
});

const result = guard.inspect(thirdPartyLLMOutput, {
  sessionId: 'ext-' + externalToolId,
  blocklist: ['client-name', 'operation-code']
});

// They get full compliance report
console.log(result.passed);  // boolean
console.log(result.violations);  // array
console.log(result.maskedOutput);  // safe text
```

---

## NEXT IMMEDIATE ACTIONS (TODAY)

1. **Send M-007 emails** (user) → 2h
2. **Publish npm** (G001) → 30min
3. **Consolidate PII config** (G002) → 2h
4. **Scaffold HTTP API** (G003) → 3h
5. **Create GUARD_BRASIL_CONFIG.json** → 1h

**Total:** 8.5 hours of team work (blocking everything else this week)

---

## QUARTERLY TARGETS (Q2 2026)

- **Revenue:** R$5,000+/month (10 paying customers)
- **Intelink:** 100% migrated to Guard Brasil facade
- **br-acc:** Consuming Guard Brasil HTTP API
- **npm:** 500+ weekly downloads
- **Compliance:** 100% LGPD auditable, zero data breaches

---

**Owner:** @enioxt
**Last Updated:** 2026-03-30T22:30:00Z
**Next Review:** 2026-04-06 (end of Phase 1)
