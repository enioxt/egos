# Intelink ↔ Guard Brasil Integration Spec

> **Purpose:** Detailed integration surface between Intelink (intelligence chat) and Guard Brasil (compliance/safety facade)
> **Version:** 1.0 | **Status:** Design Phase

---

## CURRENT STATE (Snapshot: 2026-03-30)

### Intelink Uses Guard Brasil?

✅ **Partially** — Imports individual validators, not facade:

```typescript
// apps/intelink/app/api/chat/route.ts (line 347-348)
import { createAtrianValidator } from '@egos/shared';

const atrian = createAtrianValidator({
  knownAcronyms: ['CPF', 'RG', 'REDS', 'RAG', 'LLM', 'IA', 'DHPP', 'MASP'],
  onViolation: (result) => apiLogger.warn('Intelink chat ATRiAN violation', {
    score: result.score,
    categories: [...new Set(result.violations.map((v) => v.category))]
  })
});
```

**Problem:** Intelink calls `atrian.validate()` directly, not `GuardBrasil.create()`.

**What it misses:**
- ❌ No PII scanner integration
- ❌ No Public Guard masking
- ❌ No Evidence Chain audit trail
- ❌ No unified `inspect()` method

---

## DESIGN: UNIFIED FACADE PATTERN

### Target Architecture

```
User Input
    ↓
[Intelink Chat API]
    ↓
LLM (Claude/Qwen)
    ↓
[GuardBrasil.inspect(response)]
    ├─ ATRiAN validation
    ├─ PII detection
    ├─ Public Guard masking
    └─ Evidence chain tracking
    ↓
Safe Output → User
```

### Implementation Path

**Step 1: Guard Brasil Facade (Already Exists)**

Location: `@egos/guard-brasil/src/index.ts`

```typescript
export class GuardBrasil {
  private atrian: AtrianValidator;
  private pii: PIIScanner;
  private guard: PublicGuard;
  private evidence: EvidenceChain;

  static create(config?: GuardBrasilConfig): GuardBrasil { }

  inspect(text: string, context: InspectionContext): GuardBrasilResult {
    return {
      passed: boolean,
      output: string,  // masked/safe
      blocked: boolean,
      atrian: AtrianResult,
      pii: PIIScanResult,
      masking: MaskingApplied[],
      evidenceBlock: string,  // markdown
      lgpdFooter?: string,
    };
  }
}
```

**Step 2: Intelink Migration (EGOS-G004)**

**Current Code** (chat/route.ts):
```typescript
const response = await llm.generate({...});

// Validates separately
const atrianResult = atrian.validate(response);
if (!atrianResult.passed) {
  return { error: 'Ethical violation' };
}

// No other checks
return { response };
```

**Target Code**:
```typescript
import { GuardBrasil } from '@egos/guard-brasil';

const guard = GuardBrasil.create({
  blockOnCriticalPII: false,  // Mask, don't block
  lgpdDisclosure: true,
  customBlocklist: investigation.sensitiveNames
});

const response = await llm.generate({...});

const result = guard.inspect(response, {
  sessionId: session.id,
  investigationId: investigation.id,
  claims: extractedClaims,
  context: { unit_id, user_id }
});

// Check compliance
if (!result.passed) {
  return { error: 'Compliance violation', details: result.blocked };
}

// Return safe response with evidence
return {
  response: result.output,
  compliance: {
    atrian: { passed: result.atrian.passed, score: result.atrian.score },
    pii: { findings: result.pii.findings.length, summary: result.pii.summary },
    evidence: result.evidenceBlock,
    lgpdDisclosure: result.lgpdFooter
  }
};
```

---

## DATA FLOWS

### Chat Message Flow

```
POST /api/chat
  ├─ investigationId: UUID
  ├─ messages: ChatMessage[]
  ├─ mode: 'single' | 'central'
  └─ behavior: { contentiousness: 0-1 }

         ↓

1. Fetch Investigation Context
   - Research documents
   - Previous findings
   - Sensitive entity list (for blocklist)
   - Unit-based access control

2. Route to LLM
   System prompt includes:
   - Investigation scope
   - Legal constraints (ATRiAN rules)
   - PII sensitivity (what to mask)
   - Evidence requirements

3. Generate Response
   LLM output = raw, unfiltered response

4. Guard Brasil Inspection
   guard.inspect(llmResponse, {
     sessionId: ctx.session.id,
     investigationId: ctx.investigation.id,
     claims: extractClaims(llmResponse),
     context: { unit_id: ctx.unit.id, user_id: ctx.user.id }
   })

   Returns:
   - passed: boolean (compliance OK?)
   - output: string (masked version)
   - masking: MaskingApplied[] (what was masked)
   - evidenceBlock: string (why masked)
   - lgpdFooter: string (required disclosure)

5. Return to User
   {
     response: result.output,  // Safe text
     compliance: {
       atrian: { passed, score, violations },
       pii: { findings, masked },
       evidence: result.evidenceBlock,
       lgpd: result.lgpdFooter
     }
   }
```

### Investigation Timeline API

```
GET /api/investigation/[id]/timeline
  ├─ List events chronologically
  └─ Include Guard Brasil masking on each event

Response Event Object:
{
  id: string,
  timestamp: Date,
  event: string,
  evidence: string,  // Raw claim
  maskedEvidence: string,  // After guard.inspect()
  compliance: {
    atrianScore: number,
    piiFindings: number,
    masked: { cpf, rg, masp: number }
  }
}
```

### Entity Resolution Context

```
GET /api/investigation/[id]/entities
  ├─ List discovered entities
  └─ Guard entities with unit-based access

Response Entity:
{
  id: string,
  type: 'Person' | 'Company' | 'Asset',
  name: string,
  maskedName?: string,  // If PEP or sensitive
  exposure: 'internal_only' | 'restricted' | 'public_safe',
  accessible: boolean,  // unit_id check
  accessReason?: string,
}
```

---

## ATRIAN CONTEXT IN INTELINK

### Legal Constraints System

Intelink feeds ATRIAN with investigation-specific rules:

```typescript
const atrianContext = {
  // Known actors in this investigation
  knownAcronyms: [
    'CPF', 'RG', 'MASP', 'REDS',  // Always
    'OPERAÇÃO_X', 'TASK_FORCE_Y',  // This investigation
    'AGU', 'MPF', 'PGR'  // Always
  ],

  // Blocked entities (case-specific)
  blockedClaims: [
    'civilian names',
    'operation codenames',
    'informant identities'
  ],

  // Context flags
  isPublic: false,  // Limit claims
  isJudicial: true,  // Strict evidence
  hasMinors: true,   // Extra protection
  isCrossJurisdictional: true,  // Federal/state alignment
};

const guard = GuardBrasil.create({
  atrian: {
    customAcronyms: atrianContext.knownAcronyms,
    blocklist: atrianContext.blockedClaims,
    strictMode: atrianContext.isJudicial
  }
});
```

### Evidence Claim Extraction

When Guard Brasil processes a response, it extracts claims:

```typescript
const claims = extractClaims(llmResponse);
// [
//   { claim: "Company X received R$500k from Y", source: "document_123" },
//   { claim: "Person Z was present at location", source: "interview_45" },
//   { claim: "Asset W is registered under name", source: "registry_67" }
// ]

const result = guard.inspect(llmResponse, {
  ...,
  claims  // Pass claims for ATRiAN context
});
```

---

## PII INTEGRATION

### Brazilian Document Detection

Intelink calls Guard Brasil PII scanner for:

- **CPF** (Individual tax ID): `XXX.XXX.XXX-XX`
- **RG** (National ID): `X.XXX.XXX-[0-9X]`
- **MASP** (State police ID): Varies by state
- **REDS** (Federal registry): `XX.XXX.XXX/XXXX-XX`

**Pattern Matching:**

```typescript
const piiPatterns = {
  cpf: /\d{3}\.\d{3}\.\d{3}-\d{2}/g,
  cpfRaw: /\d{11}/g,  // 11 consecutive digits
  rg: /\d{1,2}\.\d{3}\.\d{3}-[0-9X]/gi,
  masp: /\d{7}-[A-Z]/g,  // State + serial
  reds: /\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}/g,
};

const result = guard.inspect(response, {...});
// result.pii.findings = [
//   { type: 'cpf', value: '123.456.789-10', masked: 'XXX.456.789-10' },
//   { type: 'rg', value: '12.345.678-9', masked: 'XX.345.678-9' }
// ]
```

### Masking Strategy

Intelink uses **selective masking** (not blocking):

```
Original: "CPF 123.456.789-10 belongs to João Silva"
Masked:   "CPF XXX.456.789-10 belongs to [Redacted]"
```

**Rules:**
- First 3 digits of CPF: visible (geographic/registration info)
- Last 2 digits of CPF: masked (checksum, identifies individual)
- RG: first digit visible (state), rest masked
- Names: fully redacted unless PEP (Politically Exposed Person)

---

## PUBLIC GUARD INTEGRATION

### Exposure Tiers

Intelink respects Public Guard exposure levels:

```typescript
export type ExposureTier = 'internal_only' | 'restricted' | 'public_safe';

type Entity = {
  id: string;
  exposure: ExposureTier;
};

const tenantGuard = TenantGuard.create();
const accessible = await tenantGuard.guardEntity(entity, {
  unit_id: ctx.unit.id,
  user_id: ctx.user.id,
  exposure: entity.exposure  // Checked here
});

if (!accessible) {
  return { error: 'Access denied' };
}
```

**Tiers:**

| Tier | Visible To | Masking | Use Case |
|---|---|---|---|
| **internal_only** | Investigators only | Full | Active operations, informants |
| **restricted** | Unit + leadership | Partial | Sensitive persons, ongoing |
| **public_safe** | Public APIs, read-only | Minimal | Published findings, archived |

---

## EVIDENCE CHAIN INTEGRATION

### Trace Format

Guard Brasil builds an evidence chain showing why masking happened:

```typescript
const result = guard.inspect(response, {...});
console.log(result.evidenceBlock);
```

**Output Example:**

```markdown
---
**Guard Brasil Compliance Trace**

| Component | Result | Details |
|---|---|---|
| **ATRiAN** | ✅ PASS | Score: 98/100 — 1 warning (absolute claim marked) |
| **PII Scanner** | 🟡 FINDINGS | 2 CPFs masked, 1 RG masked, 1 name redacted |
| **Public Guard** | ✅ PASS | All entities accessible (unit_id=unit-456) |
| **Evidence** | ✅ RECORDED | Trace ID: `ev-chain-abc123def456` |

**Masking Applied:**
- CPF `123.456.789-10` → `XXX.456.789-10` (position: line 3, char 45)
- RG `12.345.678-9` → `XX.345.678-9` (position: line 5, char 12)
- Name "João Silva" → "[Investigado Principal]" (redacted, PEP protection)

**Reason for Masking:**
- CPFs are Personally Identifiable Information (LGPD Article 5)
- RGs identify individuals; last digit is checksum unique to person
- Names of subjects protected under operational security (EGOS investigation protocol)

**Timestamp:** 2026-03-30T22:35:42.123Z
**Session:** sess-9a8b7c6d5e4f3a2b
**Investigation:** inv-12345678-90ab-cdef-1234-567890abcdef
**Auditor:** Guard Brasil v1.0
---
```

### Intelink Integration Points

Evidence chain appears in:

1. **Chat responses** — Footer explaining what was masked
2. **Investigation timeline** — Per-event audit trail
3. **Exported reports** — Evidence appendix with full trace
4. **Audit logs** — CRCDM database for compliance review

---

## SCENARIO: INVESTIGATION WITH SENSITIVE ENTITIES

### Setup

Investigation: "Operation Green Light"
- Scope: Company bribery scheme involving public officials
- Sensitive: Informant names, bank account details, ongoing wiretaps
- Jurisdiction: Federal (AGU, MPF)
- Classification: Restricted (only authorized investigators)

### User Query

```
User: "Summarize the financial flow"
```

### System Processing

```
1. Fetch Investigation Context
   - Documents: 145 files indexed
   - Sensitive entities: 23 (informants, accounts, operations)
   - Unit access: user_id=123 → unit_id=federal_task_force_456

2. Generate LLM Response
   Prompt includes:
   - "Do not reveal informant names"
   - "Do not mention specific dates unless >12 months old"
   - "Do not reference ongoing operations"

   LLM Output:
   "Informant Silva reported Company X received R$500k from
    Bank Account 12345-6789-0123 controlled by Minister Y on
    2026-02-15 as part of Operation Theta..."

3. Guard Brasil Inspection
   guard.inspect(llmResponse, {
     sessionId: 'sess-...',
     investigationId: 'Operation Green Light',
     claims: [
       { claim: "Informant Silva reported...", source: "interview_45" },
       { claim: "Minister Y controlled account", source: "fintech_records" },
       { claim: "Operation Theta involved...", source: "coded_dispatch" }
     ],
     context: {
       unit_id: 'federal_task_force_456',
       user_id: '123',
       sensitivities: {
         informants: ['Silva', 'Pereira'],
         operations: ['Theta', 'Green Light'],
         accounts: ['12345-6789-0123']
       }
     }
   })

4. Processing Chain

   ✅ ATRiAN Validation
      - "received R$500k" → qualified claim (source cited)
      - Score: 95/100

   🟡 PII Detection
      - Name "Silva" → informant (custom blocklist)
      - Bank account "12345-6789-0123" → sensitive
      - Date "2026-02-15" → recent (operational security)

   ⛔ Public Guard Check
      - Minister Y: exposure='restricted' (judicial action ongoing)
      - Informant: exposure='internal_only' (safety)
      - Bank account: exposure='internal_only' (investigation)

   📝 Evidence Chain
      - Trace ID: ev-chain-abc123
      - Masking reasons: operational security + LGPD

5. Safe Output
   "Company X received funds from [Classified Financial Source]
    controlled by [Government Official - Restricted Access]
    as part of [Classified Operation].

    [Full names and account details available in restricted
    investigation database. Access requires unit_id=federal_task_force_456
    and judicial authorization.]

    ---
    **Audit Trail:** ev-chain-abc123
    **Decision:** Masking applied per operational security (3 entities)
    **LGPD Compliance:** Minimal PII exposure, investigator-only access"
```

---

## IMPLEMENTATION CHECKLIST (EGOS-G004)

### Code Changes

**File: apps/intelink/app/api/chat/route.ts**

- [ ] Remove `createAtrianValidator()` import
- [ ] Add `import { GuardBrasil } from '@egos/guard-brasil'`
- [ ] Replace `atrian.validate()` with `GuardBrasil.create()`
- [ ] Pass investigation context to `inspect()`
- [ ] Return `compliance` object with evidence block
- [ ] Add logging for Guard Brasil decisions (CRCDM)

**File: apps/intelink/app/api/investigation/[id]/timeline/route.ts**

- [ ] Guard each event with `guard.inspect()`
- [ ] Add `maskedEvidence` field to response
- [ ] Include `compliance` metadata

**File: apps/intelink/lib/tenant-guard.ts**

- [ ] Export `TenantGuard.guardEntity()` for use in Guard Brasil
- [ ] Ensure unit_id filtering works cross-system

### Testing

- [ ] Unit tests: Guard Brasil facade with custom blocklists
- [ ] Integration tests: Chat API returns compliance metadata
- [ ] E2E tests: Investigation timeline shows masked evidence
- [ ] Security tests: PII patterns detected (CPF, RG, MASP, REDS)
- [ ] Compliance tests: LGPD footer present in all responses

### Documentation

- [ ] Update `/api/chat` endpoint docs with `compliance` response format
- [ ] Add example: sensitive investigation + masked output
- [ ] Document blocklist override mechanism
- [ ] Add troubleshooting: "Why was my text masked?"

---

## PERFORMANCE CONSIDERATIONS

### Guard Brasil Overhead

**Current:** <5ms per `inspect()` call (benchmarked)

```
Text Input
  ↓
ATRiAN scan: ~1ms
  ↓
PII patterns: ~2ms
  ↓
Public Guard check: ~1ms
  ↓
Evidence chain: ~1ms
  ↓
Total: ~5ms
```

**For Intelink Chat:**
- LLM response generation: 2-5 seconds
- Guard Brasil inspection: 5ms (negligible)
- Return to user: <1ms

**Total overhead: <1% latency impact**

### Memory

Guard Brasil instance: ~2MB (patterns + validators loaded once)

Recommended: Create singleton per request handler:

```typescript
// At module level
const guard = GuardBrasil.create({...});

// In route handler
export default async function handler(req, res) {
  const result = guard.inspect(text, context);  // Reuse instance
}
```

---

## FUTURE ENHANCEMENTS

### Confidence Scoring

```typescript
// Currently: ATRiAN returns boolean (passed/failed)
// Future: Return confidence (0-1) for borderline cases

const result = guard.inspect(response, {...});
if (result.atrian.confidence < 0.8) {
  // Show warning badge to user
  // Allow override with justification
}
```

### Custom Validators

```typescript
// Allow investigation-specific validation rules

const guard = GuardBrasil.create({
  customValidators: [
    {
      name: 'no-operational-codenames',
      pattern: ['Operation Theta', 'Task Force X'],
      action: 'block'  // or 'redact'
    }
  ]
});
```

### Multi-Language Support

```typescript
// Currently: Portuguese only
// Future: Support English, Spanish for federal/international ops

const guard = GuardBrasil.create({
  language: 'pt-BR' | 'en-US' | 'es-MX'
});
```

---

**Owner:** EGOS Core Team
**Last Updated:** 2026-03-30
**Next Review:** After EGOS-G004 implementation
