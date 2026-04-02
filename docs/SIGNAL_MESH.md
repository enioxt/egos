# SIGNAL_MESH — Signal Extraction Capacity Matrix
**Version:** 1.0.0 | **Last updated:** 2026-04-02 | **Owner:** gem-hunter + world-model agents

---

## 1. What is SIGNAL_MESH?

In intelligence operations, this is a **Collection Management Plan** — the meta-SSOT that answers:

> *"For any topic we care about: what signals exist, from which sources, with what capacity, handled by which agent, producing what output SSOT?"*

SIGNAL_MESH is the **wiring diagram** between sources, topics, agents, and outputs.
It prevents duplicate collection, enforces cost-awareness, and ensures quality-weighted routing.

### SSOT Hierarchy position
```
TASKS.md (priority)
  → agents.json (registry)
    → SIGNAL_MESH.md  ← YOU ARE HERE (collection plan)
      → signals.json, kol-list.json, next-queries.json (outputs)
```

---

## 2. Signal Sources Table

| Source | Type | Rate Limit | Cost/day | Quality | Agent | Output SSOT |
|--------|------|------------|----------|---------|-------|-------------|
| X API (Bearer) | Social | 500K tokens/mo (Basic) | ~$0.30 | ★★★★★ | gem-hunter, kol-discovery | signals.json |
| X Following (@anoineim) | Social | same pool | free | ★★★★★ | kol-discovery | kol-list.json |
| Telegram channels | Social | bot API: unlimited read | free | ★★★★☆ | gem-hunter | signals.json |
| arXiv API | Academic | 3 req/s, no auth | free | ★★★★★ | gem-hunter (PWC pipeline) | papers.json |
| Papers With Code | Academic | no official limit | free | ★★★★★ | gem-hunter | papers.json |
| GitHub Trending | Dev | 5K req/hr (auth) | free | ★★★★☆ | gem-hunter | signals.json |
| GitHub API (stars/forks) | Dev | 5K req/hr | free | ★★★★☆ | gem-hunter | signals.json |
| HackerNews Algolia | News | ~10K req/hr | free | ★★★☆☆ | world-model | signals.json |
| Reddit (r/crypto, r/MachineLearning) | Social | 100 req/min (OAuth) | free | ★★★☆☆ | gem-hunter | signals.json |
| Exa search | Web | 1K queries/mo (free tier) | ~$0.01/q | ★★★★☆ | kol-discovery, world-model | next-queries.json |
| HuggingFace trending | ML | no rate limit | free | ★★★★☆ | gem-hunter | papers.json |
| CoinGecko API | Markets | 30 req/min (free) | free | ★★★☆☆ | gem-hunter | signals.json |
| DeFiLlama | Markets | public, no limit stated | free | ★★★★☆ | gem-hunter | signals.json |
| Dune Analytics | On-chain | 10 req/s (free tier) | free | ★★★★☆ | gem-hunter | signals.json |
| DashScope (Alibaba) | LLM | quota per key | ~$0.50 | ★★★★☆ | gem-hunter (inference) | — |
| RSS aggregator | News | unlimited | free | ★★★☆☆ | drift-sentinel | signals.json |

---

## 3. Topic × Source Matrix

Quality score 1–5 for each topic/source pairing. Empty = not relevant.

| Topic | X API | Telegram | arXiv/PWC | GitHub | HN | Reddit | Exa | CoinGecko | DeFiLlama |
|-------|-------|----------|-----------|--------|----|----|-----|-----------|-----------|
| **Crypto gems** | 5 | 5 | 2 | 3 | 3 | 4 | 3 | 5 | 5 |
| **AI agents / LLMs** | 4 | 3 | 5 | 5 | 5 | 4 | 4 | — | — |
| **EGOS governance** | 2 | 2 | 2 | 4 | 3 | 2 | 3 | — | — |
| **OSINT / LGPD** | 3 | 3 | 2 | 3 | 2 | 2 | 5 | — | — |
| **Markets / macro** | 4 | 4 | 1 | 1 | 4 | 3 | 3 | 5 | 4 |
| **Dev tooling / infra** | 3 | 2 | 3 | 5 | 5 | 3 | 3 | — | — |
| **Brazilian govtech** | 3 | 3 | 1 | 2 | 1 | 1 | 5 | — | — |

**Routing rule:** When a topic cell scores ≥ 4, that source is PRIMARY for the topic. Below 3 = skip unless PRIMARY unavailable.

---

## 4. KOL Networks

### 4.1 X Following (@anoineim)
- **Owner:** kol-discovery agent (`scripts/kol-discovery.ts`)
- **Discovery:** AUTOMATIC — uses `X_BEARER_TOKEN` to fetch full following list via X API v2
  - `GET /2/users/by/username/anoineim` → user ID
  - `GET /2/users/:id/following` (paginated, up to 1000 accounts)
  - Classifies by bio: crypto / ai-ml / dev-tooling / governance / markets
  - Run: `bun scripts/kol-discovery.ts` → `docs/gem-hunter/kol-list.json`
- **Policy:** Pull 2×/week (Mon + Thu); update kol-list.json automatically
- **Note:** No manual list maintenance needed — always reflects current following

### 4.2 Telegram Channels
| Channel | Topic | Bot | Env Var | Status |
|---------|-------|-----|---------|--------|
| Admin | Crypto gems / alerts | `TELEGRAM_ADMIN_CHAT_ID` | `TELEGRAM_BOT_TOKEN` | ✅ Active |
| AI Agents | AI tools, LLM, agents | `egosaiagents_bot` | `TELEGRAM_BOT_TOKEN_AI_AGENTS` | ✅ Configured |
| Markets | Crypto, macro, DeFi | `egosmarkets_bot` | `TELEGRAM_BOT_TOKEN_MARKETS` | ✅ Configured |

**Routing rules:**
- Gems category=`agents` / `ai-ml` → egosaiagents_bot
- Gems category=`crypto` / `markets` / `defi` → egosmarkets_bot
- Score ≥ 80 (any category) → TELEGRAM_BOT_TOKEN (admin)

**Bot policy:** Read-only listener. Never post to alpha channels from automated bots.

### 4.3 GitHub Network
- Watch: repos starred by top-20 KOLs in `kol-list.json`
- Alert threshold: ≥ 200 stars/week velocity OR ≥ 50 new forks in 48h

---

## 5. Capacity Rules

### 5.1 Anti-spam
- X API: max 1 query/topic/source combination per poll cycle
- Exa: batch similar queries; never query same URL twice within 24h
- Reddit: respect crawl-delay in robots.txt (10s default)

### 5.2 Anti-poisoning
- Cross-validate any signal scoring ≥ 7/10 against ≥ 2 independent sources
- Reject accounts created < 30 days ago from gem signals (X + Telegram)
- Flag anomalous volume spikes (>3x 7-day average) as potential wash signals

### 5.3 Deduplication
- Canonical signal ID: `sha256(source + entity_id + timestamp_day)`
- Dedup window: 24h for news, 7d for paper discoveries, 30d for project signals
- Output: deduplicated writes to `signals.json` (append-only, keyed by canonical ID)

### 5.4 Cost budget
- Hard cap: $15/month across all paid sources
- Priority order: free → freemium → paid
- Exa budget: reserve 200 queries/month for gem-hunter, 300 for kol-discovery, 500 for world-model

---

## 6. Agent Assignments

| Agent | Primary Sources | Secondary Sources | Output |
|-------|----------------|-------------------|--------|
| `gem-hunter` | arXiv, PWC, GitHub Trending, CoinGecko, DeFiLlama | X API, Reddit, Telegram | signals.json, papers.json |
| `kol-discovery` | X Following (@anoineim), X Lists, Exa | Telegram, GitHub | kol-list.json |
| `drift-sentinel` | GitHub API (egos repos), RSS, HN | Exa | TASKS.md (blockers), governance-drift.md |
| `world-model` | HN, Reddit, Exa, arXiv | X API, RSS | next-queries.json, signals.json |
| `guard-brasil` | Exa (LGPD/gov news), RSS (DOU) | Reddit Brazil | signals.json (govtech slice) |

**Ownership rule:** Each source has exactly ONE primary agent owner. Secondary agents may READ but not write collection state.

---

## 7. Update Cadence

| Source | Poll interval | Rationale |
|--------|--------------|-----------|
| X Following timeline | 2×/day (9h, 21h BRT) | Avoid rate exhaustion, catch AM+PM cycles |
| Telegram channels | Real-time (bot listener) | Low latency alpha |
| arXiv / PWC | 1×/day (6h BRT) | Daily paper drops |
| GitHub Trending | 1×/day (7h BRT) | Daily ranking refresh |
| HackerNews | 4×/day | Fast-moving news |
| Reddit | 2×/day | Moderate velocity |
| CoinGecko / DeFiLlama | 4×/day | Market volatility |
| Exa | On-demand (agent-triggered) | Budget-controlled |
| Dune Analytics | 1×/day | On-chain data latency |

**Scheduled jobs alignment:** CCR `Gem Hunter Adaptive` (Mon+Thu 2h37 BRT) triggers a full multi-source sweep. Daily `Governance Drift Sentinel` (0h17 BRT) owns GitHub + RSS only.

---

## 8. Evolution Path

### Short-term (next 30 days)
- [ ] Wire Telegram bot listener to `gem-hunter` signal ingestion pipeline
- [ ] Populate `kol-list.json` from @anoineim following (bootstrap)
- [ ] Add `LIST_ID_CRYPTO_GEMS` from @anoineim X lists
- [ ] Implement dedup hash store (Redis or simple SQLite file)

### Medium-term (next 90 days)
- [ ] Discord server listeners (major DeFi/AI protocol servers)
- [ ] Farcaster/Warpcast feed (crypto-native social layer)
- [ ] On-chain event listeners via Alchemy/Infura webhooks
- [ ] Community-contributed KOL lists (CSV import → kol-list.json merge)

### Governance
- SIGNAL_MESH is a frozen-zone document after v1.0 — changes require explicit user approval
- Source additions: must include rate limit, cost, quality score, and agent assignment
- Deletions: archive to `SIGNAL_MESH_ARCHIVE.md`, never delete rows (audit trail)

---

*SIGNAL_MESH is part of EGOS SSOT hierarchy. Next downstream: `signals.json`, `kol-list.json`, `next-queries.json`, `papers.json`*
