# OpenClaw Configuration Plan

**Status:** Container ready on Hetzner (18789 WS), awaiting Telegram bot token + LLM provider keys

---

## Current State
- **Container:** openclaw-sandbox running on Hetzner (port 18789 WebSocket)
- **Auth token:** `a61b80d29a0adb334cf3ab1370818387817d79d8b0c1ab19`
- **Access:** `wss://openclaw.egos.ia.br` (DNS record pending)
- **Default model:** anthropic/claude-opus-4-6

---

## Telegram Integration (Priority 1)

### Prerequisites
- Telegram Bot Token: get from @BotFather
- Chat ID for logs: developer group ID
- Bot commands: `/run`, `/status`, `/logs`, `/config`

### Config File
```bash
docker exec openclaw-sandbox cat > /home/node/.openclaw/integrations/telegram.json << 'EOF'
{
  "enabled": true,
  "botToken": "YOUR_TOKEN_HERE",
  "allowedChats": [123456789],
  "commands": {
    "run": "Execute task with AI",
    "status": "Show running tasks",
    "logs": "Fetch recent logs",
    "config": "Show current config"
  },
  "rateLimit": "10 msgs/min"
}
EOF
```

---

## LLM Provider Chain (Priority 1-2)

### 1. Alibaba (Primary) — ✅ Already Configured
- **API Key:** `$ALIBABA_DASHSCOPE_API_KEY` (env)
- **Models:**
  - `qwen-turbo` (fast, cheap) — simple tasks
  - `qwen-plus` (balanced) — complex tasks
  - `qwen-max` (expensive) — reasoning-heavy

### 2. OpenRouter (Fallback) — Free + Paid
- **API Key:** `$OPENROUTER_API_KEY` (get from https://openrouter.ai/keys)
- **Free models:**
  - `mistral-7b` — language tasks
  - `openhermes-2.5` — reasoning
- **Paid models (good ROI):**
  - `claude-3-haiku` — $0.25/M
  - `gpt-4-turbo` — $0.01-0.03/K

### 3. Codex (Testing)
- **Auth:** `~/.codex/config.json` (may fail)
- **Model:** `gpt-4o` (code generation)

### 4. Gemini CLI (Pro Account)
- **Auth:** `gcloud auth application-default login`
- **Models:** `gemini-2.0-flash` (free), `gemini-pro` (reasoning)

### Provider Routing Config
```json
{
  "providers": [
    {
      "name": "alibaba",
      "priority": 10,
      "models": [
        { "id": "qwen-turbo", "cost": 0.0008, "maxTokens": 4000 },
        { "id": "qwen-plus", "cost": 0.004, "maxTokens": 8000 },
        { "id": "qwen-max", "cost": 0.012, "maxTokens": 32000 }
      ]
    },
    {
      "name": "openrouter",
      "priority": 5,
      "models": [
        { "id": "mistral-7b", "cost": 0, "free": true },
        { "id": "claude-3-haiku", "cost": 0.00025, "maxTokens": 4000 }
      ]
    },
    {
      "name": "codex",
      "priority": 3,
      "models": [
        { "id": "gpt-4o", "cost": 0.015, "maxTokens": 128000 }
      ]
    },
    {
      "name": "gemini",
      "priority": 2,
      "models": [
        { "id": "gemini-2.0-flash", "cost": 0, "free": true },
        { "id": "gemini-pro", "cost": 0.0005, "maxTokens": 32000 }
      ]
    }
  ],
  "routing": {
    "simple": ["qwen-turbo", "mistral-7b"],
    "balanced": ["qwen-plus", "claude-3-haiku"],
    "complex": ["qwen-max", "gpt-4-turbo", "gemini-pro"],
    "reasoning": ["gemini-pro", "claude-opus-4-6"]
  }
}
```

---

## Setup Steps

### Step 1: Obtain Tokens
```bash
# Alibaba — already set
echo $ALIBABA_DASHSCOPE_API_KEY

# OpenRouter
visit https://openrouter.ai/keys

# Codex
codex auth login

# Gemini
gcloud auth application-default login
```

### Step 2: Deploy Config to Container
```bash
ssh root@204.168.217.125
docker exec openclaw-sandbox cat > /home/node/.openclaw/llm-config.json << 'EOF'
{...provider config above...}
EOF
```

### Step 3: Create Telegram Bot
- Chat: @BotFather in Telegram
- Get token, add to telegram.json
- Test: `/run "list models"`

### Step 4: Restart Container
```bash
docker compose -f /opt/openclaw/docker-compose.yml restart openclaw-sandbox
docker exec openclaw-sandbox cat /tmp/openclaw/openclaw-*.log | tail -20
```

### Step 5: Test Each Provider
```bash
# Via Telegram
/run "test alibaba turbo"
/run "test openrouter mistral"
/run "test gemini-pro reasoning"
/run "generate code snippet with codex"
/logs
```

---

## Cost Estimate
- **Alibaba turbo:** $0.008/day = $0.24/month
- **OpenRouter free:** $0
- **Gemini free:** $0
- **Codex (if used):** variable
- **Total:** ~$0.25-0.50/month (low usage)

---

## Security
1. Container isolated (no FS beyond `/app/data`)
2. API keys via env vars (never in git)
3. Telegram token in config (rotatable)
4. Rate limit: 10 msgs/min per chat
5. Audit logs → Telegram admin group

---

## Files to Create/Update
- `/opt/openclaw/docker-compose.yml` ✅ (done)
- `/opt/openclaw/.env` (API keys)
- Container: `/home/node/.openclaw/llm-config.json` (provider routing)
- Container: `/home/node/.openclaw/integrations/telegram.json` (bot config)
- Container: `/etc/systemd/system/openclaw-watch.service` (auto-restart)

---

## Your Action Items
1. ✍️ Create Telegram bot via @BotFather (get token)
2. ✍️ Get OpenRouter API key
3. 🧪 Test Codex auth (expect unknown result)
4. 🧪 Test Gemini CLI auth (gcloud)
5. 📝 Update `/home/enio/egos/TASKS.md` with OpenClaw checklist
