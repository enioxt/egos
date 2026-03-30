# DOMAIN RULES — EGOS Kernel

> **Version:** 2.0.0 | **Updated:** 2026-03-13
> **Project:** egos (orchestration-kernel + agent-runtime)

---

## How to Use

When a task touches a specific domain, load that domain's section
and apply its checklist BEFORE executing. Multiple domains can apply.

> **Note:** This file covers the **kernel repo** (`/home/enio/egos`).
> Leaf-repo-specific domains (egos-web, telegram-bot, eagle-eye, nexus)
> live in their own `DOMAIN_RULES.md` or inherit from `~/.egos/guarani/`.

---

## 1. AGENTIC PLATFORM

### SSOT

- **Agent registry:** `agents/registry/agents.json` (SSOT for all agents)
- **Agent runner:** `agents/runtime/runner.ts` (frozen zone)
- **Agent CLI:** `agents/cli.ts`
- **Agent implementations:** `agents/agents/*.ts`
- **Shared utils:** `packages/shared/src/` (llm-provider, model-router, types)

### Anti-Patterns

- Creating an agent without a registry entry
- Agent depending on external npm packages (zero-deps rule)
- Running `--exec` without first running `--dry`
- Duplicating logic that exists in `packages/shared/`
- Modifying `agents/runtime/runner.ts` without explicit approval

### Checklist

- [ ] Agent has registry entry in `agents.json` (id, name, description, path)
- [ ] Agent supports `--dry` mode (default)
- [ ] Agent produces structured JSON output
- [ ] Agent uses `packages/shared/src/llm-provider.ts` for AI calls
- [ ] Agent calls `routeForChat(taskType)` before LLM invocation
- [ ] Agent is idempotent (safe to re-run)
- [ ] Cost tracked per AI call
- [ ] PII masked in all output (CPF, email)

### Frozen Files

```
agents/runtime/runner.ts
agents/runtime/event-bus.ts
agents/registry/agents.json (structure, not content)
```

---

## 2. LLM PROVIDER & MODEL ROUTER

### SSOT

- **LLM client:** `packages/shared/src/llm-provider.ts`
- **Model router:** `packages/shared/src/model-router.ts`
- **Rate limiter:** `packages/shared/src/rate-limiter.ts`
- **Env vars:** `ALIBABA_DASHSCOPE_API_KEY`, `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `GROQ_API_KEY`
- **Reference:** `.env.example` for all expected keys

### Anti-Patterns

- Hardcoding a model name without going through `routeForChat()`
- Adding a new LLM provider without updating `MODEL_CATALOG`
- Calling APIs without checking `isAvailable()` first
- Ignoring cost tiers (using premium for bulk/cheap tasks)

### Checklist

- [ ] New model added to `MODEL_CATALOG` with accurate pricing
- [ ] Task type defined in `TaskType` union if new
- [ ] `.env.example` updated if new env key required
- [ ] End-to-end test with real API call passes
- [ ] Cost tracked in `AIAnalysisResult.cost_usd`

---

## 3. GOVERNANCE & SYNC

### SSOT

- **Governance DNA:** `.guarani/` (identity, orchestration, prompts, philosophy)
- **Sync script:** `scripts/governance-sync.sh` (kernel → `~/.egos` → leaf repos)
- **Shared home:** `~/.egos/` (guarani + workflows)
- **Downstream sync:** `~/.egos/sync.sh`
- **Legacy cleanup only:** `~/.egos/governance-symlink.sh` (manual remediation, not primary sync plane)
- **Repo-local surfaces:** `.windsurfrules`, `.guarani/IDENTITY.md`, `.guarani/PREFERENCES.md`
- **Governance check:** `bun run governance:check`

### Anti-Patterns

- Editing governance files in leaf repos instead of the kernel
- Forgetting to propagate after kernel edits
- Creating leaf-specific overrides that shadow kernel rules
- Using `governance-symlink.sh` as if it were the canonical propagation path
- Moving tool secrets or Claude/Codex user auth into repo-tracked config

### Checklist

- [ ] Change made in kernel `.guarani/` first
- [ ] Repo-local rule surfaces (`.windsurfrules`, `IDENTITY.md`, `PREFERENCES.md`) kept local unless a repo-role decision explicitly changes that policy
- [ ] `scripts/governance-sync.sh --exec` run after edits
- [ ] `~/.egos/sync.sh` propagated to all leaves
- [ ] User-scope tool secrets and MCP auth kept outside repo-tracked files
- [ ] `bun run governance:check` passes with 0 drift
- [ ] No hardcoded secrets or API keys

---

## 4. SECURITY

### SSOT

- **Pre-commit:** `scripts/security_scan.ts` + `scripts/ssot_governance.ts`
- **Frozen zones:** `agents/runtime/runner.ts`, `agents/runtime/event-bus.ts`, `.husky/`, `.guarani/orchestration/PIPELINE.md`
- **PII policy:** Mask CPF/email in ALL agent output
- **Prompt injection:** Sanitize external text before LLM
- **RLS:** Every new Supabase table MUST have RLS enabled

### Checklist

- [ ] No secrets in committed code (gitleaks clean)
- [ ] PII masked in logs and agent output
- [ ] External text sanitized before LLM calls
- [ ] RLS enabled on new tables
- [ ] Frozen zones untouched unless user-approved

---

## 5. SHARED PACKAGES

### SSOT

- **Path:** `packages/shared/src/`
- **LLM client:** `llm-provider.ts` (all AI calls go through here)
- **Model router:** `model-router.ts` (task-aware model selection)
- **Types:** `types.ts`
- **ATRiAN:** `atrian.ts` (ethical validation)
- **PII scanner:** `pii-scanner.ts`
- **Conversation memory:** `conversation-memory.ts`
- **Rate limiter:** `rate-limiter.ts`
- **Exports:** `index.ts` (barrel file)

### Anti-Patterns

- Duplicating logic that exists in shared packages
- Agent-specific code leaking into shared packages
- Breaking the llm-provider interface without updating all consumers
- Adding leaf-repo-specific utilities (OSINT, social, etc.) to shared

### Checklist

- [ ] New shared code is truly reusable (not agent-specific)
- [ ] TypeScript types exported via `index.ts`
- [ ] No circular dependencies
- [ ] `bun run typecheck` passes
- [ ] All consumers updated if interface changes

---

## 6. INTEGRATIONS & CHANNELS

### SSOT

- **Release contract:** `.guarani/orchestration/INTEGRATION_RELEASE_CONTRACT.md`
- **Contracts:** `integrations/_contracts/`
- **Manifests:** `integrations/manifests/`
- **Bundles:** `integrations/distribution/`
- **Gate:** `bun run integration:check`

### Anti-Patterns

- Calling an integration `validated` based only on a stub in `_contracts/`
- Documenting setup without a compact distribution artifact
- Shipping a bundle without `.env.example` when secrets are required
- Claiming runtime readiness without proof (`log`, `endpoint`, `runbook`, or equivalent)

### Checklist

- [ ] Manifest exists and is semver-valid
- [ ] SSOT, setup, and runbook refs are present
- [ ] Runtime proof is recorded
- [ ] Bundle exists in `integrations/distribution/<id>/`
- [ ] `validation.smokeCommand` passes
- [ ] `bun run integration:check` passes before merge/dissemination

---

## 7. CROSS-REPO SSOT VISIT PROTOCOL

**Rule:** Whenever you visit a file, directory, or repo that is NOT the current working repo to extract information or migrate content, you MUST mark the visit immediately. This applies in /start, /end, /disseminate, pre-commit, and any cross-repo search task.

### Protocol Steps

1. **MARK the source** — Add a `<!-- SSOT-VISITED: YYYY-MM-DD by claude, extracted to [target] -->` comment or a markdown note at the top of the source file if it's a doc.
2. **LOG the visit** in the current repo's `docs/_current_handoffs/` or `TASKS.md` with format:
   `- [x] SSOT-VISIT [date]: [source-repo/path] → extracted [what] → [disposition: archived|merged|kept-as-ref]`
3. **MARK duplicates** — If you find a duplicate of canonical content, mark the copy with `<!-- DUPLICATE: canonical at [path], keep as [ref|delete|merge] -->` and create a task to resolve.
4. **ARCHIVE after extraction** — If the source was purely aspirational/wrong, move it to `archive/` in the same repo and add an entry in the nearest TASKS.md.
5. **NEVER leave a cross-repo visit unlogged.** Missing the log is a governance violation.

### Applies to
- `/start` skill: scan visited repos → log all SSOT gaps found
- `/end` skill: verify all cross-repo visits are logged before closing session
- `/disseminate` skill: log which files were propagated to which repos
- Pre-commit hooks: if staged files contain cross-repo path references, warn if visit log is missing
- Any Agent or Explore task that reads from multiple repos

### Disposition Tags

| Tag | Meaning |
|----|---------|
| `archived` | Moved to `archive/` in source repo |
| `merged` | Content absorbed into target, source deleted or noted |
| `kept-as-ref` | Source kept but not canonical — target is SSOT |
| `superseded` | Source was wrong/outdated — replaced by target |
| `independent` | Both are canonical for different purposes |

---

## Domain Detection Heuristic

| Task Keywords | Domains to Load |
|---------------|----------------|
| agent, registry, runner, orchestrator, dry-run | Agentic Platform |
| llm, model, qwen, openrouter, alibaba, router, cost | LLM Provider & Model Router |
| governance, sync, guarani, workflow, propagate | Governance & Sync |
| security, PII, RLS, secret, scan, frozen | Security |
| shared, llm-provider, packages, types, atrian | Shared Packages |
| integration, adapter, webhook, whatsapp, telegram, slack, bundle, manifest, package | Integrations & Channels |
| cross-repo, ssot, duplicate, visit, archive, extract, eagle-eye, br-acc | Cross-Repo SSOT Visit Protocol |
