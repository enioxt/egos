# HARVEST.md — EGOS Core Knowledge

> **VERSION:** 2.0.0 | **UPDATED:** 2026-03-21
> **PURPOSE:** compact accumulation of reusable patterns discovered in the kernel repo

## Agent Operating Protocol (Self-Diagnostic v1.0)

> **What:** Complete atomic documentation of how a governed EGOS agent (Cascade) operates.
> **Why:** So any agent (Cline, Claude Code, Codex, future) or human can replicate this protocol.
> **Philosophy:** "Saímos de casa para nos doar" — everything we learn, we share.

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
| **Cline** | Exploratory UI, product edits | MUST NOT touch .guarani/, .windsurf/, .egos/ |
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
  → Load AGENTS.md, TASKS.md, .windsurfrules
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
| **852** | Product (chatbot) | `/home/enio/852` | Contabo VPS + Docker |
| **carteira-livre** | Product (marketplace) | `/home/enio/carteira-livre` | Vercel (auto) |
| **forja** | Product (ERP) | `/home/enio/forja` | Vercel |
| **br-acc** | Intelligence platform | `/home/enio/br-acc` | Contabo VPS + Docker |
| **policia** | Investigation workspace | `/home/enio/policia` | Local only |
| **santiago** | WhatsApp SaaS | `/home/enio/santiago` | Vercel + Contabo |

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
- `.windsurfrules` MANDAMENTO 15: governance changes are not complete until `bun run governance:sync:exec` + `bun run governance:check` return 0 drift.

## Cross-Repo SSOT Mesh

- `docs/SSOT_REGISTRY.md` is now the canonical registry for workspace-wide SSOT ownership.
- Kernel-owned SSOT docs must propagate through `scripts/governance-sync.sh` to `~/.egos/docs/`.
- Leaf repos must keep local pointers in `TASKS.md`, `AGENTS.md`, and local system maps instead of inventing parallel global truth.
- Canonical global SSOT changes are incomplete until both the kernel docs and leaf adoption tasks are updated.

## Workflow Inheritance

- Shared workflows such as `/start`, `/end`, and `/disseminate` should live in the kernel and propagate through `~/.egos/workflows`.
- Leaf repos should either use a symlink/exact inherited copy or a thin local wrapper only when repo-specific precedence is truly required.
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

## Multi-Model Meta-Prompt Analysis (2026-03-24)

### Context
Comprehensive analysis of 5 AI model responses (Gemini, Codex, Nemotron, Grok, ChatGPT, Claude Code) regarding Mycelium architecture, meta-prompt generator improvements, and EGOS ecosystem evolution.

### Key Insights

**1. Universal Consensus — Hub-and-Spoke Mycelium**
- Central control plane with reusable GitHub Actions workflows
- Git submodules for knowledge propagation
- Repository dispatch events for cross-repo synchronization
- Registry pattern: `repos/registry.yaml` + `prompts/registry.yaml`

**2. Meta-Prompt Generator — 5 Critical Improvements**
| # | Improvement | Source | Priority |
|---|-------------|--------|----------|
| 1 | Auto-reflection module (environment audit) | Gemini | P0 |
| 2 | Dynamic constraint injection (JSON/YAML blocks) | Gemini | P0 |
| 3 | Few-shot prompting > extensive rules | Gemini | P1 |
| 4 | Drift detection (SSOT vs projections) | ChatGPT | P0 |
| 5 | Semantic versioning (major/minor/patch) | ChatGPT | P1 |

**3. Operational Findings**
- egos-lab #26: Active, mergeable, security fixes → MERGE NOW
- egos-cortex #1: Stale (Feb 16), needs rebase → DO NOT MERGE
- Drift detected: `.guarani/prompts/meta/mycelium-orchestrator.md` returns 404
- BLUEPRINT-EGOS disconnected from kernel egos

**4. DSL Definition — Named Workflows**
| Command | Function |
|---------|----------|
| `/start` | Load registries, read repo state, update snapshot |
| `/mycelium` | Resolve deps, sync taxonomies, detect drift |
| `/disseminate` | Publish summary to output channels |
| `/end` | Persist snapshot, stamp execution, update final report |

**5. ATRiAN Ethics Assessment**
| Criterion | Rating |
|-----------|--------|
| Accuracy | 9.2/10 |
| Truth | 9.5/10 |
| Reversibility | 8.8/10 |
| Impact | 8.5/10 |
| Accountability | 8.0/10 |
| Neutrality | 9.0/10 |
| **Overall** | **8.8/10** |

**6. 5-Phase Implementation Roadmap**
1. **Control** (3 days): Choose canonical repo, create registries
2. **Observability** (1 week): PR classifiers, daily snapshots
3. **Meta-prompts** (2 weeks): Materialize conceptual → actual
4. **Dissemination** (2 weeks): Payload generation, webhooks
5. **Distributed Execution** (1-2 months): Named workflows, GitHub Actions + CLI

### Files Created/Updated
- `.agents/workflows/mycelium-disseminate.md` — Unified workflow
- `repos/registry.yaml` — Repository SSOT
- `prompts/registry.yaml` — Prompt registry
- `scripts/pr-classifier.ts` — PR classification
- `mycelium-graph.json` — Dependency graph

### Aphorism
"Código aberto sem malha vira arquivo espalhado. Código aberto com Mycelium vira sistema navegável." — ChatGPT

Open source without mesh becomes scattered files. Open source with Mycelium becomes a navigable system.
**Pattern:** Always prioritize explicit business SSOT (`inventory.md`) over leftover promotional mockup copy in frontend files (`App.tsx`). The EGOS ecosystem is strictly about the "Honest MVP" narrative (6 real products, split 95/5). The empty `/home/enio/commons` directory was ignored in favor of the monitored mono-repo structure in `egos/apps/commons`.

---

## Session 2026-03-25 — Claude Code Hub + FORJA Visão

### Claude Code as EGOS Hub (Phase 1)

**Pattern:** Claude Code can function as a lightweight orchestration kernel using:
- `~/.claude/config/` — JSON config for model routing + status line
- `~/.claude/scripts/` — TypeScript/bash for routing logic + watch scripts
- `.claude/commands/*.md` — Slash commands aligned with `.windsurf/workflows/`
- `~/.claude/dashboards/` — Markdown dashboards for session status

**Key insight:** Windsurf `.windsurf/workflows/*.md` and Claude Code `.claude/commands/*.md` are analogous interfaces — keep them synchronized for cross-IDE continuity.

**VPS Discovery:** `ssh -p 22 root@217.216.95.126` (not 2244!) — 2 PM2 agents (egos-telegram, egos-discord) + 8 Docker services (852-app, waha-santiago, infra-api-1, infra-frontend-1, bracc-neo4j, infra-caddy-1, infra-redis-1, egos-media-web-1).

### FORJA Visão — Camera Analytics Module

**Architecture decision:** Frigate NVR (Docker) → MQTT event bus → FastAPI bridge → Supabase → FORJA frontend.

**SVG Charts without deps:** Pure SVG box plots work well for cycle time distribution visualization without adding Recharts or D3. Key pattern: `scale = (v) => PAD + (v / maxVal) * (W - PAD * 2)`.

**Gauge meters:** Semicircular arc gauges using SVG path with `A` (arc) commands. Use `toRad()` helper and define start/end degrees (-220° to +40° = 260° sweep).

**Mock-first approach:** FORJA Visão built with realistic mock data matching production schema — same TypeScript interfaces as future Supabase queries. Sprint 2 replaces mocks with real queries without changing component interfaces.

**Pattern — zone editor:** SVG canvas with `viewBox="0 0 200 112"` (16:9 aspect) for camera zone polygon drawing. Grid overlay with `patternUnits="userSpaceOnUse"` for alignment reference.

**MQTT event schema fields:** `tenant_id`, `factory_id`, `family_id`, `order_id`, `camera_id`, `zone_id`, `event_type`, `piece_id`, `ts_in`, `ts_out`, `cycle_ms`, `confidence`.

**Anomaly severity tiers:** `critical` (exceeded baseline >50% or skipped QA stage), `warning` (stopped >15min or out-of-sequence), `info` (below minimum historical — possible quality skip).

### Windsurf ↔ Claude Code Workflow Sync

**Rule:** Always keep `.windsurf/workflows/*.md` as the SSOT master and `.claude/commands/*.md` as synchronized mirrors. Windsurf workflows have richer SecOps gates (BLOCKING), Codex readiness checks, and Alibaba orchestration checks.

**v5.5 additions:** Phase 4.1 Security Dependency Check (BLOCKING on UNMITIGATED CVE), explicit Codex cloud list, repo-role awareness via `egos.config.json`.
