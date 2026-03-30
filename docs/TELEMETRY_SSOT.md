# TELEMETRY SSOT — Single Source of Truth

> **VERSION:** 1.0.0 | **STATUS:** Canonical | **Updated:** 2026-03-30
> **Purpose:** Unified telemetry schema across all EGOS repos. Every repo can extend, but all must inherit base.

---

## Architecture Decision

**Problem:** 5 different telemetry implementations (egos/shared, 852, carteira-livre, intelink, forja)

**Solution:**
1. **@egos/shared/telemetry.ts** is CANONICAL base
2. Each repo extends with domain-specific types
3. Dual output: Supabase + JSON logs (docker-friendly)
4. Privacy-safe: IP hashing, no raw credentials

---

## Base Schema (CANONICAL)

Every event MUST have these fields:

```typescript
export interface TelemetryEventBase {
  // Core
  event_type: string; // 'api_call', 'chat_completion', 'error', etc.
  timestamp: string;  // ISO8601, set by recorder

  // Costs & Performance
  tokens_in?: number;      // Input tokens consumed
  tokens_out?: number;     // Output tokens generated
  cost_usd?: number;       // Total cost for this event
  duration_ms?: number;    // Wall-clock duration

  // AI Model
  model_id?: string;       // 'qwen-plus', 'claude-opus', 'gemini-2.0', etc.
  provider?: string;       // 'alibaba', 'openrouter', 'anthropic'

  // Context
  client_ip_hash?: string; // sha256(ip), not raw IP
  request_id?: string;     // Trace across requests
  user_id?: string;        // If authenticated (hashed)

  // Results
  status_code?: number;    // 200, 429, 500, etc.
  error_message?: string;  // Only if error

  // Extension
  metadata?: Record<string, unknown>; // Repo-specific data
}

export interface TelemetryConfig {
  logPrefix: string;           // '852', 'guard-brasil', 'intelink', etc.
  tableName?: string;          // Supabase table
  supabaseClient?: SupabaseClient;
  dualOutput?: boolean;        // Console JSON + DB (default: true)
  costTrackingEnabled?: boolean;
}
```

---

## Domain Extensions (Per Repo)

### 🔐 Guard Brasil Extension

```typescript
export type GuardBrasilEventType =
  | 'api_call'           // Base type
  | 'pii_inspection'     // PII scan
  | 'atrian_validation'  // Ethical scoring
  | 'policy_pack_check'  // Policy enforcement
  | 'rate_limit_hit';    // Quota exceeded

export interface GuardBrasilTelemetry extends TelemetryEventBase {
  event_type: GuardBrasilEventType;

  // Guard-specific
  api_key_hash?: string;           // Customer identifier (hashed)
  policy_pack?: 'security' | 'health' | 'judicial' | 'financial';
  pii_types_detected?: string[];   // ['cpf', 'rg', 'masp']
  atrian_score?: number;           // 0-100 ethical validation
  text_length?: number;            // Input length
  confidence?: number;             // Detection confidence

  // Business metrics
  is_free_tier?: boolean;
  quota_remaining?: number;

  metadata: {
    ip_geo?: string;               // geo hash, not exact location
    user_agent_type?: 'web' | 'sdk' | 'api'; // Aggregated
    referrer?: string;             // From X.com, email, docs, etc.
  };
}

export const guardBrasilTelemetry = createTelemetryRecorder<GuardBrasilTelemetry>({
  logPrefix: 'guard-brasil',
  tableName: 'guard_brasil_events',
  costTrackingEnabled: true,
});
```

### 🔢 852 Extension (existing, now canonical)

```typescript
export type Issue852EventType =
  | 'chat_completion'
  | 'issue_created' | 'issue_voted' | 'issue_commented'
  | 'user_login' | 'user_registered'
  | 'email_verified' | 'email_code_sent'
  | 'feedback_submitted'
  | 'news_summarization'
  | 'espiral_de_escuta_triggered';

export interface TelemetryEvent852 extends TelemetryEventBase {
  event_type: Issue852EventType;

  // 852-specific
  issue_id?: string;
  user_id?: string;          // Hashed
  sentiment?: 'positive' | 'negative' | 'neutral';
  issue_category?: string;

  metadata: {
    news_source?: string;
    summary_length?: number;
    detected_themes?: string[];
  };
}
```

### 💳 Carteira Livre Extension (logging-focused)

```typescript
export type CarteiraTelemetryEventType =
  // Auth events
  | 'auth_attempt' | 'auth_success' | 'auth_failure' | 'session_expired'
  // Payment events
  | 'payment_initiated' | 'payment_completed' | 'payment_failed' | 'payment_refunded'
  | 'pix_generated' | 'asaas_webhook_received'
  // Booking/Lesson events
  | 'booking_created' | 'booking_confirmed' | 'booking_cancelled'
  | 'lesson_started' | 'lesson_completed' | 'lesson_expired'
  // User events
  | 'instructor_registered' | 'instructor_kyc_submitted' | 'instructor_approved' | 'instructor_rejected'
  | 'student_registered' | 'student_profile_updated'
  | 'partner_action'
  // System events
  | 'database_query' | 'database_error'
  | 'api_error' | 'api_timeout' | 'rate_limit_hit'
  | 'telegram_notification' | 'whatsapp_sent' | 'email_sent'
  | 'cron_executed' | 'webhook_received';

export interface TelemetryCarte extends TelemetryEventBase {
  event_type: CarteiraTelemetryEventType;

  // Carteira-specific (extended logging)
  level: 'error' | 'warn' | 'info' | 'debug';
  category: 'auth' | 'payment' | 'booking' | 'instructor' | 'student' | 'partner' | 'api' | 'database' | 'telegram' | 'whatsapp' | 'system' | 'vercel' | 'supabase';

  stack_trace?: string;        // Only for errors
  request_path?: string;
  request_method?: string;
  user_agent?: string;
  ip_address_hash?: string;    // Hashed IP for privacy

  telegram_notified?: boolean;

  // Business IDs (for tracing)
  lesson_id?: string;
  instructor_id?: string;
  student_id?: string;
  payment_id?: string;

  metadata: {
    // Payment
    payment_method?: 'pix' | 'card' | 'boleto';
    amount_brl?: number;
    currency?: string;

    // Error context
    probable_cause?: string;
    impact?: string;
    recommended_action?: string;
    where_to_attack?: string[];
    how_to_fix?: string[];
    evidence?: string[];
    next_steps?: string[];

    // Deployment context
    deployment_id?: string;
    region?: string;

    // Additional context
    [key: string]: unknown;
  };
}

// Carteira Livre specific recorder factory
export const carteiraLivreTelemetry = createTelemetryRecorder<TelemetryCarte>({
  logPrefix: 'carteira-livre',
  tableName: 'carteira_livre_events',
  supabaseClient: supabase, // From env
  dualOutput: true, // Console JSON + Supabase
});
```

### 🌐 Intelink Extension (client-side perf)

```typescript
export type IntelinkEventType =
  | 'page_view'
  | 'user_action'
  | 'performance'
  | 'error_caught';

export interface TelemetryIntelink extends TelemetryEventBase {
  event_type: IntelinkEventType;

  // Client-side specific
  page_path?: string;
  action_type?: string;
  element_id?: string;

  // Performance
  first_paint?: number;
  first_contentful_paint?: number;
  cumulative_layout_shift?: number;

  metadata: {
    browser?: string;
    device_type?: 'mobile' | 'tablet' | 'desktop';
    viewport_size?: string;
    network_type?: 'wifi' | '4g' | '5g' | 'slow';
  };
}
```

### 🔍 Forja Extension (transparency-focused)

```typescript
export type ForjaEventType =
  | 'transparency_report'
  | 'system_health'
  | 'cost_breakdown'
  | 'quota_usage';

export interface TelemetryForja extends TelemetryEventBase {
  event_type: ForjaEventType;

  // Forja-specific
  system?: 'vercel' | 'supabase' | 'vps' | 'ali_dashscope';
  health_status?: 'healthy' | 'degraded' | 'down';

  metadata: {
    component?: string;
    uptime_percentage?: number;
    response_time_ms?: number;
  };
}
```

---

## Implementation Pattern

### Step 1: Create repo-specific recorder

```typescript
// In packages/guard-brasil/src/telemetry.ts
import { createTelemetryRecorder } from '@egos/shared';

export const guardBrasilTelemetry = createTelemetryRecorder({
  logPrefix: 'guard-brasil',
  tableName: 'guard_brasil_events',
  supabaseClient: supabase, // From env
  costTrackingEnabled: true,
});

// Export typed recorder functions
export const recordApiCall = (event: GuardBrasilTelemetry) =>
  guardBrasilTelemetry.recordEvent(event);
```

### Step 2: Use in your code

```typescript
// In /v1/inspect endpoint
async function handleInspect(req) {
  const startTime = Date.now();

  try {
    const result = await GuardBrasil.inspect(req.text);

    // Record success
    await guardBrasilTelemetry.recordEvent({
      event_type: 'pii_inspection',
      cost_usd: result.cost,
      duration_ms: Date.now() - startTime,
      model_id: result.llm_used,
      status_code: 200,
      api_key_hash: hashApiKey(req.headers.authorization),
      pii_types_detected: result.pii_found,
      atrian_score: result.atrian.score,
      policy_pack: req.policy_pack,
      is_free_tier: !isPro(req.api_key),
      metadata: {
        referrer: req.headers.referer,
        text_length: req.text.length,
      },
    });
  } catch (error) {
    // Record error
    await guardBrasilTelemetry.recordEvent({
      event_type: 'api_call',
      status_code: 500,
      error_message: error.message,
      duration_ms: Date.now() - startTime,
      metadata: { error_type: error.constructor.name },
    });
  }
}
```

---

## Supabase Schema (Auto-created)

```sql
-- Guard Brasil events table
CREATE TABLE guard_brasil_events (
  id BIGSERIAL PRIMARY KEY,

  -- Base fields
  event_type TEXT NOT NULL,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  -- Cost tracking
  tokens_in INTEGER,
  tokens_out INTEGER,
  cost_usd NUMERIC(10, 8),
  duration_ms INTEGER,

  -- AI Model
  model_id TEXT,
  provider TEXT,

  -- Context
  client_ip_hash TEXT,
  request_id TEXT,
  user_id TEXT,
  api_key_hash TEXT,  -- Guard-specific

  -- Status
  status_code INTEGER,
  error_message TEXT,

  -- Guard Brasil specific
  policy_pack TEXT,
  pii_types_detected TEXT[],
  atrian_score NUMERIC(3, 1),
  text_length INTEGER,
  is_free_tier BOOLEAN,
  quota_remaining INTEGER,

  -- Metadata (JSONB for flexibility)
  metadata JSONB,

  -- Indexing for performance
  CONSTRAINT chk_cost_positive CHECK (cost_usd >= 0),
  INDEX idx_timestamp ON guard_brasil_events(timestamp DESC),
  INDEX idx_event_type ON guard_brasil_events(event_type),
  INDEX idx_api_key_hash ON guard_brasil_events(api_key_hash),
);

-- Enable RLS
ALTER TABLE guard_brasil_events ENABLE ROW LEVEL SECURITY;

-- Policies: customers see only their data
CREATE POLICY guard_brasil_select
  ON guard_brasil_events
  FOR SELECT
  USING (api_key_hash = current_user_api_key_hash());
```

---

## Telemetry Data Flow

```
Guard Brasil API (/v1/inspect)
  ↓
recordEvent({event_type, cost_usd, duration_ms, ...})
  ↓
TelemetryRecorder (from @egos/shared)
  ├─→ [1] JSON console log: {"logPrefix":"guard-brasil","event_type":"pii_inspection",...}
  │   (parseable by docker logs, Datadog, etc.)
  │
  └─→ [2] Supabase INSERT: guard_brasil_events table
      ↓
      Realtime Webhook triggers → Dashboard WebSocket
      ↓
      Customer sees event in live Activity Feed
```

---

## Monitoring & Alerts

```typescript
// Example: Create alert for high costs
const highCostThreshold = 0.05; // $0.05 per request = unusual

// In admin panel query
SELECT
  DATE(timestamp) as date,
  COUNT(*) as requests,
  SUM(cost_usd) as total_cost,
  AVG(cost_usd) as avg_cost,
  MAX(cost_usd) as max_cost
FROM guard_brasil_events
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;

// Alert if max_cost > 0.05
```

---

## Rollout Plan

| Phase | Week | Action |
|-------|------|--------|
| **1** | This week | Move `@egos/shared/telemetry.ts` to CANONICAL status, document |
| **2** | Week 2 | Integrate Guard Brasil (create guard_brasil_events table) |
| **3** | Week 3 | Integrate 852 (update with canonical base if needed) |
| **4** | Week 4 | Integrate Carteira Livre (gradual migration from old system) |
| **5** | Week 5+ | Intelink + Forja (nice-to-have) |

---

## Cost Example: Guard Brasil With Telemetry

```
1 customer, 5,000 API calls/mo:

API cost:        R$0.02 × 5,000 = R$100/mo
LLM cost:        $0.00007 × 5,000 = $0.35/mo (Qwen)
Telemetry:       ~1MB × 5,000 = 5MB/mo → Supabase free tier
Storage (1yr):   5MB × 12 = 60MB → Well within Supabase limits

TOTAL: R$100 + $0.35 = ~R$102/mo
```

✅ **Telemetry is FREE at this scale!**

---

## FAQ

**Q: Por que Supabase e não um data warehouse?**
A: Supabase é grátis, tem Realtime, e query é SQL direto. Data warehouse (Snowflake, Redshift) é overkill para <1GB/ano.

**Q: E se temos 1M eventos/dia?**
A: Mude para Clickhouse ou Big Query. Mas naquele cenário já temos receita de R$50k+/mo para pagar.

**Q: GDPR compliance?**
A: IP hashing + api_key_hash (não raw keys) + RLS policies = compliant. Dados podem ser deletados via GDPR requests (soft delete com flag).

**Q: Como rastrear fraude/abuso?**
A: Agregue por api_key_hash + timestamp, detect padrões de request. Exemplo: 1k requests em 1 segundo = abuse.
