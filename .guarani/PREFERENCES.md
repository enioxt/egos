# EGOS Preferences — Coding Standards

> **Version:** 1.0.0 | **Updated:** 2026-03-13

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

## Design & UI

- Tailwind CSS for styling. Lucide for icons.
- Dark mode first. Framer Motion for animations.
- Fitts's Law: minimum 40x40px hit areas.
- No em-dashes in public copy.

## Docker & Infrastructure

- **NO INFINITE LOOPS:** Never use `restart: always` in local or development containers. Use `restart: on-failure:3` or `unless-stopped` to prevent zombie containers from draining CPU and Disk I/O during crash loops.
- **MONITORING:** EGOS Guardian script should be used to detect and auto-kill anomalous containers.
