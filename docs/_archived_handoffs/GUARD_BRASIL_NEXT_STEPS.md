# EGOS Guard Brasil — Next Steps (2026-03-30)

> **Flagship Product Status:** API LIVE (4ms) | Revenue Path: R$500+/mo in 7 days
> **Research Complete:** All Intelink↔Guard Brasil connections mapped
> **Roadmap Ready:** 4-phase plan (8.5 weeks to R$5k/mo)

---

## WHAT WAS RESEARCHED

### Intelink ↔ Guard Brasil ↔ br-acc Ecosystem

**✅ Connections Found:**

1. **Intelink Uses Guard Brasil Partially**
   - Location: `apps/intelink/app/api/chat/route.ts` (line 347)
   - Imports: `createAtrianValidator` only
   - Missing: PII scanner, Public Guard masking, Evidence chains
   - **Problem:** Disconnected validators instead of unified facade

2. **ATRiAN System Core**
   - Location: `@egos/shared/src/atrian.ts`
   - Validates: absolute claims, fabrications, false promises, invented acronyms
   - Score system: 0-100 with configurable deductions
   - Used by: Intelink chat, embedded in Guard Brasil

3. **br-acc (Inteligencia EGOS) Integration**
   - Has Python duplicate of CPF masking + Public Guard
   - Files: `cpf_masking.py`, `public_guard.py`
   - **Problem:** Maintenance nightmare, divergence risk
   - CPF lookup blocked entirely (LGPD enforcement)
   - PEP detection: only shows politically exposed persons

4. **Guard Brasil Unified Facade**
   - Location: `@egos/guard-brasil/src/`
   - Composes: ATRiAN + PII Scanner + Public Guard + Evidence Chain
   - **Issue:** Not published to npm (only in monorepo)
   - Not used as facade in Intelink (used separately)

5. **Shared Capabilities**
   - ATRiAN: ✅ Already consolidated
   - PII Scanner: ✅ In @egos/shared
   - Public Guard: ✅ Exists, but br-acc has Python copy ⚠️
   - Evidence Chain: ✅ In @egos/shared
   - Tenant Guard: Only in Intelink (not in br-acc) ⚠️

### Key Findings

| Finding | Impact | Priority |
|---------|--------|----------|
| **Intelink doesn't use Guard facade** | Missing PII + masking | P1 |
| **br-acc has duplicate Python code** | Sync nightmare, divergence | P1 |
| **No HTTP API for Guard Brasil** | Can't scale across teams | P1 |
| **No evidence chains in br-acc** | Audit trail incomplete | P2 |
| **No tenant guard in br-acc** | Access control missing | P2 |
| **Guard Brasil not on npm** | Third-party adoption blocked | P1 |

---

## COMPREHENSIVE NEXT STEPS

### PHASE 1: IMMEDIATE (Days 1-7) — Revenue Unlocking

**P0 BLOCKER:**

**[Manual] EGOS-M007: Send 5+ Outreach Emails**
- **What:** CTOs/directors at govtech companies, procurement teams, legal departments
- **Templates:** Ready in `docs/sales/M007_OUTREACH_STRATEGY_EMAILS.md`
- **Expect:** 48h responses → demos → LOIs → R$500+/mo first customer
- **Effort:** 2 hours manual
- **Owner:** You (requires personal credibility)
- **Impact:** Unblocks R$500/mo recurring revenue
- **Status:** 🔴 BLOCKED on user action

**Quick Wins (Technical):**

**[Auto] EGOS-G001: Publish @egos/guard-brasil to npm**
- Command: `npm publish --access public`
- Enables third-party adoption
- Effort: 30 min
- Owner: Automation
- Blocker: None (ready now)
- Impact: Unlocks Intelink clarity, br-acc migration path
- Status: 🟡 Ready (waiting queue)

**[Auto] EGOS-G002: Consolidate PII Patterns (TS ↔ Python)**
- Create shared config: `docs/products/GUARD_BRASIL_CONFIG.json`
- Extract patterns from `pii-scanner.ts` + `public_guard.py`
- Include: CPF, RG, MASP, REDS patterns + known acronyms
- Effort: 2 hours
- Owner: Core team
- Impact: Single source of truth for 9 repos
- Status: 🔴 Not started

**[Auto] EGOS-G003: Guard Brasil HTTP API Microservice**
- Endpoint: `POST /api/guard/inspect`
- Deploy: guard.egos.ia.br (Hetzner)
- Enables: br-acc + Intelink consumption
- Effort: 3 hours
- Owner: Core team
- Blocker: G001 (after npm publish)
- Impact: Eliminates duplication, enables API-driven masking
- Status: 🔴 Not started

**[Auto] EGOS-G004: Intelink → Guard Brasil Facade**
- Replace: `atrian.validate()` → `GuardBrasil.create().inspect()`
- Add: PII detection, Public Guard masking, Evidence chains
- Effort: 4 hours
- Owner: Intelink team
- Blocker: G001 (npm publish)
- Impact: Full compliance layer in Intelink
- Status: 🔴 Not started

**Total Phase 1 Technical:** ~9 hours (excluding manual M-007)

---

### PHASE 2: SOLIDIFICATION (Days 8-21) — Intelink Integration

**[Auto] EGOS-G005: Evidence Chains in Investigation Reports**
- Add `GuardBrasil.evidenceBlock` to every LLM response
- Update: `/api/intelligence/journey`, `/api/investigation/[id]/timeline`, chat
- Effort: 3 hours
- Impact: Audit trail for all intelligence findings
- Blocker: G004

**[Auto] EGOS-G006: LGPD Disclosure Footers**
- Auto-append when PII is masked
- Text: "[Dados pessoais mascarados conforme LGPD/Lei 13.709]"
- Deployment: Intelink chat, investigation reports, br-acc API
- Effort: 2 hours
- Impact: Transparent PII handling
- Blocker: G004

**[Auto] EGOS-G009 (Partial): Customer Portal Skeleton**
- Landing page at `guard.egos.ia.br/signup`
- Docs, API explorer, compliance certificates
- Effort: 8 hours (split across phases)
- Start: Now (documentation first)
- Impact: First customer self-serve path
- Blocker: None

**Phase 2 Total:** ~5 additional hours

---

### PHASE 3: UNIFICATION (Days 22-35) — br-acc Consolidation

**[Auto] EGOS-G007: br-acc → Guard Brasil API Integration**
- Replace: local `public_guard.py` → HTTP calls to Guard API
- Create: Python client for Guard Brasil endpoint
- Effort: 2 hours
- Impact: Single masking source, no duplication
- Blocker: G003 (HTTP API)

**[Auto] EGOS-G008: Unified Tenant Guard (Access Control)**
- Backport: `TenantGuard` from Intelink to Python
- Add to: Guard Brasil core
- Effort: 3 hours
- Impact: Unit-based access across both systems
- Blocker: None

**Phase 3 Total:** ~5 hours

---

### PHASE 4: MONETIZATION (Days 36-50) — Customer Tiers

**[Auto] EGOS-G010: API Rate Limiting + Quotas**
- Use: Circuit Breaker (already exists in packages/shared)
- Tier 1: 100 req/day (R$497/mo)
- Tier 2: 5k req/day (R$997/mo)
- Tier 3: unlimited (R$2,497/mo)
- Effort: 2 hours
- Impact: Revenue enforcement, usage tracking

**[Auto] EGOS-G009 (Complete): Full Customer Portal**
- Billing integration (Stripe)
- Team management, API keys
- Usage dashboard
- Effort: 8 more hours
- Blocker: None

**Phase 4 Total:** ~10 hours

---

## EXECUTION TIMELINE

### Week 1 (Days 1-7)

```
MON 2026-03-31 08:00 → Send M-007 emails (2h, user action)
                    → Start G001 (npm publish) + G002 (PII config)

TUE 2026-04-01 08:00 → Complete G001 + G002 (3h combined)
                    → Start G003 (HTTP API scaffold)

WED-FRI 2026-04-02-04 → Complete G003 (3h)
                     → Start G004 (Intelink facade)

FRI 2026-04-04 17:00 → Checkpoint: G001 ✅ G002 ✅ G003 ✅
                    → Revenue path unlocked if M-007 responded

SAT-SUN → G004 in progress, should complete early next week
```

### Week 2-3 (Days 8-21)

```
MON 2026-04-07 → Complete G004 (2-3h remaining)
               → Start G005 (Evidence chains)

TUE-WED → G005 + G006 (5h combined)

THU-FRI → Start G007 (br-acc API integration), which needs G003 live

WEE 2 CHECKPOINT: G001-G006 ✅, G007 in progress
```

### Week 4-5 (Days 22-35)

```
Complete G007 (2h) + G008 (3h)
Start G009 portal work
Milestone: br-acc unified with Guard Brasil API
```

### Week 6-7 (Days 36-50)

```
Complete G010 (quotas) + G009 (portal)
Deploy customer tiers
Milestone: Revenue monetization live
```

---

## SUCCESS CRITERIA

### By End of Week 1
- ✅ @egos/guard-brasil published to npm
- ✅ Guard Brasil HTTP API deployed
- ✅ M-007 emails sent (awaiting 48h responses)
- ✅ Shared PII config created

### By End of Week 3
- ✅ Intelink using Guard Brasil facade
- ✅ Evidence chains in investigation reports
- ✅ LGPD footers auto-appended
- ✅ 1+ customer responses (from M-007)

### By End of Week 5
- ✅ br-acc consuming Guard Brasil API
- ✅ Unified tenant guard (TS + Python)
- ✅ Customer portal skeleton live
- ✅ First customer onboarded

### By End of Week 7
- ✅ Rate limiting + quotas deployed
- ✅ Stripe billing integrated
- ✅ 3+ paying customers
- ✅ R$1,500/mo MRR

---

## DEPENDENCY GRAPH

```
G001 (npm publish)
  ↓
G004 (Intelink facade) ←─── Enables G005, G006
  ↓
G003 (HTTP API)
  ↓
G007 (br-acc integration)
  ↓
G008 (tenant guard)

G002 (PII config) ←─── Enables all phases
G009 (portal) ←─── Parallel, no blockers
G010 (quotas) ←─── Parallel, no blockers
```

---

## DOCUMENTATION READY

✅ **GUARD_BRASIL_FLAGSHIP_ROADMAP.md**
- 4-phase plan, success metrics, revenue targets
- Customer tiers, integration examples
- Technical roadmap, known gaps

✅ **INTELINK_GUARD_BRASIL_INTEGRATION_SPEC.md**
- Current state analysis
- Data flows (chat, timeline, entities)
- Evidence chain format
- Implementation checklist

✅ **Ecosystem Connections Report** (Agent research)
- Detailed findings on Intelink↔Guard Brasil↔br-acc
- Code locations, patterns, duplication identified
- Consolidation points recommended

---

## IMMEDIATE ACTIONS (THIS SESSION)

1. **Send M-007 emails** ← User action (2h) 🔴 BLOCKED
2. **Publish npm** ← Automation ready (30min) 🟡 QUEUED
3. **Create PII config** ← Need user confirmation 🟡 QUEUED
4. **Start HTTP API** ← Automation ready (3h) 🟡 QUEUED

**Recommendation:** Parallel execution:
- User sends M-007 emails (async, 2h)
- Core team: npm publish (30min) + PII config (2h) + HTTP API (3h)
- Ready for Intelink migration by tomorrow

---

## HANDOFF

**What's Ready:**
- ✅ Comprehensive roadmap (8.5 weeks to R$5k/mo)
- ✅ Integration spec (Intelink patterns detailed)
- ✅ Ecosystem research (9 findings, 5 problems identified)
- ✅ Social posts (X.com + Telegram, ready to send)
- ✅ Task breakdown (10 tasks, effort-estimated)

**What Needs Decision:**
- Should we start G001-G003 immediately (parallel to M-007)?
- Should G007 (br-acc integration) be P0 or P2?
- Customer tier pricing: stick with R$497/R$997/R$2,497 or adjust?

**Next Session:** Begin Phase 1 technical tasks + monitor M-007 responses

---

**Prepared:** 2026-03-30T22:50:00Z
**Status:** Ready for execution
**Owner:** @enioxt + core team
