# Contributing to EGOS

> Rules govern agents. Agents enforce rules. Community evolves rules.

Thank you for your interest in contributing to EGOS! This document explains
the governance model, coding standards, and contribution workflow.

## Prerequisites

- **Bun** (latest) or Node 20+
- **Git** with conventional commit discipline
- Familiarity with TypeScript

## Quick Setup

```bash
git clone https://github.com/enioxt/egos.git
cd egos
bash setup.sh          # installs deps, validates env
bun run typecheck      # must pass before any work
bun run governance:check  # must show 0 drift
```

## Governance Model

EGOS uses a **kernel + leaf** architecture:

- **Kernel** (`/home/enio/egos`) — governance DNA, agent runtime, shared packages
- **Leaves** (egos-lab, carteira-livre, etc.) — consume kernel governance via `~/.egos/`

All governance changes flow **kernel → shared home → leaves**. Never edit
governance files in a leaf repo.

## Core Rules

1. **CHALLENGE before EXECUTE** — question, detect contradictions, ask for evidence
2. **DRY-RUN FIRST** — every agent supports `--dry` before `--exec`
3. **ZERO DEPS** — agents use only Node/Bun stdlib, no external frameworks
4. **REGISTRY** — no agent runs without an entry in `agents/registry/agents.json`
5. **SHARED** — reusable code goes in `packages/shared/`, zero duplication
6. **FROZEN ZONES** — never edit protected files without explicit approval

### Frozen Files

These files require explicit maintainer approval to modify:

- `agents/runtime/runner.ts`
- `agents/runtime/event-bus.ts`
- `.husky/pre-commit`
- `.guarani/orchestration/PIPELINE.md`

## Contribution Workflow

### 1. Pick a Task

Check `TASKS.md` for open items. Tasks are prefixed `EGOS-XXX` and
prioritized as P0 (blocker), P1 (critical), P2 (important), or Backlog.

### 2. Create a Branch

```bash
git checkout -b feat/EGOS-XXX-short-description
```

### 3. Implement

- Follow existing code style (see `.guarani/PREFERENCES.md`)
- Use `routeForChat(taskType)` before any LLM call
- All AI calls go through `packages/shared/src/llm-provider.ts`
- Mask PII (CPF, email) in all output
- Never hardcode secrets — use `.env`

### 4. Validate

```bash
bun run typecheck         # TypeScript strict check
bun agents/cli.ts lint-registry  # Registry consistency
bun run governance:check  # Governance drift = 0
```

### 5. Commit

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(agents): add new compliance checker agent
fix(shared): correct model router scoring for economy tier
docs(governance): update DOMAIN_RULES for kernel reality
```

### 6. Push & PR

```bash
git push origin feat/EGOS-XXX-short-description
```

Open a PR against `main`. CI will run typecheck + registry lint.

## Adding a New Agent

1. Create `agents/agents/your-agent.ts`
2. Add entry to `agents/registry/agents.json`
3. Support `--dry` mode (default)
4. Produce structured JSON output
5. Use `routeForChat()` for model selection
6. Run `bun agents/cli.ts lint-registry` to validate
7. Test with `bun agent:run your-agent --dry`

## Model Router

EGOS uses a task-aware model router (`packages/shared/src/model-router.ts`).
Before any LLM call, declare the task type:

```typescript
import { routeForChat } from '@egos/shared';
import { chatWithLLM } from '@egos/shared';

const route = routeForChat('code_review');
const result = await chatWithLLM({
  ...route,
  systemPrompt: '...',
  userPrompt: '...',
});
```

Available task types: `orchestration`, `code_generation`, `code_review`,
`analysis`, `summarization`, `classification`, `chat`, `translation`,
`extraction`, `fast_check`.

## Security

- **No secrets in code** — use `.env` (see `.env.example`)
- **PII masking** — CPF and email must be masked in all output
- **RLS** — every new Supabase table must have Row Level Security enabled
- **Pre-commit** — gitleaks + tsc + frozen zone checks run automatically

## Questions?

Open an issue on [GitHub](https://github.com/enioxt/egos/issues) or
check `docs/` for architecture documentation.
