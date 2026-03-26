# EGOS Guard Brasil — Product Definition

> **VERSION:** 1.0.0 | **CREATED:** 2026-03-23 | **STATUS:** Active
> **TASK:** EGOS-062

---

## What It Is

**EGOS Guard Brasil** is a Brazil-first guardrails layer for AI assistants and public-facing AI systems.

It is an SDK/API/MCP that ensures AI-generated output is:
- **LGPD-compliant** — no personal data leaks through responses
- **Ethically validated** — no absolute claims, false promises, or fabricated data
- **Evidence-anchored** — every claim is traceable to a source or tool call
- **Governance-ready** — policy enforcement with full audit trail

---

## Core Modules

### 1. ATRiAN (`atrian.ts`)
Ethical validation engine for Portuguese-BR AI responses.

- Detects absolute claims (`"com certeza"`, `"nunca"`, `"sempre"`)
- Detects fabricated data references (`"segundo dados da..."`)
- Detects false promises of action (`"vamos resolver"`, `"providências serão tomadas"`)
- Blocks entity mentions (configurable blocklist)
- Returns score 0–100 with violation breakdown

```typescript
import { createAtrianValidator } from '@egos/shared';

const atrian = createAtrianValidator({ blockedEntities: ['CPF do suspeito'] });
const result = atrian.validateResponse(llmOutput);
// { passed: true, score: 94, violations: [...] }
```

### 2. PII Scanner BR (`pii-scanner.ts`)
Brazilian PII detection and sanitization.

Detects: CPF, RG, MASP, REDS, phone, email, process numbers, plates, names, dates of birth.

```typescript
import { scanForPII, sanitizeText } from '@egos/shared';

const findings = scanForPII(text);
const clean = sanitizeText(text, findings);
```

### 3. Public Guard (`public-guard.ts`)
LGPD-compliant output masking with action policies.

- Configurable per-category actions: `mask` | `redact` | `block` | `warn`
- Critical PII (CPF, MASP, REDS) get stricter defaults
- Sensitivity scoring: `low` → `critical`
- LGPD disclosure note generation

```typescript
import { maskPublicOutput, buildLGPDDisclosure } from '@egos/shared';

const result = maskPublicOutput(llmOutput);
// { masked: "...", safe: false, sensitivityLevel: 'critical', findings: [...] }

const disclosure = buildLGPDDisclosure(result);
// "[LGPD] Dados pessoais detectados e mascarados: CPF, MASP. Conforme Lei 13.709/2018."
```

### 4. Evidence Chain (`evidence-chain.ts`)
Traceable response discipline — every claim anchored to a source.

- Builder pattern for attaching evidence per claim
- Types: `tool_call`, `document`, `calculation`, `human_verified`, `inference`, `external_api`
- Confidence levels: `certain` → `speculative`
- Immutable audit hash per response
- Human-readable citation block generation

```typescript
import { createEvidenceChain, formatEvidenceBlock } from '@egos/shared';

const chain = createEvidenceChain({ sessionId: 'sess-123' })
  .addToolCallClaim('O processo 1234567-89.2024.6.26.0100 foi localizado', 'process_lookup', rawApiResponse, 'high')
  .addDocumentClaim('A decisão foi proferida em 2025-01-15', 'tjmg-api', excerpt, 'certain')
  .build();

const citation = formatEvidenceBlock(chain);
```

---

## Composition: Full Guard Pipeline

```typescript
import {
  createAtrianValidator,
  maskPublicOutput,
  buildLGPDDisclosure,
  createEvidenceChain,
} from '@egos/shared';

const atrian = createAtrianValidator();

async function guardedResponse(rawLLMOutput: string, sessionId: string) {
  // 1. Ethical validation
  const ethicsResult = atrian.validateResponse(rawLLMOutput);
  if (!ethicsResult.passed) throw new Error(`ATRiAN block: score ${ethicsResult.score}`);

  // 2. PII masking
  const guardResult = maskPublicOutput(rawLLMOutput);
  const disclosure = buildLGPDDisclosure(guardResult);

  // 3. Evidence chain (caller builds with tool call context)
  const chain = createEvidenceChain({ sessionId }).build();

  return {
    output: guardResult.masked,
    disclosure,
    ethicsScore: ethicsResult.score,
    sensitivityLevel: guardResult.sensitivityLevel,
    auditHash: chain.auditHash,
  };
}
```

---

## Use Cases

| Use Case | Modules Used | Deployment |
|----------|-------------|-----------|
| Chatbot LGPD compliance | PII Scanner + Public Guard | npm package |
| Investigation assistant (police/judicial) | All 4 modules | SDK + MCP |
| Public-sector AI copilot | ATRiAN + Public Guard | Hosted API |
| Legal document AI | Evidence Chain + PII Scanner | SDK |
| WhatsApp bot compliance | Public Guard + ATRiAN | npm package |

---

## Reference Implementations

| Repo | Usage |
|------|-------|
| `EGOS-Inteligencia (br-acc)` | Primary proof case — LGPD + ATRiAN in production |
| `forja` | Chat API with ATRiAN + PII validation |
| `carteira-livre` | WhatsApp bot with PII masking |

---

## Roadmap

### Phase 1 (Current — SDK)
- [x] ATRiAN ethical validator
- [x] PII Scanner BR
- [x] Public Guard (LGPD masking)
- [x] Evidence Chain (traceable responses)

### Phase 2 (MCP)
- [ ] MCP server exposing Guard Brasil as tools
- [ ] `guard://validate` — ATRiAN check
- [ ] `guard://mask` — PII masking
- [ ] `guard://evidence` — evidence chain builder

### Phase 3 (Hosted API)
- [ ] REST API with key auth
- [ ] Dashboard: compliance reports per tenant
- [ ] Webhook: real-time violation alerts
- [ ] Audit console: full evidence trail viewer

---

*Maintained by: EGOS Kernel*
*Related: EGOS-062, EGOS-063, EGOS-064*
