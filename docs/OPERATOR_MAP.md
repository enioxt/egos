# OPERATOR MAP — EGOS Control Plane

<!-- llmrefs:start -->
## LLM Reference Signature

- **Role:** live control-plane snapshot for services, revenue path, and active agents
- **Summary:** Fast operational map of what is live now, ownership, and immediate operator actions.
- **Read next:**
  - `TASKS.md` — execution backlog and priorities
  - `docs/SYSTEM_MAP.md` — architecture view
  - `docs/SSOT_REGISTRY.md` — truth ownership contracts
<!-- llmrefs:end -->

> **Version:** 1.0.0 | **Updated:** 2026-03-30 | **EGOS-102**
> Scannable in 10 seconds. No prose. Facts only.

---

## 1. System Status — What's Live Right Now

| Service | URL | Status | Owner |
|---------|-----|--------|-------|
| Guard Brasil API | guard.egos.ia.br | LIVE (port 3099, Docker) | egos/apps/api |
| Hetzner VPS | 204.168.217.125 | LIVE (8 Docker services) | infra |
| EGOS Web (Mission Control) | egos.ia.br | LIVE (Vercel, egos-lab) | egos-lab/apps/egos-web |
| FORJA (Gitea) | forja.egos.ia.br | LIVE (Hetzner) | infra |
| Telegram Bot | @egos_bot | LIVE (Hetzner) | egos-lab/apps/telegram-bot |
| Eagle Eye (OSINT) | egos-lab local | DEV (not deployed) | egos-lab/apps/eagle-eye |
| Guard Brasil Web | apps/guard-brasil-web | DEV (Next.js, localhost) | egos/apps/guard-brasil-web |
| br-acc / EGOS-Inteligencia | github.com/enioxt/EGOS-Inteligencia | LIVE (Phase 1 rename done) | br-acc |

---

## 2. Revenue Path — What Generates Money

| Product | Stage | MRR | Next Action |
|---------|-------|-----|-------------|
| Guard Brasil API | API live, 0 paying customers | R$0 | M-007: send 5 outreach emails → demos → LOIs |
| Guard Brasil npm pkg | Built, not published | R$0 | M-001: `npm publish --access public` |
| Guard Brasil SaaS tiers | Designed (Free/49/199/499) | R$0 | Dep: M-007 closes first customer |
| EGOS-Inteligencia (br-acc) | Rename Phase 1 done | R$0 | M-003: rename Phase 2+3 (Python/Docker) |
| Eagle Eye (OSINT) | Internal use only | R$0 | No active GTM — P2 |

**Revenue math (Month 3 projection):** 50 paid calls/day × R$0.0049 = R$7.35/day; 1 Pro tier = R$199/mo

---

## 3. Active Agents — What's Running Autonomously

| Agent | Trigger | Frequency | Last Run |
|-------|---------|-----------|----------|
| guard-brasil health cron | Hetzner crontab `*/5 * * * *` | Every 5min | Continuous |
| SSOT Auditor (egos-lab) | Manual (`bun agent:run ssot-auditor`) | On-demand | 2026-03-30 |
| Drift Sentinel (egos-lab) | Manual (`bun agent:run drift-sentinel`) | On-demand | 2026-03-29 |
| Spec Router | GitHub Actions label trigger | On PR label | Per PR |
| SLA Tracker (spec-pipeline) | GitHub Actions hourly | Hourly | Per PR |
| LLM Router (multi-model) | Code import `routeGuardBrasil()` | Per API call | Per request |
| PRI Safety Gate | Middleware in `/v1/inspect` | Per API call | Per request |

**Note:** 0 verified_agents in kernel runtime. 14 tools, 1 workflow (spec_router). See `agents/registry/agents.json`.

---

## 4. Open Blockers — What's Stopping Progress

| Blocker | Impact | Owner | ETA |
|---------|--------|-------|-----|
| M-007: 5 outreach emails not sent | Zero revenue | Human (Enio) | TODAY |
| M-002: DNS `guard.egos.ia.br` not validated | API unreachable publicly | Human (DNS provider) | <1h |
| M-001: npm publish not done | Package not discoverable | Human (Enio) | 30min |
| M-003: br-acc rename Phase 2+3 | Docker + Python imports stale | Human (Enio) | 2h |
| M-005: Docker network rename + redeploy | EGOS-Inteligencia containers misnamed | Human (Enio) | Dep: M-003 |
| EGOS-132: Brand conflict (2 palettes) | Inconsistent GTM materials | Gabriel Cambraia | P2 |
| EGOS-074: egos-lab → kernel consolidation | Duplicate governance surfaces | Enio | P2 |
| EGOS-085: SSOT registry leaf rollout | 10 repos not declaring SSOT pointers | Enio | P2 |

---

## 5. Quick Commands — 10 Most Used Ops

```bash
# --- Guard Brasil API ---
# Health check (remote)
curl -s https://guard.egos.ia.br/health

# Inspect PII (remote)
curl -s -X POST https://guard.egos.ia.br/v1/inspect \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $GUARD_API_KEY" \
  -d '{"input":"CPF 123.456.789-00"}' | jq .

# --- Hetzner VPS ---
# SSH in
ssh -i ~/.ssh/hetzner_ed25519 root@204.168.217.125

# Check all Docker containers
ssh -i ~/.ssh/hetzner_ed25519 root@204.168.217.125 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'

# Redeploy Guard Brasil API
cd /home/enio/egos && bash apps/api/deploy.sh

# Reload Caddy (after config change)
ssh -i ~/.ssh/hetzner_ed25519 root@204.168.217.125 'docker exec caddy caddy reload --config /etc/caddy/Caddyfile'

# --- Governance ---
# Doctor check (env + governance + providers)
bun scripts/doctor.ts

# Governance drift check
bun run governance:check

# Integration release gate
bun run integration:check

# --- Agents (egos-lab) ---
bun agent:list
bun agent:run <id> --dry
```

---

## 6. Manual Actions Queue (MANUAL_ACTIONS.md)

| ID | Action | Effort | Dep |
|----|--------|--------|-----|
| M-001 | `npm publish` @egosbr/guard-brasil | 30min | npm login |
| M-002 | DNS A record `guard.egos.ia.br` → 204.168.217.125 | 10min | DNS provider access |
| M-003 | br-acc rename Phase 2+3 (Python/Docker) | 2h | none |
| M-005 | Docker network rename + Hetzner redeploy | 1h | M-003 |
| M-007 | Send 5 outreach emails (templates ready) | 1h | M-002 for live demo |

**Templates:** `docs/strategy/OUTREACH_EMAILS.md` | `docs/sales/M007_OUTREACH_STRATEGY_EMAILS.md`

---

*Auto-update: run `bun run governance:sync:exec` after major changes. See `TASKS.md` for full backlog.*
