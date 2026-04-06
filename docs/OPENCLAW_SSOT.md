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
  "mcpServers": {
    "codebase-memory-mcp": {
      "command": "/home/enio/.local/bin/codebase-memory-mcp"
    }
  }
}
```
MCP servers registered here are available to the OpenClaw agent.

### 3.2 Model Providers
**Path:** `~/.openclaw/agents/main/agent/models.json`

Three providers configured:
| Provider | Models | Notes |
|----------|--------|-------|
| `openrouter` | Gemini 2.0 Flash, Claude 3 Haiku/Opus | Via OpenRouter API — paid per token |
| `github-copilot` | (empty) | Placeholder |
| `anthropic-subscription` | Sonnet 4.6, Haiku 4.5, Opus 4.6 | **Via billing proxy → Claude Code subscription (zero cost)** |

**To use subscription models:** select `anthropic-subscription` provider in OpenClaw UI. Requires billing proxy running.

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
| Wire OpenClaw + Hermes | ⬜ Pending | MASTER_HANDOFF_2026-04-03 |
| Wire Telegram → OpenClaw | ⬜ Pending | Route egosin_bot to OC gateway |
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
