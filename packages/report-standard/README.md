# @egos/report-standard

> **EGOS Report SSOT v2.0.0** — Canonical report schema, validator, and TypeScript types

## Installation

```bash
bun add @egos/report-standard
# or
npm install @egos/report-standard
```

## Usage

### Basic Validation

```typescript
import { validateReport, Report } from '@egos/report-standard';

const myReport = {
  id: crypto.randomUUID(),
  type: 'analytics',
  version: '2.0.0',
  title: 'Q1 Analysis',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  authors: [{ id: 'user-1', name: 'Analyst', role: 'author' }],
  sections: [{
    type: 'executive_summary',
    title: 'Summary',
    content: 'Key findings...',
    order: 0
  }]
};

const result = validateReport(myReport);
if (result.valid) {
  console.log('✓ Report is valid');
} else {
  console.error('✗ Validation errors:', result.errors);
}
```

### Schema Reference

See `schemas/report-v2.json` for the complete JSON Schema specification.

## Report Types

- `analytics` — Data analysis reports
- `audit` — System/process audits
- `compliance` — LGPD/regulatory compliance
- `dissemination` — Cross-repo distribution reports
- `incident` — Security/operational incidents
- `intelligence` — Research intelligence
- `research` — Technical research
- `strategy` — Strategic planning
- `technical` — Technical documentation

## Repository Integration

| Repository | Adapter | Status |
|------------|---------|--------|
| `egos` | Native | ✅ v2.0.0 |
| `852` | `src/lib/report-adapter.ts` | Planned |
| `br-acc` | Pydantic model | Planned |
| `egos-inteligencia` | RBAC extension | Planned |

## SSOT Reference

- **Full spec:** `egos/docs/REPORT_SSOT.md`
- **Dissemination plan:** `egos/docs/monitoring/REPORT_SSOT_DISSEMINATION_PLAN.md`

## Version

- Package: `1.0.0`
- Schema: `2.0.0`
