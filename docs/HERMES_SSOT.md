# HERMES_SSOT — LLM Execution Engine

> **VERSION:** 1.0.0 | **CREATED:** 2026-04-08
> **PURPOSE:** Single source of truth for the EGOS LLM execution engine (post-Codex decommission)
> **STATUS:** LIVE — Hermes systemd service running on local + VPS
> **REPLACES:** Codex Proxy + OpenClaw billing proxy (decommissioned 2026-04-08 — ChatGPT subscription cancelled)

<!-- llmrefs:start -->
## LLM Reference Signature

- **Role:** SSOT for Hermes agent runtime + DashScope/OpenRouter LLM provider chain
- **Summary:** Documents how EGOS calls LLMs after Codex decommission. Provider chain, Hermes service, integration points, troubleshooting.
- **Read next:**
  - `packages/shared/src/llm-providers/hermes.ts` — TypeScript provider implementation
  - `docs/CAPABILITY_REGISTRY.md` §16 — capability matrix entry
  - `scripts/x-opportunity-alert.ts#analyzeWithLLM` — first production consumer
<!-- llmrefs:end -->

---

## 1. What Hermes Is

Hermes is **two things** that share the same name in this codebase. Don't confuse them:

### 1.1 Hermes Agent (NousResearch)
- Python-based AI agent runtime — `~/.hermes-agent` (local) + `/opt/hermes-agent` (VPS)
- Provides: persistent TUI, 40+ tools (bash/file/CDP), scheduled automations, skills (procedural memory), messaging gateway, sub-agent spawning
- Runs as systemd service `hermes-gateway` on VPS (port 18800, MemoryMax=512M)
- License: MIT (NousResearch)

### 1.2 Hermes LLM Provider (`packages/shared/src/llm-providers/hermes.ts`)
- TypeScript module exposing `callHermes(prompt, options)` and `generateText(prompt, systemPrompt?)`
- Wraps the **provider chain** (DashScope qwen-plus → OpenRouter free fallback)
- Returns `{ content, provider, model }`
- This is what application code (HQ actions, x-opportunity-alert, gem-hunter, etc.) actually imports

**Convention:** when the code says "hermes" without further qualification, it usually means **the provider** (1.2). The agent (1.1) is referenced as `hermes-gateway` or `hermes-agent`.

---

## 2. Provider Chain (Priority Order)

| # | Provider | Model | Endpoint | Key Env Var | Cost |
|---|----------|-------|----------|-------------|------|
| 1 | Alibaba DashScope | `qwen-plus` | `dashscope-intl.aliyuncs.com/compatible-mode/v1` | `ALIBABA_DASHSCOPE_API_KEY` | Free tier (8 models) |
| 2 | OpenRouter | `google/gemma-4-26b-a4b-it:free` | `openrouter.ai/api/v1` | `OPENROUTER_API_KEY` | Free |
| 3 | OpenRouter | `qwen/qwen3-coder:free` | (same) | (same) | Free — reserved for coding tasks |

**Fallback rules:**
- Primary fails (HTTP 4xx/5xx, timeout 10s) → fall through to OpenRouter
- OpenRouter fails (timeout 15s) → return `null` (caller decides degradation)
- Never throw — caller checks `null`/`undefined` and degrades gracefully

**Why this order?**
- DashScope `qwen-plus` is cheapest + fastest + has the largest free quota in our footprint (testing 2026-04-07)
- OpenRouter `gemma-4-26b` is the model from the original "Gemma 4 + OpenClaw" research post — proves we don't need a paid Anthropic key
- Anthropic API key was removed 2026-04-07 (key invalid, OAuth flow fails on VPS)

---

## 3. Hermes Gateway Service (VPS)

```bash
# Service file: /etc/systemd/system/hermes-gateway.service
[Service]
EnvironmentFile=/root/.hermes/.env
ExecStart=/opt/hermes-venv/bin/python cli.py --gateway
Restart=always
RestartSec=15
MemoryMax=512M
CPUQuota=80%
```

**Status check:**
```bash
ssh -i ~/.ssh/hetzner_ed25519 root@204.168.217.125 "systemctl status hermes-gateway"
```

**Config file (`/root/.hermes/config.yaml`):**
```yaml
provider: alibaba_dashscope
model: openai/qwen-plus
timezone: America/Sao_Paulo
```

**Env file (`/root/.hermes/.env` — not in git):**
```bash
ALIBABA_DASHSCOPE_API_KEY=<set>
ALIBABA_DASHSCOPE_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
OPENROUTER_API_KEY=<set>
```

**Restart after env changes:**
```bash
systemctl daemon-reload && systemctl restart hermes-gateway
```

---

## 4. TypeScript Provider API

```typescript
import { callHermes, generateText } from '@egos/shared/llm-providers/hermes';

// Low-level — full control
const result = await callHermes("Resume this in 1 line: ...", {
  maxTokens: 200,
  temperature: 0.3,
});
// → { content: "...", provider: "alibaba/qwen-plus", model: "qwen-plus" }

// Convenience wrapper
const text = await generateText("What is LGPD?", "You are a Brazilian legal expert.");
```

**Source:** `packages/shared/src/llm-providers/hermes.ts` (103 lines, 0 deps beyond fetch)

---

## 5. Production Consumers

| Consumer | File | Use case |
|----------|------|----------|
| X Opportunity Alert | `scripts/x-opportunity-alert.ts#analyzeWithLLM` | AI analysis injected in Telegram alerts |
| HQ Constitutional Review | `apps/egos-hq/app/api/hq/actions/codex-review/route.ts` | Replaces former Codex proxy call |
| (Pending) Hermes Agent skills | `~/.hermes-agent/skills/*` | When skills are auto-created post-trial |

---

## 6. Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| HTTP 401 from DashScope | Wrong endpoint (cn vs intl) | Use `dashscope-intl.aliyuncs.com`, not `dashscope.aliyuncs.com` |
| HTTP 403 `AllocationQuota.FreeTierOnly` | Old key with exhausted free tier | Generate new key in DashScope console |
| HTTP 429 from OpenRouter | Rate limit on free model | Retry — usually clears in seconds |
| `hermes-gateway` not running | Token expired or env file missing | Check `/root/.hermes/.env`, `systemctl status hermes-gateway`, `journalctl -u hermes-gateway -n 50` |
| Anthropic 401 | OAuth key invalid | DON'T re-add — Hermes was migrated off Anthropic 2026-04-07 |

---

## 7. What Was Removed (Decommission Audit Trail — 2026-04-08)

| Component | Was at | Status |
|-----------|--------|--------|
| Codex CLI proxy | `~/.openclaw-codex-proxy/proxy.js` (port 18802) | systemd disabled, processes killed |
| OpenClaw billing proxy | `openclaw-billing-proxy.service` (port 18801) | systemd disabled |
| OpenClaw gateway | container `openclaw` (port 18789) | container removed |
| `openclaw.egos.ia.br` | Caddy route | DNS kept, returns 502 (manifest annotated) |
| Constitutional review cron (Codex) | `~/.openclaw-codex/jobs/constitutional-review.sh` | replaced by HQ action via DashScope |

**Why removed:** ChatGPT Plus subscription cancelled (2026-04-07). Maintaining a proxy for an unavailable service was dead code with active failure modes.

**Recovery (if ever needed):** Codex proxy code is still in git history. To restore: `git show <commit>~1:.openclaw-codex-proxy/proxy.js`. But there is no path back without resubscribing.

---

## 8. Trial & Roadmap

- **Trial period:** 2026-04-07 → 2026-04-15
- **Decision gate (HERMES-005-P4):** Go/no-go on scaling to 6 profiles (egos-kernel, egos-strategy, egos-governance, egos-research, egos-ops, egos-learning)
- **Post-MVP (HERMES-006..009):** Multi-profile, Hindsight memory integration, Gem Hunter v7 cron, watchdog

Tasks: see `TASKS.md` §Hermes MVP Deployment

---

## 9. Related SSOTs

- `docs/CAPABILITY_REGISTRY.md` §16 — capability matrix entry
- `docs/CAPABILITY_REGISTRY.md` §19 — Hermes Agent runtime details
- `docs/INFRA_SSOT.md` — VPS service mapping (when present)
- `packages/shared/src/llm-providers/hermes.ts` — implementation
- `~/.claude/CLAUDE.md` §16 — global LLM execution rule
