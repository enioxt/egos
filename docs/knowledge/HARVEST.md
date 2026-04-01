# HARVEST.md — EGOS Core Knowledge

> **VERSION:** 2.9.0 | **UPDATED:** 2026-03-31
> **PURPOSE:** compact accumulation of reusable patterns discovered in the kernel repo
> **Latest:** Caddy Split Routing, Prove-or-Kill Execution, Supabase Dual-Write, Employee-Grade CLAUDE.md

## Caddy Split Routing Pattern (2026-03-31)

### Problem
Single domain needs to serve both API (JSON) and web frontend (HTML). guard.egos.ia.br was showing raw JSON because Caddy routed everything to the API container.

### Solution
Caddy `handle` directive splits by path:
- `/v1/*` + `/health` → API container (guard-brasil-api:3099)
- `/*` → Vercel reverse proxy (guard-brasil-web.vercel.app) with `header_up Host`

### Key Detail
Must set `header_up Host guard-brasil-web.vercel.app` otherwise Vercel rejects the request. Also set `X-Forwarded-Host` for the original domain.

## Prove-or-Kill Execution Pattern (2026-03-31)

### Problem
8 agents registered as "active" but never proven to work. Registry bloat erodes trust.

### Solution
Run each with `--dry` flag, 15s timeout. Three outcomes: WORKS → KEEP, HANGS/CRASHES → KILL, NICHE → KILL.
Result: 3 killed (gtm-harvester, aiox-gem-hunter, mastra-gem-hunter), 5 kept with evidence.

### Rule
Any agent that can't complete `--dry` in 30s is broken. Single-repo scanners are redundant when gem-hunter v3.2 covers 13 sources.

## Supabase Dual-Write Pattern (2026-03-31)

### Problem
Local SQLite works for single-machine but can't power dashboards or cross-session analysis.

### Solution
Write to SQLite first (fast, always available), then async fire-and-forget to Supabase. Supabase failure is non-fatal — `console.warn` and continue.

### Applied To
- gem-hunter: `gem_hunter_gems` + `gem_hunter_runs` tables
- event-bus: `agent_events` table

## Meta-Prompt Generator Pattern (2026-03-31)

### Problem
Users write generic prompts, get generic results. Professional ArchViz requires precise language for cameras, lighting, materials, composition.

### Solution
`prompt-generator.ts` — takes structured `ProjectBriefing` JSON and generates 21 optimized prompts covering every required architectural view.

### ArchViz Rules Codified
- **Camera:** specific lens (24mm exterior, 16mm interior, 50mm aerial), aperture, height
- **Lighting:** golden hour 5500K, night amber, overcast diffused — named precisely
- **Materials:** not "stone wall" but "rough-cut quartzite, irregular blocks, organic texture, weathered patina"
- **Composition:** rule of thirds, leading lines, foreground interest, architectural framing
- **Negative prompts:** "blurry, CGI look, plastic, oversaturated, HDR look" — critical for realism

### 21 Deliverables per Project
8 categories: Exteriores (4), Aereas (2), Secao (1), Interiores (4), Circulacao+Rooftop (2), Area Externa (2), Video (3), Plantas Baixas (3)
Priority: essential (must-have for client presentation), recommended, optional

### Reusable Across EGOS
Any product needing AI-generated visuals can reuse prompt-generator. The `generateProjectPrompts()` function accepts any building type, not just hexagonal houses.

---

## fal.ai Async Queue Pattern (2026-03-31)

### Problem
fal.ai's synchronous `fal.run` endpoint times out on video generation (30s+). Need reliable async pattern.

### Solution
3-step queue pattern:
1. `POST queue.fal.run/{model}` → returns `{ request_id, response_url }`
2. Poll `queue.fal.run/{model}/requests/{id}/status` until `COMPLETED` or `FAILED`
3. `GET response_url` → returns final result with image/video URLs

### Key Details
- Auth: `Authorization: Key $FAL_KEY` (not Bearer)
- Images returned as temporary public URLs (not base64)
- Videos: set `duration` as string ("5", "10"), `aspect_ratio` as "16:9"
- Max poll: 5 minutes with 2s interval is safe for most models
- Together AI is synchronous (no queue needed)
- Google GenAI returns base64 (needs data URI conversion)

---

## Generation Engine Architecture (2026-03-31)

### Problem
ARCH needs to call 3 different providers with different auth, endpoints, and response formats.

### Solution
`generation-engine.ts` — unified `generate(request, apiKeys)` function that auto-routes by `modelId`:
- Lookup `MODEL_CONFIGS[modelId]` → get provider + endpoint
- Switch on provider → call provider-specific function
- Return normalized `GenerationResult` (url, cost, duration, model info)

### 12 Models Registered
| Provider | Models | Auth |
|----------|--------|------|
| fal.ai | Flux Schnell/Dev/Pro, Seedream, Wan 2.5, Kling, Veo 3.1 | Key header |
| Together AI | SDXL, Flux Schnell FREE | Bearer token |
| Google GenAI | Imagen 4 Fast, Imagen 4 Ultra | SDK + API key |

### Cost Per Complete Project
Economy: $0.52 (R$2.85) | Standard: $1.16 (R$6.38) | Premium: $3.17 (R$17.44)

---

## Multi-Model AI Router Pattern (2026-03-30)

### Problem
Products need access to multiple AI models (image, video, 3D) across providers at different cost tiers. Users want model choice + cost visibility.

### Solution
Router pattern with 3 layers:
1. `ai-providers.ts` — Registry of providers + models with real pricing
2. `cost-calculator.ts` — Singleton tracker recording every API call cost (USD + BRL)
3. `ModelSelector.tsx` — UI component showing tiers (economy/standard/premium/ultra)

### Key Decision: API vs Prompt Generator
- **Via API** (fal.ai/Together): 1-click automatic generation, cost per use
- **Via Prompt** (ChatGPT/Gemini): Zero API cost, user pastes in external tool
- **Hybrid** (recommended): Dashboard shows both options with cost comparison

### Top Aggregators (8 researched, 3 selected)
1. fal.ai — 1000+ models, cheapest GPU ($0.99/hr A100), image+video+3D
2. Together AI — $100 free credits, SDXL at $0.002/img, Imagen 4
3. Replicate — Largest community catalog, Vercel AI SDK integration

### Reusable Across EGOS
Any product needing AI generation can reuse this pattern. Cost per complete project: $1.60 (economy) to $3.66 (premium).

## SSOT Visit Protocol Pattern (2026-03-30)

### Problem
Large repos accumulate "lost gems" — files created in one session, never referenced again, invisible to future LLM context windows. Cross-repo work generates silent duplicates with no disposal record.

### Solution
Every contextually distant file read triggers a mandatory log entry:
```
- [x] SSOT-VISIT [date]: [path] → [what extracted] → [disposition]
```
Disposition tags: `archived` | `merged` | `kept-as-ref` | `superseded` | `independent` | `gem-found` | `stale-confirmed`

### Triggers (intra-repo)
- File in `archive/`, `docs/`, `legacy/`, `old/`
- File >2 directory levels from CWD
- File found via grep/search (not direct navigation)
- File not committed in >30 days

### Enforcement surfaces
- `/start`: SSOT Gem Scan (30s advisory)
- `/end`: Phase 4.2 SSOT Visit Audit (BLOCKING)
- `/disseminate`: Step 0 before propagation
- Pre-commit: warn on cross-repo path refs without visit log

### Key insight
"If you read it, you touched it. If you touched it, log it." — the log IS the disposal record.
SSOT: `.guarani/orchestration/DOMAIN_RULES.md §7`

---

## Parallel Agent Kernel Execution Pattern (2026-03-30)

### What
5 independent agents run in parallel on different governance domains. Each agent: reads its domain, writes deliverables, commits, does NOT push. Main agent coordinates push.

### Why it works
- Pre-commit hooks prevent broken commits — each agent validates before committing
- Agents that touch overlapping files (same TASKS.md) resolve via git's line-level merge
- Push coordination eliminates remote conflicts — only one push gate

### Observed: concurrent commit hash collision
Two agents reported the same commit hash (`acaf52a`) — one wrote the 075/076 docs, another the mcp-governance package. Git merged both changes into one commit because they ran on the same branch at the same time. The commit message reflects only one agent's task, but both sets of files are in the commit (verify with `git show <hash> --stat`).

**Mitigation:** Use worktrees (one per agent) for true isolation when commit messages matter. For pure-doc agents, concurrent commits are acceptable.

### Template
```
Agent 1: domain A (docs only)
Agent 2: domain B (docs only)
Agent 3: domain C (code — needs isolated worktree)
Main: read results, push, verify
```

---

## Agent Claim Taxonomy Pattern (2026-03-30)

### The 6 levels (in order of evidence required)
```
component      → no registration, no exec, internal helper
tool           → registered, has entrypoint, no loop
workflow       → registered, multi-step, no loop
agent_candidate → has entrypoint + dry mode, no eval yet
verified_agent  → entrypoint + eval + telemetry + runtime_proof
online_agent    → verified + persistent loop + monitoring
```

### Key law
**0 verified_agents in the EGOS kernel is correct and honest.** The kernel has tools. Honesty about capability level prevents "agent theater" — marketing claims not backed by runtime evidence.

### Anti-pattern to avoid
Calling anything that wraps an LLM call an "agent." An LLM call is a tool. An agent has: loop mechanism + trigger + eval + observability + runtime proof.

SSOT: `.guarani/orchestration/AGENT_CLAIM_CONTRACT.md`

---

## Eagle Eye Surgery Pattern (2026-03-30)

### Problem
Product with identity crisis: 4 different ICPs, 4 different GTMs, mixed into one repo. Aspirational docs (SEO_STRATEGY, GAMIFICATION_REPORT, TOURISM_MODULE) made the product look unfocused to any technical evaluator.

### Surgery checklist
1. Define ONE ICP (one sentence)
2. Kill all docs serving other ICPs → `archive/killed-docs/`
3. Fix hardcoded mock data with inflated numbers (28 → 15 territories)
4. Rewrite README with honest one-liner + real metrics
5. Update TASKS.md with what was killed and why

### Result
5 doc files killed, README → honest, dashboard mock corrected, ICP locked: "early-warning procurement intelligence for BR gov suppliers."

---

## TRANSPARÊNCIA RADICAL Pricing Pattern (2026-03-30)

### What is TRANSPARÊNCIA RADICAL?
Pay-per-use pricing model (vs fixed subscription) that shows customers **every API call, every cost, every decision** in real-time via dashboard + IA explanations. Goal: maximize trust via radical transparency.

### Why it works better than subscriptions
- **Govtech budgets unpredictable:** Monthly spend varies; fixed R$99 sounds cheap but commits budget
- **Removes price uncertainty:** Pay-per-use means "I only pay for what I use" — powerful signal
- **Builds trust:** Opaque competitors (Twilio, Stripe) hide costs in aggregated invoices; we show everything
- **IA explanation layer:** Qwen daily reports that explain *why* costs changed ("you scanned 500 extra CPFs, added 2 new policy packs")
- **Viral differentiator:** Customers brag about transparency; becomes competitive advantage

### Revenue math (R$0.02/call base rate)
- 5,000 calls/month/customer = R$100/mo (Starter)
- 50,000 calls/month = R$1,000/mo (approach Enterprise)
- Dashboard/IA insights = R$299/mo Pro tier
- Month 1: 5 Starter customers = R$500/mo → break-even Month 2 (infrastructure ~R$650/mo)
- Month 3: 35+ customers → R$7,980/mo (compound growth from referrals)

### Technical foundation
- **Telemetry layer:** TelemetryRecorder.recordEvent() in Guard Brasil API → Supabase guard_events table
- **Schema:** api_key_hash (PII), event_type (enum: api_call, pii_scan, atrian_check), cost_usd, duration_ms, metadata (JSONB)
- **Real-time:** Supabase Realtime WebSocket pushes events to dashboard as they happen
- **IA reports:** Qwen-plus via MCP generates daily summaries (pattern analysis, cost trend, recommendations)
- **Compliance:** All customer data hashed (api_key_hash not API key itself); 1-year retention in Supabase

### Key files
- `docs/strategy/GUARD_BRASIL_TRANSPARENCIA_RADICAL.md` — complete pricing spec + revenue projections
- `GUARD_BRASIL_ARCHITECTURE_STACK.md` — 4-layer technical blueprint (Client → Core → Data → Analytics)

### Gotchas
- Dashboard WebSocket auth: embed JWT in connection string or use RLS policies on guard_events
- Cost calculation: must track duration_ms + token_count to compute accurate cost (not just call count)
- Qwen report generation: batch daily (not real-time) to avoid API quota burn; schedule via Edge Function
- Customer data isolation: use api_key_hash as partition key; never expose raw API keys in logs/dashboard

---

## Guard Brasil GTM Patterns (2026-03-30)

### Docker Deploy from Monorepo
- Dockerfile in `apps/api/Dockerfile` copies from both `packages/` and `apps/api/src/` — build context MUST be repo root
- `rsync` with `--exclude` for `.git/__pycache__/data/` is the right tool for syncing code to VPS
- `--env-file /absolute/path/.env` not `--env-file .env` when running docker compose from non-standard dir
- Health check with `bun -e "fetch(...)"` works inside bun containers without installing curl

### Caddy Dynamic Config Update
- `docker exec infra-caddy-1 caddy reload --config /etc/caddy/Caddyfile` reloads without downtime
- Append-to-Caddyfile via `cat >>` + `caddy reload` is safe for adding new virtual hosts
- Use `grep -q 'domain'` before appending to prevent duplicate entries

### Intelligent Rename Script Pattern
- `sed -i` with `-e 's/specific/replacement/g'` chained from most specific → most broad prevents partial double-substitution
- `diff -q file1 file2` returns 1 if different, 0 if same — use to skip unchanged files efficiently
- Use `file "$path" | grep -qE "binary|ELF"` to skip binary files before text processing
- `should_skip()` function with `case` statement is cleaner than nested if/fi for path exclusions
- Skip the rename script itself (`[[ "$file" == *"rename-script.sh" ]] && continue`)

### Guard Brasil API Key Management
- `/proc/sys/kernel/random/uuid` generates UUID v4 on Linux without Python/uuidgen
- Store in `.env` in deploy dir, reference via `--env-file /absolute/path/.env`
- API key check: `if [ ! -f ".env" ]; then generate; else keep existing`

## MANUAL_ACTIONS Pattern (2026-03-30)

### O que é
`MANUAL_ACTIONS.md` na raiz do repo — arquivo canônico de bloqueios que só o humano pode resolver.
Wired no `/start` INTAKE como leitura obrigatória antes de qualquer planejamento técnico.

### Regras do padrão
- Cada item tem: ID (M-NNN), impacto em receita, tempo estimado, comandos exatos, e como validar
- Prioridades: 🔴 URGENTE (bloqueia receita), 🟡 IMPORTANTE (desbloqueia produto), 🟢 BAIXO
- Itens concluídos vão para o Histórico com data — nunca deletar
- Agente atualiza autonomamente (novos itens, status, deps) — humano só executa

### Gotchas
- `--env-file .env` em docker compose: DEVE ser caminho absoluto quando executado de dir não-padrão
- Docker network rename: funciona com containers attached — sem downtime
- npm publish com CI exige credenciais em secret store segura, não documentadas em superfícies públicas
- GitHub Actions publish-npm.yml: trigger é `push.tags: guard-brasil/v*`, não merge em main

## Agent Operating Protocol (Self-Diagnostic v1.0)

> **What:** Complete atomic documentation of how a governed EGOS agent (Cascade) operates.
> **Why:** So any agent (Cline, Claude Code, Codex, future) or human can replicate this protocol.
> **Philosophy:** "Saímos de casa para nos doar" — everything we learn, we share.

### Environment Reality Contract (PR/Handoff Discipline)

- Every PR/handoff must include explicit environment context (paths, runtime, tool availability).
- Validation must be reported command-by-command with pass/warn/fail status.
- Warnings must explain the limitation (e.g., script expects `/root/egos` but workspace is `/workspace/egos`).
- Include an explicit sign-off footer for traceability:
  - `Signed-off-by: EGOS Codex Agent <codex@egos.local>`
- Mark mandatory manual IDE validation after PR prep:
  - Windsurf local run
  - Antigravity local run
  - test rerun evidence after IDE edits
- Enforce with gate command before merge:
  - `bun run pr:gate --file /tmp/pr-pack.md`

### 1. Rule Hierarchy (Priority Order)

Every decision passes through these layers, top wins:

| Priority | Source | Scope | Example |
|----------|--------|-------|---------|
| **1** | System safety | Absolute | Never auto-run destructive commands |
| **2** | User memories (`.windsurfrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
| **4** | `AGENTS.md` | Per-repo | System map — what this repo IS |
| **5** | `TASKS.md` | Per-repo | What needs to be done |
| **6** | `.guarani/orchestration/PIPELINE.md` | Shared | 7-phase cognitive protocol |
| **7** | `.guarani/PREFERENCES.md` | Per-repo | Coding standards |
| **8** | `.guarani/IDENTITY.md` | Per-repo | Who the agent IS in this context |
| **9** | Workflow triggers (`/start`, `/end`) | On-demand | Loaded when user invokes slash command |
| **10** | Meta-prompt triggers (`triggers.json`) | Keyword-activated | "mycelium" → load mycelium-orchestrator.md |

### 2. Message Processing (Every Single Message)

```text
USER MESSAGE arrives
       |
       v
[CLASSIFY COMPLEXITY]
  TRIVIAL (typo, import)     → Skip to EXECUTE
  SIMPLE (add field, fix bug) → INTAKE → PLAN → EXECUTE → VERIFY
  MODERATE (component, API)   → Full 7-phase pipeline + 3 Sequential Thoughts
  COMPLEX (feature, payment)  → Full pipeline + 5 Sequential Thoughts
  CRITICAL (migration, auth)  → Full pipeline + 7 thoughts + user approval
       |
       v
[CHECK CONSTRAINTS]
  - Is this in a FROZEN ZONE? → STOP, ask user
  - Does this violate SSOT ownership? → STOP, redirect
  - Does this create a new doc? → Anti-proliferation check
  - Does this touch governance? → Will need governance:sync after
       |
       v
[EXECUTE with tool priority]
  1. code_search (explore codebase first)
  2. read_file (verify specifics)
  3. grep_search / find_by_name (targeted)
  4. MCP tools if available (MCP-FIRST principle)
  5. run_command (terminal — safe=auto, destructive=approve)
  6. edit / multi_edit (code changes — minimal, focused)
       |
       v
[VERIFY]
  - tsc --noEmit (TypeScript repos)
  - ruff check (Python repos)
  - git status (check what changed)
  - Visual validation (if UI changed)
       |
       v
[LEARN]
  - create_memory (cross-session persistence)
  - Update HARVEST.md (reusable patterns)
  - Update TASKS.md (mark done, add new)
  - Conventional commit (feat:/fix:/chore:/docs:)
```

### 3. Tool Inventory (What I Have Access To)

**IDE Tools (always available):**
- `read_file` / `edit` / `multi_edit` / `write_to_file` — file operations
- `code_search` — semantic codebase exploration (ALWAYS use first)
- `grep_search` / `find_by_name` — targeted search
- `run_command` — terminal (safe=auto, destructive=needs approval)
- `create_memory` — persist knowledge across sessions
- `todo_list` — task management within session
- `browser_preview` — preview web servers

**MCP Servers (11 connected):**

| Server | Purpose | Key Tools |
|--------|---------|-----------|
| `filesystem` | File ops beyond IDE | read/write/move/search files |
| `memory` | Knowledge graph | create/search entities and relations |
| `sequential-thinking` | Complex reasoning | structured multi-step thought chains |
| `exa` | Web search + code context | web_search, get_code_context (SERIALIZE — never consecutive) |
| `github` | Repo operations | issues, PRs, commits |
| `supabase-carteira-livre` | DB for carteira-livre | schema, queries, RLS |
| `supabase-egosv3` | DB for egos-lab | schema, queries |
| `supabase-mcp-server` | Generic Supabase | migrations, tables |
| `clarity` | Microsoft Clarity analytics | session recordings, dashboard |
| `stitch` | UI design validation | component generation |
| `mcp-playwright` | Browser automation | testing, screenshots |

**External Agents (coordination, not direct control):**

| Agent | Lane | Authority |
|-------|------|-----------|
| **Cascade** (me) | SSOT, runtime truth, deploy, audits, governance | Primary orchestrator |
| **Cline** | Exploratory UI, product edits | MUST NOT touch `.guarani/`, `.windsurf/workflows/`, `.egos/` |
| **Codex CLI** | Diff-heavy, audit, mechanical, cleanup | Second opinion, never SSOT owner |
| **Claude Code** | Repo-local tasks via CLAUDE.md | Secrets in user scope (~/.claude) |
| **Alibaba qwen-plus** | Runtime LLM in products | Primary provider for 852, forja |
| **OpenRouter/Gemini** | Fallback LLM | When Alibaba unavailable |

### 4. Governance Synchronization Model

```text
/home/enio/egos/.guarani/          ← CANONICAL SOURCE (kernel)
       |
       | governance-sync.sh
       v
/home/enio/.egos/guarani/          ← SHARED HOME (copy)
       |
       | symlinks from leaf repos
       v
/home/enio/{repo}/.guarani/        ← LEAF REPOS (symlinks)
  orchestration/ → ~/.egos/guarani/orchestration/
  philosophy/    → ~/.egos/guarani/philosophy/
  prompts/       → ~/.egos/guarani/prompts/
  refinery/      → ~/.egos/guarani/refinery/
  IDENTITY.md    → LOCAL (repo-specific) or symlink
  PREFERENCES.md → LOCAL (repo-specific) or symlink
```

**Sync commands:**
- `bun run governance:sync` — dry-run kernel → ~/.egos
- `bun run governance:sync:exec` — execute kernel → ~/.egos → leaf repos
- `bun run governance:check` — verify 0 drift

**Drift detection:** Pre-commit hooks check SSOT alignment. `/end` workflow BLOCKS if docs are stale.

### 5. SSOT Ownership Contract

| Surface | Owner | Location |
|---------|-------|----------|
| `SSOT_REGISTRY.md` | kernel | `/home/enio/egos/docs/` |
| `CAPABILITY_REGISTRY.md` | kernel | `/home/enio/egos/docs/` |
| `CHATBOT_SSOT.md` | kernel | `/home/enio/egos/docs/modules/` |
| `AGENTS.md` | each repo | repo root |
| `TASKS.md` | each repo | repo root |
| `.windsurfrules` | each repo | repo root |
| `SYSTEM_MAP.md` | each repo | `docs/` |
| `HARVEST.md` | each repo | `docs/knowledge/` |

**Rule:** Leaf repos MUST NOT create parallel global truth. They point to kernel canonical docs.

### 6. Protection Mechanisms

**Frozen Zones (kernel):**
- `agents/runtime/runner.ts` — core execution
- `agents/runtime/event-bus.ts` — core events
- `.husky/pre-commit` — enforcement
- `.guarani/orchestration/PIPELINE.md` — master protocol

**Anti-Proliferation (ALL repos):**
- NEVER create `*_2026-*.md`, `*AUDIT*.md`, `*DIAGNOSTIC*.md`, `*REPORT*.md`
- UPDATE SSOT, don't create new docs
- Handoffs are ephemeral — archive after 30 days
- Pre-commit hooks block violating filenames

**PII Protection:**
- CPF/email/MASP masked in ALL output
- PII scanner runs on LLM input AND output
- ATRiAN ethical validation on every response

**Cline Protection (added 2026-03-21):**
- `.agent/` in `.gitignore` across all repos
- Cline MUST NOT touch `.guarani/`, `.windsurf/workflows/`, `.egos/`
- Symlink breakage pattern: Cline DELETES or REPLACES symlinks with copies

### 7. Memory Model (How Knowledge Persists)

| Layer | Tool | Scope | Lifetime |
|-------|------|-------|----------|
| **Session memory** | Chat context | This conversation | Until session ends |
| **Cascade Memory** | `create_memory` | Cross-session | Permanent until deleted |
| **Knowledge Graph** | `mcp8_create_entities` | Structured relations | Permanent |
| **HARVEST.md** | `edit` | Reusable patterns per repo | Permanent |
| **Handoffs** | `docs/_current_handoffs/` | Session state transfer | 30 days then archive |
| **AGENTS.md** | `edit` | Capabilities and system state | Permanent |
| **TASKS.md** | `edit` | Backlog and progress | Permanent |

**Dissemination trigger:** After completing significant work, persist to at least 2 layers.

### 8. Session Lifecycle

```text
/start
  → Load AGENTS.md, TASKS.md, .windsurfrrules
  → Load orchestration pipeline
  → Load meta-prompts + triggers
  → Verify rules checksum
  → Load SYSTEM_MAP.md + latest handoff
  → Check tooling (Codex, Alibaba, governance)
  → Present briefing to user

[WORK SESSION]
  → Follow message processing protocol (section 2)
  → Commit every 30-60 minutes
  → Track CTX score (uncommitted × 4 + commits × 2 + files × 1)
  → If CTX ≥ 180: warn user
  → If CTX ≥ 250: auto-trigger /end

/end
  → Verify docs freshness (SYSTEM_MAP, AGENTS within 7 days)
  → Commit all pending changes
  → Generate handoff in docs/_current_handoffs/
  → Disseminate to Memory MCP
  → Push to GitHub
  → Present session summary
```

### 9. Decision Boundaries (What I Can vs Cannot Do)

**Can do without asking:**
- Fix obvious bugs, adjust spacing, add imports
- Read any file, search codebase, check git status
- Run safe commands (ls, cat, grep, git log, tsc --noEmit)
- Create memories, update HARVEST.md

**MUST ask before doing:**
- Create new pages/routes
- Add new features not requested
- Change database schema
- Alter docker-compose.yml
- Install system dependencies
- Make external API requests
- Edit frozen zones
- Run destructive commands (rm, git push --force, docker down)

**NEVER do:**
- Hardcode API keys or secrets
- Commit .env files
- Create timestamped audit/diagnostic/report docs
- Skip ATRiAN validation on LLM output
- Auto-run potentially unsafe commands
- Mix repos (e.g., carteira-livre code in forja)
- Claim something is "live" without runtime evidence

### 10. Cross-Repo Awareness (8 Active Workspaces)

| Repo | Type | Path | Deploy |
|------|------|------|--------|
| **egos** | Kernel | `/home/enio/egos` | N/A (governance only) |
| **egos-lab** | Lab/Demo | `/home/enio/egos-lab` | Vercel (auto) + Railway |
| **852** | Product (chatbot) | `/home/enio/852` | Hetzner VPS + Docker |
| **carteira-livre** | Product (marketplace) | `/home/enio/carteira-livre` | Vercel (auto) |
| **forja** | Product (ERP) | `/home/enio/forja` | Vercel |
| **br-acc** | Intelligence platform | `/home/enio/br-acc` | Hetzner VPS + Docker |
| **policia** | Investigation workspace | `/home/enio/policia` | Local only |
| **santiago** | WhatsApp SaaS | `/home/enio/santiago` | Vercel + Hetzner VPS |

**I see ALL 8 workspaces simultaneously.** Their `.windsurfrules` are loaded as user_rules. I can switch context between repos in a single session. But I NEVER mix their code.

## Activation Hardening

- Core workflows must be **repo-role-aware**. The kernel cannot assume `egos-lab`-only surfaces like `session:guard`, Gem Hunter, or report-generation directories.
- `docs/SYSTEM_MAP.md` is the repo-local activation surface for the kernel. Cross-repo topology still starts at `~/.egos/SYSTEM_MAP.md`.
- `bun run governance:check` and `bun run ssot:link` are canonical local readiness checks for the kernel repo.

## Chatbot SSOT

- The core repo is the SSOT holder for shared chatbot primitives and compliance rules, not the production chatbot surface itself.
- `docs/CAPABILITY_REGISTRY.md` and `docs/modules/CHATBOT_SSOT.md` must stay aligned with real adoption evidence.

## Cross-Repo Chatbot Hardening (2026-03-13)

- **Python adapter pattern:** Port `atrian.ts`, `pii-scanner.ts`, `conversation-memory.ts` semantics into a single `chatbot_ssot.py` in the target repo's `services/` folder. Functions must match names the compliance-checker agent looks for (`scanForPII`, `sanitizeText`, `buildConversationMemoryBlock`, `validateResponse`). No external deps; stdlib only.
- **In-memory rate limiter (TypeScript):** When a leaf repo can't use `@egos-lab/shared`, implement `RateLimiter` class with `Map`-based buckets (`windowMs`, `max`). Single-file, zero deps, drop into `src/lib/chat/rate-limiter.ts`.
- **Chat guard helper:** Wrap memory-context, PII sanitization, and ATRiAN validation into a single `_chat-guard.ts` (for serverless) or `chatbot_ssot.py` (for Python) so the route/endpoint stays thin.
- **Validation sequence in chat endpoints:** `buildMemoryContext → call LLM → scanForPII(response) → sanitizeText → validateResponse(ATRiAN) → return`. Never skip ATRiAN step even when PII is clean.
- **Compliance evidence:** `chatbot_compliance_checker --dry --target=/path` gives 100/100 when all 7 SSOT signals are present. Use this as gate before marking EGOS-0XX complete.

## Context Tracker

- **CTX score formula:** uncommitted × 4 + session_commits × 2 + changed_code_files × 1 + handoff_KB × 0.5 + agent_runs × 8. Max 280.
- **Zones:** 0–100 safe, 101–180 warn, 181–250 high, 251+ critical (auto /end).
- **Run before long multi-step tasks:** `bun agent:run context_tracker --dry` gives instant CTX estimate.
- **Auto-trigger:** If agent detects CTX ≥ 250 it MUST emit `/end` autonomously — user should then open a new chat continuing from the generated handoff.

## Governance Propagation Automation

- Remove interactive `read -p "y/n"` prompts from `governance-sync.sh`. Replace with `--auto` flag or `EGOS_AUTO_PROPAGATE=1` env var.
- Pre-commit hook should block commits that change canonical governance files without a subsequent `governance:sync:exec` pass.
- `.windsurfrrules` MANDAMENTO 15: governance changes are not complete until `bun run governance:sync:exec` + `bun run governance:check` return 0 drift.

## Cross-Repo SSOT Mesh

- `docs/SSOT_REGISTRY.md` is now the canonical registry for workspace-wide SSOT ownership.
- Kernel-owned SSOT docs must propagate through `scripts/governance-sync.sh` to `~/.egos/docs/`.
- Leaf repos must keep local pointers in `TASKS.md`, `AGENTS.md`, and local system maps instead of inventing parallel global truth.
- Canonical global SSOT changes are incomplete until both the kernel docs and leaf adoption tasks are updated.

## Workflow Inheritance

- Shared workflows such as `/start`, `/end`, and `/disseminate` should live in the kernel and propagate through `~/.egos/workflows`.
- Leaf repos should either use a symlink/exact inherited copy or a thin local wrapper only when repo-specific precedence is truly required.

---

## Event Bus for Agent Coordination (2026-03-31)

- Supabase Realtime channel `egos-events` + `agent_events` table for persistence
- `emit/subscribe/subscribeOnce` with glob pattern matching (`agent.*`, `alert.*`)
- Fire-and-forget persistence: don't block the emit on DB write — emit returns immediately, DB insert is async
- File: `packages/shared/src/event-bus.ts`

## Guard Brasil Offline Fallback (2026-03-31)

- Python middleware calls `guard.egos.ia.br/v1/inspect` with 5s timeout
- Falls back to 7 regex patterns (CPF, CNPJ, RG, MASP, REDS, email, telefone) when API is unreachable
- ETL pipeline wires guard between `transform()` and `load()` via `_guard_check()`
- File: `br-acc/etl/src/bracc_etl/guard.py`

## Pre-Commit File Intelligence (2026-03-31)

- Classifies all staged files by type (report, doc, config, code, data, test)
- Checks reports against REPORT_SSOT (mandatory sections, confidence markers, citations)
- PII scan in markdown files, `.env` blocking, file size enforcement
- File: `scripts/file-intelligence.sh`

## Prove-or-Kill Agent Lifecycle (2026-03-31)

- Set 30-day deadline, run `--dry` then `--exec`, collect telemetry
- 4 agents killed (never existed as files), 2 kept (working), 2 fixed (timeout/dry issues)
- Lesson: always verify file existence before planning work on agents

## MasterOrchestrator Scheduling (2026-03-31)

- Reads `agents.json`, builds schedule from trigger configs (`every_5min`, `daily`, `manual`)
- Detects overdue agents via event history queries
- Quota routing: checks env vars for DashScope/OpenRouter/Groq/HuggingFace
- File: `egos-lab/agents/agents/master-orchestrator.ts`

## [Gotcha] Other-AI-Session Claims Must Be Verified (2026-03-31)

- Critical analysis from another Claude session had 4 wrong claims out of 10
- ".guarani are copies" was WRONG (they're symlinks)
- "20% use LLM" was WRONG (43.6%)
- "domain-explorer missing" was WRONG (naming mismatch only)
- **Rule:** always verify with `diff`/`ls`/`grep` before acting on cross-session claims
- Exact-match local copies are drift magnets and should be re-linked to the shared source instead of being maintained by hand.
- Repo-local overrides are legitimate only when they protect local truth or sensitivity constraints, such as mapped-only or sigiloso workspaces.

## Cheap-First Orchestration

- The winning pattern is not multi-model fanout. Use one coordinator and route sequentially by cost and confidence.
- Default order: local tools and code search first, cheap triage model second, premium reasoning model only on blockers, reviewer model last for proof-of-work.
- Keep user-scope secrets and MCP auth outside repo-tracked files; keep repo instructions local; keep shared governance in `~/.egos`.

## Message Provenance & Signature Discipline (2026-03-23)

- Canonical contract lives at `.guarani/standards/AGENT_MESSAGE_SIGNATURE_CONTRACT.md`.
- Signature footer must include environment lane and Git provenance when changes/commit/push are involved.
- Google AI Studio is an explicit source lane and follows the same footer contract as Codex/Windsurf/Antigravity.
- Do not create operational status reports as standalone timestamped docs; consolidate durable learning into SSOT/HARVEST.

## Pragmatic Multi-Agent Benchmark Distillation (2026-03-26)

- Keep only execution primitives that improve reliability and delivery speed: worktree isolation, parallel lanes with ownership, QA loop, and file-first context.
- Treat integrations with external orchestrators as optional adapters, not kernel identity.
- Reject any layer that increases cognitive load without measurable reduction in risk, cost, or lead time.
- Adopt "proof-at-gate": each parallel lane must emit evidence artifacts consumable by `pr:gate`.

## GTM/Market Intelligence Harvest (Cross-Repo, 2026-03-26)

- New kernel agent: `gtm_harvester` scans public repos for GTM/market signals and named strategic entities.
- First scan result (owner `enioxt`): 9/14 repos with GTM/market signals; strongest strategic density in `egos`, `egos-lab`, `FORJA`, and `EGOS-Inteligencia`.
- Direct named references not found in public repos for: `Siberia Institute`, `Vagner Campos` (requires explicit canonical encoding if strategically relevant).
- Automation pattern: harvest -> distill -> codify in `TASKS.md` contracts -> enforce via gate workflows.
- Intake policy: when insights come from external Grok threads, register tasks immediately in kernel queue with `target_repo` marker, then migrate after triage.

## External-Input Hardening

- Treat issue titles, PR text, web pages, and imported documents as untrusted input until sanitized.
- Agents that read untrusted input must not also hold publish, cache-mutation, or broad shell privileges.
- High-impact actions must stay behind an explicit human gate, even when the analysis path is automated.

## Mycelium

- Mycelium references in the kernel must distinguish **present**, **partial**, and **planned** layers instead of implying all historical surfaces exist locally.

## Leaf Governance Audit Pattern (2026-03-21, from carteira-livre)

### Problem

Leaf repos inherit kernel governance via symlinks but keep local IDENTITY.md and PREFERENCES.md. Over time these local files drift to contain kernel-generic content (e.g., referencing `agents/runtime/runner.ts` that doesn't exist in the leaf).

### Rules Extracted

1. **Leaf IDENTITY.md** must describe WHO this specific agent is (not "kernel orchestrator").
2. **Leaf PREFERENCES.md** must reference leaf-specific paths, tools, and Supabase project refs.
3. **Shared governance** (orchestration, philosophy, prompts, refinery) comes ONLY via symlinks to `~/.egos/guarani/`.
4. **AGENTS.md** must have a **Domain Map** table classifying each domain as Frozen / Core / Supporting / Shared-candidate / Compliance with explicit owner (Leaf-exclusive vs @egos/shared).
5. **Anti-proliferation** enforcement via pre-commit blocks timestamped audits, diagnostics, reports, and checklists outside `_archived/` or `_generated/`.

### Carteira Livre Specifics

- 14 domains classified, 4 shared-candidate modules identified (AI guardrails, telemetry, notifications, LGPD).
- 28 anti-proliferation violations archived in one commit.
- AGENTS.md condensed from 358→140 lines with domain map.
- 8 reusable patterns documented in local HARVEST.md.

## Stitch-First UI Rule Upgrade (2026-03-26)

- Official Google positioning: Stitch converts prompts, wireframes, or images into UI + frontend code and supports export to HTML/CSS or Figma (Google I/O 2025 product update).
- Kernel policy updated: all new screens must pass through `/stitch` before coding starts.
- Operating split: EGOS lane writes `Stitch Prompt Pack` -> operator creates externally in Stitch -> operator returns `.zip` -> integration only begins after zip intake mapping.
- Next automation step: create `stitch_intake_mapper` agent to parse zip payloads and open integration tasks automatically.

## AIOX-Core Gem Diagnosis + NotebookLM Cross-Check (2026-03-26)

- External benchmark analyzed: `SynkraAI/aiox-core` (repo metadata + README/docs signal scan) with objective to extract only execution primitives useful to EGOS.
- Keep candidates validated as high signal for EGOS: squad pattern, worktree orchestration, spec pipeline flow (`analyst -> pm -> architect -> sm`), and doctor-style readiness checks.
- Drop candidates for now: pro-lock or platform-coupled features, mandatory memory-layer coupling, and any dependency that dilutes kernel governance or increases complexity before flagship monetization.
- Local evidence cross-check performed on `notebooklm_export_egos.md` to recover Commons-prep context and gem-hunter lineage references as migration input.
- Operationalization path: new agent `aiox_gem_hunter` added to run repeatable diagnosis and emit keep/drop findings before contract implementation.

## Codex Lane Operational Disclosure (2026-03-26)

- Added `bun run doctor:codex` (`scripts/codex-doctor.sh`) to make environment constraints explicit before long runs.
- Mandatory disclosure in handoffs/start briefings now includes Codex constraints: non-interactive execution defaults, browser-tool dependency for visual checks, and potentially ephemeral `~/.egos` state.
- Objective: avoid false assumptions about automation guarantees and keep operator expectations explicit across lanes.

## MASA Framework + Competitor Scan (2026-03-26)

- MASA positioning validated: architecture-first framework focused on "cognizability" and static interpretability for AI agents, with SKILL.md-centric adoption model.
- Practical execution test: repository downloaded via codeload zip and inspected locally; current main payload is mostly specification/docs/experiments assets (no turnkey runtime to execute like a platform service).
- Environment limitation observed: direct `git clone`/`ls-remote` to GitHub returned HTTP 403 in this Codex lane; fallback via `codeload.github.com` succeeded.
- Competitor baseline scanned from official sources: LangGraph, AutoGen, Semantic Kernel, LlamaIndex.
- EGOS recommendation: test MASA as selective architectural skill in a controlled leaf-repo pilot, not as kernel-wide hard mandate yet.

## Why MASA/Mastra Looks "Cleaner" Than EGOS Today (2026-03-26)

- They communicate one dominant story on the surface (single concise value proposition + polished onboarding path), while EGOS currently exposes many strategic threads at once.
- EGOS has technical governance advantages, but presentation and operator narrative are still fragmented across many artifacts.
- Gap is less about capability and more about packaging discipline: message hierarchy, demo reproducibility, and evidence-first storytelling.

### Architecture Plan (Kernel-side, no bloat)

1. Keep EGOS kernel minimal and governance-first (no full framework transplant).
2. Extract only high-signal gems from Mastra/MASA via dedicated hunters (`mastra_gem_hunter`, `framework_benchmarker`).
3. Build a Presentation System in SSOT (positioning + proof + demo flow) before adding more runtime complexity.
4. Validate adoption via pilot metrics (drift, lead-time, compliance incidents) before ecosystem-wide rollout.

## /end Handoff Package — 2026-03-26 (Codex lane)

### Session Outcomes

- Added and validated `mastra_gem_hunter` for targeted extraction of Mastra workflow/evals/observability/MCP/human-loop patterns.
- Added and validated `framework_benchmarker` for cross-framework scan (MASA, LangGraph, AutoGen, Semantic Kernel, LlamaIndex).
- Updated strategic backlog with presentation-system execution track (`EGOS-116..121`) to close packaging/narrative gap.

### Strategic Diagnosis (carry-forward)

- EGOS has governance/discipline advantage; bottleneck is presentation coherence and reproducible operator narrative.
- Do not transplant full external frameworks into kernel.
- Keep only portable high-signal patterns behind measurable pilot gates.

### Immediate Next Steps for Next Agent

1. Execute `EGOS-116` first: codify Presentation System SSOT (positioning, promise, evidence, differentiators).
2. Execute `EGOS-117` next: produce operator narrative kit from existing SSOT (no parallel truth docs).
3. Execute `EGOS-118`: reproducible live-demo lane script for client meetings.
4. Run benchmark evidence checks with `framework_benchmarker` + `mastra_gem_hunter` before proposing new runtime changes.

### Operational Constraints (Codex)

- Terminal-first non-interactive lane.
- Browser/UI validation depends on explicit browser tool availability.
- Home sync state (`~/.egos`) may reset across runs; re-run sync/check when drift appears.

---

## Session Harvest — 2026-03-29 (Security + Governance + Observability)

### Pattern: CRCDM Hook as Universal Governance Layer

**What:** Merged 6-check canonical spec into the single CRCDM universal pre-commit hook (`~/.egos/hooks/pre-commit`). All leaf repos with symlink get full governance automatically.
**Checks:** gitleaks (blocking), regex secret fallback (blocking), doc proliferation (blocking), SSOT size limits (warning), handoff freshness (warning), CRCDM DAG logging.
**Why this matters:** Previously there were two competing hook specs (CRCDM observability-only + .husky canonical). The dual-hook caused ambiguity and missed checks (e.g., doc proliferation not enforced in 852).
**Rule:** Single hook source `scripts/hooks/crcdm-pre-commit.sh` → deployed to `~/.egos/hooks/pre-commit` → symlinked from leaf repos.

### Gotcha: `if pipeline | head -5; then` Always True in POSIX sh

**What:** `head -5` exits 0 even on empty stdin. So `if cmd | head -5; then` is ALWAYS true regardless of whether `cmd` produces output.
**Fix:** Capture output first: `MATCH=$(cmd | head -5); if [ -n "$MATCH" ]; then`
**Where found:** carteira-livre `.husky/pre-commit` — secret scan fired on every commit as a false positive.

### Gotcha: Husky v9 Runs Hooks via `sh -e`, Ignoring Shebang

**What:** Husky v9 uses `sh -e "$hookfile"` internally, so `#!/bin/bash` in `.husky/pre-commit` is ignored. All husky hooks must use POSIX sh syntax.
**Bash constructs to avoid:** `[[ ]]`, `<<<`, `${var:0:n}`, `${var^^}`, `(( ))`.
**Fix:** Use POSIX alternatives: `echo "$var" | grep -qE 'pattern'` instead of `[[ "$var" =~ pattern ]]`.

### Pattern: Cross-Repo Health Dashboard Before Installer Scripts

**What:** `scripts/egos-repo-health.sh` — run before any `install-*.sh` script to verify all repos are committed.
**Why:** Installers copy files from kernel to leaf repos. If kernel changes are uncommitted, stale code propagates.
**Usage:** `bash scripts/egos-repo-health.sh` (exits 1 if any repo is dirty).

### Pattern: Fibonacci Context Persistence

**What:** Snapshots at Fibonacci intervals (1,1,2,3,5,8,13...) via `scripts/context-manager.ts`. Auto-triggered by post-commit hook on feat/fix/refactor commits.
**Files:** `docs/_context_snapshots/*.md` (human-readable) + `*.json` (machine).
**Why Fibonacci:** Progressively less frequent as context grows — balances granularity vs noise.
**Integration:** `/snapshot` slash command + `/start` workflow recovery.

### Pattern: Secret Leak Response Protocol

**What:** When a secret (e.g., Supabase PAT `sbp_...`) is found committed:
1. Sanitize: replace with placeholder in the file, commit with "security: sanitize"
2. Rotate: revoke token immediately in provider dashboard
3. Harden: add detection rule to `.gitleaks.toml` + universal hook
4. Verify: re-run gitleaks on all repos to confirm clean
**Supabase PAT pattern:** `sbp_[0-9a-f]{40}` — added to `.gitleaks.toml`.

---

## Session Harvest — 2026-03-29 (Guard Brasil Packaging + Flagship Brief)

### Pattern: SDK Packaging from Monorepo Shared Modules

**What:** Extract domain modules from `@egos/shared` into a standalone, npm-publishable package (`@egosbr/guard-brasil`).
**How:**
1. Create `packages/<product>/package.json` with `"license": "MIT"` (not `"private": true`)
2. `src/index.ts` re-exports from `@egos/shared` for granular usage
3. `src/guard.ts` composes a facade class (`GuardBrasil`) that calls all layers in sequence
4. `src/demo.ts` shows a realistic scenario (not toy examples)
5. `src/guard.test.ts` tests each layer independently + combined scenario
**Test runner for ESM TypeScript in this monorepo:** `bun test`, NOT jest (which fails on import syntax)
**Why:** Individual modules already exist; packaging adds the product narrative, composability, and distribution boundary.

### Pattern: Facade Composition for Safety Stacks

**What:** When building a multi-layer safety SDK (ATRiAN + PII + Evidence), create a unified `inspect(text, options)` method that:
1. Runs all checks sequentially (ATRiAN → PII scan → masking → evidence chain)
2. Returns a typed result object with all intermediate results + a `safe` boolean + human-readable `summary`
3. Is stateless — the validator instances are created at `GuardBrasil.create()` time, not per-call
**Why:** Callers shouldn't need to know the order of operations or which module to call. One method, one result.
**LGPD disclosure pattern:** Only add LGPD footer when findings exist (`if result.safe return ''`).

### Pattern: Flagship Brief as SSOT for Product Decisions

**What:** `docs/strategy/FLAGSHIP_BRIEF.md` — a single canonical document that answers:
- One-sentence value proposition (repeatable commercial sentence)
- Problem statement (what fails without this)
- Core modules table (what each layer does, succinctly)
- Target personas with "job to be done" framing
- Differentiation matrix (vs specific named competitors)
- Monetization model (what's free vs paid)
- Success metrics with targets and timeframes
- What we are NOT building (explicit scope guard)
**Why:** Prevents scope creep and "another interesting idea" drift by making the product focus a git-tracked, reviewable artifact.
**Rule:** Before accepting any new product feature or expansion, check it against FLAGSHIP_BRIEF.md "What we are NOT building" section.

---

## Session Harvest — 2026-03-30 (Forja WhatsApp Integration + Multi-Channel SSOT)

### Pattern: Integration Memory as SSOT

**Problem:** Documentation drift across sessions — references to Railway when runtime is actually Hetzner, stale API URLs, confusion about service locations.

**Solution:** `docs/INTEGRATIONS_MEMORY.md` as canonical reference for:
- Infrastructure (VPS IP, SSH keys, ports, Docker services)
- Databases (Supabase project ID, connection strings, RLS status)
- External APIs (Evolution API location, WhatsApp instances, webhook URLs)
- AI/LLM providers (Alibaba Qwen config, OpenRouter fallback, API keys location)
- Security (secrets management strategy, rotation schedule, storage surfaces)
- Quick reference commands for health checks, deploys, debugging

**Why:** Single source of truth prevents "which environment?" confusion. MCP memory sync makes it AI-persistent across sessions.

**Implementation (forja):**
```markdown
## Infrastructure

### Hetzner VPS
- **Address:** redacted in public-facing docs
- **Access:** operator-managed only
- **Docker Services:**
  - evolution-api (port 8080)
  - postgres (Evolution API DB)
  - Caddy (reverse proxy)

### Evolution API (WhatsApp Runtime)
- **Mode:** Self-hosted on Hetzner (NOT Railway)
- **URL:** internal-only runtime surface
- **Instance:** forja-notifications
- **State:** open (validated 2026-03-30)
```

**MCP Sync Pattern:**
```typescript
// Create entities for infrastructure
mcp__memory__create_entities({
  entities: [
    { name: "Hetzner VPS", entityType: "infrastructure",
      observations: ["Address redacted in public docs", "Hosts Evolution API"] },
    { name: "Evolution API", entityType: "service",
      observations: ["Self-hosted on Hetzner", "NOT on Railway", "Port 8080"] }
  ]
});

// Create relations
mcp__memory__create_relations({
  relations: [
    { from: "Evolution API", to: "Hetzner VPS", relationType: "is_hosted_on" },
    { from: "Forja", to: "Evolution API", relationType: "uses_for_whatsapp" }
  ]
});
```

**Reusable pattern:** This fix should be part of the canonical Evolution API deployment template for all products.

---

### Pattern: Evolution API Deployment Lessons

**Gotcha 1: Database Provider Invalid Error**

**Symptom:** `DATABASE_ENABLED=false` → Error: "Database provider invalid"

**Root Cause:** Evolution API requires real database even in "disabled" mode.

**Fix:** Deploy PostgreSQL container alongside Evolution API.

```yaml
services:
  postgres:
    image: postgres:15-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U evolution"]
    environment:
      - POSTGRES_USER=evolution
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=evolution

  evolution-api:
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      - DATABASE_ENABLED=true  # MUST be true
      - DATABASE_PROVIDER=postgresql  # MUST be postgresql
      - DATABASE_CONNECTION_URI=postgresql://evolution:${DB_PASSWORD}@postgres:5432/evolution
```

**Gotcha 2: Docker Compose Version Field Obsolete**

`version: '3.8'` is obsolete in modern Docker Compose. Remove it.

**Gotcha 3: Use Docker Compose Plugin, Not Standalone**

Use `docker compose` (plugin), not `docker-compose` (standalone binary).

---

### Pattern: Instance Naming Convention

```
{product}-{purpose}

Examples:
- forja-notifications
- 852-customer-service
- carteira-x-transactions
- egos-admin-alerts
```

**Purpose categories:**
- `notifications` — system alerts, status updates
- `customer-service` — support, inquiries
- `transactions` — payment confirmations, order tracking
- `admin-alerts` — internal operations monitoring

---

### Pattern: Multi-Channel Control Tower (Future)

**Problem:** Evolution Manager UI insufficient for managing 10+ WhatsApp channels across products.

**Solution:** Build internal admin dashboard with:

| Feature | Purpose | Priority |
|---------|---------|----------|
| Instance Registry | Canonical list of all channels | P0 |
| Health Dashboard | Real-time connection status | P0 |
| Test Send | Manual message dispatch per channel | P0 |
| Webhook Monitor | Event log viewer | P1 |
| Message Queue | Redis-backed queue/retry | P1 |
| Multi-Agent Routing | AI policy per channel purpose | P1 |
| Analytics | Volume, latency, success rate | P2 |

**Schema (Supabase):**
```sql
CREATE TABLE whatsapp_instances (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  instance_name VARCHAR(100) UNIQUE NOT NULL,
  product VARCHAR(50) NOT NULL,
  purpose VARCHAR(100),
  phone_number VARCHAR(20),
  connection_state VARCHAR(20),
  last_health_check_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE whatsapp_messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  instance_name VARCHAR(100) REFERENCES whatsapp_instances(instance_name),
  direction VARCHAR(10),  -- 'inbound', 'outbound'
  phone_number VARCHAR(20),
  message_text TEXT,
  status VARCHAR(20),  -- 'sent', 'delivered', 'read', 'failed'
  metadata JSONB
);
```

---

### Pattern: Notification Service Layer (TypeScript)

**Structure:**
```typescript
// src/lib/whatsapp/notifications.ts
export async function sendNotification(params: {
  type: 'production_alert' | 'stock_alert' | 'quote_update';
  recipient: string;  // E.164 format
  data: Record<string, any>;
}) {
  const provider = new EvolutionProvider({ ... });
  const template = getTemplate(params.type);
  const message = template(params.data);
  return provider.sendMessage({ number: params.recipient, text: message });
}
```

**Template Pattern:**
```typescript
const templates = {
  production_alert: (data) => `
🏭 PRODUÇÃO - Ordem #${data.orderId}

Status: ${data.status}
Etapa: ${data.stage} (${data.progress}%)
Responsável: ${data.assignee}

🔗 Ver ordem: ${data.orderUrl}
  `.trim(),

  stock_alert: (data) => `
📦 ESTOQUE BAIXO - ${data.productName}

Atual: ${data.currentStock} ${data.unit}
Mínimo: ${data.minStock} ${data.unit}

⚠️ Solicitar reposição
  `.trim()
};
```

---

### Pattern: Webhook Handler (Next.js)

```typescript
// src/app/api/notifications/whatsapp/route.ts
export async function POST(req: NextRequest) {
  const body = await req.json();
  const supabase = createClient();

  // Audit ALL events
  await supabase.from('audit_log').insert({
    action: 'whatsapp_webhook_received',
    metadata: body,
    created_at: new Date().toISOString()
  });

  // Handle specific events
  if (body.event === 'MESSAGES_UPSERT') {
    // Process incoming message
  }

  return NextResponse.json({ status: 'ok' });
}

export async function GET() {
  // Health check
  const provider = new EvolutionProvider({ ... });
  const state = await provider.getConnectionState();

  return NextResponse.json({
    status: 'ok',
    connected: state.state === 'open',
    instance: process.env.EVOLUTION_INSTANCE_NAME
  });
}
```

---

### Pattern: Secrets Management for WhatsApp

**Storage Surfaces:**

| Surface | What | Where | Rotation |
|---------|------|-------|----------|
| Hetzner .env | Evolution API key, DB password | `/opt/evolution-api/.env` | Manual (90 days) |
| Vercel Env | API URL/key, instance name | Vercel dashboard | Manual (90 days) |
| Local .env.local | Dev credentials | `.gitignore`d | Per developer |
| Supabase | Audit logs only (never secrets) | RLS-protected | N/A |

**Security Checklist:**
- [ ] Never commit `.env` or `.env.local`
- [ ] Separate API keys for dev/staging/prod
- [ ] Rotate Evolution API key every 90 days
- [ ] Mask phone numbers in logs (`557****8888`)
- [ ] Log all webhook events to Supabase
- [ ] Rate limit webhook endpoint
- [ ] Verify webhook signature if secret set
- [ ] LGPD/GDPR compliance for phone storage

---

### Dissemination Checklist (New Repo Adopting WhatsApp)

- [ ] Copy Evolution API docker-compose template
- [ ] Generate unique API key: `openssl rand -hex 32`
- [ ] Create instance: `{product}-{purpose}`
- [ ] Configure webhook to app URL
- [ ] Scan QR code (Baileys) or configure Cloud API
- [ ] Add Vercel env vars: `EVOLUTION_API_URL`, `EVOLUTION_API_KEY`, `EVOLUTION_INSTANCE_NAME`
- [ ] Implement notification service layer
- [ ] Implement webhook handler
- [ ] Create audit log table in Supabase
- [ ] Test all notification types
- [ ] Document in `docs/WHATSAPP_SETUP_GUIDE.md`
- [ ] Update `docs/INTEGRATIONS_MEMORY.md`
- [ ] Sync to MCP memory

---

### Task IDs

| Task | Status | Evidence |
|------|--------|----------|
| EGOS-WHATSAPP-001 | ✅ Complete | WhatsApp SSOT created (`docs/knowledge/WHATSAPP_SSOT.md`) |
| FORJA-WHATSAPP-008 | 🟡 70% | Runtime + QR done, notification tests pending |
| FORJA-WHATSAPP-010 | 📋 Planned | Control Tower MVP |
| FORJA-WHATSAPP-011 | 📋 Planned | Redis queue/retry |
| FORJA-WHATSAPP-012 | 📋 Planned | Multi-agent routing |

---

### References

- **WhatsApp SSOT:** `egos/docs/knowledge/WHATSAPP_SSOT.md` (canonical)
- **Forja Handoff:** `forja/docs/_current_handoffs/handoff_2026-03-30.md`
- **Forja Integration Memory:** `forja/docs/INTEGRATIONS_MEMORY.md`
- **Forja WhatsApp Setup:** `forja/docs/WHATSAPP_SETUP_GUIDE.md`
- **Forja Harvest Patterns:** `forja/docs/knowledge/HARVEST.md` (Pattern #11, #12, #13, #14)

---

## Guard Brasil v0.2.0 PII Pattern Extension (2026-03-31)

### What
Added 3 new Brazilian PII patterns to `packages/guard-brasil/src/pii-patterns.ts`, bringing total to 15 patterns.

### New patterns
| ID | Label | Confidence | Key detail |
|----|-------|------------|------------|
| `sus` | Cartão SUS | medium | 15 digits, starts with 1-9, groups of 3+4+4+4 |
| `titulo_eleitor` | Título de Eleitor | low | 12 digits (3 groups of 4) — high false-positive risk |
| `nis_pis` | NIS/PIS | medium | 11 digits, starts with [12], format `xxx.xxxxx.xx-x` |

### Insertion order matters
`ALL_PII_PATTERNS` registry order = specificity priority. `SUS` and `NIS_PIS` inserted between `CNH` and `MASP` (after more-specific CNPJ/CPF/RG). `TITULO_ELEITOR` before CEP (low confidence).

### Why `titulo_eleitor` is `low` confidence
Regex `\b\d{4}\s?\d{4}\s?\d{4}\b` matches too many 12-digit sequences. Deploy only in contexts where voter registration data is expected.

### Build + test cycle
```bash
cd packages/guard-brasil && bun run build && bun test src/guard.test.ts
```

---

## VPS vs Local Governance Gap (2026-03-31)

### Problem
`.guarani/` symlinks in kernel point to `~/.egos/guarani/`. On VPS (`/opt/egos-lab`), broken — `/home/enio/` doesn't exist.

### Fix
```bash
cd /opt/egos-lab && git checkout HEAD -- .guarani/
```
Replaces broken symlinks with actual committed files. VPS gets static copies (not live-sync). Acceptable for read-only governance.

### event-bus.ts missing on VPS
`egos-lab/packages/shared/src/event-bus.ts` is a symlink locally. On VPS, symlink target absent. Fix: `scp` the actual file.

### VPS cron path fix
All agents were pointing to `/home/enio/egos-lab` (dev path). VPS actual: `/opt/egos-lab`. Fix: edit crontab replacing all instances. Validate: `crontab -l | grep egos-lab`.

---

## MasterOrchestrator Telemetry Validation Pattern (2026-03-31)

### Validation steps (before claiming "integrated")
1. Trigger agent: `bun /opt/egos-lab/agents/agents/master-orchestrator.ts`
2. Check Supabase `agent_events` table for new rows with matching `agent_id`
3. Verify `event_type`, `timestamp`, `metadata` populated
4. Only after step 3 claim "telemetry integrated"

### 4 agents confirmed with telemetry (2026-03-31)
`uptime-monitor`, `quota-guardian`, `drift-sentinel`, `etl-orchestrator`, `master-orchestrator` — all emit to `agent_events` via event-bus.

---

## npm publish Blocked = MANUAL_ACTIONS Item (2026-03-31)

### Pattern
When `npm publish` requires interactive auth (`npm adduser`) with no browser/stdin, don't attempt. Instead: add to `MANUAL_ACTIONS.md` + `TASKS.md` with MANUAL tag, continue other work.

### npm publish workflow (when unblocked)
```bash
npm adduser    # interactive: username, password, OTP
cd packages/guard-brasil && bun run build && npm publish --access public
```

## Modification Size Guard Pattern (2026-04-01)

### Problem
Commits com 500+ linhas alteradas de uma vez dificultam code review e aumentam risco de rollback. O caso dos "800 arquivos modificados" no EGOS kernel revelou necessidade de alerta proativo.

### Solution
Hook de pre-commit verifica `git diff --cached --stat`:
- Se >500 linhas alteradas → warning com lista dos 5 arquivos mais modificados
- Pergunta interativa: "Continue anyway? [y/N]"
- Sugestão: dividir em commits menores

### Implementation
```bash
# .husky/pre-commit
STAGED_DIFF_STAT=$(git diff --cached --stat --numstat 2>/dev/null || true)
TOTAL_ADDS=$(echo "$STAGED_DIFF_STAT" | awk '{sum+=$1} END {print sum}')
TOTAL_DELS=$(echo "$STAGED_DIFF_STAT" | awk '{sum+=$2} END {print sum}')
TOTAL_LINES=$((TOTAL_ADDS + TOTAL_DELS))

if [ "$TOTAL_LINES" -gt 500 ]; then
  echo "⚠️  WARNING: Large commit detected ($TOTAL_LINES lines)"
  read -p "Continue anyway? [y/N] " -n 1 -r < /dev/tty
  [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi
```

### Rule
Commits grandes (>500 linhas) requerem justificativa explícita ou divisão.

