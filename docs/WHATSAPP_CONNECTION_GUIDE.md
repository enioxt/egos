# WhatsApp Connection Guide — EGOS Gateway

## Quick Start

### Prerequisites
- Evolution API running on VPS (port 8080)
- SSH access to Hetzner VPS (`root@204.168.217.125`)
- EVOLUTION_API_KEY configured in `/opt/apps/egos-gateway/.env`

### Option 1: Web Manager (Easiest)

```bash
# Open SSH tunnel to Evolution Manager
ssh -L 8181:localhost:8080 -i ~/.ssh/hetzner_ed25519 root@204.168.217.125 -N &

# Access in browser
open http://localhost:8181/manager
```

**In Manager UI:**
1. Find instance `forja-notifications`
2. Click "Scan QR"
3. Open WhatsApp on phone → Settings → Connected devices → Link a device
4. Scan QR code
5. Wait for status to change to `open`

### Option 2: API Direct (If QR expires)

```bash
# SSH to VPS
ssh -i ~/.ssh/hetzner_ed25519 root@204.168.217.125

# Get fresh QR code
APIKEY=$(grep EVOLUTION_API_KEY /opt/apps/egos-gateway/.env | cut -d= -f2-)
curl -s http://localhost:8080/instance/connect/forja-notifications \
  -H "apikey: $APIKEY" | python3 -c "
import sys,json,base64
d=json.load(sys.stdin)
b64=d.get('base64','').split(',',1)[-1]
with open('/tmp/whatsapp-qr.png','wb') as f:
    f.write(base64.b64decode(b64))
print('QR saved: /tmp/whatsapp-qr.png')
"
```

### Verify Connection Status

```bash
APIKEY=$(grep EVOLUTION_API_KEY /opt/apps/egos-gateway/.env | cut -d= -f2-)
curl -s http://localhost:8080/instance/connectionState/forja-notifications \
  -H "apikey: $APIKEY" | jq '.instance.state'
```

Expected output: `"open"` (connected)

## Architecture

```
WhatsApp (phone)
    ↓ (webhook)
Evolution API (port 8080)
    ↓ (http://egos-gateway:3050/channels/whatsapp/webhook)
EGOS Gateway (port 3050)
    ↓ (LLM orchestration)
Qwen-plus (DashScope)
    ↓ (save to Supabase)
egos_chat_history (persistent memory)
```

## Key URLs & Endpoints

| Service | URL | Auth |
|---------|-----|------|
| Evolution Manager | `localhost:8181/manager` | EVOLUTION_API_KEY (global) |
| Evolution API | `localhost:8080` | EVOLUTION_API_KEY header |
| EGOS Gateway | `gateway.egos.ia.br:3050` or `localhost:3050` (via docker) | None (internal) |
| WhatsApp Webhook | `http://egos-gateway:3050/channels/whatsapp/webhook` | Evolution API → Gateway (internal network) |

## Connection Troubleshooting

### Status: `open` but not connecting
- QR code may have expired (valid ~60s)
- Generate new QR: `curl -X DELETE http://localhost:8080/instance/logout/forja-notifications && sleep 2 && curl http://localhost:8080/instance/connect/forja-notifications`
- Rescan immediately

### Status: `connecting` (stuck)
- Disconnect and logout: `curl -X DELETE http://localhost:8080/instance/logout/forja-notifications`
- Wait 5s
- Reconnect: `curl http://localhost:8080/instance/connect/forja-notifications`
- Rescan new QR within 60s

### Webhook not receiving messages
- Check network: `docker network ls | grep evolution`
- Verify gateway is in evolution network: `docker inspect egos-gateway | grep -A5 NetworkSettings`
- Test internal connectivity: `docker exec egos-gateway wget -qO- http://evolution-api:8080/instance/fetchInstances`

## EGOS Gateway Integration

### Webhook Endpoint
- **URL:** `POST /channels/whatsapp/webhook`
- **Location:** `apps/egos-gateway/src/channels/whatsapp.ts`
- **Features:**
  - Accepts text, audio, image, video, document, sticker
  - Audio transcription (Groq Whisper)
  - Image description (Qwen VL)
  - Persistent memory (Supabase `egos_chat_history`)
  - 14 tools (system_status, guard_test, gem_search, wiki_search, memory_search, etc.)

### Configuration

```env
# .env (local and VPS)
EVOLUTION_API_URL=http://evolution-api:8080
EVOLUTION_INSTANCE=forja-notifications
EVOLUTION_API_KEY=<64-char hex key>
WA_AUTHORIZED_NUMBER=553492374363  # restrict to this number
```

### Testing

```bash
# Send test message via webhook
curl -X POST http://localhost:3050/channels/whatsapp/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{
      "key": {"remoteJid": "553492374363@s.whatsapp.net"},
      "message": {"conversation": "olá, qual é meu projeto principal?"}
    }]
  }'
```

## Common Commands

```bash
# List all instances
curl -s http://localhost:8080/instance/fetchInstances \
  -H "apikey: $EVOLUTION_API_KEY"

# Get connection state
curl -s http://localhost:8080/instance/connectionState/forja-notifications \
  -H "apikey: $EVOLUTION_API_KEY"

# View webhook config
curl -s http://localhost:8080/webhook/find/forja-notifications \
  -H "apikey: $EVOLUTION_API_KEY"

# Check gateway health
curl http://localhost:3050/health

# View gateway logs
docker logs egos-gateway --tail 50 -f
```

## Related Files

- **Gateway:** `apps/egos-gateway/src/channels/whatsapp.ts`
- **Orchestrator:** `apps/egos-gateway/src/orchestrator.ts` (14 tools, LLM logic)
- **Memory:** Supabase table `egos_chat_history` (persists all conversations)
- **VPS Config:** `/opt/apps/egos-gateway/.env`
- **Docker Compose:** `docker-compose.yml` (evolution-api_default network)

---

**Last updated:** 2026-04-05 22:30 (Claude Haiku)
