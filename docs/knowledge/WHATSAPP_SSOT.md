# WhatsApp Integration SSOT — EGOS Ecosystem

> **VERSION:** 1.0.0 | **CREATED:** 2026-03-30
> **PURPOSE:** Canonical patterns for WhatsApp channel integration across EGOS products
> **VALIDATED IN:** forja (2026-03-30)

---

## Philosophy

**WhatsApp is a workflow surface, not an open-chat platform.**

Meta's current policies (as of 2026-01) restrict "general AI assistants" on WhatsApp. Position WhatsApp as:
- Status notifications
- Transaction confirmations
- Workflow triggers (quote→order, alert→action)
- Human escalation surface

**NOT as:** Open conversational AI, general-purpose assistant, or unrestricted bot.

---

## Architecture Pattern

### Runtime SSOT: Centralized Evolution API

```
┌─────────────────────────────────────────────────┐
│            Hetzner VPS (SSOT Runtime)           │
│  ┌───────────────────────────────────────────┐  │
│  │      Evolution API (Single Instance)      │  │
│  │  Port: 8080  │  Mode: Baileys or Cloud    │  │
│  ├───────────────────────────────────────────┤  │
│  │  Instances (One per product/channel):     │  │
│  │  - forja-notifications                    │  │
│  │  - 852-customer-service (future)          │  │
│  │  - carteira-x-transactions (future)       │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
         │                    │
         ↓                    ↓
┌─────────────────┐   ┌──────────────────┐
│  Vercel App     │   │  Supabase DB     │
│  - Webhooks     │   │  - Audit logs    │
│  - API routes   │   │  - State/metrics │
│  - Dashboard    │   │  - Compliance    │
└─────────────────┘   └──────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  Redis (Future — P1)                │
│  - Message queue                    │
│  - Retry/dead-letter                │
│  - Rate limiting/throttle           │
└─────────────────────────────────────┘
```

### Key Decisions

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| **Hetzner as runtime SSOT** | Single source of truth for all WhatsApp operations | VPS maintenance burden |
| **One Evolution API deployment** | Simpler ops, shared config | Single point of failure (mitigated by Docker restart) |
| **One instance per channel** | Isolation, independent lifecycle | More API surface to manage |
| **Vercel for app/webhook only** | Leverage serverless scale | Can't run WhatsApp runtime on Vercel |
| **Baileys for dev/low-volume** | No Meta approval needed | 14-day timeout, QR re-pairing |
| **Cloud API for prod/high-volume** | Official, stable, higher limits | Requires Meta Business approval |

---

## Pattern #1: Evolution API Deployment

**Canonical bundle:** `integrations/manifests/whatsapp-runtime.json` + `integrations/distribution/whatsapp-runtime/`

### Docker Compose Template

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: evolution-postgres
    restart: unless-stopped
    environment:
      - POSTGRES_USER=evolution
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=evolution
    volumes:
      - evolution_postgres:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U evolution"]
      interval: 10s
      timeout: 5s
      retries: 5

  evolution-api:
    image: atendai/evolution-api:latest
    container_name: evolution-api
    restart: unless-stopped
    ports:
      - "8080:8080"
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - SERVER_URL=http://YOUR_VPS_IP:8080
      - AUTHENTICATION_API_KEY=${EVOLUTION_API_KEY}
      - DATABASE_ENABLED=true
      - DATABASE_PROVIDER=postgresql
      - DATABASE_CONNECTION_URI=postgresql://evolution:${DB_PASSWORD}@postgres:5432/evolution
      - RABBITMQ_ENABLED=false
      - CACHE_REDIS_ENABLED=false
      - CONFIG_SESSION_PHONE_VERSION=2.3000.1033994345
    volumes:
      - evolution_instances:/evolution/instances
      - evolution_store:/evolution/store

volumes:
  evolution_postgres:
  evolution_instances:
  evolution_store:
```

### Critical Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `SERVER_URL` | External URL for webhooks | `http://204.168.217.125:8080` |
| `AUTHENTICATION_API_KEY` | API authentication | Generate with `openssl rand -hex 32` |
| `CONFIG_SESSION_PHONE_VERSION` | Baileys session compatibility | `2.3000.1033994345` (fixes QR bug) |
| `DATABASE_ENABLED` | MUST be `true` | `true` (even if optional in docs) |
| `DATABASE_PROVIDER` | MUST be `postgresql` | `postgresql` |

### Deployment Commands

```bash
# SSH to Hetzner
ssh root@hetzner

# Create deployment directory
mkdir -p /opt/evolution-api
cd /opt/evolution-api

# Create .env file
cat > .env <<EOF
EVOLUTION_API_KEY=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -hex 16)
EOF

# Deploy
docker compose up -d

# Verify
docker logs evolution-api --tail 50
curl http://localhost:8080 | jq '.status'
```

---

## Pattern #2: QR Drift Recovery

### Problem

Evolution API QR code generation can fail with:
- Empty modal (QR never appears)
- `{ "count": 0 }` response from `/instance/connect/{instance}`
- Accessibility warnings in Manager UI (red herring — not the root cause)

### Root Cause

Baileys session version drift between Evolution API image and WhatsApp production runtime.

### Recovery Protocol

```
1. Validate instance exists
   → GET /instance/fetchInstances
   → Confirm instance name is correct

2. Test connect endpoint
   → GET /instance/connect/{instance}
   → If returns { "count": 0 }, proceed to step 3

3. Inspect runtime logs
   → docker logs evolution-api
   → Look for session/version errors

4. Apply session version fix
   → Add CONFIG_SESSION_PHONE_VERSION=2.3000.1033994345 to docker-compose.yml
   → Recreate container: docker compose up -d --force-recreate evolution-api

5. Validate QR generation
   → GET /instance/connect/{instance}
   → Should return base64 QR + "qrcodeCount": 1 in logs

6. Retry pairing in Manager UI
   → Only after runtime validation passes
```

### Validated Fix (2026-03-30)

```bash
# In /opt/evolution-api/docker-compose.yml
environment:
  - CONFIG_SESSION_PHONE_VERSION=2.3000.1033994345

# Recreate container
docker compose up -d --force-recreate evolution-api

# Verify in logs
docker logs evolution-api | grep qrcodeCount
# Expected: "qrcodeCount": 1
```

**Evidence:** forja-notifications instance connected successfully after applying fix.

---

## Pattern #3: Instance Management

### Instance Lifecycle

```
CREATE → CONFIGURE_WEBHOOK → CONNECT (QR) → OPEN → OPERATIONAL
   ↓            ↓                ↓          ↓           ↓
FAILED    RETRY_WEBHOOK    RETRY_QR   DISCONNECTED  RECONNECT
```

### Instance Naming Convention

```
{product}-{purpose}

Examples:
- forja-notifications
- 852-customer-service
- carteira-x-transactions
- egos-admin-alerts
```

### Create Instance (CLI)

```bash
curl -X POST http://YOUR_VPS_IP:8080/instance/create \
  -H "apikey: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "forja-notifications",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS"
  }'
```

### Configure Webhook

```bash
curl -X POST http://YOUR_VPS_IP:8080/webhook/set/forja-notifications \
  -H "apikey: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://forja-orpin.vercel.app/api/notifications/whatsapp",
    "webhook_by_events": true,
    "events": [
      "MESSAGES_UPSERT",
      "MESSAGES_UPDATE",
      "CONNECTION_UPDATE",
      "SEND_MESSAGE"
    ]
  }'
```

### Check Connection State

```bash
curl http://YOUR_VPS_IP:8080/instance/connectionState/forja-notifications \
  -H "apikey: YOUR_API_KEY"

# Expected when connected:
# { "instance": "forja-notifications", "state": "open" }
```

---

## Pattern #4: Application Integration

### Environment Variables (.env)

```env
# Evolution API Configuration (Hetzner SSOT)
EVOLUTION_API_URL=http://204.168.217.125:8080
EVOLUTION_API_KEY=<64-char-hex-from-vps>
EVOLUTION_INSTANCE_NAME=forja-notifications

# Webhook Security (optional but recommended)
WHATSAPP_WEBHOOK_SECRET=<random-secret>

# Admin Phones (E.164 format, comma-separated)
FORJA_ADMIN_PHONES=5534999999999,5534888888888
```

### Notification Service Pattern (TypeScript)

```typescript
// src/lib/whatsapp/notifications.ts
import { EvolutionProvider } from './providers';

export async function sendNotification(params: {
  type: 'production_alert' | 'stock_alert' | 'quote_update' | 'vision_anomaly';
  recipient: string; // E.164 format
  data: Record<string, any>;
}) {
  const provider = new EvolutionProvider({
    apiUrl: process.env.EVOLUTION_API_URL!,
    apiKey: process.env.EVOLUTION_API_KEY!,
    instanceName: process.env.EVOLUTION_INSTANCE_NAME!,
  });

  const template = getTemplate(params.type);
  const message = template(params.data);

  return provider.sendMessage({
    number: params.recipient,
    text: message,
  });
}

function getTemplate(type: string) {
  const templates = {
    production_alert: (data: any) => `
🏭 PRODUÇÃO - Ordem #${data.orderId}

Status: ${data.status}
Etapa: ${data.stage} (${data.progress}%)
Responsável: ${data.assignee}
Prazo: ${data.deadline}

🔗 Ver ordem: ${data.orderUrl}
    `.trim(),

    stock_alert: (data: any) => `
📦 ESTOQUE BAIXO - ${data.productName}

Quantidade atual: ${data.currentStock} ${data.unit}
Mínimo: ${data.minStock} ${data.unit}
Recomendado: ${data.recommendedStock} ${data.unit}

⚠️ Solicitar reposição urgente
    `.trim(),

    // ... more templates
  };

  return templates[type] || (() => 'Template não encontrado');
}
```

### Webhook Handler Pattern (Next.js)

```typescript
// src/app/api/notifications/whatsapp/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/lib/supabase/server';

export async function POST(req: NextRequest) {
  const body = await req.json();
  const supabase = createClient();

  // Log all events for audit
  await supabase.from('audit_log').insert({
    action: 'whatsapp_webhook_received',
    metadata: body,
    created_at: new Date().toISOString(),
  });

  // Handle specific events
  if (body.event === 'MESSAGES_UPSERT') {
    const message = body.data.messages[0];

    // Process incoming message
    // (implement business logic here)
  }

  return NextResponse.json({ status: 'ok' });
}

export async function GET() {
  // Health check endpoint
  const provider = new EvolutionProvider({
    apiUrl: process.env.EVOLUTION_API_URL!,
    apiKey: process.env.EVOLUTION_API_KEY!,
    instanceName: process.env.EVOLUTION_INSTANCE_NAME!,
  });

  const state = await provider.getConnectionState();

  return NextResponse.json({
    status: 'ok',
    connected: state.state === 'open',
    instance: process.env.EVOLUTION_INSTANCE_NAME,
  });
}
```

---

## Pattern #5: Multi-Channel Control Tower (Future)

### Vision

For products managing 10+ WhatsApp channels, Evolution Manager UI is insufficient. Build an internal admin dashboard.

### Planned Features

| Feature | Purpose | Priority |
|---------|---------|----------|
| **Instance Registry** | Canonical list of all channels | P0 |
| **Health Dashboard** | Real-time connection status | P0 |
| **Test Send** | Manual message dispatch per channel | P0 |
| **Webhook Monitor** | Event log viewer | P1 |
| **Message Queue** | Redis-backed queue/retry | P1 |
| **Multi-Agent Routing** | AI policy per channel purpose | P1 |
| **Analytics** | Volume, latency, success rate | P2 |

### Schema (Supabase)

```sql
CREATE TABLE whatsapp_instances (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  instance_name VARCHAR(100) UNIQUE NOT NULL,
  product VARCHAR(50) NOT NULL, -- 'forja', '852', 'carteira-x'
  purpose VARCHAR(100), -- 'notifications', 'customer-service', 'transactions'
  phone_number VARCHAR(20), -- E.164 format
  connection_state VARCHAR(20), -- 'open', 'close', 'connecting'
  last_health_check_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE whatsapp_messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  instance_name VARCHAR(100) REFERENCES whatsapp_instances(instance_name),
  direction VARCHAR(10), -- 'inbound', 'outbound'
  phone_number VARCHAR(20),
  message_text TEXT,
  status VARCHAR(20), -- 'sent', 'delivered', 'read', 'failed'
  sent_at TIMESTAMPTZ,
  delivered_at TIMESTAMPTZ,
  metadata JSONB
);
```

---

## Pattern #6: Secrets Management

### Storage Surfaces

| Surface | What | Where | Rotation |
|---------|------|-------|----------|
| **Hetzner .env** | Evolution API key, DB password | `/opt/evolution-api/.env` | Manual (90 days) |
| **Vercel Env Vars** | Evolution API URL/key, instance name | Vercel dashboard | Manual (90 days) |
| **Local .env.local** | Dev credentials (separate from prod) | `.gitignore`d file | Per developer |
| **Supabase** | Audit logs, never secrets | Public read, RLS-protected | N/A |

### Security Checklist

- [ ] Never commit `.env` or `.env.local` to git
- [ ] Use separate API keys for dev/staging/prod
- [ ] Rotate Evolution API key every 90 days
- [ ] Mask phone numbers in logs (`557****8888`)
- [ ] Log all webhook events to Supabase audit table
- [ ] Implement rate limiting on webhook endpoint
- [ ] Verify webhook signature (if `WHATSAPP_WEBHOOK_SECRET` set)
- [ ] Comply with LGPD/GDPR for phone number storage

---

## Pattern #7: Testing Checklist

### Pre-Production Validation

```bash
# 1. Health check
curl https://your-app.vercel.app/api/notifications/whatsapp

# 2. Test notification (production alert)
curl -X POST https://your-app.vercel.app/api/notifications/test \
  -H "Content-Type: application/json" \
  -d '{
    "type": "production_alert",
    "recipient": "5534999999999"
  }'

# 3. Verify in WhatsApp
# → Admin phone should receive formatted message

# 4. Check audit log
# → Query Supabase audit_log for whatsapp_* actions

# 5. Send inbound message to instance
# → Send WhatsApp message to instance number
# → Verify webhook received in Vercel logs
```

### Notification Types to Test

- [ ] Production alert (order created/updated)
- [ ] Stock alert (low inventory warning)
- [ ] Quote update (approved/rejected)
- [ ] Vision anomaly (camera detected issue)
- [ ] Custom message (ad-hoc broadcast)

### Load Testing (Light)

```bash
# Send 10 notifications simultaneously
for i in {1..10}; do
  curl -X POST https://your-app.vercel.app/api/notifications/test \
    -H "Content-Type: application/json" \
    -d '{"type":"custom","recipient":"5534999999999","message":"Test '$i'"}' &
done
wait

# Expected: All 10 delivered within 10 seconds
```

---

## Common Gotchas

### 1. QR Code Never Appears

**Symptoms:**
- Modal opens but stays empty
- `/instance/connect/{instance}` returns `{ "count": 0 }`

**Root Cause:** Baileys session version drift

**Fix:** Add `CONFIG_SESSION_PHONE_VERSION=2.3000.1033994345` and recreate container

**Validated:** forja-notifications (2026-03-30)

### 2. Database Provider Invalid Error

**Symptoms:**
- `DATABASE_ENABLED=false` → Error: "Database provider invalid"

**Root Cause:** Evolution API requires real database even in "disabled" mode

**Fix:** Deploy PostgreSQL container alongside Evolution API

### 3. Connection Lost After 14 Days

**Symptoms:**
- Instance shows `state: close` after inactivity

**Root Cause:** WhatsApp disconnects Baileys sessions after 14 days without traffic

**Fix:**
- Re-scan QR code
- Or: Implement keep-alive pings (send test message every 7 days)

### 4. Webhook Not Receiving Events

**Symptoms:**
- Messages sent but webhook never called

**Troubleshooting:**
1. Verify webhook URL is correct in Evolution API
2. Check Vercel function logs for incoming requests
3. Test webhook with manual curl to Vercel endpoint
4. Verify Evolution API can reach public internet

### 5. Phone Number Format Errors

**Symptoms:**
- Message send fails with "invalid number"

**Fix:** Always use E.164 format: `5534999999999` (country code + area + number, no spaces/dashes)

---

## Dissemination Checklist

### For Each New Repo Adopting WhatsApp

- [ ] Start from `egos/integrations/distribution/whatsapp-runtime/`
- [ ] Validate manifest with `bun run integration:check`
- [ ] Copy Evolution API docker-compose template
- [ ] Generate unique API key for this product
- [ ] Create instance: `{product}-{purpose}`
- [ ] Configure webhook to app URL
- [ ] Scan QR code (if Baileys mode)
- [ ] Add env vars to Vercel: `EVOLUTION_API_URL`, `EVOLUTION_API_KEY`, `EVOLUTION_INSTANCE_NAME`
- [ ] Implement notification service layer
- [ ] Implement webhook handler
- [ ] Create audit log table in Supabase
- [ ] Test all notification types
- [ ] Document in repo's `docs/WHATSAPP_SETUP_GUIDE.md`
- [ ] Update `docs/INTEGRATIONS_MEMORY.md` with instance details

---

## References

- **Evolution API Docs:** https://doc.evolution-api.com
- **WhatsApp Business API:** https://developers.facebook.com/docs/whatsapp
- **Forja Implementation:** `/home/enio/forja/docs/WHATSAPP_SETUP_GUIDE.md`
- **Forja Session Handoff:** `/home/enio/forja/docs/_current_handoffs/handoff_2026-03-30.md`
- **EGOS HARVEST Pattern #11:** WhatsApp Runtime SSOT + QR Drift Recovery

---

## Task IDs

| Task | Status | Evidence |
|------|--------|----------|
| EGOS-WHATSAPP-001 | ✅ Complete | This SSOT document created |
| FORJA-WHATSAPP-008 | 🟡 70% | Runtime + QR done, notification tests pending |
| FORJA-WHATSAPP-010 | 📋 Planned | Control Tower MVP |
| FORJA-WHATSAPP-011 | 📋 Planned | Redis queue/retry/throughput |
| FORJA-WHATSAPP-012 | 📋 Planned | Multi-agent routing |

---

**CREATED BY:** Claude Code (Sonnet 4.5) — EGOS Kernel
**VALIDATED IN:** forja (2026-03-30)
**STATUS:** Ready for dissemination to 852, carteira-livre, and future products
**SACRED CODE:** 000.111.369.963.1618
