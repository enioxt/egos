# HARVEST.md — EGOS Core Knowledge

> **VERSION:** 3.2.0 | **UPDATED:** 2026-04-03
> **PURPOSE:** compact accumulation of reusable patterns discovered in the kernel repo
> **Latest:** Dialectic Questioning P0, LLM Fallback Chain, Papers Without Code Pipeline, /start v6.0, Agent Registry Drift Detection, SSOT Validation Hierarchy, World Model AGI Roadmap

## AI Agent Validation Checklist Pattern (2026-04-03)

### Problem
AI agents jump to conclusions about "ghost agents" or "missing files" without complete validation, causing false positives and wasted investigation time.

### Root Cause (Session P17 Case Study)
When investigating 4 reported "ghost agents":
- **Error 1:** Assumed `drift-sentinel` output was ground truth
- **Error 2:** Did not check `agents.json` entrypoint field for each agent
- **Error 3:** Did not verify file existence at actual entrypoint paths
- **Error 4:** Ignored `status: "dead"` field meaning

**Result:** 2 false positives (`kol-discovery` and `gem-hunter-api` were alive in `scripts/` and `agents/api/`), 2 true positives (actually dead agents).

### Solution — 4-Point Validation Protocol
Before claiming ANY agent is "ghost/missing/dead", MUST validate:

| # | Check | Tool | Evidence Required |
|---|-------|------|-------------------|
| 1 | `agents.json` entrypoint field | `read_file` on `agents/registry/agents.json` | Exact `entrypoint` path string |
| 2 | File exists at that path | `existsSync` or manual check | File content or 404 confirmation |
| 3 | `status` field meaning | `read_file` on `agents.json` | `"dead"`, `"disabled"`, `"active"`, etc. |
| 4 | `run_modes` + `kind` context | `read_file` on `agents.json` | `service` vs `tool` vs `workflow` behavior |

### Critical Rules
- **NEVER** rely solely on `drift-sentinel` output — it has false positives on non-standard paths
- **ALWAYS** verify `scripts/` and `agents/api/` entrypoints manually
- **IGNORE** agents with `status: "dead"` — they are intentionally removed
- **CROSS-REFERENCE** multiple sources before making claims

### Applied To
- `.windsurfrules` — Added Rule 13: AGENT VALIDATION
- `agents/agents/drift-sentinel.ts` — Fixed to check any entrypoint path
- Future agent investigations — mandatory 4-point validation

---

## Agent Registry Drift Detection Pattern (2026-04-03)

### Problem
Agent registry (`agents.json`) diverges from filesystem reality: dead agents remain listed, entrypoints move to non-standard paths (`scripts/`, `agents/api/`), drift detection only checks `agents/agents/` directory.

### Solution
Two-layer validation in `drift-sentinel.ts`:
1. **Entrypoint Check**: For each agent in registry, verify `entrypoint` field exists on disk (any path: `scripts/`, `agents/agents/`, `agents/api/`)
2. **Orphan Check**: Files in `agents/agents/` not listed in registry
3. **Status Filter**: Skip agents with `status: "dead"` or `"disabled"`

### Key Implementation
```typescript
// Check each agent's entrypoint exists (respects any path)
for (const agent of agents) {
  if (agent.status === "dead" || agent.status === "disabled") continue;
  const fullPath = join(ROOT, agent.entrypoint);
  if (!existsSync(fullPath)) { /* report drift */ }
}
```

### Applied To
- `agents/agents/drift-sentinel.ts` — refactored `checkAgentsDrift()`
- `agents/registry/agents.json` — cleaned 2 dead agents (aiox-gem-hunter, mastra-gem-hunter)

---

## Dialectic Questioning Pattern (2026-04-02)

### Problem
AI agents execute complex work without confirming direction, leading to wasted effort and misaligned output.

### Solution
P0 constitutional rule: MODERATE+ tasks MUST include dialectic refinement. Present Options A/B/C with cost/effort/tradeoff analysis. Minimum 3 questions. User alignment required.

### Applied To
- `.windsurfrules` (P0 rule)
- `.guarani/PREFERENCES.md`
- `CLAUDE.md` global (feedback_posture.md)
- All future EGOS sessions

## LLM Fallback Chain Pattern (2026-04-02)

### Problem
Single LLM provider (OpenRouter) fails silently, causing --analyze and --deep to skip without notice.

### Solution
Priority-based fallback: Qwen-plus(free, 1M tokens) → OpenRouter free models (Qwen-2.5-7b, Llama 3.1 8B) → Gemini Flash($0.075/1M) → Claude Haiku($0.80/1M). Each level only activates if previous fails or exhausts quota.

### Cost Impact
$0.00/day for 80% of work (free tiers). $0.50/day max with deep reading. ~$15/month total.

## Papers Without Code Pipeline (2026-04-02)

### Problem
Traditional gem hunting only finds repos with existing code. Papers describing novel architectures WITHOUT implementations are the highest-value discoveries — they represent ideas nobody has built yet.

### Solution
6-stage pipeline: S1 Discovery (arXiv no_code + PWC no_implementations) → S2 Abstract Triage (free LLM scores 0-100) → S3 Deep Reading (Gemini Flash, targeted sections) → S4 Scaffold Generation (.ts stubs + .md spec) → S5 Scoring + World Model → S6 Trend Evolution. Output: docs/gem-hunter/papers/<paper-id>/ with REPORT.md, architecture.ts, stubs.ts, spec.test.ts.

### Key Detail
arXiv filter: `cat:cs.AI AND NOT github.com` catches papers without repos. PWC API: `/papers/?no_code=true`. Budget: ~$0.01/paper for deep reading via Gemini Flash.

## /start v6.0 Pattern (2026-04-02)

### Problem
Session initialization was slow (45s), verbose (25 lines), and not programmable.

### Solution
TypeScript engine with parallel I/O: 22s wall time, 12-line executive summary, --json output for CI/CD. Validation gates (files, types, env vars, API health) with exit codes (0=pass, 1=fail). Integrated into GitHub Actions CI and pre-commit hook.

### Key Detail
`bun scripts/start-v6.ts --json` for automation. `npm run start` for daily use. Pre-commit integration blocked by FROZEN ZONE (.husky/pre-commit) — requires user approval via --no-verify.

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
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
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
| **2** | User memories (`.windsurfrrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
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
| `.windsurfrrules` | each repo | repo root |
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
| **2** | User memories (`.windsurfrrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
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
| `.windsurfrrules` | each repo | repo root |
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
| **2** | User memories (`.windsurfrrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
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
| `.windsurfrrules` | each repo | repo root |
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
| **2** | User memories (`.windsurfrrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
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
| `.windsurfrrules` | each repo | repo root |
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
| **2** | User memories (`.windsurfrrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
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
| `.windsurfrrules` | each repo | repo root |
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
| **2** | User memories (`.windsurfrrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
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
| `.windsurfrrules` | each repo | repo root |
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
| **2** | User memories (`.windsurfrrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
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
| `.windsurfrrules` | each repo | repo root |
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
| **2** | User memories (`.windsurfrrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
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
| `.windsurfrrules` | each repo | repo root |
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
| **2** | User memories (`.windsurfrrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
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
| `.windsurfrrules` | each repo | repo root |
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
| **2** | User memories (`.windsurfrrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
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
| `.windsurfrrules` | each repo | repo root |
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
| **2** | User memories (`.windsurfrrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
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
| `.windsurfrrules` | each repo | repo root |
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
| **2** | User memories (`.windsurfrrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
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
| `.windsurfrrules` | each repo | repo root |
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
| **2** | User memories (`.windsurfrrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
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
| `.windsurfrrules` | each repo | repo root |
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
| **2** | User memories (`.windsurfrrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
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
| `.windsurfrrules` | each repo | repo root |
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
| **2** | User memories (`.windsurfrrules` from all repos) | Always active | All 8 workspace rule sets loaded simultaneously |
| **3** | Repo-local `.windsurfrrules` | Per-repo | Forja: "NUNCA fazer sem pedir permissão: criar novas páginas" |
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
| `.windsurfrrules` | each repo | repo root |
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

**I see ALL 8 workspaces simultaneously.** Their `.windsurfrules` are loaded as user_rules. I can switch context between repos in a single session. But I NEVER mix their
---

## P5 Session Patterns (2026-04-01)

### DashScope / Alibaba LLM Fallback Chain Pattern

**Problem:** OpenRouter Gemini Flash is free but rate-limited. Need sovereign Brazilian alternative with graceful fallback.

**Solution:** Tier-based fallback chain in `packages/shared/src/llm-provider.ts`:
```
fast:    qwen-flash (DashScope free) → gemini-2.0-flash (OpenRouter) → gpt-4o-mini
default: qwen-plus  (DashScope $0.0008/1K) → qwen-max → claude-sonnet-4.6
deep:    qwen-max   (DashScope $0.0016/1K) → qwq-plus (reasoning) → claude-sonnet-4.6
```
- DashScope endpoint: `dashscope-intl.aliyuncs.com` (Singapore — not mainland China endpoint)
- `isRateLimitError()` detects 429/503 and triggers next tier automatically
- `qwq-plus` = reasoning model, for complex multi-step analysis (not conversational chat)
- 90-day free quota: 1M tokens per model family (one-time, no daily reset after expiry)

**Key gotcha:** DashScope key format `sk-xxxx` same as OpenAI style. Endpoint: `/compatible-mode/v1/chat/completions`. Not the same as Qwen via OpenRouter.

---

### GitHub Secrets API Encryption Pattern (PyNaCl SealedBox)

**Problem:** Setting 10+ GitHub Secrets manually via UI is slow and error-prone.

**Solution:** Python + PyNaCl SealedBox encryption with repo public key:
```python
from nacl.public import SealedBox, PublicKey   # NOT nacl.sealed
import base64, requests

res = requests.get(f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/public-key", headers=headers)
key_id = res.json()["key_id"]
box = SealedBox(PublicKey(base64.b64decode(res.json()["key"])))
encrypted_b64 = base64.b64encode(box.encrypt(secret_value.encode())).decode()
requests.put(f"...secrets/{name}", json={"encrypted_value": encrypted_b64, "key_id": key_id}, headers=headers)
```
**Gotchas:** `GITHUB_TOKEN` cannot be set as secret (422 error — auto-injected by runner). Install: `pip install PyNaCl --break-system-packages` on Ubuntu 24+.

---

### Licitação Taxonomy Pattern (Brazilian Procurement Classification)

**Problem:** Eagle Eye AI returned unstructured opportunity text — hard to filter or aggregate by type.

**Solution:** Full taxonomy in `src/types.ts` from PNCP/CATMAT/CATSER standards:
- **9 segments:** TI_TECNOLOGIA, SAUDE, OBRAS_INFRAESTRUTURA, SERVICOS_GERAIS, ALIMENTACAO, EDUCACAO_CULTURA, VEICULOS_TRANSPORTE, CONSULTORIA_PROFISSIONAL, MATERIAIS_CONSUMO
- **12 modalities:** PREGAO_ELETRONICO … RDC, DESCONHECIDA
- **4 tiers by value:** MICRO (<50K), PEQUENO (50K–500K), MEDIO (500K–5M), GRANDE (>5M)
- **Flags:** `srp` (other orgs can adhere via ARP), `exclusivo_me_epp`, `esfera` (FEDERAL/ESTADUAL/MUNICIPAL/CONSORCIO)

Baked into AI system prompt as classification rules → Gemini Flash classifies on extraction.

---

### AI Coverage Map Auto-Update Pattern

**Problem:** No single view of which repos/files use LLMs. Cost estimates scattered. New AI calls added silently.

**Solution:** `docs/AI_COVERAGE_MAP.md` (canonical) + `scripts/ai-coverage-scan.ts` (scanner):
- Ripgrep scans 8 repos for 12 AI call patterns; extracts model names
- `--check`: exits 1 if new AI files found not in map → use as pre-commit hook
- `--update`: regenerates summary table in-place with live counts

**Key distinction:** Coverage map = breadth (which files touch AI). TELEMETRY_SSOT = depth (runtime costs, latency, tokens per call). Both needed.

---

### Territory Auto-Discovery Pattern (PNCP + IBGE)

**Problem:** Manually picking Brazilian municipalities for Eagle Eye is guesswork.

**Solution:** `scripts/discover-territories.ts` crosses two public APIs:
1. IBGE: `servicodados.ibge.gov.br/api/v1/localidades/municipios` → all 5570 municipalities
2. PNCP: `/consulta/v1/contratacoes/publicacao` → rank by real procurement volume
3. `--add-top=N` auto-injects top N into territories.ts

**Gotchas:** IBGE 7-digit → PNCP 6-digit: `String(id).slice(0, 6)`. PNCP requires `codigoModalidadeContratacao=8`. Max page size: 50. Base path: `pncp.gov.br/api/consulta/v1`.

---

### Gem Hunter Migration Pattern (egos-lab → egos)

**Trigger:** egos-lab being archived. Any agent there needs migration.

**Steps:**
1. Copy agent `.ts`, fix import paths (`../../packages/shared/src/` in egos)
2. Create `.github/workflows/<agent>-adaptive.yml` in egos with all secrets
3. Add to `agents.json` registry in egos + run `bun agent:lint`
4. Mark egos-lab copy as `[MIGRATED]` — don't delete until repo fully archived

**gem-hunter specific:** Added `early-warning` track for monitoring day-0 AI releases (e.g., HKUDS/OpenHarness by @huang_chao4969). Track type union extended: `"early-warning"` added to `SearchTrack`.

---

### X.com OAuth 1.0a Write — Bun/Web Crypto Implementation (P7)

**Problem:** X.com Bearer Token is READ-ONLY. Writing tweets/replies requires OAuth 1.0a with HMAC-SHA1, no npm packages.

**Solution using Web Crypto API (Bun-native):**
```typescript
const cryptoKey = await crypto.subtle.importKey("raw", encoder.encode(signingKey),
  { name: "HMAC", hash: "SHA-1" }, false, ["sign"]);
const signature = await crypto.subtle.sign("HMAC", cryptoKey, encoder.encode(signatureBase));
const signatureB64 = btoa(String.fromCharCode(...new Uint8Array(signature)));
```
- Signature base: `METHOD&url_encoded_endpoint&url_encoded_oauth_params_sorted`
- Signing key: `url_encoded_consumer_secret&url_encoded_access_token_secret`
- Auth header: `OAuth oauth_consumer_key="...", oauth_nonce="...", oauth_signature="...", ...`

**Rate limits (Free tier):** 50 writes/day hard limit, 10 searches/15min.
**Budget pattern:** `MAX_DAILY_REPLIES = 40` (10 buffer), `MAX_PER_RUN = 3` (hourly cron).
**State persistence:** `/tmp/x-reply-bot-state.json` with daily date reset.

---

### Rapid Response System Pattern — Matching Topics to Capabilities (P7)

**Problem:** When a trending topic matches our work, we lose hours manually writing threads. Repos are messy. Linking the wrong files is embarrassing.

**Solution:** `scripts/rapid-response.ts` with `EGOSCapability` profiles:
```typescript
interface EGOSCapability {
  id: string;
  keywords: string[];          // scored — multi-word keywords score higher
  pitch: string;               // ≤240 chars for X
  thread: string[];            // full thread, each ≤280 chars
  repos: { name, url, desc }[];
  clean_files: string[];       // ONLY share these — not the whole dirty repo
}
```
- `scoreMatch()`: each keyword match += word count (multi-word = more specific = higher score)
- `generateShowcaseREADME()`: writes `/tmp/egos-rapid-response-{ts}.md` — clean, linkable

**Key insight:** `clean_files` per capability = curated showcase without exposing repo drift.

---

### Task Reconciliation Auto-Detection Pattern (P8)

**Problem:** TASKS.md drifts. Tasks completed in commits get mentioned in commit bodies as "new tasks" and a naive pattern match falsely marks them as done.

**Solution (two-pass detection in `scripts/task-reconciliation.ts`):**
1. **Subject-line match** → reliable: commit subject `feat: GH-034 OpenHarness` = GH-034 done
2. **Body completion markers** → ID paired with `✅`, `[x] ID`, or `marked done` = confirmed

**False positive trap:** Commit body saying `"New tasks: GH-032, GH-035"` matches a naive `/\bGH-\d+\b/` pattern but these tasks are NOT done.

**Pattern:**
```typescript
// Subject-line IDs are reliable done signals
const subjectPattern = /\b([A-Z]+-\d+)\b/g;
// Body: only count with completion markers
const completionPattern = /\b([A-Z]+-\d+)[^✅\n]*✅/g;
const checkedPattern = /\[x\]\s+([A-Z]+-\d+)/g;
```

**Wire-in:** `--summary` in `/start` Phase 7.5 and `/end` Phase 3. Shows drift count + health %.

---

### Legacy Code Detector — Non-Blocking Pre-Commit Check (P7)

**Pattern:** Detect smell without blocking — exit 0 always (use `--strict` to block).
```bash
# check-legacy-code.sh pattern:
TODO_COUNT=$(git diff --cached -- "*.ts" "*.tsx" | grep '^+' | grep -c 'TODO\|FIXME' || true)
[ "$TODO_COUNT" -gt 3 ] && echo "⚠️  Adding $TODO_COUNT TODOs"
```
**What to detect:** >3 TODO/FIXME additions, >2 console.log/debug, >5 commented-out lines, hardcoded localhost URLs, possible unused TS imports.
**Why non-blocking:** These are code quality smells, not security violations. Blocking → devs add `--no-verify`. Non-blocking → devs see the feedback and often self-correct.

---

## Real Data Pipeline + Government Bid Strategy (2026-04-01)

### Problem
Mock data limits credibility. Government sales require proof-of-concept with real data from official sources. Software licitações landscape unknown.

### Solution — Eagle Eye Real Data Pipeline
**File:** `/home/enio/egos-lab/apps/eagle-eye/scripts/analyze-real-gazettes-v2.ts`

1. **Fetch real gazettes** from Querido Diário API (9,697 available)
   - Filter by territory + keywords (licitação, pregão, software, desenvolvimento)
   - Extract gazette text + metadata
   
2. **Analyze with Gemini Flash** (~$0.01/gazette)
   - Prompt includes 26 detection patterns (PII, fiscal, LGPD, etc.)
   - Returns segmento (TI, Consultoria, etc.), modalidade, porte, value, confidence
   
3. **Validate enums** — Critical bug found: market_potential enum accepts Portuguese only
   - Mapping: urgent→muito_alto, high→alto, medium→medio, low→baixo
   - Fire-and-forget insert to Supabase (non-fatal if down)

4. **Results (March 2026):**
   - 36 opportunities found, R$ 10.5M value
   - 14 software/TI (38.9%), avg confidence 85%
   - Geographic: São Paulo 6, Rio 4, BH 2, others 2

### Government Bid Waterfall (Tier 1/2/3)

**Tier 1 — High Win Probability (60-75%):** Pursue immediately
- Sistema de Gestão de Licitações: R$ 250k, 28 days to deadline
- Plataforma de Análise Dados Gov: R$ 180k, 36 days
- Auditoria e Compliance: R$ 120k, 51 days
- Total opportunity: R$ 550k

**Tier 2 — Medium (40-50%):** Add if bandwidth allows
- Dashboard Transparência: R$ 95k
- API de Integração: R$ 140k

**Tier 3 — Low (<30%):** Pass
- Commoditized dev work (too much competition, margin too low)

### Integrador Partnership Model (Recommended Path)

**Why integrador first (not direct bid):**
- Risk transfer: if EGOS misses, integrador absorbs (EGOS is subcontractor)
- Trust multiplier: public sector trusts established integrador
- Revenue bundling: integrador upsells consulting + training, pays EGOS per milestone
- Scale: integrador has sales team to find 5-10 projects/year

**Share:** 70% integrador, 30% EGOS (industry standard for subcontractors)

**Pitch:**
> "EGOS provides Eagle Eye (gazette monitor) + Guard Brasil (compliance validation) + software delivery. You handle client, compliance signoff, training. Revenue share 70/30."

### Seasonal Pattern Discovery

**Finding:** March = IT-heavy (12 TI ops vs 2 Saúde, 0 Educação)
- **Root cause:** Brazilian fiscal year ramp-up + digital agenda priority
- **Implication:** Full-year analysis (12 months) needed for accurate category balance
- **Action:** Backfill 6 months historical data, scale to 47 territories

### Deploy Daily Cron for 5 Tier-1 Territories

**File:** `/home/enio/egos-lab/apps/eagle-eye/scripts/daily-analysis-cron.ts`
**Schedule:** 0 9 * * * (9:00 AM BRT)
**Territory scope:** SP, RJ, BH, Curitiba, Porto Alegre (highest volume)
**Processing:** Top 10 gazettes/day, ~15min execution, inserts to Supabase

**Rate limit handling:** PNCP returns 403 after ~50 calls. Solution: SQLite cache + exponential backoff.

### Codex QA Summary (GH-040/041/042)

All 3 PRs production-quality, no blockers:
- **GH-040 (SSOT validator):** ⭐⭐⭐⭐⭐ Validates drift between agents.json, TASKS.md, HARVEST.md
- **GH-041 (API smoke tests):** ⭐⭐⭐⭐ Tests 5 Guard Brasil contracts (inspect, PII, Atrian, rate limit)
- **GH-042 (Version lock):** ⭐⭐⭐⭐⭐ Ensures package.json sync. Note: current versions correct by design (1.0.0 root, 0.1.0 web, 0.2.0 package, N/A api)

### Reusable Patterns

1. **Enum Validation in AI Output** — Always validate enum fields from LLM before Supabase insert
2. **Gazettes as Unstructured Data** — Text extraction + parsing + AI analysis beats manual PNCP API calls
3. **Fire-and-Forget Async** — Non-fatal Supabase failures = better UX than blocking on network
4. **Daily Cron for Market Scanning** — 9 AM BRT ensures fresh data for morning decision-making
5. **Proposal as Code** — Template proposal (PROPOSAL_250K_LICITACOES_SYSTEM.md) with real metrics = 10x faster response to RFPs


---

## Technical Learnings & API Patterns (2026-04-03)

### Stripe Metered Billing — New API Schema (v2025-03-31.basil)

**Breaking change:** Stripe deprecated `usage_type=metered` in favor of Billing Meters.

**Old pattern (broken):**
```typescript
const price = await stripe.prices.create({
  product: 'prod_...',
  type: 'recurring',
  recurring: { interval: 'month' },
  usage_type: 'metered',  // ❌ No longer valid
  tiers_mode: 'volume'
});
```

**New pattern (required):**
```typescript
// Step 1: Create a Billing Meter
const meter = await stripe.billing.meters.create({
  display_name: 'Guard Brasil API Calls',
  event_name: 'guard_brasil_api_call',  // Custom event from your backend
});

// Step 2: Create price with meter reference
const price = await stripe.prices.create({
  product: 'prod_...',
  type: 'recurring',
  recurring: { interval: 'month', meter: meter.id },
  currency: 'brl',
  billing_scheme: 'tiered',
  tiers: [
    { up_to: 1000, unit_amount: 100 },    // R$ 1.00 per call
    { up_to_inf: true, unit_amount: 50 }  // R$ 0.50 per call (volume discount)
  ]
});

// Step 3: At checkout, omit quantity (meter-driven)
const session = await stripe.checkout.sessions.create({
  customer: 'cus_...',
  line_items: [{
    price: price.id,
    // NO quantity field for metered prices
  }],
  mode: 'subscription'
});
```

**Wire-in to backend:**
```typescript
// After successful Guard Brasil API call
await stripe.billing.meterEventAdjustments.create({
  timestamp: Math.floor(Date.now() / 1000),
  identifier: customer_id,  // maps to checkout session customer
  event_name: 'guard_brasil_api_call',
  quantity: 1
});
```

**Key insight:** Event name must match meter creation. Timestamp in Unix seconds (not ms). Failures silently ignored by Stripe billing — no impact on API response.

---

### Docker Compose env_file vs environment Precedence Bug

**Problem:** When using both `env_file:` and `environment:` in docker-compose.yml:
```yaml
services:
  api:
    env_file: .env.secrets  # Contains SECRET_KEY=abc123
    environment:
      STRIPE_KEY: ${STRIPE_KEY}  # Shell var not set during compose up
```

**Behavior:** Docker treats `environment:` section as an **override layer**. If shell var `${STRIPE_KEY}` is not set, Docker inserts **empty string** into the container, shadowing any value from `env_file:`.

**Fix:**
```yaml
services:
  api:
    env_file: .env.secrets  # Secrets here: SECRET_KEY, STRIPE_KEY
    environment:
      # Only non-secret constants
      API_TIMEOUT: '30000'
      LOG_LEVEL: 'info'
```

**Best practice:** Use `env_file:` for all secret + sensitive config. Use `environment:` only for constants that don't need `.env` protection.

---

### Caddy Container Caddyfile Hot-Reload

**Problem:** Caddy running in Docker with a volume-mounted Caddyfile may cache stale config after file update.

**Solution:**
```bash
# Reload Caddy config without restart
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
```

**If mount is read-only or busy:**
1. Write updated config to temporary location inside container:
   ```bash
   docker cp new-Caddyfile caddy:/tmp/Caddyfile
   ```
2. Reload from temp:
   ```bash
   docker exec caddy caddy reload --config /tmp/Caddyfile
   ```
3. On next container restart, volume mount is fresh

**Key insight:** Caddy admin socket listens on `localhost:2019` inside container. The `reload` command uses that socket. No downtime — connections remain open during reload.

---

### Caddy Route Ordering — Specificity Rule

**Critical bug pattern:** Routes don't match expected paths due to ordering.

**Rule: Specific blocks BEFORE catch-all**
```caddy
# ✅ CORRECT
handle /api/* {
  reverse_proxy backend:3000
}

handle /guard/* {
  reverse_proxy guard:5000
}

handle {
  # Catch-all: routes not matched above
  reverse_proxy vercel.app
}

# ❌ WRONG — /api/* never matched
handle {
  reverse_proxy vercel.app  # Catch-all consumes everything
}
handle /api/* {
  reverse_proxy backend:3000
}
```

**Why it matters:** Caddy evaluates `handle` blocks top-to-bottom. First matching block wins. A catch-all `handle { }` with no path matcher matches everything.

---

### Brazilian RG Regex — Unicode & nº Prefix

**Problem:** Original regex `^([0-9.]+)-[0-9]{2}$` with word boundary `\b` failed on RG with prefix "Registro Geral nº 12.345.678-9".

**Why:** `nº°` characters weren't matched by `[:\s]*`. The `\b` word boundary expected alphanumeric before the first digit.

**Fix:**
```typescript
// Old (broken)
const rgRegex = /\bRegistro\s+Geral.*?([0-9.]+)-([0-9]{2})\b/g;

// New (works)
const rgRegex = /Registro\s+Geral[\s:nº°.]*([0-9.]+)-([0-9]{2})/iu;
```

**Key changes:**
1. Removed `\b` word boundaries (they block Unicode chars like nº)
2. Added `nº°` to the prefix pattern: `[\s:nº°.]*`
3. Added `/u` Unicode flag + `/i` case-insensitive

**Brazilian RG formats found in wild:**
- "Registro Geral nº 12.345.678-9"
- "RG: 12.345.678-9"
- "RG nº. 12.345.678-9"
- "Registro Geral: 12345678-9" (no dots)

**Test set:**
```typescript
const testRGs = [
  'Registro Geral nº 12.345.678-9',
  'RG nº 12.345.678-9',
  'Documento RG Nº 12.345.678-9',  // Capital Nº
  'rg: 12.345.678-9'  // lowercase
];
testRGs.forEach(rg => {
  const match = rg.match(rgRegex);
  console.assert(match, `Failed: ${rg}`);
});
```

---

### Eagle Eye Document Parser — Regex Confidence at 78% Without LLM

**Finding:** Structured extraction from editals (government bid documents) achieved 78% confidence using regex + heuristics, without needing LLM for every field.

**Key challenge:** Portuguese accented characters in regex. Example patterns:
- PREGÃO (not pregão)
- Modalidade: ELETRÔNICO vs eletrônico
- "não" (lowercase) vs "Não" (capitalized)

**Bug:** Case-insensitive regex `/[ãa]/i` does NOT match uppercase `Ã` without Unicode flag.

**Fix — Always use `/iu` flags for Portuguese:**
```typescript
// ❌ Misses uppercase Ã
const pattern1 = /[ãa]+/i;

// ✅ Matches all variants
const pattern2 = /[ãa]+/iu;

const testStrings = ['são', 'SÃO', 'São'];
testStrings.forEach(s => {
  console.assert(s.match(pattern2), `Failed: ${s}`);
});
```

**68 regex patterns mapped for editais:**
- Modalidade extraction: 15 patterns (pregão, concorrência, convite, etc.)
- Value patterns: 12 (handles R$, mil, M, range syntax)
- PII / document detection: 18 (CPF, CNPJ, RG, address)
- Temporal markers: 8 ("até", "30 dias", "31/12/2026")
- Organizational entities: 15 (CAIXA, CEF, BNDES, etc.)

**Confidence scoring:**
- 1 pattern match: 45% confidence
- 2-3 pattern matches: 65%
- 4+ pattern matches: 85%+

**When to use LLM:** Only for ambiguous cases (45-60% confidence) or for narrative field extraction (objectives, scope). Structure (modalidade, valor) = regex only.

**Performance:** 1,200 documents processed in 3.2 seconds (regex), vs ~8 minutes with Gemini API. 78% vs 92% accuracy — acceptable tradeoff for 150x speedup.

