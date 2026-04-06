# EGOS Preferences — Coding Standards

> **Version:** 1.1.0 | **Updated:** 2026-04-06

## Security

- Pre-commit entropy check: gitleaks on every commit.
- API Keys: NEVER hardcode. Use `.env` only.
- PII: Agents MUST mask CPF/email in all output.
- Prompt Injection: Sanitize external text before LLM calls.
- RLS ALWAYS ON: Every new table MUST have `ENABLE ROW LEVEL SECURITY`.

## Code Quality

- TypeScript strict mode (`"strict": true` in tsconfig).
- Max file size: 300 lines (refactor if exceeded).
- Conventional commits: `feat:`, `fix:`, `chore:`, `docs:`.
- Never create Supabase clients at module top-level (lazy init).
- MAX_DEPTH ~50 for recursive operations. IGNORE_DIRS: `External/`.

## Governance Canon

- `.guarani/RULES_INDEX.md` is the canonical entry point for rules in every environment.
- Kernel `.guarani/` is authoritative; `~/.egos/guarani/` is the synced mirror.
- `CLAUDE.md` and `.windsurfrules` are adapter surfaces only; if they conflict with `.guarani`, `.guarani` wins.

## Agent Conventions

- Registry first: `agents/registry/agents.json` is SSOT.
- Runner always: use `agents/runtime/runner.ts` for all execution.
- Dry-run default: `--dry` before `--exec`, always.
- Zero deps: agents use only Node/Bun stdlib. No framework dependencies.

## MCP Usage

- Prioritize MCP tools over manual implementation when a trusted tool exists.
- Supabase MCP for database operations.
- GitHub MCP for repo operations.
- Exa MCP for web search.
- Memory MCP for knowledge persistence.

## Reasoning Discipline

- Mark claims as `Verified`, `Inferred`, or `Proposed`.
- Evidence first: code, endpoint, log, or runtime proof.
- Atomize criteria into explicit, testable bullets.
- Never call something live without runtime evidence.
- Never call something missing before searching for it.
- **P0 CONSTITUTIONAL:** Present dialectic questions (Options A/B/C with tradeoffs) before executing MODERATE+ tasks. Minimum 3 questions. User alignment required.

## Rollout & Launch Planning

- Every MODERATE+ product, rollout, or deployment task MUST define dependencies and exact execution order before implementation.
- TASKS.md rollout sections MUST name gates explicitly: `deploy`, `security`, `ux`, and `launch`.
- No deploy starts before health checks, smoke checks, monitoring path, and rollback path are explicit.
- No launch starts before disclaimer/copy review, UX acceptance, and analytics/feedback path are explicit.
- Reusable rollout patterns MUST be disseminated to `TASKS.md`, `docs/knowledge/HARVEST.md`, and the relevant `.guarani` rule surface.

## Design & UI

- Tailwind CSS for styling. Lucide for icons.
- Dark mode first. Framer Motion for animations.
- Fitts's Law: minimum 40x40px hit areas.
- No em-dashes in public copy.

## Docker & Infrastructure

- **NO INFINITE LOOPS:** Never use `restart: always` in local or development containers. Use `restart: on-failure:3` or `unless-stopped` to prevent zombie containers from draining CPU and Disk I/O during crash loops.
- **MONITORING:** EGOS Guardian script should be used to detect and auto-kill anomalous containers.
