# /start — Session Initialization (v5.1)

## 1. Load Core Context

Read these files in order (all paths relative to repo root):

- `AGENTS.md` — Project config, stack, commands, SSOT files list
- `TASKS.md` — Current priorities (P0 → P1 → P2)
- `.guarani/PREFERENCES.md` — Coding standards and rules
- `.guarani/IDENTITY.md` — Agent identity and mission

## 2. Load Orchestration System

Read the orchestration pipeline that governs ALL work:

- `.guarani/orchestration/PIPELINE.md` — 7-phase protocol (INTAKE → CHALLENGE → PLAN → GATE → EXECUTE → VERIFY → LEARN)
- `.guarani/orchestration/GATES.md` — 5-dimension quality scoring (score >= 75 to proceed)
- `.guarani/orchestration/QUESTION_BANK.md` — 70+ maieutic questions by domain
- `.guarani/orchestration/DOMAIN_RULES.md` — Project-specific checklists

Acknowledge: "Orchestration Protocol loaded. Pipeline: 7 phases. Gate threshold: 75."

## 3. Load Meta-Prompt System

Scan `.guarani/prompts/triggers.json` for active trigger mappings:

- `.guarani/prompts/PROMPT_SYSTEM.md` — Meta-prompt index (anatomy, triggers, catalog)
- `.guarani/prompts/triggers.json` — Machine-readable keyword→prompt mappings
- `.guarani/prompts/meta/universal-strategist.md` — Game Theory + Oriental philosophy
- `.guarani/prompts/meta/brainet-collective.md` — Collective intelligence lens
- `.guarani/prompts/meta/mycelium-orchestrator.md` — Recursive sync, mesh reality, self-improvement loop
- `.guarani/philosophy/TSUN_CHA_PROTOCOL.md` — Dialectical debate protocol

Acknowledge: "Meta-prompt system loaded. [N] prompts, [N] triggers active."

If the task mentions `mycelium`, `mesh`, `sync`, `agents`, `auto melhorar`, or `teia`, load `.windsurf/workflows/mycelium.md` immediately after `/start`.

## 4. Load Refinery (Intent Processing)

For MODERATE+ tasks, the Refinery activates automatically:

- `.guarani/refinery/classifier.md` — Intent classification (FEATURE/BUG/REFACTOR/KNOWLEDGE)
- `.guarani/refinery/interrogators/` — 4 specialized interrogators by type
- `.guarani/preprocessor.md` — Vague→explicit translation with persona simulation

These are loaded ON-DEMAND when the pipeline activates. No need to read all at start.

If the task involves setup, auth, platform configuration, or multiple valid paths, prefer `ask_user_question` early to keep the human in the loop. Default to multiple-choice prompts unless the choice is strictly binary/exclusive.

## 5. Rule Checksum Validation

> **CRITICAL:** LLMs suffer from probabilistic rule drift over long contexts.

Read `.windsurfrules` and confirm the active ruleset:
- Print: "Rules v[X.X.X] loaded. Mandamentos: [count]. Frozen zones: [count]."
- Verify `AGENTS.md` version matches `.windsurfrules` expectations.

## 6. System Map & Handoff

- Read `docs/SYSTEM_MAP.md` for full system overview
- Check latest handoff in `docs/_current_handoffs/` (most recent file)
- Recent commits: `git log --oneline -5`

## 7. Cost Monitor

| Resource | Warning | Critical |
|----------|---------|----------|
| Vercel usage | > 50% | > 75% (STOP) |
| Supabase DB | > 500 MB | > 2 GB (EMERGENCY) |

## 8. Tooling Session Check (MANDATORY)

The agent MUST verify these before implementation work:

| Tool | Check command | Required? | Default |
|------|--------------|-----------|--------|
| Codex | `codex --version` | MODERATE+ tasks | `codex review --uncommitted` |
| Codex cloud | `codex cloud list` | If pending tasks exist | Inspect before new work |
| Alibaba | `.env` has `ALIBABA_DASHSCOPE_API_KEY` | Yes | `alibaba:qwen-plus` |
| Session guard | `bun run session:guard` | Pre-commit | Recovers handoff + checks readiness |
| Gem Hunter | `ls -t docs/gem-hunter/gems-*.md 2>/dev/null \| head -1` | Research sessions only | Suggest if > 7 days old |
| Report Generator | `ls -t docs/reports/report-*.html 2>/dev/null \| head -1` | Research sessions only | `bun agent:run report-generator --exec` |

Rules:

- Codex runs in a **parallel terminal**, NEVER in main chat
- Codex NEVER owns SSOT; it reviews under human/Cascade supervision
- Alibaba is the preferred orchestrator when configured

## 9. Output Briefing

Present to user:

- **Rules:** Version + mandamento count + orchestration status
- **Tasks:** P0 blockers → P1 sprint → P2 backlog (counts)
- **Handoff:** Last session summary (1-2 lines)
- **Recent commits:** Last 5 commits
- **Meta-prompts:** Count loaded + active triggers
- **Codex:** Availability + pending cloud tasks + chosen mode (cloud vs local read-only)
- **Alibaba:** Availability + chosen orchestrator provider/model
- **Research:** Latest gem-hunter report age + report count
- **Orchestration:** "Pipeline active. Refinery ready. Gate threshold: 75."

---

## File Existence Check

Required (flag if missing): `AGENTS.md`, `TASKS.md`, `.windsurfrules`, `.guarani/PREFERENCES.md`, `.guarani/IDENTITY.md`, `.guarani/orchestration/PIPELINE.md`, `.guarani/orchestration/GATES.md`, `.guarani/orchestration/QUESTION_BANK.md`, `.guarani/orchestration/DOMAIN_RULES.md`, `.guarani/refinery/classifier.md`, `.guarani/refinery/interrogators/*.md`, `.guarani/preprocessor.md`, `.guarani/prompts/PROMPT_SYSTEM.md`, `.guarani/prompts/triggers.json`, `docs/SYSTEM_MAP.md`.

Optional: `.guarani/philosophy/TSUN_CHA_PROTOCOL.md`, `.guarani/MCP_ORCHESTRATION_GUIDE.md`, `.guarani/DESIGN_STANDARDS.md`.

---

*v5.3 — Compressed Codex/Alibaba/Research into single dispatch table (step 8), removed redundant sub-sections 8.5/8.7*
