# Auditable Live Sandbox — EGOS Standard Pattern

> **Version:** 1.0.0 — 2026-04-06
> **Status:** SSOT — replicate for any API, MCP, or validation service
> **First implementation:** Guard Brasil `/sandbox` (`apps/guard-brasil-web/app/sandbox/`)
> **CLAUDE.md §18:** This pattern must be disseminated to every viable EGOS product

---

## What It Is

A **4-zone interactive web page** that lets users test a live API or service with:
1. Pre-validated scenarios (reproducible, hash-verifiable)
2. Free-form input (real-time call, in-place result highlighting)
3. Session audit trail (client-side only, exportable as signed JSON)
4. Inline free tier signup (zero friction, API key activated immediately)

**Why it matters for sales:** Every B2B compliance/API sale requires a "try before you buy" moment with receipts. This pattern delivers that moment in < 60 seconds, with the receipt built in.

---

## When to Use This Pattern

Apply this pattern to any EGOS product that:

| Criterion | Examples |
|-----------|---------|
| Has a REST or MCP API | Guard Brasil, Gem Hunter API, Eagle Eye API, Knowledge Base API |
| Processes or validates input | PII detection, procurement scanning, document classification |
| Needs to build trust with B2B buyers | Compliance tools, fintech integrations, legal tools |
| Has verifiable outputs | Hash receipts, scores, classifications, structured results |
| Needs a low-friction first touchpoint | Free tier onboarding, partner demos, conference demos |

**Not needed for:** pure UI products, internal-only tools, tools with no input/output model.

---

## The 4 Zones

### Zone 1 — Pre-validated Scenarios
- **What:** A curated set of scenarios with known inputs and pre-recorded outputs
- **Why:** Builds confidence before a user types anything. "We ran this 20 times, here's the hash."
- **Implementation:** Load from a static JSON file (`public/sandbox-dataset.json`) with pre-recorded API responses + receipt hashes
- **Key feature:** "Run Live" button per scenario re-runs against the actual API and shows delta
- **Trust signal:** If live result matches pre-recorded hash → green verification badge

### Zone 2 — Free-form Sandbox
- **What:** Open text/data input field with real API call and in-place result highlighting
- **Why:** User brings their own data, sees it processed in real time
- **Implementation:** Textarea → `POST /v1/inspect` (or equivalent) → colour-coded highlights by finding category
- **Trust signals:** `inspectionHash` displayed, `inputHash` verified client-side via `crypto.subtle`
- **Presets:** 3-4 curated example inputs for the target vertical (speeds up first use)

### Zone 3 — Session Audit Trail
- **What:** Rolling table of every inspection in this session (seq, timestamp, truncated input, findings, `inspectionHash`, latency, source)
- **Why:** DPOs and compliance buyers need to show evidence of consistent masking. This exports that evidence.
- **Implementation:** Client-side state only — nothing persisted on server. Export as JSON triggers blob download in browser.
- **Trust signal:** "Nenhum texto é armazenado — apenas hashes SHA-256 irreversíveis"
- **Format:** Sequential, timestamped, with source (`scenario` vs `live`)

### Zone 4 — Inline Free Tier Signup
- **What:** Email + project name → `POST /v1/keys` → API key auto-fills into Zone 2 input
- **Why:** Zero-friction conversion at the moment of maximum intent (just saw the product work)
- **Implementation:** Inline form, no redirect, key displayed immediately and activated
- **Key:** Never force account creation before value is delivered — signup is at the bottom, after value

---

## File Structure (Standard)

```
apps/{product}-web/
├── app/
│   └── sandbox/
│       ├── page.tsx              ← Next.js server wrapper + SEO metadata
│       └── sandbox-client.tsx    ← All UI logic ('use client')
└── public/
    └── sandbox-dataset.json      ← Pre-recorded scenarios + receipt hashes
```

### `sandbox-dataset.json` schema

```json
{
  "generated_at": "ISO-8601",
  "api_endpoint": "https://product.domain/v1/endpoint",
  "api_version": "semver",
  "tests": [
    {
      "id": "NN_descriptive_name",
      "body": { /* full API response snapshot */ },
      "stats": { "http_status": 200, "time_total": 0.9, "size": 1153 }
    }
  ],
  "latency_samples": [ /* optional p50/p95 measurements */ ]
}
```

### Scenario metadata (`SCENARIO_META` in client)

Since `sandbox-dataset.json` stores API responses (not inputs — for privacy), the component holds a `SCENARIO_META` map:

```typescript
const SCENARIO_META: Record<string, { label: string; input: string; category: string }> = {
  'NN_scenario_id': { label: 'Human label', input: 'Example input text', category: 'category_slug' },
};
```

---

## How to Generate `sandbox-dataset.json`

Run the scenario inputs against the live API and capture responses:

```bash
# Template script (adapt per product)
ENDPOINT="https://product.domain/v1/endpoint"
INPUTS=(
  "scenario 1 input"
  "scenario 2 input"
  # ...
)
for input in "${INPUTS[@]}"; do
  curl -s -w '\n{"time_total":%{time_total},"size":%{size_download},"http_status":%{http_code}}' \
    -X POST "$ENDPOINT" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"$input\"}"
done
```

Store output as `public/sandbox-dataset.json`. Regenerate monthly or on API version bump.

---

## Component Architecture

### Separation of concerns

| File | Responsibility |
|------|---------------|
| `page.tsx` | SSR + SEO metadata only. Zero logic. |
| `sandbox-client.tsx` | All state, API calls, UI. `'use client'`. |
| `sandbox-dataset.json` | Pre-recorded responses. Static. Never modified at runtime. |

### Key hooks pattern

```typescript
// 3 pieces of async state per zone
const [running, setRunning] = useState(false);
const [result, setResult] = useState<ResultType | null>(null);
const [duration, setDuration] = useState(0);

// Universal inspect wrapper
async function runInspect(input: string, key?: string) {
  setRunning(true);
  const t0 = performance.now();
  try {
    const resp = await fetch(ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(key ? { 'Authorization': `Bearer ${key}` } : {}) },
      body: JSON.stringify({ text: input }),
    });
    const result = await resp.json();
    setResult(result);
    setDuration(Math.round(performance.now() - t0));
    await addAuditEntry(input, result, duration, 'sandbox');
  } finally {
    setRunning(false);
  }
}
```

### Hash verification pattern (trust building)

```typescript
async function sha256hex(text: string): Promise<string> {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
}

// In ResultPanel: verify inputHash client-side
useEffect(() => {
  if (!input || !result.receipt?.inputHash) return;
  sha256hex(input).then(computed => setHashVerified(computed === result.receipt!.inputHash));
}, [input, result.receipt?.inputHash]);
```

---

## Adapting for Different Products

### Guard Brasil → already live
Route: `/sandbox` | Dataset: 20 PII test scenarios | Highlighting: regex category colour map

### Gem Hunter API
- Scenarios: 20 trending repos across domains (AI, compliance, fintech, devtools)
- Highlighting: score bands (HOT / QUALIFIED / DISCARD) with colour coding
- Zone 3 exports: search session as a "research audit" JSON
- Zone 4: API key for Gem Hunter `/v1/scan` endpoint

### Eagle Eye (Licitações)
- Scenarios: 20 procurement opportunities from real PNCP data (anonymised)
- Highlighting: opportunity score, territory, value band
- Zone 3 exports: prospect pipeline as JSON
- Zone 4: Trial account for the monitored territory list

### Knowledge Base API
- Scenarios: 20 wiki queries with known high-quality answers
- Highlighting: confidence score, source citations
- Zone 3 exports: query session for team review

### br-acc / BRACC
- Scenarios: 20 police record queries with known patterns
- Highlighting: risk level, entity type, jurisdiction
- Zone 4: access request form

---

## Pre-flight Checklist

Before launching a sandbox for a new product:

- [ ] API endpoint is live and responding < 2s p95
- [ ] `sandbox-dataset.json` generated with ≥ 10 scenarios covering main use cases
- [ ] `SCENARIO_META` populated with human labels and example inputs
- [ ] Category colour map defined (or reuse Guard Brasil colours for generic use)
- [ ] Zone 4 signup endpoint live (`POST /v1/keys` or equivalent)
- [ ] SEO metadata in `page.tsx` (title, description, OG)
- [ ] Link added to product landing page nav
- [ ] Link added to product docs page nav
- [ ] `sandbox-dataset.json` committed to git (not generated at runtime)
- [ ] No API keys or secrets in the component (key is user-supplied or anonymous)

---

## Design Constants

These are fixed across all sandbox implementations for visual consistency:

```typescript
const BRAND_COLORS = {
  base: 'bg-slate-950',
  surface: 'bg-slate-900',
  border: 'border-slate-800',
  accent: 'text-emerald-400',         // Guard Brasil green
  accentBg: 'bg-emerald-900/20',
  live: 'text-emerald-400',
  warning: 'text-amber-400',
  error: 'text-red-400',
  muted: 'text-slate-400',
};
```

Category colour map lives in the component file (not shared CSS) so each product can customise it.

---

## SEO Metadata Template

```typescript
// page.tsx
export const metadata: Metadata = {
  title: 'Sandbox Auditável — {Product Name}',
  description:
    'Teste a API {Product} ao vivo com seus próprios dados. {N} cenários pré-validados, resultados em tempo real, recibos criptograficamente verificáveis. Free tier {X} chamadas/mês.',
};
```

---

## References

| File | Description |
|------|-------------|
| `apps/guard-brasil-web/app/sandbox/sandbox-client.tsx` | Reference implementation |
| `apps/guard-brasil-web/public/sandbox-dataset.json` | Reference dataset format |
| `apps/guard-brasil-web/app/sandbox/page.tsx` | Reference page wrapper |

---

*SSOT: this file. When adapting, copy the reference implementation, rename, and update `SCENARIO_META` + `BRAND_COLORS` + dataset.*
