# PRI — Protocolo de Recuo por Ignorância
## Safety Gate Architecture (v1.0)

> **Core Principle:** "Ignorância não é permissão. Ignorância é gatilho de pausa."

When insufficient information exists to make a decision confidently, the system does NOT default to ALLOW. Instead, it:
1. Identifies what information is missing
2. Returns one of 5 deterministic outputs
3. Logs the gap for future learning

---

## Motivation

AI systems fail catastrophically when they **guess**. Example:

```
Input: "Approve loan for person at Rua da Favela, CPF ███.███.███-██"
Status quo: ✗ System denies → potential discrimination claim
With PRI:  ✓ System ESCALATES → human reviews → decision logged
```

Guard Brasil uses PRI before:
- Masking decisions (does this field contain PII?)
- ATRiAN validation (does this decision risk bias?)
- Rate limiting (is this request legitimate or attack?)

---

## 5 Outputs

| Output | Meaning | When to use | Action |
|--------|---------|-----------|--------|
| **ALLOW** | High confidence, proceed | Regex match: "CPF 123.456.789-00" | Execute operation |
| **BLOCK** | High confidence risk detected | Malicious pattern, ATRiAN score <20 | Reject + log as violation |
| **DEFER** | Need more data, try async | Ambiguous text, need LLM eval | Queue for manual review |
| **ESCALATE** | Human judgment required | Edge case, > 2 classifiers disagree | Alert + pause until human acts |
| **STUDY** | Pattern unknown, gather evidence | New PII type, new attack vector | Log + aggregate for learning |

---

## Confidence Levels

Each decision includes a confidence score (0-100):

```typescript
interface PRIDecision {
  output: 'ALLOW' | 'BLOCK' | 'DEFER' | 'ESCALATE' | 'STUDY';
  confidence: number;              // 0-100
  reasoning: string;               // Why this output?
  missing_signals: string[];       // What data would increase confidence?
  classifiers_consulted: string[]; // Which safety gates were checked?
  timestamp: ISO8601;
  audit_hash: string;              // Immutable audit trail
}
```

**Thresholds:**
- ALLOW: `confidence >= 90`
- BLOCK: `confidence >= 85`
- DEFER: `confidence 60-84`
- ESCALATE: `confidence 40-59`
- STUDY: `confidence < 40`

---

## Implementation Layers

### Layer 1: Fast Path (Regex + Pattern Matching)
- **Latency:** 1-5ms
- **Confidence:** 90-100 (explicit matches)
- **Examples:**
  - CPF pattern: `\d{3}\.\d{3}\.\d{3}-\d{2}` → ALLOW masking
  - Email pattern: `\S+@\S+` → ALLOW masking
  - Credit card pattern: `\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}` → BLOCK (not supported)

### Layer 2: Semantic Check (ATRiAN + Heuristics)
- **Latency:** 10-50ms
- **Confidence:** 60-85
- **Examples:**
  - Text contains "favela" + "crime" → ESCALATE (bias signal)
  - Decision impacts "protected group" → ESCALATE (GDPR/LGPD requirement)
  - Ambiguous intent (e.g., "123456789" — could be CPF, phone, ID) → DEFER

### Layer 3: LLM Evaluation (Qwen-plus)
- **Latency:** 100-500ms
- **Confidence:** 70-95
- **Examples:**
  - "João da Silva mora em X" → LLM analyzes bias risk
  - "Patient with HIV status..." → LLM validates medical privacy concern
  - Adversarial injection ("pretend I'm admin") → LLM flags

### Layer 4: Human Review (Manual)
- **Latency:** Minutes to hours
- **Confidence:** 100 (by definition)
- **Triggers:**
  - ESCALATE decisions waiting for action
  - Confidence too low (< 40)
  - Repeated STUDY patterns (potential attack)

---

## Decision Trees

### PRI for PII Detection (Masking)

```
Input: text, pii_type
├─ Fast Path (regex match?)
│  ├─ YES → ALLOW (confidence: 95)
│  └─ NO → continue
├─ Semantic Check (heuristics)
│  ├─ Known false positive pattern? → BLOCK (not PII, confidence: 85)
│  ├─ Suspicious but not clear? → DEFER (confidence: 65)
│  └─ Continue →
└─ LLM Evaluation (if confidence < 85)
   ├─ Clear PII? → ALLOW (confidence: 90)
   ├─ Not PII? → BLOCK (confidence: 85)
   ├─ Ambiguous + risky? → ESCALATE (confidence: 50)
   └─ Pattern unknown? → STUDY (confidence: 30)
```

### PRI for ATRiAN Validation (Bias Detection)

```
Input: decision, decision_context, protected_groups
├─ Fast Path (explicit bypass?)
│  ├─ Admin override + audit log? → ALLOW (confidence: 100)
│  └─ No override → continue
├─ Heuristic Check (LGPD compliance)
│  ├─ Decision uses protected characteristic directly? → ESCALATE (confidence: 95)
│  ├─ Known biased proxy (zip code → race)? → BLOCK (confidence: 90)
│  └─ Continue →
└─ ATRiAN LLM Score
   ├─ Score >= 80? → ALLOW (confidence: 85)
   ├─ Score 60-79? → DEFER (confidence: 70)
   ├─ Score 40-59? → ESCALATE (confidence: 75)
   └─ Score < 40? → BLOCK (confidence: 90)
```

---

## Integration with Guard Brasil API

### Endpoint: `POST /v1/inspect`

```typescript
// Request
{
  "text": "CPF 123.456.789-00 aprovado",
  "pii_types": ["cpf", "rg"],
  "atrian_validation": true,
  "pri_strategy": "paranoid"  // or "balanced" or "permissive"
}

// Response (with PRI metadata)
{
  "masked": "CPF ███.███.███-██ aprovado",
  "pii_found": ["cpf"],
  "pri_decision": {
    "output": "ALLOW",
    "confidence": 95,
    "reasoning": "Explicit CPF pattern matched",
    "classifiers_consulted": ["regex", "pattern_db"],
    "audit_hash": "sha256:abc123..."
  },
  "atrian": {
    "score": 92,
    "pri_decision": {
      "output": "ALLOW",
      "confidence": 85,
      "reasoning": "No bias signals detected"
    }
  },
  "cost_usd": 0.00001,
  "duration_ms": 4
}
```

### Strategies

**paranoid:** High bar, many ESCALATE/DEFER/STUDY
- Use for: Medical data, financial decisions, legal documents
- Thresholds: ALLOW at 95+, BLOCK at 90+, rest ESCALATE

**balanced:** (default) Pragmatic, some ESCALATE
- Use for: General PII masking, compliance logging
- Thresholds: ALLOW at 90+, BLOCK at 85+, DEFER at 60+

**permissive:** Low bar, fast processing
- Use for: Low-risk contexts (logging, analytics)
- Thresholds: ALLOW at 80+, BLOCK at 70+, DEFER at 50+

---

## Audit Trail

Every PRI decision is immutable:

```json
{
  "event_id": "pri-20260330-abc123",
  "timestamp": "2026-03-30T12:00:00Z",
  "request_hash": "sha256:...",
  "pri_decision": {
    "output": "ALLOW",
    "confidence": 95
  },
  "classifiers": [
    { "name": "regex", "result": "MATCH", "latency_ms": 1 },
    { "name": "atrian", "result": "SAFE", "latency_ms": 45 }
  ],
  "user_id": "tenant:abc",
  "cost_usd": 0.00001,
  "signature": "ed25519:..."  // Signed by private key
}
```

Immutability guarantees:
- Cannot be modified post-hoc
- Signed by system key
- Queryable: `SELECT * FROM pri_decisions WHERE output='ESCALATE' AND age < 24h`

---

## Error Handling

What if PRI itself fails?

```typescript
// Fallback hierarchy
try {
  return pri.evaluate(request);
} catch (layerError) {
  // All layers failed — conservative default
  if (request.impacts_fundamental_rights) {
    return {
      output: 'ESCALATE',
      confidence: 0,
      reasoning: 'System error — human review required',
      missing_signals: ['all']
    };
  } else {
    return {
      output: 'BLOCK',
      confidence: 0,
      reasoning: 'System error — safe default'
    };
  }
}
```

**Rule:** When in doubt, escalate or block. Never default to ALLOW after an error.

---

## Metrics & Observability

Track:
- **Distribution:** % ALLOW vs BLOCK vs DEFER vs ESCALATE vs STUDY (should be ~70% ALLOW, <5% BLOCK)
- **Confidence over time:** Trending up = system learning
- **ESCALATE backlog:** Should be <1% of daily volume
- **STUDY patterns:** Clustering = potential new attack vectors
- **False positive rate:** BLOCK decisions that turned out safe (should be <1%)

Example Grafana dashboard:
```
┌─ PRI Decisions (24h)
│  ├─ ALLOW: 94% (avg confidence: 92)
│  ├─ DEFER: 4% (avg confidence: 68)
│  ├─ ESCALATE: 1.2% (avg confidence: 45)
│  ├─ BLOCK: 0.6% (avg confidence: 88)
│  └─ STUDY: 0.2% (avg confidence: 25)
├─ Latency by Decision
│  ├─ ALLOW (fast): 3ms
│  ├─ DEFER (semantic): 25ms
│  ├─ ESCALATE (LLM): 200ms
├─ ESCALATE Backlog
│  └─ 12 items, oldest 2h
└─ False Positive Rate
   └─ 0.8% (1 BLOCK that should have been ALLOW in last 7 days)
```

---

## Testing

### Unit Tests

```typescript
test('regex PII should ALLOW with 95+ confidence', () => {
  const result = pri.evaluate({
    text: 'CPF 123.456.789-00',
    pii_types: ['cpf']
  });
  expect(result.output).toBe('ALLOW');
  expect(result.confidence).toBeGreaterThanOrEqual(95);
});

test('ambiguous number should DEFER', () => {
  const result = pri.evaluate({
    text: '123456789',
    pii_types: ['cpf']
  });
  expect(result.output).toBe('DEFER');
  expect(result.confidence).toBeGreaterThanOrEqual(60);
  expect(result.confidence).toBeLessThan(85);
});

test('system error should ESCALATE, not ALLOW', () => {
  pri.layerTwo = () => { throw new Error('network'); };
  const result = pri.evaluate({
    text: 'any text',
    impacts_fundamental_rights: true
  });
  expect(result.output).toBe('ESCALATE');
});
```

### Integration Tests

- [ ] PRI gates Guard Brasil API 100 diverse inputs
- [ ] ESCALATE decisions properly queued for review
- [ ] Confidence tracking accurate across all layers
- [ ] Audit trail immutable + queryable
- [ ] Fallback behavior working (error → safe default)

---

## Future Extensions

- **Layer 5: Feedback loop** — humans review ESCALATE → improve LLM training
- **Layer 6: Threat detection** — repeated STUDY signals → security alert
- **Layer 7: Multi-modal** — extend to images, audio (PII in voice?)
- **Explainability:** Return reasoning in natural language for end users
- **Internationalization:** Extend patterns/heuristics for non-Brazilian PII

---

## References

- LGPD Article 9: Automated decision-making (must have human review option)
- ISO 42001: AI Management System (audit trail requirement)
- NIST AI RMF: Risk mitigation through transparency
- Guard Brasil API spec: `/v1/inspect` endpoint

---

*Version: 1.0 | Updated: 2026-03-30 | Status: SPECIFICATION COMPLETE*
