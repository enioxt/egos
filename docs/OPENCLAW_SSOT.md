# OPENCLAW_SSOT.md — Single Source of Truth

> **Updated:** 2026-04-06 | **Version:** 1.0.0
> **Purpose:** Canonical reference for all OpenClaw configuration, integration, and status in the EGOS ecosystem.

---

## 1. WHAT IS OPENCLAW

OpenClaw is a personal multi-channel AI gateway (WhatsApp, Telegram, Discord, Slack, iMessage, etc.) with extensible messaging integrations. EGOS uses it as a local agent runtime for multi-channel chatbot delivery.

- **Repo:** https://github.com/openclaw/openclaw
- **Docs:** https://docs.openclaw.ai
- **Skills marketplace:** ClawHub (https://clawhub.ai)
- **EGOS strategic posture:** Adapter layer on top of OpenClaw ecosystem — not a competing platform. See `docs/research/plugplay-governance-landscape-2026-03-14.md`.

---

## 2. INSTALLATION STATE

| Component | Path | Version | Status |
|-----------|------|---------|--------|
| OpenClaw binary | `~/.npm-global/lib/node_modules/openclaw/` | 2026.4.5 | ✅ Active (systemd) |
| Gateway systemd unit | `~/.config/systemd/user/openclaw-gateway.service` | — | ✅ enabled + running |
| Gateway port | `localhost:18789` | — | ✅ UP |
| Billing proxy | `~/.openclaw-billing-proxy/proxy.js` | zacdcook/openclaw-billing-proxy | ✅ Active (systemd) |
| Billing proxy port | `localhost:18801` | — | ✅ UP |

**Install command (reinstall):**
```bash
npm install --prefix ~/.npm-global -g openclaw@latest
systemctl --user restart openclaw-gateway
```

---

## 3. CONFIGURATION FILES

### 3.1 Main OpenClaw Config
**Path:** `~/.openclaw/openclaw.json`
```json
{
  "mcp": {"servers": {"codebase-memory-mcp": {"command": "/home/enio/.local/bin/codebase-memory-mcp"}}},
  "gateway": {"mode": "local"},
  "agents": {
    "defaults": {
      "model": "anthropic-subscription/claude-sonnet-4-6",
      "compaction": {"mode": "safeguard"},
      "maxConcurrent": 4
    }
  }
}
```
**Config schema note (v2026.4.5):** Key is `mcp.servers` (not `mcpServers`). Requires `gateway.mode: "local"` to start without full setup.

MCP servers registered here are available to the OpenClaw agent.

### 3.2 Model Providers
**Path:** `~/.openclaw/agents/main/agent/models.json`

Two providers configured (VPS uses `172.19.0.1:18801` instead of `127.0.0.1:18801`):

| Provider | API type | Models | Notes |
|----------|----------|--------|-------|
| `openrouter` | `openai-completions` | Gemini 2.0 Flash | Via OpenRouter API — paid per token |
| `anthropic-subscription` | `anthropic-messages` | Sonnet 4.6, Haiku 4.5, Opus 4.6 | **Via billing proxy → Claude Code subscription (zero cost)** |

**Critical gotchas (discovered 2026-04-06):**
1. `apiKey` is **required** in provider config when `models` are defined (schema validation rejects without it — causes silent empty model list, "Unknown model" error)
2. Anthropic API type is `"anthropic-messages"` NOT `"anthropic"` (registered in `pi-ai/providers/register-builtins.js`)
3. `auth-profiles.json` must have entry with `"provider": "anthropic-subscription"` (not `"anthropic"`) for the embedded agent to resolve auth

**Test:** `openclaw agent --to @test --message "Say: PIPELINE_OK"` → should show response + proxy `requestsServed: 1`

**To use subscription models:** set `agents.defaults.model: "anthropic-subscription/claude-sonnet-4-6"` in `openclaw.json`.

### 3.3 Workspace Identity
**Path:** `~/.openclaw/workspace/`

| File | Purpose | Status |
|------|---------|--------|
| `SOUL.md` | Agent identity: "Guarani", PT-BR tutor persona | ACTIVE — loaded every session |
| `AGENTS.md` | Operating manual: memory rules, heartbeat, safety | ACTIVE |
| `USER.md` | User profile (minimal — needs expansion) | STUB |
| `TOOLS.md` | Local env (cameras, SSH, voices — empty) | TEMPLATE |
| `HEARTBEAT.md` | Periodic cron tasks (empty) | TEMPLATE |

---

## 4. BILLING PROXY (openclaw-billing-proxy)

**Repo:** https://github.com/zacdcook/openclaw-billing-proxy
**Install path:** `~/.openclaw-billing-proxy/`
**Systemd unit:** `~/.config/systemd/user/openclaw-billing-proxy.service`

**How it works:**
1. OpenClaw sends API request to `http://127.0.0.1:18801` (proxy)
2. Proxy sanitizes OpenClaw-specific trigger phrases (11 patterns)
3. Proxy injects Claude Code billing header into system prompt
4. Proxy sends request to `api.anthropic.com` using Claude Code's OAuth token
5. Response reverse-mapped (10 patterns) → returned to OpenClaw

**Billing header injected:**
```
x-anthropic-billing-header: cc_version=2.1.80.a46; cc_entrypoint=sdk-cli; cch=00000;
```

**Token source:** `~/.claude/.credentials.json` (read-only, refreshed by Claude Code daily)
**Subscription type:** `max`

**Health check:**
```bash
curl http://127.0.0.1:18801/health
```

**Manage:**
```bash
systemctl --user status openclaw-billing-proxy
systemctl --user restart openclaw-billing-proxy
```

---

## 5. INTEGRATION WITH EGOS GATEWAY

OpenClaw gateway (port 18789) and EGOS gateway (port 3050) are independent services. They are NOT yet bridged.

**Planned integration:**
- Route EGOS Gateway Telegram/WhatsApp traffic → OpenClaw agent runtime (multi-channel)
- OpenClaw handles: voice, multi-device, skill marketplace
- EGOS Gateway handles: LGPD/PII, business logic, Supabase, Gem Hunter API

**Pending task:** HERMES integration (MASTER_HANDOFF_2026-04-03_tutor_hermes_integration.md)

---

## 5.1 VPS DEPLOYMENT (Hetzner — 2026-04-06)

| Component | Location | Status |
|-----------|----------|--------|
| OpenClaw container | `openclaw-sandbox` (alpine/openclaw:latest v2026.3.24) | ✅ Running |
| Container network | `infra_bracc` (172.19.0.9) + internal (172.23.0.2) | ✅ |
| Gateway WebUI | `https://openclaw.egos.ia.br` → `openclaw-sandbox:18789` via Caddy | ✅ HTTP 200 |
| Gateway bind | `gateway.bind: "lan"` + `auth.mode: "token"` | ✅ |
| Volume | `openclaw_openclaw-data` → `/var/lib/docker/volumes/openclaw_openclaw-data/_data` | ✅ |
| Billing proxy | `/root/.openclaw-billing-proxy/` (systemd: `openclaw-billing-proxy.service`) | ✅ Active |
| Billing proxy bind | `0.0.0.0:18801` (reachable from Docker bridge 172.19.0.1) | ✅ |
| Telegram channel | `@egosmarkets_bot` (token MARKETS — distinct from EGOS Gateway's `@EGOSin_bot`) | ✅ Connected |
| anthropic-subscription provider | `http://172.19.0.1:18801` (VPS host from container) | ✅ Configured |
| Claude credentials | `/root/.claude/.credentials.json` (copied from local, OAuth token) | ⚠️ Needs periodic sync |

**Caddy upstream gotcha:** Caddy container (`infra-caddy-1`) cannot reach host via `127.0.0.1`. Must use container name `openclaw-sandbox:18789` since both are in `infra_bracc` network. Write Caddyfile via `cat file | docker exec -i infra-caddy-1 tee /etc/caddy/Caddyfile` to preserve bind mount inode.

**Billing proxy bind gotcha:** Default binds to `127.0.0.1` only — patched to `0.0.0.0` in `proxy.js:336` so container gateway (172.19.0.1) can reach it.

**Telegram channel conflict avoidance:** EGOS Gateway (port 3050) already polls `@EGOSin_bot` (token `TELEGRAM_BOT_TOKEN_AI_AGENTS`). OpenClaw uses a distinct bot (`@egosmarkets_bot`, token `TELEGRAM_BOT_TOKEN_MARKETS`) to avoid `409 Conflict: terminated by other getUpdates request`.

**Token sync:** `~/.claude/.credentials.json` rotates daily via Claude Code. Copy is STATIC on VPS — needs cron or rsync schedule to stay valid. Currently 5.8h of validity remaining at deploy time.

---

## 6. STRATEGIC POSITION

From `docs/research/plugplay-governance-landscape-2026-03-14.md`:

> "EGOS should become an adapter layer on top of OpenClaw ecosystem, not try to outbuild them."
> "Integrate with OpenClaw / agentregistry / Composio instead of building a competing platform."

**OpenClaw strengths EGOS leverages:**
- 13K+ skills on ClawHub marketplace
- Multi-channel delivery (20+ channels)
- Sessions API (`sessions_spawn`, `sessions_yield`) for multi-agent orchestration
- MCP-native integration (OpenClaw A2A Gateway)

**EGOS value-add on top:**
- LGPD/PII compliance layer (Guard Brasil)
- Governance rules (.guarani/)
- Knowledge base (wiki pages, FTS)
- Brazilian market specialization

---

## 7. ACTIVE TASKS

| Task | Status | Notes |
|------|--------|-------|
| Billing proxy installed | ✅ Done (2026-04-06) | systemd + subscription:max |
| Gateway crash-loop fixed | ✅ Done (2026-04-06) | Reinstalled v2026.4.5 |
| anthropic-subscription provider | ✅ Done (2026-04-06) | models.json updated |
| VPS billing proxy installed | ✅ Done (2026-04-06) | systemd `openclaw-billing-proxy.service`, bound 0.0.0.0:18801 |
| VPS Telegram (@egosmarkets_bot) | ✅ Done (2026-04-06) | Distinct bot to avoid conflict with EGOS Gateway |
| openclaw.egos.ia.br routing | ✅ Done (2026-04-06) | Caddy `→ openclaw-sandbox:18789`, HTTP 200 |
| Wire OpenClaw + Hermes | ⬜ Pending | MASTER_HANDOFF_2026-04-03 |
| Local Telegram channel | ⬜ Pending | OC-001 — add bot token to `~/.openclaw/openclaw.json` |
| VPS credentials cron sync | ⬜ Pending | `~/.claude/.credentials.json` rotates daily — needs rsync job |
| Populate USER.md | ⬜ Pending | Add full Enio profile |
| Configure HEARTBEAT.md | ⬜ Pending | Add monitoring tasks |

---

## 8. CLEANUP DONE (2026-04-06)

- `BOOTSTRAP.md` — deleted (one-time startup, now obsolete per AGENTS.md)
- `gems-2026-04-02.md` in egos-lab — archived (superseded by 2026-04-06 version)
- `IDENTITY.md` conflict with `SOUL.md` — IDENTITY.md kept as minimal stub, SOUL.md is canonical agent identity

---

## 9. RELATED DOCS

| Doc | Location | Purpose |
|-----|----------|---------|
| Strategic analysis | `docs/research/plugplay-governance-landscape-2026-03-14.md` | EGOS vs OpenClaw ecosystem positioning |
| Latest gem research | `docs/gem-hunter/gems-2026-04-06.md` | Market intelligence, OpenClaw ecosystem |
| Hermes integration plan | `docs/_current_handoffs/MASTER_HANDOFF_2026-04-03_tutor_hermes_integration.md` | Integration roadmap |
| Capability registry | `docs/CAPABILITY_REGISTRY.md` (§OpenClaw) | One-liner capability entry |

---

*SSOT created: 2026-04-06 | Maintained by: EGOS session /disseminate protocol*
